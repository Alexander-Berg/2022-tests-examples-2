# pylint: disable=too-many-lines

from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from . import common
from . import const
from . import experiments


def _build_categories_in_diff_layouts(grocery_products, deep_link):
    layout_1 = grocery_products.add_layout(test_id='1')
    category_group_1 = layout_1.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1', deep_link=deep_link,
    )
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    layout_2 = grocery_products.add_layout(test_id='2')
    category_group_2 = layout_2.add_category_group(test_id='2')
    virtual_category_2 = category_group_2.add_virtual_category(
        test_id='2', deep_link=deep_link,
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )


def _build_categories_in_the_same_layout(grocery_products, deep_link):
    layout = grocery_products.add_layout(test_id='1')
    category_group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1', deep_link=deep_link,
    )
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )
    virtual_category_2 = category_group_1.add_virtual_category(
        test_id='2', deep_link=deep_link,
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )


# Ручка modes/category, сценарий перехода с главной страницы на вторую,
# где с категорией передается путь до нее (category_path).
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_modes_category_200_with_path(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        locale,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID

    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    headers = {}
    if locale:
        headers['Accept-Language'] = locale
        headers['User-Agent'] = common.DEFAULT_USER_AGENT

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json, headers=headers,
    )
    assert response.status_code == 200

    if not locale:
        locale = 'en'

    expected_response = load_json('modes_category_expected_response.json')[
        locale
    ]
    assert response.json() == expected_response


# Ручка modes/category, сценарий перехода по диплинку с id категоии,
# путь до категории (category_path) не передается.
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_category_200_without_path(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    expected_response = load_json('modes_category_expected_response.json')[
        'en'
    ]
    assert response.json() == expected_response


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.SHOW_SOLD_OUT_ENABLED
async def test_modes_category_sold_out(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        depot_id=depot_id,
        category_tree=load_json('sold_overlord_category_tree_response.json'),
        product_stocks=load_json('sold_overlord_products_stocks.json'),
    )
    common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    body = response.json()

    expected_items = [
        'virtual-category-1',
        'category-1-subcategory-1',
        'product-5',
        'product-3',
        'product-2',
        'product-6',
    ]

    # check mode items presence & order
    mode_items = body['modes'][0]['items']
    for i, mode_item in enumerate(mode_items):
        assert mode_item['id'] == expected_items[i]

    # check product items presence
    assert len(body['products']) == len(expected_items)
    for product in body['products']:
        assert product['id'] in expected_items


# Ручка modes/category, сценарий перехода по диплинку с id категоии,
# путь до категории (category_path) не передается.
# Проверяются возможные ошибки.
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'error_code,category_id',
    [
        pytest.param(
            'DEPOT_NOT_FOUND', 'virtual-category-1', id='DEPOT_NOT_FOUND',
        ),
        pytest.param(
            'LAYOUT_NOT_FOUND', 'virtual-category-1', id='LAYOUT_NOT_FOUND',
        ),
        pytest.param(
            'CATEGORY_NOT_FOUND',
            'virtual-category-non-exist',
            id='CATEGORY_NOT_FOUND',
        ),
    ],
)
async def test_modes_category_404_without_path(
        taxi_grocery_api,
        load_json,
        overlord_catalog,
        grocery_products,
        error_code,
        category_id,
):
    location = const.LOCATION
    if error_code != 'DEPOT_NOT_FOUND':
        common.prepare_overlord_catalog_json(
            load_json, overlord_catalog, location,
        )

    if error_code == 'LAYOUT_NOT_FOUND':
        common.build_basic_layout(grocery_products, '2')
    else:
        common.build_basic_layout(grocery_products)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': category_id,
        'offer_id': 'some-offer-id',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 404
    assert response.json()['code'] == error_code


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'build_structure',
    [
        pytest.param(_build_categories_in_diff_layouts, id='diff layouts'),
        pytest.param(_build_categories_in_the_same_layout, id='same layout'),
    ],
)
async def test_modes_category_by_deeplink(
        taxi_grocery_api,
        load_json,
        overlord_catalog,
        grocery_products,
        build_structure,
):
    location = const.LOCATION
    deep_link = 'test_deep_link'
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    build_structure(grocery_products, deep_link)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': deep_link,
        'offer_id': 'some-offer-id',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    result = response.json()
    assert result['modes'][0]['items'][0]['id'] == 'virtual-category-1'
    assert result['modes'][0]['items'][1]['id'] == 'category-1-subcategory-1'


