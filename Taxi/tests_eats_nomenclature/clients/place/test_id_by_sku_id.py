import pytest

PLACE_ID = '3'
HANDLER = '/v1/place/products/id-by-sku-id'
AUTH_HEADERS = {'x-device-id': 'device_id'}


@pytest.mark.parametrize(
    'assortment_name, experiment_on, expected_mapping',
    [
        pytest.param(
            None,
            True,
            [
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b008'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b010'],
                },
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
                    'ids': [
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012',
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013',
                    ],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999', 'ids': []},
            ],
            id='exp_assortment',
        ),
        pytest.param(
            None,
            False,
            [
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b010'],
                },
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
                    'ids': [
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012',
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013',
                    ],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999', 'ids': []},
            ],
            id='default_assortment',
        ),
        pytest.param(
            'assortment_name',
            True,
            [
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b010'],
                },
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
                    'ids': [
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012',
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013',
                    ],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999', 'ids': []},
            ],
            id='assortment_name',
        ),
        pytest.param(
            'unknown_assortment_name',
            True,
            [
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b010'],
                },
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
                    'ids': [
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012',
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013',
                    ],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999', 'ids': []},
            ],
            id='unknown_assortment_name',
        ),
        pytest.param(
            'partner',
            False,
            [
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124', 'ids': []},
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125', 'ids': []},
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
                    'ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b010'],
                },
                {
                    'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
                    'ids': [
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b012',
                        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b013',
                    ],
                },
                {'sku_id': '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999', 'ids': []},
            ],
            id='partner',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_200_mapping_found(
        taxi_eats_nomenclature,
        set_assortment_name_exp,
        # parametrize
        assortment_name,
        experiment_on,
        expected_mapping,
):
    set_assortment_name_exp(experiment_on, 'exp_assortment_name')

    request = {
        'sku_ids': [
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4120',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4121',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4122',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4123',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4124',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4125',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4126',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4127',
            '8d0f044f-44fa-4ce4-937d-a9b5cd6a4999',
        ],
    }
    query = f'{HANDLER}?place_id={PLACE_ID}'
    if assortment_name:
        query += f'&assortment_name={assortment_name}'
    response = await taxi_eats_nomenclature.post(
        query, json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    expected_response = {'products': expected_mapping}

    assert _sorted_response(response.json()) == _sorted_response(
        expected_response,
    )


@pytest.mark.parametrize(
    'exp_brand_ids, exp_excluded_place_ids, expected_assortment_id',
    [
        pytest.param([1], [], 1, id='exp assortment'),
        pytest.param(
            [1], [3], 3, id='default assortment: place in excluded places',
        ),
        pytest.param(
            [2], [], 3, id='default assortment: brand not in exp brands',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_name_exp_brand_and_place(
        taxi_eats_nomenclature,
        testpoint,
        set_assortment_name_exp,
        # parametrize
        exp_brand_ids,
        exp_excluded_place_ids,
        expected_assortment_id,
):
    set_assortment_name_exp(
        experiment_on=True,
        assortment_name='exp_assortment_name',
        brand_ids=exp_brand_ids,
        excluded_place_ids=exp_excluded_place_ids,
    )

    @testpoint('v1-place-products-id-by-sku-id-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == expected_assortment_id

    request = {'sku_ids': ['8d0f044f-44fa-4ce4-937d-a9b5cd6a4120']}
    query = f'{HANDLER}?place_id={PLACE_ID}'
    await taxi_eats_nomenclature.post(
        query, json=request, headers=AUTH_HEADERS,
    )

    assert _assortment.has_calls


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_unknown_place(taxi_eats_nomenclature):
    unknown_place_id = '123999'
    request = {'sku_ids': ['8d0f044f-44fa-4ce4-937d-a9b5cd6a4120']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={unknown_place_id}', json=request,
    )

    assert response.status == 404
    assert response.json() == {
        'status': 404,
        'message': f'Unknown place id: {unknown_place_id}',
    }


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_place_without_assortment(taxi_eats_nomenclature):
    request = {'sku_ids': ['8d0f044f-44fa-4ce4-937d-a9b5cd6a4120']}
    assortment_name = 'some_assortment'
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}&assortment_name={assortment_name}',
        json=request,
    )

    assert response.status == 404
    assert response.json() == {
        'status': 404,
        'message': f'Place id `{PLACE_ID}` does not have active assortment',
    }


@pytest.mark.parametrize(
    'sku_ids_count',
    [pytest.param(10, id='too_much'), pytest.param(0, id='empty')],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
@pytest.mark.config(EATS_NOMENCLATURE_PUBLIC_ID_BY_SKU_ID={'max_items': 5})
async def test_400_incorrect_size_of_ids(
        taxi_eats_nomenclature, sku_ids_count,
):
    limit = 5
    request = {'sku_ids': [str(i) for i in range(sku_ids_count)]}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=request,
    )
    assert response.status_code == 400
    assert response.json() == {
        'status': 400,
        'message': (
            f'Incorrect size of sku_ids. Requested {sku_ids_count}, '
            f'should be 0 < size <= {limit}'
        ),
    }


def _sorted_response(response):
    response['products'].sort(key=lambda k: k['sku_id'])
    for i in response['products']:
        i['ids'].sort()
    return response
