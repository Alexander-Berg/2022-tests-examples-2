# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import json
import psycopg2
import pytest

CREATED = 'created'
PAYED = 'payed'
CONFIRMED = 'confirmed'
READY_TO_DELIVERY = 'ready_to_delivery'
TAKEN = 'taken'
FINISHED = 'finished'
CANCELLED = 'cancelled'
PROMISE_CHANGED = 'promise_changed'

LOGBROKER_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 2,
        'queue_timeout_ms': 50,
        'config_poll_period_ms': 1000,
    },
}


def _get_payload(order_nr, order_event):
    payload = {'order_nr': order_nr, 'order_event': order_event}

    payload['created_at'] = '2020-09-04T15:26:43+00:00'
    payload['order_type'] = 'order_type'
    payload['delivery_type'] = 'delivery_type'
    payload['shipping_type'] = 'shipping_type'
    payload['eater_id'] = '123123'
    payload['eater_personal_phone_id'] = '123123'
    payload['eater_passport_uid'] = '123123'
    payload['promised_at'] = '2020-09-04T16:26:43+00:00'
    payload['application'] = 'web'
    payload['place_id'] = '123123'
    payload['payment_method'] = 'payment-method'
    if order_event == CREATED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    if order_event == PAYED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    if order_event == CONFIRMED:
        return payload

    payload['ready_to_delivery_at'] = '2020-09-04T15:56:51+00:00'
    if order_event == READY_TO_DELIVERY:
        return payload

    payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    if order_event == TAKEN:
        return payload

    payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    if order_event == FINISHED:
        return payload

    payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
    payload['cancellation_reason'] = 'not_ready'
    payload['cancelled_by'] = 'operator'
    if order_event == CANCELLED:
        return payload

    payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    if order_event == PROMISE_CHANGED:
        return payload

    raise Exception('unknown order_event {}'.format(order_event))


async def _push_lb_order(taxi_eats_feedback, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_feedback.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-client-events-consumer',
                'data': message,
                'topic': '/eda/processing/testing/order-client-events',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200


def assert_db_orders(psql, expected_db_orders_count):
    cursor = psql.cursor()
    cursor.execute(
        """SELECT order_nr, order_delivered_at AT TIME ZONE 'UTC', status, eater_id FROM eats_feedback.orders ORDER BY order_nr ASC;""",
    )
    db_orders = cursor.fetchall()
    assert len(db_orders) == expected_db_orders_count
    return db_orders


@pytest.mark.config(
    EATS_FEEDBACK_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,expected_db_orders_count',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _get_payload('111111-100001', FINISHED),
                _get_payload('111111-100000', FINISHED),
                _get_payload('111111-100001', FINISHED),
                _get_payload('111111-100010', FINISHED),
                _get_payload('111111-100010', FINISHED),
                _get_payload('111111-100011', READY_TO_DELIVERY),
            ],
            3,
        ),
    ],
)
async def test_order_save_db(
        taxi_eats_feedback, pgsql, lb_orders, expected_db_orders_count,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_feedback, lb_order)

    # wait for lb messages to be read
    await taxi_eats_feedback.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    db_orders = assert_db_orders(
        pgsql['eats_feedback'], expected_db_orders_count,
    )

    assert db_orders[0] == (
        '111111-100000',
        datetime.datetime(2020, 9, 4, 15, 59, 51),
        'finished',
        '123123',
    )
    assert db_orders[1] == (
        '111111-100001',
        datetime.datetime(2020, 9, 4, 15, 59, 51),
        'finished',
        '123123',
    )
    assert db_orders[2] == (
        '111111-100010',
        datetime.datetime(2020, 9, 4, 15, 59, 51),
        'finished',
        '123123',
    )
