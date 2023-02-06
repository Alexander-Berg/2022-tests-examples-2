# pylint: disable=too-many-lines

import datetime
import uuid

import pytest

from . import active_orders_models
from . import common
from . import consts
from . import experiments
from . import models

DEFAULT_DEPOT_ID = '11222'

FINISHED_DT = datetime.datetime(
    2020, 3, 13, 7, 25, 00, tzinfo=active_orders_models.UTC_TZ,
)
IN_COMPENSATION_FREEZE_DT = datetime.datetime(
    2020, 3, 13, 5, 19, 00, tzinfo=models.UTC_TZ,
)
OUT_OF_COMPENSATION_FREEZE_DT = datetime.datetime(
    2020, 3, 12, 7, 19, 00, tzinfo=models.UTC_TZ,
)

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


async def _do_insert(
        taxi_grocery_support,
        pgsql,
        grocery_depots,
        grocery_marketing=None,
        order_state='created',
        tracker=None,
        cart_total_price='100',
        ticket_queue=None,
        ticket_summary=None,
        ticket_tags=None,
        delivery_type='courier',
        order_finished_date=None,
        cancel_reason_type=None,
        cancel_reason_message=None,
        country_iso3='RUS',
        grocery_orders=None,
        grocery_cart=None,
        now=None,
        is_promised_compensation=False,
        yandex_uid=None,
        personal_phone_id='personal',
        not_canceled_orders_count=None,
        grocery_flow='grocery_flow_v3',
        app_info=None,
        vip_type=None,
):
    order = active_orders_models.ActiveOrder(
        pgsql,
        update_db=False,
        order_state=order_state,
        cart_total_price=cart_total_price,
        depot_id=DEFAULT_DEPOT_ID,
        yandex_uid=yandex_uid,
        country_iso3=country_iso3,
        order_finished_date=order_finished_date,
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
        personal_phone_id=personal_phone_id,
        vip_type=vip_type,
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=DEFAULT_DEPOT_ID,
        country_iso3=country_iso3,
    )

    cart_id = str(uuid.uuid4())
    if grocery_orders is not None:
        grocery_orders.add_order(order_id=order.order_id, cart_id=cart_id)
    if grocery_cart is not None:
        grocery_cart.add_cart(cart_id)

    if is_promised_compensation:
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
    request = {
        'order_id': order.order_id,
        'order_state': order.order_state,
        'order_info': {
            'order_created_date': order.order_created_date.isoformat(),
            'short_order_id': order.short_order_id,
            'city_name': order.city_name,
            'depot_id': DEFAULT_DEPOT_ID,
            'cart_total_price': order.cart_total_price,
            'personal_phone_id': order.personal_phone_id,
            'order_promise': order.order_promise,
            'delivery_eta': order.delivery_eta,
            'delivery_type': delivery_type,
            'grocery_flow_version': grocery_flow,
        },
    }
    if order.order_finished_date is not None:
        request['order_info'][
            'order_finished_date'
        ] = order.order_finished_date.isoformat()
    if app_info is not None:
        request['order_info']['app_info'] = app_info
    if order.cancel_reason_type is not None:
        request['order_info']['cancel_reason_type'] = order.cancel_reason_type
    if order.cancel_reason_message is not None:
        request['order_info'][
            'cancel_reason_message'
        ] = order.cancel_reason_message
    if order.yandex_uid is not None:
        request['order_info']['yandex_uid'] = order.yandex_uid
    if order.vip_type is not None:
        request['order_info']['vip_type'] = order.vip_type

    if tracker is not None:
        tracker.check_request(
            active_orders_models.get_tracker_request(
                order,
                ticket_queue,
                ticket_summary,
                ticket_tags,
                send_chatterbox=True,
            ),
        )

    if not_canceled_orders_count is not None and grocery_marketing is not None:
        grocery_marketing.add_user_tag(
            tag_name='total_orders_count',
            usage_count=not_canceled_orders_count,
            user_id=yandex_uid,
        )

    response = await taxi_grocery_support.post(
        '/processing/v1/order-support', json=request,
    )
    return response, order


