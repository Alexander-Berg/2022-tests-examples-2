ORDER_ERROR = {
    'message': 'UNKNOWN_CARD',
    'cargo_order_id': 'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
    'reason': 'COMMIT_ERROR',
    'updated_ts': '2021-06-30T11:08:43.070017+00:00',
}


async def test_admin_waybill_info_order_with_error(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        mock_cargo_orders_bulk_info,
        waybill_id='waybill_fb_3',
):
    mock_cargo_orders_bulk_info(order_error=ORDER_ERROR)

    waybill_admin = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info',
        params={'waybill_external_ref': waybill_id},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )

    info = waybill_admin.json()['execution']['cargo_order_info']
    assert info['provider_order_id'] == 'taxi-id'
    assert info['order_error'] == ORDER_ERROR
