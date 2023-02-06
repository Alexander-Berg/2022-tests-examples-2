import pytest

import tests_eats_brands.common as common

BRANDS_DATA = [common.extend_brand_without_slug({common.NAME: 'Brand1'})]


@pytest.mark.parametrize(
    'brands,request_data,expected_data',
    [(BRANDS_DATA, {common.NAME: 'Brand1'}, 'Brand1')],
    ids=['simple_test'],
)
async def test_200(taxi_eats_brands, brands, request_data, expected_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-name', json=request_data,
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
        'brands/v1/find-by-name', json={common.NAME: 'Brand2'},
    )
    assert response.status_code == 404


#  Do not insert any of nullable fields
@pytest.mark.pgsql(
    'eats_brands',
    queries=[
        'INSERT INTO eats_brands.brands '
        '(id, name, slug, business_type, category_type, brand_type, '
        'is_stock_supported, ignore_surge, is_deleted, bit_settings) '
        'VALUES (1, \'Brand name\', \'brand_name\', \'restaurant\', '
        '\'default\', \'other_qsr\', false, false, false, null)',
    ],
)
async def test_bit_settings_eq_null(taxi_eats_brands):
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-name', json={'name': 'Brand name'},
    )
    assert response.status_code == 200
