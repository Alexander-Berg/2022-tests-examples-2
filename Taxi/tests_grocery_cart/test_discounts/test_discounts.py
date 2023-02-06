# pylint: disable=invalid-name
# pylint: disable=C0302
# pylint: disable=E0401
import copy
import math

from grocery_mocks import grocery_menu as mock_grocery_menu
from grocery_mocks import grocery_p13n as modifiers
import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
}

TAXI_HEADERS = {**BASIC_HEADERS, 'X-YaTaxi-Session': 'taxi:1234'}


def format_sign_currency(price):
    return f'{price} $SIGN$$CURRENCY$'


CUSTOM_APPLIED_KEY = 'applied value_1: %({})s, applied value_2: %({})s'.format(
    'absolute_value', 'cart_price_template',
)
CUSTOM_SUGGESTED_KEY = (
    'suggested value_1: %({})s, suggested value_2: %({})s'.format(
        'money_to_next_threshold', 'absolute_value',
    )
)

CUSTOM_TANKER_KEYS = pytest.mark.translations(
    discount_descriptions={
        'custom_suggested_step': {'ru': CUSTOM_SUGGESTED_KEY},
        'custom_applied_step': {'ru': CUSTOM_APPLIED_KEY},
    },
)

GROCERY_CART_DISCOUNT_PICTURES = pytest.mark.config(
    GROCERY_CART_DISCOUNT_PICTURE={
        'cashback': {
            'applied': 'applied cashback gain cart discount picture url',
            'suggested': 'suggested cashback gain cart discount picture url',
        },
        'money': {
            'applied': 'applied money cart discount picture url',
            'suggested': 'suggested money cart discount picture url',
        },
    },
)

BASIC_CART_ABSOLUTE_DISCOUNT_LABEL_TEMPLATE = (
    'Скидка {} $SIGN$$CURRENCY$ на заказ от {} $SIGN$$CURRENCY$'
)
BASIC_CART_APPLIED_DISCOUNT_LABEL_TEMPLATE = '– {} $SIGN$$CURRENCY$%'
BASIC_CART_SUGGESTED_DISCOUNT_LABEL_TEMPLATE = 'Еще {} $SIGN$$CURRENCY$%'


def make_basic_cart_absolute_discount_label(discount, from_cost):
    return BASIC_CART_ABSOLUTE_DISCOUNT_LABEL_TEMPLATE.format(
        discount, from_cost,
    )


def make_basic_cart_applied_discount_label(applied_discount):
    return BASIC_CART_APPLIED_DISCOUNT_LABEL_TEMPLATE.format(applied_discount)


def make_basic_cart_suggested_discount_label(suggested_discount):
    return BASIC_CART_SUGGESTED_DISCOUNT_LABEL_TEMPLATE.format(
        suggested_discount,
    )


BASIC_CART_ABSOLUTE_MONEY_SUGGESTED_DISCOUNT_LABEL_TEMPLATE = (
    'Еще {} $SIGN$$CURRENCY$, и скидка {} $SIGN$$CURRENCY$ на ваш заказ'
)

BASIC_CART_FRACTION_MONEY_SUGGESTED_DISCOUNT_LABEL_TEMPLATE = (
    'Еще {} $SIGN$$CURRENCY$, и скидка {}% на ваш заказ'
)

CART_ABSOLUTE_CASHBACK_SUGGESTED_DISCOUNT_LABEL_TEMPLATE = (
    'Еще {} $SIGN$$CURRENCY$, и скидка {} баллами Плюса на ваш заказ'
)

CART_FRACTION_CASHBACK_SUGGESTED_DISCOUNT_LABEL_TEMPLATE = (
    'Еще {} $SIGN$$CURRENCY$, и скидка {}% баллами Плюса на ваш заказ'
)

CART_ABSOLUTE_MONEY_APPLIED_DISCOUNT_LABEL_TEMPLATE = (
    'Скидка {} $SIGN$$CURRENCY$ на заказ от {} $SIGN$$CURRENCY$'
)

CART_FRACTION_MONEY_APPLIED_DISCOUNT_LABEL_TEMPLATE = (
    'Скидка {}% на заказ от {} $SIGN$$CURRENCY$'
)

CART_ABSOLUTE_CASHBACK_APPLIED_DISCOUNT_LABEL_TEMPLATE = (
    'Скидка {} баллами Плюса на заказ от {} $SIGN$$CURRENCY$'
)

FRACTION_CASHBACK_APPLIED_DISCOUNT_LABEL_TEMPLATE = (
    'Скидка {}% баллами Плюса на заказ от {} $SIGN$$CURRENCY$'
)

BASIC_CART_MONEY_DISCOUNT_APPLIED_LABEL_TEMPLATE = '– {} $SIGN$$CURRENCY$'


def make_money_suggested_label(discount, from_cost, payment_rule):
    if payment_rule == 'discount_value':
        return (
            BASIC_CART_ABSOLUTE_MONEY_SUGGESTED_DISCOUNT_LABEL_TEMPLATE.format(
                discount, from_cost,
            )
        )
    if payment_rule == 'discount_percent':
        return (
            BASIC_CART_FRACTION_MONEY_SUGGESTED_DISCOUNT_LABEL_TEMPLATE.format(
                discount, from_cost,
            )
        )
    return ''


def make_cashback_suggested_label(discount, from_cost, payment_rule):
    if payment_rule == 'gain_value':
        return CART_ABSOLUTE_CASHBACK_SUGGESTED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    if payment_rule == 'gain_percent':
        return CART_FRACTION_CASHBACK_SUGGESTED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    return ''


def make_money_applied_label(discount, from_cost, payment_rule):
    if payment_rule == 'discount_value':
        return CART_ABSOLUTE_MONEY_APPLIED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    if payment_rule == 'discount_percent':
        return CART_FRACTION_MONEY_APPLIED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    return ''


def make_cashback_applied_label(discount, from_cost, payment_rule):
    if payment_rule == 'gain_value':
        return CART_ABSOLUTE_CASHBACK_APPLIED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    if payment_rule == 'gain_percent':
        return FRACTION_CASHBACK_APPLIED_DISCOUNT_LABEL_TEMPLATE.format(
            discount, from_cost,
        )
    return ''


def make_money_applied_value(applied_discount):
    return BASIC_CART_MONEY_DISCOUNT_APPLIED_LABEL_TEMPLATE.format(
        applied_discount,
    )


def _expring_products_experiments(enabled):
    return pytest.mark.experiments3(
        name='grocery_enable_expiring_products',
        consumers=['grocery-cart'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=False,
    )


def get_product_group(is_selection_unique, options_to_select, products):
    return mock_grocery_menu.ProductGroup(
        is_selection_unique, options_to_select, products, 'group_title',
    )


EXPIRING_PRODUCTS_ENABLED = _expring_products_experiments(enabled=True)

EXPIRING_PRODUCTS_DISABLED = _expring_products_experiments(enabled=False)


@pytest.mark.now(keys.TS_NOW)
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize('is_surge', [True, False])
async def test_grocery_p13n_receives_surge_flag(
        taxi_grocery_cart,
        mockserver,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        is_surge,
        grocery_depots,
):
    legacy_depot_id = '111'
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        depot_id=legacy_depot_id,
        is_surge=is_surge,
        delivery={'cost': '0', 'next_cost': '0', 'next_threshold': '99999'},
    )
    overlord_catalog.add_depot(legacy_depot_id=legacy_depot_id)
    grocery_depots.add_depot(int(legacy_depot_id))

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def mock_grocery_discounts(request):
        assert 'has_surge' in request.json
        assert request.json['has_surge'] == is_surge
        return {'match_results': []}

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
    }
    await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', headers=TAXI_HEADERS, json=request,
    )
    assert mock_grocery_discounts.times_called == 1


