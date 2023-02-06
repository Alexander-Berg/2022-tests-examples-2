# pylint: disable=import-error
from grocery_mocks import grocery_menu as mock_grocery_menu
import pytest

from testsuite.utils import ordered_object


@pytest.mark.pgsql(
    'overlord_catalog', files=['menu.sql', 'refresh_wms_views.sql'],
)
async def test_category_tree_same_depot_key(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-menu.json', 'gdepots-zones-menu.json',
    )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['cursor'] == 1
    assert sorted(result['category_trees'][0]['depot_ids']) == sorted(
        [
            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
        ],
    )
    ordered_object.assert_eq(
        result['category_trees'][0]['products'],
        [
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
                'full_price': '1000',
                'full_price_updated': '2021-08-04T12:45:00+00:00',
                'rank': 1,
                'ranks': [1],
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002',
                'full_price': '1000',
                'full_price_updated': '2021-08-04T12:45:00+00:00',
                'rank': 2,
                'ranks': [2],
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000002'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'full_price': '1000',
                'full_price_updated': '2021-08-04T12:45:00+00:00',
                'rank': 2,
                'ranks': [2],
            },
        ],
        [''],
    )
    assert result['category_trees'][0]['categories'] == [
        {'id': '11111111-1111-1111-1111-000000000001'},
        {
            'id': '11111111-1111-1111-1111-000000000002',
            'category_parent_id': '11111111-1111-1111-1111-000000000001',
        },
    ]


def _format_product_v2(product, category):
    return {
        'category_ids': [category.id_wms],
        'id': product.id_wms,
        'full_price': str(product.price),
        'full_price_updated': product.updated,
        'rank': product.rank,
        'ranks': product.ranks,
    }


def _format_category_v2(category, parent_category=None):
    cat_item = {'id': category.id_wms}
    if parent_category is not None:
        cat_item['category_parent_id'] = parent_category.id_wms
    return cat_item


def _build_menus(overlord_db, mock_grocery_depots):
    trees = None
    with overlord_db as db:
        depot_1 = db.add_depot(depot_id=1)
        category_1 = depot_1.add_category(category_id=1)
        product_1 = category_1.add_product(product_id=1)

        depot_2 = db.add_depot(depot_id=2)
        category_2 = depot_2.add_category(category_id=2)
        product_2 = category_2.add_product(product_id=2)

        tree_1 = {
            'depot_ids': [depot_1.id_wms],
            'products': [],
            'markdown_products': [],
            'categories': [],
            'root_category_id': depot_1.root_category.id_wms,
        }
        tree_1['categories'].append(_format_category_v2(category_1))
        tree_1['products'].append(_format_product_v2(product_1, category_1))

        tree_2 = {
            'depot_ids': [depot_2.id_wms],
            'products': [],
            'markdown_products': [],
            'categories': [],
            'root_category_id': depot_2.root_category.id_wms,
        }
        tree_2['categories'].append(_format_category_v2(category_2))
        tree_2['products'].append(_format_product_v2(product_2, category_2))
        trees = [tree_1, tree_2]
        mock_grocery_depots.add_depot(depot_1)
        mock_grocery_depots.add_depot(depot_2)

    return trees


