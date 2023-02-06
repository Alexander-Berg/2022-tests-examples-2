import copy
import json
import uuid

# pylint: disable=import-error
from grocery_mocks.models import country as country_models
import pytest

from . import consts
from . import headers
from . import models
from . import order_log
from . import processing_noncrit
from .plugins import mock_grocery_payments

ITEM_ID_1 = 'item_id_1'
CURRENT_QUANTITY = '4'
NEW_QUANTITY_REMOVE = '1'
NEW_QUANTITY_ADD = '7'

BILLING_SETTING_VERSION = 'billing_settings'

CURRENT_ITEMS = [
    models.GroceryCartItem(
        item_id=ITEM_ID_1,
        quantity=CURRENT_QUANTITY,
        price='100',
        title='item_1',
    ),
    models.GroceryCartItem(
        item_id='item_id_2', quantity='4', price='100', title='item_2',
    ),
]

PAYMENT_METHOD = {'type': 'card', 'id': 'test_payment_method_id'}
ABSOLUTE_TIPS_AMOUNT = '10'
ABSOLUTE_TIPS = {'amount': ABSOLUTE_TIPS_AMOUNT, 'amount_type': 'absolute'}


def _get_new_quantity(correcting_type='remove'):
    if correcting_type == 'add':
        return NEW_QUANTITY_ADD
    return NEW_QUANTITY_REMOVE


def _get_corrected_items(correcting_type='remove'):
    return [
        models.GroceryCartItem(
            item_id=ITEM_ID_1,
            quantity=_get_new_quantity(correcting_type),
            price='100',
            title='item_1',
        ),
        models.GroceryCartItem(
            item_id='item_id_2', quantity='4', price='100', title='item_2',
        ),
    ]


def _get_correcting_items(correcting_type='remove'):
    return [
        {
            'item_id': ITEM_ID_1,
            'new_quantity': _get_new_quantity(correcting_type),
            'old_quantity': CURRENT_QUANTITY,
        },
    ]


def _check_correcting_payload_item(payload, expected_name, expected_count):
    expected_item = {'short_name': expected_name, 'count': expected_count}
    assert expected_item in payload['products']


def _get_event_by_reason(events, reason):
    for event in events:
        if event.payload['reason'] == reason:
            return event
    return None


def _get_correct_commit_request(
        order,
        correcting_items,
        correcting_type=None,
        correcting_source=None,
        payload=None,
):
    if payload is None:
        payload = {}

    request = {
        'order_id': order.order_id,
        'correcting_order_revision': order.order_revision,
        'correcting_cart_version': order.cart_version - 1,
        'correcting_items': correcting_items,
        'payload': payload,
    }

    if correcting_type:
        request['correcting_type'] = correcting_type
    if correcting_source:
        request['correcting_source'] = correcting_source

    return request


@pytest.fixture
def _prepare(pgsql, grocery_cart, grocery_payments, grocery_depots):
    def _do(
            country,
            correcting_type='remove',
            order_settings=None,
            order_status='assembling',
            tips_payment_flow=None,
    ):
        order = models.Order(
            pgsql=pgsql,
            status=order_status,
            billing_settings_version=BILLING_SETTING_VERSION,
            child_cart_id=str(uuid.uuid4()),
            order_settings=order_settings,
        )

        corrected_items = _get_corrected_items(correcting_type=correcting_type)
        tips = {**ABSOLUTE_TIPS, 'payment_flow': tips_payment_flow}

        grocery_cart.set_cart_data(
            cart_id=order.cart_id, cart_version=order.cart_version + 1,
        )
        grocery_cart.set_payment_method(PAYMENT_METHOD)
        grocery_cart.set_items(CURRENT_ITEMS)
        grocery_cart.set_correcting_type(correcting_type=correcting_type)
        grocery_cart.set_tips(tips)

        child_cart = grocery_cart.add_cart(cart_id=order.child_cart_id)
        child_cart.set_cart_data(
            cart_id=order.child_cart_id, cart_version=order.cart_version,
        )
        child_cart.set_items(corrected_items)
        child_cart.set_payment_method(PAYMENT_METHOD)
        child_cart.set_tips(tips)

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            country_iso3=country.country_iso3,
            currency=country.currency,
        )

        grocery_payments.check_update(
            order_id=order.order_id,
            operation_id='1',
            country_iso3=country.country_iso3,
            items_by_payment_types=[
                mock_grocery_payments.get_items_by_payment_type(
                    corrected_items, PAYMENT_METHOD,
                ),
            ],
            user_info=mock_grocery_payments.USER_INFO,
        )

        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )

        return order

    return _do