# возвращает информацию о примененной и предложенной простой скидке на корзину
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize(
    'uri,item_id,price,discount_price,total_price,catalog_total_price,'
    'applied_discount,applied_discount_per_item,applied_discount_from_cost,'
    'applied_discount_value,suggested_discount_from_cost,'
    'suggested_discount_value,suggested_discount,'
    'items',
    [
        pytest.param(
            '/lavka/v1/cart/v1/retrieve',
            'item_id_2',
            '345',  # цена товара в корзине (345р)
            '335',  # после применения скидки (335р)
            '335',  # общая цена после применения скидки (335р)
            '345',  # общая отображаемая цена товара в корзине (345р)
            '10',  # примененная скидка (всего 10р)
            '10',  # примененная скидка на единицу товара (10р, 1 единица)
            '300',  # полка примененной скидки (на заказ от 300р)
            '10',  # значение для полки (скидка 10р)
            '445',  # полка предложенной скидки (на заказ от 445р)
            '20',  # значение (будет применена скидка 20р)
            '100',  # сколько добрать до скидки (еще 100р до скидки)
            None,
            id='retrieve',
        ),
        pytest.param(
            '/lavka/v1/cart/v1/update',
            'item_id_2',
            '345',  # цена товара в корзине (345р)
            '340',  # после применения скидки (340р)
            '680',  # общая цена после применения скидки (680р)
            '690',  # общая отображаемая цена товара в корзине (690р)
            '10',  # примененная скидка (всего 10р)
            '5',  # примененная скидка на единицу товара (5р, 2 единицы)
            '300',  # полка примененной скидки (на заказ от 300р)
            '10',  # значение для полки (скидка 10р)
            '800',  # полка предложенной скидки (на заказ от 800р)
            '20',  # значение (будет применена скидка 20р)
            '110',  # сколько добрать до скидки (еще 110р до скидки)
            [
                {
                    'id': 'item_id_2',
                    'price': '345',
                    'quantity': '2',
                    'currency': 'RUB',
                },
            ],
            id='update',
        ),
    ],
)
async def test_basic_cart_money_discount_apply(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        uri,
        item_id,
        price,
        discount_price,
        total_price,
        catalog_total_price,
        applied_discount,
        applied_discount_per_item,
        applied_discount_from_cost,
        applied_discount_value,
        suggested_discount_from_cost,
        suggested_discount_value,
        suggested_discount,
        items,
):
    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_cart_modifier(
        steps=[
            (applied_discount_from_cost, applied_discount_value),
            (suggested_discount_from_cost, suggested_discount_value),
        ],
    )
    expected_applied_label = {
        'discount_template': make_basic_cart_applied_discount_label(
            applied_discount,
        ),
        'info_template': (
            make_basic_cart_absolute_discount_label(
                applied_discount_value, applied_discount_from_cost,
            )
        ),
    }

    expected_suggested_label = {
        'discount_template': make_basic_cart_suggested_discount_label(
            suggested_discount,
        ),
        'info_template': (
            make_basic_cart_absolute_discount_label(
                suggested_discount_value, suggested_discount_from_cost,
            )
        ),
    }

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
    }
    if items:
        request['items'] = items

    response = await taxi_grocery_cart.post(
        uri, json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    # в catalog_price действительно возвращается чекаутная цена, с тем чтобы
    # клиент сделал вызов update с этим значением
    assert response_cart_item['catalog_price'] == discount_price
    assert response_cart_item[
        'catalog_price_template'
    ] == format_sign_currency(price)
    assert response_cart_item[
        'catalog_total_price_template'
    ] == format_sign_currency(catalog_total_price)
    assert 'basic_cart_money_discount_applied' in response_json
    assert (
        response_json['basic_cart_money_discount_applied']
        == expected_applied_label
    )
    assert 'basic_cart_money_discount_suggested' in response_json
    assert (
        response_json['basic_cart_money_discount_suggested']
        == expected_suggested_label
    )
    assert response_json['total_price_template'] == format_sign_currency(
        total_price,
    )

    assert response_json['available_for_checkout'] is False
    assert response_json['checkout_unavailable_reason'] == 'price-mismatch'
    assert response_json['hide_price_mismatch'] is True

    assert response_json['diff_data'] == {}


# возвращает информацию о примененной и предложенной
# простой денежной скидке на корзину
@GROCERY_CART_DISCOUNT_PICTURES
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize(
    'uri,item_id,price,payment_rule,discount_price,total_price,'
    'catalog_total_price,applied_discount,applied_discount_per_item,'
    'applied_discount_from_cost,applied_discount_value,,'
    'suggested_discount_from_cost,suggested_discount_value,'
    'suggested_discount,items,',
    [
        pytest.param(
            '/lavka/v1/cart/v1/retrieve',
            'item_id_2',
            '345',  # цена товара в корзине (345р)
            'discount_value',  # тип скидки (абсолютная скидка)
            '335',  # после применения скидки (335р)
            '335',  # общая цена после применения скидки (335р)
            '345',  # общая отображаемая цена товара в корзине (345р)
            '10',  # примененная скидка (всего 10р)
            '10',  # примененная скидка на единицу товара (10р, 1 единица)
            '300',  # полка примененной скидки (на заказ от 300р)
            '10',  # значение для полки (скидка 10р)
            '445',  # полка предложенной скидки (на заказ от 445р)
            '20',  # значение (будет применена скидка 20р)
            '100',  # сколько добрать до скидки (еще 100р до скидки)
            None,
            id='retrieve',
        ),
        pytest.param(
            '/lavka/v1/cart/v1/update',
            'item_id_2',
            '100',  # цена товара в корзине (100)
            'discount_percent',  # тип скидки (относительная скидка)
            '70',  # после применения скидки (70р)
            '140',  # общая цена после применения скидки (140р)
            '200',  # общая отображаемая цена товара в корзине (200)
            '60',  # примененная скидка (всего 60)
            '30',  # примененная скидка на единицу товара (30р, 2 единицы)
            '100',  # полка примененной скидки (на заказ от 100р)
            '30',  # значение для полки (скидка 30 процентов)
            '300',  # полка предложенной скидки (на заказ от 300р)
            '50',  # значение (будет применена скидка 50 процентов)
            '100',  # сколько добрать до скидки (еще 100р до скидки)
            [
                {
                    'id': 'item_id_2',
                    'price': '100',
                    'quantity': '2',
                    'currency': 'RUB',
                },
            ],
            id='update',
        ),
    ],
)
async def test_money_cart_discount(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        uri,
        item_id,
        price,
        discount_price,
        total_price,
        catalog_total_price,
        applied_discount,
        applied_discount_per_item,
        applied_discount_from_cost,
        applied_discount_value,
        suggested_discount_from_cost,
        suggested_discount_value,
        suggested_discount,
        payment_rule,
        items,
):
    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_cart_modifier(
        steps=[
            (applied_discount_from_cost, applied_discount_value),
            (suggested_discount_from_cost, suggested_discount_value),
        ],
        payment_rule=payment_rule,
    )

    basic_cart_discount_applied = {
        'discount_template': (make_money_applied_value(applied_discount)),
        'info_template': (
            make_money_applied_label(
                applied_discount_value,
                applied_discount_from_cost,
                payment_rule,
            )
        ),
        'picture': 'applied money cart discount picture url',
    }

    basic_cart_discount_suggested = {
        'info_template': (
            make_money_suggested_label(
                suggested_discount, suggested_discount_value, payment_rule,
            )
        ),
        'picture': 'suggested money cart discount picture url',
    }

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
    }
    if items:
        request['items'] = items

    response = await taxi_grocery_cart.post(
        uri, json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    # в catalog_price действительно возвращается чекаутная цена, с тем чтобы
    # клиент сделал вызов update с этим значением
    assert response_cart_item['catalog_price'] == discount_price
    assert response_cart_item[
        'catalog_price_template'
    ] == format_sign_currency(price)
    assert response_cart_item[
        'catalog_total_price_template'
    ] == format_sign_currency(catalog_total_price)
    assert 'basic_cart_discount_applied' in response_json
    assert (
        response_json['basic_cart_discount_applied']
        == basic_cart_discount_applied
    )
    assert 'basic_cart_discount_suggested' in response_json
    assert (
        response_json['basic_cart_discount_suggested']
        == basic_cart_discount_suggested
    )
    assert response_json['total_price_template'] == format_sign_currency(
        total_price,
    )

    assert response_json['available_for_checkout'] is False
    assert response_json['checkout_unavailable_reason'] == 'price-mismatch'
    assert response_json['hide_price_mismatch'] is True

    assert response_json['diff_data'] == {}


# возвращает информацию о предложенной скидке на корзину баллами Плюса
@GROCERY_CART_DISCOUNT_PICTURES
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize(
    'uri,item_id,price,payment_rule,applied_discount,'
    'applied_discount_from_cost,applied_discount_value,'
    'suggested_discount_from_cost,suggested_discount_value,'
    'suggested_discount,items,',
    [
        pytest.param(
            '/lavka/v1/cart/v1/retrieve',
            'item_id_2',
            '345',  # цена товара в корзине (345р)
            'gain_value',  # тип скидки (абсолютная скидка)
            '10',  # примененная скидка (всего 10 баллов)
            '300',  # полка примененной скидки (на заказ от 300р)
            '10',  # значение для полки (скидка 10 баллов)
            '445',  # полка предложенной скидки (на заказ от 445р)
            '20',  # значение (будет возвращено 20 баллов Плюса)
            '100',  # сколько добрать до скидки (еще 100р до скидки)
            None,
            id='retrieve',
        ),
        pytest.param(
            '/lavka/v1/cart/v1/update',
            'item_id_2',
            '200',  # цена товара в корзине (200р)
            'gain_percent',  # тип скидки (относительная скидка)
            '40',  # примененная скидка (всего 40 баллов Плюса)
            '100',  # полка примененной скидки (на заказ от 100р)
            '10',  # значение для полки (скидка 10% баллами Плюса)
            '800',  # полка предложенной скидки (на заказ от 800р)
            '20',  # значение предложенной скидки (скидка 20% баллами Плюса)
            '400',  # сколько добрать до скидки (еще 400р до скидки)
            [
                {
                    'id': 'item_id_2',
                    'price': '200',
                    'quantity': '2',
                    'currency': 'RUB',
                },
            ],
            id='update',
        ),
    ],
)
async def test_cashback_gain_cart_discount(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        uri,
        item_id,
        price,
        applied_discount,
        applied_discount_from_cost,
        applied_discount_value,
        suggested_discount_from_cost,
        suggested_discount_value,
        suggested_discount,
        payment_rule,
        items,
):
    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_cart_modifier(
        steps=[
            (applied_discount_from_cost, applied_discount_value),
            (suggested_discount_from_cost, suggested_discount_value),
        ],
        payment_rule=payment_rule,
    )

    expected_basic_cart_discount_suggested = {
        'info_template': (
            make_cashback_suggested_label(
                suggested_discount, suggested_discount_value, payment_rule,
            )
        ),
        'picture': 'suggested cashback gain cart discount picture url',
    }

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
    }
    if items:
        request['items'] = items
    response = await taxi_grocery_cart.post(
        uri, json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'basic_cart_discount_applied' not in response_json
    assert 'basic_cart_discount_suggested' in response_json
    assert (
        response_json['basic_cart_discount_suggested']
        == expected_basic_cart_discount_suggested
    )


@GROCERY_CART_DISCOUNT_PICTURES
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_cashback_gain_cart_discount_no_step_applied(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    overlord_catalog.add_product(product_id='item_id_2', price='200')
    payment_rule = 'gain_percent'
    grocery_p13n.add_cart_modifier(
        steps=[('800', '20')], payment_rule=payment_rule,
    )

    expected_basic_cart_discount_suggested = {
        'info_template': (
            make_cashback_suggested_label('400', '20', payment_rule)
        ),
        'picture': 'suggested cashback gain cart discount picture url',
    }

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
        'items': [
            {
                'id': 'item_id_2',
                'price': '200',
                'quantity': '2',
                'currency': 'RUB',
            },
        ],
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'basic_cart_discount_applied' not in response_json
    assert 'basic_cart_discount_suggested' in response_json
    assert (
        response_json['basic_cart_discount_suggested']
        == expected_basic_cart_discount_suggested
    )


@CUSTOM_TANKER_KEYS
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_custom_tanker_keys_for_cart_discount(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    item_id = 'item_id_2'
    item_price = '345'
    overlord_catalog.add_product(product_id=item_id, price=item_price)
    meta = {
        'title_tanker_key': 'custom_suggested_step',
        'subtitle_tanker_key': 'custom_applied_step',
    }

    grocery_p13n.add_cart_modifier(
        steps=[('50', '100'), ('1000', '120')],
        payment_rule='discount_value',
        meta=meta,
    )
    applied_info_template = 'applied value_1: {}, applied value_2: {}'.format(
        '100 $SIGN$$CURRENCY$', '50 $SIGN$$CURRENCY$',
    )
    suggested_info_template = (
        'suggested value_1: {}, suggested value_2: {}'.format(
            '655 $SIGN$$CURRENCY$', '120 $SIGN$$CURRENCY$',
        )
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'basic_cart_discount_applied' in response_json
    assert (
        response_json['basic_cart_discount_applied']['info_template']
        == applied_info_template
    )
    assert 'basic_cart_discount_suggested' in response_json
    assert (
        response_json['basic_cart_discount_suggested']['info_template']
        == suggested_info_template
    )


@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_menu_discounts_description(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    item_id = 'item_id_2'
    item_price = 345
    item_quantity = 4
    overlord_catalog.add_product(product_id=item_id, price=str(item_price))

    grocery_p13n.add_modifier(
        product_id=item_id,
        value_type=modifiers.DiscountValueType.RELATIVE,
        value='10',
    )
    total_discount = math.ceil(0.1 * item_price) * item_quantity

    grocery_p13n.add_modifier(
        product_id=item_id,
        value='10',
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
        meta={
            'picture': 'mastercard',
            'subtitle_tanker_key': 'test_mastercard_discount_on_cart',
            'payment_method_subtitle': 'test_mastercard_discount',
        },
    )
    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
        'cart_version': 1,
        'items': [
            {
                'id': item_id,
                'price': str(item_price),
                'quantity': str(item_quantity),
                'currency': 'RUB',
            },
        ],
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    discount_descriptions = response.json()['discount_descriptions']
    assert len(discount_descriptions) == 2

    menu_discounts_desc = None
    for description in discount_descriptions:
        if description['type'] == 'menu_discounts':
            menu_discounts_desc = description

    assert menu_discounts_desc is not None
    assert (
        menu_discounts_desc['discount_value']
        == f'{total_discount} $SIGN$$CURRENCY$'
    )


# Не возвращает перечеркнутую цену, если получил флаг от сервиса скидок
@experiments.SUBSTITUTE_UNCROSSED_PRICE
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize('is_price_uncrossed', [True, False])
async def test_is_price_uncrossed(
        taxi_grocery_cart, overlord_catalog, is_price_uncrossed, grocery_p13n,
):
    price = '355'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    discount_price = '345'
    meta = {'is_price_uncrossed': is_price_uncrossed}

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_modifier(
        product_id=item_id, value=int(price) - int(discount_price), meta=meta,
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    assert response_cart_item['catalog_price'] == discount_price
    assert (
        not ('full_catalog_price' in response_cart_item) == is_price_uncrossed
    )
    assert response_cart_item['is_price_uncrossed'] == is_price_uncrossed
    assert not ('full_price_template' in response_json) == is_price_uncrossed
    assert response_json['available_for_checkout']


@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize(
    'experiment_enabled',
    [
        pytest.param(True, marks=[EXPIRING_PRODUCTS_ENABLED]),
        pytest.param(False, marks=[EXPIRING_PRODUCTS_DISABLED]),
    ],
)
@pytest.mark.parametrize('is_expiring', [True, False])
async def test_expiring_cart_item(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        is_expiring,
        experiment_enabled,
):
    price = '355'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    discount_price = '345'
    meta = {'is_expiring': is_expiring}

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_modifier(
        product_id=item_id, value=int(price) - int(discount_price), meta=meta,
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]

    assert response_cart_item['id'] == item_id
    if not experiment_enabled:
        assert 'is_expiring' not in response_cart_item
    else:
        assert response_cart_item['is_expiring'] == is_expiring


# применяет скидку бандлом
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_menu_bundle_discount(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    price = '345'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    discount_price = '336'
    full_price = '690'
    total_price = '672'

    overlord_catalog.add_product(product_id=item_id, price=price)

    # discount per product (345 * 0.055) / 2 = 9.4875, round up -> 10
    grocery_p13n.add_modifier_product_payment(
        product_id=item_id, payment_per_product='5.5', quantity='2',
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': '2',
                'currency': 'RUB',
            },
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['diff_data'] == {}
    assert response_json['full_price_template'] == format_sign_currency(
        full_price,
    )
    assert response_json['total_price_template'] == format_sign_currency(
        total_price,
    )
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    assert response_cart_item['catalog_price'] == discount_price
    assert response_cart_item['full_catalog_price'] == price


# применяет скидку бандлом и деньгами,
# скидка бандлом применяется первой
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_menu_complex_discount(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    price = '345'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'

    overlord_catalog.add_product(product_id=item_id, price=price)

    # применится второй, 177*0,5 = 88,5 -> 88
    grocery_p13n.add_modifier(
        product_id=item_id,
        value='50',
        value_type=modifiers.DiscountValueType.RELATIVE,
    )

    # применится первой, значение скидки ceil(345*0.97) = 335 ->
    # 335 -> 336 (чтобы размазаться равномерно по 2 товарам)
    # цена за 1 товар после этого шага 345 - 336/2= 177
    grocery_p13n.add_modifier_product_payment(
        product_id=item_id, payment_per_product='97', quantity='2',
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': '2',
                'currency': 'RUB',
            },
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    assert response_cart_item['catalog_price'] == '89'
    assert response_cart_item['full_catalog_price'] == '345'


# применяет скидки на меню, корзину и метод оплаты одновременно
@experiments.SUBSTITUTE_UNCROSSED_PRICE
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize('is_price_uncrossed', [True, False])
async def test_menu_cart_and_payment_method_discounts_combo(
        taxi_grocery_cart, overlord_catalog, is_price_uncrossed, grocery_p13n,
):
    price = '355'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    catalog_price = '345'
    discount_price = '337'

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_modifier(
        product_id=item_id,
        value='10',
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={'is_price_uncrossed': is_price_uncrossed},
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value='3',
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
    )
    grocery_p13n.add_cart_modifier(steps=[('60', '5')])

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['diff_data'] == {}
    assert response_json['full_price_template'] == format_sign_currency(
        (catalog_price if is_price_uncrossed else price),
    )

    assert response_json['total_price_template'] == format_sign_currency(
        discount_price,
    )

    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    # в catalog_price действительно возвращается чекаутная цена, с тем чтобы
    # клиент сделал вызов update с этим значением
    assert response_cart_item['catalog_price'] == discount_price
    assert (
        not ('full_catalog_price' in response_cart_item) == is_price_uncrossed
    )
    assert (
        is_price_uncrossed or response_cart_item['full_catalog_price'] == price
    )


# вызов update с применением скидки по методу оплаты
# проверяется недоступность корзины для чекаута, а также, что при этом в
# catalog_price возвращается чекаутная цена
async def test_payment_method_discount_checkout_unavailable(
        taxi_grocery_cart, overlord_catalog, grocery_p13n,
):
    item_id = 'item_id_2'
    catalog_price = '200'
    discount_price = '190'

    overlord_catalog.add_product(product_id=item_id, price=catalog_price)

    grocery_p13n.add_modifier(
        product_id=item_id,
        value='10',
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
    )

    item = {
        'id': item_id,
        'price': catalog_price,
        'quantity': '1',
        'currency': 'RUB',
    }

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'items': [item],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()

    assert response_json['available_for_checkout'] is False
    assert response_json['checkout_unavailable_reason'] == 'price-mismatch'
    assert response_json['hide_price_mismatch'] is True

    assert response_json['items']
    item = response_json['items'][0]
    assert item['id'] == item_id
    # в catalog_price действительно возвращается чекаутная цена, с тем чтобы
    # клиент сделал вызов update с этим значением
    assert item['catalog_price'] == discount_price
    # в строке действительно возвращается менюшная цена
    assert item['catalog_price_template'] == format_sign_currency(
        catalog_price,
    )

    # цена корзины равна чекаутной
    assert response_json[
        'total_price_no_delivery_template'
    ] == format_sign_currency(discount_price)
    assert response_json['total_price_template'] == format_sign_currency(
        discount_price,
    )


# тест информации в логе скидок, который пишется в YT
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_discount_yt_log(
        taxi_grocery_cart,
        mockserver,
        overlord_catalog,
        testpoint,
        grocery_p13n,
):
    price = '100'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_modifier(
        product_id=item_id,
        value='55',
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={'draft_id': 'draft_1'},
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value='4',
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
        meta={
            'picture': 'mastercard',
            'subtitle_tanker_key': 'test_mastercard_discount',
            'draft_id': 'draft_2',
        },
    )
    grocery_p13n.add_cart_modifier(
        steps=[('10', '5')], meta={'draft_id': 'draft_3'},
    )

    pricing_calculation = {
        'products_calculation': [
            {
                'product_id': item_id,
                'steps': [
                    {'bag': [{'price': '100', 'quantity': '1'}]},
                    {
                        'bag': [{'price': '45', 'quantity': '1'}],
                        'discount': {
                            'discount_type': 'menu_discount',
                            'payment_type': 'money_payment',
                            'draft_id': 'draft_1',
                        },
                        'total_discount': '55',
                    },
                    {
                        'bag': [{'price': '40', 'quantity': '1'}],
                        'discount': {
                            'discount_type': 'cart_discount',
                            'draft_id': 'draft_3',
                            'payment_type': 'money_payment',
                        },
                        'total_discount': '5',
                    },
                    {
                        'bag': [{'price': '36', 'quantity': '1'}],
                        'discount': {
                            'discount_type': 'payment_method_discount',
                            'payment_type': 'money_payment',
                            'draft_id': 'draft_2',
                        },
                        'total_discount': '4',
                    },
                ],
            },
        ],
        'cart_calculation': [
            {
                'discount': {
                    'discount_type': 'cart_discount',
                    'draft_id': 'draft_3',
                    'payment_type': 'money_payment',
                },
                'total_discount': '5',
            },
        ],
    }

    @testpoint('yt_calculation_log')
    def yt_calculation_log(data):
        assert data == {
            'calculation': pricing_calculation,
            'coupon': {'value': '0'},
            'currency': 'RUB',
            'service_fees': {'delivery_cost': '0'},
            'total': '36',
        }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'cart_id': cart_id,
            'cart_version': 1,
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        },
        headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    assert yt_calculation_log.times_called == 1


# применяет скидку бандлом, если набрано нужное количество
# не отправляем лейбл на фронт
@pytest.mark.translations(
    discount_descriptions={
        'test_discount_label': {'ru': 'test bundle discount label'},
    },
)
@pytest.mark.parametrize(
    'discount_quantity,label_presented',
    [
        pytest.param('2', False, id='discount applied'),
        pytest.param('5', True, id='discount not applied'),
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_hide_bundle_discount_if_applied(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        discount_quantity,
        label_presented,
):
    price = '345'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'

    overlord_catalog.add_product(product_id=item_id, price=price)
    grocery_p13n.add_modifier_product_payment(
        product_id=item_id,
        payment_per_product='100',
        quantity=discount_quantity,
        meta={'subtitle_tanker_key': 'test_discount_label'},
    )

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart_id,
        'cart_version': 1,
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': '2',
                'currency': 'RUB',
            },
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert ('discount_label' in response_cart_item) == label_presented


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'__default__': 0.1, 'grocery': 0.01},
        '__default__': {'10x': 10, '__default__': 1},
    },
)
async def test_round_cart_discount(
        taxi_grocery_cart, overlord_catalog, grocery_p13n, grocery_depots,
):
    price = '345.55'
    item_id = 'item_id_2'
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100,
        legacy_depot_id='100',
        depot_id='depot-id',
        currency='EUR',
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    await taxi_grocery_cart.invalidate_caches()
    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_cart_modifier(steps=[('0', '10')])

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': '3',
                'currency': 'EUR',
            },
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    assert response_cart_item['catalog_price'] == '342.21'


# проверяем распределение скидки на корзину в размере 58 р.
# Разбивка товаров после размазывания (цена,количество) и после округления
# currency_min_value = 1 :
# [(90,1),(90,2),(90,1),(91,2)] -> [(90,1),(90,2),(90,3)]
# currency_min_value = 0.1 :
# [(90.3,1),(90.3,2),(90.3,1),(90.4,2)] -> [(90.3,1),(90.3,2),(90.3,3)]
# currency_min_value = 0.01 :
# [(90.33,1),(90.33,2),(90.33,1),(90.34,2)] -> [(90.33,1),(90.33,2),(90.33,3)]
# во всех случаях лишняя скидка не превышает
# currency_min_value * максимальное кол-во 1 SKU (в тесте это item_3-3 единицы)
@pytest.mark.config(GROCERY_PRICING_LIBRARY_VERSION=2)
@pytest.mark.parametrize(
    'expected_prices',
    [
        pytest.param(
            ['90', '90', '90'],
            marks=pytest.mark.config(
                CURRENCY_ROUNDING_RULES={
                    'RUB': {'__default__': 0.1, 'grocery': 1},
                    '__default__': {'__default__': 1},
                },
            ),
        ),
        pytest.param(
            ['90.3', '90.3', '90.3'],
            marks=pytest.mark.config(
                CURRENCY_ROUNDING_RULES={
                    'RUB': {'__default__': 0.1, 'grocery': 0.1},
                    '__default__': {'__default__': 1},
                },
            ),
        ),
        pytest.param(
            ['90.33', '90.33', '90.33'],
            marks=pytest.mark.config(
                CURRENCY_ROUNDING_RULES={
                    'RUB': {'__default__': 0.1, 'grocery': 0.01},
                    '__default__': {'__default__': 1},
                },
            ),
        ),
    ],
)
async def test_cart_discount_shared(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        expected_prices,
        grocery_depots,
):
    price = '100'
    item_1 = 'item_1'
    item_2 = 'item_2'
    item_3 = 'item_3'
    grocery_depots.add_depot(
        100, legacy_depot_id='100', depot_id='depot-id', currency='RUB',
    )
    overlord_catalog.add_depot(
        legacy_depot_id='100', depot_id='depot-id', currency='RUB',
    )
    overlord_catalog.add_product(product_id=item_1, price=price)
    overlord_catalog.add_product(product_id=item_2, price=price)
    overlord_catalog.add_product(product_id=item_3, price=price)

    cart_discount_value = '58'
    grocery_p13n.add_cart_modifier(steps=[('0', cart_discount_value)])

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'items': [
            {'id': item_1, 'price': price, 'quantity': '1', 'currency': 'RUB'},
            {'id': item_2, 'price': price, 'quantity': '2', 'currency': 'RUB'},
            {'id': item_3, 'price': price, 'quantity': '3', 'currency': 'RUB'},
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert [
        item['catalog_price'] for item in response_json['items']
    ] == expected_prices


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'__default__': 0.1, 'grocery': 0.01},
        '__default__': {'10x': 10, '__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={'EUR': {'__default__': 1, 'grocery': 2}},
)
async def test_item_min_price(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        experiments3,
        grocery_depots,
):
    experiments.add_lavka_cart_prices_config(
        experiments3,
        currency_min_value='0.01',
        precision=2,
        minimum_total_cost='0.01',
        minimum_item_price='0.01',
        promocode_rounding_value='0.01',
    )
    price = '10'
    item_id = 'item_id_2'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100,
        legacy_depot_id='100',
        depot_id='depot-id',
        currency='EUR',
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    await taxi_grocery_cart.invalidate_caches()

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_cart_modifier(steps=[('0', '100')])

    request = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': '3',
                'currency': 'EUR',
            },
        ],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=request, headers=TAXI_HEADERS,
    )
    response_json = response.json()
    assert response_json['items']
    response_cart_item = response_json['items'][0]
    assert response_cart_item['id'] == item_id
    assert response_cart_item['catalog_price'] == '0.01'
    assert (
        response_json['basic_cart_money_discount_applied']['discount_template']
        == '– 29,97 $SIGN$$CURRENCY$%'
    )


@pytest.mark.parametrize(
    'test_handler',
    [
        '/internal/v2/cart/checkout',
        '/internal/v1/cart/retrieve/raw',
        '/admin/v1/cart/retrieve/raw',
    ],
)
async def test_limited_discount_ids(
        taxi_grocery_cart, cart, overlord_catalog, grocery_p13n, test_handler,
):
    item_id = 'item_id_1'
    price = '123'
    quantity = '1'
    discounts = [50, 10, 5, 2, 1]
    headers = {}
    json = {}

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_p13n.add_modifier(  # correct limited discount
        product_id=item_id,
        value=str(discounts[0]),
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={
            'draft_id': 'draft_1',
            'has_discount_usage_restrictions': True,
            'discount_id': 'correct_discount_id',
        },
    )

    grocery_p13n.add_modifier(  # has not discount id
        product_id=item_id,
        value=str(discounts[1]),
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={'draft_id': 'draft_2', 'has_discount_usage_restrictions': True},
    )

    grocery_p13n.add_modifier(  # usage restrictions : False
        product_id=item_id,
        value=str(discounts[2]),
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={
            'draft_id': 'draft_3',
            'has_discount_usage_restrictions': False,
            'discount_id': 'disabled_restrictions_id',
        },
    )

    grocery_p13n.add_modifier(  # usage restrictions is not specified
        product_id=item_id,
        value=str(discounts[3]),
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={
            'draft_id': 'draft_4',
            'discount_id': 'no_restriction_specified_id',
        },
    )

    grocery_p13n.add_modifier(  # another correct limited discount
        product_id=item_id,
        value=str(discounts[4]),
        discount_type=modifiers.DiscountType.ITEM_DISCOUNT,
        meta={
            'draft_id': 'draft_5',
            'has_discount_usage_restrictions': True,
            'discount_id': 'another_correct_id',
        },
    )

    price_with_discount = str(int(price) - sum(discounts))
    await cart.modify({item_id: {'q': quantity, 'p': price_with_discount}})
    if 'raw' in test_handler:
        await cart.checkout()
        json = {'cart_id': cart.cart_id, 'source': 'SQL'}
        headers = {}
    else:
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }
        headers = {
            'X-Idempotency-Token': 'checkout-token',
            'X-YaTaxi-Session': 'taxi:1234',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        }

    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert 'limited_discount_ids' in response_json
    assert (
        response_json['limited_discount_ids'].sort()
        == ['correct_discount_id', 'another_correct_id'].sort()
    )


