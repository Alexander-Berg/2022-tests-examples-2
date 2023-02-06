import pytest

HANDLER = '/v1/place/category_products/filtered'

PARENT_CATEGORY_ID = '11'
CATEGORY_ID_22 = '22'
CATEGORY_ID_33 = '33'
CATEGORY_ID_44 = '44'
CATEGORIES_IDS = [
    PARENT_CATEGORY_ID,
    CATEGORY_ID_22,
    CATEGORY_ID_33,
    CATEGORY_ID_44,
]
BRAND_ID = 1
PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
FILTER_TYPE = 'multiselect'
MIN_ITEMS_WITH_FILLED_OPTIONS_PERCENT = 50
SKU_ID_1 = 1
SKU_ID_2 = 2
SKU_ID_3 = 3
PRODUCT_BRAND_1 = 1
PRODUCT_BRAND_2 = 2
PRODUCT_BRAND_3 = 3
FILTER_VALUE_1 = '11.1'
FILTER_VALUE_2 = '22.2'
FILTER_VALUE_3 = '33.3'
TAG_NAME_1 = 'Тег 1'
TAG_NAME_2 = 'Тег 2'


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_single_product_with_all_attributes(
        taxi_eats_nomenclature, pgsql, update_taxi_config, sql_set_sku_brand,
):
    filters_info = {
        'fat_content': {'name': 'Жирность'},
        'milk_type': {'name': 'Тип молока'},
        'cultivar': {'name': 'Сорт'},
        'flavour': {'name': 'Вкус'},
        'meat_type': {'name': 'Тип мяса'},
        'carcass_part': {'name': 'Часть тушки'},
        'egg_category': {'name': 'Категория яиц'},
        'country': {'name': 'Страна производства'},
        'package_type': {'name': 'Упаковка'},
        'volume': {'name': 'Объем'},
        'brand': {'name': 'Бренд'},
    }
    filter_value = '12.5'

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO', {'filters_info': filters_info},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {
            PARENT_CATEGORY_ID: {
                'default_category_settings': {
                    'fat_content': {},
                    'milk_type': {},
                    'cultivar': {},
                    'flavour': {},
                    'meat_type': {},
                    'carcass_part': {},
                    'egg_category': {},
                    'country': {},
                    'package_type': {},
                    'volume': {},
                    'brand': {},
                },
            },
        },
    )

    sql_set_all_attributes(pgsql, filter_value)
    sql_set_sku_brand([(1, 1)])
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == len(filters_info.keys())
    for response_filter in response_filters:
        response_filter_id = response_filter['id']
        assert (
            response_filter['name'] == filters_info[response_filter_id]['name']
        )
        assert len(response_filter['values']) == 1
        assert response_filter['type'] == FILTER_TYPE
        assert response_filter['values'][0]['value'] == filter_value
        assert response_filter['values'][0]['items_count'] == 1


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
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_single_filter_multiple_values(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
):
    filter_name = 'Фильтр'
    values_to_fill = [
        (SKU_ID_1, FILTER_VALUE_1),
        (SKU_ID_2, FILTER_VALUE_2),
        (SKU_ID_3, FILTER_VALUE_3),
    ]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {PARENT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )
    if filter_id == 'brand':
        sql_set_sku_brand(
            [
                (SKU_ID_1, PRODUCT_BRAND_1),
                (SKU_ID_2, PRODUCT_BRAND_2),
                (SKU_ID_3, PRODUCT_BRAND_3),
            ],
        )
    else:
        sql_set_sku_product_attribute(filter_id, values_to_fill)
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == 1
    assert len(response_filters[0]['values']) == len(values_to_fill)
    response_filters[0]['values'].sort(key=lambda item: item['value'])
    for i in range(len(response_filters[0]['values'])):
        assert (
            response_filters[0]['values'][i]['value'] == values_to_fill[i][1]
        )
        assert response_filters[0]['values'][i]['items_count'] == 1


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
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filter_one_value_in_multiple_products(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
):
    filter_name = 'Фильтр'
    values_to_fill = [
        (1, FILTER_VALUE_1),
        (2, FILTER_VALUE_1),
        (3, FILTER_VALUE_1),
    ]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {PARENT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )

    if filter_id == 'brand':
        sql_set_sku_brand(
            [
                (SKU_ID_1, PRODUCT_BRAND_1),
                (SKU_ID_2, PRODUCT_BRAND_1),
                (SKU_ID_3, PRODUCT_BRAND_1),
            ],
        )
    else:
        sql_set_sku_product_attribute(filter_id, values_to_fill)
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == 1
    assert len(response_filters[0]['values']) == 1
    assert response_filters[0]['values'][0]['items_count'] == 3
    assert response_filters[0]['values'][0]['value'] == values_to_fill[0][1]


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
    'items_count_to_fill, expected_filters_count',
    [
        pytest.param(2, 1, id='enough_items'),
        pytest.param(1, 0, id='not_enough_items'),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_items_with_filter_attributes_count(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        sql_set_sku_brand,
        # parametrize params
        filter_id,
        items_count_to_fill,
        expected_filters_count,
):
    filter_name = 'Фильтр'
    values_to_fill = [(1, FILTER_VALUE_1), (2, FILTER_VALUE_1)]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {
            'filters_info': {
                filter_id: {
                    'name': filter_name,
                    'min_items_with_filled_options_percent': (
                        MIN_ITEMS_WITH_FILLED_OPTIONS_PERCENT
                    ),
                },
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        {PARENT_CATEGORY_ID: {'default_category_settings': {filter_id: {}}}},
    )

    if filter_id == 'brand':
        sql_set_sku_brand(
            [(SKU_ID_1, PRODUCT_BRAND_1), (SKU_ID_2, PRODUCT_BRAND_1)][
                :items_count_to_fill
            ],
        )
    else:
        sql_set_sku_product_attribute(
            filter_id, values_to_fill[:items_count_to_fill],
        )
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == expected_filters_count


@pytest.mark.parametrize(
    'config, expect_filter_in_response',
    [
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {'milk_type': {}},
                },
            },
            True,
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {},
                    BRAND_ID: {'milk_type': {}},
                },
            },
            True,
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {'milk_type': {}},
                    BRAND_ID: {},
                },
            },
            False,
        ),
        pytest.param(
            {PARENT_CATEGORY_ID: {'default_category_settings': {}}}, False,
        ),
        pytest.param({}, False),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_filter_in_category_config(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        config,
        expect_filter_in_response,
):
    filter_id = 'milk_type'
    filter_name = 'Фильтр'
    values_to_fill = [(SKU_ID_1, FILTER_VALUE_1), (SKU_ID_2, FILTER_VALUE_1)]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config('EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO', config)

    sql_set_sku_product_attribute(filter_id, values_to_fill)
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == (1 if expect_filter_in_response else 0)


