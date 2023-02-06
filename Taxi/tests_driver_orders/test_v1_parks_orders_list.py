import json

import pytest

from tests_driver_orders import utils


ENDPOINT = 'v1/parks/orders/list'


async def common_request(taxi_driver_orders, request, code, expected_response):
    response = await taxi_driver_orders.post(ENDPOINT, json=request)

    assert response.status_code == code, response.text
    assert response.json() == expected_response


def common_response(date, order_indices, limit=10):
    orders = [utils.RESULT_ORDERS[i] for i in order_indices]
    return {
        'orders': [order[0] for order in orders],
        'limit': limit,
        **({'cursor': orders[-1][1][date]} if orders else {}),
    }


TEST_BAD_PARAMS = [
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {
                        'booked_at': {
                            'from': '2019-05-01T00:00:00+03:00',
                            'to': '2019-06-01T00:00:00+03:00',
                        },
                        'price': {'from': 'wrong_value'},
                    },
                },
            },
            'limit': 10,
        },
        {'code': '400', 'message': 'field \'query.order.price\' is invalid'},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {
                        'booked_at': {
                            'from': '2019-05-01T00:00:00+03:00',
                            'to': '2019-06-01T00:00:00+03:00',
                        },
                    },
                },
            },
            'limit': 10,
            'cursor': 'invalid cursor',
        },
        {'code': '400', 'message': 'cursor is invalid'},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {
                        'booked_at': {
                            'from': '2019-06-01T00:00:00+03:00',
                            'to': '2019-05-01T00:00:00+03:00',
                        },
                    },
                },
            },
            'limit': 10,
        },
        {'code': '400', 'message': 'time interval is empty'},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {
                        'booked_at': {
                            'from': '2019-05-01T00:00:00+03:00',
                            'to': '2019-06-01T00:00:00+03:00',
                        },
                        'price': {'from': '200.05', 'to': '100.1'},
                    },
                },
            },
            'limit': 10,
        },
        {'code': '400', 'message': 'price interval is empty'},
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {
                        'booked_at': {
                            'from': '2019-05-01T00:00:00+03:00',
                            'to': '2019-06-01T00:00:00+03:00',
                        },
                        'categories': ['trash'],
                    },
                },
            },
            'limit': 10,
        },
        {
            'code': '400',
            'message': 'field \'query.order.categories\' is invalid',
        },
    ),
]


@pytest.mark.parametrize('payload, expected_response', TEST_BAD_PARAMS)
async def test_bad_request(
        taxi_driver_orders, fleet_parks_shard, payload, expected_response,
):
    await common_request(taxi_driver_orders, payload, 400, expected_response)


async def test_empty_orders(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_???',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = {'orders': [], 'limit': 10}
    await common_request(taxi_driver_orders, payload, 200, expected_response)


TEST_DATE_PARAMETER = ['booked_at', 'ended_at']


@pytest.mark.parametrize('filter_date', TEST_DATE_PARAMETER)
async def test_all_fields(taxi_driver_orders, fleet_parks_shard, filter_date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_0',
                'order': {
                    filter_date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 1,
    }

    expected_response = common_response(filter_date, [0], limit=1)
    await common_request(taxi_driver_orders, payload, 200, expected_response)


async def test_cursor(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 2,
    }

    expected_response = common_response('booked_at', [1, 3], limit=2)
    await common_request(taxi_driver_orders, payload, 200, expected_response)

    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 1,
        'cursor': utils.RESULT_ORDERS[3][1]['booked_at'],
    }

    expected_response = common_response('booked_at', [2], limit=1)
    await common_request(taxi_driver_orders, payload, 200, expected_response)

    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 1,
        'cursor': utils.RESULT_ORDERS[2][1]['booked_at'],
    }

    expected_response = {'limit': 1, 'orders': []}
    await common_request(taxi_driver_orders, payload, 200, expected_response)


