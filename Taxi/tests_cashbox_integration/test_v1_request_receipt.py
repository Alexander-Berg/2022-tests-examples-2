import json

import pytest

from tests_cashbox_integration import utils


ENDPOINT = 'v1/parks/orders/receipt/request'


TEST_BAD_PARAMS = [
    ('park_id_1', 'order_???', 'order not found'),
    ('park_id_1', 'order_id_3', 'order won\'t complete, status is failed'),
    (
        'park_id_1',
        'order_id_4',
        'payment method must be a cash, payment method is card',
    ),
    ('park_id_3', 'order_id_1', 'not found active cashbox'),
]


def check_geotracks_request(request, expected_body):
    assert request['request'].method == 'POST'
    assert json.loads(request['request'].get_data()) == expected_body


@pytest.mark.parametrize('park_id, order_id, message', TEST_BAD_PARAMS)
async def test_bad_request(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        geotracks,
        park_id,
        order_id,
        message,
):
    driver_authorizer.set_session(park_id, 'driver_session_1', 'driver_id_1')

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': message}


def check_receipt(
        receipt,
        park_id,
        order_id,
        status,
        driver_id,
        cashbox_id,
        order_end_point=None,
):
    assert receipt['park_id'] == park_id
    assert receipt['order_id'] == order_id
    assert receipt['status'] == status
    assert receipt['driver_id'] == driver_id
    assert receipt['cashbox_id'] == cashbox_id
    assert receipt['order_end_point'] == order_end_point


async def test_create_receipt(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
        geotracks,
):
    park_id = 'park_id_1'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', 'driver_id_1')

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt,
        park_id,
        order_id,
        'need_order_info',
        'driver_id_1',
        cashbox_id,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }


async def test_exists_receipt(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
        geotracks,
):
    park_id = 'park_id_1'
    order_id = 'order_id_2'
    cashbox_id = 'cashbox_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', 'driver_id_1')

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt,
        park_id,
        order_id,
        'need_order_info',
        'driver_id_1',
        cashbox_id,
    )

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt,
        park_id,
        order_id,
        'need_order_info',
        'driver_id_1',
        cashbox_id,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }


async def test_create_receipt_with_order_1(
        mockserver,
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
):
    @mockserver.json_handler('/driver-trackstory/shorttrack')
    def geotracks(request):
        return {'adjusted': [{'lon': 10.02, 'lat': 20.01, 'timestamp': 100}]}

    park_id = 'park_id_2'
    order_id = 'order_id_0'
    cashbox_id = 'cashbox_id_2'
    driver_id = 'driver_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', driver_id)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )
    assert geotracks.times_called == 1
    check_geotracks_request(
        geotracks.next_call(),
        {
            'driver_id': 'park_id_2_driver_id_1',
            'type': 'adjusted',
            'merge_close': True,
            'merge_last_adjust_with_raw_position': False,
        },
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt,
        park_id,
        order_id,
        'push_to_cashbox',
        driver_id,
        cashbox_id,
        '(10.02,20.01)',
    )

    assert receipt['order_price'] == 999.0

    assert response.status_code == 201, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }


async def test_create_receipt_with_order_2(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
        geotracks,
):
    park_id = 'park_id_2'
    order_id = 'order_id_1'
    cashbox_id = 'cashbox_id_2'
    driver_id = 'driver_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', driver_id)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt, park_id, order_id, 'push_to_cashbox', driver_id, cashbox_id,
    )

    assert receipt['order_price'] == 1000.0

    assert response.status_code == 201, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }


async def test_create_receipt_with_order_3(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
        geotracks,
):
    park_id = 'park_id_2'
    order_id = 'order_id_3'
    cashbox_id = 'cashbox_id_2'
    driver_id = 'driver_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', driver_id)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt, park_id, order_id, 'push_to_cashbox', driver_id, cashbox_id,
    )

    assert receipt['order_price'] == 9999.0

    assert response.status_code == 201, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }


async def test_create_receipt_with_order_4(
        taxi_cashbox_integration,
        driver_authorizer,
        driver_orders,
        pgsql,
        geotracks,
):
    park_id = 'park_id_2'
    order_id = 'order_id_4'
    cashbox_id = 'cashbox_id_2'
    driver_id = 'driver_id_1'

    driver_authorizer.set_session(park_id, 'driver_session_1', driver_id)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        headers={'X-Driver-Session': 'driver_session_1'},
        params={'order_id': order_id, 'park_id': park_id},
    )

    receipt = utils.get_receipt_by_id(pgsql, park_id, order_id)

    check_receipt(
        receipt, park_id, order_id, 'push_to_cashbox', driver_id, cashbox_id,
    )

    assert receipt['order_price'] == 10000.0

    assert response.status_code == 201, response.text
    assert response.json() == {
        'receipt_url': utils.get_receipt_url(park_id, order_id),
    }
