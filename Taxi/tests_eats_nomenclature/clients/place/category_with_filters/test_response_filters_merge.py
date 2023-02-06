import pytest

HANDLER = '/v1/place/category_products/filtered'

ROOT_CATEGORY_ID = '11'
CATEGORY_ID_1 = '22'
CATEGORY_ID_2 = '33'
CATEGORY_ID_1_1 = '44'
CATEGORIES_IDS = [
    ROOT_CATEGORY_ID,
    CATEGORY_ID_1,
    CATEGORY_ID_2,
    CATEGORY_ID_1_1,
]
SKU_ID_1 = 1
SKU_ID_2 = 2
SKU_ID_3 = 3
SKU_ID_4 = 4
SKU_ID_5 = 5
SKU_ID_6 = 6
PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
FILTER_TYPE = 'multiselect'


@pytest.mark.parametrize(
    'filter_id',
    [
        'fat_content',
        'milk_type',
        'cultivar',
        'flavour',
        'meat_type',
        'carcass_part',
        'egg_category',
        'country',
        'package_type',
        'volume',
        'brand',
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_merge_one_filter_same_values(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
):
    filter_name = 'Фильтр'
    values = [(SKU_ID_1, '11.1'), (SKU_ID_2, '11.1')]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_2: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1_1: {'default_category_settings': {filter_id: {}}},
        },
    )

    if filter_id == 'brand':
        sql_set_sku_brand([(SKU_ID_1, 1), (SKU_ID_2, 1)])
    else:
        sql_set_sku_product_attribute(filter_id, values)
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()

    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        assert len(category['filters']) == 1
        assert category['filters'][0]['id'] == filter_id
        assert category['filters'][0]['name'] == filter_name
        assert category['filters'][0]['type'] == FILTER_TYPE
        assert len(category['filters'][0]['values']) == 1
        assert category['filters'][0]['values'][0]['value'] == '11.1'
        assert category['filters'][0]['values'][0]['items_count'] == (
            2 if category['id'] == ROOT_CATEGORY_ID else 1
        )


