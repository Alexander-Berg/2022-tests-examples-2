# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import json
import psycopg2
import pytest
from tests_eats_place_subscriptions import utils

CREATED = 'created'
PAYED = 'payed'
CONFIRMED = 'confirmed'
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


def _get_payload(
        order_nr,
        order_event,
        place_id=123,
        finish_at=None,
        delivery_type='marketplace',
):
    payload = {'order_nr': order_nr, 'order_event': order_event}

    payload['created_at'] = '2020-09-04T15:26:43+00:00'
    payload['order_type'] = 'order_type'
    payload['delivery_type'] = delivery_type
    payload['shipping_type'] = 'shipping_type'
    payload['eater_id'] = '123123'
    payload['eater_personal_phone_id'] = '123123'
    payload['eater_passport_uid'] = '123123'
    payload['promised_at'] = '2020-09-04T16:26:43+00:00'
    payload['application'] = 'web'
    payload['place_id'] = str(place_id)
    payload['payment_method'] = 'payment-method'
    if order_event == CREATED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    if order_event == PAYED:
        return payload

    payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    if order_event == CONFIRMED:
        return payload

    payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    if order_event == TAKEN:
        return payload

    payload['finished_at'] = finish_at
    if order_event == FINISHED:
        return payload

    payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
    payload['cancellation_reason'] = 'client_no_show'
    payload['cancelled_by'] = 'operator'
    if order_event == CANCELLED:
        return payload

    payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    if order_event == PROMISE_CHANGED:
        return payload

    raise Exception('unknown order_event {}'.format(order_event))


