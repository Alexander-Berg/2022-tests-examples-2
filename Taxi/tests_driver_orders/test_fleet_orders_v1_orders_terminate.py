def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-Login': 'user_login',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


async def test_success_complete(
        taxi_driver_orders, mockserver, fleet_parks_shard, doaa_mock,
):
    doaa_mock.set_request_body(
        {
            'cost': 100.0,
            'total': 100.0,
            'park_id': 'park_id_2',
            'driver_profile_id': 'driver_id1',
            'setcar_id': 'order4',
            'should_notify': True,
            'origin': 'yandex_dispatch',
        },
    )
    doaa_mock.set_status_code(200)
    doaa_mock.set_json({'status': 'complete', 'cost': 100})

    json = {'status': 'complete', 'cost': '100'}
    params = {'order_id': 'order4', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.post(
        'fleet/orders/v1/orders/terminate',
        json=json,
        params=params,
        headers=build_headers('park_id_2'),
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'complete', 'cost': '100.000000'}
    assert doaa_mock.times_called() == 1


async def test_success_cancelled(
        taxi_driver_orders, mockserver, fleet_parks_shard, doaa_mock,
):
    doaa_mock.set_request_body(
        {
            'park_id': 'park_id_2',
            'driver_profile_id': 'driver_id1',
            'setcar_id': 'order4',
            'should_notify': True,
            'origin': 'yandex_dispatch',
        },
    )
    doaa_mock.set_status_code(200)
    doaa_mock.set_json({'status': 'cancelled'})

    json = {'status': 'cancelled'}
    params = {'order_id': 'order4', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.post(
        'fleet/orders/v1/orders/terminate',
        json=json,
        params=params,
        headers=build_headers('park_id_2'),
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'cancelled'}
    assert doaa_mock.times_called() == 1


async def test_platform_only(taxi_driver_orders, fleet_parks_shard):
    json = {'status': 'complete', 'cost': '100'}
    params = {'order_id': 'order0', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.post(
        'fleet/orders/v1/orders/terminate',
        json=json,
        params=params,
        headers=build_headers('park_id_0'),
    )

    assert response.status_code == 403


async def test_order_not_found(taxi_driver_orders, fleet_parks_shard):
    json = {'status': 'complete', 'cost': '100'}
    params = {'order_id': 'order04', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.post(
        'fleet/orders/v1/orders/terminate',
        json=json,
        params=params,
        headers=build_headers('park_id_0'),
    )

    assert response.status_code == 404
