from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from . import common
from . import const
from . import experiments
from . import tests_headers


@common.HANDLERS
async def test_modes_grocery_with_error_from_13n(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _mock_discount_modifiers(request):
        return mockserver.make_response('Error 500', status=500)

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
    )
    assert response.status_code == 200
    for item in response.json()['products']:
        if item['type'] == 'good':
            assert 'price_template' in item['pricing']
            assert 'price' in item['pricing']
            assert 'discount_pricing' not in item


# в выдаче присутствует информация о скидках из p13n
@common.HANDLERS
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED),
        pytest.param(True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
        pytest.param(True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
async def test_modes_grocery_with_discount(
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_products,
        load_json,
        grocery_p13n,
        test_handler,
        antifraud_enabled,
        is_fraud,
):
    location = const.LOCATION
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    layout = common.build_basic_layout(grocery_products)

    grocery_p13n.add_modifier(product_id='product-1', value='0.7')

    # catalog price is 5.7, so no discount_price in output
    grocery_p13n.add_modifier(product_id='product-2', value='0.3')

    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(orders_count),
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={
            'X-Yandex-UID': yandex_uid,
            'User-Agent': common.DEFAULT_USER_AGENT,
        },
    )
    assert response.status_code == 200

    assert grocery_p13n.discount_modifiers_times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )

    for item in response.json()['products']:
        if item['id'] == 'product-1':
            assert item['discount_pricing'] == {
                'price': '1',
                'price_template': '1 $SIGN$$CURRENCY$',
            }
        elif item['id'] == 'product-2':
            assert 'discount_pricing' not in item


