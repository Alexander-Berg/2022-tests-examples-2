from typing import Optional

import pytest

from tests_eats_products.helpers import request_checker

PLACE_ID = 1
BRAND_ID = 1
PLACE_SLUG = 'slug'
BRAND_SLUG = 'brand_slug'

REPEAT_CATEGORY_ID = 44004
DISCOUNT_CATEGORY_ID = 44008
POPULAR_CATEGORY_ID = 44012
CASHBACK_CATEGORY_ID = 1_000_000
REPEAT_THIS_BRAND_ID = 1_000_001
REPEAT_OTHER_BRANDS_ID = 1_000_002


class Handlers:
    # core handlers:
    CORE_BRANDS = '/eats-core-retail/v1/brands/retrieve'
    CORE_RETAIL_MAPPING = (
        '/eats-core-retail/v1/nomenclature/id-mapping/retrieve'
    )
    CORE_RETAIL_BRAND_PLACES = '/eats-core-retail/v1/brand/places/retrieve'

    # eats-discounts handlers:
    FETCH_DISCOUNTS = '/eats-discounts/v2/fetch-discounts'
    MATCH_DISCOUNTS = '/eats-discounts/v2/match-discounts'

    # eats-catalog handlers:
    CATALOG_FOR_LAYOUT = '/eats-catalog/internal/v1/catalog-for-layout'
    CATALOG_INTERNAL_V1_PLACES = '/catalog/internal/v1/places'

    # eats-nomenclature handlers:
    NOMENCLATURE = '/eats-nomenclature/v1/nomenclature'
    NOMENCLATURE_ASSORTMENT = '/eats-nomenclature/v2/place/assortment/details'
    NOMENCLATURE_PRODUCTS = '/eats-nomenclature/v1/products'
    NOMENCLATURE_PRODUCT_CATEGORIES = (
        '/eats-nomenclature/v1/product/categories'
    )
    NOMENCLATURE_PRODUCTS_INFO = '/eats-nomenclature/v1/products/info'
    NOMENCLATURE_PLACE_PRODUCTS_INFO = (
        '/eats-nomenclature/v1/place/products/info'
    )
    NOMENCLATURE_PLACE_CATEGORIES_GET_PARENT = (
        '/eats-nomenclature/v1/place/categories/get_parent'
    )
    NOMENCLATURE_PLACE_CATEGORIES_GET_CHILDREN = (
        '/eats-nomenclature/v1/place/categories/get_children'
    )
    NOMENCLATURE_PLACES_CATEGORIES = '/eats-nomenclature/v1/places/categories'
    NOMENCLATURE_PUBLIC_ID_BY_SKU_ID = (
        '/eats-nomenclature/v1/place/products/id-by-sku-id'
    )
    NOMENCLATURE_CATEGORY_PRODUCTS_FILTERED = (
        '/eats-nomenclature/v1/place/category_products/filtered'
    )
    NOMENCLATURE_INFO_BY_SKU_ID = (
        '/eats-nomenclature/v1/places/products/info-by-sku-id'
    )

    RETAIL_SEO_GENERALIZED_INFO = 'eats-retail-seo/v1/product/generalized-info'

    # eats-products handlers:
    ASSORTMENT = '/api/v2/place/assortment/details'
    EDADEAL_PLACES = '/api/v1/edadeal/places'
    FOR_SEARCH_CATEGORIES = '/api/v1/for-search/place/dynamic_categories'
    FOR_SEARCH_CATEGORIES_V2 = (
        '/internal/v2/for-search/place/dynamic_categories'
    )
    GET_CATEGORIES = '/api/v2/menu/goods/get-categories'
    MENU_GET_ITEMS = '/api/v2/menu/get-items'
    MENU_GOODS = '/api/v2/menu/goods'
    MENU_PRODUCT = '/api/v2/menu/product'
    CROSS_BRAND_PRODUCTS = '/api/v1/product/cross-brand-products'

    CROSS_BRAND_HISTORY_PLACES = '/api/v1/cross-brand-history/places'
    PUBLIC_ID_BY_ORIGIN_ID = '/internal/v2/products/public_id_by_origin_id'
    CROSS_BRAND_HISTORY_PRODUCTS = '/api/v1/cross-brand-history/products'

    # eats-upsell handlers:
    UPSELL_RECOMMENDATIONS = (
        '/eats-upsell/internal/eats-upsell/retail/v1/menu/recommendations'
    )

    # eats-communications
    SCREEN_COMMUNICATIONS = (
        '/eats-communications/internal/v1/screen/communications'
    )
    CATEGORIES_COMMUNICATIONS = (
        '/eats-communications/internal/v1/categories/communications'
    )

    # eats-retail-categories
    BRAND_ORDERS_HISTORY = (
        '/eats-retail-categories/v1/orders-history/products/brand'
    )

    # eats-retail-categories
    CROSS_BRAND_ORDERS_HISTORY = (
        '/eats-retail-categories/v1/orders-history/products/cross-brand'
    )

    # eats-catalog-storage
    PLACES_BY_PARAMS = (
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/'
        'places-by-params'
    )