@experiments.INFORMERS_CONFIG
async def test_insert_order(taxi_grocery_support, pgsql, grocery_depots):
    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_insert(
        taxi_grocery_support, pgsql, grocery_depots,
    )
    assert response.status_code == 200
    order.compare_with_db()


@pytest.mark.parametrize(
    'proactive_support_type, country_iso3',
    [
        ('late_order', 'RUS'),
        ('expensive_order', 'GBR'),
        ('vip_order', 'FRA'),
        ('canceled_order', 'ISR'),
        ('first_order', 'RUS'),
    ],
)
async def test_trigger(pgsql, proactive_support_type, country_iso3):
    active_orders_models.prepare_counter_table(pgsql=pgsql)
    active_orders_models.ActiveOrder(
        pgsql=pgsql,
        proactive_support_type=proactive_support_type,
        country_iso3=country_iso3,
        ticket_key='key',
        ticket_id='id',
        update_db=True,
    )
    assert (
        active_orders_models.get_number_of_created_tickets(
            pgsql=pgsql,
            proactive_support_type=proactive_support_type,
            country_iso3=country_iso3,
        )
        == 1
    )


@experiments.PROACTIVE_SUPPORT_FIRST_ORDERS_EXPERIMENT_WITH_FLOW
@pytest.mark.parametrize(
    'flow, app_info',
    [
        ('grocery_flow_v3', 'app_name=lavka_iphone'),
        ('grocery_flow_v3', 'app_name=lavket_android'),
        ('tristero_flow_v2', 'app_name=lavket_android'),
        ('tristero_flow_v2', 'app_name=lavka_iphone'),
    ],
)
async def test_flow_version(
        taxi_grocery_support,
        stq,
        grocery_marketing,
        pgsql,
        tracker,
        grocery_depots,
        flow,
        app_info,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='first_order',
        count=0,
        country_iso3='RUS',
    )
    personal_phone_id = 'personal'
    yandex_uid = 'yandex_uid'

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        grocery_marketing=grocery_marketing,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.FIRST_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        country_iso3='RUS',
        yandex_uid=yandex_uid,
        personal_phone_id=personal_phone_id,
        not_canceled_orders_count=0,
        grocery_flow=flow,
        app_info=app_info,
    )

    assert response.status_code == 200
    if flow == 'grocery_flow_v3' and app_info == 'app_name=lavka_iphone':
        order.update()
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'first_order'
        assert tracker.times_called() == 1
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='first_order',
                country_iso3='RUS',
            )
            == 1
        )
    else:
        assert tracker.times_called() == 0
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='first_order',
                country_iso3='RUS',
            )
            == 0
        )


@experiments.INFORMERS_CONFIG
@experiments.LATE_ORDERS_MANUAL_PROACTIVE_EXPERIMENT
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
async def test_late_order_proactive_support(
        taxi_grocery_support, pgsql, stq, grocery_depots, country_iso3,
):
    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_insert(
        taxi_grocery_support, pgsql, grocery_depots, country_iso3=country_iso3,
    )
    assert response.status_code == 200
    if country_iso3 == 'RUS':
        assert stq.grocery_support_proactive_support.times_called == 1
        _assert_stq(
            stq.grocery_support_proactive_support,
            task_id=order.order_id,
            order_id=order.order_id,
            ticket_queue='test_queue',
            summary='Заказ опаздывает',
            ticket_tags=['test_tag', 'another_test_tag'],
        )
    else:
        assert stq.grocery_support_proactive_support.times_called == 0


def _assert_stq(stq_handler, task_id=None, **vargs):
    stq_call = stq_handler.next_call()
    if task_id is not None:
        assert stq_call['id'] == task_id
    kwargs = stq_call['kwargs']
    for key in vargs:
        assert kwargs[key] == vargs[key], key


