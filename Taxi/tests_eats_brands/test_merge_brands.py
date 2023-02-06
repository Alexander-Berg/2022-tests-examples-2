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
        {common.NAME: 'Brand3', common.SLUG: 'Brand3'},
    ),
]

CASES = [(BRANDS_DATA, {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2, 3]})]


@pytest.mark.parametrize('brands, request_data', CASES)
async def test_merge(
        taxi_eats_brands, get_brand, get_merge_history, brands, request_data,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=request_data,
    )
    assert response.status_code == 200

    actual_id_from_request = request_data[common.ACTUAL_ID]
    history = get_merge_history(actual_id_from_request)
    assert history

    for brand_id in request_data[common.IDS_TO_MERGE]:
        brand = get_brand(brand_id)
        assert brand['actual_id'] == actual_id_from_request
        assert brand['is_deleted']
        assert brand_id in history['merged_brands_ids']


@pytest.mark.parametrize(
    'brands, request_data',
    [(BRANDS_DATA, {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: []})],
)
async def test_empty_merge(taxi_eats_brands, brands, request_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=request_data,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'brands, request_data',
    [(BRANDS_DATA, {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [1, 2, 3]})],
)
async def test_actual_also_in_merge(taxi_eats_brands, brands, request_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=request_data,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'brands, first_request_data, second_request_data',
    [
        (
            BRANDS_DATA,
            {common.ACTUAL_ID: 2, common.IDS_TO_MERGE: [3]},
            {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2]},
        ),
    ],
)
async def test_merge_chain(
        taxi_eats_brands,
        get_brand,
        get_merge_history,
        brands,
        first_request_data,
        second_request_data,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    first_response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=first_request_data,
    )
    assert first_response.status_code == 200

    second_response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=second_request_data,
    )
    assert second_response.status_code == 200

    actual_id_from_request = second_request_data[common.ACTUAL_ID]
    history = get_merge_history(actual_id_from_request)
    assert history

    for brand_id in (
            second_request_data[common.IDS_TO_MERGE]
            + first_request_data[common.IDS_TO_MERGE]
    ):
        brand = get_brand(brand_id)
        assert brand['actual_id'] == actual_id_from_request
        assert brand['is_deleted']
        assert brand_id in history['merged_brands_ids']


@pytest.mark.parametrize(
    'brands, request_data',
    [(BRANDS_DATA, {common.ACTUAL_ID: 5, common.IDS_TO_MERGE: [1, 2, 3]})],
)
async def test_wrong_actual_id(taxi_eats_brands, brands, request_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=request_data,
    )
    assert response.status_code == 404
