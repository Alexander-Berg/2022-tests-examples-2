import typing

import pytest

ALWAYS_MATCH = {'predicate': {'type': 'true'}, 'enabled': True}


def repeat_category(version='v1', category_name_override=None):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_repeat_category',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {
                    'version': version,
                    'category_name_override': category_name_override,
                },
                'predicate': {'type': 'true'},
            },
        ],
    )


def discount_category(enabled=True, min_products=1, minimal_stock=None):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_discount_category',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {
                    'enabled': enabled,
                    'minimal_products': min_products,
                    'minimal_stock': minimal_stock,
                },
                'predicate': {'type': 'true'},
            },
        ],
    )


def popular_category(enabled=True, min_products=1, max_products=20):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_popular_category',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {
                    'enabled': enabled,
                    'min_products': min_products,
                    'max_products': max_products,
                },
                'predicate': {'type': 'true'},
            },
        ],
    )


DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_discounts_enabled',
    consumers=['eats-discounts-applicator/enabled_discounts'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

DISCOUNTS_APPLICATOR_CASHBACK_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_discounts_applicator_cashback',
    consumers=['eats-discounts-applicator/enabled_discounts'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

CASHBACK_DISCOUNTS_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_discounts_applicator',
    consumers=['eats_products/discounts_applicator'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'discounts_enabled': True, 'cashback_enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

REQUEST_SHOPS_ONLY_FROM_CATALOG = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_edadeal_request_shop_only',
    consumers=['eats_products/edadeal_places'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)


def make_sort_types(
        by_popularity=False,
        price_asc=False,
        price_desc=False,
        block_position=None,
):
    result = {
        'predicate': {'init': {}, 'type': 'true'},
        'title': 'any-title',
        'value': {
            'by_popularity': {
                'enabled': by_popularity,
                'slug': 'by_popularity',
                'title_applied': 'Сначала популярные',
                'title_in_list': 'Популярные',
            },
            'price_asc': {
                'enabled': price_asc,
                'slug': 'price_asc',
                'title_applied': 'Сначала дешевые',
                'title_in_list': 'Дешевые',
            },
            'price_desc': {
                'enabled': price_desc,
                'slug': 'price_desc',
                'title_applied': 'Сначала дорогие',
                'title_in_list': 'Дорогие',
            },
        },
    }

    if block_position is not None:
        result['sort_block_position'] = block_position

    return [result]


def few_sorts_enabled(block_position=None):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_sort_types',
        consumers=['eats_products/menu_goods'],
        clauses=make_sort_types(
            by_popularity=True, price_desc=True, block_position=block_position,
        ),
    )


FEW_SORTS_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_sort_types',
    consumers=['eats_products/menu_goods'],
    clauses=make_sort_types(by_popularity=True, price_desc=True),
)

SORTS_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_sort_types',
    consumers=['eats_products/menu_goods'],
    clauses=make_sort_types(),
)


def make_cashback_category_clauses(enabled=True, min_products=1):
    return [
        {
            'title': 'Always match',
            'value': {'enabled': enabled, 'min_products': min_products},
            'predicate': {'type': 'true'},
        },
    ]


CASHBACK_CATEGORY_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_cashback_category',
    consumers=['eats_products/menu_goods'],
    clauses=make_cashback_category_clauses(),
)


def cashback_category_enabled(min_products=1):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_cashback_category',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': True, 'min_products': min_products},
                'predicate': {'type': 'true'},
            },
        ],
    )


CASHBACK_CATEGORY_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_cashback_category',
    consumers=['eats_products/menu_goods'],
    clauses=make_cashback_category_clauses(enabled=False),
)

REQUEST_FIRST_LEAF_EXP = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_request_first_leaf',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True, 'min_products': 50},
            'predicate': {'type': 'true'},
        },
    ],
)

REQUEST_FIRST_LEAF_EXP_OFF = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_request_first_leaf',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False, 'min_products': 50},
            'predicate': {'type': 'true'},
        },
    ],
)

UPSELL_RECOMMENDATIONS_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_upsell_recommendations',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

UPSELL_RECOMMENDATIONS_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_upsell_recommendations',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False},
            'predicate': {'type': 'true'},
        },
    ],
)

DETAILED_DATA_DESCRIPTIONS_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_detailed_data_descriptions',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

DETAILED_DATA_DESCRIPTIONS_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_detailed_data_descriptions',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False},
            'predicate': {'type': 'true'},
        },
    ],
)


