# pylint: disable=too-many-lines

import datetime

from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from . import common
from . import conftest
from . import const
from . import experiments
from . import tests_headers


# Ручка modes/product, сценарий перехода c диплинка на продукт
@pytest.mark.parametrize('product_id', ['product-1', 'product-2'])
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED),
        pytest.param(True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
        pytest.param(True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
@conftest.DIFFERENT_LAYOUT_SOURCE
async def test_modes_product_200(
        taxi_grocery_api,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        overlord_catalog,
        load_json,
        product_id,
        empty_upsale,
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

    if product_id == 'product-2':
        grocery_p13n.add_modifier(product_id='product-2', value='2')

    json = {
        'position': {'location': location},
        'product_id': product_id,
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }

    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(orders_count),
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={
            'X-Yandex-UID': yandex_uid,
            'Accept-Language': 'en',
            'User-Agent': common.DEFAULT_USER_AGENT,
        },
    )
    assert response.status_code == 200

    assert grocery_p13n.discount_modifiers_times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )

    data = response.json()

    assert data['product']['id'] == product_id

    if product_id == 'product-2':
        assert 'discount_pricing' in data['product']

    # при отсутствии параметра modes == ['upsale'] апсейл не возвращается и в
    # сам апсейл не ходим
    assert data['modes'] == []
    assert empty_upsale.times_called == 0


# при включенном эксперименте распроданный товар должен возвращаться;
# при выключенном - 404
@pytest.mark.parametrize(
    'sold_out_enabled',
    [
        pytest.param(True, marks=[experiments.SHOW_SOLD_OUT_ENABLED]),
        pytest.param(False),
    ],
)
async def test_modes_product_sold_out(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        load_json,
        sold_out_enabled,
):
    product_id = 'product-3'
    location = const.LOCATION

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    if sold_out_enabled:
        assert response.status_code == 200
        assert response.json()['product']['id'] == product_id
    else:
        assert response.status_code == 404
        assert response.json()['code'] == 'PRODUCT_NOT_FOUND'


@pytest.mark.parametrize(
    'product_id,location,error_code',
    [
        pytest.param(
            'product-1', [1, 1], 'DEPOT_NOT_FOUND', id='DEPOT_NOT_FOUND',
        ),
        pytest.param(
            'product-3',
            const.LOCATION,
            'PRODUCT_NOT_FOUND',
            id='PRODUCT_NOT_FOUND',
        ),
    ],
)
async def test_modes_product_404(
        taxi_grocery_api,
        overlord_catalog,
        mockserver,
        load_json,
        product_id,
        location,
        error_code,
):
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, const.LOCATION,
    )

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/catalog/discounts',
    )
    def _mock_grocery_p13n(mock_request):
        return mockserver.make_response(
            json={
                'code': 'DISCOUNTS_NOT_AVAILABLE',
                'message': 'error_message',
            },
            status=400,
        )

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == error_code


async def test_modes_product_with_discount_label_and_color(
        taxi_grocery_api, grocery_p13n, overlord_catalog, load_json,
):
    product_id = 'product-1'
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    color = '#51c454'
    grocery_p13n.add_modifier(
        product_id=product_id,
        value='0.1',
        meta={'title_tanker_key': 'test_discount_label', 'label_color': color},
    )

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()

    assert (
        data['product']['discount_pricing']['discount_label'] == '-50% за два'
    )
    assert data['product']['discount_pricing']['label_color'] == color
    assert data['modes'] == []


