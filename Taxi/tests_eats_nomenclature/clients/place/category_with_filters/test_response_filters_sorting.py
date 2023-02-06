import pytest

HANDLER = '/v1/place/category_products/filtered'

CATEGORY_ID = '11'
PLACE_ID = 1
BRAND_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
FILTER_TYPE = 'multiselect'


@pytest.mark.parametrize(
    'id_with_value, expected_order, config_sort_order, filters',
    [
        pytest.param(
            [
                (1, 'Коровье'),
                (2, 'Верблюжье'),
                (3, 'Коровье'),
                (4, 'Ослиное'),
                (5, 'Ослиное'),
                (6, 'Ослиное'),
            ],
            [
                {'value': 'Ослиное', 'items_count': 3, 'sort_order': 1},
                {'value': 'Коровье', 'items_count': 2, 'sort_order': 2},
                {'value': 'Верблюжье', 'items_count': 1, 'sort_order': 3},
            ],
            None,
            [],
            id='sort_by_items_count',
        ),
        pytest.param(
            [
                (1, 'Коровье'),
                (2, 'Верблюжье'),
                (3, 'Коровье'),
                (4, 'Ослиное'),
                (5, 'Ослиное'),
                (6, 'Ослиное'),
            ],
            [
                {'value': 'Ослиное', 'items_count': 3, 'sort_order': 1},
                {'value': 'Коровье', 'items_count': 2, 'sort_order': 2},
                {'value': 'Верблюжье', 'items_count': 1, 'sort_order': 3},
            ],
            None,
            [
                {
                    'id': 'milk_type',
                    'type': 'multiselect',
                    'chosen_options': ['Верблюжье'],
                },
            ],
            id='sort_by_items_count_with_filtered_items',
        ),
        pytest.param(
            [
                (1, 'Коровье'),
                (2, 'Козлиное'),
                (3, 'Коровье'),
                (4, 'Козлиное'),
                (5, 'Крысиное'),
                (6, 'Крысиное'),
            ],
            [
                {'value': 'Козлиное', 'items_count': 2, 'sort_order': 1},
                {'value': 'Коровье', 'items_count': 2, 'sort_order': 2},
                {'value': 'Крысиное', 'items_count': 2, 'sort_order': 3},
            ],
            None,
            [],
            id='sort_by_items_count_and_name',
        ),
        pytest.param(
            [(1, 'Коровье'), (2, 'Ослиное'), (3, 'Козлиное')],
            [
                {'value': 'Козлиное', 'items_count': 1, 'sort_order': 3},
                {'value': 'Коровье', 'items_count': 1, 'sort_order': 2},
                {'value': 'Ослиное', 'items_count': 1, 'sort_order': 1},
            ],
            [
                {'value': 'Ослиное', 'sort_order': 1},
                {'value': 'Коровье', 'sort_order': 2},
                {'value': 'Козлиное', 'sort_order': 3},
            ],
            [],
            id='sort_by_config',
        ),
        pytest.param(
            [
                (1, 'Коровье'),
                (2, 'Козлиное'),
                (3, 'Коровье'),
                (4, 'Ослиное'),
                (5, 'Ослиное'),
                (6, 'Крысиное'),
            ],
            [
                {'value': 'Козлиное', 'items_count': 1, 'sort_order': 1},
                {'value': 'Ослиное', 'items_count': 2, 'sort_order': 2},
                {'value': 'Коровье', 'items_count': 2, 'sort_order': 3},
                {'value': 'Крысиное', 'items_count': 1, 'sort_order': 4},
            ],
            [
                {'value': 'Козлиное', 'sort_order': 1},
                {'value': 'Ослиное', 'sort_order': 2},
            ],
            [],
            id='sort_by_config_and_items_count',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_options_sorting(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        id_with_value,
        expected_order,
        config_sort_order,
        filters,
):
    filter_id = 'milk_type'
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                filter_id: {'name': 'Тип молока', 'values': config_sort_order},
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )

    sql_set_sku_product_attribute(filter_id, id_with_value)
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'
        '&include_products=false'
    )

    response = await taxi_eats_nomenclature.post(
        request, json={'filters': filters},
    )
    assert response.status == 200

    response_json = response.json()
    response_filters = extract_filters_from_response(response_json)

    assert len(response_filters) == 1
    response_filters[0]['values'].sort(key=lambda item: item['sort_order'])
    expected_order.sort(key=lambda item: item['sort_order'])
    assert response_filters[0]['values'] == expected_order


@pytest.mark.parametrize(
    'product_attributes, expected_order, category_settings, '
    'category_brand_settings',
    [
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [(1, 'Клубничное'), (2, 'Шоколадное')],
                'fat_content': [(1, '3.2')],
            },
            [
                {'id': 'milk_type', 'sort_order': 1},
                {'id': 'flavour', 'sort_order': 2},
                {'id': 'fat_content', 'sort_order': 3},
            ],
            {'milk_type': {}, 'flavour': {}, 'fat_content': {}},
            None,
            id='sort_by_items_count',
        ),
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [
                    (1, 'Клубничное'),
                    (2, 'Шоколадное'),
                    (3, 'Ванильное'),
                ],
                'fat_content': [(1, '3.2'), (2, '2.5'), (3, '6.0')],
            },
            [
                {'id': 'milk_type', 'sort_order': 3},
                {'id': 'flavour', 'sort_order': 2},
                {'id': 'fat_content', 'sort_order': 1},
            ],
            {'milk_type': {}, 'flavour': {}, 'fat_content': {}},
            None,
            id='sort_by_items_count_and_id',
        ),
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [
                    (1, 'Клубничное'),
                    (2, 'Шоколадное'),
                    (3, 'Ванильное'),
                ],
                'fat_content': [(1, '3.2'), (2, '2.5'), (3, '6.0')],
            },
            [
                {'id': 'milk_type', 'sort_order': 1},
                {'id': 'flavour', 'sort_order': 3},
                {'id': 'fat_content', 'sort_order': 2},
            ],
            {
                'milk_type': {'sort_order': 1},
                'flavour': {'sort_order': 3},
                'fat_content': {'sort_order': 2},
            },
            None,
            id='sort_by_category_config',
        ),
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [
                    (1, 'Клубничное'),
                    (2, 'Шоколадное'),
                    (3, 'Ванильное'),
                ],
                'fat_content': [(1, '3.2'), (2, '2.5'), (3, '6.0')],
            },
            [
                {'id': 'milk_type', 'sort_order': 2},
                {'id': 'flavour', 'sort_order': 1},
                {'id': 'fat_content', 'sort_order': 3},
            ],
            {
                'milk_type': {'sort_order': 1},
                'flavour': {'sort_order': 3},
                'fat_content': {'sort_order': 2},
            },
            {
                'milk_type': {'sort_order': 2},
                'flavour': {'sort_order': 1},
                'fat_content': {'sort_order': 3},
            },
            id='sort_by_category_brand_config',
        ),
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [
                    (1, 'Клубничное'),
                    (2, 'Шоколадное'),
                    (3, 'Ванильное'),
                ],
                'fat_content': [(1, '3.2'), (2, '2.5'), (3, '6.0')],
            },
            [
                {'id': 'milk_type', 'sort_order': 1},
                {'id': 'flavour', 'sort_order': 2},
                {'id': 'fat_content', 'sort_order': 3},
            ],
            None,
            {
                'milk_type': {'sort_order': 1},
                'flavour': {'sort_order': 2},
                'fat_content': {'sort_order': 3},
            },
            id='sort_by_brand_config',
        ),
        pytest.param(
            {
                'milk_type': [
                    (1, 'Коровье'),
                    (2, 'Козлиное'),
                    (3, 'Крысиное'),
                ],
                'flavour': [
                    (1, 'Клубничное'),
                    (2, 'Шоколадное'),
                    (3, 'Ванильное'),
                    (4, 'Ванильное'),
                ],
                'fat_content': [(1, '3.2'), (2, '2.5'), (3, '6.0')],
            },
            [
                {'id': 'milk_type', 'sort_order': 1},
                {'id': 'flavour', 'sort_order': 2},
                {'id': 'fat_content', 'sort_order': 3},
            ],
            {'milk_type': {'sort_order': 3}, 'flavour': {}, 'fat_content': {}},
            None,
            id='sort_by_config_and_items_count',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filters_sorting(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        product_attributes,
        expected_order,
        category_settings,
        category_brand_settings,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                'milk_type': {'name': 'Тип молока'},
                'flavour': {'name': 'Вкус'},
                'fat_content': {'name': 'Жирность'},
            },
        },
    )
    category_brand_config = {'default_category_settings': category_settings}
    if category_brand_settings:
        category_brand_config[BRAND_ID] = category_brand_settings
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {CATEGORY_ID: category_brand_config},
    )

    sql_set_sku_product_attribute('milk_type', product_attributes['milk_type'])
    sql_set_sku_product_attribute('flavour', product_attributes['flavour'])
    sql_set_sku_product_attribute(
        'fat_content', product_attributes['fat_content'],
    )

    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'
        '&include_products=false'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    response_filters = extract_filters_from_response(response_json)

    assert len(response_filters) == len(product_attributes.keys())
    filter_id_and_sort_order = [
        {'id': item['id'], 'sort_order': item['sort_order']}
        for item in response_filters
    ]

    filter_id_and_sort_order.sort(key=lambda item: item['sort_order'])
    expected_order.sort(key=lambda item: item['sort_order'])
    assert expected_order == filter_id_and_sort_order


def extract_filters_from_response(response):
    assert len(response['categories']) == 1
    category = response['categories'][0]
    category['filters'].sort(key=lambda filter: filter['id'])
    return category['filters']
