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
SENT = 'sent'

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

    if order_event == CREATED:
        payload['created_at'] = '2020-09-04T15:26:43+00:00'
        payload['order_type'] = 'order_type'
        payload['delivery_type'] = 'native'
        payload['shipping_type'] = 'delivery'
        payload['eater_id'] = '123123'
        payload['eater_personal_phone_id'] = '123123'
        payload['eater_passport_uid'] = '123123'
        payload['promised_at'] = '2020-09-04T16:26:43+00:00'
        payload['application'] = 'web'
        payload['place_id'] = '123123'
        payload['device_id'] = 'some_device_id'
        payload['payment_method'] = 'payment-method'
    elif order_event == PAYED:
        payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    elif order_event == CONFIRMED:
        payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    elif order_event == READY_TO_DELIVERY:
        payload['ready_to_delivery_at'] = '2020-09-04T15:36:51+00:00'
    elif order_event == TAKEN:
        payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    elif order_event == FINISHED:
        payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    elif order_event == CANCELLED:
        payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
        payload['cancellation_reason'] = 'not_ready'
        payload['cancelled_by'] = 'operator'
    elif order_event == PROMISE_CHANGED:
        payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    elif order_event == SENT:
        payload['sent_at'] = '2020-09-04T15:36:51+00:00'
    else:
        raise Exception('unknown order_event {}'.format(order_event))

    return payload


def _merge_events(order_nr, events):
    payload = {}
    for order_event in events:
        payload.update(_get_payload(order_nr, order_event))
    return payload


