import copy
import math
import typing

import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323

POST_BODY = dict(
    item_id=MENU_ITEM_ID, place_business='restaurant', **utils.ITEM_PROPERTIES,
)


class Discount:
    def apply_to_item(self, _: str) -> typing.Optional[str]:
        raise NotImplementedError()

    def apply_to_option(self, _: str) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_promo(self) -> typing.Optional[dict]:
        raise NotImplementedError()

    def get_promo_item(
            self, price: str, paid_quantity: int, quantity: int,
    ) -> typing.Optional[dict]:
        promo = self.get_promo()
        if not promo:
            return None
        promo_price = float(self.apply_to_item(price) or price)
        free_quantity = quantity - paid_quantity
        discount = (
            float(price) - promo_price
        ) * quantity + free_quantity * promo_price
        return {
            'name': promo['name'],
            'picture_uri': promo['picture_uri'],
            'type': 'discount',
            'amount': math.floor(discount),
            'decimal_amount': '{:g}'.format(discount),
        }


class FractionDiscount(Discount):
    _percent: float

    def __init__(self, percent: float):
        self._percent = percent

    def apply_to_item(self, amount: str) -> typing.Optional[str]:
        promo_price = round(float(amount) * (100.0 - self._percent) / 100.0, 2)
        return '{:g}'.format(promo_price)

    def apply_to_option(self, amount: str) -> typing.Optional[str]:
        promo_price = round(float(amount) * (100.0 - self._percent) / 100.0, 2)
        return '{:g}'.format(promo_price)

    def get_promo(self):
        return {
            'description': 'Описание',
            'name': 'money_promo_2',
            'picture_uri': 'some_uri',
        }


class AbsoluteDiscount(Discount):
    _value: float

    def __init__(self, value: float):
        self._value = value

    def apply_to_item(self, amount: str) -> typing.Optional[str]:
        promo_price = float(amount) - self._value
        return '{:g}'.format(promo_price)

    def apply_to_option(self, _: str) -> typing.Optional[str]:
        return None

    def get_promo(self):
        return {
            'description': 'Описание',
            'name': 'money_promo_1',
            'picture_uri': 'some_uri',
        }


class ProductDiscount(Discount):
    def apply_to_item(self, _: str) -> typing.Optional[str]:
        return None

    def apply_to_option(self, _: str) -> typing.Optional[str]:
        return None

    def get_promo(self):
        return {
            'description': 'Описание',
            'name': 'product_promo',
            'picture_uri': 'some_uri',
        }


class NoDiscount(Discount):
    def apply_to_item(self, _: str) -> typing.Optional[str]:
        return None

    def apply_to_option(self, _: str) -> typing.Optional[str]:
        return None

    def get_promo(self):
        return None


def check_db(
        eats_cart_cursor,
        eater_id: str,
        quantity: int,
        paid_quantity: int,
        discount_id: str,
        discount_amount: typing.Optional[str],
):
    eats_cart_cursor.execute(utils.SELECT_CART_DISCOUNTS)
    cart_discount = eats_cart_cursor.fetchall()

    assert not cart_discount

    select_items = (
        'SELECT it.id, it.cart_id, it.place_menu_item_id, '
        'it.price, '
        'it.promo_price, it.quantity, it.deleted_at FROM '
        'eats_cart.cart_items as it join eats_cart.carts '
        'on it.cart_id = carts.id  WHERE carts.eater_id = '
        f'\'{eater_id}\' ORDER BY id;'
    )

    eats_cart_cursor.execute(select_items)
    cart_items = eats_cart_cursor.fetchall()

    assert len(cart_items) == (1 if paid_quantity == quantity else 2)

    total_quantity = 0
    for item in cart_items:
        assert item['place_menu_item_id'] == str(MENU_ITEM_ID)
        assert str(item['price']) == '50.00'

        # we never store promo price to restaurant items
        assert item['promo_price'] is None
        total_quantity = total_quantity + item['quantity']

    assert total_quantity == quantity

    eats_cart_cursor.execute(utils.SELECT_CART_ITEM_OPTIONS)
    options = eats_cart_cursor.fetchall()

    for option in options:
        # we never store promo price to restaurant items options
        assert option['promo_price'] is None

    select_new_items_discounts = (
        'SELECT d.promo_id, d.amount, d.deleted_at '
        'FROM eats_cart.new_cart_item_discounts as d '
        'join eats_cart.cart_items it on d.cart_item_id = it.id '
        'join eats_cart.carts on it.cart_id = carts.id '
        f'where carts.eater_id = \'{eater_id}\';'
    )
    eats_cart_cursor.execute(select_new_items_discounts)
    new_item_discounts = eats_cart_cursor.fetchall()
    assert len(new_item_discounts) == (1 if discount_amount else 0)
    if discount_amount:
        new_item_discount = utils.pg_result_to_repr(new_item_discounts)[0]
        assert new_item_discount[0] == discount_id  # promo_id
        assert new_item_discount[1] == discount_amount  # amount


