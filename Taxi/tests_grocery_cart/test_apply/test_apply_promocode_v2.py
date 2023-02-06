import copy
import decimal
import math
import string
import uuid

import pytest

from tests_grocery_cart import configs
from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

DISCOUNT_PERCENT = 30

DELIVERY_COST = 200

CART_ITEMS = {
    'test-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
    'beer-item': {'q': 1, 'p': keys.DEFAULT_PRICE},
    'medicine_id': {'q': 1, 'p': keys.DEFAULT_PRICE},
}


def _calc_cart_items_price(cart_items):
    price = decimal.Decimal(0)
    for _, item_cost in cart_items.items():
        price += item_cost['p'] * item_cost['q']

    return price


def _calc_discount(
        cart_items_total,
        discount,
        discount_type,
        discount_percent,
        discount_limit,
        lavka_cart_prices,
):

    calc_discount = decimal.Decimal(0)
    if discount_type == 'fixed':
        calc_discount = discount
    else:
        calc_discount = cart_items_total * discount_percent / 100

    promocode_rounding_value = decimal.Decimal(
        lavka_cart_prices.promocode_rounding_value,
    )

    calc_discount = (
        math.ceil(calc_discount / promocode_rounding_value)
        * promocode_rounding_value
    )

    if discount_limit is not None and discount_limit < calc_discount:
        calc_discount = discount_limit

    if cart_items_total < calc_discount:
        calc_discount = cart_items_total - decimal.Decimal(
            lavka_cart_prices.minimum_total_cost,
        )

    return calc_discount


@pytest.fixture(name='lavka_cart_prices')
def _lavka_cart_prices(experiments3):
    class Context:
        currency_min_value: string
        currency_precision: decimal.Decimal
        minimum_total_cost: string
        minimum_item_price: string
        promocode_rounding_value: string

        def set_values(
                self,
                currency_min_value='0.01',
                precision=1,
                minimum_total_cost='0',
                minimum_item_price='0',
                promocode_rounding_value='0.01',
        ):
            self.currency_min_value = currency_min_value
            self.currency_precision = precision
            self.minimum_total_cost = minimum_total_cost
            self.minimum_item_price = minimum_item_price
            self.promocode_rounding_value = promocode_rounding_value

            experiments3.add_config(
                name='lavka_cart_prices',
                consumers=['grocery-cart'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                default_value={
                    'currency_min_value': currency_min_value,
                    'currency_precision': precision,
                    'minimum_total_cost': minimum_total_cost,
                    'minimum_item_price': minimum_item_price,
                    'promocode_rounding_value': promocode_rounding_value,
                },
            )

    context = Context()
    context.set_values()
    return context


def _cart_prices_decimal(cart_prices, price_name):
    return decimal.Decimal(
        cart_prices[price_name].strip(' $SIGN$$CURRENCY$').replace(',', '.'),
    )


def _eats_check_request_translations(key, value):
    if key == 'cart_cost':
        return {'applyForAmount': value}
    if key == 'promocode':
        return {'code': value}

    if key == 'depot_id':
        return {'place': {'id': value}}

    return None


@pytest.fixture(name='promocode_info')
def _promocode_info(eats_promocodes, grocery_coupons):
    class Context:
        def set_grocery_data(
                self,
                discount,
                valid=True,
                discount_type='percent',
                discount_percent=DISCOUNT_PERCENT,
                discount_limit=None,
                check_request_additional_data=False,
        ):
            response = {
                'valid': valid,
                'error_message': '1',
                'promocode_info': {
                    'currency_code': 'RUB',
                    'format_currency': True,
                    'value': (
                        str(discount)
                        if discount_type == 'fixed'
                        else str(discount_percent)
                    ),
                    'type': discount_type,
                    'series_purpose': 'support',
                    'limit': (
                        None if discount_limit is None else str(discount_limit)
                    ),
                },
            }

            if check_request_additional_data:
                grocery_coupons.check_check_request(
                    **keys.CHECK_REQUEST_ADDITIONAL_DATA,
                )
            grocery_coupons.set_check_response(response_body=response)

        def set_eats_data(
                self,
                discount,
                valid=True,
                discount_type='percent',
                discount_percent=DISCOUNT_PERCENT,
                discount_limit=None,
        ):
            discount_limit = (
                None if discount_limit is None else str(discount_limit)
            )
            eats_promocodes.set_response(
                discount=discount,
                valid=valid,
                discount_type='fixed',
                discount_percent=discount_percent,
                discount_limit=discount_limit,
            )

        def times_called(self):
            times_called_ = grocery_coupons.check_times_called()
            assert times_called_ == eats_promocodes.times_called()
            return times_called_

        def check_request(self, **kwargs):
            if not kwargs.items():
                return

            grocery_coupons.check_check_request(**kwargs)

            eats_kwargs = {}

            for key, value in kwargs.items():
                translation = _eats_check_request_translations(key, value)
                if translation is not None:
                    eats_kwargs.update(translation)

            if eats_kwargs.items():
                eats_promocodes.check_request(**eats_kwargs)

    context = Context()
    return context


def set_grocery_order_flow(experiments3, flow_version='grocery_flow_v1'):
    experiments3.add_config(
        name='grocery_order_cycle_enabled',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': True},
    )
    experiments3.add_config(
        name='grocery_order_flow_version',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'flow_version': flow_version},
    )