EATS_CATALOG_STORAGE = (
    '/eats-catalog-storage/internal/eats-catalog-storage'
    '/v1/places/retrieve-by-ids'
)

DEFAULT_EATS_CATALOG_RESPONSE = {
    'places': [
        {
            'id': 1,
            'revision_id': 100,
            'updated_at': '2020-03-02T20:47:44.338Z',
            'address': {'city': 'Казань', 'short': 'Тихорецкая 28'},
            'brand': {
                'id': 1,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'region': {
                'id': 1,
                'geobase_ids': [],
                'time_zone': 'Europe/Moscow',
            },
            'business': 'shop',
            'country': {
                'name': 'Russia',
                'code': 'RU',
                'currency': {'code': 'RUB', 'sign': '₽'},
                'id': 35,
            },
        },
    ],
    'not_found_place_ids': [],
}


EATS_PRODUCT_DEFAULT_SETTINGS = {
    'ordershistory_days': 60,
    'ordershistory_orders': 10,
    'max_products': 100,
    'user_lifetime_sec': 600,
    'discount_promo': {'enabled': True},
}


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

EATS_PRODUCTS_BADGES = {
    'discount_badges': [
        {
            'text': {'light': '#100000', 'dark': '#100001'},
            'background': {'light': '#100002', 'dark': '#100003'},
        },
    ],
    'promo_badges': [
        {
            'text': {'light': '#000001', 'dark': '#000002'},
            'background': {'light': '#000003', 'dark': '#000004'},
        },
    ],
}

PRODUCTS_HANDLER_SETTINGS = {
    'use_fallback_to_generalized_info_product_not_found': True,
}
PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS = pytest.mark.parametrize(
    'use_fallback_to_generalized_info_not_found',
    [
        pytest.param(False, id='use 404 if product not found'),
        pytest.param(
            True,
            id='use /v1/product/generalized-info if product not found',
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS=(
                        PRODUCTS_HANDLER_SETTINGS
                    ),
                ),
            ),
        ),
    ],
)

PARAMETRIZE_CASHBACK_CATEGORY_HANDLERS_VERSION = pytest.mark.parametrize(
    'cashback_handles_version',
    [
        pytest.param('v1', id='use /assortment/details for product info'),
        pytest.param(
            'v2',
            id='use /products/info for product info',
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                        {'get_cashback_category_version': 'v2'}
                    ),
                ),
            ),
        ),
    ],
)


PARAMETRIZE_REPEAT_CATEGORY_HANDLERS_VERSION = pytest.mark.parametrize(
    'handlers_version',
    [
        pytest.param('v1', id='v1'),
        pytest.param(
            'v2',
            id='v2',
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                        {'repeat_category_handlers_version': 'v2'}
                    ),
                ),
            ),
        ),
    ],
)

PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION = pytest.mark.parametrize(
    'handlers_version',
    [
        pytest.param('v1', id='get_categories_products_info v1'),
        pytest.param(
            'v2',
            id='get_categories_products_info v2',
            marks=(
                pytest.mark.config(
                    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                        {'get_categories_products_info_version': 'v2'}
                    ),
                ),
            ),
        ),
    ],
)

PARAMETRIZE_WEIGHT_DATA_ROUNDING = pytest.mark.parametrize(
    'should_round_prices',
    [
        pytest.param(True, id='no rounding config'),
        pytest.param(
            False,
            id='default rounding config',
            marks=pytest.mark.config(
                EATS_NOMENCLATURE_PRICE_ROUNDING={
                    'unknown_brand': {
                        'should_include_pennies_in_price': False,
                    },
                    '__default__': {'should_include_pennies_in_price': True},
                },
            ),
        ),
        pytest.param(
            True,
            id='round by brand',
            marks=pytest.mark.config(
                EATS_NOMENCLATURE_PRICE_ROUNDING={
                    str(BRAND_ID): {'should_include_pennies_in_price': False},
                    '__default__': {'should_include_pennies_in_price': True},
                },
            ),
        ),
    ],
)


