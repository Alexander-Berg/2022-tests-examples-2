import pytest


URLS_WITH_DATA_NAME = [
    ('phones', 'phone'),
    ('emails', 'email'),
    ('driver_licenses', 'license'),
    ('yandex_logins', 'login'),
    ('tins', 'tin'),
    ('identifications', 'identification'),
    ('telegram_logins', 'login'),
]


@pytest.mark.parametrize('url, data_name', URLS_WITH_DATA_NAME)
async def test_find_hash_collision(taxi_personal, url, data_name):
    response = await taxi_personal.post(
        f'{url}/find',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={data_name: 'COLLISION_VALUE'},
    )
    assert response.status_code == 500


@pytest.mark.parametrize('url, data_name', URLS_WITH_DATA_NAME)
async def test_store_hash_collision(taxi_personal, url, data_name):
    response = await taxi_personal.post(
        f'{url}/store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={data_name: 'COLLISION_VALUE', 'validate': False},
    )
    assert response.status_code == 500


@pytest.mark.parametrize('url, data_name', URLS_WITH_DATA_NAME)
async def test_bulk_store_hash_collision(taxi_personal, url, data_name):
    request_items = [{data_name: 'COLLISION_VALUE'}]
    response = await taxi_personal.post(
        f'{url}/bulk_store',
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': request_items, 'validate': False},
    )
    assert response.status_code == 500
