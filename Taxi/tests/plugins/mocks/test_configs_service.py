import pytest


@pytest.fixture(scope='session')
def config_service_defaults():
    return {
        'foo': 1,
        'bar': 'maurice',
    }


@pytest.fixture(autouse=True)
def deps(taxi_config):
    pass


async def test_config_default(mockserver_client):
    response = await mockserver_client.get('configs-service/configs/values')
    assert response.status_code == 200

    data = response.json()
    assert 'updated_at' in data
    assert data['configs'] == {
        'foo': 1,
        'bar': 'maurice',
    }


@pytest.mark.config(foo=2)
async def test_config_override(mockserver_client):
    response = await mockserver_client.get('configs-service/configs/values')
    assert response.status_code == 200

    data = response.json()
    assert 'updated_at' in data
    assert data['configs'] == {
        'foo': 2,
        'bar': 'maurice',
    }


async def test_config_set(mockserver_client, taxi_config):
    taxi_config.set(foo=3)
    response = await mockserver_client.get('configs-service/configs/values')
    assert response.status_code == 200

    data = response.json()
    assert 'updated_at' in data
    assert data['configs'] == {
        'foo': 3,
        'bar': 'maurice',
    }