@experiments.INFORMERS_CONFIG
@experiments.PROACTIVE_SUPPORT_EXPENSIVE_ORDERS_EXPERIMENT
@pytest.mark.parametrize(
    'cart_total_price', [consts.PRICE_LIMIT, str(int(consts.PRICE_LIMIT) - 1)],
)
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize('proactive_counter', [0, 101])
async def test_expensive_order_support(
        taxi_grocery_support,
        pgsql,
        tracker,
        grocery_depots,
        cart_total_price,
        country_iso3,
        proactive_counter,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='expensive_order',
        count=proactive_counter,
        country_iso3=country_iso3,
    )
    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        cart_total_price=cart_total_price,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.EXPENSIVE_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        country_iso3=country_iso3,
    )
    assert response.status_code == 200
    order.update()

    if (
            proactive_counter < 100
            and cart_total_price >= consts.PRICE_LIMIT
            and country_iso3 == 'RUS'
    ):
        assert tracker.times_called() == 1
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'expensive_order'
        assert order.country_iso3 == country_iso3
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='expensive_order',
                country_iso3=country_iso3,
            )
            == proactive_counter + 1
        )
    else:
        assert order.proactive_support_type is None
        assert tracker.times_called() == 0
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='expensive_order',
                country_iso3=country_iso3,
            )
            == proactive_counter
        )


@experiments.INFORMERS_CONFIG
@experiments.PROACTIVE_SUPPORT_VIP_ORDERS_EXPERIMENT
@pytest.mark.parametrize('vip_type', [None, 'celebrate'])
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize('proactive_counter', [0, 101])
async def test_vip_order_support(
        taxi_grocery_support,
        pgsql,
        tracker,
        grocery_depots,
        vip_type,
        country_iso3,
        proactive_counter,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='vip_order',
        count=proactive_counter,
        country_iso3=country_iso3,
    )

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.VIP_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        country_iso3=country_iso3,
        vip_type=vip_type,
    )
    assert response.status_code == 200
    order.update()
    if (
            proactive_counter < 100
            and vip_type == 'celebrate'
            and country_iso3 == 'RUS'
    ):
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'vip_order'
        assert order.vip_type == 'celebrate'
        assert tracker.times_called() == 1
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='vip_order',
                country_iso3=country_iso3,
            )
            == proactive_counter + 1
        )
    else:
        assert order.proactive_support_type is None
        assert tracker.times_called() == 0
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='vip_order',
                country_iso3=country_iso3,
            )
            == proactive_counter
        )


@experiments.PROACTIVE_SUPPORT_FIRST_ORDERS_EXPERIMENT
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize(
    'user_order_count, proactive_counter', [(0, 0), (0, 101), (3, 0)],
)
async def test_first_order_support(
        taxi_grocery_support,
        pgsql,
        tracker,
        grocery_depots,
        grocery_tags,
        grocery_marketing,
        country_iso3,
        user_order_count,
        proactive_counter,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='first_order',
        count=proactive_counter,
        country_iso3=country_iso3,
    )
    personal_phone_id = 'personal'
    yandex_uid = 'yandex_uid'

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        grocery_marketing=grocery_marketing,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.FIRST_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        country_iso3=country_iso3,
        yandex_uid=yandex_uid,
        personal_phone_id=personal_phone_id,
        not_canceled_orders_count=user_order_count,
    )
    assert response.status_code == 200
    order.update()
    if (
            proactive_counter < 100
            and user_order_count < consts.FIRST_ORDER_COUNT
            and country_iso3 == 'RUS'
    ):
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'first_order'
        assert tracker.times_called() == 1
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='first_order',
                country_iso3=country_iso3,
            )
            == proactive_counter + 1
        )
    else:
        assert order.proactive_support_type is None
        assert tracker.times_called() == 0
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='first_order',
                country_iso3=country_iso3,
            )
            == proactive_counter
        )


@experiments.PROACTIVE_SUPPORT_FIRST_ORDERS_DELAYED_EXPERIMENT
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize(
    'user_order_count, proactive_counter', [(0, 0), (0, 101), (3, 0)],
)
async def test_first_order_support_with_delay(
        taxi_grocery_support,
        pgsql,
        tracker,
        grocery_depots,
        grocery_tags,
        stq,
        grocery_marketing,
        country_iso3,
        user_order_count,
        proactive_counter,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='first_order',
        count=proactive_counter,
        country_iso3=country_iso3,
    )
    personal_phone_id = 'personal'
    yandex_uid = 'yandex_uid'

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        grocery_marketing=grocery_marketing,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.FIRST_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        country_iso3=country_iso3,
        yandex_uid=yandex_uid,
        personal_phone_id=personal_phone_id,
        not_canceled_orders_count=user_order_count,
    )
    assert response.status_code == 200
    order.update()
    if country_iso3 == 'RUS' and user_order_count < consts.FIRST_ORDER_COUNT:
        assert stq.grocery_support_delayed_proactive_support.times_called == 1
        _assert_stq(
            stq.grocery_support_delayed_proactive_support,
            task_id=order.order_id,
            order_id=order.order_id,
            ticket_queue=consts.TICKET_QUEUE,
            summary=consts.FIRST_ORDER_SUMMARY,
            ticket_tags=['test_tag', 'another_test_tag'],
        )
    else:
        assert stq.grocery_support_proactive_support.times_called == 0


