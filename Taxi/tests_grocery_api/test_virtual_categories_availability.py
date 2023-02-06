import pytest

from . import common


async def test_depot_not_found(taxi_grocery_api):
    location = [0, 0]
    json = {'position': {'location': location}, 'virtual_categories': []}
    headers = {}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/virtual-categories-availability',
        json=json,
        headers=headers,
    )
    assert response.status_code == 404


async def test_status_200(taxi_grocery_api, overlord_catalog):
    location = [0, 0]
    common.prepare_overlord_catalog(overlord_catalog, location)
    json = {'position': {'location': location}, 'virtual_categories': []}
    headers = {}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/virtual-categories-availability',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('subcategory_available', [True, False])
@pytest.mark.parametrize(
    'if_subcategory_is_empty_value',
    ['null', '"category-1"', '"category-not-in-category-tree"'],
)
async def test_category_hidings(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        taxi_config,
        subcategory_available,
        if_subcategory_is_empty_value,
):
    item_meta = (
        '{"hide_if_subcategory_is_empty":'
        + if_subcategory_is_empty_value
        + '}'
    )
    category_tree = [
        {'id': 'category-1', 'products': ['product-1']},
        {'id': 'category-2', 'products': ['product-2']},
    ]
    stocks = {'product-1': '10', 'product-2': '10'}
    location = [0, 0]
    virtual_category = common.setup_hide_if_tests(
        overlord_catalog,
        grocery_products,
        location,
        category_tree,
        stocks,
        item_meta,
    )
    overlord_catalog.set_category_availability(
        category_id='category-1', available=subcategory_available,
    )

    virtual_category_id = virtual_category.virtual_category_id

    json = {
        'position': {'location': location},
        'virtual_categories': [virtual_category_id],
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/virtual-categories-availability',
        json=json,
        headers={},
    )
    assert response.status_code == 200

    response_categories = response.json()['available_virtual_categories']

    if if_subcategory_is_empty_value == 'null':
        # subcategory_id not set
        assert response_categories == [virtual_category_id]
    elif if_subcategory_is_empty_value == '"category-not-in-category-tree"':
        # subcategory_id not found in category-tree
        assert response_categories == []
    elif if_subcategory_is_empty_value == '"category-1"':
        # subcategory_id in category-tree and available
        if subcategory_available:
            assert response_categories == [virtual_category_id]
        else:
            assert response_categories == []
    else:
        assert False
