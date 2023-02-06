import itertools

import pymongo
import pytest

NOW = '2019-11-18T19:03:08+00:00'


def build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }


def build_params(order_id):
    return {'order_id': order_id}


def check_equal(mongo_item, service_item):
    assert mongo_item['message'] == service_item['message']
    assert mongo_item['user_name'] == service_item['user_name']


OK_PARAMS = [
    ('park_id_1', 'order_id_1', {'db': 'park_id_1', 'order': 'order_id_1'}),
    ('park_id_2', 'order_id_1', {'db': 'park_id_2', 'order': 'order_id_1'}),
]


@pytest.mark.parametrize('park_id, order_id, mongo_params', OK_PARAMS)
@pytest.mark.now(NOW)
async def test_get_messages(
        mongodb, taxi_driver_order_messages, park_id, order_id, mongo_params,
):
    response = await taxi_driver_order_messages.get(
        '/fleet/order-messages/v1/order/messages/',
        headers=build_headers(park_id),
        params=build_params(order_id),
    )

    projection = {'date', 'user_name', 'message'}
    mongo_response = list(
        mongodb.ordermessages.find(mongo_params, projection).sort(
            'date', pymongo.ASCENDING,
        ),
    )

    assert response.status_code == 200
    assert len(mongo_response) == len(response.json()['messages'])

    for mongo_item, service_item in itertools.zip_longest(
            mongo_response, response.json()['messages'], fillvalue=' ',
    ):
        check_equal(mongo_item, service_item)


@pytest.mark.now(NOW)
async def test_empty(mongodb, taxi_driver_order_messages):
    response = await taxi_driver_order_messages.get(
        '/fleet/order-messages/v1/order/messages/',
        headers=build_headers('not_found'),
        params=build_params(''),
    )

    assert response.status_code == 200
    assert not response.json()['messages']
