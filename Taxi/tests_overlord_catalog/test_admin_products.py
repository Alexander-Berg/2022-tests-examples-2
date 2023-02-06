import pytest

from testsuite.utils import ordered_object

from . import conftest


@pytest.mark.pgsql(
    'overlord_catalog', files=['table.sql', 'refresh_wms_views.sql'],
)
async def test_without_category(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-table.json', 'gdepots-zones-table.json',
    )
    await taxi_overlord_catalog.invalidate_caches()
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        json={'wms_depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        {
            'categories': [
                {
                    'data': {
                        'id': '11111111-1111-1111-1111-000000000001',
                        'image_url_template': (
                            '(61d24b27-0e8e-4173-a861-95c87802972f'
                            ',cat_1.jpg,"2019-12-26 15:36:36+03")'
                        ),
                        'subtitle': 'y',
                        'title': 'category_name_1',
                    },
                    'is_available_now': True,
                },
                {
                    'data': {
                        'id': '11111111-1111-1111-1111-000000000002',
                        'image_url_template': (
                            '(61d24b27-0e8e-4173-a861-95c87802972f,cat_1.jpg'
                            ',"2019-12-26 15:36:36+03")'
                        ),
                        'subtitle': 'x',
                        'title': 'category_name_2.0',
                    },
                    'is_available_now': True,
                },
            ],
            'currency': 'RUB',
            'products': [],
        },
        ['categories', 'currency', 'products'],
    )


@pytest.mark.pgsql(
    'overlord_catalog', files=['table.sql', 'refresh_wms_views.sql'],
)
async def test_with_category(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-table.json', 'gdepots-zones-table.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        json={
            'wms_depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'category_id': '11111111-1111-1111-1111-000000000001',
        },
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        {
            'categories': [
                {
                    'data': {
                        'id': '11111111-1111-1111-1111-000000000001',
                        'image_url_template': (
                            '(61d24b27-0e8e-4173-a861-95c87802972f,'
                            'cat_1.jpg,"2019-12-26 15:36:36+03")'
                        ),
                        'subtitle': 'y',
                        'title': 'category_name_1',
                    },
                    'is_available_now': True,
                },
            ],
            'currency': 'RUB',
            'products': [
                {
                    'data': {
                        'description': 'x',
                        'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
                        'subtitle': 'y',
                        'title': 'product_name_1',
                    },
                    'full_price': '1000',
                    'is_available_now': True,
                    'parent_ids': [
                        {
                            'category_id': (
                                '11111111-1111-1111-1111-000000000001'
                            ),
                        },
                    ],
                },
            ],
        },
        [''],
    )


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_with_product_ids(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    with overlord_db as db:
        depot = db.add_depot(depot_id=911)
        category = depot.add_category(category_id=119)
        for idx in range(1, 100):
            depot.add_product(product_id=idx)
            category.add_product(product_id=idx)
        category = depot.add_category(category_id=120)
        for idx in range(100, 200):
            depot.add_product(product_id=idx)
            category.add_product(product_id=idx)
        mock_grocery_depots.add_depot(depot)

    product_ids = []
    for idx in range(102, 300, 3):
        product_ids.append('01234567-89ab-cdef-0000-000000000' + str(idx))

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        json={
            'wms_depot_id': depot.id_wms,
            'category_id': '01234567-89ab-cdef-000a-000911000120',
            'product_ids': product_ids,
        },
    )
    assert response.status_code == 200
    assert (
        'products' in response.json()
        and len(response.json()['products']) == 33
    )

    for product in response.json()['products']:
        assert (
            product['parent_ids'][0]['category_id']
            == '01234567-89ab-cdef-000a-000911000120'
        )


async def test_storage_traits(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=100)
        product = category.add_product(
            product_id=1,
            storage_traits={
                'shelf_life': 365,
                'write_off_before': 10,
                'store_lo_temp': 15,
                'store_hi_temp': 25,
            },
        )
        mock_grocery_depots.add_depot(depot)
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        headers=conftest.DEFAULT_HEADERS,
        json={'wms_depot_id': depot.id_wms, 'product_ids': [product.id_wms]},
    )
    assert response.status_code == 200
    assert len(response.json()['products']) == 1
    product = response.json()['products'][0]
    traits = product['data']['storage']['traits']
    assert traits == [
        {
            'id': 'condition',
            'title': 'Safe conditions',
            'value': 'between 15C˚ and 25C˚',
        },
        {'id': 'shelf_life', 'title': 'Good before', 'value': '365 days'},
        {
            'id': 'write_off_before',
            'title': 'Write off before',
            'value': '10 days',
        },
    ]


async def test_product_measurements(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    measurements = {
        'width': 10,
        'height': 20,
        'depth': 30,
        'gross_weight': 500,
        'net_weight': 480,
    }

    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=100)
        product = category.add_product(product_id=1, measurements=measurements)
        mock_grocery_depots.add_depot(depot)
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        headers=conftest.DEFAULT_HEADERS,
        json={'wms_depot_id': depot.id_wms, 'product_ids': [product.id_wms]},
    )
    assert response.status_code == 200
    assert len(response.json()['products']) == 1
    product = response.json()['products'][0]
    response_measurements = product['data']['measurements']
    assert response_measurements == measurements


@pytest.mark.parametrize(
    'photo_stickers', [['hot', 'defrost', 'justBaked'], [], None],
)
async def test_photo_stickers(
        taxi_overlord_catalog,
        overlord_db,
        mock_grocery_depots,
        photo_stickers,
):
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=100)
        product = category.add_product(
            product_id=1, photo_stickers=photo_stickers,
        )
        mock_grocery_depots.add_depot(depot)
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products',
        headers=conftest.DEFAULT_HEADERS,
        json={'wms_depot_id': depot.id_wms, 'product_ids': [product.id_wms]},
    )
    assert response.status_code == 200
    assert len(response.json()['products']) == 1
    product_data = response.json()['products'][0]['data']
    if photo_stickers is not None and photo_stickers:
        assert product_data['photo_stickers'] == photo_stickers
    else:
        assert 'photo_stickers' not in product_data
