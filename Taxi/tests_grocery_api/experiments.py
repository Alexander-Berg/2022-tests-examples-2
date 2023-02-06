# pylint: disable=too-many-lines
# pylint: disable=invalid-name

import pytest


def create_modes_layouts_exp(layout_id):
    return pytest.mark.experiments3(
        name='grocery-api-modes-layouts',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'layout_id': layout_id},
            },
        ],
    )


MODES_ROOT_LAYOUT_ENABLED = create_modes_layouts_exp('layout-1')

SUBSTITUTE_UNCROSSED_PRICE_ENABLED = pytest.mark.experiments3(
    name='substitute_uncrossed_price',
    is_config=True,
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)

SUBSTITUTE_UNCROSSED_PRICE_DISABLED = pytest.mark.experiments3(
    name='substitute_uncrossed_price',
    is_config=True,
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': False},
        },
    ],
)

CASHBACK_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_cashback',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

UPSALE_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_caas_upsale',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

PROMO_CAAS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_caas_discounts',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)

TIPS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_tips_proposals',
    is_config=True,
    consumers=['grocery-tips-shared/tips'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Выкл для tristero',
            'enabled': True,
            'extension_method': 'replace',
            'predicate': {
                'init': {
                    'arg_name': 'order_flow_version',
                    'set': ['tristero_flow_v1'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {},
        },
        {
            'title': 'Always enabled RUS',
            'predicate': {
                'init': {
                    'arg_name': 'country_iso3',
                    'set': ['RUS'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'tips_proposals': ['49', '99', '149'],
                'tips_proposals_v2': [
                    {'amount': '49', 'amount_type': 'absolute'},
                    {'amount': '99', 'amount_type': 'absolute'},
                    {'amount': '149', 'amount_type': 'absolute'},
                ],
            },
        },
    ],
    default_value={},
)


def create_search_flow_experiment(
        search_flow, *, fallback_flow=None, search_flow_api_params=None,
):
    clauses = [
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'search_flow': search_flow},
        },
    ]
    if search_flow_api_params is not None:
        clauses[0]['value']['search_flow_api_params'] = search_flow_api_params
    if fallback_flow is not None:
        clauses[0]['value']['fallback_flow'] = fallback_flow

    return pytest.mark.experiments3(
        name='grocery_api_search_flow',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
    )


SEARCH_FLOW_INTERNAL = create_search_flow_experiment('internal')
SEARCH_FLOW_SAAS = create_search_flow_experiment('saas')
SEARCH_FLOW_MARKET = create_search_flow_experiment('market')


def create_search_categories_flow_experiment(
        search_categories_flow, *, allowed_categories=None,
):
    clauses = [
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'search_categories_flow': search_categories_flow},
        },
    ]
    if allowed_categories is not None:
        clauses[0]['value']['allowed_categories'] = allowed_categories

    return pytest.mark.experiments3(
        name='grocery_api_search_categories_flow',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
    )


SEARCH_CATEGORIES_FLOW_NONE = create_search_categories_flow_experiment('none')
SEARCH_CATEGORIES_FLOW_INTERNAL = create_search_categories_flow_experiment(
    'internal', allowed_categories=['category', 'virtual_category'],
)
SEARCH_CATEGORIES_FLOW_SAAS = create_search_categories_flow_experiment(
    'saas', allowed_categories=['category'],
)


