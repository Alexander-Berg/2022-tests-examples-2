import pytest

import tests_eats_brands.common as common


BRANDS_DATA = [
    common.extend_default_brand(
        {common.NAME: 'Some Name', common.SLUG: 'Some_Name'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Some Name 2', common.SLUG: 'Some_Name_2'},
    ),
]

CASES = [(BRANDS_DATA, {common.ID: 2}, BRANDS_DATA[1])]


def id_format(val):
    if common.SLUG in val:
        return val[common.SLUG]
    return ''


@pytest.mark.parametrize(
    'brands,request_data,expected_data', CASES, ids=id_format,
)
async def test_200(
        taxi_eats_brands,
        brands,
        request_data,
        expected_data,
        check_brand_data,
):
    # we need to create brand first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-id', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    brand = response_json['brand']
    check_brand_data(brand, expected_data)


@pytest.mark.parametrize('request_data', [{common.ID: 2}])
async def test_404(taxi_eats_brands, request_data):
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-id', json=request_data,
    )
    assert response.status_code == 404


@pytest.mark.parametrize('brands', [BRANDS_DATA])
async def test_find_merged_brand(taxi_eats_brands, check_brand_data, brands):
    # we need to create brand first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands',
        json={common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2]},
    )

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/find-by-id', json={common.ID: 2},
    )
    assert response.status_code == 200
    check_brand_data(response.json()['brand'], brands[0])
    assert response.json()['brand'][common.ACTUAL_ID] == 1
