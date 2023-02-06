import pytest


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {'limit': 2, 'cursor': 3},
            [
                {
                    'data': {
                        'color_code': '000000',
                        'raw_color': 'карбоновый',
                        'normalized_color': 'карбоновый',
                    },
                    'revision': 4,
                },
                {
                    'data': {
                        'raw_color': 'бирюза',
                        'normalized_color': 'бирюза',
                    },
                    'revision': 5,
                },
            ],
            200,
        ),
        ({'limit': 0}, None, 400),
        ({'limit': 1001}, None, 400),
    ],
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_colors.sql'])
async def test_get_colors(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_colors'
    expected = {'items': expected}
    await _check(web_app_client, params, expected, status, url)


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {'limit': 2, 'cursor': 1},
            [
                {'data': {'raw_brand': 'Toyota'}, 'revision': 2},
                {
                    'data': {
                        'raw_brand': 'Toyota',
                        'raw_model': 'Camry',
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'CAMRY',
                        'corrected_model': 'Toyota Camry',
                    },
                    'revision': 3,
                },
            ],
            200,
        ),
        ({'limit': 0}, None, 400),
        ({'limit': 1001}, None, 400),
    ],
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_brand_models.sql'])
async def test_get_brand_models(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_brand_models'
    expected = {'items': expected}
    await _check(web_app_client, params, expected, status, url)


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {'limit': 2, 'cursor': 1},
            [
                {
                    'data': {
                        'car_age': 4,
                        'car_price': 6000,
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'CAMRY',
                    },
                    'revision': 2,
                },
                {
                    'data': {
                        'car_year': 2010,
                        'car_age': 8,
                        'car_price': 500000,
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'COROLLA',
                    },
                    'revision': 3,
                },
            ],
            200,
        ),
        ({'limit': 0}, None, 400),
        ({'limit': 1001}, None, 400),
        (
            {'limit': 20, 'cursor': 3},
            [
                {
                    'data': {
                        'car_age': 8,
                        'car_price': -1.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'VAZ',
                        'normalized_model_code': 'KALINA',
                    },
                    'revision': 4,
                },
                {
                    'data': {
                        'car_age': 8,
                        'car_price': 228.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'FERRARI',
                        'normalized_model_code': 'ITALIA',
                    },
                    'revision': 5,
                },
                {
                    'data': {
                        'car_age': 8,
                        'car_price': 322.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': '7ER',
                    },
                    'revision': 6,
                },
                {
                    'data': {
                        'car_age': 8,
                        'car_price': 1488.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'TT',
                    },
                    'revision': 7,
                },
                {
                    'data': {
                        'car_age': 0,
                        'car_price': 101,
                        'car_year': 2020,
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'TT',
                    },
                    'revision': 8,
                },
                {
                    'data': {
                        'car_age': 3,
                        'car_price': -1,
                        'car_year': 2015,
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A8',
                    },
                    'revision': 9,
                },
                {
                    'data': {
                        'car_age': 8,
                        'car_price': -1.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'ASTON_MARTIN',
                        'normalized_model_code': 'DB9',
                    },
                    'revision': 10,
                },
                {
                    'data': {
                        'car_age': 8,
                        'car_price': 228.0,
                        'car_year': 2010,
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X6',
                    },
                    'revision': 11,
                },
            ],
            200,
        ),
    ],
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_prices.sql'])
@pytest.mark.config(
    CARS_CATALOG_PRICES_CLARIFICATION={
        'enable': True,
        'default_price': 228,
        'override': {
            'BMW 7er 2010': 322,
            'Audi TT 2010': 1488,
            'Audi TT': 101,
        },
        'exclude': [
            {'brand': 'LADA (ВАЗ)'},
            {'brand': 'Audi'},
            {'brand': 'Aston Martin', 'model': 'DB9'},
        ],
    },
)
async def test_get_prices(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_prices'
    expected = {'items': expected}
    await _check(web_app_client, params, expected, status, url)


async def _check(web_app_client, params, expected, status, url, method='GET'):
    get_params = None
    body = None
    if method == 'GET':
        get_params = params
        handler = web_app_client.get
    else:
        body = params
        handler = web_app_client.post
    response = await handler(url, headers={}, params=get_params, json=body)
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {'raw_color': 'Бронза'},
            {'normalized_color': 'бронза', 'color_code': '555555'},
            200,
        ),
        ({'raw_color': 'meow'}, None, 404),
        ({'unexpected': ''}, None, 400),
    ],
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_colors.sql'])
async def test_get_color(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_color'
    await _check(web_app_client, params, expected, status, url)


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {'raw_brand': 'Toyota', 'raw_model': 'Corolla'},
            {
                'normalized_mark_code': 'TOYOTA',
                'normalized_model_code': 'COROLLA',
                'corrected_model': 'Toyota Corolla',
            },
            200,
        ),
        ({'raw_brand': 'moo', 'raw_model': 'meow'}, None, 404),
    ],
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_brand_models.sql'])
async def test_brand_model(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_brand_model'
    await _check(web_app_client, params, expected, status, url)


@pytest.mark.parametrize(
    'params,expected,status',
    [
        (
            {
                'car_year': 2013,
                'normalized_mark_code': 'TOYOTA',
                'normalized_model_code': 'CAMRY',
            },
            {'car_age': 5, 'car_price': 600000.0},
            200,
        ),
        (
            {
                'car_year': 2010,
                'normalized_mark_code': 'VAZ',
                'normalized_model_code': 'KALINA',
            },
            {'car_age': 8, 'car_price': -1},
            200,
        ),
        (
            {
                'car_year': 2010,
                'normalized_mark_code': 'BMW',
                'normalized_model_code': '7ER',
            },
            {'car_age': 8, 'car_price': 322.0},
            200,
        ),
        (
            {
                'car_year': 2010,
                'normalized_mark_code': 'AUDI',
                'normalized_model_code': 'TT',
            },
            {'car_age': 8, 'car_price': 1488.0},
            200,
        ),
        (
            {
                'car_year': 2010,
                'normalized_mark_code': 'ASTON_MARTIN',
                'normalized_model_code': 'DB9',
            },
            {'car_age': 8, 'car_price': -1.0},
            200,
        ),
        (
            {
                'car_year': 2010,
                'normalized_mark_code': 'FERRARI',
                'normalized_model_code': 'ITALIA',
            },
            {'car_age': 8, 'car_price': 228.0},
            200,
        ),
        (
            {
                'car_year': 2000,
                'normalized_mark_code': 'moo',
                'normalized_model_code': 'meow',
            },
            None,
            404,
        ),
    ],
)
@pytest.mark.config(
    CARS_CATALOG_PRICES_CLARIFICATION={
        'enable': True,
        'default_price': 228,
        'override': {'BMW 7er 2010': 322, 'Audi TT 2010': 1488},
        'exclude': [
            {'brand': 'LADA (ВАЗ)'},
            {'brand': 'Aston Martin', 'model': 'DB9'},
        ],
    },
)
@pytest.mark.pgsql('cars_catalog', files=['test_get_prices.sql'])
async def test_get_price(web_app_client, params, expected, status):
    url = '/api/v1/cars/get_price'
    await _check(web_app_client, params, expected, status, url, 'POST')