def set_eats_order_flow(experiments3):
    experiments3.add_config(
        name='grocery_order_cycle_enabled',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': False},
    )


@pytest.fixture(name='apply_promocode_v2_check_db')
def _apply_promocode_v2_check_db(cart, fetch_promocode, promocode_info):
    async def _inner(promocode, idempotency_token, discount):
        cart_version = cart.cart_version
        headers = {'X-Idempotency-Token': idempotency_token}

        promocode_info.set_grocery_data(
            discount=discount,
            discount_type='fixed',
            check_request_additional_data=True,
        )

        await cart.apply_promocode_v2(promocode=promocode, headers=headers)

        cart_doc = cart.fetch_db()

        assert cart_doc.cart_version == cart_version + 1
        assert cart_doc.idempotency_token == idempotency_token

        promocode_data = fetch_promocode(cart.cart_id)

        if promocode is None:
            assert promocode_data is None
            return

        assert promocode_data.promocode == promocode
        assert promocode_data.discount == discount
        assert promocode_data.valid

    return _inner


@configs.GROCERY_CURRENCY
@pytest.mark.parametrize('promocode_source', ['grocery', 'eats'])
@pytest.mark.parametrize('discount_type', ['fixed', 'percent'])
@pytest.mark.parametrize('discount_percent', [0, 30])
@pytest.mark.parametrize('discount', [100, 200])
@pytest.mark.parametrize('discount_limit', [None, 500, 100000])
async def test_basic(
        cart,
        promocode_source,
        promocode_info,
        discount_type,
        discount_percent,
        discount_limit,
        discount,
        lavka_cart_prices,
        experiments3,
        taxi_grocery_cart,
):
    await cart.modify(CART_ITEMS, headers=common.TAXI_HEADERS)

    if promocode_source == 'grocery':
        set_grocery_order_flow(experiments3)
    else:
        set_eats_order_flow(experiments3)

    await taxi_grocery_cart.invalidate_caches()

    promocode_info.set_grocery_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
        check_request_additional_data=True,
    )
    promocode_info.set_eats_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
    )

    promocode = 'test_promocode_01'

    cart.update_db(delivery_cost=DELIVERY_COST)

    cart_version = cart.cart_version

    response = await cart.apply_promocode_v2(promocode=promocode)

    assert response['cart_version'] == cart_version + 1

    promocode_response = response['promocode_info']

    assert promocode_response['code'] == promocode
    assert promocode_response['valid']
    assert promocode_response['messages'][0] == '1'

    cart_prices = response['cart_prices']
    cart_items_total = _calc_cart_items_price(CART_ITEMS)

    discount = _calc_discount(
        cart_items_total=cart_items_total,
        discount=discount,
        discount_type=(
            discount_type if promocode_source == 'grocery' else 'fixed'
        ),
        discount_percent=discount_percent,
        discount_limit=discount_limit,
        lavka_cart_prices=lavka_cart_prices,
    )

    total_with_promocode = cart_items_total + DELIVERY_COST - discount
    total_price_no_delivery = cart_items_total - discount

    assert (
        _cart_prices_decimal(cart_prices, 'total_price_template')
        == total_with_promocode
    )

    assert (
        _cart_prices_decimal(cart_prices, 'total_price_no_delivery_template')
        == total_price_no_delivery
    )

    if discount > 0:
        assert (
            _cart_prices_decimal(cart_prices, 'discount_profit_template')
            == discount
        )

        assert (
            _cart_prices_decimal(cart_prices, 'full_price_template')
            == cart_items_total + DELIVERY_COST
        )

        assert (
            _cart_prices_decimal(
                cart_prices, 'discount_profit_no_delivery_template',
            )
            == cart_items_total - total_with_promocode
        )

        assert (
            _cart_prices_decimal(
                cart_prices, 'full_price_no_delivery_template',
            )
            == cart_items_total
        )

        assert (
            _cart_prices_decimal(cart_prices, 'promocode_discount_template')
            == discount
        )

        assert decimal.Decimal(cart_prices['promocode_discount']) == discount

        if discount_type == 'fixed' or promocode_source == 'eats':
            assert 'promocode_discount_percent' not in cart_prices.keys()
        else:
            assert (
                decimal.Decimal(cart_prices['promocode_discount_percent'])
                == discount_percent
            )

        assert promocode_info.times_called() == 1