# для подсчета цены уцененного товара используется цена обычного товара
@pytest.mark.experiments3(filename='exp_del_type.json')
@experiments.MARKDOWN_DISCOUNTS_ENABLED
async def test_markdown_discount(cart, grocery_p13n, overlord_catalog):
    store_item_id = 'item-id'
    markdown_item_id = store_item_id + ':st-md'
    markdown_stock = 15
    store_stock = 10
    store_price = 100
    markdow_price = 50
    discount = 30

    overlord_catalog.add_product(
        product_id=store_item_id, price=store_price, in_stock=str(store_stock),
    )
    overlord_catalog.add_product(
        product_id=markdown_item_id,
        price=markdow_price,
        in_stock=str(markdown_stock),
    )
    grocery_p13n.add_modifier(product_id=markdown_item_id, value=discount)
    response = await cart.modify(
        products={markdown_item_id: {'q': 1, 'p': store_price - discount}},
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )
    assert response['items'][0]['id'] == markdown_item_id
    assert response['items'][0]['catalog_price'] == str(store_price - discount)
    assert response['items'][0]['quantity_limit'] == str(markdown_stock)


# Проверяем,что скиндки высчитываются корректно
# в зависимости от состава и количества продуктов
@experiments.ENABLE_BUNDLE_DISCOUNT_V2
@pytest.mark.parametrize(
    'product_groups,quantities,total_price,have_discount',
    [
        pytest.param(
            [
                get_product_group(True, 1, ['product_1', 'product_4']),
                get_product_group(True, 1, ['product_2', 'product_5']),
            ],
            ['1', '1', '1'],
            280,
            True,
            id='default bundle discount',
        ),
        pytest.param(
            [
                get_product_group(True, 1, ['product_1', 'product_4']),
                get_product_group(True, 1, ['product_2', 'product_5']),
            ],
            ['2', '1', '1'],
            380,
            True,
            id='two products from group',
        ),
        pytest.param(
            [
                get_product_group(True, 2, ['product_1', 'product_4']),
                get_product_group(True, 1, ['product_2', 'product_5']),
            ],
            ['2', '1', '1'],
            400,
            False,
            id='not enough products for group',
        ),
        pytest.param(
            [get_product_group(False, 2, ['product_1', 'product_4'])],
            ['2', '1', '1'],
            380,
            True,
            id='not unique selection',
        ),
        pytest.param(
            [
                get_product_group(True, 1, ['product_1', 'product_4']),
                get_product_group(True, 1, ['product_2', 'product_5']),
            ],
            ['2', '2', '1'],
            460,
            True,
            id='two combos',
        ),
        pytest.param(
            [
                get_product_group(True, 1, ['product_1', 'product_3']),
                get_product_group(True, 1, ['product_2', 'product_5']),
            ],
            ['1', '2', '1'],
            359,
            True,
            id='two different groups',
        ),
        pytest.param(
            [
                get_product_group(True, 1, ['product_1']),
                get_product_group(True, 1, ['product_1']),
            ],
            ['2', '0', '0'],
            180,
            True,
            id='two groups with one product',
        ),
    ],
)
@pytest.mark.parametrize(
    'test_handler,get_price',
    [
        (
            '/internal/v2/cart/checkout',
            lambda response: response['cart']['diff_data']['cart_total'][
                'actual_template'
            ],
        ),
        (
            '/lavka/v1/cart/v1/retrieve',
            lambda response: response['total_price_template'],
        ),
    ],
)
async def test_bundle_discount(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        grocery_p13n,
        grocery_menu,
        product_groups,
        total_price,
        quantities,
        test_handler,
        get_price,
        have_discount,
):
    product_1 = 'product_1'
    overlord_catalog.add_product(product_id=product_1, price='100')
    product_2 = 'product_2'
    overlord_catalog.add_product(product_id=product_2, price='100')
    product_3 = 'product_3'
    overlord_catalog.add_product(product_id=product_3, price='100')

    await cart.modify({product_1: {'p': '100', 'q': quantities[0]}})
    await cart.modify({product_2: {'p': '100', 'q': quantities[1]}})
    await cart.modify({product_3: {'p': '100', 'q': quantities[2]}})
    combo_id = 'combo_1'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_id)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_id, ['some_product'], product_groups, 'revision',
        ),
    )
    json = {}
    headers = common.TAXI_HEADERS
    if 'raw' in test_handler:
        json = {'cart_id': cart.cart_id, 'source': 'SQL'}
        headers = {}
    else:
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }

    grocery_menu.flush_selected_times_called()
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert grocery_menu.selected_times_called == 1
    assert response.status_code == 200
    if have_discount:
        assert (
            get_price(response.json())
            == f'{str(total_price)} $SIGN$$CURRENCY$'
        )
    elif 'checkout' in test_handler:
        assert response.json()['cart']['diff_data'] == {}


