import copy

import pytest

from . import consts
from . import experiments

OTHER_ORDER_ID = 'other_order_id'
CART_ID = '32d82a0f-7da0-459c-ba24-12ec11f30c99'
OTHER_CART_ID = '42d82a0f-7da0-459c-ba24-12ec11f30c99'
LOCATION = {'lat': 39.60258, 'lon': 52.569089}
TIMESTAMP = '2020-03-03T10:04:37.646+00:00'

CART_RETRIEVE_RAW = 'cart_retrieve_raw'

TICKETS_PARAMETERS = {
    'ticket_queue': consts.TICKET_QUEUE,
    'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
    'create_chatterbox_ticket': True,
    'max_tickets_count': 100,
}


def _get_task_id(order_id, status, reschedule_count=None):
    task_id = '{}-{}-process-status-changed-events'.format(order_id, status)
    if reschedule_count is not None:
        task_id = task_id + '-reschedule-{}'.format(reschedule_count)
    return task_id


@pytest.fixture
def _run_stq(mockserver, stq_runner):
    async def _inner(
            status_change_infos,
            reschedule_count=None,
            exec_tries=None,
            expect_fail=False,
    ):
        assert status_change_infos

        await stq_runner.grocery_support_process_status_changed_events.call(
            task_id=_get_task_id(
                status_change_infos[0]['order_id'],
                status_change_infos[0]['order_status'],
            ),
            kwargs={
                'status_change_infos': status_change_infos,
                'reschedule_count': (
                    reschedule_count if reschedule_count else None
                ),
            },
            exec_tries=exec_tries,
            expect_fail=expect_fail,
        )

    return _inner


def _assert_stq(stq_handler, task_id=None, eta=None, **vargs):
    stq_call = stq_handler.next_call()
    if task_id is not None:
        assert stq_call['id'] == task_id
    if eta is not None:
        assert stq_call['eta'] == eta
    kwargs = stq_call['kwargs']
    for key in vargs:
        assert kwargs[key] == vargs[key], key


@pytest.mark.config(GROCERY_SUPPORT_PROACTIVE_ENABLE_STQ_RESCHEDULING=True)
@experiments.GROCERY_SUPPORT_PROACTIVE_OPTIONS
@pytest.mark.parametrize(
    'other_order_event',
    [
        'no_order_info',
        'no_cart',
        # 'no_orders_count',
        'no_depot',
        'underpriced',
        'is_old_user',
        None,
    ],
)
async def test_basic(
        _run_stq,
        grocery_orders,
        grocery_cart,
        grocery_marketing,
        grocery_depots,
        stq,
        other_order_event,
):
    status_change_info = {
        'order_id': 'order_id',
        'order_status': 'assembling',
        'timestamp': TIMESTAMP,
    }
    order = grocery_orders.add_order(
        order_id=status_change_info['order_id'],
        cart_id=CART_ID,
        status=status_change_info['order_status'],
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        country_iso3='RUS',
        location=LOCATION,
        depot_id='123',
    )
    cart = grocery_cart.add_cart(cart_id=order['cart_id'])
    cart.set_order_conditions(delivery_cost=1, max_eta=15)
    cart.set_client_price('700')
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=0,
        user_id=order['yandex_uid'],
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order['depot']['id'], region_id=213,
    )

    other_status_change_info = {
        'order_id': OTHER_ORDER_ID,
        'order_status': 'closed',
        'timestamp': TIMESTAMP,
    }
    if other_order_event != 'no_order_info':
        other_order = grocery_orders.add_order(
            order_id=other_status_change_info['order_id'],
            cart_id=OTHER_CART_ID,
            status=other_status_change_info['order_status'],
            yandex_uid='other_yandex_uid',
            personal_phone_id='other_personal_phone_id',
            country_iso3='ISR',
            location=LOCATION,
            depot_id='124',
        )
        other_cart = grocery_cart.add_cart(cart_id=other_order['cart_id'])
        other_cart.set_order_conditions(delivery_cost=1, max_eta=25)
        other_cart.set_client_price(
            '500' if other_order_event == 'underpriced' else '700',
        )
        if other_order_event == 'no_cart':
            other_cart.set_error_code(handler=CART_RETRIEVE_RAW, code=404)

        if other_order_event != 'no_orders_count':
            grocery_marketing.add_user_tag(
                tag_name='total_orders_count',
                usage_count=3 if other_order_event == 'is_old_user' else 0,
                user_id=other_order['yandex_uid'],
            )
        else:
            grocery_marketing.set_tag_retrieve_error_code(
                user_id=other_order['yandex_uid'], code=500,
            )

        if other_order_event != 'no_depot':
            grocery_depots.add_depot(
                depot_test_id=124,
                legacy_depot_id=other_order['depot']['id'],
                region_id=512,
            )

    await _run_stq(
        status_change_infos=[status_change_info, other_status_change_info],
    )
    _assert_stq(
        stq.grocery_support_proactive_expected_late_order,
        task_id='{}-{}'.format(order['order_id'], order['status']),
        order_id=order['order_id'],
        order_status=order['status'],
        **TICKETS_PARAMETERS,
    )

    if other_order_event is None:
        _assert_stq(
            stq.grocery_support_proactive_expected_late_order,
            task_id='{}-{}'.format(OTHER_ORDER_ID, other_order['status']),
            order_id=OTHER_ORDER_ID,
            order_status=other_order['status'],
            **TICKETS_PARAMETERS,
        )
    elif other_order_event in ['no_depot', 'underpriced', 'is_old_user']:
        # Nothing happens because experiment doesn't match
        pass
    else:
        _assert_stq(
            stq.grocery_support_process_status_changed_events,
            task_id=_get_task_id(
                OTHER_ORDER_ID,
                other_status_change_info['order_status'],
                reschedule_count=1,
            ),
            status_change_infos=[other_status_change_info],
        )