@pytest.mark.parametrize(
    'config_by_id, config_by_tag, expect_filter_in_response',
    [
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {'milk_type': {}},
                },
            },
            {
                TAG_NAME_1: {'default_category_settings': {'milk_type': {}}},
                TAG_NAME_2: {'default_category_settings': {'milk_type': {}}},
            },
            True,
        ),
        pytest.param(
            None,
            {
                TAG_NAME_1: {'default_category_settings': {'milk_type': {}}},
                TAG_NAME_2: {'default_category_settings': {'milk_type': {}}},
            },
            False,
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_products.sql'],
)
async def test_category_tags_config_conflict(
        taxi_eats_nomenclature,
        pgsql,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize
        config_by_id,
        config_by_tag,
        expect_filter_in_response,
):
    filter_id = 'milk_type'
    filter_name = 'Фильтр'
    values_to_fill = [(SKU_ID_1, FILTER_VALUE_1), (SKU_ID_2, FILTER_VALUE_1)]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    if config_by_id:
        update_taxi_config(
            'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO', config_by_id,
        )
    if config_by_tag:
        update_taxi_config(
            'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO_BY_TAGS',
            config_by_tag,
        )

    sql_make_category_custom(pgsql, PARENT_CATEGORY_ID)
    sql_add_tags_to_custom_category(
        pgsql, [TAG_NAME_1, TAG_NAME_2], PARENT_CATEGORY_ID,
    )

    sql_set_sku_product_attribute(filter_id, values_to_fill)
    request = (
        HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'
    )

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200

    response_filters = extract_filters_from_response(response.json())
    assert len(response_filters) == (1 if expect_filter_in_response else 0)