def is_upsell_above_descriptions(enabled=True):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_detailed_data_settings',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'upsell_above_description': enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )


def product_card_widgets(enabled=True):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_product_card_widgets',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'name_and_about_product_widgets_enabled': enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )


def categories_carousels_position(
        restaurants_carousel,
        categories_carousel,
        is_restaurants_in_horizontal_carousels,
):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_categories_carousels_position',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {
                    'restaurants_carousel': restaurants_carousel,
                    'categories_carousel': categories_carousel,
                    'is_restaurants_in_horizontal_carousels': (
                        is_restaurants_in_horizontal_carousels
                    ),
                },
                'predicate': {'type': 'true'},
            },
        ],
    )


ENERGY_VALUES_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_energy_values',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

ENERGY_VALUES_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_energy_values',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False},
            'predicate': {'type': 'true'},
        },
    ],
)

CUSTOM_CATEGORIES_RANDOMIZATION_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_custom_categories_randomization',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True, 'randomization_period_minutes': 60},
            'predicate': {'type': 'true'},
        },
    ],
)

CUSTOM_CATEGORIES_RANDOMIZATION_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_custom_categories_randomization',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False, 'randomization_period_minutes': 60},
            'predicate': {'type': 'true'},
        },
    ],
)


PROMO_PRODUCTS_TEXT_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_promo_products_text',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True, 'text': '1+1'},
            'predicate': {'type': 'true'},
        },
    ],
)


PROMO_PRODUCTS_TEXT_NONE = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_promo_products_text',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)


PROMO_PRODUCTS_TEXT_DISABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_promo_products_text',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': False, 'text': '1+1'},
            'predicate': {'type': 'true'},
        },
    ],
)


def make_promo_sorts_experiment(
        promotions: typing.List[str],
        promo_positions: typing.List[int] = None,
        consumer='eats_products/menu_goods',
):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='adverts_auction_products',
        consumers=[consumer],
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {
                    'promotions': [
                        {'promo_name': name} for name in promotions
                    ],
                    'promo_positions': promo_positions,
                },
            },
        ],
    )


def weight_data(enabled=True, tag_name=None):
    return pytest.mark.experiments3(
        is_config=True,
        match=ALWAYS_MATCH,
        name='eats_products_weight_data',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': enabled, 'tag_name': tag_name},
                'predicate': {'type': 'true'},
            },
        ],
    )


def filters_settings(
        enabled=True,
        use_nomenclature=False,
        use_brand=None,
        discounts_filter=None,
        popular_options_limit=2,
):
    return pytest.mark.experiments3(
        is_config=False,
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {
                    'all_text': 'Все',
                    'brand_filter_enabled': use_brand,
                    'brand_filter_name': 'Бренд',
                    'done_button_text': 'Готово',
                    'enabled': enabled,
                    'min_goods_to_show_filters': 0,
                    'min_percent_of_filled_brand': 0,
                    'popular_options_limit': popular_options_limit,
                    'popular_text': 'Популярное',
                    'reset_button_text': 'Сбросить',
                    'show_all_button_text': 'Еще',
                    'show_button_text': 'Показать',
                    'nomenclature_filters_enabled': use_nomenclature,
                    'discounts_filter': discounts_filter,
                },
            },
        ],
        consumers=['eats_products/filters_settings'],
        name='eats_products_filters_settings',
    )


CATALOG_OVERRIDES = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_catalog_slug_brand_color_overrides',
    consumers=['eats-catalog-slug'],
    clauses=[
        {
            'title': 'Always match',
            'value': {
                'color': [
                    {'theme': 'light', 'value': '#000000'},
                    {'theme': 'dark', 'value': '#FFFFFF'},
                ],
                'logo_url': [
                    {'theme': 'light', 'size': 'small', 'url': 'light_url'},
                    {'theme': 'dark', 'size': 'small', 'url': 'dark_url'},
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
)

CAROUSEL_PICTURES_TYPE_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_carousel_pictures_type',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

REMOVE_EMPTY_CATEGORIES_ENABLED = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_products_categories_settings',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'remove_categories_without_products': True},
            'predicate': {'type': 'true'},
        },
    ],
)

