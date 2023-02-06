import copy

import pytest

from . import const
from . import experiments

# Сетка, с которой работаем в этом файле, выглядит так:
# -   group-a
#     -   category-b
#         -   subcategory-c
#             -   product-d
#             -   product-e
#             -   product-f
#         -   subcategory-g
#             -   product-h
#             -   product-i
#             -   product-j
# -   group-k
#     -   category-l
#         -   subcategory-m
#             -   product-d
#             -   product-n
#             -   product-o
# -   group-special
#     -   promo-caas
#         -   caas-subcategory
#             -   product-x
#             -   product-y


CATEGORY_TREE = {
    'categories': [
        {'id': 'subcategory-c'},
        {'id': 'subcategory-g'},
        {'id': 'subcategory-m'},
        {'id': 'out-of-layout-subcategory-for-caas'},
    ],
    'depot_ids': ['test-depot-id'],
    'markdown_products': [],
    'products': [
        {
            'category_ids': ['subcategory-c', 'subcategory-m'],
            'full_price': '100.0',
            'id': 'product-d',
            'rank': 1,
        },
        {
            'category_ids': ['subcategory-c'],
            'full_price': '200.0',
            'id': 'product-e',
            'rank': 2,
        },
        {
            'category_ids': ['subcategory-c'],
            'full_price': '300',
            'id': 'product-f',
            'rank': 3,
        },
        {
            'category_ids': ['subcategory-g'],
            'full_price': '100.1',
            'id': 'product-h',
            'rank': 1,
        },
        {
            'category_ids': ['subcategory-g'],
            'full_price': '200.2',
            'id': 'product-i',
            'rank': 2,
        },
        {
            'category_ids': ['subcategory-g'],
            'full_price': '300.3',
            'id': 'product-j',
            'rank': 3,
        },
        {
            'category_ids': ['subcategory-m'],
            'full_price': '50',
            'id': 'product-n',
            'rank': 10,
        },
        {
            'category_ids': ['subcategory-m'],
            'full_price': '70',
            'id': 'product-o',
            'rank': 5,
        },
        {
            'category_ids': ['out-of-layout-subcategory-for-caas'],
            'full_price': '33',
            'id': 'product-x',
            'rank': 1,
        },
        {
            'category_ids': ['out-of-layout-subcategory-for-caas'],
            'full_price': '22',
            'id': 'product-y',
            'rank': 2,
        },
    ],
}

STOCKS = [
    {'in_stock': '10', 'product_id': 'product-d', 'quantity_limit': '5'},
    {'in_stock': '10', 'product_id': 'product-e', 'quantity_limit': '10'},
    {'in_stock': '0', 'product_id': 'product-f', 'quantity_limit': '0'},
    {'in_stock': '0', 'product_id': 'product-h', 'quantity_limit': '0'},
    {'in_stock': '10', 'product_id': 'product-i', 'quantity_limit': '10'},
    {'in_stock': '0', 'product_id': 'product-j', 'quantity_limit': '0'},
    {'in_stock': '1', 'product_id': 'product-n', 'quantity_limit': '1'},
    {'in_stock': '0', 'product_id': 'product-o', 'quantity_limit': '0'},
]

EXPECTED_RELATIONS = [
    {
        'children': [
            {
                'children': [
                    {
                        'children': [
                            {
                                'item': {
                                    'id': 'product-d',
                                    'price': '100',
                                    'quantity': 10,
                                    'type': 'product',
                                },
                            },
                            {
                                'item': {
                                    'id': 'product-e',
                                    'price': '200',
                                    'quantity': 10,
                                    'type': 'product',
                                },
                            },
                        ],
                        'item': {'id': 'subcategory-c', 'type': 'subcategory'},
                    },
                    {
                        'children': [
                            {
                                'item': {
                                    'id': 'product-i',
                                    'price': '200.2',
                                    'quantity': 10,
                                    'type': 'product',
                                },
                            },
                        ],
                        'item': {'id': 'subcategory-g', 'type': 'subcategory'},
                    },
                ],
                'item': {
                    'id': 'virtual-category-category-b',
                    'type': 'category',
                },
            },
        ],
        'item': {'id': 'category-group-group-a', 'type': 'category_group'},
    },
    {
        'children': [
            {
                'children': [
                    {
                        'item': {
                            'id': 'product-x',
                            'price': '33',
                            'quantity': 17,
                            'type': 'product',
                        },
                    },
                ],
                'item': {'id': 'promo-caas', 'type': 'category'},
            },
        ],
        'item': {
            'id': 'category-group-group-special',
            'type': 'category_group',
        },
    },
]