# Проверяем, что применяется самое большое комбо
@experiments.ENABLE_BUNDLE_DISCOUNT_V2
@pytest.mark.parametrize(
    'quantities,total_price',
    [
        pytest.param(['1', '1', '1'], 270, id='one combo'),
        pytest.param(['2', '2', '1'], 450, id='two combo'),
    ],
)
@pytest.mark.parametrize(
    'test_handler,get_price',
    [
        (
            '/internal/v2/cart/checkout',
            lambda response: response['cart']['diff_data']['cart_total'][
                'actual_template'
            ],
        ),
        (
            '/lavka/v1/cart/v1/retrieve',
            lambda response: response['total_price_template'],
        ),
    ],
)
async def test_bundle_discount_two_combos(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        grocery_p13n,
        grocery_menu,
        quantities,
        total_price,
        test_handler,
        get_price,
):
    product_1 = 'product_1'
    overlord_catalog.add_product(product_id=product_1, price='100')
    product_2 = 'product_2'
    overlord_catalog.add_product(product_id=product_2, price='100')
    product_3 = 'product_3'
    overlord_catalog.add_product(product_id=product_3, price='100')

    await cart.modify({product_1: {'p': '100', 'q': quantities[0]}})
    await cart.modify({product_2: {'p': '100', 'q': quantities[1]}})
    await cart.modify({product_3: {'p': '100', 'q': quantities[2]}})
    combo_1 = 'combo_1'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_1)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_1,
            ['some_product'],
            [
                get_product_group(True, 1, [product_1]),
                get_product_group(True, 1, [product_2]),
            ],
            'revision_1',
        ),
    )
    combo_2 = 'combo_2'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_2)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_2,
            ['some_product'],
            [
                get_product_group(True, 1, [product_1]),
                get_product_group(True, 1, [product_2]),
                get_product_group(True, 1, [product_3]),
            ],
            'revision_2',
        ),
    )
    json = {}
    headers = common.TAXI_HEADERS
    if 'raw' in test_handler:
        json = {'cart_id': cart.cart_id, 'source': 'SQL'}
        headers = {}
    else:
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }

    grocery_menu.flush_selected_times_called()
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert grocery_menu.selected_times_called == 1
    assert get_price(response.json()) == f'{total_price} $SIGN$$CURRENCY$'


