import decimal

import pytest


@pytest.mark.now('2020-06-01T00:00:00Z+00:00')
@pytest.mark.pgsql(
    'cars_catalog',
    queries=[
        """
        INSERT INTO cars_catalog.brand_models
        (raw_brand, raw_model, normalized_mark_code, normalized_model_code)
        VALUES ('Vaz', '2106', 'VAZ', '2106'),
               ('Renault', 'Logan', 'RENAULT', 'LOGAN')
        """,
    ],
)
@pytest.mark.parametrize(
    'mark,model,year,expected_status,expected_data',
    [
        (
            'Vaz',
            '2106',
            2000,
            200,
            {
                'mark_code': 'VAZ',
                'model_code': '2106',
                'year': 2000,
                'adjusted_age': 20,
                'price': '100500',
            },
        ),
        (
            'Vaz',
            '2106',
            2001,
            200,
            {
                'mark_code': 'VAZ',
                'model_code': '2106',
                'year': 2001,
                'adjusted_age': 19,
                'price': '110550.0',
            },
        ),
        (
            'Vaz',
            '2106',
            1980,
            200,
            {
                'mark_code': 'VAZ',
                'model_code': '2106',
                'year': 1980,
                'adjusted_age': 40,
                'price': '-1',
            },
        ),
        (
            'Renault',
            'Logan',
            2019,
            200,
            {
                'mark_code': 'RENAULT',
                'model_code': 'LOGAN',
                'year': 2019,
                'adjusted_age': 1,
                'price': '123',
            },
        ),
        (
            'Renault',
            'Logan',
            2020,
            200,
            {
                'mark_code': 'RENAULT',
                'model_code': 'LOGAN',
                'year': 2020,
                'adjusted_age': 0,
                'price': '321',
            },
        ),
        (
            'qwe',
            'asd',
            2015,
            404,
            {'code': 'NOT_FOUND', 'message': 'Mark/model not found'},
        ),
    ],
)
@pytest.mark.config(
    CARS_CATALOG_PRICES_CLARIFICATION={
        'enable': True,
        'default_price': 123,
        'override': {'Renault Logan 2020': 321},
        'exclude': [{'brand': 'Vaz'}],
    },
)
async def test_check(
        web_app_client,
        patch,
        mark,
        model,
        year,
        expected_status,
        expected_data,
):
    @patch('cars_catalog.components.prices_source.Component.load_prices')
    async def _load(*args, **kwargs):
        return {2000: decimal.Decimal(100500)}

    response = await web_app_client.get(
        '/v1/vehicles/check-stats',
        params={'mark': mark, 'model': model, 'year': year},
    )
    data = await response.json()
    assert data == expected_data
    assert response.status == expected_status