# Ручка modes/category, новый способ проверки доступности
# подкатегорий через overlord-catalog
@pytest.mark.parametrize(
    'subcategory_available,response_items', [(True, 4), (False, 1)],
)
async def test_modes_category_new_subcategories_availability(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        load_json,
        subcategory_available,
        response_items,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1',
        available=subcategory_available,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )
    assert response.status_code == 200
    assert overlord_catalog.internal_categories_availability_times_called == 1
    assert len(response.json()['modes'][0]['items']) == response_items


@pytest.mark.config(
    GROCERY_API_LOG_CATALOG_RESPONSE_TO_YT=['/lavka/v1/api/v1/modes/category'],
)
async def test_modes_category_yt_log(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        testpoint,
        grocery_p13n,
        grocery_depots,
):
    """ user context, depot_id and products info should be
    logged to be sent to YT via logbrocker """

    location = const.LOCATION
    depot_id = const.DEPOT_ID
    legacy_depot_id = '123'

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id), depot_id=depot_id,
    )

    overlord_catalog.clear()
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)
    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    grocery_p13n.add_modifier(product_id='product-1', value='1.1')
    grocery_p13n.add_modifier(
        product_id='product-2',
        value='1',
        payment_type=p13n.PaymentType.CASHBACK_DISCOUNT,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    @testpoint('yt_grocery_catalog')
    def yt_grocery_catalog(grocery_catalog):
        del grocery_catalog['timestamp']
        assert grocery_catalog == {
            'catalog': {
                'items': [
                    {'id': 'virtual-category-1', 'type': 'category'},
                    {'id': 'category-1-subcategory-1', 'type': 'subcategory'},
                    {
                        'discount_pricing': {
                            'price': '1',
                            'price_template': '1 $SIGN$$CURRENCY$',
                        },
                        'id': 'product-1',
                        'pricing': {
                            'price': '2',
                            'price_template': '2 $SIGN$$CURRENCY$',
                        },
                        'quantity_limit': '5',
                        'type': 'good',
                    },
                    {
                        'discount_pricing': {'cashback': '1'},
                        'id': 'product-2',
                        'pricing': {
                            'price': '5',
                            'price_template': '5 $SIGN$$CURRENCY$',
                        },
                        'quantity_limit': '10',
                        'type': 'good',
                    },
                ],
            },
            'depot_id': '123',
            'handler_name': '/lavka/v1/api/v1/modes/category',
            'user_context': {
                'app_vars': 'app_name=android',
                'eats_user_id': 'some_eats_user_id',
                'locale': 'ru',
                'personal_email_id': 'some_personal_email_id',
                'personal_phone_id': 'some_personal_phone_id',
                'taxi_user_id': '123456',
                'yandex_uid': 'some_yandex_uid',
                'appmetrica_device_id': 'some_appmetrica_device_id',
            },
            'version': 1,
        }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={
            'X-YaTaxi-Session': 'taxi:123456',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
            'X-Yandex-UID': 'some_yandex_uid',
            'X-YaTaxi-User': (
                'personal_phone_id=some_personal_phone_id,'
                'personal_email_id=some_personal_email_id,'
                'eats_user_id=some_eats_user_id'
            ),
            'X-AppMetrica-DeviceId': 'some_appmetrica_device_id',
        },
    )
    assert response.status_code == 200

    assert yt_grocery_catalog.times_called == 1


# Проверяем что из мульти-экспа достается эксп с сетками и из него сетка
@pytest.mark.experiments3(
    name='grocery_api_layout_exps_names',
    consumers=['grocery-api/modes'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'exp_name': 'some-exp-name'},
        },
    ],
)
@pytest.mark.experiments3(
    name='some-exp-name',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_id': 'layout-2'},
        },
    ],
)
async def test_modes_category_layout_multi_exp(
        taxi_grocery_api, overlord_catalog, grocery_products, load_json,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    common.build_basic_layout(grocery_products, layout_test_id='2')

    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': 'virtual-category-1',
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )
    assert response.status_code == 200