# test POST /internal/v1/catalog/v2/category-tree
# get all category trees
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_v2(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    trees = _build_menus(overlord_db, mock_grocery_depots)
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 2
    assert response.json()['category_trees'] == trees


# test POST /internal/v1/catalog/v2/category-tree
# get category tree one by one
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_consistently_v2(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    trees = _build_menus(overlord_db, mock_grocery_depots)
    response_length = [1, 1, 0]
    cursor = 0
    for length in response_length:
        response = await taxi_overlord_catalog.post(
            '/internal/v1/catalog/v2/category-tree',
            json={'limit': 1, 'cursor': cursor},
        )
        assert response.status_code == 200
        if length == 0:
            assert response.json()['cursor'] == cursor
            assert response.json()['category_trees'] == []
        else:
            assert response.json()['category_trees'] == [trees[cursor]]
            cursor = response.json()['cursor']


# test POST /internal/v1/catalog/v2/category-tree
# get category tree with markdown products
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_markdown_products(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    with overlord_db as db:
        depot_1 = db.add_depot(depot_id=1)
        category_1 = depot_1.add_category(category_id=1)
        category_1.add_product(product_id=1, shelf_type='markdown')
        mock_grocery_depots.add_depot(depot_1)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 1
    assert response.json()['category_trees'] == [
        {
            'depot_ids': ['0123456789abcdef0000000000000000000000000001'],
            'categories': [],
            'products': [],
            'markdown_products': [
                {
                    'id': '01234567-89ab-cdef-0000-000000000001',
                    'price': '100500',
                },
            ],
            'root_category_id': depot_1.root_category.id_wms,
        },
    ]


# test POST /internal/v1/catalog/v2/category-tree
# test attributes:
# category_ids for product (product is contained in category_1 and category_2)
# category_parent_id for category (category_1 is parent for category_2)
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_parent_ids(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    tree = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category_1 = depot.add_category(category_id=1)
        category_2 = depot.add_category(category_id=2, parent_id=1)
        product = category_1.add_product(product_id=1)
        category_2.add_product(product_id=1)
        tree = {
            'depot_ids': [depot.id_wms],
            'products': [],
            'markdown_products': [],
            'categories': [],
            'root_category_id': depot.root_category.id_wms,
        }
        tree['categories'].append(_format_category_v2(category_1))
        tree['categories'].append(_format_category_v2(category_2, category_1))
        tree['products'].append(_format_product_v2(product, category_1))
        tree['products'][0]['category_ids'].append(category_2.id_wms)
        tree['products'][0]['ranks'] = [1]
        mock_grocery_depots.add_depot(depot)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 1
    assert response.json()['category_trees'] == [tree]


@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_invalid_price_products(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    with overlord_db as db:
        depot_1 = db.add_depot(depot_id=1)
        category_1 = depot_1.add_category(category_id=1)
        category_1.add_product(product_id=1, price='0.0')
        category_1.add_product(product_id=2, price='-10.0')
        category_1.add_product(
            product_id=3, price='0.0', shelf_type='markdown',
        )
        category_1.add_product(
            product_id=4, price='-10.0', shelf_type='markdown',
        )
        mock_grocery_depots.add_depot(depot_1)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 1
    assert response.json()['category_trees'][0]['products'] == []
    assert response.json()['category_trees'][0]['markdown_products'] == []


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['menu_with_parents.sql', 'refresh_wms_views.sql'],
)
async def test_category_tree_parent_products(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-menu_with_parents.json',
        'gdepots-zones-menu_with_parents.json',
    )
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['cursor'] == 1
    assert result['category_trees'][0]['depot_ids'] == [
        'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
    ]
    ordered_object.assert_eq(
        result['category_trees'][0]['products'],
        [
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
                'full_price': '1000',
                'full_price_updated': '2021-08-04T02:39:00+00:00',
                'rank': 1,
                'ranks': [1],
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000002',
                'full_price': '1000',
                'full_price_updated': '2021-07-30T18:39:00+00:00',
                'rank': 2,
                'ranks': [2],
                'parent_id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000002'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'full_price': '1000',
                'full_price_updated': '2020-12-08T13:10:00+00:00',
                'rank': 2,
                'ranks': [2],
                'order_in_parent': 123,
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'full_price': '0',
                'rank': 3,
                'ranks': [3],
            },
            {
                'category_ids': ['11111111-1111-1111-1111-000000000001'],
                'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000005',
                'full_price': '1000',
                'full_price_updated': '2021-08-04T12:45:00+00:00',
                'rank': 4,
                'ranks': [4],
                'parent_id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'order_in_parent': 456,
            },
        ],
        [''],
    )
    assert result['category_trees'][0]['categories'] == [
        {'id': '11111111-1111-1111-1111-000000000001'},
        {
            'id': '11111111-1111-1111-1111-000000000002',
            'category_parent_id': '11111111-1111-1111-1111-000000000001',
        },
    ]


# Родительский товар без грейдов является бандлом
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
@pytest.mark.parametrize('grades', [[], ['netto']])
async def test_category_tree_bundle_products(
        taxi_overlord_catalog, overlord_db, grades, mock_grocery_depots,
):
    child_product_1 = None
    child_product_2 = None
    bundle_product = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        bundle_product = category.add_product(
            product_id=1, grades=[grades, None, None],
        )
        child_product_1 = category.add_product(
            product_id=2,
            grades=[None, None, 10],
            parent_id=bundle_product.id_wms,
        )
        child_product_2 = category.add_product(
            product_id=3,
            grades=[None, None, 20],
            parent_id=bundle_product.id_wms,
        )
        mock_grocery_depots.add_depot(depot)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    is_bundle = not grades
    assert response.status_code == 200
    result = response.json()
    assert result['cursor'] == 1
    products = result['category_trees'][0]['products']
    assert len(products) == 3
    if is_bundle:
        assert set(
            next(
                product
                for product in products
                if product['id'] == bundle_product.id_wms
            )['nested_items'],
        ) == {child_product_1.id_wms, child_product_2.id_wms}
    else:
        assert [
            product['parent_id']
            for product in products
            if product['id'] == child_product_1.id_wms
            or product['id'] == child_product_2.id_wms
        ] == [bundle_product.id_wms, bundle_product.id_wms]


# Проверяем что не отдаем не активные бандлы
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_disabled_bundle_products(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    child_product_1 = None
    child_product_2 = None
    bundle_product = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        bundle_product = category.add_product(
            product_id=1, grades=[[], None, None], status='disabled',
        )
        child_product_1 = category.add_product(
            product_id=2,
            grades=[None, None, 10],
            parent_id=bundle_product.id_wms,
        )
        child_product_2 = category.add_product(
            product_id=3,
            grades=[None, None, 20],
            parent_id=bundle_product.id_wms,
        )
        mock_grocery_depots.add_depot(depot)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['cursor'] == 1
    products = result['category_trees'][0]['products']
    assert len(products) == 2
    assert {product['id'] for product in products} == {
        child_product_1.id_wms,
        child_product_2.id_wms,
    }


@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
@pytest.mark.parametrize('is_valid_combo', [True, False])
async def test_category_tree_combo_products(
        taxi_overlord_catalog,
        overlord_db,
        mock_grocery_depots,
        grocery_menu,
        is_valid_combo,
):
    combo_product = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        combo_product = category.add_product(product_id=2, price=0)
        mock_grocery_depots.add_depot(depot)

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'COMBO_ID',
            [combo_product.id_wms] if is_valid_combo else [],
            [mock_grocery_menu.ProductGroup(False, 1, ['test-product'])],
            'combo_revision',
        ),
    )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )

    assert response.status_code == 200
    result = response.json()
    products = result['category_trees'][0]['products']
    if is_valid_combo:
        assert len(products) == 1
        assert products[0]['id'] == combo_product.id_wms
    else:
        assert not products


# метатовары попдают в дерево категорий только при статусе = active
@pytest.mark.pgsql('overlord_catalog', files=['refresh_wms_views.sql'])
async def test_category_tree_combo_products_status(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots, grocery_menu,
):
    combo_product_1 = None
    combo_product_2 = None
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        combo_product_1 = category.add_product(
            product_id=2, price=0, status='active',
        )
        combo_product_2 = category.add_product(
            product_id=3, price=0, status='disabled',
        )
        mock_grocery_depots.add_depot(depot)

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'COMBO_ID',
            [combo_product_1.id_wms, combo_product_2.id_wms],
            [mock_grocery_menu.ProductGroup(False, 1, ['test-product'])],
            'combo_revision',
        ),
    )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/category-tree',
        json={'limit': 100, 'cursor': 0},
    )

    assert response.status_code == 200
    result = response.json()
    products = result['category_trees'][0]['products']
    assert len(products) == 1
    assert products[0]['id'] == combo_product_1.id_wms