@common.GROCERY_ORDER_CYCLE_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
async def test_pg(
        cart,
        lavka_cart_prices,
        experiments3,
        taxi_grocery_cart,
        apply_promocode_v2_check_db,
):
    await cart.modify(CART_ITEMS, headers=common.TAXI_HEADERS)

    set_grocery_order_flow(experiments3)

    await taxi_grocery_cart.invalidate_caches()

    cart.update_db(delivery_cost=DELIVERY_COST)

    discount = 100
    idempotency_token = common.UPDATE_IDEMPOTENCY_TOKEN

    for promocode in ['test_promocode_01', 'test_promocode_02', None]:
        # some change of discount and idempotency_token to check result
        discount *= 2
        idempotency_token = idempotency_token + 'x'

        await apply_promocode_v2_check_db(
            promocode=promocode,
            idempotency_token=idempotency_token,
            discount=discount,
        )


@pytest.mark.parametrize('promocode_source', ['grocery', 'eats'])
async def test_promocode_request(
        cart,
        promocode_source,
        promocode_info,
        lavka_cart_prices,
        experiments3,
        taxi_grocery_cart,
        overlord_catalog,
        grocery_depots,
):
    depot_id = '0'  # default depot for testsuite

    await cart.modify(CART_ITEMS, headers=common.TAXI_HEADERS)

    if promocode_source == 'grocery':
        set_grocery_order_flow(experiments3)
    else:
        set_eats_order_flow(experiments3)

    await taxi_grocery_cart.invalidate_caches()

    discount = 100
    discount_percent = 30
    discount_type = 'fixed'
    discount_limit = 10000

    promocode_info.set_grocery_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
        check_request_additional_data=True,
    )
    promocode_info.set_eats_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
    )

    promocode = 'test_promocode_01'

    cart.update_db(delivery_cost=DELIVERY_COST)

    cart_items_total = _calc_cart_items_price(CART_ITEMS)

    promocode_info.check_request(
        cart_cost=str(cart_items_total),
        cart_id=cart.cart_id,
        cart_version=cart.cart_version,
        promocode=promocode,
        depot_id=depot_id,
    )

    await cart.apply_promocode_v2(promocode=promocode)

    assert promocode_info.times_called() == 1


async def test_cart_not_found(cart):
    await cart.init(['test_item'])
    cart.cart_id = str(uuid.uuid4())

    try:
        await cart.apply_promocode_v2(promocode='some_promocode')
    except common.CartHttpError as error:
        assert error.status_code == 404
        assert error.response_json['code'] == 'CART_NOT_FOUND'
    else:
        assert False


async def test_depot_not_found(cart, overlord_catalog):
    await cart.init(['test_item'])

    depot_id = '100'
    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )

    try:
        position = {'location': [30, 40]}
        await cart.apply_promocode_v2(
            promocode='some_promocode', position=position,
        )
    except common.CartHttpError as error:
        assert error.status_code == 404
        assert error.response_json['code'] == 'DEPOT_NOT_FOUND'
    else:
        assert False


