import pytest

HANDLER = '/v1/place/category_products/filtered'

CATEGORY_ID = '11'
BRAND_ID = 1
PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
FILTER_TYPE = 'multiselect'
SKU_ID_1 = 1
SKU_ID_2 = 2
SKU_ID_3 = 3
SKU_ID_4 = 4
SKU_ID_5 = 5


@pytest.mark.parametrize('filter_id', ['fat_content', 'volume'])
@pytest.mark.parametrize(
    'config_ranges, items_to_fill, expected_filter_values',
    [
        pytest.param(
            {
                '0-1.99': {'from': '0', 'to': '2'},
                '2-5': {'from': '2', 'to': '5'},
            },
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
                (SKU_ID_5, '6'),
            ],
            [
                {'value': '0-1.99', 'items_count': 2, 'sort_order': 1},
                {'value': '2-5', 'items_count': 2, 'sort_order': 2},
            ],
        ),
        pytest.param(
            {
                '0-1.99': {'from': '0', 'to': '2'},
                '2-5': {'from': '2', 'to': '5'},
            },
            [(SKU_ID_1, '1'), (SKU_ID_2, '1')],
            [{'value': '0-1.99', 'items_count': 2, 'sort_order': 1}],
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_response_range_mapping(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        filter_id,
        config_ranges,
        items_to_fill,
        expected_filter_values,
):
    filter_name = 'Фильтр'

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            CATEGORY_ID: {
                'default_category_settings': {
                    filter_id: {'ranges': config_ranges},
                },
            },
        },
    )

    sql_set_sku_product_attribute(filter_id, items_to_fill)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == 1
    assert response_filters[0]['values'] == expected_filter_values


@pytest.mark.parametrize('filter_id', ['fat_content', 'volume'])
@pytest.mark.parametrize(
    'config_ranges, config_sort_order, items_to_fill, expected_filter_values',
    [
        pytest.param(
            {
                'Меньше': {'from': '0', 'to': '2'},
                'Больше': {'from': '2', 'to': '5'},
            },
            None,
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
            ],
            [
                {'value': 'Больше', 'items_count': 2, 'sort_order': 1},
                {'value': 'Меньше', 'items_count': 2, 'sort_order': 2},
            ],
            id='sort_in_lexigraphical_order',
        ),
        pytest.param(
            {
                'Меньше': {'from': '0', 'to': '2'},
                'Больше': {'from': '2', 'to': '5'},
            },
            [
                {'value': 'Меньше', 'sort_order': 1},
                {'value': 'Больше', 'sort_order': 2},
            ],
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
            ],
            [
                {'value': 'Меньше', 'items_count': 2, 'sort_order': 1},
                {'value': 'Больше', 'items_count': 2, 'sort_order': 2},
            ],
            id='sort_by_config',
        ),
        pytest.param(
            {
                'Меньше': {'from': '0', 'to': '2'},
                'Больше': {'from': '2', 'to': '5'},
            },
            [
                {'value': 'Меньше', 'sort_order': 1},
                {'value': 'Больше', 'sort_order': 2},
            ],
            [(SKU_ID_1, '0'), (SKU_ID_2, '1'), (SKU_ID_3, '2')],
            [
                {'value': 'Меньше', 'items_count': 2, 'sort_order': 1},
                {'value': 'Больше', 'items_count': 1, 'sort_order': 2},
            ],
            id='sort_by_config',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_response_ranges_sorting(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        filter_id,
        config_ranges,
        config_sort_order,
        items_to_fill,
        expected_filter_values,
):
    filter_name = 'Фильтр'

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                filter_id: {'name': filter_name, 'values': config_sort_order},
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            CATEGORY_ID: {
                'default_category_settings': {
                    filter_id: {'ranges': config_ranges},
                },
            },
        },
    )

    sql_set_sku_product_attribute(filter_id, items_to_fill)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == 1
    assert response_filters[0]['values'] == expected_filter_values


@pytest.mark.parametrize('filter_id', ['fat_content', 'volume'])
@pytest.mark.parametrize(
    'config_ranges, items_to_fill, request_filters, expected_product_ids',
    [
        pytest.param(
            {
                '0-1.99': {'from': '0', 'to': '2'},
                '2-5': {'from': '2', 'to': '5'},
            },
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
                (SKU_ID_5, '6'),
            ],
            [{'type': 'multiselect', 'chosen_options': ['2-5']}],
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            ],
        ),
        pytest.param(
            {
                '0-1.99': {'from': '0', 'to': '2'},
                '2-5': {'from': '2', 'to': '5'},
            },
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
                (SKU_ID_5, '6'),
            ],
            [{'type': 'multiselect', 'chosen_options': ['0-1.99']}],
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            ],
        ),
        pytest.param(
            {
                '0-1.99': {'from': '0', 'to': '2'},
                '2-5': {'from': '2', 'to': '5'},
            },
            [
                (SKU_ID_1, '0'),
                (SKU_ID_2, '1'),
                (SKU_ID_3, '2'),
                (SKU_ID_4, '2.5'),
                (SKU_ID_5, '6'),
            ],
            [{'type': 'multiselect', 'chosen_options': ['0-1.99', '2-5']}],
            [
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filter_with_ranges(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        filter_id,
        config_ranges,
        items_to_fill,
        request_filters,
        expected_product_ids,
):
    filter_name = 'Фильтр'
    for request_filter in request_filters:
        request_filter['id'] = filter_id

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            CATEGORY_ID: {
                'default_category_settings': {
                    filter_id: {'ranges': config_ranges},
                },
            },
        },
    )

    sql_set_sku_product_attribute(filter_id, items_to_fill)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(
        request, json={'filters': request_filters},
    )
    assert response.status == 200
    assert expected_product_ids == extract_product_ids_from_response(
        response.json(),
    )


def extract_filters_from_response(response):
    assert len(response['categories']) == 1
    category = response['categories'][0]
    category['filters'].sort(key=lambda filter: filter['id'])
    return category['filters']


def extract_product_ids_from_response(response):  # pylint: disable=C0103
    assert len(response['categories']) == 1
    return [product['id'] for product in response['categories'][0]['products']]