PARAMETRIZE_CATEGORY_PRODUCTS_VERSION = pytest.mark.parametrize(
    'category_products_version',
    [
        pytest.param(
            'v1',
            id='v1',
            marks=pytest.mark.config(
                EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                    {'menu_goods_category_products_version': 'v1'}
                ),
            ),
        ),
        pytest.param(
            'v2',
            id='v2',
            marks=pytest.mark.config(
                EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
                    {'menu_goods_category_products_version': 'v2'}
                ),
            ),
        ),
    ],
)

PARAMETRIZE_BRAND_PLACES_SOURCE = pytest.mark.parametrize(
    'use_catalog_storage',
    [
        pytest.param(False, id='core_default'),
        pytest.param(
            False,
            id='core',
            marks=pytest.mark.config(
                EATS_PRODUCTS_CORE_REQUEST_SETTINGS=(
                    {'use_catalog_storage_for_retrieve_places': False}
                ),
            ),
        ),
        pytest.param(
            True,
            id='catalog_storage',
            marks=pytest.mark.config(
                EATS_PRODUCTS_CORE_REQUEST_SETTINGS=(
                    {'use_catalog_storage_for_retrieve_places': True}
                ),
            ),
        ),
    ],
)

REQUEST_WITH_PLACE_AND_PRODUCT_IDS = (
    request_checker.RequestChecker()
    .add(request_checker.PlaceChecker())
    .add(request_checker.ProductIdsChecker())
)

REQUEST_WITH_PLACE_AND_ORIGIN_IDS = (
    request_checker.RequestChecker()
    .add(request_checker.PlaceChecker())
    .add(request_checker.OriginIdsInProductsChecker())
)

REQUEST_WITH_PLACE_AND_CATEGORY_IDS = (
    request_checker.RequestChecker()
    .add(request_checker.PlaceChecker())
    .add(request_checker.CategoryIdsChecker())
)


def dynamic_categories_config(
        repeat_enabled=False,
        discount_enabled=False,
        popular_enabled=False,
        cashback_enabled=False,
        repeat_this_brand_enabled=False,
        repeat_other_brands_enabled=False,
):
    return {
        'popular': {
            'enabled': popular_enabled,
            'id': POPULAR_CATEGORY_ID,
            'name': 'Популярное',
        },
        'discount': {
            'enabled': discount_enabled,
            'id': DISCOUNT_CATEGORY_ID,
            'name': 'Скидки',
        },
        'repeat': {
            'enabled': repeat_enabled,
            'id': REPEAT_CATEGORY_ID,
            'name': 'Вы уже заказывали',
        },
        'cashback': {
            'enabled': cashback_enabled,
            'id': CASHBACK_CATEGORY_ID,
            'name': 'Товары с кeшбеком',
        },
        'repeat_this_brand': {
            'enabled': repeat_this_brand_enabled,
            'id': REPEAT_THIS_BRAND_ID,
            'name': 'В этом магазине',
        },
        'repeat_other_brands': {
            'enabled': repeat_other_brands_enabled,
            'id': REPEAT_OTHER_BRANDS_ID,
            'name': 'В других магазинах',
        },
    }


async def get_goods_response(taxi_eats_products, params: dict, headers=None):
    body = {**params, 'slug': 'slug'}
    return await taxi_eats_products.post(
        Handlers.MENU_GOODS, json=body, headers=headers or PRODUCTS_HEADERS,
    )


def build_nomenclature_product(
        product_id,
        description,
        price=100,
        old_price=None,
        is_available=True,
        is_catch_weight=True,
        measure=None,
        in_stock: Optional[int] = None,
        shipping_type='delivery',
        name='item_4',
):
    product = {
        'adult': False,
        'description': description,
        'images': [],
        'is_available': is_available,
        'name': name,
        'old_price': old_price,
        'price': price,
        'product_id': product_id,
        'shipping_type': shipping_type,
        'sort_order': 0,
        'vat': 20,
        'is_catch_weight': is_catch_weight,
        'measure': measure,
    }
    if in_stock:
        product['in_stock'] = in_stock
    return product


def build_v1_nomenclature_product(
        product_id,
        price=100,
        old_price=None,
        id_=None,
        is_available=True,
        is_catch_weight=True,
        measure=None,
        name='Яблоки',
        description='Описание Яблоки',
        in_stock=None,
):
    product = {
        'adult': False,
        'description': {'general': description},
        'id': id_ or 'item_id_3',
        'images': [],
        'is_available': is_available,
        'is_catch_weight': is_catch_weight,
        'is_choosable': True,
        'measure': measure,
        'name': name,
        'old_price': old_price,
        'price': price,
        'public_id': product_id,
        'shipping_type': 'pickup',
        'sort_order': 3,
    }
    if in_stock:
        product['in_stock'] = in_stock
    return product


