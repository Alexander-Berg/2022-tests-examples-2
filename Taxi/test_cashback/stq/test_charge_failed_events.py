import functools
import json

import aiohttp
import pytest

from taxi.stq import async_worker_ng

from cashback.generated.stq3 import pytest_plugin as stq_plugin
from cashback.stq import cashback_charge_failed_events


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'billing_service': 'card',
                },
            },
        },
    ),
]

DEFAULT_EVENT = {
    'event_id': 'event_id',
    'external_ref': 'order_id',
    'currency': 'RUB',
    'value': '30',
    'type': 'invoice',
    'source': 'user',
    'yandex_uid': 'yandex_uid_1',
    'service': 'yataxi',
    'payload': {},
}


def make_event(**kwargs):
    res = DEFAULT_EVENT.copy()
    res.update(kwargs)
    return res


def _create_task_info(exec_tries=0):
    return async_worker_ng.TaskInfo(
        id='task_id', exec_tries=exec_tries, reschedule_counter=0, queue='',
    )


def _compare_reward(reward_a: dict, reward_b: dict):
    if reward_a['source'] == reward_b['source']:
        return reward_a['amount'] - reward_b['amount']
    if reward_a['source'] > reward_b['source']:
        return 1
    return -1


@pytest.fixture(name='mock_events_by_id')
def _mock_cashback_events_id(mock_cashback):
    @mock_cashback('/internal/events/by-id')
    async def _mock_events(request, **kwargs):
        return {'events': [make_event()]}

    return _mock_events


async def test_empty_events(
        stq_runner: stq_plugin.Stq3Runner, stq, mock_events_by_id,
):
    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id', args=([],),
    )

    assert stq['cashback_charge_failed_events'].times_called == 0
    assert mock_events_by_id.times_called == 0


async def test_start_transaction(
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        transactions_mock,
        mock_plus_balances,
        mock_events_by_id,
        mockserver,
):
    @mockserver.json_handler('/transactions/v2/cashback/update')
    async def _mock_cashback_update(request):
        request_json = request.json
        request_json['reward'].sort(key=functools.cmp_to_key(_compare_reward))
        assert request_json == {
            'billing_service': 'card',
            'extra_payload': {},
            'invoice_id': 'order_id',
            'operation_id': 'event_id/retry',  # most important field
            'reward': [{'amount': '30', 'source': 'user'}],
            'user_ip': '2a02:6b8:b010:50a3::3',
            'version': 1,
            'wallet_account': 'wallet_1',
            'yandex_uid': 'yandex_uid_1',
        }

        return {}

    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id', args=(['event_id'],),
    )

    assert _mock_cashback_update.has_calls
    assert stq['cashback_charge_failed_events'].times_called == 1

    call = stq['cashback_charge_failed_events'].next_call()
    assert call['id'] == 'order_id/retry'
    assert call['kwargs'] == {'event_ids': ['event_id'], 'cashback_version': 1}


async def test_reschedule_old_version(
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        transactions_mock,
        mock_events_by_id,
        mock_reschedule,
):
    reschedule_mock = mock_reschedule('cashback_charge_failed_events')
    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id',
        args=(['event_id'],),
        kwargs=dict(cashback_version=1),
    )
    assert reschedule_mock.has_calls


async def test_reschedule_in_progress(
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        transactions_mock,
        mock_events_by_id,
        mock_reschedule,
):
    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'status': 'in-progress',
                'version': 3,
                'rewarded': [],
                'transactions': [],
                'commit_version': 1,
                'operations': [],
            },
        },
    )

    reschedule_mock = mock_reschedule('cashback_charge_failed_events')
    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id',
        args=(['event_id'],),
        kwargs=dict(cashback_version=2),
    )
    assert reschedule_mock.has_calls


@pytest.mark.parametrize(
    'invoice_status, event_status',
    [('success', 'done'), ('failed', 'failed')],
)
async def test_terminal_status(
        invoice_status,
        event_status,
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        transactions_mock,
        mock_events_by_id,
        mock_cashback,
):
    @mock_cashback('/internal/events/mark-processed')
    async def _mock_mark_events(request):
        assert request.json['status'] == event_status
        return {}

    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'status': invoice_status,
                'version': 3,
                'rewarded': [],
                'transactions': [],
                'commit_version': 1,
                'operations': [],
            },
        },
    )

    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id',
        args=(['event_id'],),
        kwargs=dict(cashback_version=2),
    )

    assert _mock_mark_events.has_calls


@pytest.mark.parametrize(
    'events, expected_exception',
    [
        (
            [dict(external_ref='order_id1'), dict(external_ref='order_id2')],
            cashback_charge_failed_events.DifferentOrders,
        ),
        (
            [dict(service='yataxi'), dict(service='lavka')],
            cashback_charge_failed_events.DifferentServices,
        ),
    ],
)
async def test_validation(
        events, expected_exception, stq3_context, mock_cashback,
):
    @mock_cashback('/internal/events/by-id')
    async def _mock_events(request, **kwargs):
        return {'events': [make_event(**event) for event in events]}

    with pytest.raises(expected_exception):
        await cashback_charge_failed_events.task(
            stq3_context, _create_task_info(), ['event_id'],
        )


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'cashback', 'dst': 'archive-api'},
        {'src': 'cashback', 'dst': 'stq-agent'},
    ],
)
async def test_invoice_not_found(
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        mock_events_by_id,
        mockserver,
        mock_reschedule,
):
    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    async def _mock_retrieve(request, **kwargs):
        return aiohttp.web.Response(
            status=404, body=json.dumps({'code': '1', 'message': '2'}),
        )

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    async def _mock_restore_archive(request, **kwargs):
        return [{'id': request.json['id'], 'status': 'restored'}]

    reschedule_mock = mock_reschedule('cashback_charge_failed_events')

    await stq_runner.cashback_charge_failed_events.call(
        task_id='order_id', args=(['event_id'],),
    )

    assert _mock_retrieve.has_calls
    assert _mock_restore_archive.has_calls
    assert reschedule_mock.has_calls
