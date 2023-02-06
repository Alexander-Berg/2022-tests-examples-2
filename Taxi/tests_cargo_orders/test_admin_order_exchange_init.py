import pytest


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
    },
)
@pytest.mark.parametrize(
    'dispatch_response_code, point_id, result_code',
    [
        (200, 100500, 200),
        (404, 100500, 404),
        (409, 100500, 409),
        (410, 100500, 410),
        (429, 100500, 429),
        (500, 100500, 500),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_orders_yagr_store_driver_position',
    consumers=['cargo-orders/yagr-store-driver-position'],
    default_value={'enabled': True},
)
async def test_claims_exchange_statuses(
        taxi_cargo_orders,
        mockserver,
        default_order_id,
        dispatch_response_code: int,
        point_id: int,
        result_code: int,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/init')
    def _mock_segment_init(request):
        assert not request.json['is_driver_request']
        return mockserver.make_response(
            json={'new_status': 'pickup_confirmation'}
            if dispatch_response_code == 200
            else {'code': 'not_found', 'message': 'some message'},
            status=dispatch_response_code,
        )

    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _mock_position_store(request):
        return mockserver.make_response(
            status=200,
            headers={'X-Polling-Power-Policy': 'policy'},
            content_type='application/json',
        )

    response = await taxi_cargo_orders.post(
        '/admin/v1/order/exchange/init',
        params={'cargo_order_id': default_order_id},
        headers={
            'X-Forwarded-For': '12.34.56.78,12.34.56.79',
            'Accept-Language': 'en',
        },
        json={
            'last_known_status': 'pickuped',
            'point_id': point_id,
            'idempotency_token': 'some_token',
            'location_data': {'a': []},
        },
    )
    assert response.status_code == result_code
