import json

import pytest

LOGBROKER_TOPIC = '/eda/processing/production/order-client-events'
LOGBROEKR_CONSUMER = 'order-client-events-consumer'
LOGBROKER_TESTPOINT = 'logbroker_commit'
CONSUMER_TASK = 'order-client-events-consumer-lb_consumer'

CREATED = 'created'
FINISHED = 'finished'

PLACE_ID = '1'
EATER_ID = 'eater_id-1'
ORDER_NR = 'order-nr'


def make_event(
        order_nr=ORDER_NR,
        event_time='2021-09-16T12:00:00.1234+03:00',
        order_event='created',
        created_at=None,
        order_type='native',
        delivery_type='native',
        shipping_type='delivery',
        eater_id=EATER_ID,
        eater_personal_phone_id='eater_personal_phone_id-1',
        promised_at='2022-03-03T19:30:00+03:00',
        application='web',
        place_id=PLACE_ID,
        meta=None,
        payment_method='payment-method',
        **kwargs,
):
    event = {
        'order_nr': order_nr,
        'order_event': order_event,
        'created_at': created_at or event_time,
        'order_type': order_type,
        'delivery_type': delivery_type,
        'shipping_type': shipping_type,
        'eater_id': eater_id,
        'eater_personal_phone_id': eater_personal_phone_id,
        'promised_at': promised_at,
        'application': application,
        'place_id': place_id,
        f'{order_event}_at': event_time,
        'payment_method': payment_method,
    }
    if meta:
        event['meta'] = meta

    return event


async def push_message(taxi_eats_retail_categories, event, cookie=ORDER_NR):
    # This is emulation of writing message to logbroker.
    response = await taxi_eats_retail_categories.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': LOGBROEKR_CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': cookie,
            },
        ),
    )
    return response


async def test_order_clients_several_events(
        taxi_eats_retail_categories,
        testpoint,
        pg_add_brand,
        pg_add_place,
        stq,
):
    """
    Тест проверяет отправку нескольких сообщений в брокер.
    """
    pg_add_brand()
    pg_add_place()

    # Этот тестпоинт будет активирован на каждый commit каждого сообщения
    @testpoint(LOGBROKER_TESTPOINT)
    def commit(_):
        pass

    events = {}

    for _, order_event in enumerate([CREATED, FINISHED]):
        events[order_event] = make_event(order_event=order_event)

    for order_event, event in events.items():
        response = await push_message(
            taxi_eats_retail_categories, event, cookie=order_event,
        )
        assert response.status_code == 200

    await taxi_eats_retail_categories.run_task(CONSUMER_TASK)
    for _ in events:
        await commit.wait_call()

    assert (
        stq.eats_retail_categories_update_user_order_history.times_called == 1
    )


@pytest.mark.parametrize(
    'status, expected_count_call',
    [
        pytest.param(FINISHED, 1, id='task finished'),
        pytest.param(CREATED, 0, id='task created'),
    ],
)
async def test_order_clients_event(
        taxi_eats_retail_categories,
        testpoint,
        pg_add_brand,
        pg_add_place,
        stq,
        status,
        expected_count_call,
):
    """
    Тест проверяет отправку одного сообщения в брокер.
    """
    pg_add_brand()
    pg_add_place()

    # Этот тестпоинт будет активирован на каждый commit каждого сообщения
    @testpoint('logbroker_commit')
    def commit(_):
        pass

    event = make_event(order_event=status)

    response = await push_message(taxi_eats_retail_categories, event)
    assert response.status_code == 200

    await taxi_eats_retail_categories.run_task(CONSUMER_TASK)
    await commit.wait_call()

    assert (
        stq.eats_retail_categories_update_user_order_history.times_called
        == expected_count_call
    )


@pytest.mark.config(
    EATS_RETAIL_CATEGORIES_ORDER_CLIENT_EVENTS_CONSUMER={'enabled': False},
)
@pytest.mark.parametrize(
    'status',
    [
        pytest.param(FINISHED, id='task finished'),
        pytest.param(CREATED, id='task created'),
    ],
)
async def test_order_clients_events_disabled(
        taxi_eats_retail_categories, pg_add_brand, pg_add_place, stq, status,
):
    """
    Тест проверяет отправку одного сообщения в брокер с выключенным конфигом.
    """
    pg_add_brand()
    pg_add_place()

    event = make_event(order_event=status)

    response = await push_message(taxi_eats_retail_categories, event)
    assert response.status_code == 200

    assert (
        stq.eats_retail_categories_update_user_order_history.times_called == 0
    )
