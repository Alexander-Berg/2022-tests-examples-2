import json

import pytest

from . import utils

ALLOWED_ORDER_TYPES = [utils.OrderType.shop, utils.OrderType.retail]

LOGBROKER_TOPIC = '/eda/processing/production/order-client-events'
MESSAGE_COOKIE = 'message_cookie'

LB_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 2,
        'queue_timeout_ms': 50,
        'config_poll_period_ms': 1000,
    },
}


@pytest.mark.parametrize(
    'events',
    [
        (utils.OrderClientEvent.created,),
        (utils.OrderClientEvent.payed,),
        (utils.OrderClientEvent.taken,),
        (utils.OrderClientEvent.created, utils.OrderClientEvent.payed),
        (
            utils.OrderClientEvent.created,
            utils.OrderClientEvent.payed,
            utils.OrderClientEvent.taken,
        ),
    ],
)
@pytest.mark.parametrize(
    'order_type, do_call_by_order_type',
    [
        (order_type, order_type in ALLOWED_ORDER_TYPES)
        for order_type in utils.OrderType
    ],
)
@pytest.mark.config(
    EATS_RETAIL_ORDER_HISTORY_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS,
)
async def test_order_client_events_consumer(
        taxi_eats_retail_order_history,
        testpoint,
        stq,
        events,
        order_type,
        do_call_by_order_type,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    order_client_events = []
    for i, order_event in enumerate(events):
        data = utils.make_order_client_event(
            f'order_nr_{i}',
            order_event,
            f'eater_id_{i}',
            f'passport_uid_{i}',
            f'taxi_user_id_{i}',
            f'place_id_{i}',
            f'eater_personal_phone_id_{i}',
            f'application_{i}',
            order_type,
        )
        order_client_events.append(data)
        response = await taxi_eats_retail_order_history.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'order-client-events-consumer',
                    'data': json.dumps(data),
                    'topic': LOGBROKER_TOPIC,
                    'cookie': MESSAGE_COOKIE,
                },
            ),
        )
        assert response.status_code == 200
        await taxi_eats_retail_order_history.run_task(
            'order-client-events-consumer-lb_consumer',
        )
        await commit.wait_call()

    count_of_calls = len([e for e in events if do_call_by_order_type])

    assert (
        stq.eats_retail_order_history_order_client_events.times_called
        == count_of_calls
    )
    for i, order_event in enumerate(events):
        if not do_call_by_order_type:
            continue
        task_info = (
            stq.eats_retail_order_history_order_client_events.next_call()
        )
        kwargs = task_info['kwargs']
        assert kwargs['event'] == order_client_events[i]


@pytest.mark.config(
    EATS_RETAIL_ORDER_HISTORY_LOGBROKER_CONSUMER_SETTINGS=LB_CONSUMER_SETTINGS,
)
async def test_order_client_events_consumer_json_parse_error(
        taxi_eats_retail_order_history, stq, testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    response = await taxi_eats_retail_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-client-events-consumer',
                'data': 'invalid json',
                'topic': LOGBROKER_TOPIC,
                'cookie': MESSAGE_COOKIE,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_retail_order_history.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    await commit.wait_call()

    assert stq.eats_retail_order_history_order_client_events.times_called == 0
