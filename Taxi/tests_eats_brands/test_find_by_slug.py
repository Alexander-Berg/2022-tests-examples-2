import pytest

import tests_eats_brands.common as common

BRANDS_DATA = [
    common.extend_default_brand({common.NAME: 'Brand1', common.SLUG: 'brand'}),
]


@pytest.mark.parametrize(
    'brands,request_data,expected_data',
    [(BRANDS_DATA, {common.SLUG: 'brand'}, 'Brand1')],
    ids=['simple_test'],
)
async def test_200(taxi_eats_brands, brands, request_data, expected_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-slug', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json['brand']['name'] == expected_data


@pytest.mark.parametrize('brands', [BRANDS_DATA])
async def test_not_found(taxi_eats_brands, brands):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-slug', json={common.SLUG: 'brand2'},
    )
    assert response.status_code == 404