HORIZONTAL_CAROUSEL_SHOW_IN_ENABLED = pytest.mark.experiments3(
    is_config=False,
    match=ALWAYS_MATCH,
    name='eats_products_horizontal_carousel_show_in',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

INVERT_GALLERY_SOURCES_ENABLED = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_products_categories_gallery_settings',
    consumers=['eats_products/menu_goods'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'invert_gallery_sources': True},
            'predicate': {'type': 'true'},
        },
    ],
)


def personalized_carousels(parts: typing.List[str]):
    return pytest.mark.experiments3(
        is_config=True,
        match=ALWAYS_MATCH,
        name='eats_products_personalized_carousels',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {'personalization_types': parts},
            },
        ],
    )


def cross_brand_history(
        new_min_total=3,
        new_min_available=2,
        old_min_available=2,
        informer=None,
        this_brand_category_name='Только в {brand}',
        other_brands_category_name='Не только в {brand}',
        promo_cheaper_here=None,
):
    return pytest.mark.experiments3(
        is_config=True,
        match=ALWAYS_MATCH,
        name='eats_products_cross_brand_history',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {
                    'new_brand': {
                        'min_total_products': new_min_total,
                        'min_available_products': new_min_available,
                        'informer': informer,
                    },
                    'brand_with_orders': {
                        'min_available_products': old_min_available,
                    },
                    'this_brand_category_name': this_brand_category_name,
                    'other_brands_category_name': other_brands_category_name,
                    'promo_cheaper_here': promo_cheaper_here,
                },
                'predicate': {'type': 'true'},
            },
        ],
    )


def discounts_categorization(enabled: bool, top_discounts_limit=None):
    value: dict = {'enabled': enabled}
    if top_discounts_limit is not None:
        value['top_discounts_limit'] = top_discounts_limit
        value['top_discounts_name'] = 'Топ скидок'
    return pytest.mark.experiments3(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': value,
            },
        ],
        consumers=['eats_products/menu_goods'],
        name='eats_products_discounts_categorization',
    )


def discounts_max_products(enabled: bool):
    return pytest.mark.experiments3(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {
                    'enabled': enabled,
                    'name': 'Скидки',
                    'max_products': 3,
                },
            },
        ],
        consumers=['eats_products/menu_goods'],
        name='eats_products_discount_category_max_products',
    )


def communications(
        main_shop_stories_enabled: bool = False,
        categories_stories_enabled: bool = False,
        main_shop_informers_enabled: bool = False,
        categories_informers_enabled: bool = False,
        product_card_informers_enabled: bool = False,
):
    return pytest.mark.experiments3(
        is_config=True,
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {
                    'main_shop_stories_enabled': main_shop_stories_enabled,
                    'categories_stories_enabled': categories_stories_enabled,
                    'main_shop_informers_enabled': main_shop_informers_enabled,
                    'categories_informers_enabled': (
                        categories_informers_enabled
                    ),
                    'product_card_informers_enabled': (
                        product_card_informers_enabled
                    ),
                },
            },
        ],
        consumers=['eats_products/menu_goods'],
        name='eats_products_communications',
    )


def categories_show_in_overrides(show_in=None):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_categories_position_overrides',
        consumers=['eats_products/categories_position_overrides'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'show_in': show_in},
                'predicate': {'type': 'true'},
            },
        ],
    )


def categories_position_sort_order(categories=None):
    if categories is None:
        categories = []
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_categories_position_overrides',
        consumers=['eats_products/categories_position_overrides'],
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'category_id',
                        'arg_type': 'string',
                        'value': str(category['id']),
                    },
                    'type': 'eq',
                },
                'enabled': True,
                'value': {
                    'show_in': ['horizontal_carousel'],
                    'sort_order': category['sort_order'],
                },
            }
            for category in categories
        ],
    )


def categories_scoring(enabled=True, yt_table_name='yt_categories_table_v3'):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_categories_scoring',
        consumers=['eats_products/categories_scoring'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': enabled, 'yt_table_name': yt_table_name},
                'predicate': {'init': {}, 'type': 'true'},
            },
        ],
    )


def products_scoring(enabled=True, yt_table_name='yt_table_v3'):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_products_scoring',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': enabled, 'yt_table_name': yt_table_name},
                'predicate': {'init': {}, 'type': 'true'},
            },
        ],
    )


def category_picture_type(enabled=True):
    return pytest.mark.experiments3(
        is_config=False,
        match=ALWAYS_MATCH,
        name='eats_products_carousel_pictures_type',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': enabled},
                'predicate': {'init': {}, 'type': 'true'},
            },
        ],
    )
