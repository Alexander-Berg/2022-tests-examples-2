import datetime

import pytest

PLUS_TX_CASHBACK_PATH = '/plus-transactions/plus-transactions/v1/cashback'


@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_reward_enabled.json')
@pytest.mark.parametrize(
    'cashback_status, should_reschedule',
    [
        pytest.param('init', True, id='cashback_status_init'),
        pytest.param('in_progress', True, id='cashback_status_in_progress'),
        pytest.param('success', False, id='cashback_status_success'),
        pytest.param('failed', False, id='cashback_status_failed'),
    ],
)
@pytest.mark.parametrize(
    'service_id',
    ['taxi', 'eda', 'lavka', 'market', 'kinopoisk', 'music', 'fuel'],
)
@pytest.mark.now('2021-11-08 00:00:00.000000')
async def test_cashback_levels_reward(
        stq_runner,
        stq,
        mockserver,
        load_json,
        cashback_status,
        should_reschedule,
        service_id,
):
    expected_payload = load_json('expected_{}_payload.json'.format(service_id))

    @mockserver.json_handler('/cashback/v1/cashback/payload')
    def _mock_cashback_payload(request):
        assert request.args['order_id'] == 'order_id'
        return {
            'payload': {
                'order_id': 'order_id',
                'alias_id': 'alias_id',
                'base_amount': '100',
                'oebs_mvp_id': 'oebs_mvp_id',
                'tariff_class': 'business',
                'currency': 'RUB',
                'country': 'RU',
            },
        }

    @mockserver.json_handler(PLUS_TX_CASHBACK_PATH + '/status')
    def _mock_plus_transactions_cashback_status(request):
        assert request.args['ext_ref_id'] == 'ext_ref_id'
        assert request.args['service_id'] == service_id
        assert request.args['consumer'] == 'cashback-levels'
        return {'status': cashback_status, 'version': 1, 'amount': '0'}

    @mockserver.json_handler(PLUS_TX_CASHBACK_PATH + '/update')
    def _mock_plus_transactions_cashback_update(request):
        assert request.json['ext_ref_id'] == 'ext_ref_id'
        assert request.json['service_id'] == service_id
        assert request.json['consumer'] == 'cashback-levels'
        assert request.json['yandex_uid'] == 'yandex_uid'
        assert request.json['currency'] == 'RUB'
        assert request.json['version'] == 1
        assert request.json['user_ip'] == ''

        amount_by_source_map = request.json['amount_by_source']
        assert len(amount_by_source_map) == 1

        amount_by_source = amount_by_source_map['service']
        assert amount_by_source['amount'] == '100'
        assert amount_by_source['payload'] == expected_payload

        return mockserver.make_response(status=200, json={})

    stq_kwargs = {
        'ext_ref_id': 'ext_ref_id',
        'task_id': '{}_task'.format(service_id),
        'yandex_uid': 'yandex_uid',
        'has_plus': expected_payload['has_plus'],
    }
    if 'order_id' in expected_payload:
        stq_kwargs['order_id'] = expected_payload['order_id']
    if 'base_amount' in expected_payload:
        stq_kwargs['base_amount'] = expected_payload['base_amount']

    await stq_runner.cashback_levels_reward.call(
        task_id='task_id_1',
        kwargs=stq_kwargs,
        expect_fail=cashback_status == 'failed',
    )

    assert _mock_plus_transactions_cashback_status.has_calls
    if cashback_status == 'init':
        assert _mock_plus_transactions_cashback_update.has_calls
    else:
        assert not _mock_plus_transactions_cashback_update.has_calls

    if should_reschedule:
        next_call = stq.cashback_levels_reward.next_call()
        assert next_call
        expected_eta = datetime.datetime.fromisoformat(
            '2021-11-08 00:00:05.000000',
        )
        diff = next_call['eta'] - expected_eta
        assert abs(diff.total_seconds()) < 1
    else:
        with pytest.raises(Exception):
            stq.cashback_levels_reward.next_call()


@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_reward_disabled.json')
@pytest.mark.now('2021-11-08 00:00:00.000000')
async def test_cashback_levels_reward_exp_disabled_reschedule(
        stq_runner, stq, mockserver,
):
    @mockserver.json_handler(PLUS_TX_CASHBACK_PATH + '/status')
    def _mock_plus_transactions_cashback_status(request):
        return

    @mockserver.json_handler(PLUS_TX_CASHBACK_PATH + '/update')
    def _mock_plus_transactions_cashback_update(request):
        return

    await stq_runner.cashback_levels_reward.call(
        task_id='task_id_1',
        kwargs={
            'ext_ref_id': 'ext_ref_id',
            'task_id': 'task_id_1',
            'yandex_uid': 'yandex_uid',
            'has_plus': 'true',
            'order_id': 'order_id',
        },
    )

    expected_eta = datetime.datetime.fromisoformat(
        '2021-11-08 00:01:00.000000',
    )
    next_call = stq.cashback_levels_reward.next_call()
    diff = next_call['eta'] - expected_eta
    assert abs(diff.total_seconds()) < 1
    assert not _mock_plus_transactions_cashback_status.has_calls
    assert not _mock_plus_transactions_cashback_update.has_calls