async def _push_lb_order(taxi_eats_proactive_support, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_proactive_support.post(
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


async def db_insert_order(pgsql, order_nr, order_status):
    cursor = pgsql['eats_proactive_support'].cursor()
    payload = """ {"application": "dummy_application",
                  "place_id": "dummy_place_id"}"""
    cursor.execute(
        f"""
            INSERT INTO eats_proactive_support.orders
              (order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
            VALUES 
              ('{order_nr}', '{order_status}', NOW(), 'dummy_order_type',
               'native', 'delivery', '{payload}');""",
    )


def assert_db_orders(psql, expected_db_orders_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.orders;')
    db_orders = cursor.fetchall()
    assert len(db_orders) == expected_db_orders_count


def assert_db_sensitive_data(psql, expected_db_orders_count):
    cursor = psql.cursor()
    cursor.execute(
        'SELECT * FROM eats_proactive_support.orders_sensitive_data;',
    )
    db_orders_data = cursor.fetchall()
    assert len(db_orders_data) == expected_db_orders_count


def assert_db_order_cancellations(psql, expected_db_order_cancellations_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.order_cancellations;')
    db_orders = cursor.fetchall()
    assert len(db_orders) == expected_db_order_cancellations_count


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
            ],
            PAYED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
            ],
            CONFIRMED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, TAKEN]),
            ],
            TAKEN,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, CANCELLED]),
            ],
            CANCELLED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PROMISE_CHANGED]),
            ],
            CREATED,
        ),
        (
            [
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
                _merge_events('111111-100000', [CREATED, PAYED]),
            ],
            PAYED,
        ),
        (
            [
                _merge_events('111111-100000', [CREATED, PAYED]),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
            ],
            CONFIRMED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, PAYED]),
                _merge_events('111111-100000', [CREATED, CONFIRMED]),
                _merge_events('111111-100000', [CREATED, TAKEN]),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
        (
            [
                _merge_events('111111-100000', [CREATED, PAYED]),
                _get_payload('111111-100000', CREATED),
            ],
            PAYED,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, READY_TO_DELIVERY]),
            ],
            READY_TO_DELIVERY,
        ),
    ],
)
async def test_order_save_db(
        taxi_eats_proactive_support, pgsql, lb_orders, db_order_status,
):
    order_nr = '111111-100000'
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""SELECT status FROM eats_proactive_support.orders WHERE order_nr='{order_nr}'""",
    )
    status = cursor.fetchone()[0]
    assert status == db_order_status


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'db_order_nr,db_order_status,lb_orders,expected_db_orders',
    [
        (
            '111111-100000',
            CREATED,
            [_merge_events('111111-100000', [CREATED, PAYED])],
            {'111111-100000': PAYED},
        ),
        (
            '111111-100000',
            PAYED,
            [_get_payload('111111-100000', CREATED)],
            {'111111-100000': PAYED},
        ),
        (
            '111111-100000',
            CONFIRMED,
            [_get_payload('111111-100000', CREATED)],
            {'111111-100000': CONFIRMED},
        ),
        (
            '111111-100000',
            TAKEN,
            [_get_payload('111111-100000', CREATED)],
            {'111111-100000': TAKEN},
        ),
        (
            '111111-100000',
            FINISHED,
            [_get_payload('111111-100000', CREATED)],
            {'111111-100000': FINISHED},
        ),
        (
            '111111-100000',
            CANCELLED,
            [_get_payload('111111-100000', CREATED)],
            {'111111-100000': CANCELLED},
        ),
        (
            '111111-100000',
            CREATED,
            [_merge_events('111111-100000', [CREATED, PROMISE_CHANGED])],
            {'111111-100000': CREATED},
        ),
        (
            '111111-100000',
            CREATED,
            [_merge_events('111111-100000', [CREATED, READY_TO_DELIVERY])],
            {'111111-100000': READY_TO_DELIVERY},
        ),
    ],
)
async def test_order_update_db(
        taxi_eats_proactive_support,
        pgsql,
        db_order_nr,
        db_order_status,
        lb_orders,
        expected_db_orders,
):
    await db_insert_order(pgsql, db_order_nr, db_order_status)

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    cursor = pgsql['eats_proactive_support'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'SELECT order_nr, status FROM eats_proactive_support.orders;',
    )
    db_orders = cursor.fetchall()

    assert len(db_orders) == len(expected_db_orders)
    for db_order in db_orders:
        assert db_order['order_nr'] in expected_db_orders
        assert db_order['status'] == expected_db_orders[db_order['order_nr']]


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,expected_db_orders_cancellation_count',
    [
        ([_get_payload('111111-100000', CREATED)], 0),
        ([_merge_events('111111-100000', [CREATED, CANCELLED])], 1),
        (
            [
                {'not_valid_message': 'not_valid_message'},
                _merge_events('111111-100000', [CREATED, CANCELLED]),
            ],
            1,
        ),
    ],
)
async def test_order_cancellation_save_db(
        taxi_eats_proactive_support,
        pgsql,
        lb_orders,
        expected_db_orders_cancellation_count,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert_db_order_cancellations(
        pgsql['eats_proactive_support'], expected_db_orders_cancellation_count,
    )


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS={
        'order_cancelled': {
            'events_settings': [
                {'enabled': True, 'delay_sec': 0, 'order_event': CANCELLED},
            ],
        },
    },
)
async def test_detector_stq_task_created(taxi_eats_proactive_support, stq):
    lb_orders = [
        _get_payload('111111-100000', CREATED),
        _merge_events('111111-100000', [CREATED, CANCELLED]),
    ]
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    assert stq.eats_proactive_support_detections.times_called == 1


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS={
        'order_cancelled': {
            'events_settings': [
                {'enabled': False, 'delay_sec': 0, 'order_event': CANCELLED},
            ],
        },
    },
)
async def test_detector_disabled_no_stq_task_created(
        taxi_eats_proactive_support, stq,
):
    lb_orders = [
        _get_payload('111111-100000', CREATED),
        _merge_events('111111-100000', [CREATED, CANCELLED]),
    ]
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.now('2020-09-04T20:59:50+03:00')
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS={
        'order_cancelled': {
            'events_settings': [
                {'enabled': True, 'delay_sec': 10, 'order_event': CANCELLED},
            ],
        },
    },
)
async def test_detector_delayed_stq_task_created(
        taxi_eats_proactive_support, stq,
):
    lb_orders = [
        _get_payload('111111-100000', CREATED),
        _merge_events('111111-100000', [CREATED, CANCELLED]),
    ]
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    assert stq.eats_proactive_support_detections.times_called == 1

    stq_payload = stq.eats_proactive_support_detections.next_call()
    assert stq_payload['eta'].isoformat() == '2020-09-04T18:00:00'


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_promise_changed_event_exist_order(
        taxi_eats_proactive_support, pgsql,
):
    order_nr = '111111-100000'
    await db_insert_order(pgsql, order_nr, CREATED)
    await _push_lb_order(
        taxi_eats_proactive_support,
        _merge_events(order_nr, [CREATED, PROMISE_CHANGED]),
    )

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""SELECT promised_at FROM eats_proactive_support.orders WHERE order_nr='{order_nr}'""",
    )
    db_promised_at = cursor.fetchone()[0]
    assert db_promised_at.isoformat() == '2020-09-04T20:59:51+03:00'


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_sent_event(taxi_eats_proactive_support, pgsql):
    order_nr = '111111-100000'
    await db_insert_order(pgsql, order_nr, CREATED)
    await _push_lb_order(
        taxi_eats_proactive_support, _merge_events(order_nr, [CREATED, SENT]),
    )

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""SELECT sent_at FROM eats_proactive_support.orders WHERE order_nr='{order_nr}'""",
    )
    db_sent_at = cursor.fetchone()[0]
    assert db_sent_at.isoformat() == '2020-09-04T18:36:51+03:00'


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,expected_db_orders_count',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100001', [CREATED, PAYED]),
            ],
            2,
        ),
        (
            [
                {'not_valid_message': 'not_valid_message'},
                _merge_events('111111-100001', [CREATED, PAYED]),
            ],
            1,
        ),
    ],
)
async def test_order_save_db_different_orders(
        taxi_eats_proactive_support,
        pgsql,
        lb_orders,
        expected_db_orders_count,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert_db_orders(pgsql['eats_proactive_support'], expected_db_orders_count)
    assert_db_sensitive_data(
        pgsql['eats_proactive_support'], expected_db_orders_count,
    )


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_order_save_db_no_passport_uid(
        taxi_eats_proactive_support, pgsql,
):
    lb_orders = [
        _get_payload('111111-100000', CREATED),
        _get_payload('111111-100001', CREATED),
    ]
    del lb_orders[0]['eater_passport_uid']

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert_db_orders(pgsql['eats_proactive_support'], 2)
    assert_db_sensitive_data(pgsql['eats_proactive_support'], 2)


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
)
async def test_order_save_db_device_id(taxi_eats_proactive_support, pgsql):
    lb_orders = [
        _get_payload('111111-100000', CREATED),
        _get_payload('111111-100001', CREATED),
    ]
    del lb_orders[1]['device_id']

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_proactive_support, lb_order)

    # wait for lb messages to be read
    await taxi_eats_proactive_support.run_task(
        'order-client-events-consumer-lb_consumer',
    )
    assert_db_orders(pgsql['eats_proactive_support'], 2)
    assert_db_sensitive_data(pgsql['eats_proactive_support'], 2)

    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        """SELECT eater_device_id FROM eats_proactive_support.orders_sensitive_data
         ORDER BY order_nr ASC;""",
    )
    db_device_ids = cursor.fetchall()
    assert len(db_device_ids) == 2
    assert db_device_ids == [('some_device_id',), (None,)]