def build_v1_products_static_info(
        id_,
        carbohydrates=None,
        proteins=None,
        fats=None,
        calories_value=None,
        calories_unit=None,
        description_general='Описание Яблоки',
        is_catch_weight=True,
        measure=None,
        sku_id=None,
        name=None,
        images=None,
        shipping_type='all',
        expiration_info_value=None,
        expiration_info_unit=None,
        composition=None,
        storage_requirements=None,
        vendor_name=None,
        vendor_country=None,
        is_alcohol=False,
        brand=None,
        alco_grape_cultivar=None,
        alco_flavour=None,
        alco_aroma=None,
        alco_pairing=None,
):
    calories = None
    if calories_value and calories_unit:
        calories = {'value': calories_value, 'unit': calories_unit}

    expiration_info = None
    if expiration_info_value and expiration_info_unit:
        expiration_info = {
            'value': expiration_info_value,
            'unit': expiration_info_unit,
        }

    if images is None:
        images = images or [
            {
                'url': 'https://avatars.mdst.yandex.net/get-eda/69745/orig',
                'sort_order': 0,
            },
        ]

    product = {
        'id': id_,
        'origin_id': 'origin_id_101',
        'place_brand_id': 'place_brand_id_1',
        'name': (
            name
            if name is not None
            else 'Масло сливочное Из Вологды Традиционное 82,5%'
        ),
        'measure': measure,
        'description': {'general': description_general},
        'is_choosable': True,
        'is_catch_weight': is_catch_weight,
        'adult': False,
        'shipping_type': shipping_type,
        'barcodes': [],
        'images': images,
        'vendor_name': vendor_name,
        'vendor_country': vendor_country,
        'is_sku': False,
        'carbohydrates': carbohydrates,
        'proteins': proteins,
        'fats': fats,
        'calories': calories,
        'storage_requirements': storage_requirements,
        'expiration_info': expiration_info,
        'composition': composition,
        'sku_id': sku_id,
        'is_alcohol': is_alcohol,
        'brand': brand,
        'alco_grape_cultivar': alco_grape_cultivar,
        'alco_flavour': alco_flavour,
        'alco_aroma': alco_aroma,
        'alco_pairing': alco_pairing,
    }

    return product


def build_v1_products_dynamic_info(
        id_,
        price,
        is_available,
        old_price,
        origin_id,
        parent_category_ids,
        in_stock,
):
    return {
        'id': id_,
        'origin_id': origin_id,
        'parent_category_ids': parent_category_ids,
        'vendor_code': '1',
        'location': 'location',
        'price': price,
        'old_price': old_price,
        'vat': 0,
        'is_available': is_available,
        'in_stock': in_stock,
    }


def build_filtered_product(
        public_id,
        name,
        price,
        is_catch_weight,
        adult,
        sort_order,
        images,
        description,
        shipping_type,
        in_stock,
        old_price,
        measure,
):
    result = {
        'id': public_id,
        'name': name,
        'price': price,
        'is_catch_weight': is_catch_weight,
        'adult': adult,
        'sort_order': sort_order,
        'images': images,
        'description': description,
        'shipping_type': shipping_type,
        'in_stock': in_stock,
        'old_price': old_price,
    }

    if measure is not None:
        result['measure'] = measure
    return result


def build_v1_categories_get_parent(
        id_, name, parent_id, sort_order, type_, tags,
):
    return {
        'id': id_,
        'parent_id': parent_id,
        'child_ids': [],
        'name': name,
        'sort_order': sort_order,
        'type': type_,
        'images': [],
        'products': [],
        'tags': tags,
    }


def build_v1_product_category(public_id, name, parent_public_id):
    return {
        'public_id': public_id,
        'name': name,
        'public_parent_id': parent_public_id,
    }


def make_filter_for_response(
        query: str,
        name: str,
        values: Optional[list] = None,
        filter_type: str = 'multiselect',
        image: Optional[str] = None,
        is_applied: bool = False,
):
    result = {'is_applied': is_applied, 'query': query, 'type': filter_type}

    more_items_count = 0
    if values is not None:
        result['values'] = values
        filtered_values = filter(lambda item: 'top_index' in item, values)
        sorted_values = sorted(
            filtered_values, key=lambda item: item['top_index'],
        )
        top_values = [value for value in sorted_values]
        if top_values:
            result['top_values'] = top_values
            more_items_count = len(values) - len(top_values)

    if image is not None:
        result['icon'] = {'light': image, 'dark': image}

    result['ui_strings'] = {
        'all': 'Все',
        'done': 'Готово',
        'name': name,
        'popular': 'Популярное',
        'reset': 'Сбросить',
        'show': 'Показать',
        'show_all': f'Еще {more_items_count}',
    }
    return result