async def _do_update(
        taxi_grocery_support,
        pgsql,
        order_state,
        grocery_depots,
        delivery_eta,
        order_promise=None,
):
    order = active_orders_models.ActiveOrder(
        pgsql,
        update_db=True,
        order_state='created',
        order_pickuped_date=None,
        depot_id=DEFAULT_DEPOT_ID,
        delivery_eta=delivery_eta,
        order_promise=order_promise,
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=DEFAULT_DEPOT_ID,
        country_iso3='RUS',
    )

    if not delivery_eta:
        delivery_eta = 15
    request = {
        'order_id': order.order_id,
        'order_state': order_state,
        'order_info': {
            'order_pickuped_date': (
                active_orders_models.PICKUPED_DT.isoformat()
            ),
            'delivery_eta': delivery_eta,
            'depot_id': DEFAULT_DEPOT_ID,
        },
    }
    response = await taxi_grocery_support.post(
        '/processing/v1/order-support', json=request,
    )
    return response, order


@pytest.mark.now('2020-03-13T07:10:00+00:00')
@experiments.INFORMERS_CONFIG
@pytest.mark.parametrize(
    'order_state',
    [
        'dispatch_approved',
        'performer_found',
        'assembling',
        'assembled',
        'delivering',
    ],
)
async def test_update_order(
        taxi_grocery_support, pgsql, order_state, grocery_depots,
):
    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_update(
        taxi_grocery_support,
        pgsql,
        order_state,
        grocery_depots=grocery_depots,
        delivery_eta=None,
    )
    assert response.status_code == 200
    order.update()
    assert order.order_pickuped_date == active_orders_models.PICKUPED_DT
    assert order.delivery_eta == 15


@experiments.INFORMERS_CONFIG
@pytest.mark.parametrize('order_state', ['closed', 'canceled'])
async def test_remove_order(
        taxi_grocery_support, pgsql, order_state, grocery_depots,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql, update_db=True, order_state='delivering', country_iso3='RUS',
    )
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=DEFAULT_DEPOT_ID,
        country_iso3='RUS',
    )
    request = {
        'order_id': order.order_id,
        'order_state': order_state,
        'order_info': {'depot_id': DEFAULT_DEPOT_ID},
    }
    response = await taxi_grocery_support.post(
        '/processing/v1/order-support', json=request,
    )
    assert response.status_code == 200
    pg_db = pgsql['grocery_support']
    cursor = pg_db.cursor()

    cursor.execute(
        """
        select count(*) order_id from grocery_support.active_orders
        where order_id = %s
        """,
        [order.order_id],
    )
    result = cursor.fetchone()
    assert result
    (count,) = result
    assert count == 0


