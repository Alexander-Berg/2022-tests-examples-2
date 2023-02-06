import copy
from typing import Optional

import pytest

from . import active_orders_models
from . import consts


TICKET_QUEUE = 'queue'


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id='order_id',
            queue=TICKET_QUEUE,
            summary=consts.FIRST_ORDER_SUMMARY,
            tags=copy.deepcopy(consts.TICKET_TAGS),
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_support_delayed_proactive_support.call(
            task_id=order_id,
            kwargs={
                'order_id': order_id,
                'ticket_queue': queue,
                'ticket_tags': tags,
                'summary': summary,
                'max_number_of_tickets': 100,
                'create_chatterbox_ticket': True,
            },
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


async def test_basic(_run_stq, pgsql, tracker, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    tracker.check_request(
        active_orders_models.get_tracker_request(
            order,
            TICKET_QUEUE,
            consts.FIRST_ORDER_SUMMARY,
            copy.deepcopy(consts.TICKET_TAGS),
            send_chatterbox=True,
        ),
    )
    await _run_stq(order_id=order.order_id)
    order.update()
    assert tracker.times_called() == 1
    assert order.ticket_id is not None
    assert order.ticket_key is not None
    assert order.proactive_support_type == 'first_order'
    assert order.country_iso3 == 'RUS'
    assert (
        active_orders_models.get_number_of_created_tickets(
            pgsql=pgsql,
            proactive_support_type='first_order',
            country_iso3='RUS',
        )
        == 1
    )


async def test_no_order(_run_stq, pgsql, tracker, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=False, country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    await _run_stq(order_id=order.order_id)
    assert tracker.times_called() == 0
    assert (
        active_orders_models.get_number_of_created_tickets(
            pgsql=pgsql,
            proactive_support_type='late_order',
            country_iso3='RUS',
        )
        == 0
    )


async def test_ticket_created(_run_stq, pgsql, tracker, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql,
        proactive_support_type='late_order',
        country_iso3='RUS',
        ticket_id='ticket_id',
        ticket_key='ticket_key',
        update_db=True,
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    await _run_stq(order_id=order.order_id)
    assert tracker.times_called() == 0


async def test_created_ticket_failed(_run_stq, pgsql, tracker, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    tracker.set_response_code(500)
    await _run_stq(order_id=order.order_id, expect_fail=True)
    # attempts value from API_TRACKER_CLIENT_QOS
    assert tracker.times_called() == 3


async def test_order_state(_run_stq, pgsql, tracker, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql,
        order_state='canceled',
        country_iso3='RUS',
        update_db=True,
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    await _run_stq(order_id=order.order_id)
    assert tracker.times_called() == 0
