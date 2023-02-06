import datetime as dt

import pytest
import pytz

HANDLER = '/v1/place/category_products/filtered'
MOCK_NOW = dt.datetime(2022, 6, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.parametrize(
    'use_exp, exp_assortment_name',
    [
        pytest.param(False, '', id='default_assortment'),
        pytest.param(True, 'assortment_name_2', id='exp_assortment'),
    ],
)
@pytest.mark.parametrize(
    'requested_assortment_name',
    [None, 'assortment_name_1', 'assortment_name_2'],
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_for_assortments.sql'],
)
async def test_assortment_name(
        taxi_eats_nomenclature,
        set_assortment_name_exp,
        # parametrize params
        use_exp,
        exp_assortment_name,
        requested_assortment_name,
):
    set_assortment_name_exp(use_exp, exp_assortment_name)

    place_id = 1
    category_to_request = 11

    if requested_assortment_name is not None:
        expected_assortment_name = requested_assortment_name
    elif use_exp:
        expected_assortment_name = exp_assortment_name
    else:
        expected_assortment_name = 'assortment_name_1'

    if expected_assortment_name == 'assortment_name_1':
        expected_categories = {'11': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001']}
    elif expected_assortment_name == 'assortment_name_2':
        expected_categories = {'11': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b002']}
    else:
        assert False, 'Forgot to add corresponding response?'

    url = HANDLER + f'?place_id={place_id}&category_id={category_to_request}'
    if requested_assortment_name is not None:
        url += f'&assortment_name={requested_assortment_name}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    response_categories = extract_ids(response_json)
    assert response_categories == expected_categories


@pytest.mark.parametrize(
    'exp_brand_ids, exp_excluded_place_ids, expected_categories',
    [
        pytest.param(
            [1],
            [],
            {'11': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b002']},
            id='exp assortment',
        ),
        pytest.param(
            [1],
            [1],
            {'11': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001']},
            id='default assortment: place in excluded places',
        ),
        pytest.param(
            [2],
            [],
            {'11': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001']},
            id='default assortment: brand not in exp brands',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_for_assortments.sql'],
)
async def test_assortment_name_exp_brand_and_place(
        taxi_eats_nomenclature,
        set_assortment_name_exp,
        # parametrize
        exp_brand_ids,
        exp_excluded_place_ids,
        expected_categories,
):
    set_assortment_name_exp(
        experiment_on=True,
        assortment_name='assortment_name_2',
        brand_ids=exp_brand_ids,
        excluded_place_ids=exp_excluded_place_ids,
    )

    place_id = 1
    category_to_request = 11

    url = HANDLER + f'?place_id={place_id}&category_id={category_to_request}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    response_categories = extract_ids(response_json)
    assert response_categories == expected_categories


@pytest.mark.parametrize(
    'category_id, max_depth, expected_categories',
    [
        pytest.param('11', None, ['11', '22', '33', '44', '55', '66']),
        pytest.param('11', 0, ['11']),
        pytest.param('11', 1, ['11', '22', '66']),
        pytest.param('11', 2, ['11', '22', '33', '44', '66']),
        pytest.param('11', 100, ['11', '22', '33', '44', '55', '66']),
        pytest.param('22', None, ['22', '33', '44', '55']),
        pytest.param('22', 0, ['22']),
        pytest.param('22', 1, ['22', '33', '44']),
        pytest.param('22', 2, ['22', '33', '44', '55']),
        pytest.param('22', 100, ['22', '33', '44', '55']),
        pytest.param('66', None, ['66']),
        pytest.param('66', 0, ['66']),
        pytest.param('66', 1, ['66']),
        pytest.param('66', 100, ['66']),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_for_categories.sql'],
)
async def test_filter_by_depth_and_ids(
        taxi_eats_nomenclature,
        # parametrize params
        category_id,
        max_depth,
        expected_categories,
):
    place_id = 1

    request = HANDLER + f'?place_id={place_id}&category_id={category_id}'
    if max_depth is not None:
        request += f'&max_depth={max_depth}'

    response = await taxi_eats_nomenclature.post(request, json={'filters': []})
    assert response.status == 200
    response_categories = [
        category['id'] for category in response.json()['categories']
    ]
    assert sorted(response_categories) == expected_categories


@pytest.mark.parametrize('include_products', [None, True, False])
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_some_products.sql'],
)
async def test_include_products(
        taxi_eats_nomenclature,
        # parametrize params
        include_products,
):
    place_id = 1
    category_to_request = 11

    url = HANDLER + f'?place_id={place_id}&category_id={category_to_request}'
    if include_products is not None:
        url += f'&include_products={include_products}'

    response = await taxi_eats_nomenclature.post(url, json={'filters': []})
    assert response.status == 200

    response_json = response.json()
    for category in response_json['categories']:
        if include_products in (True, None):
            assert len(category['products']) == 4
        else:
            assert category['products'] == []


def extract_ids(response):
    extracted_categories = {}
    for category in response['categories']:
        extracted_categories.update({category['id']: []})
        for product in category['products']:
            extracted_categories[category['id']].append(product['id'])
        extracted_categories[category['id']].sort()

    return dict(sorted(extracted_categories.items()))
