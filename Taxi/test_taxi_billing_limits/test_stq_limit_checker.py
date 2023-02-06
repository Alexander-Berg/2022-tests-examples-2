# pylint: disable=too-many-arguments
import datetime as dt
import uuid

from aiohttp import web
import pytest

from testsuite.utils import callinfo

from taxi_billing_limits.stq import limit_checker


@pytest.mark.now('2019-08-29T18:00:00+00:00')
@pytest.mark.pgsql(
    'billing_limits@0', files=('limits.limits.sql', 'limits.windows.sql'),
)
async def test_task_budget_ok(
        stq3_context, mock_billing_accounts, stq, load_json,
):
    fixtures = load_json('budget_ok.json')
    actual_balance_query = None

    @mock_billing_accounts('/v2/balances/select')
    async def _balances_select(request):
        nonlocal actual_balance_query
        actual_balance_query = request.json
        balances = fixtures['balances_select']
        return web.json_response(balances)

    await limit_checker.task(
        stq3_context, data=load_json('limit_checker_data_tumbling.json'),
    )
    assert fixtures['balance_query'] == actual_balance_query
    with pytest.raises(callinfo.CallQueueEmptyError):
        stq.billing_budget_alert.next_call()
    assert stq.is_empty


@pytest.mark.now('2019-08-29T18:00:00+00:00')
@pytest.mark.parametrize(
    'fname,check_data,alert_data,window_pk,window_wid',
    (
        (
            'budget_exhausted_tumbling.json',
            'limit_checker_data_tumbling.json',
            'budget_alert_data_tumbling.json',
            1,
            1026,
        ),
        (
            'budget_exhausted_sliding.json',
            'limit_checker_data_sliding.json',
            'budget_alert_data_sliding.json',
            2,
            18138,
        ),
    ),
)
@pytest.mark.pgsql(
    'billing_limits@0', files=('limits.limits.sql', 'limits.windows.sql'),
)
async def test_task_budget_exhausted(
        stq3_context,
        mock_billing_accounts,
        stq,
        load_json,
        fname,
        check_data,
        alert_data,
        window_pk,
        window_wid,
):
    fixtures = load_json(fname)
    actual_balance_query = None

    @mock_billing_accounts('/v2/balances/select')
    async def _balances_select(request):
        nonlocal actual_balance_query
        actual_balance_query = request.json
        balances = fixtures['balances_select']
        return web.json_response(balances)

    await limit_checker.task(stq3_context, data=load_json(check_data))
    assert fixtures['balance_query'] == actual_balance_query
    task = stq.billing_budget_alert.next_call()
    assert task['queue'] == 'billing_budget_alert'
    assert task['id'] == f'alert/{window_pk}/{window_wid}'
    assert task['args'] == [load_json(alert_data)]
    assert task['eta'].isoformat() == '1970-01-01T00:00:00'
    assert stq.is_empty


@pytest.mark.now('2022-06-29T18:00:00+03:00')
@pytest.mark.pgsql('billing_limits@0', files=['tumbling_eats.sql'])
async def test_task_budget_exhausted_stq_notification(
        stq3_context, mock_billing_accounts, stq, load_json, patch,
):
    test_data = load_json('tumbling_eats.json')

    @mock_billing_accounts('/v2/balances/select')
    async def _balances_select(request):
        return web.json_response(test_data['balances_select'])

    @patch('taxi_billing_limits.stq.queues.uuid.uuid4')
    def _uuid4():
        return uuid.UUID(int=0x0123456789ABCDEF)

    query = {'limit': {'ref': 'tumbling_eats'}}
    await limit_checker.task(stq3_context, data=query)
    task = stq.eats_restapp_promo_finish_on_limit.next_call()
    assert task == {
        'queue': 'eats_restapp_promo_finish_on_limit',
        'id': '00000000000000000123456789abcdef',
        'args': ['tumbling_eats', 'some_value', 'another_value'],
        'eta': dt.datetime.fromisoformat('1970-01-01T00:00:00'),
        'kwargs': {},
    }
    assert stq.is_empty
