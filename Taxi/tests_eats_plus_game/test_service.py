# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_plus_game_plugins.generated_tests import *
from tests_eats_plus_game import storage

import datetime
import hashlib
import json
import psycopg2
import pytest

CREATED = 'created'
FINISHED = 'finished'
CANCELLED = 'cancelled'

PERIODIC_DB_CLEANUP_TASK_NAME = 'periodic-order-db-cleanup-task'
LOGBROKER_CONSUMER_NAME = 'order-client-events-consumer'
LOGBROKER_TASK_NAME = f'{LOGBROKER_CONSUMER_NAME}-lb_consumer'

LOGBROKER_CHUNK_CONSUMER_SETTINGS = {
    'enabled': True,
    'chunk_size': 2,
    'queue_timeout_ms': 50,
    'config_poll_period_ms': 1000,
}

EATS_ORDERSHISTORY_V1_GET_ORDERS_RESPONSE = {
    'orders': [
        {
            'order_id': '111111-100000',
            'place_id': 1337,
            'status': 'in_progress',
            'source': 'eda',
            'delivery_location': {'lat': 0, 'lon': 0},
            'total_amount': '123',
            'is_asap': False,
            'created_at': '2020-09-04T15:26:43+0000',
        },
    ],
}


def _get_payload(order_nr, order_event):
    payload = {'order_nr': order_nr, 'order_event': order_event}

    if order_event == CREATED:
        payload['created_at'] = '2020-09-04T15:26:43+0000'
        payload['order_type'] = 'order_type'
        payload['delivery_type'] = 'delivery_type'
        payload['shipping_type'] = 'delivery'
        payload['eater_id'] = '123'
        payload['eater_personal_phone_id'] = '123'
        payload['eater_passport_uid'] = '123'
        payload['promised_at'] = '2020-09-04T16:26:43+0000'
        payload['application'] = 'web'
        payload['place_id'] = '1337'
    elif order_event == FINISHED:
        payload['finished_at'] = '2020-09-04T15:59:51+0000'
    elif order_event == CANCELLED:
        payload['cancelled_at'] = '2020-09-04T16:59:51+0000'
        payload['cancellation_reason'] = 'not_ready'
        payload['cancelled_by'] = 'operator'
    else:
        raise Exception('unknown order_event {}'.format(order_event))

    return payload


def _merge_events(order_nr, events):
    payload = {}
    for order_event in events:
        payload.update(_get_payload(order_nr, order_event))
    return payload


@pytest.mark.config(
    EATS_PLUS_GAME_LOGBROKER_CHUNK_CONSUMER_SETTINGS=LOGBROKER_CHUNK_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        ([_get_payload('111111-100000', CREATED)], CREATED),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
    ],
)
async def test_finished_orders_propagation_to_enrichment_feed(
        taxi_eats_plus_game,
        pgsql,
        lb_orders,
        db_order_status,
        stq,
        stq_runner,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_plus_game, lb_order)

    # wait for lb messages to be read
    await taxi_eats_plus_game.run_task(LOGBROKER_TASK_NAME)

    # LogBroker machinery has called db stq under the hood, pump it
    for _ in range(stq.eats_plus_game_db_feed.times_called):
        next_call = stq.eats_plus_game_db_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_db_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    assert stq.eats_plus_game_enrichment_feed.times_called == (
        db_order_status == FINISHED
    )


