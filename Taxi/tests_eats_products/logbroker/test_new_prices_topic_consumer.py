import json

import pytest


@pytest.mark.pgsql('eats_products', files=['fill_places.sql'])
async def test_consumer(taxi_eats_products, testpoint, stq):
    msg_cookie = 'cookie1'
    # This testpoint will be activated on every message commit.
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == msg_cookie

    place_id = '1'

    data = {
        'place_id': place_id,
        'timestamp': '2021-03-04T00:00:00',
        'timestamp_raw': '2021-03-04T17:19:42.838992671+03:00',
    }
    # This is emulation of writing message to logbroker.
    response = await taxi_eats_products.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'new_prices',
                'data': json.dumps(data),
                'topic': '/eda/prod/eda-prod-eats-nomenclature-new-prices-log',
                'cookie': msg_cookie,
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    assert stq.eats_products_update_discount_products.has_calls
    task_info = stq.eats_products_update_discount_products.next_call()
    assert task_info['kwargs']['place_id'] == place_id


@pytest.mark.pgsql('eats_products', files=['fill_places.sql'])
async def test_split_message(taxi_eats_products, testpoint, stq):
    msg_cookie = 'cookie1'
    # This testpoint will be activated on every message commit.
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == msg_cookie

    place_id_1 = 1
    place_id_2 = 2
    place_id_3 = 3

    data = (
        """{"timestamp_raw":"2021-04-21T11:31:50.623121494+03:00","""
        + f""""place_id":"{place_id_1}","""
        + """"timestamp":"2021-04-21T08:31:50"}\n"""
        + """{"timestamp_raw":"2021-04-21T11:31:51.793351952+03:00","""
        + f""""place_id":"{place_id_2}","""
        + """"timestamp":"2021-04-21T08:31:51"}\n"""
        + """{"timestamp_raw":"2021-04-21T11:31:51.793351952+03:00","""
        + f""""place_id":"{place_id_3}","""
        + """"timestamp":"2021-04-21T08:31:51"}\n"""
    )
    # This is emulation of writing message to logbroker.
    response = await taxi_eats_products.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'new_prices',
                'data': data,
                'topic': '/eda/prod/eda-prod-eats-nomenclature-new-prices-log',
                'cookie': msg_cookie,
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
    assert stq.eats_products_update_discount_products.times_called == 3
    for place_id in [place_id_1, place_id_2, place_id_3]:
        task_info = stq.eats_products_update_discount_products.next_call()
        assert task_info['kwargs']['place_id'] == str(place_id)
