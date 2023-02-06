import pytest

import tests_eats_brands.common as common


def compare_brands_lists(expected_data, response_data, check_brand_data):
    assert len(expected_data) == len(response_data)

    response_brands = {
        brand[common.SLUG].lower(): brand for brand in response_data
    }
    expected_brands = {
        expected_brand[common.SLUG].lower(): expected_brand
        for expected_brand in expected_data
    }

    for expected_slug in expected_brands:
        assert expected_slug in response_brands
        check_brand_data(
            response_brands[expected_slug], expected_brands[expected_slug],
        )


BRANDS_DATA = [
    common.extend_default_brand(
        {common.NAME: 'Some Name', common.SLUG: 'Some_Name'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Some Name 2', common.SLUG: 'Some_Name_2'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Some Name 3', common.SLUG: 'Some_Name_3'},
    ),
]

CASES = [
    (BRANDS_DATA, {common.IDS: [1, 2, 3]}, BRANDS_DATA),  # All found
    (BRANDS_DATA, {common.IDS: [1, 2, 4]}, BRANDS_DATA[:2]),  # Part found
    (BRANDS_DATA, {common.IDS: [4, 5, 6]}, []),
]  # Not found


@pytest.mark.parametrize('brands,request_data,expected_data', CASES)
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
        'brands/v1/find-by-ids', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    compare_brands_lists(
        expected_data, response_json[common.BRANDS], check_brand_data,
    )


@pytest.mark.parametrize('brands', [BRANDS_DATA])
async def test_find_merged_brand(taxi_eats_brands, brands, check_brand_data):
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
        'brands/v1/find-by-ids', json={common.IDS: [2]},
    )
    assert response.status_code == 200
    check_brand_data(response.json()[common.BRANDS][0], brands[0])
    assert response.json()[common.BRANDS][0][common.ACTUAL_ID] == 1
