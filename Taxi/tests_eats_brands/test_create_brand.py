import pytest

import tests_eats_brands.common as common


TEST_DATA = [
    common.extend_default_brand(
        {common.NAME: 'Перекресток', common.SLUG: 'Perekrestok'},
    ),
    common.extend_default_brand(
        {common.NAME: 'Магнит', common.SLUG: 'Magnit'},
    ),
]


def format_ids(data):
    return data[common.SLUG]


@pytest.mark.parametrize('test_data', TEST_DATA, ids=format_ids)
async def test_200(taxi_eats_brands, get_brand, check_brand_data, test_data):
    response = await taxi_eats_brands.post('brands/v1/create', json=test_data)

    assert response.status_code == 200
    response_json = response.json()

    brand_id = response_json['brand']['id']
    brand = get_brand(brand_id)
    check_brand_data(brand, test_data)


@pytest.mark.parametrize(
    'request_data,expected_data,metrics_count',
    [
        (
            common.extend_brand_without_slug({common.NAME: 'Магнит'}),
            common.extend_default_brand(
                {common.NAME: 'Магнит', common.SLUG: 'Magnit'},
            ),
            1,
        ),
        (
            common.extend_brand_without_slug({common.NAME: 'Имя с пробелами'}),
            common.extend_default_brand(
                {
                    common.NAME: 'Имя с пробелами',
                    common.SLUG: 'ima_s_probelami',
                },
            ),
            1,
        ),
    ],
    ids=['Slug not given', 'names with whitespaces'],
)
async def test_slug(
        taxi_eats_brands,
        get_brand,
        check_brand_data,
        request_data,
        expected_data,
        metrics_count,
        taxi_eats_brands_monitor,
):
    await taxi_eats_brands.tests_control(reset_metrics=True)

    response = await taxi_eats_brands.post(
        'brands/v1/create', json=request_data,
    )

    assert response.status_code == 200
    response_json = response.json()

    brand_id = response_json['brand']['id']
    brand = get_brand(brand_id)
    check_brand_data(brand, expected_data)
    metrics_generate_slug_counter = await taxi_eats_brands_monitor.get_metric(
        'eats-brands-generate-slug-counter',
    )
    metrics_slug_fails_counter = await taxi_eats_brands_monitor.get_metric(
        'eats-brands-generate-slug-fails-counter',
    )
    assert metrics_generate_slug_counter == metrics_count
    assert metrics_slug_fails_counter == 0


@pytest.mark.parametrize(
    'test_data',
    [
        common.extend_default_brand(
            {common.NAME: 'Brand Name', common.BUSINESS_TYPE: 'bad_value'},
        ),
    ],
    ids=['Bad business_type'],
)
async def test_400(taxi_eats_brands, test_data):
    response = await taxi_eats_brands.post('brands/v1/create', json=test_data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'test_data', [common.DEFAULT_BRAND.copy()], ids=['Create twice'],
)
async def test_409(taxi_eats_brands, test_data):
    response = await taxi_eats_brands.post('brands/v1/create', json=test_data)
    assert response.status_code == 200

    response = await taxi_eats_brands.post('brands/v1/create', json=test_data)
    assert response.status_code == 409


@pytest.mark.parametrize(
    'request_data, expected_data',
    [
        (
            common.extend_brand_without_slug({common.NAME: '  ! d :a '}),
            common.extend_default_brand(
                {common.NAME: '! d :a', common.SLUG: 'd_a'},
            ),
        ),
        (
            common.extend_default_brand(
                {common.NAME: '! d : ', common.SLUG: '__d____'},
            ),
            common.extend_default_brand(
                {common.NAME: '! d :', common.SLUG: 'd'},
            ),
        ),
    ],
)
async def test_query_validation(
        taxi_eats_brands,
        get_brand,
        check_brand_data,
        request_data,
        expected_data,
):
    response = await taxi_eats_brands.post(
        'brands/v1/create', json=request_data,
    )

    assert response.status_code == 200
    response_json = response.json()

    brand_id = response_json['brand']['id']
    brand = get_brand(brand_id)
    check_brand_data(brand, expected_data)


@pytest.mark.parametrize(
    'request_data, request_data_second, slug',
    [
        (
            common.extend_brand_without_slug({common.NAME: 'Aaa_aa'}),
            common.extend_brand_without_slug({common.NAME: 'aaa__aa'}),
            'aaa_aa',
        ),
        (
            common.extend_brand_without_slug({common.NAME: 'aaa_aa'}),
            common.extend_brand_without_slug({common.NAME: 'Aaa__aa'}),
            'aaa_aa',
        ),
        (
            common.extend_brand_without_slug({common.NAME: '_aaa_aa'}),
            common.extend_brand_without_slug({common.NAME: 'Aaa__aa_'}),
            'aaa_aa',
        ),
        (
            common.extend_brand_without_slug({common.NAME: '_aaa_aa'}),
            common.extend_brand_without_slug({common.NAME: 'aaa__aa_'}),
            'aaa_aa',
        ),
    ],
)
async def test_slug_unique_validation(
        taxi_eats_brands, get_brand, request_data, request_data_second, slug,
):
    response = await taxi_eats_brands.post(
        'brands/v1/create', json=request_data,
    )

    assert response.status_code == 200
    response_json = response.json()

    brand_id = response_json['brand']['id']
    brand = get_brand(brand_id)

    assert brand['slug'] == slug

    response = await taxi_eats_brands.post(
        'brands/v1/create', json=request_data_second,
    )

    assert response.status_code == 200
    response_json = response.json()

    brand_id = response_json['brand']['id']
    brand = get_brand(brand_id)

    assert brand['slug'] != slug
