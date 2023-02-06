import pytest

import tests_eats_brands.common as common

BRANDS_DATA = [
    common.extend_default_brand(
        {common.NAME: 'Brand1', common.SLUG: 'Brand1'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Brand2', common.SLUG: 'Brand2'},
    ),
    common.extend_default_brand(
        {
            common.NAME: 'Brand3',
            common.SLUG: 'Brand3',
            common.BUSINESS_TYPE: 'shop',
        },
    ),
]


@pytest.mark.parametrize(
    'brands,request_data',
    [([BRANDS_DATA[0]], {common.BUSINESS_TYPE: 'store'})],
    ids=['simple_test'],
)
async def test_200_one(taxi_eats_brands, brands, request_data):
    # we need to create brand first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-business-type', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    result = response_json['brands'][0]

    assert result['business_type'] == common.DEFAULT_BRAND['business_type']


@pytest.mark.parametrize(
    'brands,request_data',
    [(BRANDS_DATA, {common.BUSINESS_TYPE: 'store'})],
    ids=['simple_test'],
)
async def test_200_many(taxi_eats_brands, brands, request_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-business-type', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    result = response_json['brands']
    assert len(result) == 2
    assert sorted([x[common.NAME] for x in result]) == ['Brand1', 'Brand2']


@pytest.mark.parametrize(
    'brands,request_data',
    [(BRANDS_DATA, {common.BUSINESS_TYPE: 'store'})],
    ids=['simple_test'],
)
async def test_not_found(taxi_eats_brands, brands, request_data):
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-business-type', json=request_data,
    )
    assert response.status_code == 200

    assert not response.json()['brands']