EXPECTED_RELATIONS_GROUPS = [
    {'item': {'id': 'category-group-group-a', 'type': 'category_group'}},
    {'item': {'id': 'category-group-group-special', 'type': 'category_group'}},
]

EXPECTED_RELATIONS_SUBCATEGORIES = [
    {'item': {'id': 'subcategory-c', 'type': 'subcategory'}},
    {'item': {'id': 'subcategory-g', 'type': 'subcategory'}},
]


def category_tree_for_depot(depot_id):
    new_category_tree = copy.deepcopy(CATEGORY_TREE)
    new_category_tree['depot_ids'] = [depot_id]
    return new_category_tree


def initialize_layout(
        depot_id,
        legacy_depot_id,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
):
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, depot_id=depot_id,
    )
    overlord_catalog.add_category_tree(
        depot_id=depot_id, category_tree=category_tree_for_depot(depot_id),
    )
    overlord_catalog.add_products_stocks(
        depot_id=depot_id, new_products_stocks=STOCKS,
    )
    overlord_catalog.set_category_availability(
        category_id='subcategory-c', available=True,
    )
    overlord_catalog.set_category_availability(
        category_id='subcategory-g', available=True,
    )
    overlord_catalog.set_category_availability(
        category_id='subcategory-m', available=False,
    )

    layout = grocery_products.add_layout(test_id='id')
    group_a = layout.add_category_group(test_id='group-a')
    category_b = group_a.add_virtual_category(test_id='category-b')
    category_b.add_subcategory(subcategory_id='subcategory-c')
    category_b.add_subcategory(subcategory_id='subcategory-g')

    group_k = layout.add_category_group(test_id='group-k')
    category_l = group_k.add_virtual_category(test_id='category-l')
    category_l.add_subcategory(subcategory_id='subcategory-m')

    special_group = layout.add_category_group(test_id='group-special')
    special_group.add_virtual_category(
        test_id='category-special', special_category='promo-caas',
    )
    grocery_caas_promo.add_subcategory(
        subcategory_id='caas-subcategory',
        title_tanker_key='caas-subcategory-title',
    )
    grocery_caas_promo.add_products(product_ids=['product-x', 'product-y'])
    overlord_catalog.add_products_stocks(
        depot_id=depot_id,
        new_products_stocks=[
            {
                'in_stock': '17',
                'product_id': 'product-x',
                'quantity_limit': '5',
            },
        ],
    )


@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.experiments3(
    name='grocery-api-modes-layouts',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_id': 'layout-id'},
        },
    ],
)
async def test_builds_menu_based_on_layout_and_category_tree(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    initialize_layout(
        depot_id,
        legacy_depot_id,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
    )

    response = await taxi_grocery_api.post(
        '/internal/v1/api/v1/menu', json={'depot_id': legacy_depot_id},
    )
    assert response.status_code == 200
    assert response.json() == {'relations': EXPECTED_RELATIONS}


@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.experiments3(
    name='grocery-api-modes-layouts',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_id': 'layout-id'},
        },
    ],
)
async def test_can_be_constrained_with_depth(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    initialize_layout(
        depot_id,
        legacy_depot_id,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
    )

    response = await taxi_grocery_api.post(
        '/internal/v1/api/v1/menu',
        json={'depot_id': legacy_depot_id, 'depth': 1},
    )
    assert response.status_code == 200
    assert response.json() == {'relations': EXPECTED_RELATIONS_GROUPS}


@experiments.PROMO_CAAS_EXPERIMENT
@pytest.mark.experiments3(
    name='grocery-api-modes-layouts',
    consumers=['grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_id': 'layout-id'},
        },
    ],
)
async def test_menu_items_can_be_cherry_picked(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    initialize_layout(
        depot_id,
        legacy_depot_id,
        overlord_catalog,
        grocery_products,
        grocery_caas_promo,
    )

    response = await taxi_grocery_api.post(
        '/internal/v1/api/v1/menu',
        json={
            'depot_id': legacy_depot_id,
            'depth': 1,
            'root': {
                'path': [
                    'category-group-group-a',
                    'virtual-category-category-b',
                ],
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {'relations': EXPECTED_RELATIONS_SUBCATEGORIES}


async def test_returns_404_when_depot_is_absent_in_cache(taxi_grocery_api):
    response = await taxi_grocery_api.post(
        '/internal/v1/api/v1/menu', json={'depot_id': 'another-depot-id'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'