async def test_unauthorized_access(cart):
    await cart.init(['test_item'])

    try:
        await cart.apply_promocode_v2(
            promocode='some_promocode', headers={'X-YaTaxi-Session': ''},
        )
    except common.CartHttpError as error:
        assert error.status_code == 401
    else:
        assert False


async def test_wrong_cart_status(cart):
    await cart.init(['test_item_1'])

    checked_out = 'checked_out'

    cart.update_db(status=checked_out)

    try:
        await cart.apply_promocode_v2(promocode='some_promocode')
    except common.CartHttpError as error:
        assert error.status_code == 409
        assert error.response_json['code'] == 'INVALID_PARAMS'
    else:
        assert False


async def test_old_cart_version(cart):
    await cart.init(['test_item_1'])

    cart.update_db(cart_version=3)

    try:
        await cart.apply_promocode_v2(
            promocode='some_promocode', cart_version=5,
        )
    except common.CartHttpError as error:
        assert error.status_code == 409
        assert error.response_json['code'] == 'INVALID_PARAMS'
    else:
        assert False


@pytest.mark.parametrize(
    'cart_version, idempotency_token',
    [
        (3, common.UPDATE_IDEMPOTENCY_TOKEN),
        (4, common.UPDATE_IDEMPOTENCY_TOKEN + 'x'),
        (6, common.UPDATE_IDEMPOTENCY_TOKEN),
    ],
)
async def test_race_condition(cart_version, idempotency_token, cart):
    await cart.init(['test_item_1'])

    db_cart_version = 5

    cart.update_db(
        cart_version=db_cart_version,
        idempotency_token=common.UPDATE_IDEMPOTENCY_TOKEN,
    )

    try:
        await cart.apply_promocode_v2(
            promocode='some_promocode',
            cart_version=cart_version,
            headers={'X-Idempotency-Token': idempotency_token},
        )
    except common.CartHttpError as error:
        assert error.status_code == 409
        assert error.response_json['code'] == 'INVALID_PARAMS'

        cart_doc = cart.fetch_db()
        assert cart_doc.cart_version == db_cart_version
    else:
        assert False


async def test_cart_is_up_to_date(cart, promocode_info, lavka_cart_prices):
    await cart.init(['test_item_1'])

    cart_version = 5

    cart.update_db(
        cart_version=cart_version,
        idempotency_token=common.UPDATE_IDEMPOTENCY_TOKEN,
    )

    discount = 100
    discount_percent = 30
    discount_type = 'fixed'
    discount_limit = 10000

    promocode_info.set_grocery_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
        check_request_additional_data=True,
    )
    promocode_info.set_eats_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
    )

    response = await cart.apply_promocode_v2(
        promocode='some_promocode',
        cart_version=cart_version - 1,
        headers={'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN},
    )

    cart_doc = cart.fetch_db()

    assert response['cart_version'] == cart_version
    assert cart_doc.cart_version == cart_version


async def test_eats_pickup(cart, promocode_info, lavka_cart_prices):
    await cart.init(['test_item_1'])

    cart.update_db(delivery_type='pickup')

    discount = 100
    discount_percent = 30
    discount_type = 'fixed'
    discount_limit = 10000

    promocode_info.set_grocery_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
        check_request_additional_data=True,
    )
    promocode_info.set_eats_data(
        discount=discount,
        valid=True,
        discount_type=discount_type,
        discount_percent=discount_percent,
        discount_limit=discount_limit,
    )

    try:
        await cart.apply_promocode_v2(promocode='some_promocode')
    except common.CartHttpError as error:
        assert error.status_code == 400
        assert error.response_json['code'] == 'PROMOCODE_BAD_DELIVERY_TYPE'
    else:
        assert False


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        cart, promocode_info, experiments3, user_api, has_personal_phone_id,
):
    headers = copy.deepcopy(common.TAXI_HEADERS)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    await cart.modify(CART_ITEMS, headers=common.TAXI_HEADERS)
    set_grocery_order_flow(experiments3)

    promocode_info.set_grocery_data(
        discount=100,
        valid=True,
        discount_type='fixed',
        discount_percent=30,
        discount_limit=10000,
        check_request_additional_data=True,
    )

    promocode = 'test_promocode_01'
    cart.update_db(delivery_cost=DELIVERY_COST)

    await cart.apply_promocode_v2(promocode=promocode, headers=headers)
    assert user_api.times_called == (1 if has_personal_phone_id else 0)
