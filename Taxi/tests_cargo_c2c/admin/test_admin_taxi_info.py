import pytest


@pytest.mark.parametrize('add_postcard', [True, False])
async def test_taxi_admin(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        add_postcard,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json('waybill_info_response.json')
        resp['execution']['segments'][0]['cargo_c2c_order_id'] = order_id
        return mockserver.make_response(json=resp)

    order_id = await create_cargo_c2c_orders(add_postcard=add_postcard)

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/taxi-admin-info',
        json={
            'cargo_ref_id': 'order/8ff12bef-515d-43bb-b038-c625234331c3',
            'phone_pd_id': 'phone_pd_id_3',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'contains_postcard': add_postcard,
        'order_id': order_id,
        'order_provider_id': 'cargo-c2c',
    }


async def test_taxi_admin_order_waybill_not_found(
        taxi_cargo_c2c, create_cargo_c2c_orders, mockserver, load_json,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'no such claim_id'},
            status=404,
        )

    await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/taxi-admin-info',
        json={
            'cargo_ref_id': 'order/8ff12bef-515d-43bb-b038-c625234331c3',
            'phone_pd_id': 'phone_pd_id_3',
        },
    )
    assert response.status_code == 404


async def test_taxi_admin_order_delivery_not_found(
        taxi_cargo_c2c, create_cargo_c2c_orders, mockserver, load_json,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json('waybill_info_response.json')
        resp['execution']['segments'][0]['cargo_c2c_order_id'] = 'random'
        return mockserver.make_response(json=resp)

    await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/taxi-admin-info',
        json={
            'cargo_ref_id': 'order/8ff12bef-515d-43bb-b038-c625234331c3',
            'phone_pd_id': 'phone_pd_id_3',
        },
    )
    assert response.status_code == 404
