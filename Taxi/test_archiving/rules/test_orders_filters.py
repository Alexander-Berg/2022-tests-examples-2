# pylint: disable=protected-access
import datetime

import pytest

from archiving import cron_run
from archiving.rules.orders.filters import orders


@pytest.mark.parametrize(
    'order_id,expected',
    [
        ('order_need_disp_accept', False),
        ('order_decoupling_need_upd_transaction', False),
        ('order_decoupling_can_remove', True),
        ('order_decoupling_vat_included_can_remove', True),
    ],
)
async def test_can_be_moved_to_archive(
        cron_context,
        order_id,
        expected,
        replication_state_min_ts,
        fake_task_id,
        requests_handlers,
):
    replication_state_min_ts.apply(
        {'orders': ('updated', datetime.datetime(2018, 1, 2, 0, 0, 29))},
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, 'orders_hourly', fake_task_id,
    )
    archiver = next(iter(archivers.values()))
    orders_collection = await archiver.get_source()
    order = await orders_collection.find_one(order_id)
    date = datetime.datetime(2016, 1, 1)
    result = orders._can_be_moved_to_archive(order, date)
    assert result == expected