# Если не находим эксп с сетками из мульти-экспа фолбэчимся на старый
@pytest.mark.experiments3(
    name='grocery_api_layout_exps_names',
    consumers=['grocery-api/modes'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'exp_name': 'some-exp-name'},
        },
    ],
)
@experiments.MODES_ROOT_LAYOUT_ENABLED
async def test_modes_category_layout_fallback_exp(
        taxi_grocery_api, overlord_catalog, grocery_products, load_json,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    common.build_basic_layout(grocery_products, layout_test_id='1')

    overlord_catalog.set_category_availability(
        category_id='category-1-subcategory-1', available=True,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': 'virtual-category-1',
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )
    assert response.status_code == 200


def all_items_ids(response):
    return [item['id'] for item in response.json()['modes'][0]['items']]


# проверяем, что появляется скидочная подкатегория, где лежат
# уникальные товары со скидкой
@pytest.mark.translations(
    virtual_catalog={
        'discounts_subcategory': {
            'en': 'discounts subcategory',
            'ru': 'скидочная подкатегория',
        },
    },
)
@pytest.mark.parametrize(
    'payment_type',
    [p13n.PaymentType.MONEY_DISCOUNT, p13n.PaymentType.CASHBACK_DISCOUNT],
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@experiments.FIRST_SUBCATEGORY_DISCOUNT
async def test_first_subcategory_is_discount(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        grocery_p13n,
        locale,
        payment_type,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    grocery_p13n.add_modifier(
        product_id='product-1', value='1.1', payment_type=payment_type,
    )

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    headers = {}
    if locale:
        headers['Accept-Language'] = locale

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json, headers=headers,
    )

    assert all_items_ids(response) == [
        'virtual-category-1',
        'discounts_subcategory',
        'product-1',
        'category-1-subcategory-1',
        'product-1',
        'product-2',
    ]
    discount = 'discounts subcategory'
    if locale == 'ru':
        discount = 'скидочная подкатегория'

    discounts_subcategory_title = None
    discounts_subcategory_type = None
    for item in response.json()['modes'][0]['items']:
        if item['id'] == 'discounts_subcategory':
            discounts_subcategory_title = item['title']
            discounts_subcategory_type = item['type']
    assert discount == discounts_subcategory_title
    assert discounts_subcategory_type == 'carousel'


@experiments.FIRST_SUBCATEGORY_DISCOUNT
async def test_discounts_carousel_disabled(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        grocery_p13n,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    layout = grocery_products.add_layout(test_id='1')

    category_group_1 = layout.add_category_group(test_id='1')

    virtual_category_1 = category_group_1.add_virtual_category(
        test_id='1',
        add_short_title=True,
        layout_meta='{"disable_discounts_carousel": true}',
    )
    virtual_category_1.add_subcategory(
        subcategory_id='category-1-subcategory-1',
    )

    virtual_category_2 = category_group_1.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-1',
    )
    virtual_category_2.add_subcategory(
        subcategory_id='category-2-subcategory-2',
    )

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    grocery_p13n.add_modifier(product_id='product-1', value='1.1')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )

    assert all_items_ids(response) == [
        'virtual-category-1',
        'category-1-subcategory-1',
        'product-1',
        'product-2',
    ]


# при наличии поля subcategories_as_carousel=true в мете категории
# и включенном эксперименте grocery_api_enable_carousel_subcategories
# подкатегории внутри данной категории имеют тип carousel.
# При наличии массива subcategories_as_carousel
# делаем карусельными подкаты содержащиеся в нем
@experiments.carousel_subcategories_enabled()
@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize(
    'layout_meta,expected_subcategory_types',
    [
        pytest.param(
            '{"subcategories_as_carousel": true}', ['carousel'] * 3, id='bool',
        ),
        pytest.param(
            '{"subcategories_as_carousel": ["category-1-subcategory-1"]}',
            ['carousel', 'subcategory', 'subcategory'],
            id='set',
        ),
    ],
)
async def test_modes_category_subcategory_as_carousel(
        taxi_grocery_api,
        load_json,
        overlord_catalog,
        grocery_products,
        layout_meta,
        expected_subcategory_types,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id='1', layout_meta=layout_meta,
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')
    virtual_category.add_subcategory(subcategory_id='category-2-subcategory-1')
    virtual_category.add_subcategory(subcategory_id='category-2-subcategory-2')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': virtual_category.virtual_category_id,
        'offer_id': 'some-offer-id',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    subcategory_types = [
        item['type']
        for item in response.json()['modes'][0]['items']
        if item['id'].startswith('category')
    ]
    assert len(subcategory_types) == 3
    assert subcategory_types == expected_subcategory_types


# Подкатегории в специальных категориях трансформируются в
# карусели по эксперименту grocery_api_enable_carousel_subcategories
# и мете с ключом subcategories_as_carousel
@experiments.carousel_subcategories_enabled()
@experiments.CASHBACK_EXPERIMENT
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PROMO_CAAS_EXPERIMENT
async def test_modes_special_category_subcategory_as_carousel(
        taxi_grocery_api,
        load_json,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id='1',
        special_category='cashback-caas',
        layout_meta='{"subcategories_as_carousel": true}',
    )

    grocery_caas_promo.add_subcategory(
        subcategory_id='subcategory-1',
        title_tanker_key='subcategory-1-title',
        is_cashback=True,
    )
    grocery_caas_promo.add_products(
        product_ids=['product-1', 'product-2'], is_cashback=True,
    )
    grocery_caas_promo.add_subcategory(
        subcategory_id='subcategory-2',
        title_tanker_key='subcategory-2-title',
        is_cashback=True,
    )
    grocery_caas_promo.add_product(product_id='product-1', is_cashback=True)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': virtual_category.virtual_category_id,
        'offer_id': 'some-offer-id',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    subcategory_types = [
        item['type']
        for item in response.json()['modes'][0]['items']
        if item['id'].startswith('subcategory')
    ]
    assert len(subcategory_types) == 2
    assert set(subcategory_types) == {'carousel'}


# Подкатегории становятся каруселями только если
# количество товаров в них превышает min_items_count из
# эксперимента grocery_api_enable_carousel_subcategories
@experiments.carousel_subcategories_enabled(min_items_count=2)
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.PROMO_CAAS_EXPERIMENT
async def test_modes_subcategory_as_carousel_min_items(
        taxi_grocery_api, load_json, overlord_catalog, grocery_products,
):
    # category-1-subcategory-1 - 2 товара
    # category-2-subcategory-1 - 1 товар
    # category-2-subcategory-2 - 1 товар
    # только category-1-subcategory-1 будет каруселью
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = grocery_products.add_layout(test_id='1')
    category_group = layout.add_category_group(test_id='1')
    virtual_category = category_group.add_virtual_category(
        test_id='1', layout_meta='{"subcategories_as_carousel": true}',
    )
    virtual_category.add_subcategory(subcategory_id='category-1-subcategory-1')
    virtual_category.add_subcategory(subcategory_id='category-2-subcategory-1')
    virtual_category.add_subcategory(subcategory_id='category-2-subcategory-2')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_id': virtual_category.virtual_category_id,
        'offer_id': 'some-offer-id',
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json=json,
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    subcategory_types = [
        (item['id'], item['type'])
        for item in response.json()['modes'][0]['items']
        if item['id'].startswith('category')
    ]
    assert subcategory_types == [
        ('category-1-subcategory-1', 'carousel'),
        ('category-2-subcategory-1', 'subcategory'),
        ('category-2-subcategory-2', 'subcategory'),
    ]


# проверяем, что если все товары в категории со скидкой,
# то мы не рисуем скидочную подкатегорию
@experiments.FIRST_SUBCATEGORY_DISCOUNT
async def test_no_discount_subcategory(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        grocery_p13n,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)
    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    grocery_p13n.add_modifier(product_id='product-1', value='1.1')
    grocery_p13n.add_modifier(product_id='product-2', value='1.1')

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': offer_id,
    }

    headers = {}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json, headers=headers,
    )

    assert all_items_ids(response) == [
        'virtual-category-1',
        'category-1-subcategory-1',
        'product-1',
        'product-2',
    ]


