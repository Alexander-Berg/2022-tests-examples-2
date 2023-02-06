import copy
import uuid

import pytest

from tests_grocery_cart import common

YANDEX_UID = 'some-uid-1'
TAXI_SESSION = 'taxi:5555'

BASIC_HEADERS = common.TAXI_HEADERS.copy()

BASIC_HEADERS['X-Yandex-UID'] = YANDEX_UID
BASIC_HEADERS['X-YaTaxi-Session'] = TAXI_SESSION

CART_ID = 'e6a59113-503c-4d3e-8c59-000000000020'
USER_TYPE = 'yandex_taxi'
USER_ID = '5555'
PERSONAL_PHONE_ID = 'personal-phone-id-123'
CREATED = '2020-03-13T00:50:00+0000'
BOUND_UIDS = ['some-uid']
BOUND_TAXI_SESSIONS = ['some-texi-sessions']
DELIVERY_TYPE = 'eats_dispatch'
DELIVERY_ZONE_TYPE = 'pedestrian'
PAYMENT_METHOD_TYPE = 'card'
PROMOCODE = 'LAVKA100'
CASHBACK_FLOW = 'charge'
CASHBACK_TO_PAY = '40'

DELIVERY_COST = '10'
MIN_ETA = 10
MAX_ETA = 15
ORDER_CONDITIONS_WITH_ETA = {
    'delivery_cost': DELIVERY_COST,
    'min_eta': MIN_ETA,
    'max_eta': MAX_ETA,
}

TIPS_AMOUNT = '5'
TIPS_AMOUNT_TYPE = 'absolute'

TIMESLOT_START = '2020-03-13T09:50:00+0000'
TIMESLOT_END = '2020-03-13T17:50:00+0000'
TIMESLOT_REQUEST_KIND = 'wide_slot'

ITEM_ID = '3564d458-9a8a-11ea-7681-314846475f02'
ITEM_PRICE = '299'
ITEM_QUANTITY = '3'
ITEM_TITLE = f'title for {ITEM_ID}'

ITEM = {
    'item_id': ITEM_ID,
    'price': ITEM_PRICE,
    'quantity': ITEM_QUANTITY,
    'title': ITEM_TITLE,
    'created': CREATED,
    'currency': 'RUB',
}

COLD_CART_RESPONSE = {
    'created': CREATED,
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'cart_version': 1,
    'order_id': 'order-id-1',
    'delivery_type': DELIVERY_TYPE,
    'payment_method_type': PAYMENT_METHOD_TYPE,
    'tips_amount': TIPS_AMOUNT,
    'tips_amount_type': TIPS_AMOUNT_TYPE,
    'items': [ITEM],
    'promocode': PROMOCODE,
    'user_type': USER_TYPE,
    'user_id': USER_ID,
    'cashback_flow': CASHBACK_FLOW,
    'timeslot_start': TIMESLOT_START,
    'timeslot_end': TIMESLOT_END,
    'timeslot_request_kind': TIMESLOT_REQUEST_KIND,
    'yandex_uid': YANDEX_UID,
    'personal_phone_id': PERSONAL_PHONE_ID,
    'bound_uids': BOUND_UIDS,
    'bound_sessions': BOUND_TAXI_SESSIONS,
    'session': TAXI_SESSION,
}

COLD_CHECKOUT_DATA = {
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'order_conditions_with_eta': ORDER_CONDITIONS_WITH_ETA,
    'depot_id': '91456',
    'cashback_to_pay': CASHBACK_TO_PAY,
    'delivery_zone_type': DELIVERY_ZONE_TYPE,
}


@pytest.fixture(name='cold_storage')
def _mock_cold_storage(grocery_cold_storage):
    class Context:
        def __init__(self):
            self.carts_response = copy.deepcopy(COLD_CART_RESPONSE)
            self.checkout_data = copy.deepcopy(COLD_CHECKOUT_DATA)

        def mock_cold_storage(self, checked_out):
            self.carts_response['checked_out'] = checked_out

            grocery_cold_storage.set_carts_response(
                items=[self.carts_response],
            )

            if checked_out:
                grocery_cold_storage.set_checkout_data_response(
                    items=[self.checkout_data],
                )

        def carts_times_called(self):
            return grocery_cold_storage.carts_times_called()

        def checkout_data_times_called(self):
            return grocery_cold_storage.checkout_data_times_called()

    context = Context()
    return context


async def test_takeout_load_pg_cart(overlord_catalog, cart, cold_storage):
    cold_storage.mock_cold_storage(checked_out=False)

    overlord_catalog.add_product(product_id=ITEM_ID, price=ITEM_PRICE)

    await cart.init(
        {ITEM_ID: {'q': ITEM_QUANTITY, 'p': ITEM_PRICE}},
        headers=BASIC_HEADERS,
    )

    cart.update_db(
        payment_method_type=PAYMENT_METHOD_TYPE,
        promocode=PROMOCODE,
        delivery_type=DELIVERY_TYPE,
        personal_phone_id=PERSONAL_PHONE_ID,
        tips_amount=TIPS_AMOUNT,
        tips_amount_type=TIPS_AMOUNT_TYPE,
        timeslot_start=TIMESLOT_START,
        timeslot_end=TIMESLOT_END,
        timeslot_request_kind=TIMESLOT_REQUEST_KIND,
        created=CREATED,
        cashback_flow=CASHBACK_FLOW,
        bound_uids=BOUND_UIDS,
        bound_sessions=BOUND_TAXI_SESSIONS,
    )

    response = await cart.takeout_load(cart_id=cart.cart_id)
    load_data = response['objects'][0]
    item_created = load_data['data']['cart_items'][0]['created']

    assert load_data['id'] == cart.cart_id
    assert load_data['data']['cart'] == _cart_data_response(created=CREATED)
    assert 'checkout_data' not in load_data['data']
    assert load_data['data']['cart_items'] == (
        _items_data_response(created=item_created, title=ITEM_ID)
    )
    assert load_data['sensitive_data'] == _sensitive_data_response()

    assert cold_storage.carts_times_called() == 0
    assert cold_storage.checkout_data_times_called() == 1