@pytest.mark.parametrize(
    'config_category_settings, expected_filter_names',
    [
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                            ),
                        },
                    },
                },
                CATEGORY_ID_33: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + CATEGORY_ID_33
                            ),
                        },
                    },
                },
            },
            {
                PARENT_CATEGORY_ID: (
                    'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                ),
                CATEGORY_ID_33: 'Имя фильтра в категории ' + CATEGORY_ID_33,
                CATEGORY_ID_44: 'Сорт',
            },
            id='override_in_parent_and_child_categories',
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {'cultivar': {}},
                },
                CATEGORY_ID_33: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + CATEGORY_ID_33
                            ),
                        },
                    },
                },
            },
            {
                PARENT_CATEGORY_ID: 'Сорт',
                CATEGORY_ID_33: 'Имя фильтра в категории ' + CATEGORY_ID_33,
                CATEGORY_ID_44: 'Сорт',
            },
            id='override_in_child_category',
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                            ),
                        },
                    },
                },
                CATEGORY_ID_33: {
                    'default_category_settings': {'cultivar': {}},
                },
            },
            {
                PARENT_CATEGORY_ID: (
                    'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                ),
                CATEGORY_ID_33: 'Сорт',
                CATEGORY_ID_44: 'Сорт',
            },
            id='override_in_parent_category',
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                            ),
                        },
                    },
                    str(BRAND_ID): {
                        'cultivar': {
                            'overriden_name': (
                                'Другое имя фильтра в категории '
                                + PARENT_CATEGORY_ID
                            ),
                        },
                    },
                },
                CATEGORY_ID_33: {
                    'default_category_settings': {'cultivar': {}},
                },
            },
            {
                PARENT_CATEGORY_ID: (
                    'Другое имя фильтра в категории ' + PARENT_CATEGORY_ID
                ),
                CATEGORY_ID_33: 'Сорт',
                CATEGORY_ID_44: 'Сорт',
            },
            id='brand_override_in_parent_category',
        ),
        pytest.param(
            {
                PARENT_CATEGORY_ID: {
                    'default_category_settings': {
                        'cultivar': {
                            'overriden_name': (
                                'Имя фильтра в категории ' + PARENT_CATEGORY_ID
                            ),
                        },
                    },
                    str(BRAND_ID): {'cultivar': {}},
                },
                CATEGORY_ID_33: {
                    'default_category_settings': {'cultivar': {}},
                },
            },
            {
                PARENT_CATEGORY_ID: 'Сорт',
                CATEGORY_ID_33: 'Сорт',
                CATEGORY_ID_44: 'Сорт',
            },
            id='empty_brand_override_in_parent_category',
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_multiple_categories.sql'],
)
async def test_set_custom_filter_name_for_categories(
        taxi_eats_nomenclature,
        update_taxi_config,
        sql_set_sku_product_attribute,
        # parametrize params
        config_category_settings,
        expected_filter_names,
):
    filter_id = 'cultivar'
    filter_name = 'Сорт'
    values = [(1, '11.1'), (1, '11.1')]

    categories_with_filters = [PARENT_CATEGORY_ID, CATEGORY_ID_33]

    update_taxi_config(
        'EATS_NOMENCLATURE_FILTERS_INFO',
        {'filters_info': {filter_id: {'name': filter_name}}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO',
        config_category_settings,
    )

    sql_set_sku_product_attribute(filter_id, values)

    url = HANDLER + f'?place_id={PLACE_ID}&category_id={PARENT_CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200
    response_json = response.json()

    assert len(response_json['categories']) == len(CATEGORIES_IDS)
    for category in response_json['categories']:
        if category['id'] in categories_with_filters:
            assert len(category['filters']) == 1
            assert category['filters'][0]['id'] == filter_id
            assert (
                category['filters'][0]['name']
                == expected_filter_names[category['id']]
            )
        else:
            assert category['filters'] == []


def sql_set_all_attributes(pgsql, value, sku_id=1):
    cursor = pgsql['eats_nomenclature'].cursor()

    cursor.execute(
        f"""update eats_nomenclature.sku
            set
                fat_content = {value},
                milk_type = '{value}',
                cultivar = '{value}',
                flavour = '{value}',
                meat_type = '{value}',
                carcass_part = '{value}',
                egg_category = '{value}',
                country = '{value}',
                package_type = '{value}',
                volume = '{value} мл'
            where id = {sku_id}
        """,
    )


def extract_filters_from_response(response):
    assert len(response['categories']) == 1
    category = response['categories'][0]
    category['filters'].sort(key=lambda filter: filter['id'])
    return category['filters']


def sql_make_category_custom(pgsql, category_id):
    cursor = pgsql['eats_nomenclature'].cursor()

    cursor.execute(
        f"""insert into eats_nomenclature.custom_categories
                (id, name, description, external_id)
            values ({category_id}, 'custom category {category_id}',
                'abc', {category_id});
            update eats_nomenclature.categories
            set custom_category_id = {category_id}
            where public_id = {category_id};
        """,
    )


def sql_add_tags_to_custom_category(pgsql, tags, custom_category_id):
    cursor = pgsql['eats_nomenclature'].cursor()

    for tag in tags:
        cursor.execute(
            f"""insert into eats_nomenclature.tags (id, name)
                values (default, '{tag}')
                returning id;
            """,
        )

        tag_id = cursor.fetchone()[0]

        cursor.execute(
            f"""insert into eats_nomenclature.custom_category_tags
                    (custom_category_id, tag_id)
                values ({custom_category_id}, {tag_id});
            """,
        )