def _create_saas_relev_params_experiment(debug, formula, kps=None):
    value = {}
    value['debug'] = debug
    if formula:
        value['formula'] = formula
    if kps:
        value['kps'] = kps

    return pytest.mark.experiments3(
        name='grocery_saas_relev_params',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


def create_saas_custom_formula(formula):
    return _create_saas_relev_params_experiment(True, formula)


def create_saas_custom_params(debug, formula, kps):
    return _create_saas_relev_params_experiment(debug, formula, kps)


MARKDOWN_ENABLED = pytest.mark.experiments3(
    name='lavka_selloncogs',
    consumers=['grocery-caas/client_library'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

USE_AUTOMATIC_DISCOUNT_LABEL = pytest.mark.experiments3(
    name='grocery_api_enable_automatic_discount_label',
    consumers=['grocery-api/discounts'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=False,
)


def _expring_products_experiments(enabled):
    return pytest.mark.experiments3(
        name='grocery_enable_expiring_products',
        consumers=['grocery-api/discounts'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=False,
    )


EXPIRING_PRODUCTS_ENABLED = _expring_products_experiments(enabled=True)

EXPIRING_PRODUCTS_DISABLED = _expring_products_experiments(enabled=False)


def lavka_parcel_config(experiments3, enabled=True):
    experiments3.add_config(
        name='lavka_parcel',
        consumers=['grocery-api/modes', 'grocery-api/parcels'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


def oneclick_catalog_availability(experiments3, available=True):
    experiments3.add_config(
        name='grocery_oneclick_catalog_availability',
        consumers=['grocery-api/parcels'],
        clauses=[
            {
                'title': 'Always available',
                'predicate': {'type': 'true'},
                'value': {'available': available},
            },
        ],
    )


GROCERY_API_INFORMER = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'name': 'test_informer',
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': True,
                        'place': 'root',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'category_ids': ['category-1', 'category-2'],
                        'category_group_ids': ['some_category_group'],
                        'product_ids': ['product-1', 'product-2'],
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_INFORMER_WITH_PREDICATE = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'uid',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'user_id',
                    'value': 'user_id',
                },
            },
            'value': {
                'informers': [
                    {
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': False,
                        'place': 'category',
                        'category_ids': ['some_category_id'],
                    },
                ],
            },
        },
    ],
    is_config=True,
    default_value={
        'informers': [
            {
                'picture': 'another_url',
                'text': 'bye',
                'show_in_root': False,
                'place': 'category',
                'category_ids': ['some_category_id'],
            },
        ],
    },
)

GROCERY_API_INFORMER_ORDER_COMPLETED_PREDICATE = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'uid',
            'predicate': {
                'init': {
                    'arg_name': 'user_orders_completed',
                    'arg_type': 'int',
                    'value': 0,
                },
                'type': 'eq',
            },
            'value': {
                'informers': [
                    {
                        'picture': 'welcome_newbie.jpg',
                        'text': 'Free delivery for newbies',
                        'show_in_root': True,
                        'place': 'root',
                    },
                ],
            },
        },
    ],
    is_config=True,
    default_value={
        'informers': [
            {
                'picture': 'welcome.jpg',
                'text': 'Sorry, no free delivery for you',
                'show_in_root': True,
                'place': 'root',
            },
        ],
    },
)

