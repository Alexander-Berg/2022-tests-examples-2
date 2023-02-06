import copy
from typing import Optional
import uuid

import pytest

from . import active_orders_models
from . import common
from . import consts
from . import experiments
from . import models

TICKET_QUEUE = 'queue'

COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}

SAVE_INFORMER_EVENT_POLICY = {
    'error_after': models.THREE_MINUTES_FROM_NOW,
    'retry_interval': 30,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id='order_id',
            queue=TICKET_QUEUE,
            summary=consts.LATE_ORDER_SUMMARY,
            tags=copy.deepcopy(consts.TICKET_TAGS),
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_support_proactive_support.call(
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


async def test_basic(_run_stq, pgsql, tracker, grocery_depots, processing):
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
            consts.LATE_ORDER_SUMMARY,
            copy.deepcopy(consts.TICKET_TAGS),
            send_chatterbox=True,
        ),
    )
    await _run_stq(order_id=order.order_id)
    order.update()
    assert tracker.times_called() == 1
    assert order.ticket_id is not None
    assert order.ticket_key is not None
    assert order.proactive_support_type == 'late_order'
    assert order.country_iso3 == 'RUS'
    assert (
        active_orders_models.get_number_of_created_tickets(
            pgsql=pgsql,
            proactive_support_type='late_order',
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
        proactive_support_type='expensive_order',
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


@pytest.mark.now(models.NOW)
async def test_promised_compensation(
        _run_stq, pgsql, tracker, grocery_depots, grocery_orders, now,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )

    grocery_orders.add_order(order_id=order.order_id)
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    customer = common.create_system_customer(pgsql, now)
    rate = 15
    compensation_info = {
        'compensation_value': rate,
        'numeric_value': str(rate),
        'status': 'in_progress',
    }
    source = 'proactive_support'
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [],
        None,
        compensation_info,
        source,
        order.order_id,
        rate,
        is_promised=True,
    )
    compensation.update_db()

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


@pytest.mark.now(models.NOW)
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@experiments.LATE_ORDERS_MANUAL_PROACTIVE_EXPERIMENT
@pytest.mark.parametrize(
    'grocery_flow_version, informers_sent',
    [('grocery_flow_v3', True), ('tristero_flow_v2', False)],
)
async def test_send_informer(
        _run_stq,
        pgsql,
        tracker,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        mockserver,
        grocery_flow_version,
        informers_sent,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    cart_id = str(uuid.uuid4())
    grocery_orders.add_order(
        order_id=order.order_id,
        cart_id=cart_id,
        grocery_flow_version=grocery_flow_version,
        status='draft',
    )
    grocery_cart.add_cart(cart_id=cart_id)

    await _run_stq(order_id=order.order_id)

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if informers_sent:
        assert len(events) == 2

        informer_event = events[0]
        assert informer_event.payload['order_id'] == order.order_id
        assert informer_event.payload['reason'] == 'save_informer'
        assert informer_event.payload['compensation_type'] == 'promocode'
        assert (
            informer_event.payload['event_policy']
            == SAVE_INFORMER_EVENT_POLICY
        )

        compensation_event = events[1]
        assert compensation_event.payload['order_id'] == order.order_id
        assert compensation_event.payload['reason'] == 'apology_notification'
        assert (
            compensation_event.payload['event_policy']
            == COMPENSATION_EVENT_POLICY
        )
    else:
        assert not events