@experiments.GROCERY_SUPPORT_PROACTIVE_OPTIONS
@pytest.mark.parametrize(
    'order_event', ['status_mismatch', 'no_depot_id', 'pickup', 'parcel'],
)
async def test_invalid_order_data(
        _run_stq,
        grocery_orders,
        grocery_cart,
        grocery_marketing,
        grocery_depots,
        stq,
        order_event,
):
    status_change_info = {
        'order_id': 'order_id',
        'order_status': 'closed',
        'timestamp': TIMESTAMP,
    }
    order = grocery_orders.add_order(
        order_id=status_change_info['order_id'],
        cart_id=CART_ID,
        status=status_change_info['order_status']
        if order_event != 'status_mismatch'
        else 'assembled',
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        country_iso3='ISR',
        location=LOCATION,
        depot_id='123' if order_event != 'no_depot_id' else None,
    )
    cart = grocery_cart.add_cart(cart_id=order['cart_id'])
    cart.set_order_conditions(delivery_cost=1, max_eta=25)
    cart.set_client_price('700')
    if order_event == 'pickup':
        cart.set_delivery_type('pickup')
    if order_event == 'parcel':
        items = copy.deepcopy(cart.get_items())
        items[0].item_id = items[0].item_id + ':st-pa'
        cart.set_items(items)

    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=0,
        user_id=order['yandex_uid'],
    )

    if order_event != 'no_depot_id':
        grocery_depots.add_depot(
            depot_test_id=123,
            legacy_depot_id=order['depot']['id'],
            region_id=512,
        )

    other_status_change_info = {
        'order_id': OTHER_ORDER_ID,
        'order_status': 'assembling',
        'timestamp': TIMESTAMP,
    }
    other_order = grocery_orders.add_order(
        order_id=other_status_change_info['order_id'],
        cart_id=OTHER_CART_ID,
        status=other_status_change_info['order_status'],
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        country_iso3='RUS',
        location=LOCATION,
        depot_id='124',
    )
    other_cart = grocery_cart.add_cart(cart_id=other_order['cart_id'])
    other_cart.set_order_conditions(delivery_cost=1, max_eta=15)
    other_cart.set_client_price('700')
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=0,
        user_id=other_order['yandex_uid'],
    )
    grocery_depots.add_depot(
        depot_test_id=124,
        legacy_depot_id=other_order['depot']['id'],
        region_id=213,
    )

    await _run_stq(
        status_change_infos=[status_change_info, other_status_change_info],
    )

    # nothing should happen for the first order

    _assert_stq(
        stq.grocery_support_proactive_expected_late_order,
        task_id='{}-{}'.format(other_order['order_id'], other_order['status']),
        order_id=other_order['order_id'],
        order_status=other_order['status'],
        **TICKETS_PARAMETERS,
    )


@experiments.GROCERY_SUPPORT_PROACTIVE_OPTIONS
@pytest.mark.parametrize(
    'grocery_orders_status', ['assembled', 'delivering', 'closed'],
)
async def test_basic_assembled(
        _run_stq,
        grocery_orders,
        grocery_cart,
        grocery_marketing,
        grocery_depots,
        stq,
        grocery_orders_status,
):
    status_change_info = {
        'order_id': 'order_id',
        'order_status': 'assembled',
        'timestamp': TIMESTAMP,
    }
    order = grocery_orders.add_order(
        order_id=status_change_info['order_id'],
        cart_id=CART_ID,
        status=grocery_orders_status,
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        country_iso3='RUS',
        location=LOCATION,
        depot_id='123',
    )
    cart = grocery_cart.add_cart(cart_id=order['cart_id'])
    cart.set_order_conditions(delivery_cost=1, max_eta=15)
    cart.set_client_price('700')
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=0,
        user_id=order['yandex_uid'],
    )
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order['depot']['id'], region_id=213,
    )

    await _run_stq(status_change_infos=[status_change_info])
    if grocery_orders_status != 'closed':
        _assert_stq(
            stq.grocery_support_proactive_expected_late_order,
            task_id='{}-{}'.format(
                order['order_id'], status_change_info['order_status'],
            ),
            order_id=order['order_id'],
            order_status=status_change_info['order_status'],
            **TICKETS_PARAMETERS,
        )
    else:
        # nothing should happen
        pass


@pytest.mark.parametrize('exec_tries', [0, 1])
async def test_retry(_run_stq, grocery_orders, stq, exec_tries):
    status_change_info = {
        'order_id': 'order_id',
        'order_status': 'assembled',
        'timestamp': TIMESTAMP,
    }
    grocery_orders.set_get_info_bulk_response(status_code=500)
    await _run_stq(
        status_change_infos=[status_change_info],
        exec_tries=exec_tries,
        expect_fail=exec_tries == 0,
    )
