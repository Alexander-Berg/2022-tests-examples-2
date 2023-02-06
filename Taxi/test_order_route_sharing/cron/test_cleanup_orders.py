# pylint: disable=redefined-outer-name
from typing import Set

import pytest

from order_route_sharing.generated.cron import run_cron


def get_order_ids(pgsql) -> Set[str]:
    cursor = pgsql['order_route_sharing'].cursor()
    cursor.execute('SELECT order_id FROM order_route_sharing.sharing_keys')
    return {item[0] for item in cursor}


def check_phone_ids(pgsql):
    cursor = pgsql['order_route_sharing'].cursor()
    cursor.execute('SELECT * FROM order_route_sharing.phone_ids')
    assert not cursor.fetchall()


@pytest.mark.now('2020-04-04T10:05:00+03:00')
@pytest.mark.config(ORDER_ROUTE_SHARING_CLEANUP_TTL=3600)
async def test_cleanup_orders(pgsql):
    await run_cron.main(
        ['order_route_sharing.crontasks.cleanup_orders', '-t', '0'],
    )

    assert get_order_ids(pgsql) == {'order_1', 'order_2', 'order_4', 'order_6'}


@pytest.mark.now('2020-04-04T10:05:00+03:00')
@pytest.mark.config(ORDER_ROUTE_SHARING_CLEANUP_TTL_FOR_ANY_ORDER=3600)
async def test_cleanup_any_orders(pgsql):
    await run_cron.main(
        ['order_route_sharing.crontasks.cleanup_any_orders', '-t', '0'],
    )
    check_phone_ids(pgsql)
    assert get_order_ids(pgsql) == {'order_6'}