def _check_cancel_pipeline(order, processing, has_cancel_event):
    events = list(processing.events(scope='grocery', queue='processing'))

    if not has_cancel_event:
        assert not events
    else:
        assert len(events) == 1

        payload = events[0].payload
        assert payload['order_id'] == order.order_id
        assert payload['reason'] == 'cancel'
        assert payload['flow_version'] == 'grocery_flow_v1'
        assert payload['cancel_reason_type'] == 'failure'


def _check_order_edited_pipeline(order, processing, new_items):
    payload = processing_noncrit.check_noncrit_event(
        order_id=order.order_id, reason='order_edited', processing=processing,
    )
    order_log.check_order_log_payload(
        payload=payload,
        order=order,
        cart_items=new_items,
        depot=None,
        delivery_cost=None,
    )


@consts.COUNTRIES
@pytest.mark.parametrize(
    'correcting_type, order_status',
    [
        (None, 'assembling'),
        (None, 'delivering'),
        ('remove', 'assembling'),
        ('remove', 'delivering'),
        ('add', 'assembling'),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=False)
@pytest.mark.config(GROCERY_ORDERS_SEND_ORDER_EDITED_NOTIFICATION=True)
async def test_basic_commit(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        country,
        processing,
        _prepare,
        correcting_type,
        order_status,
):
    order = _prepare(
        country, correcting_type=correcting_type, order_status=order_status,
    )

    prev_cart_version = order.cart_version

    correcting_items = _get_correcting_items(correcting_type)

    grocery_payments.check_update(
        billing_settings_version=BILLING_SETTING_VERSION,
        user_info=mock_grocery_payments.USER_INFO,
    )

    request = _get_correct_commit_request(
        order,
        correcting_items,
        correcting_type=correcting_type,
        correcting_source='system',
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )
    order.update()

    assert response.status_code == 200

    order.check_order_history(
        'order_correcting_status',
        {
            'to_order_correcting': 'correcting_finished',
            'correcting_result': 'success',
            'correcting_items': [{'item_id': ITEM_ID_1, 'quantity': '3'}],
        },
    )
    assert order.cart_version == prev_cart_version + 1

    assert grocery_cart.correct_commit_times_called() == 1
    assert grocery_cart.retrieve_times_called() == 1
    assert grocery_payments.times_update_called() == 1

    _check_cancel_pipeline(order, processing, has_cancel_event=False)
    # we check current items here
    # because mock can't simulate /commit behaviour
    _check_order_edited_pipeline(order, processing, CURRENT_ITEMS)

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 2
    event = _get_event_by_reason(events, 'create_support_chat')

    assert event
    assert event.payload['code'] == 'order_edited'
    payload = event.payload['payload']
    assert (
        payload['operation_type'] == correcting_type
        if correcting_type
        else 'remove'
    )
    _check_correcting_payload_item(payload, 'item_1', '3')


@pytest.mark.parametrize(
    'order_revision_shift,cart_version_shift', [(1, 0), (0, 2)],
)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=False)
async def test_idempotency(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        processing,
        _prepare,
        order_revision_shift,
        cart_version_shift,
):
    order = _prepare(models.Country.Russia)
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': (
                order.order_revision - order_revision_shift
            ),
            'correcting_cart_version': order.cart_version - cart_version_shift,
            'correcting_items': _get_correcting_items(),
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == 200


@consts.COUNTRIES
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=False)
@pytest.mark.parametrize('error_code', [404, 409, 500])
async def test_commit_cart_failed(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        processing,
        country,
        _prepare,
        error_code,
):
    order = _prepare(country)

    grocery_cart.set_correct_commit_error(code=error_code)

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit',
        json={
            'order_id': order.order_id,
            'correcting_order_revision': order.order_revision,
            'correcting_cart_version': order.cart_version - 1,
            'correcting_items': _get_correcting_items(),
            'payload': {},
        },
    )

    order.update()

    assert response.status_code == 500
    assert grocery_payments.times_update_called() == 0

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events


@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=False)
@consts.COUNTRIES
@pytest.mark.parametrize('error_code', [400, 409, 500])
async def test_money_fail(
        taxi_grocery_orders,
        grocery_payments,
        country,
        processing,
        _prepare,
        error_code,
):
    order = _prepare(country)

    grocery_payments.set_error_code(
        handler=mock_grocery_payments.UPDATE, code=error_code,
    )

    request = _get_correct_commit_request(order, _get_correcting_items())
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )
    order.update()

    if error_code == 500:
        assert response.status_code == 500
        _check_cancel_pipeline(order, processing, has_cancel_event=False)
    else:
        assert response.status_code == 409
        _check_cancel_pipeline(order, processing, has_cancel_event=True)
        order.check_order_history(
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_finished',
                'correcting_result': 'fail',
            },
        )

    assert grocery_payments.times_update_called() == 1