async def _push_lb_order(taxi_eats_plus_game, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_plus_game.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': LOGBROKER_CONSUMER_NAME,
                'data': message,
                'topic': '/eda/processing/testing/order-client-events',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200


@pytest.mark.config(
    EATS_PLUS_GAME_LOGBROKER_CHUNK_CONSUMER_SETTINGS=LOGBROKER_CHUNK_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        ([_get_payload('111111-100000', CREATED)], CREATED),
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
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
    ],
)
async def test_logbroker_events_cause_db_ops(
        taxi_eats_plus_game,
        pgsql,
        lb_orders,
        db_order_status,
        stq,
        stq_runner,
):
    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_plus_game, lb_order)

    # wait for lb messages to be read
    await taxi_eats_plus_game.run_task(LOGBROKER_TASK_NAME)

    # LogBroker machinery has called db stq under the hood, pump it
    for _ in range(stq.eats_plus_game_db_feed.times_called):
        next_call = stq.eats_plus_game_db_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_db_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    cursor = pgsql['eats_plus_game'].cursor()
    cursor.execute(
        f"""SELECT status FROM eats_plus_game.orders WHERE order_nr='111111-100000'""",
    )
    fetched = cursor.fetchone()
    if db_order_status in [CANCELLED, FINISHED]:
        assert not fetched
    else:
        status = fetched[0]
        assert status == db_order_status