GROCERY_API_INFORMER_EMPTY_RESPONSE = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'name': 'test_informer',
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': False,
                        'place': 'product',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'category_ids': [],
                        'category_group_ids': [],
                        'product_ids': [],
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                    {
                        'name': 'test_informer',
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': False,
                        'place': 'category',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'category_ids': [],
                        'category_group_ids': [],
                        'product_ids': [],
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_INFORMER_IN_PRODUCT = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'name': 'test_informer',
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': False,
                        'place': 'product',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'category_ids': ['category-1', 'category-2'],
                        'category_group_ids': ['some_category_group'],
                        'product_ids': ['product-1', 'product-2'],
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_MARKET_INFORMER = pytest.mark.experiments3(
    name='grocery_api_market_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'name': 'test_market_informer',
                        'picture': 'some_url',
                        'text': 'hello',
                        'show_in_root': True,
                        'place': 'root',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'category_ids': ['category-1', 'category-2'],
                        'category_group_ids': ['some_category_group'],
                        'product_ids': ['product-1', 'product-2'],
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_DIFFERENT_PLACES_INFORMER = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {'text': 'Only root', 'show_in_root': True},
                    {
                        'text': 'Only category',
                        'show_in_root': False,
                        'category_ids': ['virtual-category-1'],
                    },
                    {
                        'text': 'For subcategory',
                        'show_in_root': False,
                        'category_ids': ['category-1-subcategory-1'],
                    },
                    {
                        'text': 'Only category-2',
                        'show_in_root': False,
                        'category_ids': ['category-1'],
                    },
                    {
                        'text': 'Only category group',
                        'show_in_root': False,
                        'category_group_ids': ['category-group-1'],
                        'category_ids': [],
                    },
                    {
                        'text': 'Only category group-2',
                        'show_in_root': False,
                        'category_group_ids': ['some_category_group'],
                    },
                    {
                        'text': 'Only product-1',
                        'show_in_root': False,
                        'category_group_ids': [],
                        'product_ids': ['product-1'],
                    },
                    {
                        'text': 'Only product-2',
                        'show_in_root': False,
                        'category_group_ids': [],
                        'product_ids': ['product-2'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_PRODUCT_INFORMER = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'text': 'Only root',
                        'show_in_root': False,
                        'category_ids': ['virtual-category-1'],
                        'hide_if_product_is_missing': [
                            'product-1',
                            'product-3',
                        ],
                    },
                    {
                        'text': 'Only root',
                        'show_in_root': False,
                        'category_ids': ['virtual-category-1'],
                        'hide_if_product_is_missing': ['product-3'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_SURGE_INFORMER = pytest.mark.experiments3(
    name='grocery_surge_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'picture': 'surge_url',
                        'text': 'bolsho surge',
                        'show_in_root': False,
                        'place': 'category',
                        'category_ids': ['some_category_id'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_ROOT_SURGE_INFORMER = pytest.mark.experiments3(
    name='grocery_surge_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'picture': 'surge_url',
                        'text': 'bolsho surge',
                        'show_in_root': True,
                        'place': 'root',
                        'category_ids': ['some_category_id'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_CASHBACK_ANNIHILATION_INFORMER = pytest.mark.experiments3(
    name='grocery_cashback_annihilation_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'picture': 'some url',
                        'text': 'cashback`s not gonna wait for you, pal!',
                        'show_in_root': False,
                        'category_ids': ['some_category_id'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

GROCERY_API_DESKTOP_HEAD_BANNERS = pytest.mark.experiments3(
    name='grocery_api_desktop_head_banners',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'desktop_head_banners': [
                    {
                        'picture_key': 'picture_key',
                        'picture_x2_key': 'picture_x2_key',
                        'width': 2,
                        'height': 1,
                        'link_key': 'link_key',
                        'background_color': 'black',
                    },
                ],
            },
        },
    ],
    is_config=False,
)

GROCERY_SUGGEST_ML = pytest.mark.experiments3(
    name='grocery_suggest_ml',
    is_config=False,
    consumers=['grocery-api/modes', 'grocery-upsale-provider'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'tag': 'ml/suggest/heuristic-on-historical-candidates',
                'complement_candidates_default': ['product-1'],
                'complement_candidates_ranker_field': 'total_cnt',
            },
        },
    ],
    default_value={},
)

GROCERY_PRODUCTS_BIG_CARDS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='grocery_api_modes_products_big_cards',
    consumers=['grocery-api/modes'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                '__default__': {'width': 2, 'height': 4, 'categories': []},
                'product-2': {
                    'width': 6,
                    'height': 3,
                    'categories': ['virtual-category-1', 'virtual-category-3'],
                },
            },
        },
    ],
)

GROCERY_PRODUCTS_SMALL_CARDS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_api_modes_products_small_cards',
    consumers=['grocery-api/modes'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'width': 3,
                'height': 4,
                'categories': ['virtual-category-1'],
            },
        },
    ],
)

GROCERY_API_REFERRAL_INFORMERS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='grocery_api_referral_informers',
    consumers=['grocery-api/service-info'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)


def parent_products_exp(enabled):
    return pytest.mark.experiments3(
        name='grocery_api_parent_products',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': False},
        is_config=False,
    )


PARENT_PRODUCTS_ENABLED = parent_products_exp(enabled=True)

SHOW_SOLD_OUT_ENABLED = pytest.mark.experiments3(
    name='grocery_api_show_sold_out',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

GROCERY_PRICE_RISE_MAP = pytest.mark.experiments3(
    name='grocery_price_rise_map',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'products_map': [
                    {'products_ids': ['product-1'], 'rise_coef': '3.5'},
                ],
            },
        },
    ],
    is_config=False,
)