# Проверяем выдачу скидки кэшбэком из p13n
async def test_modes_grocery_with_cashback(
        taxi_grocery_api, overlord_catalog, load_json, grocery_p13n,
):
    location = const.LOCATION
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    cashback = 1.23
    expected_cashback = '2'  # ceil(cashback)

    grocery_p13n.add_modifier(
        product_id='product-1',
        value=str(cashback),
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['product']['discount_pricing']['cashback'] == expected_cashback
    assert data['modes'] == []


# Пробрасывает флаги из метаинформации о скидке.
@pytest.mark.parametrize(
    'forward_flag, experiment_enabled',
    [
        pytest.param(
            'is_expiring', True, marks=[experiments.EXPIRING_PRODUCTS_ENABLED],
        ),
        pytest.param(
            'is_expiring',
            False,
            marks=[experiments.EXPIRING_PRODUCTS_DISABLED],
        ),
        pytest.param('is_price_uncrossed', True),
    ],
)
@pytest.mark.parametrize('forward_flag_value', [True, False])
async def test_forwards_flags_from_p13n_product(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        forward_flag,
        forward_flag_value,
        experiment_enabled,
):
    location = const.LOCATION
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    grocery_p13n.add_modifier(
        product_id=product_id,
        value='1',
        meta={forward_flag: forward_flag_value},
    )

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    if not experiment_enabled:
        assert forward_flag not in data['product']['discount_pricing']
    else:
        assert (
            data['product']['discount_pricing'][forward_flag]
            == forward_flag_value
        )
    assert data['modes'] == []


async def test_modes_product_offer_time(
        taxi_grocery_api, load_json, overlord_catalog, offers, mockserver,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )

    date = '2020-01-21T10:00:00+00:00'
    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=datetime.datetime.fromisoformat(date),
        depot_id=depot_id,
        location=location,
    )

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _mock_p13n_discount_modifiers(request):
        assert request.json['offer_time'] == date
        return {'modifiers': []}

    json = {
        'position': {'location': location},
        'product_id': product_id,
        'offer_id': offer_id,
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert _mock_p13n_discount_modifiers.times_called == 1


# Проверяем что неперечеркнутые цены заменяют
# цену в каталоге в выдаче ручки
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
async def test_replace_catalog_price_product(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        should_replace,
):
    location = const.LOCATION
    product_id = 'product-1'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    grocery_p13n.add_modifier(
        product_id=product_id, value='1.09', meta={'is_price_uncrossed': True},
    )

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    res_product = data['product']
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
    assert data['modes'] == []


@pytest.mark.experiments3(
    name='grocery_product_card_content',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'content': [
                    # {'title_key': '', 'attributes': ['pfc']}, Вернем в LAVKABACKEND-9188
                    {
                        'title_key': 'product_content_manufacturer',
                        'attributes': ['brand', 'manufacturer', 'country'],
                        'delimiter': ', ',
                    },
                    {
                        'title_key': 'product_content_shelf_life',
                        'attributes': ['shelf_life'],
                    },
                    {
                        'title_key': 'product_content_after_open',
                        'attributes': ['after_open'],
                    },
                    {
                        'title_key': 'product_content_ingredients',
                        'attributes': ['ingredients'],
                    },
                    {
                        'title_key': 'product_content_description',
                        'attributes': ['description'],
                    },
                    {
                        'title_key': 'product_content_long_title',
                        'attributes': ['long_title'],
                    },
                    {
                        'title_key': 'product_content_condition',
                        'attributes': ['condition'],
                    },
                    {
                        'title_key': 'product_content_disclaimer',
                        'attributes': ['disclaimer'],
                    },
                    {
                        'title_key': 'product_content_title',
                        'attributes': ['title'],
                    },
                    {
                        'title_key': 'write_off_before_title',
                        'attributes': ['write_off_before'],
                    },
                ],
            },
        },
    ],
)
@pytest.mark.config(
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION={
        'keyset': 'wms_items',
        'suffix': '_description',
    },
)
@pytest.mark.translations(
    grocery_localizations={'decimal_separator': {'fr': ',', 'en': '.'}},
    overlord_catalog={
        'write_off_before_key': {
            'en': 'not less than %(write_off_before)s days',
        },
        'zero_write_off_before_key': {'en': 'without expiration date'},
    },
)
@pytest.mark.parametrize(
    'deleted_manufacturer_option,expected_manufacturer_value',
    [
        pytest.param('brand', 'some company, Russia', id='without brand'),
        pytest.param(
            'manufacturer', 'ООО ААА, Russia', id='without manufacturer',
        ),
        pytest.param(
            None,
            'ООО ААА, some company, Russia',
            id='full manufacturer content',
        ),
    ],
)
@pytest.mark.parametrize(
    'deleted_storage_option',
    [
        pytest.param(1, id='without after_open'),
        pytest.param(None, id='with after_open'),
    ],
)
@pytest.mark.parametrize(
    'locale,decimal_separator',
    [
        pytest.param('fr', ',', id='coma'),
        pytest.param('en', '.', id='point'),
        pytest.param('ar', '.', id='no translate'),
    ],
)
@pytest.mark.parametrize(
    'write_off_before,expected_write_off_before_template',
    [('17', 'not less than {} days'), ('0', 'without expiration date')],
)
async def test_modes_product_card_content(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        deleted_manufacturer_option,
        expected_manufacturer_value,
        deleted_storage_option,
        locale,
        decimal_separator,
        write_off_before,
        expected_write_off_before_template,
):
    """ Checks that product content is building from
    grocery_product_card_content experiment """

    location = const.LOCATION

    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )

    if deleted_manufacturer_option:
        del products_data[0]['options'][deleted_manufacturer_option]

    if deleted_storage_option:
        del products_data[0]['options']['storage'][deleted_storage_option]

    products_data[0]['options']['storage'].append(
        {'key': 'write_off_before', 'value': write_off_before},
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, products_data=products_data,
    )

    json = {'position': {'location': location}, 'product_id': 'product-1'}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'content' in response_json['product']

    content = response_json['product']['content']

    expected_result = {
        'items': [
            {
                'items': [
                    {'title': 'Calories', 'value': '100'},
                    {'title': 'Protein', 'value': f'18{decimal_separator}9'},
                    {'title': 'Fat', 'value': f'15{decimal_separator}678'},
                    {'title': 'Carbohydrate', 'value': '10'},
                ],
                'measure_title': 'per 100 grams',
                'type': 'pfc',
            },
            {
                'attributes': ['brand', 'manufacturer', 'country'],
                'title': 'Manufacturer',
                'type': 'text',
                'value': expected_manufacturer_value,
            },
            {
                'attributes': ['shelf_life'],
                'title': 'Shelf life',
                'type': 'text',
                'value': '12 days',
            },
            {
                'attributes': ['after_open'],
                'title': 'After open',
                'type': 'text',
                'value': '14 days',
            },
            {
                'attributes': ['ingredients'],
                'title': 'Content',
                'type': 'text',
                'value': 'piece of something',
            },
            {
                'attributes': ['description'],
                'title': 'Description',
                'type': 'text',
                'value': 'product-1-description',
            },
            {
                'attributes': ['long_title'],
                'title': 'Full title',
                'type': 'text',
                'value': 'product-1-long-title',
            },
            {
                'attributes': ['condition'],
                'title': 'Condition',
                'type': 'text',
                'value': 'between 10C˚ and 30C˚',
            },
            {
                'attributes': ['disclaimer'],
                'title': 'Disclaimer',
                'type': 'text',
                'value': 'Disclaimer text',
            },
            {
                'attributes': ['title'],
                'title': 'Title',
                'type': 'text',
                'value': 'product-1-title',
            },
            {
                'attributes': ['write_off_before'],
                'title': 'write_off_before_title',
                'type': 'text',
                'value': expected_write_off_before_template.format(
                    write_off_before,
                ),
            },
        ],
    }

    if deleted_storage_option:
        del expected_result['items'][3]

    assert content == expected_result