async def test_cursor_end(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'ended_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 2,
    }

    expected_response = common_response('ended_at', [1, 3], limit=2)
    await common_request(taxi_driver_orders, payload, 200, expected_response)

    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'ended_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 1,
        'cursor': utils.RESULT_ORDERS[3][1]['ended_at'],
    }

    expected_response = common_response('ended_at', [2], limit=1)
    await common_request(taxi_driver_orders, payload, 200, expected_response)

    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'ended_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 1,
        'cursor': utils.RESULT_ORDERS[2][1]['ended_at'],
    }

    expected_response = {'limit': 1, 'orders': []}
    await common_request(taxi_driver_orders, payload, 200, expected_response)


async def test_driver_filter(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'driver_profile': {'id': 'driver_id_1'},
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response('booked_at', [1])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_car_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'car': {'id': 'car_id_3'},
                'order': {
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [3])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize(
    'payload,expected_response',
    [
        (
            {
                'query': {
                    'park': {
                        'id': 'park_id_1',
                        'order': {
                            'ids': ['order3', 'order1', 'order?'],
                            'short_ids': [3, 1],
                            'booked_at': {
                                'from': '2019-05-01T00:00:00+03:00',
                                'to': '2019-06-01T00:00:00+03:00',
                            },
                        },
                    },
                },
                'limit': 10,
            },
            common_response('booked_at', [1, 3]),
        ),
        (
            {
                'query': {
                    'park': {
                        'id': 'park_id_1',
                        'order': {
                            'short_ids': [3, 1],
                            'ended_at': {
                                'from': '2019-05-01T00:00:00+03:00',
                                'to': '2019-06-01T00:00:00+03:00',
                            },
                        },
                    },
                },
                'limit': 10,
            },
            common_response('ended_at', [1, 3]),
        ),
    ],
)
async def test_orders_filter(
        taxi_driver_orders, fleet_parks_shard, payload, expected_response,
):
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_order_types_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_0',
                'order': {
                    'order_type': {
                        'ids': ['request_type_0', 'request_type_?'],
                    },
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [0])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_statuses_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_2',
                'order': {
                    'statuses': ['expired', 'cancelled'],
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [5, 4])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_payments_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_2',
                'order': {
                    'payment_method': ['cash', 'corp'],
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [5, 4])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_providers_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_2',
                'order': {
                    'providers': ['partner', 'platform'],
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [5, 4])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
@pytest.mark.parametrize(
    'categories, order_indices',
    [
        (None, [5, 4]),
        (['park_vip'], [5]),
        (['business'], [4]),
        (['business', 'park_vip'], [5, 4]),
        (['econom', 'premium_suv'], []),
    ],
)
async def test_categories_filter(
        taxi_driver_orders, fleet_parks_shard, date, categories, order_indices,
):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_2',
                'order': {
                    'categories': categories,
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, order_indices)
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize('date', TEST_DATE_PARAMETER)
async def test_price_filter(taxi_driver_orders, fleet_parks_shard, date):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_2',
                'order': {
                    'price': {'from': '150.0'},
                    date: {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response(date, [4])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_3',
        {'order6': json.dumps({'provider': 2})},
    ],
)
async def test_hidden_details_driving(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_3',
                'order': {
                    'ids': ['order6'],
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response('booked_at', [6])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_35',
        {'order65': json.dumps({'provider': 2})},
    ],
)
async def test_hidden_details_none(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_35',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response('booked_at', [7])
    await common_request(taxi_driver_orders, payload, 200, expected_response)


async def test_invalid_data(taxi_driver_orders, fleet_parks_shard):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_4',
                'order': {
                    'booked_at': {
                        'from': '2019-05-01T00:00:00+03:00',
                        'to': '2019-06-01T00:00:00+03:00',
                    },
                },
            },
        },
        'limit': 10,
    }

    expected_response = common_response('booked_at', [8])
    await common_request(taxi_driver_orders, payload, 200, expected_response)