@pytest.mark.parametrize(
    'filter_id',
    [
        'fat_content',
        'milk_type',
        'cultivar',
        'flavour',
        'meat_type',
        'carcass_part',
        'egg_category',
        'country',
        'package_type',
        'volume',
        'brand',
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_merge_one_filter_different_values(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
):
    filter_name = 'Фильтр'
    values = [(SKU_ID_1, '11.1'), (SKU_ID_2, '22.2')]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_2: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1_1: {'default_category_settings': {filter_id: {}}},
        },
    )

    if filter_id == 'brand':
        sql_set_sku_brand([(SKU_ID_1, 1), (SKU_ID_2, 2)])
    else:
        sql_set_sku_product_attribute(filter_id, values)
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        assert len(category['filters']) == 1
        assert category['filters'][0]['id'] == filter_id
        assert category['filters'][0]['name'] == filter_name
        assert category['filters'][0]['type'] == FILTER_TYPE
        assert len(category['filters'][0]['values']) == (
            2 if category['id'] == ROOT_CATEGORY_ID else 1
        )


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_merge_different_filters(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
):
    cultivar_filter_info = {
        'id': 'cultivar',
        'name': 'Сорт',
        'category_id': CATEGORY_ID_2,
    }
    flavour_filter_info = {
        'id': 'flavour',
        'name': 'Вкус',
        'category_id': CATEGORY_ID_1_1,
    }
    value = 'Значение'

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                cultivar_filter_info['id']: {
                    'name': cultivar_filter_info['name'],
                },
                flavour_filter_info['id']: {
                    'name': flavour_filter_info['name'],
                },
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {
                'default_category_settings': {
                    cultivar_filter_info['id']: {},
                    flavour_filter_info['id']: {},
                },
            },
            CATEGORY_ID_1: {
                'default_category_settings': {
                    cultivar_filter_info['id']: {},
                    flavour_filter_info['id']: {},
                },
            },
            cultivar_filter_info['category_id']: {
                'default_category_settings': {cultivar_filter_info['id']: {}},
            },
            flavour_filter_info['category_id']: {
                'default_category_settings': {flavour_filter_info['id']: {}},
            },
        },
    )

    sql_set_sku_product_attribute(
        cultivar_filter_info['id'], [(SKU_ID_1, value)],
    )
    sql_set_sku_product_attribute(
        flavour_filter_info['id'], [(SKU_ID_2, value)],
    )
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        assert len(category['filters']) == (
            2 if category['id'] == ROOT_CATEGORY_ID else 1
        )


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_multiple_categories_and_many_products.sql',
    ],
)
async def test_merge_one_filter_with_many_options(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
):
    filter_id = 'milk_type'
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': 'Тип молока'}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_2: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1_1: {'default_category_settings': {filter_id: {}}},
        },
    )

    sql_set_sku_product_attribute(
        filter_id,
        [
            (1, 'Коровье'),
            (2, 'Верблюжье'),
            (3, 'Коровье'),
            (4, 'Ослиное'),
            (5, 'Ослиное'),
            (6, 'Коровье'),
        ],
    )

    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
        '&include_products=false'
    )

    expected_options = {
        ROOT_CATEGORY_ID: [
            {'value': 'Коровье', 'items_count': 3, 'sort_order': 1},
            {'value': 'Ослиное', 'items_count': 2, 'sort_order': 2},
            {'value': 'Верблюжье', 'items_count': 1, 'sort_order': 3},
        ],
        CATEGORY_ID_1: [
            {'value': 'Ослиное', 'items_count': 2, 'sort_order': 1},
            {'value': 'Коровье', 'items_count': 1, 'sort_order': 2},
        ],
        CATEGORY_ID_2: [
            {'value': 'Коровье', 'items_count': 2, 'sort_order': 1},
            {'value': 'Верблюжье', 'items_count': 1, 'sort_order': 2},
        ],
        CATEGORY_ID_1_1: [
            {'value': 'Ослиное', 'items_count': 2, 'sort_order': 1},
            {'value': 'Коровье', 'items_count': 1, 'sort_order': 2},
        ],
    }

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    assert len(response_json['categories']) == len(expected_options.keys())

    for category in response_json['categories']:
        assert len(category['filters']) == 1
        category['filters'][0]['values'].sort(
            key=lambda item: item['sort_order'],
        )
        expected_options[category['id']].sort(
            key=lambda item: item['sort_order'],
        )
        assert (
            category['filters'][0]['values']
            == expected_options[category['id']]
        )


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_merge_after_filtering(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
):
    cultivar_filter_info = {
        'id': 'cultivar',
        'name': 'Сорт',
        'category_id': CATEGORY_ID_2,
        'chosen_option': 'Сорт1',
    }
    flavour_filter_info = {
        'id': 'flavour',
        'name': 'Вкус',
        'category_id': CATEGORY_ID_1_1,
        'chosen_option': 'Вкус1',
    }

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                cultivar_filter_info['id']: {
                    'name': cultivar_filter_info['name'],
                },
                flavour_filter_info['id']: {
                    'name': flavour_filter_info['name'],
                },
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {
                'default_category_settings': {
                    cultivar_filter_info['id']: {},
                    flavour_filter_info['id']: {},
                },
            },
            CATEGORY_ID_1: {
                'default_category_settings': {
                    cultivar_filter_info['id']: {},
                    flavour_filter_info['id']: {},
                },
            },
            cultivar_filter_info['category_id']: {
                'default_category_settings': {cultivar_filter_info['id']: {}},
            },
            flavour_filter_info['category_id']: {
                'default_category_settings': {flavour_filter_info['id']: {}},
            },
        },
    )

    sql_set_sku_product_attribute(
        cultivar_filter_info['id'],
        [(SKU_ID_1, cultivar_filter_info['chosen_option'])],
    )
    sql_set_sku_product_attribute(
        flavour_filter_info['id'], [(SKU_ID_2, flavour_filter_info['id'])],
    )
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(
        url,
        json={
            'filters': [
                {
                    'id': cultivar_filter_info['id'],
                    'type': 'multiselect',
                    'chosen_options': [cultivar_filter_info['chosen_option']],
                },
            ],
        },
    )
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        assert len(category['filters']) == (
            2 if category['id'] == ROOT_CATEGORY_ID else 1
        )
        for response_filter in category['filters']:
            assert len(response_filter['values']) == 1
            if response_filter['id'] == cultivar_filter_info['id']:
                assert response_filter['values'][0]['items_count'] == 1
            else:
                assert response_filter['values'][0]['items_count'] == 0