# Проверяем правильность шаблона: разделитель и количество знаков
@pytest.mark.parametrize('locale', ['en', 'fr', 'ru'])
@pytest.mark.parametrize(
    'price,expected_result',
    [('5.30', '5.30'), ('5.25', '5.25'), ('1.001', '1.00')],
)
@pytest.mark.parametrize('currency', ['EUR', 'GBP', 'RUB'])
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'grocery': 0.01},
        'GBP': {'grocery': 0.01},
        '__default__': {'__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={
        'EUR': {'__default__': 2, 'iso4217': 2},
        'GBP': {'__default__': 2, 'iso4217': 2},
        'RUB': {'grocery': 2},
    },
    LOCALES_SUPPORTED=['en', 'fr', 'ru'],
)
async def test_price_format_and_trailing_zeros(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        load_json,
        locale,
        price,
        expected_result,
        currency,
        grocery_depots,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=const.DEPOT_ID,
        currency=currency,
    )

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location=location, currency=currency,
    )
    if currency == 'RUB':
        expected_result = expected_result.split('.')[0]
    product_id = 'product-1'
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree={
            'categories': [{'id': 'category-2-subcategory-2'}],
            'products': [
                {
                    'full_price': price,
                    'id': product_id,
                    'category_ids': ['category-2-subcategory-2'],
                    'rank': 1,
                },
            ],
            'markdown_products': [],
        },
    )

    grocery_p13n.add_modifier(product_id=product_id, value=price)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': locale},
    )
    assert response.status_code == 200
    actual_price = response.json()['product']['pricing']['price_template']
    if locale == 'en':
        assert actual_price == '$SIGN${}$CURRENCY$'.format(expected_result)
    if locale in ('fr', 'ru'):
        expected_result = expected_result.replace('.', ',')
        assert actual_price == '{} $SIGN$$CURRENCY$'.format(expected_result)


