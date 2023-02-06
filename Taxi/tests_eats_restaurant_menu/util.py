import typing

import pytest

MODIFY_MENU_HANDLER = '/api/v1/menu/retrieve/modify'
MODIFY_SEARCH_HANDLER = '/api/v1/menu/goods/search/modify'


def get_sort_exp3_with_value(sort_type: str):
    return pytest.mark.experiments3(
        name='eats_restaurant_menu_sort',
        consumers=['eats_restaurant_menu'],
        is_config=True,
        default_value={'sort_type': sort_type},
    )


def build_item(
        item_id: int,
        name: str = 'item',
        description: typing.Optional[str] = None,
        available: bool = True,
        in_stock: typing.Optional[int] = None,
        price: float = 10,
        promo_price: typing.Optional[float] = None,
        promo_types: list = None,
        options_groups: list = None,
        picture: dict = None,
        weight: typing.Optional[str] = None,
        adult: bool = False,
        for_search: bool = False,
        measure: typing.Optional[dict] = None,
        shipping_type: typing.Optional[str] = None,
        public_id: typing.Optional[str] = None,
        categories_ids: list = None,
        vat: str = None,
        nutrients: typing.Optional[dict] = None,
) -> dict:
    if not promo_types:
        promo_types = []
    if not options_groups:
        options_groups = []
    options_groups_key = 'optionGroups' if for_search else 'optionsGroups'
    result = {
        'id': item_id,
        'name': name,
        'available': available,
        'price': int(price),
        'decimalPrice': str(price),
        options_groups_key: options_groups,
        'promoTypes': promo_types,
        'adult': adult,
        'inStock': in_stock,
    }
    if description is not None:
        result['description'] = description
    if promo_price:
        result['promoPrice'] = round(promo_price)
        result['decimalPromoPrice'] = str(promo_price)
    if picture:
        result['picture'] = picture
    if weight:
        result['weight'] = weight
    if measure is not None:
        result['measure'] = measure
    if shipping_type is not None:
        result['shippingType'] = shipping_type
    if public_id is not None:
        result['publicId'] = public_id
    if categories_ids:
        result['categories_ids'] = categories_ids
    if vat:
        result['vat'] = vat
    if nutrients:
        result['nutrients'] = nutrients
    return result


def discounts_applicator_enabled():
    return pytest.mark.experiments3(
        name='eats_discounts_enabled',
        consumers=['eats-discounts-applicator/enabled_discounts'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def promo_category_enabled():
    return pytest.mark.experiments3(
        name='add_smart_promo_category',
        consumers=['eats_restaurant_menu'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def discounts_applicator_menu():
    return pytest.mark.experiments3(
        name='eats_discounts_applicator_in_eats_restaurant_menu',
        consumers=['eats_restaurant_menu'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def eats_client_menu_use_erms(enabled: bool = False, dry_run: bool = False):
    return pytest.mark.experiments3(
        name='eats_client_menu_use_erms',
        consumers=['eats_restaurant_menu'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled, 'dry_run': dry_run},
            },
        ],
    )


EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT = [
    {
        'id': 1,
        'slug': 'test_slug',
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [37.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'restaurant',
        'allowed_couriers_types': ['pedestrian'],
        'working_intervals': [],
    },
]


def dynamic_prices(default_percent: int, items_percents: dict = None):
    items = {'__default__': default_percent}
    if items_percents:
        items.update(items_percents)
    return pytest.mark.experiments3(
        name='eats_dynamic_price_by_user',
        consumers=['eats_smart_prices/user'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': True,
                    'calculate_method': 'by_place_percent',
                    'modification_percent': items,
                },
            },
        ],
    )


def build_category(
        category_id: typing.Optional[int],
        name: str = 'cat',
        available: bool = True,
        gallery: typing.Optional[typing.List] = None,
        items: typing.Optional[typing.List] = None,
        schedule: typing.Optional[str] = None,
        dynamic_id: typing.Optional[str] = None,
):
    if not gallery:
        gallery = []

    if not items:
        items = []

    result = {
        'name': name,
        'available': available,
        'items': items,
        'gallery': gallery,
        'categories': [],
    }
    if schedule:
        result['schedule'] = schedule
    if category_id:
        result['id'] = category_id
    if dynamic_id:
        result['dynamicId'] = dynamic_id
    return result


def compare_order(
        expected_items_order: typing.Dict[
            typing.Optional[int], typing.List[int],
        ],
        response_categories: dict,
):
    for category in response_categories:
        for item, expected_item in zip(
                category['items'], expected_items_order[category.get('id')],
        ):
            assert item['id'] == expected_item
