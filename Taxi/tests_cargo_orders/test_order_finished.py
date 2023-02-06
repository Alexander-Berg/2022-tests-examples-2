import pytest


async def test_order_finished_with_confirmation(
        mockserver, stq_runner, calc_price, mock_cargo_pricing_calc,
):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/confirm-usage')
    def cargo_pricing(request):
        return {}

    await calc_price()
    await calc_price('requestconfirm')

    # confirming stq from processing
    await stq_runner.cargo_pricing_taxi_order_finished.call(
        task_id='test_stq',
        kwargs={
            'user_id': 'mock-user',
            'order_id': 'taxi-order',
            'tariff_class': 'mock-tariff',
            'order_status': 'failed',
        },
        expect_fail=False,
    )

    assert cargo_pricing.times_called == 1
    assert mock_cargo_pricing_calc.mock.times_called == 2


@pytest.mark.config(
    CARGO_ORDERS_FINISH_ORDER_USES_DRIVER_ORDERS_APP_API_ENABLED=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_orders_price_source',
    consumers=['cargo-orders/stq/cargo_pricing_taxi_order_finished'],
    clauses=[],
    default_value={
        'result': [
            {
                'source': 'orders',
                'path': 'payment_tech.driver_without_vat_to_pay.rebate',
            },
            {
                'source': 'orders',
                'path': 'payment_tech.driver_without_vat_to_pay.ride',
            },
            {'source': 'orders', 'path': 'payment_tech.sum_to_pay.ride'},
            {'source': 'pricing'},
        ],
    },
    is_config=True,
)
async def test_order_finished_using_driver_orders_app(
        stq_runner,
        mock_cargo_pricing_calc_retrieve,
        mock_archive_api,
        mock_driver_orders_app_api_order_update_fields,
        calc_price,
):
    calc_retrieve_response = mock_cargo_pricing_calc_retrieve.response
    calc_retrieve_response['details']['paid_waiting_in_transit_price'] = '40'
    calc_retrieve_response['details']['paid_waiting_in_transit_time'] = '120'
    calc_retrieve_response['details'][
        'paid_waiting_in_transit_total_price'
    ] = '222'
    calc_retrieve_response['details']['paid_waiting_price'] = '50'
    calc_retrieve_response['details']['paid_waiting_time'] = '30'
    calc_retrieve_response['details']['paid_waiting_total_price'] = '333'

    await calc_price()
    await calc_price('requestconfirm')

    # confirming stq from processing
    await stq_runner.cargo_pricing_taxi_order_finished.call(
        task_id='test_stq',
        kwargs={
            'user_id': 'mock-user',
            'order_id': 'taxi-order',
            'tariff_class': 'mock-tariff',
            'order_status': 'failed',
        },
        expect_fail=False,
    )

    request = mock_driver_orders_app_api_order_update_fields.request
    assert request == {
        'fields': {
            'cost_total': 799.0,
            'cost_full': 799.0,
            'receipt_data': {
                'services': {
                    'door_to_door': 150.0,
                    'fake_middle_point_express': 160.0,
                },
                'services_count': {
                    'door_to_door': {'count': 1, 'price': '150', 'sum': 150.0},
                    'fake_middle_point_express': {
                        'count': 2,
                        'price': '80',
                        'sum': 160.0,
                    },
                },
                'sum': 827.0,
                'total': 827.0,
                'total_distance': 13155.5,
                'waiting_cost': 50.0,
                'waiting_in_transit_cost': 40.0,
                'waiting_in_transit_sum': 222.0,
                'waiting_in_transit_time': 120.0,
                'waiting_sum': 333.0,
                'waiting_time': 30.0,
            },
        },
        'park_id': 'mock_performer_clid',
        'setcar_id': 'mock_performer_taxi_alias_id',
        'driver_profile_id': '3b21002ec1564d87ac05174bf261379f',
        'origin': 'cargo',
    }

    pricing_retrieve_request = mock_cargo_pricing_calc_retrieve.request
    assert (
        pricing_retrieve_request['calc_id']
        == 'cargo-pricing/v1/f6e1661746e34f8c8234832e1d718d85'
    )

    assert mock_archive_api.request == {'id': 'taxi-order'}


@pytest.mark.config(
    CARGO_ORDERS_FINISH_ORDER_USES_DRIVER_ORDERS_APP_API_ENABLED=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_orders_price_source',
    consumers=['cargo-orders/stq/cargo_pricing_taxi_order_finished'],
    clauses=[
        {
            'title': 'test',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'currency_code',
                                'arg_type': 'string',
                                'value': 'KZT',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'payment_type',
                                'arg_type': 'string',
                                'value': 'corp',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {'result': [{'source': 'pricing'}]},
        },
    ],
    default_value={
        'result': [
            {
                'source': 'orders',
                'path': 'payment_tech.driver_without_vat_to_pay.rebate',
            },
            {
                'source': 'orders',
                'path': 'payment_tech.driver_without_vat_to_pay.ride',
            },
            {'source': 'orders', 'path': 'payment_tech.sum_to_pay.ride'},
            {'source': 'pricing'},
        ],
    },
    is_config=True,
)
async def test_order_finished_pricing_source(
        stq_runner,
        mock_cargo_pricing_calc_retrieve,
        mock_archive_api,
        mock_driver_orders_app_api_order_update_fields,
        calc_price,
):
    mock_response = mock_cargo_pricing_calc_retrieve.response

    mock_response['units']['currency'] = 'KZT'

    await calc_price()
    await calc_price('requestconfirm')

    # confirming stq from processing
    await stq_runner.cargo_pricing_taxi_order_finished.call(
        task_id='test_stq',
        kwargs={
            'user_id': 'mock-user',
            'order_id': 'taxi-order',
            'tariff_class': 'mock-tariff',
            'order_status': 'failed',
        },
        expect_fail=False,
    )

    request = mock_driver_orders_app_api_order_update_fields.request
    assert request['fields']['cost_full'] == 827.0
    assert request['fields']['cost_total'] == 827.0