def parametrize_amount_price_exp(amount_price_exp_enabled):
    return pytest.mark.experiments3(
        match={
            'predicate': {'type': 'true'},
            'enabled': amount_price_exp_enabled,
        },
        is_config=True,
        name='grocery_api_price_per_unit',
        consumers=['grocery-api/modes'],
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': amount_price_exp_enabled},
            },
        ],
    )


@pytest.mark.translations(
    overlord_catalog={
        'amount_price': {'en': '%(price)s/%(amount)s%(amount_units)s'},
    },
)
@pytest.mark.parametrize(
    'amount,amount_units,price,discount_price,amount_part,amount_pack',
    [
        # Ожидаем цену 2.2 / 1.5 * 1 = 1.47 без скидки
        # и 1.2 / 1.5 * 1 = 0.8 со скидкой
        ('1.5', 'кг', '1.47', '0.80', '1', None),
        # Ожидаем цену 2.2 / 300 * 100 = 0.73 без скидки
        # и 1.2 / 300 * 100 = 0.4 со скидкой
        ('300', 'г', '0.73', '0.40', '100', None),
        # Ожидаем цену 2.2 / (150 * 2) * 100 = 0.73 без скидки
        # и 1.2 / (150 * 2) * 100 = 0.4 со скидкой
        ('150', 'г', '0.73', '0.40', '100', 2),
    ],
)
@pytest.mark.parametrize(
    'amount_price_exp_enabled',
    [
        pytest.param(True, marks=(parametrize_amount_price_exp(True))),
        pytest.param(False, marks=(parametrize_amount_price_exp(False))),
    ],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'EUR': {'grocery': 0.01},
        '__default__': {'__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={'EUR': {'__default__': 2, 'iso4217': 2}},
    LOCALES_SUPPORTED=['en', 'fr', 'ru'],
)
async def test_modes_product_amount_price(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        grocery_p13n,
        amount,
        amount_units,
        price,
        discount_price,
        amount_part,
        amount_pack,
        amount_price_exp_enabled,
        grocery_depots,
):
    """ amount_price should be in response if amount price experiment is enabled
    """
    currency = 'EUR'
    location = const.LOCATION

    product_id = 'product-1'
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    products_data[0]['options']['amount'] = amount
    products_data[0]['options']['amount_units'] = amount_units
    products_data[0]['options']['amount_pack'] = amount_pack

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.LEGACY_DEPOT_ID),
        depot_id=const.DEPOT_ID,
        currency=currency,
    )

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data=products_data,
        currency=currency,
    )

    grocery_p13n.add_modifier(product_id=product_id, value='1')

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}, 'product_id': product_id}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    product = response.json()['product']
    if amount_price_exp_enabled:
        # проверяем что цена равняется full_price/amount * amount_part
        assert product['pricing']['amount_price'] == str(float(price))
        # проверяем что цена со скидкой равняется
        # discount_price/amount * amount_part
        assert product['discount_pricing']['amount_price'] == str(
            float(discount_price),
        )
        # проверяем шаблон и форматирование
        # цены в нем(количество знаков после запятой)
        assert product['pricing'][
            'amount_price_template'
        ] == '$SIGN${}$CURRENCY$/{}{}'.format(price, amount_part, amount_units)
        # проверяем шаблон и форматирование цены
        # со скидкой в нем(количество знаков после запятой)
        assert (
            product['discount_pricing']['amount_price_template']
            == '$SIGN${}$CURRENCY$/{}{}'.format(
                discount_price, amount_part, amount_units,
            )
        )
    else:
        # если фича отключена amount_price не должно быть в ответе ручки
        assert 'amount_price' not in product['pricing']
        assert 'amount_price' not in product['discount_pricing']
        assert 'amount_price_template' not in product['pricing']
        assert 'amount_price_template' not in product['discount_pricing']