# Проверяем, что применяется самое большое комбо
@experiments.ENABLE_BUNDLE_DISCOUNT_V2
@pytest.mark.parametrize(
    'quantities,total_price',
    [
        pytest.param(['1', '1', '1', '1'], 370, id='one combo'),
        pytest.param(['2', '2', '1', '1'], 550, id='two combo'),
        pytest.param(['3', '2', '1', '1'], 630, id='three combo'),
    ],
)
@pytest.mark.parametrize(
    'test_handler,get_price',
    [
        (
            '/internal/v2/cart/checkout',
            lambda response: response['cart']['diff_data']['cart_total'][
                'actual_template'
            ],
        ),
        (
            '/lavka/v1/cart/v1/retrieve',
            lambda response: response['total_price_template'],
        ),
    ],
)
async def test_bundle_discount_several_combos(
        taxi_grocery_cart,
        overlord_catalog,
        cart,
        grocery_p13n,
        grocery_menu,
        quantities,
        total_price,
        test_handler,
        get_price,
):
    product_1 = 'product_1'
    overlord_catalog.add_product(product_id=product_1, price='100')
    product_2 = 'product_2'
    overlord_catalog.add_product(product_id=product_2, price='100')
    product_3 = 'product_3'
    overlord_catalog.add_product(product_id=product_3, price='100')
    product_4 = 'product_4'
    overlord_catalog.add_product(product_id=product_4, price='100')

    await cart.modify({product_1: {'p': '100', 'q': quantities[0]}})
    await cart.modify({product_2: {'p': '100', 'q': quantities[1]}})
    await cart.modify({product_3: {'p': '100', 'q': quantities[2]}})
    await cart.modify({product_4: {'p': '100', 'q': quantities[3]}})
    combo_1 = 'combo_1'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_1)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_1,
            ['some_product'],
            [
                get_product_group(True, 1, [product_1]),
                get_product_group(True, 1, [product_2]),
            ],
            'revision_1',
        ),
    )
    combo_2 = 'combo_2'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_2)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_2,
            ['some_product'],
            [
                get_product_group(True, 1, [product_1]),
                get_product_group(True, 1, [product_2]),
                get_product_group(True, 1, [product_3]),
            ],
            'revision_2',
        ),
    )
    combo_3 = 'combo_3'
    grocery_p13n.add_bundle_v2_modifier(value=10, bundle_id=combo_3)
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            combo_3,
            ['some_product'],
            [
                get_product_group(True, 1, [product_1]),
                get_product_group(True, 1, [product_4]),
            ],
            'revision_3',
        ),
    )
    json = {}
    headers = common.TAXI_HEADERS
    if 'raw' in test_handler:
        json = {'cart_id': cart.cart_id, 'source': 'SQL'}
        headers = {}
    else:
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }
    grocery_menu.flush_selected_times_called()
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert grocery_menu.selected_times_called == 1
    assert get_price(response.json()) == f'{total_price} $SIGN$$CURRENCY$'


