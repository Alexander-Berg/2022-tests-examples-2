# pylint: disable=C5521

from datetime import datetime

import pytest

from tests_grocery_order_log import models
from tests_grocery_order_log.helpers_retrieve import create_cart_items
from tests_grocery_order_log.helpers_retrieve import fetch_delivery_cost
from tests_grocery_order_log.helpers_retrieve import from_template

STQ_TASK_DELAY = 101325
YANDEX_UID = '4037511539'
YANDEX_UID2 = '0123456789'
TASK_ID = f'yandex_uid:{YANDEX_UID}'
HISTORY_SIZE = 5

SELECT_ARCHIVED_ORDER_IDS = """
SELECT
    order_id
FROM
    order_log.order_log
WHERE
    yandex_uid = %s
    AND can_be_archived IS TRUE
"""

SELECT_OTHER_ORDERS = """
SELECT
    order_id,
    can_be_archived
FROM
    order_log.order_log
WHERE
    yandex_uid = %s
"""

CLEAR_YANDEX_UIDS = """
UPDATE
    order_log.order_log
SET
    yandex_uid = NULL
WHERE
    yandex_uid = %s
RETURNING
    order_id
"""

SET_CAN_BE_ARCHIVED = """
WITH
order_ids AS (
    SELECT
        order_id
    FROM
        order_log.order_log
    WHERE
        yandex_uid = %s
    ORDER BY
        order_created_date DESC
    LIMIT
        ALL
    OFFSET
        %s
)
UPDATE
    order_log.order_log
SET
    can_be_archived = TRUE
FROM
    order_ids
WHERE
    order_log.order_id = order_ids.order_id
"""

GET_ORDERS_WO_YANDEX_UIDS = """
SELECT
    can_be_archived
FROM
    order_log.order_log
WHERE
    yandex_uid IS NULL
"""

NOW = pytest.mark.now('1970-02-01T12:00:00+00:00')

TRANSLATIONS = pytest.mark.translations(
    grocery_order_log={
        key: {'en': key}
        for key in ['TIN', 'Address', 'Yango Deli', 'Delivery']
    },
)

ARCHIVING_TESTSUITE_TASK_NAME = 'archiving'

PERSONAL_PHONE_ID = 'personal-phone-id'
USER_IDENTITY = {
    'user_identity': {
        'yandex_uid': YANDEX_UID,
        'bound_yandex_uids': [],
        'personal_phone_id': PERSONAL_PHONE_ID,
    },
}

HEADERS = {'Accept-Language': 'en'}


@pytest.fixture(name='logs')
async def _capture_logs(taxi_grocery_order_log):
    async with taxi_grocery_order_log.capture_logs() as capture:
        yield capture


def exp3_archiving_settings(*, enabled_source):
    return pytest.mark.experiments3(
        is_config=True,
        name='grocery_order_log_archiving_settings',
        consumers=['grocery-order-log/retrieve'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled': [enabled_source],
            'stq_task_delay': STQ_TASK_DELAY,
        },
    )


def _stringtime(timestring):
    if not timestring:
        return None
    if timestring[-3:-2] == ':':
        timestring = timestring[:-3] + timestring[-2:]
    return datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S.%f%z')


@pytest.fixture(name='orders')
async def _orders(pgsql, load_json):
    orders = load_json('grocery_order_log_retrieve_response.json')['orders']
    assert HISTORY_SIZE == len(orders)

    def _add_order(idx, order, order_id, yandex_uid, can_be_archived=None):
        cart_id = f'cart_id_{idx}'
        created_date = _stringtime(order['created_at'])
        finished_date = _stringtime(order['closed_at'])
        calculation = order['calculation']
        order_log = models.OrderLog(
            pgsql=pgsql,
            order_id=order_id,
            order_created_date=created_date,
            order_finished_date=finished_date,
            cart_id=cart_id,
            courier=order.get('contact', {}).get('courier', {}).get('name'),
            destination=order['destinations'][0],
            legal_entities=order['legal_entities'],
            receipts=order['receipts'],
            order_state=order['status'],
            cart_items=create_cart_items(
                calculation['addends'], from_template,
            ),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id=f'test_geo_id_{idx}',
            can_be_archived=can_be_archived,
        )
        order_log.update_db()

        order_log_index = models.OrderLogIndex(
            pgsql=pgsql,
            order_id=order_id,
            cart_id=cart_id,
            order_created_date=created_date,
            yandex_uid=yandex_uid,
        )
        order_log_index.update_db()

    for idx, order in enumerate(orders):
        _add_order(idx, order, order['order_id'], YANDEX_UID)

    _add_order(
        len(orders) + 0,
        orders[0],
        'order_id_1',
        YANDEX_UID2,
        can_be_archived=True,
    )
    _add_order(
        len(orders) + 1,
        orders[1],
        'order_id_2',
        YANDEX_UID2,
        can_be_archived=None,
    )

    return sorted(orders, key=lambda order: order['created_at'])