# Ручка modes/product резолвит лавку по external_depot_id
async def test_modes_product_resolve_depot_by_external_depot_id(
        taxi_grocery_api, grocery_p13n, overlord_catalog, load_json,
):
    location = [100, 100]
    product_id = 'product-1'

    external_depot_id = const.LEGACY_DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location=const.LOCATION,
        legacy_depot_id=external_depot_id,
    )

    json = {
        'position': {'location': location},
        'product_id': product_id,
        'external_depot_id': external_depot_id,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['product']['id'] == product_id


# проверяем что цена в каталоге повышается если товар
# задан в эксперрименте повышения цен
# повышающий коэфициет = 3.5, цена товара = 2.2, скидка = 1.
# тогда финальная цена = floor(3.5*2.2)=7, скидочная цена 7-1
@experiments.GROCERY_PRICE_RISE_MAP
async def test_modes_product_price_rise(
        taxi_grocery_api, grocery_p13n, overlord_catalog, load_json,
):
    location = const.LOCATION

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    grocery_p13n.add_modifier(product_id='product-1', value='1')

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={'position': {'location': location}, 'product_id': 'product-1'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['product']['id'] == 'product-1'
    assert data['product']['pricing'] == {
        'price_template': '7 $SIGN$$CURRENCY$',
        'price': '7',
    }
    assert data['product']['discount_pricing'] == {
        'price_template': '6 $SIGN$$CURRENCY$',
        'price': '6',
    }


def _prepare_test_context_markdown(
        overlord_catalog, load_json, grocery_caas_markdown=None,
):
    depot_id = const.DEPOT_ID
    # legacy_depot_id = '123'
    # overlord_catalog.add_depot(
    #     legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    # )
    # overlord_catalog.add_location(
    #     location=const.LOCATION
    #     depot_id=depot_id,
    #     legacy_depot_id=legacy_depot_id,
    # )

    grocery_caas_markdown.add_product(product_id='product-1')
    overlord_catalog.add_category_tree(
        depot_id=depot_id,
        category_tree=load_json('overlord_md_category_tree.json'),
    )

    overlord_catalog.add_categories_data(
        new_categories_data=load_json('overlord_md_categories_data.json'),
    )

    overlord_catalog.add_products_data(
        new_products_data=load_json('overlord_md_products_data.json'),
    )

    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=load_json('overlord_md_products_stocks.json'),
    )


# проверка случая, товар полностью перемещен в markdown:
# должен корректно возвращаться как markdown, не должен возвращаться как
# обычный
@pytest.mark.parametrize(
    'product_id, status, code',
    [
        pytest.param(
            'product-1:st-md', 200, None, id='request markdown product',
        ),
        pytest.param(
            'product-1',
            404,
            'PRODUCT_NOT_FOUND',
            id='request regular product',
        ),
    ],
)
async def test_modes_product_markdown(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_markdown,
        load_json,
        product_id,
        status,
        code,
):
    location = const.LOCATION

    _prepare_test_context_markdown(
        overlord_catalog, load_json, grocery_caas_markdown,
    )

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    body = response.json()
    assert response.status == status
    if status == 200:
        assert body['product']['id'] == product_id
    else:
        assert body['code'] == 'PRODUCT_NOT_FOUND'


# проверяем что ручка product возвращает скидку на уцененный товар
@experiments.MARKDOWN_DISCOUNTS_ENABLED
async def test_modes_product_markdown_discount(
        taxi_grocery_api, overlord_catalog, grocery_p13n,
):
    depot_id = const.DEPOT_ID
    # legacy_depot_id = '123'
    # overlord_catalog.add_depot(
    #     legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    # )
    # overlord_catalog.add_location(
    #     location=DEFAULT_LOCATION,
    #     depot_id=depot_id,
    #     legacy_depot_id=legacy_depot_id,
    # )

    product_id = 'product-1:st-md'
    common.build_overlord_catalog_products(
        overlord_catalog,
        [{'id': 'category-1', 'products': [product_id[:-6]]}],
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': product_id,
                'quantity_limit': '5',
            },
        ],
    )

    grocery_p13n.add_modifier(product_id=product_id, value='100')

    json = {'position': {'location': const.LOCATION}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    body = response.json()
    assert response.status == 200
    assert body['product']['id'] == product_id
    assert body['product']['pricing']['price'] == '123'
    assert body['product']['discount_pricing']['price'] == '23'


@pytest.mark.parametrize('is_markdown', [True, False])
@experiments.MARKDOWN_DISCOUNTS_ENABLED
async def test_modes_product_discount_master_categories(
        load_json,
        mockserver,
        taxi_grocery_api,
        overlord_catalog,
        grocery_caas_markdown,
        is_markdown,
):
    master_categories = ['master_category_1', 'master_category_2']

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _mock_p13n_discount_modifiers(request):
        assert (
            request.json['items'][0]['master_categories'] == master_categories
        )
        return {'modifiers': []}

    location = const.LOCATION
    depot_id = const.DEPOT_ID

    _prepare_test_context_markdown(
        overlord_catalog, load_json, grocery_caas_markdown,
    )

    product_id = 'product-1'

    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '10',
                'product_id': product_id,
                'quantity_limit': '5',
            },
        ],
    )
    overlord_catalog.add_products_data(
        new_products_data=[
            {
                'description': 'product-1-description',
                'image_url_template': 'product-1-image-url-template',
                'long_title': 'product-1-long-title',
                'product_id': product_id,
                'title': 'product-1-title',
                'master_categories': master_categories,
            },
        ],
    )

    if is_markdown:
        product_id += ':st-md'

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    body = response.json()
    assert response.status == 200
    assert body['product']['id'] == product_id
    assert _mock_p13n_discount_modifiers.times_called == 1