@experiments.ENABLE_BUNDLE_DISCOUNT_V2
@pytest.mark.parametrize(
    'test_handler',
    ['/internal/v2/cart/checkout', '/lavka/v1/cart/v1/retrieve'],
)
async def test_bundle_empty_cart(
        taxi_grocery_cart, overlord_catalog, cart, grocery_menu, test_handler,
):
    product_1 = 'product_1'
    overlord_catalog.add_product(product_id=product_1, price='100')

    await cart.modify({product_1: {'p': '100', 'q': '1'}})
    await cart.modify({product_1: {'p': '100', 'q': '0'}})
    json = {}
    headers = common.TAXI_HEADERS
    if 'raw' in test_handler:
        json = {'cart_id': cart.cart_id, 'source': 'SQL'}
        headers = {}
    else:
        json = {
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            'cart_id': cart.cart_id,
            'cart_version': cart.cart_version,
            'offer_id': cart.offer_id,
        }
    grocery_menu.flush_selected_times_called()
    await taxi_grocery_cart.post(test_handler, headers=headers, json=json)
    assert grocery_menu.selected_times_called == 0


@pytest.mark.parametrize(
    'test_handler',
    ['/internal/v2/cart/checkout', '/lavka/v1/cart/v1/retrieve'],
)
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud,'
    'antifraud_user_profile_tagged, is_fraud_in_user_profile',
    [
        pytest.param(
            False,
            True,
            False,
            False,
            marks=experiments.ANTIFRAUD_CHECK_DISABLED,
        ),
        pytest.param(
            True,
            False,
            False,
            True,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            True,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            False,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_WITH_CACHE_ENABLED,
        ),
    ],
)
async def test_antifraud(
        taxi_grocery_cart,
        overlord_catalog,
        antifraud,
        grocery_depots,
        grocery_marketing,
        grocery_p13n,
        grocery_user_profiles,
        user_api,
        testpoint,
        cart,
        test_handler,
        antifraud_enabled,
        is_fraud,
        antifraud_user_profile_tagged,
        is_fraud_in_user_profile,
):
    user_agent = 'user-agent'
    city = 'Moscow'
    street = 'Bolshie Kamenshiki'
    house = '8k4'
    flat = '32'
    comment = 'test comment'
    doorcode = '42'
    entrance = '3333'
    floor = '13'
    product_1 = 'product_1'
    yandex_uid = copy.deepcopy(common.YANDEX_UID)
    eats_uid = 'eats-user-id'
    personal_phone_id = 'personal-phone-id'
    appmetrica_device_id = 'appmetrica-device-id'
    payment_method = 'card'
    payment_method_id = '1'
    discount_prohibited = (
        antifraud_enabled
        and is_fraud
        or antifraud_user_profile_tagged
        and is_fraud_in_user_profile
    )
    if discount_prohibited:
        orders_count_uid = 0
        orders_count_glue = 0
        orders_count_p13n = None
    else:
        orders_count_uid = 1
        orders_count_glue = 1
        orders_count_p13n = 2
    orders_count_marketing = orders_count_uid + orders_count_glue
    if test_handler == '/internal/v2/cart/checkout':
        request_source = 'checkout'
    else:
        request_source = 'cart'
    additional_data = copy.deepcopy(keys.DEFAULT_ADDITIONAL_DATA)
    additional_data['doorcode'] = doorcode
    additional_data['entrance'] = entrance
    additional_data['floor'] = floor

    overlord_catalog.add_product(product_id=product_1, price='100')
    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count_uid, user_id=yandex_uid,
    )
    grocery_marketing.add_glue_tag(
        'total_orders_count', orders_count_glue, user_id=yandex_uid,
    )
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100, legacy_depot_id='100', location=keys.DEFAULT_DEPOT_LOCATION,
    )

    await cart.modify({product_1: {'p': '100', 'q': '2'}})
    antifraud.set_is_fraud(is_fraud)
    antifraud.check_discount_antifraud(
        user_id=yandex_uid,
        user_id_service='passport',
        user_personal_phone_id=personal_phone_id,
        user_agent=user_agent,
        application_type='android',
        service_name='grocery',
        short_address=f'{city}, {street} {house} {flat}',
        address_comment=comment,
        flat=flat,
        doorcode=doorcode,
        entrance=entrance,
        floor=floor,
        order_coordinates={'lon': 10.0, 'lat': 20.0},
        device_coordinates={'lon': 11.0, 'lat': 21.0},
        user_device_id=appmetrica_device_id,
        order_amount='200',
        store_id='100',
        request_source=request_source,
    )
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(
            orders_count_p13n,
        ),
    )
    grocery_user_profiles.set_is_fraud(is_fraud_in_user_profile)
    grocery_user_profiles.check_info_request(
        yandex_uid=yandex_uid, personal_phone_id=personal_phone_id,
    )
    grocery_user_profiles.check_save_request(
        yandex_uid=yandex_uid,
        personal_phone_id=personal_phone_id,
        antifraud_info={'name': 'lavka_newcomer_discount_fraud'},
    )

    @testpoint('yt_discount_offer_info')
    def yt_discount_offer_info(discount_offer_info):
        assert discount_offer_info['cart_id'] == cart.cart_id
        assert discount_offer_info['doc'] == {
            'cart_id': cart.cart_id,
            'passport_uid': yandex_uid,
            'eats_uid': eats_uid,
            'personal_phone_id': personal_phone_id,
            'personal_email_id': '',
            'discount_allowed_by_antifraud': not discount_prohibited,
            'discount_allowed': False,
            'discount_allowed_by_rt_xaron': not (
                antifraud_enabled and is_fraud
            ),
            'discount_allowed_by_truncated_flat': True,
            'discount_allowed_by_user_profile': not (
                antifraud_user_profile_tagged and is_fraud_in_user_profile
            ),
            'usage_count': orders_count_marketing,
            'usage_count_according_to_uid': orders_count_uid,
            'usage_count_according_to_glue': orders_count_glue,
            'promocode_id': '',
            'promocode': '',
        }

    headers = copy.deepcopy(common.TAXI_HEADERS)
    headers['X-YaTaxi-User'] = (
        f'eats_user_id={eats_uid}, ' f'personal_phone_id={personal_phone_id}'
    )
    headers['User-Agent'] = user_agent
    headers['X-AppMetrica-DeviceId'] = appmetrica_device_id
    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'additional_data': additional_data,
        'payment_method': {'type': payment_method, 'id': payment_method_id},
    }
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert response.status_code == 200
    if discount_prohibited:
        if not test_handler == '/internal/v2/cart/checkout':
            assert response.json()['notifications'] == [
                {'name': 'cart_newbie_discount_missing'},
            ]

    # 2 requests:
    # - cart.modify
    # - in test_handler
    assert grocery_user_profiles.times_antifraud_info_called() == 2 * int(
        antifraud_user_profile_tagged,
    )
    assert antifraud.times_discount_antifraud_called() == 2 * int(
        antifraud_enabled,
    )
    assert yt_discount_offer_info.times_called == 1