# Проверяем корректное округление цены со скидкой
# и цены в каталоге.
@common.HANDLERS
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'ILS': {'__default__': 0.1}},
    CURRENCY_FORMATTING_RULES={'ILS': {'__default__': 2, 'iso4217': 2}},
)
async def test_modes_grocery_rounded_price(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        grocery_p13n,
        test_handler,
        grocery_depots,
):
    currency = 'ILS'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=const.DEPOT_ID,
        currency=currency,
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, currency=currency,
    )
    layout = common.build_basic_layout(grocery_products)
    overlord_catalog.add_category_tree(
        depot_id=const.DEPOT_ID,
        category_tree={
            'categories': [{'id': 'category-2-subcategory-2'}],
            'products': [
                {
                    'full_price': '10.1',
                    'id': 'product-2',
                    'category_ids': ['category-2-subcategory-2'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )

    grocery_p13n.add_modifier(product_id='product-2', value='4.5')

    await taxi_grocery_api.invalidate_caches()

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-2',
        ),
    )
    assert response.status_code == 200
    item = next(
        item
        for item in response.json()['products']
        if item['id'] == 'product-2'
    )
    assert item['discount_pricing'] == {
        'price': '5.6',
        'price_template': '5,6 $SIGN$$CURRENCY$',
    }
    assert item['pricing'] == {
        'price': '10.1',
        'price_template': '10,1 $SIGN$$CURRENCY$',
    }


# в выдаче присутствует информация о скидках и кэшбэке из p13n
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 1},
        'ILS': {'__default__': 0.1},
    },
    CURRENCY_FORMATTING_RULES={
        'RUB': {'__default__': 2},
        'ILS': {'__default__': 2},
    },
)
@common.HANDLERS
@pytest.mark.parametrize(
    'currency, expected_price, expected_price_template, expected_cashback',
    [
        (
            'RUB',
            {'product-1': '1', 'product-2': '2'},
            {
                'product-1': '1 $SIGN$$CURRENCY$',
                'product-2': '2 $SIGN$$CURRENCY$',
            },
            {'product-1': '4', 'product-2': '6'},
        ),
        (
            'ILS',
            {'product-1': '1.1', 'product-2': '2.2'},
            {
                'product-1': '1,1 $SIGN$$CURRENCY$',
                'product-2': '2,2 $SIGN$$CURRENCY$',
            },
            {'product-1': '2.5', 'product-2': '5.3'},
        ),
    ],
)
async def test_modes_grocery_with_cashback(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_depots,
        grocery_p13n,
        load_json,
        test_handler,
        currency,
        expected_price,
        expected_price_template,
        expected_cashback,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(depot_id=const.DEPOT_ID, currency=currency)
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    grocery_p13n.add_modifier(product_id='product-1', value='1.09')
    grocery_p13n.add_modifier(
        product_id='product-1',
        value='1.23',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.add_modifier(
        product_id='product-1',
        value='100',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
        value_type=p13n.DiscountValueType.RELATIVE,
    )

    grocery_p13n.add_modifier(product_id='product-2', value='3.48')
    grocery_p13n.add_modifier(
        product_id='product-2',
        value='4.56',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )
    grocery_p13n.add_modifier(
        product_id='product-2',
        value='30',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
        value_type=p13n.DiscountValueType.RELATIVE,
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
    )
    assert response.status_code == 200

    for product in response.json()['products']:
        if product['id'] not in ['product-1', 'product-2']:
            continue
        assert product['discount_pricing'] == {
            'price': expected_price[product['id']],
            'price_template': expected_price_template[product['id']],
            'cashback': expected_cashback[product['id']],
        }


# проверяем что для продукта уходит название и цвет стикера
@common.HANDLERS
async def test_modes_discount_label_and_color(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)
    color = '#51c454'

    grocery_p13n.add_modifier(
        product_id='product-1',
        value='0.1',
        meta={'title_tanker_key': 'test_discount_label', 'label_color': color},
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    for item in response.json()['products']:
        if item['id'] == 'product-1':
            assert item['discount_pricing']['discount_label'] == '-50% за два'
            assert item['discount_pricing']['label_color'] == color


# Пробрасывает флаги из метаинформации о скидке.
@common.HANDLERS
@pytest.mark.parametrize(
    'forward_flag',
    [
        pytest.param(
            'is_expiring', marks=[experiments.EXPIRING_PRODUCTS_ENABLED],
        ),
        pytest.param('is_price_uncrossed'),
    ],
)
@pytest.mark.parametrize('forward_flag_value', [True, False])
async def test_forwards_flags_from_p13n(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        load_json,
        forward_flag,
        forward_flag_value,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)
    grocery_p13n.add_modifier(
        product_id='product-1',
        value='0.1',
        meta={forward_flag: forward_flag_value},
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    for item in response.json()['products']:
        if item['id'] == 'product-1':
            assert item['discount_pricing'][forward_flag] == forward_flag_value


# Проверяем что неперечеркнутые цены заменяют
# цену в каталоге в выдаче ручки
@common.HANDLERS
@pytest.mark.parametrize(
    'should_replace',
    [
        pytest.param(False, id='not replace by default'),
        pytest.param(
            True,
            marks=[experiments.SUBSTITUTE_UNCROSSED_PRICE_ENABLED],
            id='replace by experiment',
        ),
        pytest.param(
            False,
            marks=[experiments.SUBSTITUTE_UNCROSSED_PRICE_DISABLED],
            id='not replace by experiment',
        ),
    ],
)
async def test_replace_catalog_price(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_p13n,
        load_json,
        should_replace,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)
    grocery_p13n.add_modifier(
        product_id='product-1', value='1', meta={'is_price_uncrossed': True},
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.status_code == 200
    res_product = response.json()['products'][2]
    if should_replace:
        assert res_product['pricing']['price'] == '1'
        assert res_product['pricing']['price_template'] == '1 $SIGN$$CURRENCY$'
        assert 'price' not in res_product['discount_pricing']
        assert 'price_template' not in res_product['discount_pricing']
    else:
        assert res_product['pricing']['price'] == '2'
        assert res_product['pricing']['price_template'] == '2 $SIGN$$CURRENCY$'
        assert res_product['discount_pricing']['price'] == '1'
        assert (
            res_product['discount_pricing']['price_template']
            == '1 $SIGN$$CURRENCY$'
        )


# Проверяем что для продукта не показывается скидка продуктом,
# если остатков меньше чем требуемое колличество для скидки.
# остатки для product-1 = 10, если скидка от 5 товаров - отсылаем скидку,
# если от 50, не отсылаем
@common.HANDLERS
@pytest.mark.parametrize(
    'discount_quantity,discount_presented',
    [
        pytest.param(5, True, id='sufficient'),
        pytest.param(50, False, id='insufficient'),
    ],
)
async def test_modes_product_payment_discount(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
        discount_quantity,
        discount_presented,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)
    grocery_p13n.add_modifier_product_payment(
        product_id='product-1',
        payment_per_product='50',
        quantity=str(discount_quantity),
        meta={'title_tanker_key': 'test_discount_label'},
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    for item in response.json()['products']:
        if item['id'] == 'product-1':
            if discount_presented:
                assert (
                    item['discount_pricing']['discount_label'] == '-50% за два'
                )
            else:
                assert 'discount_pricing' not in item


# Проверка правильного кол-ва скидки в новом (discount_value) поле
@common.HANDLERS
@experiments.USE_AUTOMATIC_DISCOUNT_LABEL
@pytest.mark.config(GROCERY_API_DEFAULT_DISCOUNT_LABEL_COLOR='#e14138')
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        'RUB': {
            '__default__': 1,
            'grocery': 2,  # проверяем что юзается grocery
        },
    },
)
async def test_modes_discount_automatic_label(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        grocery_products,
        load_json,
        test_handler,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    grocery_p13n.add_modifier_percent_discount(
        product_id='product-1', discount_percentage=50,
    )
    discount_value = 2.84

    grocery_p13n.add_modifier_absolute_discount(
        product_id='product-2', discount_value=discount_value,
    )

    response = await taxi_grocery_api.post(
        test_handler,
        json=common.build_grocery_mode_request(
            test_handler,
            layout.layout_id,
            'category-group-1',
            'virtual-category-1',
        ),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    for item in response.json()['products']:
        if item['id'] == 'product-1':
            assert item['discount_pricing']['discount_label'] == '-50%'
            assert item['discount_pricing']['label_color'] == '#e14138'
        if item['id'] == 'product-2':
            # catalog price is 5.7
            assert (
                item['discount_pricing']['discount_label']
                == '-' + str(int(discount_value * 100 / 5.7)) + '%'
            )
            assert item['discount_pricing']['label_color'] == '#e14138'
