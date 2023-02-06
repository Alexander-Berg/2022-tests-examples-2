import pytest


@pytest.mark.pgsql(
    'overlord_catalog', files=['default_wms.sql', 'refresh_wms_views.sql'],
)
async def test_nomenclature_data_from_wms(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default_wms.json', 'gdepots-zones-default_wms.json',
    )
    response = await taxi_overlord_catalog.get(
        '/internal/v1/catalog/v1/nomenclature-data',
        params={'limit': 100, 'cursor': ''},
    )
    assert response.status_code == 200
    _assert_eq(
        response.json()['categories'],
        [
            {
                'id': '73fa0267-8519-485a-9e06-5e18a9a7514c',
                'name': 'Завтрак',
                'region_ids': [111, 222],
            },
            {
                'id': '61d24b27-0e8e-4173-a861-95c87802972f',
                'name': 'Яйца',
                'region_ids': [111, 222],
            },
        ],
    )

    _assert_eq(
        response.json()['products'],
        [
            {
                'id': '0326d831-877f-11e9-b7ff-ac1f6b8569b3',
                'name': 'Багет',
                'region_ids': [111, 222],
            },
            {
                'id': '941a2f7f-77ff-11e9-b7ff-ac1f6b8566c7',
                'name': 'Twinings Lady Grey',
                'region_ids': [111, 222],
            },
        ],
    )


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['product_in_several_root.sql', 'refresh_wms_views.sql'],
)
async def test_product_in_several_roots(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-product_in_several_root.json',
        'gdepots-zones-product_in_several_root.json',
    )
    response = await taxi_overlord_catalog.get(
        '/internal/v1/catalog/v1/nomenclature-data',
        params={'limit': 100, 'cursor': ''},
    )
    assert response.status_code == 200
    _assert_eq(
        response.json()['categories'],
        [
            {
                'id': '73fa0267-8519-485a-9e06-5e18a9a7514b',
                'name': 'Завтрак - 2',
                'region_ids': [222],
            },
            {
                'id': '73fa0267-8519-485a-9e06-5e18a9a7514c',
                'name': 'Завтрак - 1',
                'region_ids': [111],
            },
        ],
    )

    _assert_eq(
        response.json()['products'],
        [
            {
                'id': '0326d831-877f-11e9-b7ff-ac1f6b8569b3',
                'name': 'Багет',
                'region_ids': [111, 222],
            },
        ],
    )


@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'wms_generate_stocks.sql',
        'refresh_wms_views.sql',
    ],
)
async def test_nomenclature_data_from_wms_chunked(
        taxi_overlord_catalog, load_json, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
        replace_at_depots=[
            [
                {},
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
    response_len = [150, 150, 141, 0]
    products = []
    categories = []
    limit = 150
    cursor = ''
    for length in response_len:
        response = await taxi_overlord_catalog.get(
            '/internal/v1/catalog/v1/nomenclature-data',
            params={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        cursor = response.json()['cursor']
        products_len = len(response.json()['products'])
        categories_len = len(response.json()['categories'])
        assert max(products_len, categories_len) == length
        products.extend(response.json()['products'])
        categories.extend(response.json()['categories'])

    answer = load_json('chunk_answer.json')
    _assert_eq(products, answer['products'])
    _assert_eq(categories, answer['categories'])
    # > select count(*) from catalog_wms.goods;
    #  count
    # -------
    #    152
    # (1 row)
    assert len(products) == 152

    # > select count(*) from catalog_wms.categories;
    #  count
    # -------
    #    442
    # (1 row)
    assert len(categories) == 441  # -1 is root category


def _assert_eq(first_list, second_list):
    assert len(first_list) == len(second_list)
    for item in first_list:
        for key, value in item.items():
            if isinstance(value, list):
                item[key] = sorted(value)
        assert item in second_list
