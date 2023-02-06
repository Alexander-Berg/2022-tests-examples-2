import pytest

HANDLER = '/v1/manage/products/search_by_type'

BRAND_ID = 1
NAME_PART = 'Тип'
MAX_LIMIT = 100
MOCK_NOW = '2021-09-30T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_empty_name_part(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'brand_id': BRAND_ID, 'product_type_name_part': ''},
    )
    assert response.status_code == 200
    assert response.json() == {'cursor': '', 'limit': 0, 'products': []}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_no_cursor_no_limit(
        product_search_test_utils, taxi_eats_nomenclature,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER,
        json={'brand_id': BRAND_ID, 'product_type_name_part': NAME_PART},
    )
    assert response.status_code == 200

    expected_json = product_search_test_utils.generate_expected_json(
        start_idx=0,
        end_idx=MAX_LIMIT,
        expected_limit=MAX_LIMIT,
        current_cursor=None,
    )
    assert product_search_test_utils.sorted_response(
        response.json(),
    ) == product_search_test_utils.sorted_response(expected_json)


@pytest.mark.parametrize('name_part', ['тип', 'Тип', 'ТИП', 'ти'])
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_search_type_with_different_letter_case(
        name_part, product_search_test_utils, taxi_eats_nomenclature,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER,
        json={'brand_id': BRAND_ID, 'product_type_name_part': name_part},
    )
    assert response.status_code == 200

    expected_json = product_search_test_utils.generate_expected_json(
        start_idx=0,
        end_idx=MAX_LIMIT,
        expected_limit=MAX_LIMIT,
        current_cursor=None,
    )
    assert product_search_test_utils.sorted_response(
        response.json(),
    ) == product_search_test_utils.sorted_response(expected_json)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_cursor_limit(
        limit, product_search_test_utils, taxi_eats_nomenclature,
):
    cursor = None
    start_idx = 0
    end_idx = limit
    last_response_products_count = -1

    while True:
        print(f'Current start index: {start_idx}')

        response = await taxi_eats_nomenclature.post(
            HANDLER,
            json={
                'brand_id': BRAND_ID,
                'product_type_name_part': NAME_PART,
                'limit': limit,
                'cursor': cursor,
            },
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

        # check that all responses except last one contain
        # limit number of items
        if last_response_products_count != -1:
            assert last_response_products_count == limit
        last_response_products_count = len(response_json['products'])

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
        HANDLER, json={'brand_id': BRAND_ID, 'product_type_name_part': 'Тип'},
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