@pytest.mark.translations(
    wms_attributes={
        'sahar': {'en': 'shugar'},
        'fish': {'en': 'translated_fish'},
    },
)
@pytest.mark.config(
    GROCERY_API_ATTRIBUTES_ICONS={
        'sahar': {'icon_link': 'sahar_icon'},
        'fish': {'icon_link': 'fish_icon', 'big_icon_link': 'big_fish_icon'},
    },
)
async def test_modes_product_attributes_in_response(
        taxi_grocery_api, overlord_catalog, load_json,
):
    location = const.LOCATION
    product_id = 'product-1'
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, products_data,
    )

    json = {
        'position': {'location': location},
        'product_id': product_id,
        'user_preferences': {
            'important_ingredients': ['sahar'],
            'main_allergens': ['fish', 'some more', 'sahar'],
            'custom_tags': ['halal'],
        },
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    options = response.json()['product']['options']
    assert options['important_ingredients'] == [
        {'attribute': 'sahar', 'title': 'shugar', 'icon_link': 'sahar_icon'},
    ]
    assert options['main_allergens'] == [
        {
            'attribute': 'fish',
            'title': 'translated_fish',
            'icon_link': 'fish_icon',
            'big_icon_link': 'big_fish_icon',
        },
    ]
    assert options['custom_tags'] == [{'attribute': 'halal', 'title': 'halal'}]
    assert options['attributes'] == {
        'important_ingredients': ['sahar'],
        'main_allergens': ['fish'],
        'custom_tags': ['halal'],
    }


@pytest.mark.translations(
    wms_attributes={
        'sticker_id_1': {'en': 'some text'},
        'sticker_id_2': {'en': 'another text'},
    },
)
@pytest.mark.config(GROCERY_LOCALIZATION_ATTRIBUTES_KEYSET='wms_attributes')
@common.STICKERS_INFO_CONFIG
async def test_modes_product_stickers(
        taxi_grocery_api, overlord_catalog, load_json,
):
    location = const.LOCATION
    product_id = 'product-1'
    products_data = [
        {
            'description': 'product-1-description',
            'image_url_template': 'product-1-image-url-template',
            'long_title': 'product-1-long-title',
            'options': {
                'amount': '',
                'amount_units': '',
                'brand': '',
                'country_codes': [],
                'custom_tags': [],
                'ingredients': [],
                'pfc': [],
                'shelf_life_measure_unit': '',
                'storage': [],
                'photo_stickers': ['sticker_id_1', 'sticker_id_2'],
            },
            'product_id': 'product-1',
            'title': 'product-1-title',
        },
    ]

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, products_data,
    )

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', json=json, headers={},
    )
    assert response.status_code == 200
    expected_stickers = [
        {
            'sticker_color': 'yellow',
            'text': 'some text',
            'text_color': 'white',
        },
        {
            'sticker_color': 'black',
            'text': 'another text',
            'text_color': 'white',
        },
    ]
    stickers = response.json()['product']['stickers']
    assert stickers == expected_stickers


