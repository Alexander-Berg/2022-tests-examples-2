import datetime
import json

import pytest

from tests_cashbox_integration import utils

OK_QUERY_TO_RECEIPTS = """
    INSERT INTO cashbox_integration.receipts(
    park_id, driver_id, order_id, cashbox_id,
    external_id, status, created_at, updated_at)
    VALUES(
        'park_id_2',
        'driver_id_1',
        'order_id_0',
        'cashbox_id_1',
        'key1',
        'need_order_info',
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    )
"""


def check_receipt(
        receipt,
        park_id,
        order_id,
        status,
        driver_id,
        external_id,
        order_end_point,
        fail_message=None,
        order_end=None,
):
    assert receipt['park_id'] == park_id
    assert receipt['order_id'] == order_id
    assert receipt['status'] == status
    assert receipt['driver_id'] == driver_id
    assert receipt['external_id'] == external_id
    assert receipt['order_end_point'] == order_end_point
    assert receipt['fail_message'] == fail_message
    assert receipt['order_end'] == order_end


def check_geotracks_request(request, expected_body):
    assert request['request'].method == 'POST'
    assert json.loads(request['request'].get_data())['params'] == expected_body


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\', {}, {})'.format(
            'park_id_2',
            'driver_id_1',
            'order_id_0',
            'cashbox_id_1',
            'idempotency_key2',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
    ],
)
async def test_get_order_info(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {
            'tracks': [
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 1,
                    'track': [
                        {
                            'point': [10.02, 20.01],
                            'timestamp': 100,
                            'bearing': 1,
                            'speed': 1,
                        },
                    ],
                },
            ],
        }

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 2}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 1
    check_geotracks_request(
        geotracks.next_call(),
        [
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 1,
                'to': 1556740810,
            },
        ],
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt,
        'park_id_2',
        'order_id_0',
        'push_to_cashbox',
        'driver_id_1',
        'idempotency_key2',
        '(10.02,20.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\',{},{})'.format(
            'park_id_2',
            'driver_id_1',
            'order_id_0',
            'cashbox_id_1',
            'idempotency_key2',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\',{},{})'.format(
            'park_id_2',
            'driver_id_1',
            'order_id_2',
            'cashbox_id_1',
            'idempotency_key3',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
    ],
)
async def test_orders_from_one_park(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {
            'tracks': [
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 2,
                    'track': [
                        {
                            'point': [10.02, 20.01],
                            'timestamp': 100,
                            'bearing': 1,
                            'speed': 1,
                        },
                    ],
                },
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 1,
                    'track': [
                        {
                            'point': [11.02, 21.01],
                            'timestamp': 100,
                            'bearing': 1,
                            'speed': 1,
                        },
                    ],
                },
            ],
        }

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 2}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')
    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 1
    check_geotracks_request(
        geotracks.next_call(),
        [
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 1,
                'to': 1556740810,
            },
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 2,
                'to': 1556740810,
            },
        ],
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt,
        'park_id_2',
        'order_id_0',
        'push_to_cashbox',
        'driver_id_1',
        'idempotency_key2',
        '(10.02,20.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_2')
    check_receipt(
        receipt,
        'park_id_2',
        'order_id_2',
        'push_to_cashbox',
        'driver_id_1',
        'idempotency_key3',
        '(11.02,21.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\', {}, {})'.format(
            'park_id_2',
            'driver_id_1',
            'order_id_0',
            'cashbox_id_1',
            'key1',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\', {}, {})'.format(
            'park_id_2',
            'driver_id_1',
            'order_id_2',
            'cashbox_id_1',
            'key2',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\', {}, {})'.format(
            'park_id_3',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'key3',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
    ],
)
async def test_get_orders_info(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        if request.json['params']:
            if request.json['params'][0]['db_id'] == 'park_id_2':
                return {
                    'tracks': [
                        {
                            'db_id': 'park_id_2',
                            'driver_id': 'driver_id_1',
                            'req_id': 1,
                            'track': [
                                {
                                    'point': [10.02, 20.01],
                                    'timestamp': 100,
                                    'bearing': 1,
                                    'speed': 1,
                                },
                            ],
                        },
                    ],
                }
        return {'tracks': []}

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 2}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')
    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 3
    assert geotracks.times_called >= 2

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt,
        'park_id_2',
        'order_id_0',
        'push_to_cashbox',
        'driver_id_1',
        'key1',
        '(10.02,20.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_2')
    check_receipt(
        receipt,
        'park_id_2',
        'order_id_2',
        'push_to_cashbox',
        'driver_id_1',
        'key2',
        '(10.02,20.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_3', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_3',
        'order_id_1',
        'push_to_cashbox',
        'driver_id_1',
        'key3',
        None,
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        """
        INSERT INTO cashbox_integration.receipts(
        park_id, driver_id, order_id, cashbox_id, external_id,
        status, created_at, updated_at) VALUES
        (
            'park_id_4',
            'driver_id_1',
            'order_id_???',
            'cashbox_id_1',
            'key1',
            'need_order_info',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'park_id_4',
            'driver_id_1',
            'order_id_1',
            'cashbox_id_1',
            'key2',
            'need_order_info',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'park_id_4',
            'driver_id_1',
            'order_id_2',
            'cashobox_id_1',
            'key3',
            'need_order_info',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'park_id_4',
            'driver_id_1',
            'order_id_5',
            'cashobox_id_1',
            'key4',
            'need_order_info',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ),
        (
            'park_id_4',
            'driver_id_1',
            'order_id_6',
            'cashobox_id_1',
            'key5',
            'need_order_info',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        """,
    ],
)
async def test_fail_orders(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {'tracks': []}

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 10}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 0

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_???')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_???',
        'invalid',
        'driver_id_1',
        'key1',
        None,
        'order not found',
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_1')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_1',
        'invalid',
        'driver_id_1',
        'key2',
        None,
        'order won\'t complete, status is cancelled',
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_2')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_2',
        'invalid',
        'driver_id_1',
        'key3',
        None,
        'payment method must be a cash, payment method is card',
    )
    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_5')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_5',
        'invalid',
        'driver_id_1',
        'key4',
        None,
        'order price too much',
    )
    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_6')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_6',
        'invalid',
        'driver_id_1',
        'key5',
        None,
        'order price too small',
    )


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\',{},{})'.format(
            'park_id_4',
            'driver_id_1',
            'order_id_3',
            'cashbox_id_1',
            'key4',
            'need_order_info',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
        'INSERT INTO cashbox_integration.receipts('
        'park_id, driver_id, order_id, cashbox_id, external_id,'
        'status, created_at, updated_at) '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\',{},{})'.format(
            'park_id_4',
            'driver_id_1',
            'order_id_4',
            'cashbox_id_1',
            'key5',
            'push_to_cashbox',
            'CURRENT_TIMESTAMP',
            'CURRENT_TIMESTAMP',
        ),
    ],
)
async def test_nothing_orders(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {'tracks': []}

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 10}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 0

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_3')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_3',
        'need_order_info',
        'driver_id_1',
        'key4',
        None,
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_4', 'order_id_4')
    check_receipt(
        receipt,
        'park_id_4',
        'order_id_4',
        'push_to_cashbox',
        'driver_id_1',
        'key5',
        None,
    )