async def _push_lb_order(taxi_eats_place_subscriptions, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_place_subscriptions.post(
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


@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,expect',
    [
        pytest.param(
            [],
            [(124, datetime.date(2020, 5, 24), 10)],
            id='empty_lb_only_in_db',
        ),
        pytest.param(
            [
                _get_payload('111111-100001', CREATED),
                _get_payload('111111-100001', CANCELLED),
            ],
            [(124, datetime.date(2020, 5, 24), 10)],
            id='ignore cancel event',
        ),
        pytest.param(
            [
                _get_payload('111111-100001', CREATED),
                _get_payload(
                    '111111-100001',
                    FINISHED,
                    finish_at='2020-09-04T15:56:51+00:00',
                ),
            ],
            [
                (123, datetime.date(2020, 9, 4), 1),
                (124, datetime.date(2020, 5, 24), 10),
            ],
            id='return one',
        ),
        pytest.param(
            [
                _get_payload('111111-100000', CREATED),
                _get_payload('111111-100000', CANCELLED),
                _get_payload('111111-100001', CREATED),
                _get_payload(
                    '111111-100001',
                    FINISHED,
                    finish_at='2020-09-04T15:56:51+00:00',
                ),
            ],
            [
                (123, datetime.date(2020, 9, 4), 1),
                (124, datetime.date(2020, 5, 24), 10),
            ],
            id='return one with ignore cancel',
        ),
        pytest.param(
            [
                _get_payload('111111-100000', CREATED),
                _get_payload('111111-100000', CANCELLED),
                _get_payload('111111-100001', CREATED),
                _get_payload(
                    '111111-100001',
                    FINISHED,
                    finish_at='2020-09-03T21:00:51+00:00',
                ),
                _get_payload('111111-100002', CREATED),
                _get_payload(
                    '111111-100002',
                    FINISHED,
                    finish_at='2020-09-03T23:00:51+00:00',
                ),
                _get_payload('111111-100003', CREATED),
                _get_payload(
                    '111111-100003',
                    FINISHED,
                    finish_at='2020-09-04T10:56:51+00:00',
                ),
                _get_payload('111111-100004', CREATED),
                _get_payload(
                    '111111-100004',
                    FINISHED,
                    finish_at='2020-09-04T13:56:51+00:00',
                ),
                _get_payload('111111-100005', CREATED),
                _get_payload(
                    '111111-100005',
                    FINISHED,
                    finish_at='2020-09-04T16:56:51+00:00',
                ),
                _get_payload('111111-100006', CREATED),
                _get_payload(
                    '111111-100006',
                    FINISHED,
                    finish_at='2020-09-04T20:56:51+00:00',
                ),
            ],
            [
                (123, datetime.date(2020, 9, 4), 6),
                (124, datetime.date(2020, 5, 24), 10),
            ],
            id='return one with multi in one day',
        ),
        pytest.param(
            [
                _get_payload('111111-100000', CREATED),
                _get_payload(
                    '111111-100001',
                    FINISHED,
                    finish_at='2020-09-04T15:56:51+00:00',
                ),
                _get_payload('111111-100001', CREATED),
                _get_payload('111111-100003', CANCELLED),
                _get_payload('111111-100010', CREATED),
                _get_payload(
                    '111111-100010',
                    FINISHED,
                    finish_at='2020-09-04T23:56:51+00:00',
                ),
                _get_payload('111111-100011', CREATED),
                _get_payload(
                    '111111-100011',
                    FINISHED,
                    finish_at='2020-09-05T15:56:51+00:00',
                ),
            ],
            [
                (123, datetime.date(2020, 9, 4), 1),
                (123, datetime.date(2020, 9, 5), 2),
                (124, datetime.date(2020, 5, 24), 10),
            ],
            id='multiple orders and border date',
        ),
        pytest.param(
            [
                _get_payload('111111-100011', CREATED, place_id=124),
                _get_payload(
                    '111111-100011',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T15:56:51+00:00',
                ),
            ],
            [(124, datetime.date(2020, 5, 24), 11)],
            id='already db add counter',
        ),
        pytest.param(
            [
                _get_payload('111111-100011', CREATED, place_id=124),
                _get_payload(
                    '111111-100011',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T15:56:51+00:00',
                ),
                _get_payload('111111-100015', CREATED, place_id=124),
                _get_payload(
                    '111111-100015',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T20:56:51+00:00',
                ),
                _get_payload('111111-100016', CREATED, place_id=124),
                _get_payload(
                    '111111-100016',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T23:56:51+00:00',
                ),
                _get_payload('111111-100018', CREATED, place_id=124),
                _get_payload(
                    '111111-100018',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-30T15:56:51+00:00',
                ),
                _get_payload('111111-100020', CREATED, place_id=124),
                _get_payload(
                    '111111-100020',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-30T17:56:51+00:00',
                ),
            ],
            [
                (124, datetime.date(2020, 5, 24), 11),
                (124, datetime.date(2020, 5, 25), 2),
                (124, datetime.date(2020, 5, 30), 2),
            ],
            id='already db add counter diff date',
        ),
        pytest.param(
            [
                _get_payload('111111-100011', CREATED, place_id=123),
                _get_payload(
                    '111111-100011',
                    FINISHED,
                    place_id=123,
                    finish_at='2020-05-24T15:50:51+00:00',
                ),
                _get_payload('111111-200015', CREATED, place_id=124),
                _get_payload(
                    '111111-200015',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T15:56:51+00:00',
                ),
                _get_payload('111111-300015', CREATED, place_id=125),
                _get_payload(
                    '111111-300015',
                    FINISHED,
                    place_id=125,
                    finish_at='2020-05-24T15:58:51+00:00',
                ),
                _get_payload('111111-400015', CREATED, place_id=126),
                _get_payload(
                    '111111-400015',
                    FINISHED,
                    place_id=126,
                    finish_at='2020-05-24T15:59:51+00:00',
                ),
                _get_payload('111111-400015', CREATED, place_id=126),
                _get_payload(
                    '111111-400015',
                    FINISHED,
                    place_id=126,
                    finish_at='2020-05-24T16:01:51+00:00',
                ),
                _get_payload('111111-400015', CREATED, place_id=126),
                _get_payload(
                    '111111-400015',
                    CANCELLED,
                    place_id=126,
                    finish_at='2020-05-24T16:02:51+00:00',
                ),
            ],
            [
                (123, datetime.date(2020, 5, 24), 1),
                (124, datetime.date(2020, 5, 24), 11),
                (125, datetime.date(2020, 5, 24), 1),
                (126, datetime.date(2020, 5, 24), 2),
            ],
            id='add diff place in one time',
        ),
        pytest.param(
            [
                _get_payload('111111-100111', CREATED, place_id=124),
                _get_payload(
                    '111111-100111',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T14:56:51+00:00',
                ),
                _get_payload('111111-100211', CREATED, place_id=124),
                _get_payload(
                    '111111-100211',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T13:56:51+00:00',
                ),
                _get_payload('111111-100011', CREATED, place_id=124),
                _get_payload(
                    '111111-100011',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T15:56:51+00:00',
                ),
                _get_payload('111111-100015', CREATED, place_id=124),
                _get_payload(
                    '111111-100015',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T20:56:51+00:00',
                ),
                _get_payload('111111-100016', CREATED, place_id=124),
                _get_payload(
                    '111111-100016',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-24T23:56:51+00:00',
                ),
                _get_payload('111111-100018', CREATED, place_id=124),
                _get_payload(
                    '111111-100018',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-30T15:56:51+00:00',
                ),
                _get_payload('111111-100020', CREATED, place_id=124),
                _get_payload(
                    '111111-100020',
                    FINISHED,
                    place_id=124,
                    finish_at='2020-05-30T17:56:51+00:00',
                ),
            ],
            [
                (124, datetime.date(2020, 5, 24), 13),
                (124, datetime.date(2020, 5, 25), 2),
                (124, datetime.date(2020, 5, 30), 2),
            ],
            id='already db add multi counter diff date',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_order_counter_db(
        taxi_eats_place_subscriptions, lb_orders, expect, pgsql,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_place_subscriptions, lb_order)

    # wait for lb messages to be read
    await taxi_eats_place_subscriptions.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    cursor = await utils.db_get_counter(pgsql)
    assert list(cursor) == expect
