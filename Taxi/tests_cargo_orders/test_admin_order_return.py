import pytest


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_orders_yagr_store_driver_position',
    consumers=['cargo-orders/yagr-store-driver-position'],
    default_value={'enabled': True},
)
async def test_claims_exchange_statuses(
        taxi_cargo_orders, mockserver, mock_dispatch_return, default_order_id,
):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _mock_position_store(request):
        return mockserver.make_response(
            status=200,
            headers={'X-Polling-Power-Policy': 'policy'},
            content_type='application/json',
        )

    response = await taxi_cargo_orders.post(
        '/admin/v1/order/return',
        params={'cargo_order_id': default_order_id},
        headers={
            'X-Forwarded-For': '12.34.56.78,12.34.56.79',
            'Accept-Language': 'en',
        },
        json={
            'last_known_status': 'pickuped',
            'point_id': 100,
            'comment': 'some comment',
            'ticket': 'TESTBACKEND-100500',
            'location_data': {'a': []},
        },
    )

    assert response.status_code == 200
