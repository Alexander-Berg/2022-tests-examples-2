# pylint: disable = W0621
import asyncio
import datetime

import pytest

ORDERS_LIFETIME = 1000
ORDERS_SET = [
    ('d1', 1, False, 'pending'),
    ('d2', 1, False, 'complete'),
    ('d3', 1, True, 'pending'),
    ('d4', 1, True, 'complete'),
]


@pytest.fixture
def cursor(pgsql):
    return pgsql['corp_billing_orders'].cursor()


def sql_order_to_json(order):
    schema = ['id', 'last_modified_at', 'status']
    json = {}
    for i, elem in enumerate(schema):
        json[elem] = order[i]
    return json


def get_incompleted_orders(cursor):
    exec_command = (
        'select id, last_modified_at, status '
        'from corp_billing_orders.payment_orders '
        'where status != \'complete\' '
        'or (status = \'complete\' '
        'and last_modified_at > now() - interval \'{} second\')'.format(
            ORDERS_LIFETIME,
        )
    )
    cursor.execute(exec_command)
    return [sql_order_to_json(x) for x in cursor]


def set_old_dates_to_orders(ids_to_update, cursor):
    old_date = datetime.datetime.now() - datetime.timedelta(
        seconds=(ORDERS_LIFETIME + 5),
    )
    ids_str = ', '.join(ids_to_update)
    cursor.execute(
        'update corp_billing_orders.payment_orders '
        'set last_modified_at = \'{}\' where id in ({});'.format(
            old_date, ids_str,
        ),
    )


def get_orders(cursor):
    cursor.execute(
        'select id, last_modified_at, status '
        'from corp_billing_orders.payment_orders',
    )
    return [sql_order_to_json(x) for x in cursor]


@pytest.mark.config(CORP_BILLING_ORDERS_SYNC_INTERVAL_MS=1)
async def test_deleting_disabled_by_default(
        _self_service, _build_orders_with_statuses, _push_orders,
):
    orders, statuses = _build_orders_with_statuses()
    state = _self_service(statuses)
    await _push_orders(orders)
    await asyncio.sleep(0.1)
    assert not state.service.requests


@pytest.mark.config(CORP_BILLING_ORDERS_LIFETIME=ORDERS_LIFETIME)
async def test_delete_old_orders(
        _self_service,
        _build_orders_with_statuses,
        _push_orders,
        _do_sync_until_finish,
        call_delete_orders,
        cursor,
):
    orders, statuses = _build_orders_with_statuses(ORDERS_SET)
    _self_service(statuses)
    await _push_orders(orders)
    await _do_sync_until_finish()
    set_old_dates_to_orders(['2', '3'], cursor)
    deleted_count = await call_delete_orders()
    assert deleted_count == 1
    assert get_orders(cursor) == get_incompleted_orders(cursor)
