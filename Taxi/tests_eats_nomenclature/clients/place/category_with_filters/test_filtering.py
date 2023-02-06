import pytest

HANDLER = '/v1/place/category_products/filtered'

CATEGORY_ID = '11'
PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
ANOTHER_FAT_CONTENT = '6.3'
ANOTHER_MILK_TYPE = 'Sheep'


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
    'filter_options, expected_filter_options, expected_products_count',
    [
        pytest.param(
            ['12.5'],
            [
                {'value': '12.5', 'items_count': 1, 'sort_order': 2},
                {'value': '100', 'items_count': 1, 'sort_order': 1},
            ],
            1,
            id='match_filter',
        ),
        pytest.param(
            ['12.3'],
            [
                {'value': '12.5', 'items_count': 1, 'sort_order': 2},
                {'value': '100', 'items_count': 1, 'sort_order': 1},
            ],
            0,
            id='dont_match_filter',
        ),
        pytest.param(
            ['12.3', '12.5'],
            [
                {'value': '12.5', 'items_count': 1, 'sort_order': 2},
                {'value': '100', 'items_count': 1, 'sort_order': 1},
            ],
            1,
            id='one_match_among_options',
        ),
        pytest.param(
            ['12.3', '12.4'],
            [
                {'value': '12.5', 'items_count': 1, 'sort_order': 2},
                {'value': '100', 'items_count': 1, 'sort_order': 1},
            ],
            0,
            id='no_matches_among_options',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filtering_one_filter(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
        filter_options,
        expected_filter_options,
        expected_products_count,
):
    attribute_values = [(1, '12.5'), (2, '100')]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': 'Имя фильтра'}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )

    if filter_id != 'brand':
        sql_set_sku_product_attribute(filter_id, attribute_values)
    else:
        sql_set_sku_brand([(1, 1), (2, 2)])
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(
        url,
        json={
            'filters': [
                {
                    'id': filter_id,
                    'type': 'multiselect',
                    'chosen_options': filter_options,
                },
            ],
        },
    )
    assert response.status == 200
    response_json = response.json()

    assert len(response_json['categories']) == 1
    assert (
        len(response_json['categories'][0]['products'])
        == expected_products_count
    )
    assert len(response_json['categories'][0]['filters']) == 1
    assert len(response_json['categories'][0]['filters'][0]['values']) == len(
        attribute_values,
    )

    response_json['categories'][0]['filters'][0]['values'].sort(
        key=lambda item: item['sort_order'],
    )
    expected_filter_options.sort(key=lambda item: item['sort_order'])

    assert (
        response_json['categories'][0]['filters'][0]['values']
        == expected_filter_options
    )


@pytest.mark.parametrize(
    'attributes_values, fat_content_chosen_option, milk_type_chosen_option, '
    'products_count, response_filters_count, expected_filter_options',
    [
        pytest.param(
            [
                ('2.5', 'Cow'),
                ('3.2', 'Goat'),
                (ANOTHER_FAT_CONTENT, ANOTHER_MILK_TYPE),
            ],
            '2.5',
            'Cow',
            1,
            2,
            {
                'fat_content': {
                    'filter_options': [
                        {'value': '2.5', 'items_count': 1, 'sort_order': 1},
                        {'value': '3.2', 'items_count': 0, 'sort_order': 2},
                        {
                            'value': ANOTHER_FAT_CONTENT,
                            'items_count': 0,
                            'sort_order': 3,
                        },
                    ],
                },
                'milk_type': {
                    'filter_options': [
                        {'value': 'Cow', 'items_count': 1, 'sort_order': 1},
                        {'value': 'Goat', 'items_count': 0, 'sort_order': 2},
                        {
                            'value': ANOTHER_MILK_TYPE,
                            'items_count': 0,
                            'sort_order': 3,
                        },
                    ],
                },
            },
            id='match_both_filters',
        ),
        pytest.param(
            [
                ('2.5', None),
                ('3.2', 'Goat'),
                (ANOTHER_FAT_CONTENT, ANOTHER_MILK_TYPE),
            ],
            '3.2',
            'Goat',
            1,
            2,
            {
                'fat_content': {
                    'filter_options': [
                        {'value': '2.5', 'items_count': 0, 'sort_order': 1},
                        {'value': '3.2', 'items_count': 1, 'sort_order': 2},
                        {
                            'value': ANOTHER_FAT_CONTENT,
                            'items_count': 0,
                            'sort_order': 3,
                        },
                    ],
                },
                'milk_type': {
                    'filter_options': [
                        {'value': 'Goat', 'items_count': 1, 'sort_order': 1},
                        {
                            'value': ANOTHER_MILK_TYPE,
                            'items_count': 0,
                            'sort_order': 2,
                        },
                    ],
                },
            },
            id='match_fat_content',
        ),
        pytest.param(
            [
                ('2.5', 'Cow'),
                ('3.2', 'Goat'),
                (ANOTHER_FAT_CONTENT, ANOTHER_MILK_TYPE),
            ],
            '3.2',
            None,
            1,
            2,
            {
                'fat_content': {
                    'filter_options': [
                        {'value': '2.5', 'items_count': 1, 'sort_order': 1},
                        {'value': '3.2', 'items_count': 1, 'sort_order': 2},
                        {
                            'value': ANOTHER_FAT_CONTENT,
                            'items_count': 1,
                            'sort_order': 3,
                        },
                    ],
                },
                'milk_type': {
                    'filter_options': [
                        {'value': 'Cow', 'items_count': 0, 'sort_order': 1},
                        {'value': 'Goat', 'items_count': 1, 'sort_order': 2},
                        {
                            'value': ANOTHER_MILK_TYPE,
                            'items_count': 0,
                            'sort_order': 3,
                        },
                    ],
                },
            },
            id='one_filter',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filtering_multiple_filters(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        attributes_values,
        fat_content_chosen_option,
        milk_type_chosen_option,
        products_count,
        response_filters_count,
        expected_filter_options,
):
    fat_content_filter = {'id': 'fat_content', 'name': 'Жирность'}
    milk_type_filter = {'id': 'milk_type', 'name': 'Тип молока'}

    fat_content_attributes = []
    milk_type_attributes = []
    i = 1
    for fat_content_attr, milk_type_attr in attributes_values:
        if fat_content_attr is not None:
            fat_content_attributes += [(i, fat_content_attr)]
        if milk_type_attr is not None:
            milk_type_attributes += [(i, milk_type_attr)]
        i += 1

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                fat_content_filter['id']: {'name': fat_content_filter['name']},
                milk_type_filter['id']: {'name': milk_type_filter['name']},
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            CATEGORY_ID: {
                'default_category_settings': {
                    fat_content_filter['id']: {},
                    milk_type_filter['id']: {},
                },
            },
        },
    )

    sql_set_sku_product_attribute(
        fat_content_filter['id'], fat_content_attributes,
    )
    sql_set_sku_product_attribute(milk_type_filter['id'], milk_type_attributes)

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    request_filters = []
    if fat_content_chosen_option:
        request_filters += [
            {
                'id': fat_content_filter['id'],
                'type': 'multiselect',
                'chosen_options': [fat_content_chosen_option],
            },
        ]
    if milk_type_chosen_option:
        request_filters += [
            {
                'id': milk_type_filter['id'],
                'type': 'multiselect',
                'chosen_options': [milk_type_chosen_option],
            },
        ]

    response = await taxi_eats_nomenclature.post(
        url, json={'filters': request_filters},
    )
    assert response.status == 200
    response_json = response.json()

    assert len(response_json['categories']) == 1
    assert (
        len(response_json['categories'][0]['filters'])
        == response_filters_count
    )
    for response_filter in response_json['categories'][0]['filters']:
        assert len(response_filter['values']) == len(
            expected_filter_options[response_filter['id']]['filter_options'],
        )

        response_filter['values'].sort(key=lambda item: item['sort_order'])
        expected_filter_options[response_filter['id']]['filter_options'].sort(
            key=lambda item: item['sort_order'],
        )

        assert (
            response_filter['values']
            == expected_filter_options[response_filter['id']]['filter_options']
        )
    assert len(response_json['categories'][0]['products']) == products_count


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_bool_filter(taxi_eats_nomenclature):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(
        url,
        json={
            'filters': [
                {'id': 'bool_filter', 'type': 'bool', 'chosen_option': True},
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_filter_not_in_config(taxi_eats_nomenclature):
    url = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'
    response = await taxi_eats_nomenclature.post(
        url,
        json={
            'filters': [
                {
                    'id': 'bad_filter_id',
                    'type': 'multiselect',
                    'chosen_options': ['kek'],
                },
            ],
        },
    )
    assert response.status_code == 400
