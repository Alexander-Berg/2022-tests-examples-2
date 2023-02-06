import datetime as dt

import pytest
import pytz

HANDLER = '/v1/place/category_products/filtered'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)

CATEGORY_ID = '11'
BRAND_ID = 1
PLACE_ID = 1
QUERY_PRODUCT_ID = 1
PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'


@pytest.mark.parametrize(
    'use_sku_data, exclude_brand_from_exp, expected_product_name',
    [
        pytest.param(True, False, 'Имя с МК 1', id='exp_enabled'),
        pytest.param(True, True, '1', id='exp_enabled_with_excluded_brand'),
        pytest.param(False, False, '1', id='exp_disabled'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_sku_exp(
        taxi_eats_nomenclature,
        pgsql,
        experiments3,
        load_json,
        # parametrize params
        use_sku_data,
        exclude_brand_from_exp,
        expected_product_name,
):
    experiment_data = load_json('use_sku_experiment.json')
    if use_sku_data:
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'true'
    else:
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'false'
    if exclude_brand_from_exp:
        experiment_data['experiments'][0]['clauses'][0]['value'][
            'excluded_brand_ids'
        ] = ['2']
    experiments3.add_experiments_json(experiment_data)

    sql_set_sku(pgsql, 1, None)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_product = extract_product_from_response(response.json())
    assert response_product['name'] == expected_product_name


@pytest.mark.parametrize(
    'sku_id, overriden_sku_id, expected_product_name',
    [
        pytest.param(1, None, 'Имя с МК 1', id='without_override'),
        pytest.param(1, 2, 'Имя с МК 2', id='with_override'),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_overriden_sku(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        sku_id,
        overriden_sku_id,
        expected_product_name,
):
    sql_set_sku(pgsql, sku_id, overriden_sku_id)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_product = extract_product_from_response(response.json())
    assert response_product['name'] == expected_product_name


@pytest.mark.parametrize(
    'sku_id, expected_product_info',
    [
        pytest.param(
            None,
            {
                'adult': False,
                'description': {'general': '1'},
                'id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'images': [
                    {'url': 'processed_url_1', 'sort_order': 0},
                    {'url': 'processed_url_2', 'sort_order': 1},
                ],
                'is_catch_weight': False,
                'measure': {'quantum': 0.1, 'unit': 'GRM', 'value': 100},
                'name': '1',
                'price': '999',
                'shipping_type': 'all',
                'sort_order': 1,
            },
        ),
        pytest.param(
            1,
            {
                'adult': True,
                'description': {
                    'general': (
                        'Состав: Состав с МК 1<br>Пищевая ценность на 100 г: '
                        'белки 103 г, жиры 104 г, углеводы 102 г, '
                        'энергетическая ценность 105 ккал<br>Срок хранения: '
                        '300 д<br>Условия хранения: Хранить МК 1<br>'
                        'Упаковка: Картонная коробка<br>Страна производства: '
                        'Бельгия'
                    ),
                },
                'id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'images': [{'url': 'processed_url_3', 'sort_order': 0}],
                'is_catch_weight': False,
                'measure': {'unit': 'GRM', 'value': 101},
                'name': 'Имя с МК 1',
                'price': '999',
                'shipping_type': 'all',
                'sort_order': 1,
            },
        ),
        pytest.param(
            2,
            {
                'adult': False,
                'description': {
                    'general': (
                        'Состав: Состав с МК 2<br>Пищевая ценность на 100 г: '
                        'белки 253 г, жиры 254 г, углеводы 252 г, '
                        'энергетическая ценность 255 ккал<br>Срок '
                        'хранения: 300 д<br>Условия хранения: '
                        'Хранить МК 2<br>Упаковка: Бумага<br>Страна '
                        'производства: Франция'
                    ),
                },
                'id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                'images': [{'url': 'processed_url_4', 'sort_order': 0}],
                'is_catch_weight': False,
                'measure': {'unit': 'GRM', 'value': 251},
                'name': 'Имя с МК 2',
                'price': '999',
                'shipping_type': 'all',
                'sort_order': 1,
            },
        ),
    ],
)
@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_fill_info_from_sku(
        taxi_eats_nomenclature,
        pgsql,
        # parametrize params
        sku_id,
        expected_product_info,
):
    sql_set_sku(pgsql, sku_id, None)
    request = HANDLER + f'?place_id={PLACE_ID}&category_id={CATEGORY_ID}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_product = extract_product_from_response(response.json())
    assert response_product == expected_product_info


def sql_set_sku(pgsql, sku_id, overriden_sku_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    if sku_id:
        cursor.execute(
            f"""update eats_nomenclature.products
                set
                    sku_id = {sku_id}
                where id = {QUERY_PRODUCT_ID}
            """,
        )
    if overriden_sku_id:
        cursor.execute(
            f"""insert into eats_nomenclature.overriden_product_sku(
                product_id, sku_id
            )
            values ({QUERY_PRODUCT_ID}, {overriden_sku_id})
            """,
        )


def extract_product_from_response(response):
    assert len(response['categories']) == 1
    assert len(response['categories'][0]['products']) == 1
    assert response['categories'][0]['products'][0]['id'] == PRODUCT_PUBLIC_ID

    product = response['categories'][0]['products'][0]
    product['images'].sort(key=lambda item: item['url'])
    return response['categories'][0]['products'][0]