@pytest.mark.pgsql('eats_plus_game', files=['insert_order_from_year_ago.sql'])
async def test_periodic_db_cleanup_task(
        taxi_eats_plus_game_aiohttp, pgsql, stq, stq_runner,
):
    cursor = pgsql['eats_plus_game'].cursor()

    cursor.execute(
        f"""SELECT * FROM eats_plus_game.orders WHERE order_nr='111111-100000'""",
    )
    fetched = cursor.fetchone()
    assert fetched

    await taxi_eats_plus_game_aiohttp.run_task(PERIODIC_DB_CLEANUP_TASK_NAME)

    cursor.execute(
        f"""SELECT * FROM eats_plus_game.orders WHERE order_nr='111111-100000'""",
    )
    fetched = cursor.fetchone()
    assert not fetched


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1337,
            'business': 'restaurant',
            'country': {
                'id': 1,
                'name': 'foo',
                'code': 'FOO',
                'currency': {'sign': 'USD', 'code': '$'},
            },
            'categories': [{'id': 1234, 'name': 'category_1234'}],
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.config(
    EATS_PLUS_GAME_LOGBROKER_CHUNK_CONSUMER_SETTINGS=LOGBROKER_CHUNK_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        ([_get_payload('111111-100000', CREATED)], CREATED),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
    ],
)
async def test_logbroker_invocation_on_enrichment_completion(
        taxi_eats_plus_game,
        lb_orders,
        pgsql,
        stq,
        stq_runner,
        testpoint,
        db_order_status,
        mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eats_ordershistory_v1_get_orders(data):
        return EATS_ORDERSHISTORY_V1_GET_ORDERS_RESPONSE

    @testpoint('eats_plus_game_enrichment_feed_sent_logbroker_message')
    def on_stq_logbroker_send(data):
        pass

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_plus_game, lb_order)

    # wait for lb messages to be read
    await taxi_eats_plus_game.run_task(LOGBROKER_TASK_NAME)

    # LogBroker machinery has called db stq under the hood, pump it
    for _ in range(stq.eats_plus_game_db_feed.times_called):
        next_call = stq.eats_plus_game_db_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_db_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    # due to finished orders being processed, db stq has called enrichment stq, so pump it as well
    for _ in range(stq.eats_plus_game_enrichment_feed.times_called):
        next_call = stq.eats_plus_game_enrichment_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_enrichment_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    assert on_stq_logbroker_send.times_called == (db_order_status == FINISHED)


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1337,
            'business': 'restaurant',
            'country': {
                'id': 1,
                'name': 'foo',
                'code': 'FOO',
                'currency': {'sign': 'USD', 'code': '$'},
            },
            'categories': [{'id': 1234, 'name': 'category_1234'}],
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.config(
    EATS_PLUS_GAME_LOGBROKER_CHUNK_CONSUMER_SETTINGS=LOGBROKER_CHUNK_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
        ),
    ],
)
async def test_enrichment_correctness(
        taxi_eats_plus_game,
        lb_orders,
        pgsql,
        stq,
        stq_runner,
        testpoint,
        db_order_status,
        mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eats_ordershistory_v1_get_orders(data):
        return EATS_ORDERSHISTORY_V1_GET_ORDERS_RESPONSE

    @testpoint('eats_plus_game_enrichment_feed__enrichment_finished')
    def enriched_order(data):
        order_nr = '111111-100000'
        hashed_order_nr = hashlib.md5(order_nr.encode('utf-8')).hexdigest()
        assert data == {
            'created_timestamp': 1599231600,
            'eda_order': {
                'brand_id': '122333',
                'business': 'EDA_BUSINESS_TYPE_RESTAURANT',
                'categories': ['1234'],
                'order_id': hashed_order_nr,
                'place_id': '1337',
                'shipping': 'EDA_SHIPPING_TYPE_DELIVERY',
                'transaction': {
                    'cashback_gain': {
                        'amount': 0,
                        'currency': 'CURRENCY_INVALID',
                    },
                    'cashback_spend': {
                        'amount': 0,
                        'currency': 'CURRENCY_INVALID',
                    },
                    'price': {'amount': 12300, 'currency': 'CURRENCY_INVALID'},
                },
            },
            'id': hashed_order_nr,
            'platform': 'PLATFORM_WEB',
            'puid': 123,
            'type': 'EVENT_TYPE_EDA_ORDER',
        }

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_plus_game, lb_order)

    # wait for lb messages to be read
    await taxi_eats_plus_game.run_task(LOGBROKER_TASK_NAME)

    # LogBroker machinery has called db stq under the hood, pump it
    for _ in range(stq.eats_plus_game_db_feed.times_called):
        next_call = stq.eats_plus_game_db_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_db_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    # due to finished orders being processed, db stq has called enrichment stq, so pump it as well
    for _ in range(stq.eats_plus_game_enrichment_feed.times_called):
        next_call = stq.eats_plus_game_enrichment_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_enrichment_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    assert enriched_order.times_called == 1


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1337,
            'business': 'restaurant',
            'country': {
                'id': 1,
                'name': 'foo',
                'code': 'FOO',
                'currency': {'sign': 'USD', 'code': '$'},
            },
            'categories': [],
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
@pytest.mark.config(
    EATS_PLUS_GAME_LOGBROKER_CHUNK_CONSUMER_SETTINGS=LOGBROKER_CHUNK_CONSUMER_SETTINGS,
)
@pytest.mark.parametrize(
    'lb_orders,db_order_status, is_lavka',
    [
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
            True,
        ),
        (
            [
                _get_payload('111111-100000', CREATED),
                _merge_events('111111-100000', [CREATED, FINISHED]),
            ],
            FINISHED,
            False,
        ),
    ],
)
async def test_lavka_orders_using_its_flow(
        taxi_eats_plus_game,
        lb_orders,
        is_lavka,
        stq,
        stq_runner,
        testpoint,
        mockserver,
        db_order_status,
):
    @testpoint('eats_plus_game_enrichment_feed_sent_logbroker_message')
    def on_stq_logbroker_send(data):
        pass

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eats_ordershistory_v1_get_orders(data):
        return EATS_ORDERSHISTORY_V1_GET_ORDERS_RESPONSE

    for lb_order in lb_orders:
        if is_lavka:
            lb_order['order_type'] = 'lavka'
        await _push_lb_order(taxi_eats_plus_game, lb_order)

    # wait for lb messages to be read
    await taxi_eats_plus_game.run_task(LOGBROKER_TASK_NAME)

    # LogBroker machinery has called db stq under the hood, pump it
    for _ in range(stq.eats_plus_game_db_feed.times_called):
        next_call = stq.eats_plus_game_db_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_db_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    # due to finished orders being processed, db stq has called enrichment stq, so pump it as well
    for _ in range(stq.eats_plus_game_enrichment_feed.times_called):
        next_call = stq.eats_plus_game_enrichment_feed.next_call()
        next_task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.eats_plus_game_enrichment_feed.call(
            task_id=next_task_id, kwargs=kwargs,
        )

    # lavka orders should not be sent via logbroker, so check they were skipped
    assert on_stq_logbroker_send.times_called == int(not is_lavka)

    # lavka uses it's own stq task, check it's called
    assert stq.grocery_marketing_plus_game.times_called == int(is_lavka)
