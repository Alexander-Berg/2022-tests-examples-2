import pytest

from testsuite.utils import ordered_object

OVERLORD_CATALOG_REGION_IDS_CONFIG = pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213, 2]},
    ],
)


@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_products_search(taxi_overlord_catalog, load_json):
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search',
        json=load_json('products_request_data.json'),
    )
    expected_json = load_json('products_expected_response.json')
    ordered_object.assert_eq(
        response.json(), expected_json, ['result.categories'],
    )


@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_products_search_suggest_get_all(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search/suggest', json={},
    )
    assert response.status_code == 200
    assert len(response.json()['result']) == 152


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
@OVERLORD_CATALOG_REGION_IDS_CONFIG
@pytest.mark.parametrize(
    'filter_type, filter_data, status, count',
    [
        ('country', 'RUS', 200, 155),
        ('country', 'no such country', 404, 0),
        ('region_id', '213', 200, 152),
        ('region_id', '2', 200, 3),
        ('region_id', '999999999', 404, 0),
        ('region_id', 'bad request', 400, 0),
        ('depot_id', 'aab8a6fbcee34b38b5281d8ea6ef749a000100010000', 200, 152),
        ('depot_id', '87840', 200, 152),
        ('depot_id', 'test-depot-id', 200, 3),
        ('depot_id', 'no such depot', 404, 0),
    ],
)
async def test_products_search_suggest_filters_and_empty_str(
        taxi_overlord_catalog,
        filter_type,
        filter_data,
        status,
        count,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search/suggest',
        json={'filter_type': filter_type, 'filter_data': filter_data},
    )
    assert response.status_code == status
    if status == 200:
        assert len(response.json()['result']) == count


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.parametrize(
    'part, count, search_type',
    [
        ('ала', 4, 'title'),
        ('клубника', 2, 'title'),
        ('not found', 0, 'title'),
        ('88b4b', 12, 'product_id'),
        ('bed45', 2, 'product_id'),
        ('not found', 0, 'product_id'),
    ],
)
async def test_products_search_suggest_str_and_empty_filter(
        taxi_overlord_catalog, part, count, search_type,
):
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search/suggest', json={'part': part},
    )
    assert response.status_code == 200
    assert len(response.json()['result']) == count
    for item in response.json()['result']:
        assert part in item[search_type]