async def test_takeout_load_pg_checkout_data(
        cart,
        offers,
        experiments3,
        grocery_surge,
        eats_promocodes,
        grocery_coupons,
        grocery_p13n,
        cold_storage,
):
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        min_eta=str(MIN_ETA),
        max_eta=str(MAX_ETA),
        minimum_order='300',
        delivery={
            'cost': DELIVERY_COST,
            'next_cost': '50',
            'next_threshold': '350',
        },
    )

    eats_promocodes.set_valid(False)
    grocery_coupons.check_check_request()

    grocery_p13n.set_cashback_info_response(
        payment_available=True, balance='999999',
    )

    await cart.modify(['item_id_1'])
    await cart.set_cashback_flow(flow=CASHBACK_FLOW)
    await cart.checkout(cashback_to_pay=CASHBACK_TO_PAY)

    response = await cart.takeout_load(cart_id=cart.cart_id)
    response_data = response['objects'][0]
    assert response_data['data']['checkout_data'] == _checkout_data_response()

    assert cold_storage.carts_times_called() == 0
    assert cold_storage.checkout_data_times_called() == 0


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'grocery': 0.01}},
    CURRENCY_FORMATTING_RULES={'RUB': {'grocery': 2}},
)
async def test_takeout_load_pg_item_title(cart, overlord_catalog):
    overlord_catalog.add_product(product_id=ITEM_ID, price=ITEM_PRICE)

    await cart.modify({ITEM_ID: {'q': ITEM_QUANTITY, 'p': ITEM_PRICE}})
    await cart.checkout()

    response = await cart.takeout_load(cart_id=cart.cart_id)

    load_data = response['objects'][0]
    item_created = load_data['data']['cart_items'][0]['created']

    assert load_data['data']['cart_items'] == (
        _items_data_response(created=item_created, title=ITEM_TITLE)
    )


async def test_takeout_load_cold_storage_cart(cart, cold_storage):
    cold_storage.mock_cold_storage(checked_out=False)

    response = await cart.takeout_load(cart_id=CART_ID)
    load_data = response['objects'][0]

    assert load_data['id'] == CART_ID
    assert load_data['data']['cart'] == _cart_data_response()
    assert load_data['data']['cart_items'] == (
        _items_data_response(title=ITEM_TITLE)
    )
    assert 'checkout_data' not in load_data['data']
    assert load_data['sensitive_data'] == _sensitive_data_response()

    assert cold_storage.carts_times_called() == 1
    assert cold_storage.checkout_data_times_called() == 1


async def test_takeout_load_cold_storage_checkout_data(cart, cold_storage):
    cold_storage.mock_cold_storage(checked_out=True)

    response = await cart.takeout_load(cart_id=CART_ID)
    load_data = response['objects'][0]

    assert load_data['data']['checkout_data'] == _checkout_data_response()


async def test_404_response(cart, cold_storage):
    cart_id = str(uuid.uuid4())

    await cart.takeout_load(cart_id=cart_id, status_code=404)

    assert cold_storage.carts_times_called() == 1
    assert cold_storage.checkout_data_times_called() == 0


def _sensitive_data_response(**kwargs):
    return {
        'yandex_uid': YANDEX_UID,
        'taxi_session': TAXI_SESSION,
        'extra_data': {'user_type': USER_TYPE, 'user_id': USER_ID},
        'bound_uids': BOUND_UIDS,
        'bound_taxi_sessions': BOUND_TAXI_SESSIONS,
        'personal_phone_id': PERSONAL_PHONE_ID,
        **kwargs,
    }


def _cart_data_response(**kwargs):
    return {
        'created': CREATED,
        'delivery_type': DELIVERY_TYPE,
        'promocode': PROMOCODE,
        'payment_method_type': PAYMENT_METHOD_TYPE,
        'cashback_flow': CASHBACK_FLOW,
        'tips_amount': TIPS_AMOUNT,
        'tips_amount_type': TIPS_AMOUNT_TYPE,
        'timeslot_start': TIMESLOT_START,
        'timeslot_end': TIMESLOT_END,
        'timeslot_request_kind': TIMESLOT_REQUEST_KIND,
        **kwargs,
    }


def _checkout_data_response(**kwargs):
    return {
        'delivery_zone_type': DELIVERY_ZONE_TYPE,
        'cashback_to_pay': CASHBACK_TO_PAY,
        'delivery_info': {
            'cost': DELIVERY_COST,
            'max_eta': MAX_ETA,
            'min_eta': MIN_ETA,
        },
        **kwargs,
    }


def _items_data_response(**kwargs):
    return [
        {
            'price': ITEM_PRICE,
            'quantity': ITEM_QUANTITY,
            'created': CREATED,
            **kwargs,
        },
    ]
