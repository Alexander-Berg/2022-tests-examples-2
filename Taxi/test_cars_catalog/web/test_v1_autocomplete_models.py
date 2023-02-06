import pytest


OK_PARAMS = [
    ('Toyota', '', ['Camry', 'Corolla']),
    ('Toyota', 'c', ['Camry', 'Corolla']),
    ('Toyota', 'C', ['Camry', 'Corolla']),
    ('Toyota', 'cA', ['Camry']),
]


@pytest.mark.parametrize('brand, text_query, models', OK_PARAMS)
async def test_ok(web_app_client, brand, text_query, models):
    response = await web_app_client.post(
        '/cars-catalog/v1/autocomplete-models',
        params={'brand': brand, 'text_query': text_query},
    )

    assert response.status == 200, response.text
    assert await response.json() == {'brand': brand, 'models': models}


async def test_not_found(web_app_client):
    response = await web_app_client.post(
        '/cars-catalog/v1/autocomplete-models',
        params={'brand': 'trash', 'text_query': ''},
    )

    assert response.status == 404, await response.text
    assert await response.json() == {
        'code': '404',
        'message': 'brand `trash` was not found',
    }