FIRST_SUBCATEGORY_DISCOUNT = pytest.mark.experiments3(
    name='grocery_api_create_discount_subcategory',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'min_items_count': 1,
                'max_items_count': 100,
            },
        },
    ],
    default_value={
        'enabled': False,
        'min_items_count': 1,
        'max_items_count': 1,
    },
    is_config=False,
)

GROCERY_API_ERRORS_CONFIG = pytest.mark.experiments3(
    name='grocery_api_errors_config',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'errors': [
                    {
                        'name': 'test_informer',
                        'text': 'hello',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'disable_cart': True,
                        'disable_cart_checkout': False,
                        'modal': {
                            'text': 'hello',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'picture': 'some_picture',
                            'title': 'some_title',
                            'buttons': [
                                {
                                    'variant': 'action',
                                    'text': 'button',
                                    'text_color': 'blue',
                                    'background_color': 'blue',
                                    'link': 'some_link',
                                },
                                {'variant': 'default', 'text': 'button too'},
                            ],
                        },
                    },
                ],
            },
        },
    ],
    is_config=True,
)


def carousel_subcategories_enabled(enabled=True, min_items_count=1):
    return pytest.mark.experiments3(
        name='grocery_api_enable_carousel_subcategories',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always disabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': enabled,
                    'min_items_count': min_items_count,
                },
            },
        ],
        is_config=False,
    )


MARKDOWN_DISCOUNTS_ENABLED = pytest.mark.experiments3(
    name='grocery_enable_markdown_discounts',
    consumers=['grocery-api/discounts'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)

DESCRIPTION_INGREDIENTS_CONTENT = pytest.mark.experiments3(
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
                    {'title_key': '', 'attributes': ['pfc']},
                    {
                        'title_key': 'product_content_ingredients',
                        'attributes': ['ingredients'],
                    },
                    {
                        'title_key': 'product_content_description',
                        'attributes': ['description'],
                    },
                ],
            },
        },
    ],
)


def parametrize_recent_goods_exp(enabled=True, always_enabled=False):
    return pytest.mark.experiments3(
        name='grocery_caas_recent_products',
        consumers=['grocery-caas/client_library'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': enabled,
                    'always_enabled': always_enabled,
                },
            },
        ],
        is_config=True,
    )


def random_products(
        experiments3,
        upper_shift,
        prefetch_limit,
        lower_shift='0',
        response_limit=10,
):
    return experiments3.add_config(
        name='grocery_api_random_products',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'lower_shift': lower_shift,
                    'upper_shift': upper_shift,
                    'prefetch_limit': prefetch_limit,
                    'response_limit': response_limit,
                },
            },
        ],
    )


RECENT_GOODS_EXP = parametrize_recent_goods_exp()

HAPPY_NEW_YEAR = pytest.mark.experiments3(
    name='grocery_caas_new_year',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'answers': [
                    {
                        'question_id': f'answer_{i}',
                        'subcategories': [
                            {'id': f'category-1-subcategory-{j + 1}'}
                            for j in range(4)
                        ],
                    }
                    for i in range(5)
                ],
            },
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)


ENABLE_PERSONAL = pytest.mark.experiments3(
    name='grocery_caas_personal',
    consumers=['grocery-caas/client_library'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'subcategories_order': ['recent_purchases', 'favorites'],
            },
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)


def _enable_combo_v2(value):
    return pytest.mark.experiments3(
        name='grocery_enable_combo_products',
        consumers=['grocery-api/modes'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': False, 'enabled_combo_v2': value},
            },
        ],
        default_value={'enabled': False, 'enabled_combo_v2': False},
    )


ENABLE_COMBO_V2 = _enable_combo_v2(True)

DISABLE_COMBO_V2 = _enable_combo_v2(False)

