import pytest

HANDLER_UNTYPED_PRODUCTS = '/v1/manage/products/get_untyped'

BRAND_ID = 1
MOCK_NOW = '2021-09-30T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_search_untyped_products(
        product_search_test_utils, taxi_eats_nomenclature,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER_UNTYPED_PRODUCTS, json={'brand_id': BRAND_ID},
    )
    assert response.status_code == 200
    expected_response = {
        'products': [
            {
                'id': '00000000-0000-0000-0000-000000000013',
                'measure': '8 л',
                'name': 'is_catch_weight_true',
                'origin_id': 'origin_13',
            },
            {
                'id': '33333333-3333-3333-3333-333333333333',
                'name': 'null_product_type',
                'origin_id': 'origin_3',
                'picture_url': 'processed_url_4',
            },
            {
                'id': '55555555-5555-5555-5555-555555555555',
                'name': 'no_product_type',
                'origin_id': 'origin_5',
            },
            {
                'id': '66666666-6666-6666-6666-666666666666',
                'name': 'disabled_place_with_no_type',
                'origin_id': 'origin_6',
            },
            {
                'id': '00000000-0000-0000-0000-000000000008',
                'name': 'overriden_with_sku_has_no_type',
                'origin_id': 'origin_8',
                'sku_id': '00000000-0000-0000-0000-000000000005',
            },
            {
                'id': '00000000-0000-0000-0000-000000000009',
                'name': 'overriden_with_null_sku_has_no_type',
                'origin_id': 'origin_9',
            },
            {
                'id': '00000000-0000-0000-0000-000000000011',
                'name': 'sku_with_null_product_type',
                'origin_id': 'origin_11',
                'sku_id': '00000000-0000-0000-0000-000000000006',
            },
        ],
        'limit': 100,
        'cursor': 'MTM=',
    }
    assert product_search_test_utils.sorted_response(
        response.json(),
    ) == product_search_test_utils.sorted_response(expected_response)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('limit', [1, 2])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_cursor_limit(
        limit, product_search_test_utils, taxi_eats_nomenclature,
):
    cursor = None
    start_idx = 0
    end_idx = limit

    while True:
        print(f'Current start index: {start_idx}')

        response = await taxi_eats_nomenclature.post(
            HANDLER_UNTYPED_PRODUCTS,
            json={'brand_id': BRAND_ID, 'limit': limit, 'cursor': cursor},
        )
        assert response.status_code == 200

        response_json = response.json()
        expected_json = product_search_test_utils.generate_expected_json(
            start_idx=start_idx,
            end_idx=end_idx,
            expected_limit=limit,
            current_cursor=cursor,
        )
        assert product_search_test_utils.sorted_response(
            response_json,
        ) == product_search_test_utils.sorted_response(expected_json)

        cursor = response_json['cursor']
        start_idx = end_idx
        end_idx += limit

        if len(expected_json['products']) < limit:
            break


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_categories_path.sql'],
)
@pytest.mark.parametrize(
    'enable_brand_to_show_categories_in_admin', [True, False],
)
async def test_categories_path(
        product_search_test_utils,
        taxi_eats_nomenclature,
        # parametrize
        enable_brand_to_show_categories_in_admin,
):
    if enable_brand_to_show_categories_in_admin:
        product_search_test_utils.set_brands_to_show_categories_in_admin(
            [BRAND_ID],
        )

    response = await taxi_eats_nomenclature.post(
        HANDLER_UNTYPED_PRODUCTS, json={'brand_id': BRAND_ID},
    )
    assert response.status_code == 200

    if enable_brand_to_show_categories_in_admin:
        # first product has no category,
        # second has only one category,
        # third has path with two categories
        expected_categories_paths = [
            [],
            ['Корневая категория 2'],
            ['Корневая категория 1', 'Подкатегория 11'],
        ]
    else:
        expected_categories_paths = [[], [], []]

    assert (
        product_search_test_utils.extract_categories_paths_from_response(
            product_search_test_utils.sorted_response(response.json()),
        )
        == expected_categories_paths
    )