@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_products_search_suggest_by_external_id(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search/suggest', json={'part': '2141'},
    )
    response_json = {
        'categories': ['38c15a3c-38f4-400a-a0a3-2d48dca49b40'],
        'product_id': 'fd11cadf-877e-11e9-b7ff-ac1f6b8569b3',
        'status': 'active',
        'title': 'Сэндвич овощи гриль-лосось «Братья Караваевы»',
    }

    assert response.status_code == 200
    assert len(response.json()['result']) == 1
    assert response.json()['result'][0] == response_json


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'default.sql',
        'refresh_wms_views.sql',
    ],
)
@OVERLORD_CATALOG_REGION_IDS_CONFIG
@pytest.mark.parametrize(
    'filter_type, filter_data, count',
    [
        ('country', 'RUS', 1),
        ('region_id', '213', 0),
        ('region_id', '2', 1),
        ('depot_id', 'aab8a6fbcee34b38b5281d8ea6ef749a000100010000', 0),
        ('depot_id', '87840', 0),
        ('depot_id', 'test-depot-id', 1),
    ],
)
@pytest.mark.parametrize(
    'part, title',
    [
        ('Товар 1', 'Товар 1'),
        ('Товар 3', 'Товар 3'),
        ('1234', 'Товар 1'),
        ('d36ff36d-cb3c-11e9-b7ff-000000000003', 'Товар 3'),
    ],
)
async def test_products_search_suggest_filter_and_str(
        taxi_overlord_catalog,
        filter_type,
        filter_data,
        count,
        part,
        title,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/products/v1/search/suggest',
        json={
            'filter_type': filter_type,
            'filter_data': filter_data,
            'part': part,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['result']) == count
    if count:
        assert response.json()['result'][0]['title'] == title


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
async def test_categories_search_root_get_all(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        ['gdepots-depots-default.json'], ['gdepots-zones-default.json'],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root', json={},
    )

    result = {
        'result': [
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-000000000001',
                'depot_ids': ['test-depot-id'],
                'store_ids': ['123456789'],
                'status': 'active',
                'title': 'Корень 2',
                'type': 'FRONT',
            },
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'depot_ids': [],
                'store_ids': [],
                'status': 'active',
                'title': 'Корень 1',
                'type': 'FRONT',
            },
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), result, ['result.category_id'])


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
@pytest.mark.parametrize(
    'ids, inds',
    [
        (['d9ef3613-c0ed-40d2-9fdc-000000000001'], [0]),
        (['d9ef3613-c0ed-40d2-9fdc-3eed67f55aae'], [1]),
        (['bad_id'], [2]),
        (
            [
                'd9ef3613-c0ed-40d2-9fdc-000000000001',
                'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'bad_id',
                '61d24b27-0e8e-4173-a861-000000000002',
            ],
            [0, 1, 2, 3],
        ),
    ],
)
async def test_categories_search_root_get_by_ids(
        taxi_overlord_catalog, ids, inds, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        ['gdepots-depots-default.json'], ['gdepots-zones-default.json'],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root',
        json={'filter_type': 'root_ids', 'root_ids': ids},
    )

    items = [
        {
            'category_id': 'd9ef3613-c0ed-40d2-9fdc-000000000001',
            'depot_ids': ['test-depot-id'],
            'store_ids': ['123456789'],
            'status': 'active',
            'title': 'Корень 2',
            'type': 'FRONT',
        },
        {
            'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
            'depot_ids': [],
            'store_ids': [],
            'status': 'active',
            'title': 'Корень 1',
            'type': 'FRONT',
        },
        {
            'category_id': 'bad_id',
            'depot_ids': [],
            'store_ids': [],
            'status': 'not_found',
            'title': 'Root category not found',
            'type': 'FRONT',
        },
        {
            'category_id': '61d24b27-0e8e-4173-a861-000000000002',
            'depot_ids': [],
            'store_ids': [],
            'status': 'not_found',
            'title': 'Category is not root',
            'type': 'FRONT',
        },
    ]

    result = {'result': [items[i] for i in inds]}

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), result, ['result.category_id'])


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'default.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213, 2, 999]},
    ],
)
@pytest.mark.parametrize(
    'country, status', [('RUS', 200), ('No such country', 404)],
)
async def test_categories_search_root_get_by_country(
        taxi_overlord_catalog, country, status, mock_grocery_depots,
):
    """ Checks /admin/categories/v1/search/root POST return
    root categories in |country|, should return 200 on valid country and
    ignore regions without any depots in it """
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root',
        json={'filter_type': 'country', 'country': country},
    )
    assert response.status_code == status
    if status == 200:
        result = {
            'result': [
                {
                    'category_id': 'd9ef3613-c0ed-40d2-9fdc-000000000001',
                    'depot_ids': ['test-depot-id'],
                    'store_ids': ['123456789'],
                    'status': 'active',
                    'title': 'Корень 2',
                    'type': 'FRONT',
                },
                {
                    'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'depot_ids': [
                        'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
                        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
                    ],
                    'store_ids': ['87840', '90213'],
                    'status': 'active',
                    'title': 'Корень 1',
                    'type': 'FRONT',
                },
            ],
        }
        ordered_object.assert_eq(
            response.json(),
            result,
            ['result', 'result.depot_ids', 'result.store_ids'],
        )


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'default.sql',
        'refresh_wms_views.sql',
    ],
)
@OVERLORD_CATALOG_REGION_IDS_CONFIG
@pytest.mark.parametrize(
    'region_id, status, idx', [(213, 200, 1), (2, 200, 0), (999, 404, None)],
)
async def test_categories_search_root_get_by_region_id(
        taxi_overlord_catalog, region_id, status, idx, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root',
        json={'filter_type': 'region_id', 'region_id': region_id},
    )
    assert response.status_code == status
    if status == 200:
        items = [
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-000000000001',
                'depot_ids': ['test-depot-id'],
                'store_ids': ['123456789'],
                'status': 'active',
                'title': 'Корень 2',
                'type': 'FRONT',
            },
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'depot_ids': [
                    'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
                    'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
                ],
                'store_ids': ['87840', '90213'],
                'status': 'active',
                'title': 'Корень 1',
                'type': 'FRONT',
            },
        ]
        result = {'result': [items[idx]]}
        ordered_object.assert_eq(
            response.json(),
            result,
            ['result', 'result.depot_ids', 'result.store_ids'],
        )


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'default.sql',
        'refresh_wms_views.sql',
    ],
)
@OVERLORD_CATALOG_REGION_IDS_CONFIG
@pytest.mark.parametrize(
    'depot_id, status, idx',
    [
        ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000', 200, 1),
        ('90213', 200, 1),
        ('test-depot-id', 200, 0),
        ('No such depot', 404, None),
    ],
)
async def test_categories_search_root_get_by_depot_id(
        taxi_overlord_catalog, depot_id, status, idx, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root',
        json={'filter_type': 'depot_id', 'depot_id': depot_id},
    )
    assert response.status_code == status
    if status == 200:
        items = [
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-000000000001',
                'depot_ids': ['test-depot-id'],
                'store_ids': ['123456789'],
                'status': 'active',
                'title': 'Корень 2',
                'type': 'FRONT',
            },
            {
                'category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'depot_ids': [
                    'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
                    'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
                ],
                'store_ids': ['87840', '90213'],
                'status': 'active',
                'title': 'Корень 1',
                'type': 'FRONT',
            },
        ]
        result = {'result': [items[idx]]}
        ordered_object.assert_eq(
            response.json(),
            result,
            ['result', 'result.depot_ids', 'result.store_ids'],
        )


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
@pytest.mark.parametrize(
    'root_id, status, count',
    [
        ('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 200, 441),
        ('d9ef3613-c0ed-40d2-9fdc-000000000001', 200, 2),
        ('61d24b27-0e8e-4173-a861-95c87802972f', 404, 0),
    ],
)
async def test_categories_search_suggest_get_all_subcategories(
        taxi_overlord_catalog, root_id, status, count,
):
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/suggest', json={'root_id': root_id},
    )
    assert response.status_code == status
    if status == 200:
        assert len(response.json()['result']) == count


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
@pytest.mark.parametrize(
    'root_id, part, count',
    [
        ('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'Сала', 2),
        ('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', '95d6e4', 1),
        ('d9ef3613-c0ed-40d2-9fdc-000000000001', 'категория 1', 1),
        ('d9ef3613-c0ed-40d2-9fdc-000000000001', '61d24b2', 1),
    ],
)
async def test_categories_search_suggest_subcategories_by_str(
        taxi_overlord_catalog, root_id, part, count,
):
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/suggest',
        json={'root_id': root_id, 'part': part},
    )
    assert response.status_code == 200
    assert len(response.json()['result']) == count


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['wms_menu_data.sql', 'default.sql', 'refresh_wms_views.sql'],
)
async def test_categories_search_suggest_subcategories_data(
        taxi_overlord_catalog,
):
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/suggest',
        json={
            'root_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
            'part': 'Консервы',
        },
    )

    result = {
        'result': [
            {
                'category_id': '836ef54b-58c0-43be-a3ff-8a2eaadd9afa',
                'root_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'parent_id': '0c1e6ad8-1e85-47b8-97b0-f9b5744af651',
                'title': 'Консервы рыбные',
                'status': 'active',
            },
            {
                'category_id': 'ea028766-1f26-4df6-b854-94bdcd7a402f',
                'root_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                'parent_id': '0c1e6ad8-1e85-47b8-97b0-f9b5744af651',
                'title': 'Консервы',
                'status': 'active',
            },
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), result, ['result'])


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'wms_menu_data.sql',
        'set_categories_status.sql',
        'refresh_wms_views.sql',
    ],
)
async def test_categories_search(taxi_overlord_catalog, load_json):
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search',
        json=load_json('categories_request_data.json'),
    )
    assert response.json() == load_json('categories_expected_response.json')


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'master_categories.sql',
        'wms_menu_data.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213, 2]},
        {'country_id': 181, 'region_ids': [131]},
    ],
)
@pytest.mark.parametrize(
    'country_iso2,country_iso3,request_type,request_value',
    [
        ('RU', 'RUS', 'region_id', 213),
        ('RU', 'RUS', 'depot_id', '90213'),
        ('IL', 'ISR', 'region_id', 131),
        ('IL', 'ISR', 'depot_id', '90213'),
        ('GB', 'GBR', 'region_id', 10393),
    ],
)
async def test_master_categories(
        taxi_overlord_catalog,
        mock_grocery_depots,
        request_type,
        request_value,
        country_iso2,
        country_iso3,
):
    mock_grocery_depots.load_json(
        [
            'gdepots-depots-default.json',
            'gdepots-depots-catalog_wms_test_depots.json',
        ],
        [
            'gdepots-zones-default.json',
            'gdepots-zones-catalog_wms_test_depots.json',
        ],
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    **(
                        {'region_id': request_value}
                        if request_type == 'region_id'
                        else {}
                    ),
                    'country_iso2': country_iso2,
                    'country_iso3': country_iso3,
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.post(
        '/admin/categories/v1/search/root',
        json={'filter_type': request_type, request_type: request_value},
    )
    categories = response.json()['result']

    find_category = (
        category['category_id']
        for category in categories
        if category['type'] == 'MASTER'
    )

    if country_iso2 == 'GB':
        assert not any(find_category)
    else:
        master_category = next(find_category)
        assert master_category == f'master-{country_iso2}'