SEARCH_FILTER_CATEGORIES_FOUND_BY_NOT_EQUALLY_MATCHED_PREFIXES = (
    pytest.mark.experiments3(
        name='grocery_api_search_categories_internal',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'filter_found_by_not_equally_matched_prefix': True},
            },
        ],
        is_config=True,
    )
)


GROCERY_API_INFORMER_STORIES = pytest.mark.experiments3(
    name='grocery_api_informer',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'informers': [
                    {
                        'text': 'hello',
                        'show_in_root': True,
                        'product_ids': ['product-1'],
                        'category_ids': ['virtual-category-1'],
                        'stories': [
                            {
                                'variant': 'normal',
                                'caption': 'text_caption',
                                'title': 'title',
                                'text': 'text',
                                'text_position': 'top',
                                'text_color': 'red',
                                'image': {
                                    'source': 'some_picture',
                                    'fallback_color': 'black',
                                    'duration_ms': 10,
                                },
                                'with_fade': True,
                                'product_id': 'product-1',
                                'buttons': [
                                    {
                                        'text': 'button_text',
                                        'variant': 'default',
                                    },
                                ],
                            },
                            {
                                'variant': 'inverted',
                                'video': {
                                    'source': 'some_video',
                                    'cover': 'cover',
                                    'fallback_color': 'black',
                                    'source_webm': 'some_video_webm',
                                },
                            },
                            {
                                'variant': 'inverted',
                                'title': 'video_and_image',
                                'video': {
                                    'source': 'some_video',
                                    'cover': 'cover',
                                    'fallback_color': 'black',
                                    'source_webm': 'some_video_webm',
                                },
                                'image': {
                                    'source': 'some_picture',
                                    'fallback_color': 'black',
                                    'duration_ms': 10,
                                },
                            },
                            {
                                'variant': 'inverted',
                                'title': 'invalid_story_1',
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)


def antifraud_check_exp_(enabled, cache_enabled=False):
    return pytest.mark.experiments3(
        name='grocery_enable_discount_antifraud',
        consumers=['grocery-antifraud'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enable': enabled, 'cache_enable': cache_enabled},
            },
        ],
        default_value={'enable': False},
        is_config=True,
    )


ANTIFRAUD_CHECK_ENABLED = antifraud_check_exp_(True)
ANTIFRAUD_CHECK_WITH_CACHE_ENABLED = antifraud_check_exp_(True, True)
ANTIFRAUD_CHECK_DISABLED = antifraud_check_exp_(False)


def _pigeon_data_enabled(enabled):
    return pytest.mark.experiments3(
        name='grocery_api_enable_pigeon_data',
        consumers=['grocery-api/user-defined-exp'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=False,
    )


PIGEON_DATA_ENABLED = _pigeon_data_enabled(True)
PIGEON_DATA_DISABLED = _pigeon_data_enabled(False)


def _combos_in_search_enable(enabled):
    return pytest.mark.experiments3(
        name='grocery_api_search_enable_combos',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )


COMBOS_IN_SEARCH_ENABLED = _combos_in_search_enable(True)
COMBOS_IN_SEARCH_DISABLED = _combos_in_search_enable(False)


def custom_special_category(
        enabled, special_category_id, products_ids, is_config=False,
):
    return pytest.mark.experiments3(
        name='grocery_custom_special_category_' + special_category_id,
        consumers=['grocery-api/custom-special-categories'],
        match={'predicate': {'type': 'true'}, 'enabled': enabled},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'products': products_ids.copy()},
            },
        ],
        default_value={'products': []},
        is_config=is_config,
    )


def grocery_api_enable_newbie_scoring(experiments3, enabled=True):
    experiments3.add_config(
        name='grocery_api_enable_newbie_scoring',
        consumers=['grocery-api/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {
                    'init': {
                        'arg_name': 'application',
                        'arg_type': 'string',
                        'value': 'mobileweb_android',
                    },
                    'type': 'eq',
                },
                'value': {'enabled': enabled},
            },
        ],
    )


def seach_market_use_relevance_formula(formula):
    return pytest.mark.experiments3(
        name='grocery_search_market_use_relevance_formula',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'formula': formula},
            },
        ],
    )