@pytest.mark.parametrize(
    'filter_id',
    [
        'fat_content',
        'milk_type',
        'cultivar',
        'flavour',
        'meat_type',
        'carcass_part',
        'egg_category',
        'country',
        'package_type',
        'volume',
        'brand',
    ],
)
@pytest.mark.parametrize(
    'max_depth, response_categories_count, '
    'response_filters_in_parent_category_count',
    [pytest.param(0, 1, 0), pytest.param(1, 3, 1), pytest.param(None, 4, 1)],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_merge_with_filtered_categories(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
        max_depth,
        response_categories_count,
        response_filters_in_parent_category_count,
):
    filter_name = 'Фильтр'
    values = [(SKU_ID_1, '11.1'), (SKU_ID_2, '22.2')]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            ROOT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_2: {'default_category_settings': {filter_id: {}}},
            CATEGORY_ID_1_1: {'default_category_settings': {filter_id: {}}},
        },
    )

    if filter_id == 'brand':
        sql_set_sku_brand([(SKU_ID_1, 1), (SKU_ID_2, 2)])
    else:
        sql_set_sku_product_attribute(filter_id, values)
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'
    if max_depth is not None:
        url += f'&max_depth={max_depth}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == response_categories_count
    for category in response_json['categories']:
        if category['id'] == ROOT_CATEGORY_ID:
            assert (
                len(category['filters'])
                == response_filters_in_parent_category_count
            )


@pytest.mark.parametrize(
    'config, expected_filter_values',
    [
        pytest.param(
            {
                ROOT_CATEGORY_ID: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 11': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
                CATEGORY_ID_1: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 33': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 44': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
            },
            {
                ROOT_CATEGORY_ID: [
                    {
                        'value': 'Диапазон 11',
                        'items_count': 2,
                        'sort_order': 1,
                    },
                ],
                CATEGORY_ID_2: [
                    {
                        'value': 'Диапазон 33',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                ],
                CATEGORY_ID_1_1: [
                    {
                        'value': 'Диапазон 44',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                ],
            },
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 11': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
                CATEGORY_ID_1: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 44': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
            },
            {
                ROOT_CATEGORY_ID: [
                    {
                        'value': 'Диапазон 11',
                        'items_count': 2,
                        'sort_order': 1,
                    },
                ],
                CATEGORY_ID_1_1: [
                    {
                        'value': 'Диапазон 44',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                ],
            },
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 11-1': {'from': '0', 'to': '5'},
                                'Диапазон 11-2': {'from': '5', 'to': '10'},
                            },
                        },
                    },
                },
                CATEGORY_ID_1: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 33': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {
                        'fat_content': {
                            'ranges': {
                                'Диапазон 44': {'from': '0', 'to': '10'},
                            },
                        },
                    },
                },
            },
            {
                ROOT_CATEGORY_ID: [
                    {
                        'value': 'Диапазон 11-1',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                    {
                        'value': 'Диапазон 11-2',
                        'items_count': 1,
                        'sort_order': 2,
                    },
                ],
                CATEGORY_ID_2: [
                    {
                        'value': 'Диапазон 33',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                ],
                CATEGORY_ID_1_1: [
                    {
                        'value': 'Диапазон 44',
                        'items_count': 1,
                        'sort_order': 1,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_use_ranges_config(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        config,
        expected_filter_values,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {'fat_content': {'name': 'Жирность'}}},
    )
    update_taxi_config('EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO', config)

    sql_set_sku_product_attribute(
        'fat_content', [(SKU_ID_1, 3), (SKU_ID_2, 6)],
    )
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        if category['id'] in expected_filter_values:
            assert len(category['filters']) == 1
            assert (
                category['filters'][0]['values']
                == expected_filter_values[category['id']]
            )


@pytest.mark.parametrize(
    'config, expected_categories_with_filters',
    [
        pytest.param(
            {
                ROOT_CATEGORY_ID: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {'fat_content': {}},
                },
            },
            [ROOT_CATEGORY_ID, CATEGORY_ID_1, CATEGORY_ID_2, CATEGORY_ID_1_1],
        ),
        pytest.param(
            {
                CATEGORY_ID_1: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {'fat_content': {}},
                },
            },
            [CATEGORY_ID_1, CATEGORY_ID_2, CATEGORY_ID_1_1],
        ),
        pytest.param(
            {
                CATEGORY_ID_2: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {'fat_content': {}},
                },
            },
            [CATEGORY_ID_2, CATEGORY_ID_1_1],
        ),
        pytest.param(
            {
                ROOT_CATEGORY_ID: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_2: {
                    'default_category_settings': {'fat_content': {}},
                },
                CATEGORY_ID_1_1: {
                    'default_category_settings': {'fat_content': {}},
                },
            },
            [ROOT_CATEGORY_ID, CATEGORY_ID_2, CATEGORY_ID_1_1],
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_filters_in_not_leaf_categories(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        config,
        expected_categories_with_filters,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {'fat_content': {'name': 'Жирность'}}},
    )
    update_taxi_config('EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO', config)

    sql_set_sku_product_attribute(
        'fat_content', [(SKU_ID_1, 3), (SKU_ID_2, 6)],
    )
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={ROOT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()
    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        assert len(category['filters']) == (
            1 if category['id'] in expected_categories_with_filters else 0
        )