@experiments.INFORMERS_CONFIG
@pytest.mark.parametrize(
    'order_state',
    [
        None,
        'created',
        'dispatch_approved',
        'performer_found',
        'assembling',
        'assembled',
        'delivering',
        'closed',
        'canceled',
    ],
)
async def test_bad_request(taxi_grocery_support, grocery_depots, order_state):
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=DEFAULT_DEPOT_ID,
        country_iso3='RUS',
    )
    request = {
        'order_id': 'order_id',
        'order_state': order_state,
        'order_info': {'depot_id': DEFAULT_DEPOT_ID},
    }
    response = await taxi_grocery_support.post(
        '/processing/v1/order-support', json=request,
    )
    if order_state in [
            'dispatch_approved',
            'performer_found',
            'closed',
            'canceled',
            'assembling',
            'assembled',
    ]:
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@experiments.INFORMERS_CONFIG
@experiments.PROACTIVE_SUPPORT_EXPENSIVE_ORDERS_EXPERIMENT
@pytest.mark.parametrize('delivery_type', ['courier', 'rover', 'pickup'])
async def test_delivery_type_pickup(
        taxi_grocery_support, pgsql, tracker, grocery_depots, delivery_type,
):
    active_orders_models.prepare_counter_table(pgsql)

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        cart_total_price=consts.PRICE_LIMIT,
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.EXPENSIVE_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        delivery_type=delivery_type,
    )

    assert response.status_code == 200

    if delivery_type != 'pickup':
        order.update()
        assert tracker.times_called() == 1
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'expensive_order'
        assert order.country_iso3 == 'RUS'
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql, proactive_support_type='expensive_order',
            )
            == 1
        )
    else:
        assert tracker.times_called() == 0
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql, proactive_support_type='expensive_order',
            )
            == 0
        )


@experiments.INFORMERS_CONFIG
@experiments.LATE_ORDER_SITUATIONS
@pytest.mark.now(models.NOW)
@pytest.mark.parametrize('is_ml_compensation_issued', ['false', 'true'])
async def test_closed_order_support(
        taxi_grocery_support,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        now,
        is_ml_compensation_issued,
):
    active_orders_models.prepare_counter_table(pgsql)
    order = active_orders_models.ActiveOrder(
        pgsql=pgsql, update_db=True, order_state='dispatch_approved',
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

    if is_ml_compensation_issued:
        compensation_uid = str(uuid.uuid4())
        compensation_info['status'] = 'success'
        compensation = common.create_compensation_v2(
            pgsql,
            compensation_uid,
            compensation_maas_id,
            customer,
            [],
            None,
            compensation_info,
            'ml',
            order.order_id,
            rate,
            main_situation_code='test_code',
        )
        compensation.update_db()

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        order_state='closed',
        grocery_depots=grocery_depots,
        tracker=tracker,
        order_finished_date=FINISHED_DT,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='compensations'))
    if not is_ml_compensation_issued:
        assert len(events) == 2
        event = events[0]
        assert event.payload['order_id'] == order.order_id
        assert event.payload['reason'] == 'created'
        assert 'event_policy' not in event.payload

        compensation_event = events[1]
        assert compensation_event.payload['order_id'] == order.order_id
        assert compensation_event.payload['reason'] == 'compensation_promocode'
        assert (
            compensation_event.payload['event_policy']
            == COMPENSATION_EVENT_POLICY
        )
    else:
        assert not events


@pytest.mark.now(models.NOW)
@experiments.INFORMERS_CONFIG
@experiments.PROACTIVE_SUPPORT_CANCELED_ORDERS_EXPERIMENT
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'cancel_reason_type, cancel_reason_message',
    [
        ('failure', 'reserve_failed'),
        ('dispatch_failure', 'performer_not_found'),
    ],
)
@pytest.mark.parametrize('country_iso3', ['RUS', 'GBR'])
@pytest.mark.parametrize('proactive_counter', [0, 101])
async def test_canceled_order_support(
        taxi_grocery_support,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        cancel_reason_type,
        cancel_reason_message,
        country_iso3,
        proactive_counter,
):
    active_orders_models.prepare_counter_table(pgsql)
    active_orders_models.set_number_of_created_tickets(
        pgsql=pgsql,
        proactive_support_type='canceled_order',
        count=proactive_counter,
        country_iso3=country_iso3,
    )
    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        order_state='canceled',
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.CANCELED_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        order_finished_date=FINISHED_DT,
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
        country_iso3=country_iso3,
        grocery_orders=grocery_orders,
        grocery_cart=grocery_cart,
    )
    assert response.status_code == 200

    if (
            proactive_counter < 100
            and cancel_reason_type == 'dispatch_failure'
            and cancel_reason_message == 'performer_not_found'
            and country_iso3 == 'RUS'
    ):
        assert tracker.times_called() == 1
        order.update()
        assert order.ticket_id is not None
        assert order.ticket_key is not None
        assert order.proactive_support_type == 'canceled_order'
        assert order.country_iso3 == 'RUS'
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='canceled_order',
                country_iso3=country_iso3,
            )
            == proactive_counter + 1
        )

        assert stq.grocery_support_remove_active_order.times_called == 1
        _assert_stq(
            stq.grocery_support_remove_active_order,
            task_id=order.order_id,
            order_id=order.order_id,
        )
    else:
        assert order.proactive_support_type is None
        assert tracker.times_called() == 0
        order.assert_db_is_empty()
        assert (
            active_orders_models.get_number_of_created_tickets(
                pgsql=pgsql,
                proactive_support_type='canceled_order',
                country_iso3=country_iso3,
            )
            == proactive_counter
        )

        assert stq.grocery_support_remove_active_order.times_called == 0

    events = list(processing.events(scope='grocery', queue='compensations'))
    if (
            cancel_reason_type == 'failure'
            and cancel_reason_message == 'reserve_failed'
            and country_iso3 == 'RUS'
    ):
        assert len(events) == 2
        event = events[0]
        assert event.payload['order_id'] == order.order_id
        assert event.payload['reason'] == 'created'
        assert 'event_policy' not in event.payload

        compensation_event = events[1]
        assert compensation_event.payload['order_id'] == order.order_id
        assert compensation_event.payload['reason'] == 'compensation_promocode'
        assert (
            compensation_event.payload['event_policy']
            == COMPENSATION_EVENT_POLICY
        )
    else:
        assert not events


