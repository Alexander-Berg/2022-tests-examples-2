from typing import Optional
import uuid

import pytest

from . import active_orders_models
from . import common
from . import consts
from . import experiments
from . import models


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
            order_id,
            informer,
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
    ):
        await stq_runner.grocery_support_check_informer.call(
            task_id=order_id,
            kwargs={'order_id': order_id, 'informer': informer},
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.mark.now(models.NOW)
@experiments.INFORMERS_CONFIG
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
async def test_send_long_search_informer(
        _run_stq, pgsql, grocery_depots, mockserver, processing,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, order_state='dispatch_approved',
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )

    await _run_stq(
        order_id=order.order_id, informer=consts.LONG_SEARCH_INFORMER,
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 2

    informer_event = events[0]
    assert informer_event.payload['order_id'] == order.order_id
    assert informer_event.payload['reason'] == 'save_informer'
    assert informer_event.payload['event_policy'] == SAVE_INFORMER_EVENT_POLICY

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == order.order_id
    assert compensation_event.payload['reason'] == 'apology_notification'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )


@pytest.mark.now(models.NOW)
@experiments.INFORMERS_CONFIG
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'grocery_flow_version', ['tristero_flow_v2', 'grocery_flow_v2'],
)
async def test_send_long_search_promocode_informer(
        _run_stq,
        pgsql,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        mockserver,
        processing,
        now,
        grocery_flow_version,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, order_state='dispatch_approved',
    )
    grocery_orders.add_order(
        order_id=order.order_id, grocery_flow_version=grocery_flow_version,
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )

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
        is_promised=True,
    )

    await _run_stq(
        order_id=order.order_id,
        informer=consts.LONG_SEARCH_PROMOCODE_INFORMER,
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if grocery_flow_version == 'tristero_flow_v2':
        assert not events
        return
    assert len(events) == 2

    informer_event = events[0]
    assert informer_event.payload['order_id'] == order.order_id
    assert informer_event.payload['reason'] == 'save_informer'
    assert informer_event.payload['compensation_type'] == 'promocode'
    assert informer_event.payload['compensation_info'] == compensation_info
    assert informer_event.payload['event_policy'] == SAVE_INFORMER_EVENT_POLICY
    assert informer_event.payload['compensation_info'] == compensation_info

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == order.order_id
    assert compensation_event.payload['reason'] == 'apology_notification'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )

    compensation.compare_with_db()


@pytest.mark.now('2020-03-13T07:20:00+00:00')
@experiments.INFORMERS_CONFIG
@pytest.mark.parametrize(
    'order_state, informer',
    [
        ('performer_found', consts.LONG_SEARCH_INFORMER),
        ('performer_found', consts.LONG_SEARCH_PROMOCODE_INFORMER),
    ],
)
async def test_status_changed(
        _run_stq,
        pgsql,
        grocery_depots,
        mockserver,
        processing,
        order_state,
        informer,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, order_state=order_state,
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )

    await _run_stq(order_id=order.order_id, informer=informer)
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events


@experiments.INFORMERS_CONFIG
@experiments.LATE_ORDER_SITUATIONS
@pytest.mark.now(models.NOW)
async def test_compensation_already_issued(
        _run_stq, pgsql, grocery_depots, grocery_orders, processing, now,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, order_state='dispatch_approved',
    )
    grocery_orders.add_order(order_id=order.order_id)
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    late_situation_code = 'test_code'

    customer = common.create_system_customer(pgsql, now)
    compensation = common.create_compensation_v2(
        pgsql,
        str(uuid.uuid4()),
        0,
        customer,
        order_id=order.order_id,
        is_promised=True,
        main_situation_code=late_situation_code,
    )
    compensation.update_db()

    await _run_stq(
        order_id=order.order_id,
        informer=consts.LONG_SEARCH_PROMOCODE_INFORMER,
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events
