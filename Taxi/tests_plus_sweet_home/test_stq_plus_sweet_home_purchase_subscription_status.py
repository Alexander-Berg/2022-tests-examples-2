import pytest


# pylint: disable=invalid-name
pytestmark = [pytest.mark.experiments3(filename='experiments3_defaults.json')]


DEFAULT_ORDER_ID = 'default_order'
BASE_ARGS_STQ_BEFORE_START_PURCHASE = {
    'order_id': DEFAULT_ORDER_ID,
    'purchase_context': {
        'ip_address': '185.15.98.233',
        'subscription_id': 'ya_plus_rus_v2',
        'service_id': 'taxi',
        'payment_method_id': 'method_id',
        'application_info': {
            'platform': 'ios',
            'application_version': '0.0.0',
        },
        'country_code': 'ru',
    },
    'yandex_uid': '111111',
    'event': 'catching_up_cashback',
}


BASE_ARGS_STQ_AFTER_START_PURCHASE = {
    'order_id': 'default_order',
    'subscription_purchase_id': '1000',
    'yandex_uid': '111111',
    'event': 'catching_up_cashback',
}


@pytest.mark.parametrize(
    'mediabilling_status_code, mediabilling_status, sync_features, '
    'cnt_new_stq_calls, cnt_rates_processing_calls, '
    'cnt_universal_processing_calls',
    [
        ('200', 'ok', True, 0, 1, 1),
        ('200', 'ok', False, 1, 0, 0),
        ('500', 'ok', False, 1, 0, 0),
        ('200', 'pending', False, 1, 0, 0),
        ('200', 'pending', True, 1, 0, 0),
        ('200', 'fail-3ds', False, 0, 0, 0),
        ('200', 'error', True, 0, 0, 0),
        ('500', 'cancelled', True, 0, 0, 0),
    ],
)
async def test_happy_path_check_purchase_status(
        stq_runner,
        stq,
        mockserver,
        mediabilling_status,
        sync_features,
        cnt_new_stq_calls,
        cnt_rates_processing_calls,
        cnt_universal_processing_calls,
        mediabilling_status_code,
):
    @mockserver.json_handler(
        '/mediabilling/internal-api/account/billing/order-info',
    )
    def _mock_billing_order_info(request):
        resp = {'status': mediabilling_status, 'orderId': 1000}
        if sync_features is not None:
            resp['synchronizationState'] = {'featuresSync': sync_features}
        return {'result': resp, 'status': mediabilling_status_code}

    @mockserver.handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        assert request.json == {
            'fields': [
                'extra_data.cashback.is_cashback',
                'extra_data.cashback.is_possible_cashback',
                'order.user_id',
                'order.user_uid',
            ],
            'lookup_flags': 'none',
            'order_id': DEFAULT_ORDER_ID,
            'require_latest': True,
            'search_archive': False,
        }
        return mockserver.make_response(
            json={
                'order_id': DEFAULT_ORDER_ID,
                'replica': 'master',
                'version': '1',
                'fields': {
                    'order': {
                        'creditcard': {
                            'tips_perc_default': 0,
                            'tips': {'type': 'flat', 'value': 10},
                        },
                        'user_id': 'some_user_id',
                        'user_uid': '111111',
                    },
                },
            },
            status=200,
        )

    @mockserver.handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert request.json == {
            'call_processing': False,
            'order_id': DEFAULT_ORDER_ID,
            'update': {
                'set': {
                    'extra_data.cashback.is_cashback': True,
                    'extra_data.cashback.is_possible_cashback': True,
                },
            },
            'user_id': 'some_user_id',
            'version': '1',
        }
        return mockserver.make_response(json={}, status=200)

    await stq_runner.plus_sweet_home_purchase_subscription_status.call(
        task_id=DEFAULT_ORDER_ID, kwargs=BASE_ARGS_STQ_AFTER_START_PURCHASE,
    )

    assert (
        stq.plus_sweet_home_purchase_subscription_status.times_called
        == cnt_new_stq_calls
    )
    assert (
        stq.cashback_rates_processing.times_called
        == cnt_rates_processing_calls
    )
    assert (
        stq.universal_cashback_processing.times_called
        == cnt_universal_processing_calls
    )

    if cnt_new_stq_calls:
        stq_call = stq.plus_sweet_home_purchase_subscription_status.next_call()

        assert stq_call['id'] == DEFAULT_ORDER_ID
