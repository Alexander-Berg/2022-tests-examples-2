import pytest

from . import experiments


# возвращает информацию о запрошенных товарах в конкретной лавке
@pytest.mark.now('2020-10-13T07:19:00+00:00')
async def test_ok_depot_product(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    products = {}
    supplier_tin = 'supplier-tin'

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        products[0] = category.add_product(
            product_id=1, supplier_tin=supplier_tin,
        )
        mock_grocery_depots.add_depot(depot)

    wms_product_ids = [p.id_wms for _, p in products.items()]
    product_id = wms_product_ids[0]
    category_id = category.id_wms

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '1', 'product_ids': wms_product_ids},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json == {
        'products': [
            {
                'catalog_price': '100500',
                'category_ids': [category_id],
                'product_id': product_id,
                'external_id': '1',
                'stock_quantity': '1',
                'quantity_limit': '1',
                'subtitle': f'Long Test Product With ID {product_id}',
                'title': f'Test Product With ID {product_id}',
                'image_url_template': f'image of {product_id}',
                'image_url_templates': [f'image of {product_id}'],
                'vat': '20.00',
                'options': {
                    'amount': '5',
                    'amount_unit': 'kg',
                    'logistic_tags': [],
                },
                'categories': [
                    {
                        'id': category_id,
                        'parent_ids': [],
                        'title': f'test_category_{category_id}',
                    },
                ],
                'private_label': False,
                'supplier_tin': supplier_tin,
            },
        ],
    }


@pytest.mark.now('2020-10-13T07:19:00+00:00')
async def test_ok_depot_product_with_master_categories(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    products = {}

    with overlord_db as db:
        depot = db.add_depot(depot_id=1, root_category_external_id='master')
        depot.add_category(category_id=3)
        depot.add_category(category_id=2, parent_id=3)
        category = depot.add_category(category_id=1, parent_id=2)
        products[0] = category.add_product(product_id=1)
        mock_grocery_depots.add_depot(depot)

    wms_product_ids = [p.id_wms for _, p in products.items()]

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '1', 'product_ids': wms_product_ids},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200
    response_json = response.json()

    master_categories = [
        '01234567-89ab-cdef-000a-000001000001',
        '01234567-89ab-cdef-000a-000001000002',
        '01234567-89ab-cdef-000a-000001000003',
        '01234567-89ab-cdef-000a-000001000000',
    ]

    assert (
        response_json['products'][0]['master_categories'] == master_categories
    )


# проверка наличия логистических тегов
@pytest.mark.now('2020-10-13T07:19:00+00:00')
@pytest.mark.parametrize('logistic_tags', [[], ['hot', 'fragile']])
async def test_logistic_tags(
        taxi_overlord_catalog, overlord_db, logistic_tags, mock_grocery_depots,
):
    products = {}

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        products[0] = category.add_product(
            product_id=1, logistic_tags=logistic_tags,
        )
        mock_grocery_depots.add_depot(depot)

    wms_product_ids = [p.id_wms for _, p in products.items()]

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '1', 'product_ids': wms_product_ids},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200

    response_tags = response.json()['products'][0]['options']['logistic_tags']
    assert response_tags == logistic_tags


# если запрашивается отсутствующий продукт, это не является ошибкой
async def test_product_not_found(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        mock_grocery_depots.add_depot(depot)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '1', 'product_ids': ['1']},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {'products': []}


# запрос с отсутствующим депотом
async def test_depot_not_found(taxi_overlord_catalog, overlord_db):
    with overlord_db as db:
        db.add_depot(depot_id=1)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '2', 'product_ids': ['1']},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'NOT_FOUND'


@pytest.mark.parametrize(
    'stocks,price,parents_parent',
    [(1, 0, None), (0, 1, None), (0, 0, 'parent_id'), (0, 0, None)],
)
async def test_only_valid_parent_in_response(
        taxi_overlord_catalog,
        overlord_db,
        stocks,
        price,
        parents_parent,
        mock_grocery_depots,
):
    products = {}
    parent_id = ''

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        parent = category.add_product(
            product_id=1,
            in_stock=stocks,
            price=price,
            parent_id=parents_parent,
            grades=[['netto'], None, None],
        )
        parent_id = parent.id_wms
        products[0] = category.add_product(product_id=2, parent_id=parent_id)
        mock_grocery_depots.add_depot(depot)

    wms_product_ids = [p.id_wms for _, p in products.items()]
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': '1', 'product_ids': wms_product_ids},
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200
    response_json = response.json()
    if stocks == 0 and price == 0 and parents_parent is None:
        assert response_json['products'][0]['parent_id'] == parent_id
    else:
        assert 'parent_id' not in response_json['products'][0]


@experiments.hide_depot(depot_id='1')
async def test_returns_products_if_depot_is_hidden(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    """ Проверяет, что ручка возвращает 200 и информацию о запрошенных товарах,
        если лавка скрыта. """

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        product = category.add_product(product_id=1)
        mock_grocery_depots.add_depot(depot)

    product_id = product.id_wms

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={'depot_id': str(depot.depot_id), 'product_ids': [product_id]},
        headers={},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'][0]['product_id'] == product_id


# проверяем что наборы в которых содержится товар передаются в поле bundle_ids
# если передан флаг need_bundle_products, то в ответ ручки в products
# добавляется информация о наборах
@pytest.mark.parametrize('need_bundle_products', [True, False])
@pytest.mark.parametrize('bundle_is_active', [True, False])
async def test_bundles_in_response(
        taxi_overlord_catalog,
        overlord_db,
        need_bundle_products,
        mock_grocery_depots,
        bundle_is_active,
):
    product_1 = None
    product_2 = None
    bundle_id = None

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        bundle = category.add_product(
            product_id=1,
            in_stock=0,
            price=0,
            vat=None,
            grades=[None, None, None],
            status='active' if bundle_is_active else 'disabled',
        )
        bundle_id = bundle.id_wms
        product_1 = category.add_product(
            product_id=2, parent_id=bundle_id,
        ).id_wms
        product_2 = category.add_product(
            product_id=3, parent_id=bundle_id,
        ).id_wms
        mock_grocery_depots.add_depot(depot)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v2/products',
        json={
            'depot_id': '1',
            'product_ids': [product_1],
            'need_bundle_products': need_bundle_products,
        },
        headers={'X-YaTaxi-Session': 'taxi:userid'},
    )

    assert response.status_code == 200
    response_json = response.json()
    first_product = response_json['products'][0]
    assert first_product['product_id'] == product_1
    if bundle_is_active:
        assert first_product['bundle_ids'] == [bundle_id]
    else:
        assert 'bundle_ids' not in first_product

    assert 'parent_id' not in response_json['products'][0]

    if need_bundle_products:
        if bundle_is_active:
            assert response_json['products'][1]['product_id'] == bundle_id
            assert set(response_json['products'][1]['nested_products']) == {
                product_1,
                product_2,
            }
        else:
            assert len(response_json['products']) == 1
    else:
        assert len(response_json['products']) == 1