# если товаров больше или равно чем заданно в конфиге
# GROCERY_API_STOCKS_DISCOUNTS_ASYNC_POLICY начинаем ходить за остатками
# затем за скидками, последовательно. Запрос в скидки фильтруется по остаткам.
@pytest.mark.parametrize(
    'discount_request_products',
    [
        pytest.param(
            ['product-1', 'product-2', 'product-3'],
            marks=pytest.mark.config(
                GROCERY_API_STOCKS_DISCOUNTS_ASYNC_POLICY={
                    '__default__': 1000,
                    '/lavka/v1/api/v1/modes/category': 4,
                },
            ),
            id='async stocks and discounts',
        ),
        pytest.param(
            ['product-1', 'product-2'],
            marks=pytest.mark.config(
                GROCERY_API_STOCKS_DISCOUNTS_ASYNC_POLICY={
                    '__default__': 1000,
                    '/lavka/v1/api/v1/modes/category': 1,
                },
            ),
            id='consistently stocks and then discounts',
        ),
    ],
)
async def test_modes_category_async_policy(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        mockserver,
        load_json,
        discount_request_products,
):
    location = const.LOCATION
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)
    layout = common.build_basic_layout(grocery_products)

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def mock_p13n_discount_modifiers(request):
        assert (
            sorted([item['product_id'] for item in request.json['items']])
            == discount_request_products
        )
        return {'modifiers': []}

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
        'offer_id': 'some-offer-id',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json,
    )
    assert response.status_code == 200
    assert mock_p13n_discount_modifiers.times_called > 0


