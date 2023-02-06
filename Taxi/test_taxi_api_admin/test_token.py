import pytest


@pytest.mark.parametrize('handler', ['/me', '/me/'])
async def test_me(taxi_api_admin_client, handler):
    taxi_api_admin_client.app.secdist['settings_override'][
        'TAXI_ADMIN_CSRF_TOKEN'
    ] = 'temp'
    response = await taxi_api_admin_client.request(
        'GET',
        handler,
        headers={'uid': 'elrrusso'},
        cookies={'yandexuid': '24248601603782976'},
    )
    assert response.status == 200
    data = await response.json()
    assert data['csrf_token'] and len(data) == 1


async def test_me_without_yandexuid(taxi_api_admin_client):
    taxi_api_admin_client.app.secdist['settings_override'][
        'TAXI_ADMIN_CSRF_TOKEN'
    ] = 'temp'
    response = await taxi_api_admin_client.request('GET', '/me')
    assert response.status == 403
