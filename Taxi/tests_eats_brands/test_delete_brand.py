import pytest

import tests_eats_brands.common as common

BRANDS_DATA = [
    common.extend_default_brand(
        {common.NAME: 'Brand1', common.SLUG: 'Brand1'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Brand2', common.SLUG: 'Brand2'},
    ),
]

CASES = [(BRANDS_DATA, {common.ID: 1}), (BRANDS_DATA, {common.ID: 2})]


@pytest.mark.parametrize('brands,ids_to_delete', CASES)
async def test_delete(taxi_eats_brands, brands, ids_to_delete):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/find-by-id', json=ids_to_delete,
    )
    assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/delete', json=ids_to_delete,
    )
    assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/find-by-id', json=ids_to_delete,
    )
    assert response.status_code == 200


async def test_not_found(taxi_eats_brands):
    response = await taxi_eats_brands.post(
        'brands/v1/delete', json={common.ID: 1},
    )
    assert response.status_code == 404
