import pytest

import tests_eats_brands.common as common


BRANDS_DATA = [
    common.extend_brand_without_slug({common.NAME: 'Brand1'}),
    common.extend_brand_without_slug({common.NAME: 'Brand2'}),
]

REQUEST = 'request'
STATUS = 'status'
CHANGES = [
    {REQUEST: {common.ID: 2, common.NAME: 'Brand New Name'}, STATUS: 200},
    {REQUEST: {common.ID: 3}, STATUS: 404},
    {REQUEST: {common.ID: 1, common.NAME: 'Brand New Name'}, STATUS: 409},
]

CASES_STATUSES = [(BRANDS_DATA, CHANGES)]


@pytest.mark.parametrize('brands,changes', CASES_STATUSES)
async def test_statuses(taxi_eats_brands, brands, changes):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now check statuses
    for new_data in changes:
        response = await taxi_eats_brands.post(
            'brands/v1/edit', json=new_data[REQUEST],
        )
        assert response.status_code == new_data[STATUS]


CASES_EDIT = [
    (
        {common.NAME: 'Create'},
        {
            common.ID: 1,
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.BIT_SETTINGS: 2,
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: 1,
            common.EDITORIAL_VERDICT: 'editorial_verdict',
            common.EDITORIAL_DESCRIPTION: 'editorial_description',
        },
        {
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.BIT_SETTINGS: 2,
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: 1,
            common.EDITORIAL_VERDICT: 'editorial_verdict',
            common.EDITORIAL_DESCRIPTION: 'editorial_description',
        },
    ),
    (
        {
            common.NAME: 'Create',
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'mcd',
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: 1,
            common.EDITORIAL_VERDICT: 'editorial_verdict',
            common.EDITORIAL_DESCRIPTION: 'editorial_description',
        },
        {
            common.ID: 1,
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.SET_NOTIFY_EMAILS_TO_NULL: True,
            common.SET_BIT_SETTINGS_TO_NULL: True,
            common.SET_FAST_FOOD_NOTIFY_TIME_SHIFT_TO_NULL: True,
            common.SET_EDITORIAL_VERDICT_TO_NULL: True,
            common.SET_EDITORIAL_DESCRIPTION_TO_NULL: True,
        },
        {
            common.ID: 1,
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.BIT_SETTINGS: None,
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: None,
            common.EDITORIAL_VERDICT: None,
            common.EDITORIAL_DESCRIPTION: None,
        },
    ),
    (
        {
            common.NAME: 'Create',
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'mcd',
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: 1,
            common.EDITORIAL_VERDICT: 'editorial_verdict',
            common.EDITORIAL_DESCRIPTION: 'editorial_description',
        },
        {
            common.ID: 1,
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.NOTIFY_EMAIL_PERSONAL_IDS: ['111', '222'],
            common.SET_BIT_SETTINGS_TO_NULL: True,
            common.SET_FAST_FOOD_NOTIFY_TIME_SHIFT_TO_NULL: True,
            common.SET_EDITORIAL_VERDICT_TO_NULL: True,
            common.SET_EDITORIAL_DESCRIPTION_TO_NULL: True,
        },
        {
            common.ID: 1,
            common.NAME: 'Edit',
            common.SLUG: 'Edit',
            common.BUSINESS_TYPE: 'store',
            common.CATEGORY_TYPE: 'client',
            common.BRAND_TYPE: 'not_restaurant',
            common.IS_STOCK_SUPPORTED: True,
            common.IGNORE_SURGE: True,
            common.NOTIFY_EMAIL_PERSONAL_IDS: ['111', '222'],
            common.BIT_SETTINGS: None,
            common.FAST_FOOD_NOTIFY_TIME_SHIFT: None,
            common.EDITORIAL_VERDICT: None,
            common.EDITORIAL_DESCRIPTION: None,
        },
    ),
]


@pytest.mark.parametrize('brand,edit,expected', CASES_EDIT)
async def test_edit(
        taxi_eats_brands, get_brand, check_brand_data, brand, edit, expected,
):
    # we need to create brands first
    response = await taxi_eats_brands.post('brands/v1/create', json=brand)
    assert response.status_code == 200

    # edit
    response = await taxi_eats_brands.post('brands/v1/edit', json=edit)
    assert response.status_code == 200

    # check expected
    brand = get_brand(edit[common.ID])
    check_brand_data(brand, expected)


CASES_VALIDATION_200 = [
    (
        {common.NAME: 'tri_medvedia'},
        {common.ID: 1},  # no changes
        {
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'not_qsr',
            common.BIT_SETTINGS: 1,
        },
    ),
    (
        {common.NAME: 'tri_medvedia'},
        {
            common.ID: 1,
            common.BUSINESS_TYPE: 'shop',
            common.BRAND_TYPE: 'not_restaurant',
        },
        {
            common.BUSINESS_TYPE: 'shop',
            common.BRAND_TYPE: 'not_restaurant',
            common.BIT_SETTINGS: 1,
        },
    ),
    (
        {
            common.NAME: 'tri_medvedia',
            common.BUSINESS_TYPE: 'shop',
            common.BRAND_TYPE: 'not_restaurant',
        },
        {
            common.ID: 1,
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'not_qsr',
        },
        {
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'not_qsr',
            common.BIT_SETTINGS: 1,
        },
    ),
]


@pytest.mark.parametrize('brand,edit,expected', CASES_VALIDATION_200)
async def test_queries_validation_200(
        taxi_eats_brands, get_brand, check_brand_data, brand, edit, expected,
):
    # we need to create brands first
    response = await taxi_eats_brands.post('brands/v1/create', json=brand)
    assert response.status_code == 200

    # edit
    response = await taxi_eats_brands.post('brands/v1/edit', json=edit)
    assert response.status_code == 200

    # check expected
    brand = get_brand(edit[common.ID])
    check_brand_data(brand, expected)


CASES_VALIDATION_BAD_REQUEST = [
    (
        {common.NAME: 'tri_medvedia'},
        {common.ID: 1, common.BUSINESS_TYPE: 'shop'},
        {
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'not_qsr',
            common.BIT_SETTINGS: 1,
        },
    ),
    (
        {common.NAME: 'tri_medvedia'},
        {common.ID: 1, common.BRAND_TYPE: 'not_restaurant'},
        {
            common.BUSINESS_TYPE: 'restaurant',
            common.BRAND_TYPE: 'not_qsr',
            common.BIT_SETTINGS: 1,
        },
    ),
    (
        {
            common.NAME: 'tri_medvedia',
            common.BUSINESS_TYPE: 'shop',
            common.BRAND_TYPE: 'not_restaurant',
        },
        {common.ID: 1, common.BUSINESS_TYPE: 'restaurant'},
        {
            common.BUSINESS_TYPE: 'shop',
            common.BRAND_TYPE: 'not_restaurant',
            common.BIT_SETTINGS: 1,
        },
    ),
]


@pytest.mark.parametrize('brand,edit,expected', CASES_VALIDATION_BAD_REQUEST)
async def test_not_found(
        taxi_eats_brands, get_brand, check_brand_data, brand, edit, expected,
):
    # we need to create brands first
    response = await taxi_eats_brands.post('brands/v1/create', json=brand)
    assert response.status_code == 200

    # edit
    response = await taxi_eats_brands.post('brands/v1/edit', json=edit)
    assert response.status_code == 404

    # check expected
    brand = get_brand(edit[common.ID])
    check_brand_data(brand, expected)