def matching_discounts_experiments(enabled, value):
    return pytest.mark.experiments3(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {'enabled': enabled, 'value': value},
            },
        ],
        consumers=['eats-discounts-applicator/users_experiments'],
        name=value,
    )


def compare_badges(resp_item, expected):
    assert resp_item['promoTypes']

    badge_color = resp_item['promoTypes'][0]['badgeColor']
    assert badge_color == expected['background']

    text_color = resp_item['promoTypes'][0]['textColor']
    assert text_color == expected['text']


def create_expected_badges(badges_settings):
    light = 'light'
    dark = 'dark'

    return {
        'background': [
            {'theme': light, 'value': badges_settings[0]['background'][light]},
            {'theme': dark, 'value': badges_settings[0]['background'][dark]},
        ],
        'text': [
            {'theme': light, 'value': badges_settings[0]['text'][light]},
            {'theme': dark, 'value': badges_settings[0]['text'][dark]},
        ],
    }


def make_communications_story(story_id):
    black = '#FFFFFF'
    white = '#FFFFFF'
    story = {
        'offer': {
            'shortcut_id': story_id,
            'title': {'color': black, 'content': 'some_title'},
            'subtitle': {'color': black, 'content': 'some_subtitle'},
            'backgrounds': [
                {'type': 'color', 'content': white},
                {'type': 'video', 'content': 'mp4'},
            ],
        },
        'pages': [
            {
                'duration': 2,
                'autonext': True,
                'title': {'color': black, 'content': 'some_page_title'},
                'text': {'color': black, 'content': 'some_text'},
                'backgrounds': [{'type': 'image', 'content': 'image_url'}],
                'widgets': {
                    'close_button': {'color': black},
                    'pager': {'color_on': black, 'color_off': white},
                    'link': {
                        'text': 'link_text',
                        'text_color': black,
                        'action': {
                            'type': 'deeplink',
                            'payload': {
                                'content': 'url',
                                'need_authorization': False,
                            },
                        },
                    },
                },
            },
            {
                'duration': 3,
                'autonext': False,
                'title': {'color': black, 'content': 'some_page_title'},
                'text': {'color': black, 'content': 'some_text'},
                'backgrounds': [
                    {'type': 'image', 'content': 'image_url'},
                    {'type': 'animation', 'content': 'gif'},
                ],
                'widgets': {
                    'close_button': {'color': black},
                    'action_buttons': [
                        {
                            'color': black,
                            'text': 'action_text',
                            'text_color': white,
                            'deeplink': 'link',
                        },
                        {
                            'color': white,
                            'text': 'action_text2',
                            'text_color': black,
                            'deeplink': 'link2',
                        },
                    ],
                },
            },
        ],
    }
    return story


def make_discounts_filter_settings(
        id_='discounts_filter_id',
        name_key='discounts_filter_name_key',
        position=0,
        icon=None,
):
    return {
        'id': id_,
        'name_key': name_key,
        'position': position,
        'icon': icon,
    }


def make_text_image_informer(informer_id):
    return {
        'id': informer_id,
        'payload': {
            'text': {
                'value': 'some_text',
                'color': {'light': '#0000FF', 'dark': '#FF0000'},
            },
            'image': {'light': 'light_image', 'dark': 'dark_image'},
            'background': {
                'light': {
                    'type': 'image',
                    'content': 'light_background_image',
                },
                'dark': {'type': 'color', 'content': '#6D131C'},
            },
            'type': 'text_with_image',
        },
        'has_close_button': True,
        'url': 'http://yandex.ru',
        'deeplink': 'http://yandex.ru/mobile',
    }


def make_background_informer(informer_id):
    return {
        'id': informer_id,
        'payload': {
            'background': {
                'light': {
                    'type': 'image',
                    'content': 'light_background_image',
                },
                'dark': {'type': 'color', 'content': '#FF00FF'},
            },
            'text': {
                'value': 'some_text',
                'color': {'light': '#000FFF', 'dark': '#FFF000'},
            },
            'type': 'background',
        },
        'has_close_button': True,
        'url': 'http://yandex.ru',
        'deeplink': 'http://yandex.ru/mobile',
    }