@experiments.DESCRIPTION_INGREDIENTS_CONTENT
@pytest.mark.config(
    GROCERY_LOCALIZATION_PRODUCT_DESCRIPTION={
        'keyset': 'wms_items',
        'suffix': '_description',
    },
)
@pytest.mark.parametrize('locale', ['en', 'ru'])
@pytest.mark.parametrize(
    'product_id',
    [
        pytest.param('product-1', id='translation exists'),
        pytest.param('product-2', id='translation is absent'),
        pytest.param('product-3', id='translation is empty'),
    ],
)
async def test_modes_translate_product_card_content(
        taxi_grocery_api, overlord_catalog, load_json, locale, product_id,
):
    """ Checks that product content translated correctly """

    location = const.LOCATION

    products_data = load_json('overlord_catalog_products_data.json')

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data=products_data,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': product_id,
                'quantity_limit': '5',
            },
        ],
    )

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'content' in response_json['product']

    content = response_json['product']['content']

    expected_result = load_json(
        'modes_translate_product_content_expected.json',
    )[product_id][locale]

    assert content == expected_result


# modes/product возвращает пустой список информеров
# при их отсутствии
async def test_modes_product_empty_informers(
        taxi_grocery_api, overlord_catalog, load_json,
):
    location = const.LOCATION

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={'position': {'location': location}, 'product_id': 'product-1'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json()['informers'] == []


# modes/product возвращает только информеры для продуктов
# из запроса
@experiments.GROCERY_API_DIFFERENT_PLACES_INFORMER
async def test_modes_product_informers(
        taxi_grocery_api, overlord_catalog, load_json,
):
    location = const.LOCATION

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={'position': {'location': location}, 'product_id': 'product-1'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json()['informers'] == [
        {
            'text': 'Only product-1',
            'show_in_root': False,
            'category_group_ids': [],
            'product_ids': ['product-1'],
        },
    ]


# Проверка тайтлов
async def test_modes_product_titles(
        taxi_grocery_api, overlord_catalog, load_json,
):
    location = const.LOCATION

    product_id = 'product-1'

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['product']['title'] == 'product-1-title'
    assert data['product']['long_title'] == 'product-1-long-title'
    assert 'short_title' not in data['product']


async def test_modes_product_favorites(
        taxi_grocery_api, overlord_catalog, load_json, grocery_fav_goods,
):
    location = const.LOCATION

    product_id = 'product-1'
    grocery_fav_goods.add_favorite(
        yandex_uid=common.DEFAULT_UID, product_id=product_id,
    )

    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    json = {'position': {'location': location}, 'product_id': product_id}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'X-Yandex-UID': common.DEFAULT_UID},
    )
    assert response.status_code == 200
    assert response.json()['product']['is_favorite']


