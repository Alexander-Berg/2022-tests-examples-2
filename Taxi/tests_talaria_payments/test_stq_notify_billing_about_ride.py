import pytest

BILLING_NOTIFICATIONS_CONFIG = {
    'ride_notifications': {
        'cost_default_settings': {
            'is_enabled': True,
            'product': 'cost_default_product',
            'payment_kind': 'cost_default_payment_kind',
            'detailed_product': 'cost_default_detailed_product',
            'billing_client_id': 'cost_default_billing_client_id',
            'contract_id': 'cost_default_contract_id',
            'service_id': 123,
            'tariff_class': 'cost_default_tariff_class',
            'transaction_type': 'cost_default_transaction_type',
            'refunded_transaction_type': (
                'cost_default_refunded_transaction_type'
            ),
            'default_agglomeration': 'cost_default_agglomeration',
            'vat': '0.1',
            'topic_prefix': '/taxi/scooters/talaria',
        },
        'discount_default_settings': {
            'is_enabled': True,
            'product': 'discount_default_product',
            'payment_kind': 'discount_default_payment_kind',
            'detailed_product': 'discount_default_detailed_product',
            'billing_client_id': 'discount_default_billing_client_id',
            'contract_id': 'discount_default_contract_id',
            'service_id': 321,
            'tariff_class': 'discount_default_tariff_class',
            'transaction_type': 'discount_default_transaction_type',
            'refunded_transaction_type': (
                'discount_default_refunded_transaction_type'
            ),
            'default_agglomeration': 'discount_default_agglomeration',
            'vat': '0.1',
            'use_amount_with_vat': True,
            'topic_prefix': '/taxi/scooters/talaria',
        },
        'cost_type_overrides': {
            'card': {'payment_kind': 'card_payment_kind'},
            'wallet': {'payment_kind': 'wallet_payment_kind'},
        },
        'discount_type_overrides': {
            'bonus_balance': {'payment_kind': 'bonus_discount_payment_kind'},
        },
        'is_enabled': True,
        'stq_rescheduling_delay': 60,
    },
    'transaction_notifications': {
        'default_settings': {},
        'charge_type_overrides': {},
        'is_enabled': False,
    },
}


@pytest.mark.now('2022-02-18T00:00:00+00:00')
@pytest.mark.config(
    TALARIA_PAYMENTS_BILLING_NOTIFICATIONS=BILLING_NOTIFICATIONS_CONFIG,
)
async def test_notification_success(load_json, mockserver, stq_runner):
    @mockserver.json_handler(
        (
            '/stq-agent/queues/api/add/'
            'talaria_payments_notify_billing_about_ride'
        ),
    )
    def stq_mock(request):
        return {}

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/get-or-create-wind-user',
    )
    def talaria_misc_mock(request):
        assert request.json == load_json(
            'talaria_misc_get_or_create_user_request.json',
        )
        return load_json('talaria_misc_get_or_create_user_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/ride_id')
    def wind_mock(request):
        return load_json('wind_board_rides_response.json')

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_process(request):
        assert request.json == load_json('billing_orders_process_request.json')
        return load_json('billing_orders_process_response.json')

    kwargs = {
        'wind_ride_id': 'ride_id',
        'yandex_uid': 'yandex_uid',
        'personal_phone_id': 'personal_phone_id',
    }

    await stq_runner.talaria_payments_notify_billing_about_ride.call(
        task_id='task_id', kwargs=kwargs,
    )

    assert talaria_misc_mock.times_called == 1
    assert wind_mock.times_called == 1
    assert billing_orders_process.times_called == 1
    assert stq_mock.times_called == 0


@pytest.mark.now('2022-02-18T00:00:00+00:00')
@pytest.mark.config(
    TALARIA_PAYMENTS_BILLING_NOTIFICATIONS=BILLING_NOTIFICATIONS_CONFIG,
)
async def test_notification_failed(load_json, mockserver, stq_runner):
    @mockserver.json_handler(
        (
            '/stq-agent/queues/api/add/'
            'talaria_payments_notify_billing_about_ride'
        ),
    )
    def stq_mock(request):
        return {}

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/get-or-create-wind-user',
    )
    def talaria_misc_mock(request):
        assert request.json == load_json(
            'talaria_misc_get_or_create_user_request.json',
        )
        return load_json('talaria_misc_get_or_create_user_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/ride_id')
    def wind_mock(request):
        response = load_json('wind_board_rides_response.json')
        response['result'] = 42
        return response

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_process(request):
        return {}

    kwargs = {
        'wind_ride_id': 'ride_id',
        'yandex_uid': 'yandex_uid',
        'personal_phone_id': 'personal_phone_id',
    }

    await stq_runner.talaria_payments_notify_billing_about_ride.call(
        task_id='task_id', kwargs=kwargs, expect_fail=True,
    )

    assert talaria_misc_mock.times_called == 1
    assert wind_mock.times_called == 1
    assert billing_orders_process.times_called == 0
    assert stq_mock.times_called == 0


@pytest.mark.now('2022-02-18T00:00:00+00:00')
@pytest.mark.config(
    TALARIA_PAYMENTS_BILLING_NOTIFICATIONS=BILLING_NOTIFICATIONS_CONFIG,
)
async def test_notification_rescheduled(load_json, mockserver, stq_runner):
    @mockserver.json_handler(
        (
            '/stq-agent/queues/api/add/'
            'talaria_payments_notify_billing_about_ride'
        ),
    )
    def stq_mock(request):
        assert request.json['eta'] == '2022-02-18T00:01:00+0000'
        assert request.json['task_id'] == 'task_id'
        kwargs = request.json['kwargs']
        kwargs.pop('log_extra')
        assert kwargs == {
            'yandex_uid': 'yandex_uid',
            'personal_phone_id': 'personal_phone_id',
            'wind_ride_id': 'ride_id',
        }
        return {}

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/get-or-create-wind-user',
    )
    def talaria_misc_mock(request):
        assert request.json == load_json(
            'talaria_misc_get_or_create_user_request.json',
        )
        return load_json('talaria_misc_get_or_create_user_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/ride_id')
    def wind_mock(request):
        response = load_json('wind_board_rides_response.json')
        response['ride']['status'] = 1
        return response

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_process(request):
        return {}

    kwargs = {
        'wind_ride_id': 'ride_id',
        'yandex_uid': 'yandex_uid',
        'personal_phone_id': 'personal_phone_id',
    }

    await stq_runner.talaria_payments_notify_billing_about_ride.call(
        task_id='task_id', kwargs=kwargs,
    )

    assert talaria_misc_mock.times_called == 1
    assert wind_mock.times_called == 1
    assert billing_orders_process.times_called == 0
    assert stq_mock.times_called == 1
