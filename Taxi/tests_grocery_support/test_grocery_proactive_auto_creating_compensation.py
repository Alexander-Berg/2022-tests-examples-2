import copy
import datetime
import json
from typing import Optional
import uuid

import pytest

from . import active_orders_models
from . import common
from . import consts
from . import experiments
from . import models


COMPENSATION_PACK_ID = 23156
SITUATION_ID = 8957
TICKET_QUEUE = 'queue'
TICKET_TAGS = ['test_tag', 'another_test_tag']
TIMESTAMP = datetime.datetime(2020, 3, 13, 7, 25, 00, tzinfo=models.UTC_TZ)
SYSTEM_YANDEX_LOGIN = 'system_yandex_login'

LATE_ORDERS_AUTO_PROACTIVE_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_late_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'delay': 30,
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                },
                'auto_proactive_info': {
                    'can_process_automatically': True,
                    'compensations_info': [
                        {
                            'delay': 30,
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'percent',
                                'promocode_value': 15,
                            },
                        },
                        {
                            'delay': 10,
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'percent',
                                'promocode_value': 20,
                            },
                        },
                    ],
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'manual_proactive_info': {
                    'delay': 30,
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                },
            },
        },
    ],
    is_config=True,
)

CANCELED_ORDERS_AUTO_PROACTIVE_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_canceled_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'cancel_reasons': [
                        {
                            'type': 'dispatch_failure',
                            'message': 'performer_not_found',
                        },
                    ],
                    'task_ttl': 1,
                },
                'auto_proactive_info': {
                    'can_process_automatically': True,
                    'compensations_info': [
                        {
                            'cancel_reason': {
                                'type': 'dispatch_failure',
                                'message': 'performer_not_found',
                            },
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'fixed',
                                'promocode_value': 15,
                            },
                        },
                    ],
                },
            },
        },
        {
            'title': 'Israel',
            'predicate': {
                'init': {
                    'value': 'ISR',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'cancel_reasons': [
                        {
                            'type': 'dispatch_failure',
                            'message': 'performer_not_found',
                        },
                    ],
                    'task_ttl': 1,
                },
                'auto_proactive_info': {
                    'can_process_automatically': True,
                    'compensations_info': [
                        {
                            'cancel_reason': {
                                'type': 'dispatch_failure',
                                'message': 'performer_not_found',
                            },
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'percent',
                                'promocode_value': 15,
                            },
                        },
                    ],
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'manual_proactive_support': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'cancel_reasons': [
                        {
                            'type': 'dispatch_failure',
                            'message': 'performer_not_found',
                        },
                    ],
                    'task_ttl': 1,
                },
            },
        },
    ],
    is_config=True,
)


def _create_situation(
        pgsql, order_id, maas_id, situation_code, compensation_id=None,
):
    return models.SituationV2(
        pgsql,
        bound_compensation=compensation_id,
        source='system',
        has_photo=False,
        situation_id=str(uuid.uuid4()),
        maas_id=maas_id,
        order_id=order_id,
        situation_code=situation_code,
    )


def _create_customer(pgsql):
    return models.Customer(
        pgsql,
        personal_phone_id='p_phone_id',
        comments=[
            {
                'comment': 'Unicorn, be aware of a horn',
                'support_login': SYSTEM_YANDEX_LOGIN,
                'timestamp': TIMESTAMP.isoformat(),
            },
        ],
        phone_id='phone_id',
        yandex_uid='838101',
        antifraud_score='good',
    )


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            order_id='order_id',
            compensation_id=None,
            queue=TICKET_QUEUE,
            summary=consts.LATE_ORDER_SUMMARY,
            tags=copy.deepcopy(consts.TICKET_TAGS),
            expect_fail: bool = False,
            exec_tries: Optional[int] = None,
            reschedule_counter: int = 0,
    ):
        await stq_runner.grocery_support_proactive_support.call(
            task_id=order_id,
            kwargs={
                'order_id': order_id,
                'compensation_id': compensation_id,
                'ticket_queue': queue,
                'ticket_tags': tags,
                'summary': summary,
                'max_number_of_tickets': 100,
                'create_chatterbox_ticket': True,
            },
            expect_fail=expect_fail,
            exec_tries=exec_tries,
            reschedule_counter=reschedule_counter,
        )

    return _inner


