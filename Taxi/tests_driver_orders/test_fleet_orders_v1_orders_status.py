import pytest


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-Login': 'user_login',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


async def test_change_orders_status_complete(taxi_driver_orders, doaa_mock):
    doaa_mock.set_status_code(200)
    doaa_mock.set_json({'status': 'complete'})

    request = {'status': 'complete'}

    params = {'order_id': 'order_id1', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.put(
        'fleet/orders/v1/orders/status',
        json=request,
        params=params,
        headers=build_headers('park_id1'),
    )

    assert doaa_mock.times_called() == 1
    assert response.status_code == 204


async def test_change_orders_status_cancelled(taxi_driver_orders, doaa_mock):
    doaa_mock.set_status_code(200)
    doaa_mock.set_json({'status': 'cancelled'})

    request = {'status': 'cancelled'}

    params = {'order_id': 'order_id1', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.put(
        'fleet/orders/v1/orders/status',
        json=request,
        params=params,
        headers=build_headers('park_id1'),
    )

    assert doaa_mock.times_called() == 1
    assert response.status_code == 204


@pytest.mark.parametrize(
    'doaa_code,status_code', [(404, 404), (406, 409), (410, 409)],
)
async def test_change_orders_status_cancelled_error(
        taxi_driver_orders, mockserver, doaa_code, status_code, doaa_mock,
):
    doaa_mock.set_status_code(doaa_code)
    doaa_mock.set_json({'code': str(doaa_code), 'message': 'error'})

    request = {'status': 'cancelled'}

    params = {'order_id': 'order_id1', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.put(
        'fleet/orders/v1/orders/status',
        json=request,
        params=params,
        headers=build_headers('park_id1'),
    )

    assert doaa_mock.times_called() == 1
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'doaa_code,status_code', [(404, 404), (406, 409), (410, 409)],
)
async def test_change_orders_status_complete_error(
        taxi_driver_orders, mockserver, doaa_code, status_code, doaa_mock,
):
    doaa_mock.set_status_code(doaa_code)
    doaa_mock.set_json({'code': str(doaa_code), 'message': 'error'})

    request = {'status': 'complete'}

    params = {'order_id': 'order_id1', 'driver_id': 'driver_id1'}

    response = await taxi_driver_orders.put(
        'fleet/orders/v1/orders/status',
        json=request,
        params=params,
        headers=build_headers('park_id1'),
    )

    assert doaa_mock.times_called() == 1
    assert response.status_code == status_code