def check_cart_resp(
        discount: Discount,
        resp_cart: dict,
        quantity: int,
        paid_quantity: int,
        delivery_fee: float,
):
    item_price = '61.98'
    item_promo_price = discount.apply_to_item(item_price)

    promo = discount.get_promo()
    if promo:
        assert len(resp_cart['promos']) == 1
        assert resp_cart['promos'][0] == promo
    else:
        assert not resp_cart['promos']
    promo_item = discount.get_promo_item(item_price, paid_quantity, quantity)
    if promo_item:
        assert len(resp_cart['promo_items']) == 1
        assert resp_cart['promo_items'][0] == promo_item
    else:
        assert not resp_cart['promo_items']
    assert len(resp_cart['items']) == 1
    item = resp_cart['items'][0]
    assert item.get('decimal_promo_price') == item_promo_price
    assert item['quantity'] == quantity
    assert item['decimal_price'] == item_price
    assert item['subtotal'] == '{:g}'.format(float(item_price) * quantity)
    assert item.get('promo_subtotal') == (
        '{:g}'.format(
            float(item_promo_price if item_promo_price else item_price)
            * paid_quantity,
        )
        if (paid_quantity != quantity or item_promo_price)
        else None
    )
    assert 'promo_type' not in item
    assert item['place_menu_item'].get(
        'decimal_promo_price',
    ) == discount.apply_to_item(item['place_menu_item']['decimal_price'])
    for group in item['place_menu_item']['options_groups']:
        for option in group['options']:
            assert option.get(
                'decimal_promo_price',
            ) == discount.apply_to_option(option['decimal_price'])

    assert resp_cart['decimal_subtotal'] == '{:g}'.format(
        float(item_price) * quantity,
    )
    assert resp_cart['decimal_delivery_fee'] == str(delivery_fee)
    assert resp_cart['decimal_total'] == '{:g}'.format(
        float(item_promo_price if item_promo_price else item_price)
        * paid_quantity
        + delivery_fee,
    )


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    (
        'discount_id, discount, quantity,'
        ' paid_quantity, discount_amount, delivery_fee'
    ),
    [
        pytest.param(
            '1', AbsoluteDiscount(10), 2, 2, '10.00', 20, id='absolute',
        ),
        pytest.param(
            '2', FractionDiscount(10), 2, 2, '6.20', 20, id='fraction',
        ),
        pytest.param(
            '3', NoDiscount(), 1, 1, None, 50, id='product_not_apply',
        ),
        pytest.param(
            '3', ProductDiscount(), 2, 1, '61.98', 50, id='product_apply',
        ),
        pytest.param(
            '3',
            ProductDiscount(),
            3,
            2,
            '61.98',
            20,
            id='product_partial_apply',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_post_restaurants_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        discount_id,
        discount,
        quantity,
        paid_quantity,
        discount_amount,
        delivery_fee,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    discounts_resp = load_json('eats_discounts_resp.json')
    discounts_resp['match_results'][0]['subquery_results'][0][
        'discount_id'
    ] = discount_id
    local_services.eats_discounts_response = discounts_resp
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    body = copy.deepcopy(POST_BODY)
    body['quantity'] = quantity

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    check_db(
        eats_cart_cursor,
        EATER_ID,
        quantity,
        paid_quantity,
        discount_id,
        discount_amount,
    )

    check_cart_resp(
        discount,
        response.json()['cart'],
        quantity,
        paid_quantity,
        delivery_fee,
    )


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    'delivery_discount_on',
    [
        pytest.param(
            True,
            marks=utils.delivery_discount_enabled(),
            id='delivery_discount_on',
        ),
        pytest.param(False, id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    (
        'eater_id, discount_id, discount, quantity,'
        ' paid_quantity, discount_amount, delivery_fee'
    ),
    [
        pytest.param(
            'eater1',
            '1',
            AbsoluteDiscount(10),
            1,
            1,
            '10.00',
            50,
            id='absolute',
        ),
        pytest.param(
            'eater2',
            '2',
            FractionDiscount(10),
            1,
            1,
            '6.20',
            50,
            id='fraction',
        ),
        pytest.param(
            'eater3',
            '3',
            NoDiscount(),
            1,
            1,
            None,
            50,
            id='product_not_apply',
        ),
        pytest.param(
            'eater4',
            '3',
            ProductDiscount(),
            2,
            1,
            '61.98',
            50,
            id='product_apply',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_get_restaurants_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        delivery_discount_on,
        eater_id,
        discount_id,
        discount,
        quantity,
        paid_quantity,
        discount_amount,
        delivery_fee,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    discounts_resp = load_json('eats_discounts_resp.json')
    discounts_resp['match_results'][0]['subquery_results'][0][
        'discount_id'
    ] = discount_id
    local_services.eats_discounts_response = discounts_resp
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    response = await taxi_eats_cart.get(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == (
        2 if delivery_discount_on else 1
    )
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    check_db(
        eats_cart_cursor,
        eater_id,
        quantity,
        paid_quantity,
        discount_id,
        discount_amount,
    )

    check_cart_resp(
        discount, response.json(), quantity, paid_quantity, delivery_fee,
    )


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    (
        'eater_id, discount_id, item_id, discount, quantity,'
        ' paid_quantity, discount_amount, delivery_fee'
    ),
    [
        pytest.param(
            'eater1',
            '1',
            1,
            AbsoluteDiscount(10),
            2,
            2,
            '10.00',
            20,
            id='absolute',
        ),
        pytest.param(
            'eater2',
            '2',
            2,
            FractionDiscount(10),
            2,
            2,
            '6.20',
            20,
            id='fraction',
        ),
        pytest.param(
            'eater3',
            '3',
            3,
            ProductDiscount(),
            2,
            1,
            '61.98',
            50,
            id='product_was_not_apply',
        ),
        pytest.param(
            'eater4',
            '3',
            4,
            ProductDiscount(),
            3,
            2,
            '61.98',
            20,
            id='product_was_apply_update_paid',
        ),
        pytest.param(
            'eater4',
            '3',
            5,
            ProductDiscount(),
            3,
            2,
            '61.98',
            20,
            id='product_was_apply_update_gift',
        ),
        pytest.param(
            'eater5',
            '3',
            6,
            ProductDiscount(),
            3,
            2,
            '61.98',
            20,
            id='product_was_apply_update_gift',
        ),
    ],
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
@pytest.mark.now('2022-07-01T00:00:00+0000')
async def test_put_restaurants_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        discount_id,
        eater_id,
        item_id,
        discount,
        quantity,
        paid_quantity,
        discount_amount,
        delivery_fee,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    discounts_resp = load_json('eats_discounts_resp.json')
    discounts_resp['match_results'][0]['subquery_results'][0][
        'discount_id'
    ] = discount_id
    local_services.eats_discounts_response = discounts_resp
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    body = dict(place_business='restaurant', **utils.ITEM_PROPERTIES)
    body['quantity'] = quantity

    response = await taxi_eats_cart.put(
        f'api/v1/cart/{item_id}',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id),
        json=body,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == 2
    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_products_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    check_db(
        eats_cart_cursor,
        eater_id,
        quantity,
        paid_quantity,
        discount_id,
        discount_amount,
    )

    check_cart_resp(
        discount,
        response.json()['cart'],
        quantity,
        paid_quantity,
        delivery_fee,
    )


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    (
        'eater_id, discount_id, discount, quantity,'
        ' paid_quantity, delivery_fee'
    ),
    [
        pytest.param(
            'eater1', '1', AbsoluteDiscount(10), 1, 1, 50, id='absolute',
        ),
        pytest.param(
            'eater2', '2', FractionDiscount(10), 1, 1, 50, id='fraction',
        ),
        pytest.param(
            'eater3', '3', NoDiscount(), 1, 1, 50, id='product_not_apply',
        ),
        pytest.param(
            'eater4', '3', ProductDiscount(), 2, 1, 50, id='product_apply',
        ),
    ],
)
@pytest.mark.parametrize('yandex_plus', [False, True])
@utils.discounts_applicator_enabled(True)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
async def test_related_data_restaurants_discounts(
        taxi_eats_cart,
        load_json,
        local_services,
        eats_order_stats,
        eater_id,
        discount_id,
        discount,
        quantity,
        paid_quantity,
        delivery_fee,
        yandex_plus,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    discounts_resp = load_json('eats_discounts_resp.json')
    discounts_resp['match_results'][0]['subquery_results'][0][
        'discount_id'
    ] = discount_id
    local_services.eats_discounts_response = discounts_resp
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )

    plus_response = load_json('eats_plus_cashback.json')
    local_services.set_plus_checkout_response(status=200, json=plus_response)
    item_price = '61.98'
    item_promo_price = discount.apply_to_item(item_price)
    item_promo_price = item_promo_price if item_promo_price else item_price
    total_cost = float(item_promo_price) * paid_quantity + delivery_fee
    local_services.plus_checkout_request = {
        'currency': 'RUB',
        'place_id': {'place_id': '123', 'provider': 'eats'},
        'yandex_uid': '0',
        'services': [
            {
                'service_type': 'product',
                'quantity': str(paid_quantity),
                'public_id': '232323',
                'cost': item_promo_price,
            },
            {
                'service_type': 'delivery',
                'quantity': '1',
                'cost': str(delivery_fee),
            },
        ],
        'order_id': 'cart_1a73add7-9c84-4440-9d3a-12f3e71c6026',
        'total_cost': '{:g}'.format(total_cost),
    }
    free_quantity = quantity - paid_quantity
    if free_quantity > 0:
        plus_services = local_services.plus_checkout_request['services']
        plus_services.append(copy.deepcopy(plus_services[-1]))  # copy delivery
        plus_services[1] = copy.deepcopy(plus_services[0])
        plus_services[1]['quantity'] = str(free_quantity)
        plus_services[1]['cost'] = '0'

    request = {
        'location': {'lat': 55.75, 'lon': 37.62},  # Moscow
        'eater_id': eater_id,
        'delivery_date': '2021-04-04T08:00:00+00:00',
    }
    yandex_uid = ''
    if yandex_plus:
        yandex_uid = '0'
        request['yandex_uid'] = yandex_uid
    response = await taxi_eats_cart.post(
        '/internal/eats-cart/v1/related_data',
        headers=utils.get_auth_headers(eater_id, yandex_uid=yandex_uid),
        json=request,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == 0
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_products_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    if yandex_plus:
        assert local_services.mock_plus_checkout_cashback.times_called == 1
    resp_cart = response.json()['cart']
    assert resp_cart['decimal_total'] == '{:g}'.format(total_cost)

    assert resp_cart['decimal_discount'] == '0'  # only for promocode
    if free_quantity > 0:
        assert len(resp_cart['items']) == 2
        assert resp_cart['items'][0]['decimal_price'] == item_price
        assert resp_cart['items'][0]['quantity'] == paid_quantity
        assert resp_cart['items'][1]['decimal_price'] == '0'
        assert resp_cart['items'][1]['quantity'] == free_quantity
    else:
        assert len(resp_cart['items']) == 1
        assert resp_cart['items'][0]['decimal_price'] == item_price
        assert resp_cart['items'][0]['quantity'] == paid_quantity


@utils.use_new_disc_for_rest_exp()
@pytest.mark.experiments3(filename='eats_discounts_enabled_exp.json')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=utils.delivery_discount_enabled(), id='delivery_discount_on',
        ),
        pytest.param(id='delivery_discount_off'),
    ],
)
@pytest.mark.parametrize(
    (
        'eater_id, discount_id, discount, quantity,'
        ' paid_quantity, discount_amount, delivery_fee'
    ),
    [
        pytest.param(
            'eater1', '1', AbsoluteDiscount(10), 1, 1, '10', 50, id='absolute',
        ),
        pytest.param(
            'eater2',
            '2',
            FractionDiscount(10),
            1,
            1,
            '6.2',
            50,
            id='fraction',
        ),
        pytest.param(
            'eater3',
            '3',
            NoDiscount(),
            1,
            1,
            None,
            50,
            id='product_not_apply',
        ),
        pytest.param(
            'eater4',
            '3',
            ProductDiscount(),
            2,
            1,
            '61.98',
            50,
            id='product_apply',
        ),
    ],
)
@pytest.mark.parametrize(
    'for_pickup',
    (pytest.param(False, id='delivery'), pytest.param(True, id='pickup')),
)
@utils.discounts_applicator_enabled(True)
@pytest.mark.pgsql('eats_cart', files=['existing_cart.sql'])
async def test_lock_cart_restaurants_discounts(
        taxi_eats_cart,
        load_json,
        eats_cart_cursor,
        local_services,
        eats_order_stats,
        eater_id,
        discount_id,
        for_pickup,
        discount,
        quantity,
        paid_quantity,
        discount_amount,
        delivery_fee,
):
    eats_order_stats()
    local_services.set_place_slug('place123')
    local_services.available_discounts = True
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_id = 123
    local_services.eats_core_items_response = load_json(
        'eats_core_menu_items.json',
    )
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )
    discounts_resp = load_json('eats_discounts_resp.json')
    discounts_resp['match_results'][0]['subquery_results'][0][
        'discount_id'
    ] = discount_id
    local_services.eats_discounts_response = discounts_resp
    local_services.eats_catalog_storage_response = load_json(
        'eats_catalog_response.json',
    )
    if for_pickup:
        del local_services.request_params['deliveryTime']
        del local_services.request_params['longitude']
        del local_services.request_params['latitude']
        local_services.request_params['shippingType'] = 'pickup'

    response = await utils.call_lock_cart(
        taxi_eats_cart, eater_id, utils.get_auth_headers(eater_id), for_pickup,
    )

    assert response.status_code == 200
    assert local_services.mock_eats_catalog_storage.times_called == 0
    assert local_services.mock_match_discounts.times_called == 0
    assert local_services.mock_eats_core_menu.times_called == 0
    assert local_services.mock_eats_products_menu.times_called == 0
    assert local_services.mock_eats_catalog.times_called == 1
    assert local_services.mock_eats_core_discount.times_called == 0

    resp = response.json()

    if not for_pickup:
        assert resp['delivery_fee'] == str(delivery_fee)
    assert resp['discount'] == (discount_amount or '0')
    assert not resp['new_promos']
    assert not resp['promos']

    item_price = '61.98'

    assert resp['subtotal'] == '{:g}'.format(float(item_price) * quantity)

    item_promo_price = discount.apply_to_item(item_price)
    item_promo_price = item_promo_price if item_promo_price else item_price
    total_cost = float(item_promo_price) * paid_quantity + delivery_fee

    assert resp['total'] == '{:g}'.format(total_cost)

    item = resp['items'][0]

    assert item.get('promo_price') == discount.apply_to_item(item['price'])
    assert item['quantity'] == paid_quantity

    free_quantity = quantity - paid_quantity
    if free_quantity > 0:
        assert not item['new_promos']
        assert not item['is_gift']
        free_item = resp['items'][1]
        assert free_item['price'] == item['price']
        assert free_item['promo_price'] == '0'
        assert free_item['quantity'] == free_quantity
        assert len(free_item['new_promos']) == 1
        new_promo = free_item['new_promos'][0]
        assert new_promo['amount'] == item_price
        assert new_promo['discount_provider'] == 'place'
        assert new_promo['promo_id'] == discount_id
        assert not free_item['is_gift']
    elif discount_amount:
        assert len(item['new_promos']) == 1
        assert not item['is_gift']
        new_promo = item['new_promos'][0]
        assert new_promo['amount'] == '{:g}'.format(
            float(item_price) - float(item_promo_price),
        )
        assert new_promo['discount_provider'] == 'place'
        assert new_promo['promo_id'] == discount_id