@pytest.mark.now(models.NOW)
@experiments.PROACTIVE_SUPPORT_CANCELED_ORDERS_EXPERIMENT
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
async def test_promised_compensation_in_canceled_order(
        taxi_grocery_support,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        now,
):
    cancel_reason_type = 'dispatch_failure'
    cancel_reason_message = 'performer_not_found'
    active_orders_models.prepare_counter_table(pgsql)

    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        order_state='canceled',
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.CANCELED_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        order_finished_date=FINISHED_DT,
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
        grocery_orders=grocery_orders,
        grocery_cart=grocery_cart,
        now=now,
        is_promised_compensation=True,
    )
    assert response.status_code == 200

    assert tracker.times_called() == 0
    order.assert_db_is_empty()
    assert (
        active_orders_models.get_number_of_created_tickets(
            pgsql=pgsql, proactive_support_type='canceled_order',
        )
        == 0
    )
    assert stq.grocery_support_remove_active_order.times_called == 0

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 2

    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'created'
    assert 'event_policy' not in event.payload

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == order.order_id
    assert compensation_event.payload['reason'] == 'compensation_promocode'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )


@experiments.INFORMERS_CONFIG
async def test_informer_task_started(
        taxi_grocery_support, pgsql, stq, grocery_depots,
):
    informers = [
        consts.LONG_SEARCH_INFORMER,
        consts.LONG_SEARCH_PROMOCODE_INFORMER,
    ]

    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_update(
        taxi_grocery_support,
        pgsql,
        'dispatch_approved',
        grocery_depots=grocery_depots,
        delivery_eta=None,
    )
    assert response.status_code == 200

    assert stq.grocery_support_check_informer.times_called == len(informers)
    for informer in informers:
        _assert_stq(
            stq.grocery_support_check_informer,
            task_id=order.order_id + '-' + informer,
            order_id=order.order_id,
            informer=informer,
        )


@experiments.EMPTY_PROMOCODE_INFORMERS_CONFIG
async def test_empty_informer_task_did_not_start(
        taxi_grocery_support, pgsql, stq, grocery_depots,
):
    informers = [consts.LONG_SEARCH_INFORMER]

    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_update(
        taxi_grocery_support,
        pgsql,
        'dispatch_approved',
        grocery_depots=grocery_depots,
        delivery_eta=None,
    )
    assert response.status_code == 200

    assert stq.grocery_support_check_informer.times_called == len(informers)
    for informer in informers:
        _assert_stq(
            stq.grocery_support_check_informer,
            task_id=order.order_id + '-' + informer,
            order_id=order.order_id,
            informer=informer,
        )