def _check_stq_client(stq):
    stq_queue = stq['grocery_order_log_archiving']
    assert stq_queue.times_called == 0


@TRANSLATIONS
@exp3_archiving_settings(enabled_source='retrieve')
@NOW
async def test_stq_client_retrieve(taxi_grocery_order_log, stq, now, orders):
    orderhistory_limit = 2
    assert orderhistory_limit <= HISTORY_SIZE

    request_json = {
        'range': {'count': orderhistory_limit},
        **USER_IDENTITY,
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={**HEADERS, 'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )

    assert response.status_code == 200

    order_idx = {order['order_id']: order for order in orders}
    last_order_ids = set(
        order['order_id'] for order in orders[-orderhistory_limit:]
    )
    for order in response.json()['orders']:
        order_id = order['order_id']
        assert order_id in last_order_ids
        last_order_ids.remove(order_id)
        assert order_idx[order_id] == order

    _check_stq_client(stq)


@TRANSLATIONS
@exp3_archiving_settings(enabled_source='insert')
@NOW
async def test_stq_client_insert(
        taxi_grocery_order_log, grocery_cold_storage, load_json, stq, now,
):
    request = load_json('../test_processing_insert/default_order_log.json')
    request['order_log_info']['order_type'] = 'grocery'
    request['order_log_info']['yandex_uid'] = YANDEX_UID
    request['order_log_info']['personal_phone_id'] = PERSONAL_PHONE_ID

    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )

    assert response.status_code == 200
    assert grocery_cold_storage.orders_times_called == 1
    assert grocery_cold_storage.prefetch_times_called == 0

    _check_stq_client(stq)


async def test_basic_stq_worker(taxi_grocery_order_log, stq_runner):
    await stq_runner.grocery_order_log_archiving.call(
        task_id=TASK_ID, kwargs=USER_IDENTITY,
    )


@TRANSLATIONS
@pytest.mark.parametrize(
    'use_can_be_archived', [True, False, 'disable_by_handler_id'],
)
@pytest.mark.parametrize(
    ['handler', 'handler_id'],
    [
        pytest.param(
            '/internal/orders/v1/retrieve',
            'internal_orders_v1_retrieve',
            id='internal_retrieve',
        ),
        pytest.param(
            '/internal/orders/v1/retrieve-raw',
            'internal_orders_v1_retrieve_raw',
            id='retrieve_raw',
        ),
        pytest.param(
            '/lavka/order-log/v1/retrieve',
            'lavka_order_log_v1_retrieve',
            id='retrieve',
        ),
    ],
)
async def test_use_can_be_archived(
        taxi_grocery_order_log,
        pgsql,
        taxi_config,
        experiments3,
        logs,
        orders,
        grocery_cold_storage,
        use_can_be_archived,
        handler,
        handler_id,
):
    orderhistory_limit = 2
    requested_count = orderhistory_limit + 2
    assert requested_count <= HISTORY_SIZE

    experiments3.add_config(
        name='grocery_order_log_use_can_be_archived',
        consumers=['grocery-order-log/retrieve'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': use_can_be_archived is True},
    )

    order_ids = [order['order_id'] for order in orders]
    if use_can_be_archived is True:
        grocery_cold_storage.set_get_request(
            item_ids=set(order_ids[-requested_count:-orderhistory_limit]),
        )
        grocery_cold_storage.set_prefetch_request(
            item_ids=set(
                order_ids[(-requested_count * 2) : -orderhistory_limit],
            ),
        )
        last_order_ids = set(order_ids[-orderhistory_limit:])
    else:
        grocery_cold_storage.set_get_request(item_ids=set())
        grocery_cold_storage.set_prefetch_request(item_ids=set())
        last_order_ids = set(order_ids[-requested_count:])

    if use_can_be_archived == 'disable_by_handler_id':
        handler_ids = []
    else:
        handler_ids = [handler_id]

    taxi_config.set(
        GROCERY_ORDER_LOG_ARCHIVING_SETTINGS={
            'skip_handling': False,
            'orderhistory_limit': orderhistory_limit,
            'use_index_table': False,
            'handler_ids': handler_ids,
        },
    )

    await taxi_grocery_order_log.invalidate_caches()

    db = pgsql['grocery_order_log']
    cursor = db.cursor()
    cursor.execute(SET_CAN_BE_ARCHIVED, [YANDEX_UID, orderhistory_limit])

    request_json = {
        'range': {'count': requested_count},
        **USER_IDENTITY,
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        handler, headers=HEADERS, json=request_json,
    )
    assert response.status_code == 200

    response_orders = response.json()['orders']
    if use_can_be_archived is True:
        assert len(response_orders) == orderhistory_limit
        assert grocery_cold_storage.orders_times_called == 1
        assert grocery_cold_storage.prefetch_times_called == 1
    else:
        assert len(response_orders) == requested_count
        assert grocery_cold_storage.orders_times_called == 0
        assert grocery_cold_storage.prefetch_times_called == 0

    for order in response_orders:
        order_id = order['order_id']
        assert order_id in last_order_ids
        last_order_ids.remove(order_id)

    assert logs.select(
        meta_type=handler,
        meta_user_uid=YANDEX_UID,
        personal_phone_id=PERSONAL_PHONE_ID,
    )


@TRANSLATIONS
@pytest.mark.parametrize('use_can_be_archived', [True, False])
async def test_use_can_be_archived_order_by_order_id(
        taxi_grocery_order_log,
        pgsql,
        taxi_config,
        experiments3,
        orders,
        grocery_cold_storage,
        use_can_be_archived,
):
    orderhistory_limit = 2
    requested_index = orderhistory_limit + 2
    assert requested_index <= HISTORY_SIZE

    experiments3.add_config(
        name='grocery_order_log_use_can_be_archived',
        consumers=['grocery-order-log/retrieve'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': use_can_be_archived},
    )

    if use_can_be_archived:
        handler_ids = ['internal_v1_order_log_v1_order_by_id']
    else:
        handler_ids = []

    taxi_config.set(
        GROCERY_ORDER_LOG_ARCHIVING_SETTINGS={
            'skip_handling': False,
            'orderhistory_limit': orderhistory_limit,
            'use_index_table': False,
            'handler_ids': handler_ids,
        },
    )

    await taxi_grocery_order_log.invalidate_caches()

    db = pgsql['grocery_order_log']
    cursor = db.cursor()
    cursor.execute(SET_CAN_BE_ARCHIVED, [YANDEX_UID, orderhistory_limit])

    order_id = orders[-requested_index]['order_id']
    response = await taxi_grocery_order_log.post(
        '/internal/v1/order-log/v1/order-by-id',
        headers=HEADERS,
        json={'order_id': order_id},
    )
    if use_can_be_archived:
        assert response.status_code == 404
        assert grocery_cold_storage.orders_times_called == 1
        assert grocery_cold_storage.prefetch_times_called == 1
    else:
        assert response.status_code == 200
        assert response.json()['order_id'] == order_id
        assert grocery_cold_storage.orders_times_called == 0
        assert grocery_cold_storage.prefetch_times_called == 0


async def test_periodic_archiving_task(
        taxi_grocery_order_log, pgsql, taxi_config, mocked_time, orders,
):
    """
    test depends on CURRENT_TIMESTAMP (value of 'updated' column),
    thus not going to use @pytest.mark.now
    along with mocked_time
    """

    expiration_interval = 2400  # hours
    chunk_size = 2  # rows

    taxi_config.set(
        GROCERY_ORDER_LOG_PERIODIC_ARCHIVING_TASK={
            'enabled': True,
            'cleanup_period': 1,
            'expiration_interval': expiration_interval,
            'chunk_size': chunk_size,
            'verbose_periodic': True,
            'max_order_ids_to_log': 1000,
        },
    )
    await taxi_grocery_order_log.invalidate_caches()

    db = pgsql['grocery_order_log']
    cursor = db.cursor()

    cursor.execute(CLEAR_YANDEX_UIDS, [YANDEX_UID])
    total_row_count = len(cursor.fetchall())

    def _get_row_count_can_be_archived():
        cursor.execute(GET_ORDERS_WO_YANDEX_UIDS)
        rows = cursor.fetchall()
        assert len(rows) == total_row_count
        return sum(map(lambda row: 1 if row[0] is True else 0, rows))

    await taxi_grocery_order_log.run_task(ARCHIVING_TESTSUITE_TASK_NAME)
    assert _get_row_count_can_be_archived() == 0

    # shortly before expiration
    mocked_time.sleep(expiration_interval * 60 * 60 - 10)
    await taxi_grocery_order_log.invalidate_caches()

    await taxi_grocery_order_log.run_task(ARCHIVING_TESTSUITE_TASK_NAME)
    assert _get_row_count_can_be_archived() == 0

    # right after expiration
    mocked_time.sleep(20)
    await taxi_grocery_order_log.invalidate_caches()

    assert total_row_count % chunk_size != 0
    for row_count in range(0, total_row_count, chunk_size):
        assert _get_row_count_can_be_archived() == row_count
        await taxi_grocery_order_log.run_task(ARCHIVING_TESTSUITE_TASK_NAME)

    assert _get_row_count_can_be_archived() == total_row_count