# Проверка поля 'catalog_paths' в ответе ручки
@pytest.mark.parametrize(
    'layout_id',
    [
        pytest.param(
            'layout-1', marks=experiments.create_modes_layouts_exp('layout-1'),
        ),
        pytest.param(
            'layout-2', marks=experiments.create_modes_layouts_exp('layout-2'),
        ),
    ],
)
@pytest.mark.parametrize('need_catalog_paths', [None, False, True])
async def test_catalog_paths(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        layout_id,
        need_catalog_paths,
):
    product_id = 'some-product-id'
    common.setup_catalog_for_paths_test(
        overlord_catalog, grocery_products, product_id,
    )

    headers = {'Accept-Language': 'en'}
    request_body = {
        'position': {'location': common.DEFAULT_LOCATION},
        'product_id': product_id,
    }
    if need_catalog_paths is not None:
        request_body['need_catalog_paths'] = need_catalog_paths

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product', headers=headers, json=request_body,
    )
    assert response.status_code == 200
    response_data = response.json()

    assert response_data['product']['id'] == product_id
    if need_catalog_paths is True:
        assert 'catalog_paths' in response_data['product']
        common.check_catalog_paths(
            response_data['product']['catalog_paths'], layout_id,
        )
    else:
        assert 'catalog_paths' not in response_data['product']


# Проверяем новые long_title
@pytest.mark.translations(
    pigeon_product_long_title={'external_id_1': {'en': 'pigeon_long_title'}},
    wms_items={'product-1_long_title': {'en': 'wms_long_title'}},
)
@pytest.mark.parametrize(
    'pigeon_enabled,long_title',
    [
        pytest.param(False, 'wms_long_title', id='wms'),
        pytest.param(True, 'pigeon_long_title', id='pigeon'),
    ],
)
async def test_modes_product_pigeon_long_titles(
        taxi_grocery_api,
        taxi_config,
        overlord_catalog,
        load_json,
        pigeon_enabled,
        long_title,
):
    taxi_config.set(
        GROCERY_LOCALIZATION_PIGEON_LONG_TITLE={
            'keyset': 'pigeon_product_long_title',
            'enabled': pigeon_enabled,
        },
    )
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, const.LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': const.LOCATION},
            'product_id': 'product-1',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json()['product']['long_title'] == long_title


# Проверяем, что новый amount склеивается
# по шаблону из танкера, в зависимости от amount_pack(=1, >1)
# В случае нецелого числа разделитель берется из танкера
@pytest.mark.translations(
    overlord_catalog={
        'amount_pack_key': {
            'en': '%(amount_pack)s x %(amount)s %(amount_unit)s',
        },
        'single_amount_pack_key': {'en': '%(amount)s %(amount_unit)s'},
    },
    wms_amount_units={'gram': {'en': 'g'}},
    grocery_localizations={'decimal_separator': {'ru': ',', 'en': '.'}},
)
@pytest.mark.parametrize(
    'amount_pack,amount,expected_amount',
    [
        (3, '100', '3 x 100 g'),
        (2, '40.5', '2 x 40{}5 g'),
        (1, '300', '300 g'),
        (None, '300', '300 g'),
    ],
)
@pytest.mark.parametrize(
    'locale,expected_separator', [('ru', ','), ('en', '.')],
)
async def test_modes_product_new_amount(
        taxi_grocery_api,
        overlord_catalog,
        load_json,
        amount_pack,
        amount,
        expected_amount,
        locale,
        expected_separator,
):

    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    products_data[0]['options']['amount'] = amount
    products_data[0]['options']['amount_units'] = 'г'
    products_data[0]['options']['amount_units_alias'] = 'gram'
    products_data[0]['options']['amount_pack'] = amount_pack

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        const.LOCATION,
        products_data=products_data,
    )

    json = {
        'position': {'location': const.LOCATION},
        'product_id': 'product-1',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json=json,
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    assert response.json()['product']['amount'] == expected_amount.format(
        expected_separator,
    )


# Проверяем что коды переработки протаскиваются на фронт
async def test_modes_product_recycling_codes(
        taxi_grocery_api, overlord_catalog, load_json,
):

    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    recycling_codes = ['some_code_1', 'some_code_2']
    products_data[0]['options']['recycling_codes'] = recycling_codes
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        const.LOCATION,
        products_data=products_data,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/product',
        json={
            'position': {'location': const.LOCATION},
            'product_id': 'product-1',
        },
        headers={'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert (
        response.json()['product']['options']['recycling_codes']
        == recycling_codes
    )