@pytest.mark.now(models.NOW)
@experiments.INFORMERS_CONFIG
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'order_promise, delivery_eta, informer, informer_sent',
    [
        (20, 35, consts.LONG_DELIVERY_INFORMER, True),
        (20, 25, consts.LONG_DELIVERY_INFORMER, False),
    ],
)
async def test_send_long_delivery_informer(
        taxi_grocery_support,
        pgsql,
        grocery_depots,
        mockserver,
        processing,
        order_promise,
        delivery_eta,
        informer,
        informer_sent,
):
    active_orders_models.prepare_counter_table(pgsql)

    response, order = await _do_update(
        taxi_grocery_support,
        pgsql,
        'delivering',
        grocery_depots=grocery_depots,
        delivery_eta=delivery_eta,
        order_promise=order_promise,
    )
    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if informer_sent:
        assert len(events) == 2
        informer_event = events[0]
        assert informer_event.payload['order_id'] == order.order_id
        assert informer_event.payload['reason'] == 'save_informer'
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


@pytest.mark.now(models.NOW)
@experiments.EMPTY_PROMOCODE_INFORMERS_CONFIG
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'order_promise, delivery_eta, informer, informer_sent',
    [(20, 45, consts.LONG_DELIVERY_INFORMER, True)],
)
async def test_send_long_delivery_informer_not_promocode(
        taxi_grocery_support,
        pgsql,
        grocery_depots,
        mockserver,
        processing,
        order_promise,
        delivery_eta,
        informer,
        informer_sent,
):
    active_orders_models.prepare_counter_table(pgsql)

    response, order = await _do_update(
        taxi_grocery_support,
        pgsql,
        'delivering',
        grocery_depots=grocery_depots,
        delivery_eta=delivery_eta,
        order_promise=order_promise,
    )
    assert response.status_code == 200

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
@experiments.PROACTIVE_SUPPORT_CANCELED_ORDERS_EXPERIMENT
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'last_compensation_dt, issuance_frozen',
    [
        (IN_COMPENSATION_FREEZE_DT, True),
        (OUT_OF_COMPENSATION_FREEZE_DT, False),
    ],
)
async def test_canceled_order_support_issuance_freeze(
        taxi_grocery_support,
        pgsql,
        stq,
        tracker,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        last_compensation_dt,
        issuance_frozen,
):
    cancel_reason_type = 'failure'
    cancel_reason_message = 'technical_issues'
    country_iso3 = 'RUS'

    compensation_uid = str(uuid.uuid4())
    customer = common.create_system_customer(pgsql, models.NOW_DT)
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        123,
        customer,
        created=last_compensation_dt,
        cancel_reason=cancel_reason_message,
    )
    compensation.update_db()

    active_orders_models.prepare_counter_table(pgsql)
    response, order = await _do_insert(
        taxi_grocery_support,
        pgsql,
        order_state='canceled',
        grocery_depots=grocery_depots,
        tracker=tracker,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_summary=consts.CANCELED_ORDER_SUMMARY,
        ticket_tags=consts.TICKET_TAGS,
        order_finished_date=FINISHED_DT,
        cancel_reason_type=cancel_reason_type,
        cancel_reason_message=cancel_reason_message,
        country_iso3=country_iso3,
        grocery_orders=grocery_orders,
        grocery_cart=grocery_cart,
        personal_phone_id=customer.personal_phone_id,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='compensations'))
    if not issuance_frozen:
        assert len(events) == 2
        event = events[0]
        assert event.payload['order_id'] == order.order_id
        assert event.payload['reason'] == 'created'
        assert 'event_policy' not in event.payload

        compensation_event = events[1]
        assert compensation_event.payload['order_id'] == order.order_id
        assert compensation_event.payload['reason'] == 'compensation_promocode'
        assert (
            compensation_event.payload['event_policy']
            == COMPENSATION_EVENT_POLICY
        )
    else:
        assert len(events) == 1

        compensation_event = events[0]
        assert compensation_event.payload['order_id'] == order.order_id
        assert (
            compensation_event.payload['reason'] == 'compensation_notification'
        )
        assert (
            compensation_event.payload['compensation_id'] == compensation_uid
        )
        assert (
            compensation_event.payload['compensation_type']
            == compensation.compensation_type
        )
