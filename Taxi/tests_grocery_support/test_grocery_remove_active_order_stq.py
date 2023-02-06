from typing import Optional

import pytest

from . import active_orders_models as models

TICKET_QUEUE = 'queue'


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id='order_id',
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_support_remove_active_order.call(
            task_id=order_id,
            kwargs={'order_id': order_id},
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


async def test_basic(_run_stq, pgsql, grocery_depots):
    models.prepare_counter_table(pgsql)
    order = models.ActiveOrder(pgsql=pgsql, update_db=True)
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )

    await _run_stq(order_id=order.order_id)
    order.assert_db_is_empty()
    assert (
        models.get_number_of_created_tickets(
            pgsql=pgsql,
            proactive_support_type='canceled_order',
            country_iso3='RUS',
        )
        == 0
    )