# Ручка modes/category возвращает только принадлежащие ей информеры,
# а также информеры всех подкатегорий.
@experiments.GROCERY_API_DIFFERENT_PLACES_INFORMER
async def test_modes_category_informers(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json={
            'modes': ['grocery'],
            'position': {'location': location},
            'category_path': {
                'layout_id': layout.layout_id,
                'group_id': layout.group_ids_ordered[0],
            },
            'category_id': 'virtual-category-1',
            'offer_id': offer_id,
        },
        headers={},
    )
    assert response.status_code == 200

    assert response.json()['informers'] == [
        {
            'category_ids': ['virtual-category-1'],
            'show_in_root': False,
            'text': 'Only category',
        },
        {
            'category_ids': ['category-1-subcategory-1'],
            'show_in_root': False,
            'text': 'For subcategory',
        },
    ]


# Ручка modes/category возвращает сторис с продуктом
@experiments.GROCERY_API_INFORMER_STORIES
async def test_modes_category_stories_with_product(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json={
            'modes': ['grocery'],
            'position': {'location': location},
            'category_path': {
                'layout_id': layout.layout_id,
                'group_id': layout.group_ids_ordered[0],
            },
            'category_id': 'virtual-category-1',
            'offer_id': offer_id,
        },
        headers={},
    )
    assert response.status_code == 200
    assert 'informers' in response.json()


# Ручка modes/category возвращает информеры, и если они для товаров,
# то товары есть в остатках
@experiments.GROCERY_API_PRODUCT_INFORMER
async def test_modes_category_informers_check_by_stocks(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(offer_id, now, depot_id, location)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category',
        json={
            'modes': ['grocery'],
            'position': {'location': location},
            'category_path': {
                'layout_id': layout.layout_id,
                'group_id': layout.group_ids_ordered[0],
            },
            'category_id': 'virtual-category-1',
            'offer_id': offer_id,
        },
        headers={},
    )
    assert response.status_code == 200

    assert response.json()['informers'] == [
        {
            'category_ids': ['virtual-category-1'],
            'hide_if_product_is_missing': ['product-1', 'product-3'],
            'show_in_root': False,
            'text': 'Only root',
        },
    ]


@pytest.mark.config(GROCERY_API_GET_DISCOUNTS_LIMIT=1)
async def test_discounts_by_parts(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_products,
        load_json,
        now,
        grocery_p13n,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, depot_id=depot_id,
    )
    layout = common.build_basic_layout(grocery_products)

    json = {
        'modes': ['grocery'],
        'position': {'location': location},
        'category_path': {
            'layout_id': layout.layout_id,
            'group_id': layout.group_ids_ordered[0],
        },
        'category_id': 'virtual-category-1',
    }

    headers = {}

    await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/category', json=json, headers=headers,
    )

    assert grocery_p13n.discount_modifiers_times_called == 3