@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize('compensation_id', ['compensation-id', None])
@pytest.mark.parametrize(
    'grocery_flow_version', ['tristero_flow_v2', 'grocery_flow_v2'],
)
@LATE_ORDERS_AUTO_PROACTIVE_EXPERIMENT
async def test_late_order_support(
        _run_stq,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        grocery_cart,
        grocery_orders,
        mockserver,
        processing,
        country_iso3,
        compensation_id,
        grocery_flow_version,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql,
        update_db=True,
        order_id='order_id',
        country_iso3=country_iso3,
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=order.depot_id,
        country_iso3=country_iso3,
    )
    cart_id = str(uuid.uuid4())
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    source = 'proactive_support'

    customer = _create_customer(pgsql)

    compensations_info = [
        {
            'compensation_value': 15,
            'numeric_value': '15',
            'status': 'in_progress',
        },
        {
            'compensation_value': 20,
            'numeric_value': '20',
            'status': 'in_progress',
        },
    ]
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [],
        None,
        compensations_info[0],
        source,
        order.order_id,
        is_promised=True,
    )

    grocery_orders.add_order(
        order_id=order.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        country_iso2='ru',
        country_iso3=country_iso3,
        cart_id=cart_id,
        locale='ru',
        grocery_flow_version=grocery_flow_version,
        status='draft',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_payment_method({'type': 'card'}, cart_id=cart_id)

    await _run_stq(order_id=order.order_id, compensation_id=compensation_id)

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if country_iso3 == 'GBR':
        assert tracker.times_called() == 1
        assert not events
        return
    if grocery_flow_version == 'tristero_flow_v2':
        assert tracker.times_called() == 0
        assert not events
        return
    assert tracker.times_called() == 0
    assert len(events) == 2

    informer_event = events[0]
    assert informer_event.payload['order_id'] == order.order_id
    assert informer_event.payload['reason'] == 'save_informer'
    assert informer_event.payload['compensation_type'] == 'promocode'

    order.update()
    assert order.proactive_support_type is None
    assert order.country_iso3 == country_iso3

    compensation.compare_with_db()

    if compensation_id is not None:
        # task rescheduled
        assert stq.grocery_support_proactive_support.times_called == 1
        await _run_stq(
            order_id=order.order_id,
            compensation_id=compensation_id,
            reschedule_counter=1,
        )
        # has no more compensations in exp
        assert stq.grocery_support_proactive_support.times_called == 1
        compensation.raw_compensation_info = json.dumps(compensations_info[1])
        compensation.compare_with_db()
    else:
        assert stq.grocery_support_proactive_support.times_called == 0


@LATE_ORDERS_AUTO_PROACTIVE_EXPERIMENT
@pytest.mark.parametrize('actual_status', ['draft', 'closed'])
async def test_not_actual_active_order_status(
        _run_stq,
        pgsql,
        tracker,
        grocery_cart,
        grocery_depots,
        grocery_orders,
        processing,
        actual_status,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, order_state='created', country_iso3='RUS', update_db=True,
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    grocery_orders.add_order(
        order_id=order.order_id,
        status=actual_status,
        grocery_flow_version='grocery_flow_v2',
    )

    compensation_id = str(uuid.uuid4())
    await _run_stq(order_id=order.order_id, compensation_id=compensation_id)
    assert tracker.times_called() == 0

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if actual_status == 'draft':
        assert len(events) == 2
    else:
        assert not events


def _assert_stq(stq_handler, task_id=None, **vargs):
    assert stq_handler.times_called == 1
    stq_call = stq_handler.next_call()
    if task_id is not None:
        assert stq_call['id'] == task_id
    kwargs = stq_call['kwargs']
    for key in vargs:
        assert kwargs[key] == vargs[key], key


@experiments.INFORMERS_CONFIG
@CANCELED_ORDERS_AUTO_PROACTIVE_EXPERIMENT
@pytest.mark.parametrize(
    'cancel_reason_type, cancel_reason_message',
    [
        ('failure', 'reserve_failed'),
        ('dispatch_failure', 'performer_not_found'),
    ],
)
@pytest.mark.parametrize(
    'promocode_type, country', [('percent', 'Israel'), ('fixed', 'Russia')],
)
async def test_canceled_order_support(
        taxi_grocery_support,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        cancel_reason_type,
        cancel_reason_message,
        grocery_cart,
        grocery_orders,
        mockserver,
        promocode_type,
        country,
):
    active_orders_models.prepare_counter_table(pgsql)
    ticket_summary = consts.CANCELED_ORDER_SUMMARY
    order = active_orders_models.ActiveOrder(
        pgsql,
        update_db=False,
        order_id='order_id',
        order_state='canceled',
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
    )
    if country == 'Russia':
        grocery_depots.add_depot(
            depot_test_id=123,
            legacy_depot_id=order.depot_id,
            country_iso3='RUS',
        )
    else:
        grocery_depots.add_depot(
            depot_test_id=123,
            legacy_depot_id=order.depot_id,
            country_iso3='ISR',
        )
    request = {
        'order_id': order.order_id,
        'order_state': order.order_state,
        'order_info': {
            'order_created_date': order.order_created_date.isoformat(),
            'short_order_id': order.short_order_id,
            'city_name': order.city_name,
            'depot_id': order.depot_id,
            'cart_total_price': order.cart_total_price,
            'personal_phone_id': order.personal_phone_id,
            'order_promise': order.order_promise,
            'delivery_eta': order.delivery_eta,
            'delivery_type': 'courier',
            'order_finished_date': TIMESTAMP.isoformat(),
            'cancel_reason_type': order.cancel_reason_type,
            'cancel_reason_message': order.cancel_reason_message,
        },
    }

    if tracker is not None:
        tracker.check_request(
            active_orders_models.get_tracker_request(
                order,
                TICKET_QUEUE,
                ticket_summary,
                TICKET_TAGS,
                send_chatterbox=True,
            ),
        )
    cart_id = str(uuid.uuid4())
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 0
    source = 'proactive_support'
    compensation_info = {
        'compensation_value': 15,
        'numeric_value': '15',
        'status': 'in_progress',
    }
    if promocode_type == 'fixed':
        compensation_info['currency'] = 'RUB'

    customer = _create_customer(pgsql)
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [],
        None,
        compensation_info,
        source,
        compensation_type='superVoucher'
        if promocode_type == 'fixed'
        else 'promocode',
        cancel_reason=cancel_reason_message,
    )

    grocery_orders.add_order(
        order_id=order.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        country_iso2='ru',
        country_iso3='RUS',
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_payment_method({'type': 'card'}, cart_id=cart_id)

    @mockserver.json_handler(
        '/processing/v1/grocery/compensations/create-event',
    )
    def mock_processing(_):
        return {'event_id': 'test_event_id'}

    response = await taxi_grocery_support.post(
        '/processing/v1/order-support', json=request,
    )

    assert response.status_code == 200
    assert tracker.times_called() == 0

    if (
            cancel_reason_type == 'dispatch_failure'
            and cancel_reason_message == 'performer_not_found'
    ):
        compensation.compare_with_db()
        assert mock_processing.times_called == 2
    else:
        order.assert_db_is_empty()
        assert stq.grocery_support_remove_active_order.times_called == 0


@CANCELED_ORDERS_AUTO_PROACTIVE_EXPERIMENT
@experiments.LATE_ORDER_SITUATIONS
async def test_compensation_already_issued(
        _run_stq, pgsql, grocery_depots, processing, tracker,
):
    country_iso3 = 'rus'
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql,
        update_db=True,
        order_id='order_id',
        country_iso3=country_iso3,
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=order.depot_id,
        country_iso3=country_iso3,
    )
    late_situation_code = 'test_code'

    customer = _create_customer(pgsql)
    compensation = common.create_compensation_v2(
        pgsql,
        str(uuid.uuid4()),
        0,
        customer,
        order_id=order.order_id,
        main_situation_code=late_situation_code,
    )
    compensation.update_db()

    await _run_stq(order_id=order.order_id)

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events
    assert tracker.times_called() == 0
