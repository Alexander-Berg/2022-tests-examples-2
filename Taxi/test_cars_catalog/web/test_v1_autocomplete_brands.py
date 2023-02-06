import pytest


OK_PARAMS = [
    (
        '',
        [
            'Aston Martin',
            'Audi',
            'BMW',
            'Ferrari',
            'Ford',
            'LADA (ВАЗ)',
            'Toyota',
        ],
    ),
    ('a', ['Aston Martin', 'Audi']),
    ('ord', []),
    ('f', ['Ferrari', 'Ford']),
    ('F', ['Ferrari', 'Ford']),
    ('   f   ', ['Ferrari', 'Ford']),
    ('fOrD', ['Ford']),
    ('toy', ['Toyota']),
]


@pytest.mark.parametrize('text_query, brands', OK_PARAMS)
async def test_ok(web_app_client, text_query, brands):
    response = await web_app_client.post(
        '/cars-catalog/v1/autocomplete-brands',
        params={'text_query': text_query},
    )

    assert response.status == 200, await response.text
    assert await response.json() == {'brands': brands}