@pytest.mark.pgsql('cashbox_integration', queries=[OK_QUERY_TO_RECEIPTS])
async def test_ended_points(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {
            'tracks': [
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 1,
                    'track': [
                        {
                            'point': [10.11, 20.11],
                            'timestamp': (
                                1556695210
                            ),  # 2019-05-01T07:20:10+00:00
                            'bearing': 1,
                            'speed': 1,
                        },
                        {
                            'point': [10.11, 20.11],
                            'timestamp': (
                                1556695230
                            ),  # 2019-05-01T07:20:30+00:00
                            'bearing': 1,
                            'speed': 1,
                        },
                        {
                            'point': [10.01, 20.01],
                            'timestamp': (
                                1556695230
                            ),  # 2019-05-01T07:20:30+00:00
                            'bearing': 1,
                            'speed': 1,
                        },
                        {
                            'point': [10.01, 20.01],
                            'timestamp': (
                                1556695259
                            ),  # 2019-05-01T07:20:59+00:00
                            'bearing': 1,
                            'speed': 1,
                        },
                    ],
                },
            ],
        }

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 10}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 1
    check_geotracks_request(
        geotracks.next_call(),
        [
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 1,
                'to': 1556740810,
            },
        ],
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt=receipt,
        park_id='park_id_2',
        order_id='order_id_0',
        status='push_to_cashbox',
        driver_id='driver_id_1',
        external_id='key1',
        order_end_point='(10.01,20.01)',
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )


@pytest.mark.pgsql('cashbox_integration', queries=[OK_QUERY_TO_RECEIPTS])
async def test_empty_track(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {
            'tracks': [
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 1,
                    'track': [],
                },
            ],
        }

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 10}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 1
    check_geotracks_request(
        geotracks.next_call(),
        [
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 1,
                'to': 1556740810,
            },
        ],
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt=receipt,
        park_id='park_id_2',
        order_id='order_id_0',
        status='push_to_cashbox',
        driver_id='driver_id_1',
        external_id='key1',
        order_end_point=None,
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )


@pytest.mark.pgsql('cashbox_integration', queries=[OK_QUERY_TO_RECEIPTS])
async def test_without_track(
        mockserver,
        taxi_cashbox_integration,
        driver_orders,
        pgsql,
        taxi_config,
):
    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    def geotracks(request):
        return {
            'tracks': [
                {
                    'db_id': 'park_id_2',
                    'driver_id': 'driver_id_1',
                    'req_id': 1,
                },
            ],
        }

    taxi_config.set_values(
        dict(CASHBOX_GET_ORDERS_INFO={'enable': True, 'request_count': 10}),
    )

    await taxi_cashbox_integration.run_periodic_task('OrdersInfoGetter0')

    assert driver_orders.times_called >= 1
    assert geotracks.times_called >= 1
    check_geotracks_request(
        geotracks.next_call(),
        [
            {
                'db_id': 'park_id_2',
                'driver_id': 'driver_id_1',
                'from': 1556737490,
                'preprocess': 0,
                'req_id': 1,
                'to': 1556740810,
            },
        ],
    )

    receipt = utils.get_receipt_by_id(pgsql, 'park_id_2', 'order_id_0')
    check_receipt(
        receipt=receipt,
        park_id='park_id_2',
        order_id='order_id_0',
        status='push_to_cashbox',
        driver_id='driver_id_1',
        external_id='key1',
        order_end_point=None,
        order_end=datetime.datetime.fromisoformat('2019-05-01T23:00:00+03:00'),
    )