@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=True)
@pytest.mark.parametrize('correcting_type', [None, 'remove', 'add'])
@consts.COUNTRIES
async def test_commit_in_set_state(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        country,
        processing,
        correcting_type,
        _prepare,
):
    order = _prepare(country, correcting_type=correcting_type)

    prev_cart_version = order.cart_version
    prev_order_version = order.order_version

    correcting_items = _get_correcting_items(correcting_type)

    grocery_payments.check_update(
        billing_settings_version=BILLING_SETTING_VERSION,
        user_info=mock_grocery_payments.USER_INFO,
    )

    request = _get_correct_commit_request(
        order, correcting_items, correcting_type=correcting_type,
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )
    order.update()

    assert response.status_code == 200

    if correcting_type is not None:
        assert order.correcting_type == correcting_type

    assert order.cart_version == prev_cart_version
    assert order.order_version == prev_order_version + 1

    assert grocery_cart.correct_commit_times_called() == 0
    assert grocery_cart.retrieve_times_called() == 1
    assert grocery_payments.times_update_called() == 1

    assert order.state == models.OrderState()

    _check_cancel_pipeline(order, processing, has_cancel_event=False)
    _check_order_edited_pipeline(
        order, processing, _get_corrected_items(correcting_type),
    )


@pytest.mark.config(GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=True)
@consts.TIPS_FLOW_MARK
async def test_tips_with_order(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        processing,
        _prepare,
        tips_payment_flow,
):
    correcting_type = 'remove'
    cart_tips_payment_flow = tips_payment_flow

    order = _prepare(
        country_models.Country.Russia,
        correcting_type=correcting_type,
        tips_payment_flow=cart_tips_payment_flow,
    )

    correcting_items = _get_correcting_items(correcting_type)
    items = copy.deepcopy(_get_corrected_items(correcting_type))

    if tips_payment_flow == consts.TIPS_WITH_ORDER_FLOW:
        items.append(
            models.GroceryCartItem(
                item_id='tips', price=ABSOLUTE_TIPS_AMOUNT, quantity='1',
            ),
        )

    grocery_payments.check_update(
        items_by_payment_types=[
            mock_grocery_payments.get_items_by_payment_type(
                items, PAYMENT_METHOD,
            ),
        ],
    )

    request = _get_correct_commit_request(
        order, correcting_items, correcting_type=correcting_type,
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )

    assert response.status_code == 200
    assert grocery_payments.times_update_called() == 1


def _prepare_order_and_items(_prepare, grocery_payments, correcting_type):
    order = _prepare(
        country_models.Country.Russia,
        correcting_type=correcting_type,
        order_status='assembling',
    )
    correcting_items = _get_correcting_items()
    grocery_payments.check_update(
        billing_settings_version=BILLING_SETTING_VERSION,
        user_info=mock_grocery_payments.USER_INFO,
    )
    return [order, correcting_items]


@pytest.mark.config(GROCERY_ORDERS_SEND_ORDER_EDITED_NOTIFICATION=False)
async def test_support_chat_disabled_by_config(
        taxi_grocery_orders, grocery_payments, processing, _prepare,
):
    correcting_type = 'remove'

    [order, correcting_items] = _prepare_order_and_items(
        _prepare, grocery_payments, correcting_type,
    )
    request = _get_correct_commit_request(
        order,
        correcting_items,
        correcting_type=correcting_type,
        correcting_source='system',
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )
    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not _get_event_by_reason(events, 'create_support_chat')


@pytest.mark.config(GROCERY_ORDERS_SEND_ORDER_EDITED_NOTIFICATION=True)
async def test_support_chat_disabled_by_correcting_source(
        taxi_grocery_orders, grocery_payments, processing, _prepare,
):
    correcting_type = 'remove'

    [order, correcting_items] = _prepare_order_and_items(
        _prepare, grocery_payments, correcting_type,
    )
    request = _get_correct_commit_request(
        order,
        correcting_items,
        correcting_type=correcting_type,
        correcting_source='admin',
    )
    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/commit', json=request,
    )
    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not _get_event_by_reason(events, 'create_support_chat')
