import json

import pytest

EATER_ID = '1'
LOGBROKER_TOPIC = '/eda/processing/production/order-client-events'
MESSAGE_COOKIE = 'cookie1'

MESSAGE_TYPE_CREATED = 'created_message'
MESSAGE_TYPE_CREATED_WRONG_APPLICATION = 'created_message_wrong_application'
MESSAGE_TYPE_FINISHED = 'finished_message'


@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_CORE_ORDERS_SETTINGS={
        'applications_to_process': ['application1'],
    },
    EATS_RETAIL_MARKET_INTEGRATION_CONSUMERS={
        '__default__': {'is_enabled': True},
    },
)
@pytest.mark.parametrize(
    'message_type',
    [
        pytest.param(MESSAGE_TYPE_CREATED, id=MESSAGE_TYPE_CREATED),
        pytest.param(
            MESSAGE_TYPE_CREATED_WRONG_APPLICATION,
            id=MESSAGE_TYPE_CREATED_WRONG_APPLICATION,
        ),
        pytest.param(MESSAGE_TYPE_FINISHED, id=MESSAGE_TYPE_FINISHED),
    ],
)
async def test_order_client_events_consumer_one_message(
        taxi_eats_retail_market_integration, testpoint, message_type, stq,
):
    # This testpoint will be activated on every message commit.
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    response = await push_message(
        taxi_eats_retail_market_integration,
        json.dumps(_get_payload(message_type)),
    )
    assert response.status_code == 200
    await commit.wait_call()

    if message_type == MESSAGE_TYPE_CREATED:
        assert stq.eats_retail_market_integration_core_orders.times_called == 1
    else:
        assert not stq.eats_retail_market_integration_core_orders.has_calls


@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_CORE_ORDERS_SETTINGS={
        'applications_to_process': ['application1'],
    },
    EATS_RETAIL_MARKET_INTEGRATION_CONSUMERS={
        '__default__': {'is_enabled': True},
    },
)
async def test_order_client_events_consumer_multiple_messages_save_one(
        taxi_eats_retail_market_integration, testpoint, stq,
):
    # This testpoint will be activated on every message commit.
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    order1 = (
        f""""order_event":"created","application":"application1","""
        + f""""eater_id":"{EATER_ID}","order_nr":"1","""
    )
    order2 = (
        f""""order_event":"created","application":"application2","""
        + f""""eater_id":"{EATER_ID}","order_nr":"2","""
    )
    order3 = (
        f""""order_event":"finished","""
        + f""""eater_id":"{EATER_ID}","order_nr":"3","""
    )

    data = (
        """{"timestamp_raw":"2021-04-21T11:31:50.623121494+03:00","""
        + f"""{order1}"""
        + """"timestamp":"2021-04-21T08:31:50"}\n"""
        + """{"timestamp_raw":"2021-04-21T11:31:51.793351952+03:00","""
        + f"""{order2}"""
        + """"timestamp":"2021-04-21T08:31:51"}\n"""
        + """{"timestamp_raw":"2021-04-21T11:31:51.793351952+03:00","""
        + f"""{order3}"""
        + """"timestamp":"2021-04-21T08:31:51"}\n"""
    )

    response = await push_message(taxi_eats_retail_market_integration, data)
    assert response.status_code == 200

    await commit.wait_call()
    assert stq.eats_retail_market_integration_core_orders.times_called == 1


@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_CORE_ORDERS_SETTINGS={
        'applications_to_process': ['application1'],
    },
    EATS_RETAIL_MARKET_INTEGRATION_CONSUMERS={
        '__default__': {'is_enabled': True},
    },
)
async def test_order_client_events_consumer_multiple_messages_save_all(
        taxi_eats_retail_market_integration, testpoint, stq,
):
    # This testpoint will be activated on every message commit.
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    order1 = (
        f""""order_event":"created","application":"application1","""
        + f""""eater_id":"{EATER_ID}","order_nr":"1","""
    )
    order2 = (
        f""""order_event":"created","application":"application1","""
        + f""""eater_id":"{EATER_ID}","order_nr":"2","""
    )

    data = (
        """{"timestamp_raw":"2021-04-21T11:31:50.623121494+03:00","""
        + f"""{order1}"""
        + """"timestamp":"2021-04-21T08:31:50"}\n"""
        + """{"timestamp_raw":"2021-04-21T11:31:51.793351952+03:00","""
        + f"""{order2}"""
        + """"timestamp":"2021-04-21T08:31:51"}\n"""
    )

    response = await push_message(taxi_eats_retail_market_integration, data)
    assert response.status_code == 200

    await commit.wait_call()
    assert stq.eats_retail_market_integration_core_orders.times_called == 2


async def push_message(taxi_eats_retail_market_integration, data):
    # This is emulation of writing message to logbroker.
    response = await taxi_eats_retail_market_integration.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order_client_events',
                'data': data,
                'topic': LOGBROKER_TOPIC,
                'cookie': MESSAGE_COOKIE,
            },
        ),
    )
    return response


def _get_payload(message_type=MESSAGE_TYPE_FINISHED):
    if message_type == MESSAGE_TYPE_CREATED:
        return {
            'order_event': 'created',
            'order_nr': '1',
            'eater_id': '1',
            'application': 'application1',
        }
    if message_type == MESSAGE_TYPE_CREATED_WRONG_APPLICATION:
        return {
            'order_event': 'created',
            'order_nr': '1',
            'eater_id': '1',
            'application': 'application2',
        }
    if message_type == MESSAGE_TYPE_FINISHED:
        return {
            'order_event': 'finished',
            'order_nr': '1',
            'finished_at': '2020-09-04T16:59:51+00:00',
        }
    return None