@pytest.mark.parametrize(
    'test_handler',
    ['/internal/v2/cart/checkout', '/lavka/v1/cart/v1/retrieve'],
)
@pytest.mark.parametrize('flat, truncated_flat', [('32', None), ('32.', '32')])
@experiments.ANTIFRAUD_CHECK_ENABLED
async def test_antifraud_truncated_flat(
        taxi_grocery_cart,
        antifraud,
        testpoint,
        cart,
        test_handler,
        flat,
        truncated_flat,
):
    city = 'Moscow'
    street = 'Bolshie Kamenshiki'
    house = '8k4'
    frauder_flat = '32'
    additional_data = copy.deepcopy(keys.DEFAULT_ADDITIONAL_DATA)
    additional_data['flat'] = flat

    await cart.modify({'product_1': {'p': '100', 'q': '2'}})
    antifraud.set_is_fraud(False)
    antifraud.set_frauder_address(f'{city}, {street} {house} {frauder_flat}')
    if truncated_flat:
        truncated_short_address = f'{city}, {street} {house} {truncated_flat}'
    else:
        truncated_short_address = None
    antifraud.check_discount_antifraud(
        short_address=f'{city}, {street} {house} {flat}',
        truncated_short_address=truncated_short_address,
    )

    @testpoint('yt_discount_offer_info')
    def yt_discount_offer_info(discount_offer_info):
        assert discount_offer_info['cart_id'] == cart.cart_id
        assert not discount_offer_info['doc']['discount_allowed']
        assert not discount_offer_info['doc']['discount_allowed_by_antifraud']
        assert discount_offer_info['doc']['discount_allowed_by_rt_xaron'] == (
            flat != frauder_flat
        )
        assert discount_offer_info['doc'][
            'discount_allowed_by_truncated_flat'
        ] == (truncated_flat != frauder_flat)

    headers = copy.deepcopy(common.TAXI_HEADERS)
    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'additional_data': additional_data,
    }
    await taxi_grocery_cart.post(test_handler, headers=headers, json=json)

    if truncated_flat:
        # 3 antifraud requests:
        # - cart.modify (without check)
        # - in handler with full flat
        # - in handler with truncated flat
        assert antifraud.times_discount_antifraud_called() == 3
        assert antifraud.times_full_flat_called() == 1
        assert antifraud.times_truncated_flat_called() == 1
    else:
        assert antifraud.times_discount_antifraud_called() == 2
        assert antifraud.times_full_flat_called() == 1
        assert antifraud.times_truncated_flat_called() == 0
    assert yt_discount_offer_info.times_called == 1
