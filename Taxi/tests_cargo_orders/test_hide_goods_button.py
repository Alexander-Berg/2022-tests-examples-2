import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.config(CARGO_ORDERS_ENABLE_C2C_HIDE_GOODS_BUTTON=True)
async def test_hide_goods_button(
        taxi_cargo_orders,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    for segment in my_waybill_info['execution']['segments']:
        segment['cargo_c2c_order_id'] = 'c2c_id'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert response.json()['current_point']['hide_goods_button']
