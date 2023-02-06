import requests

from taxi_tests import utils

BASE_URL = 'http://configs-admin.taxi.yandex.net'
NAME = 'TEST_CONFIG_SCHEMA'
ERROR_TIMEOUT_MSG = 'Schemas cache has not been updated in time'
WAITING_TIME = 100


def get_commit():
    url = 'http://configs-admin.taxi.yandex.net/v1/schemas/actual_commit/'
    response = requests.get(url)
    print('Get commit:', response.status_code, response.text)

    return response.json().get('commit') or ''


def update_definitions(actual_commit, new_commit, definitions):
    url = f'{BASE_URL}/v1/schemas/definitions/'
    response = requests.post(
        url,
        headers={'X-YaTaxi-Api-Key': 'configs_admin_token'},
        json={
            'actual_commit': actual_commit,
            'new_commit': new_commit,
            'definitions': definitions,
        },
    )
    print('Update definitions:', response.status_code, response.text)
    return response.json()


def update_schemas(actual_commit, new_commit, schemas, group):
    url = f'{BASE_URL}/v1/schemas/'
    response = requests.post(
        url,
        headers={'X-YaTaxi-Api-Key': 'configs_admin_token'},
        json={
            'actual_commit': actual_commit,
            'new_commit': new_commit,
            'schemas': schemas,
            'group': group,
        },
    )
    print('Update schemas:', response.status_code, response.text)
    return response.json()


def get_config(name):
    url = f'{BASE_URL}/v1/configs/{name}/'
    response = requests.get(url)
    print('Get config result:', response.status_code, response.text)
    return response.json()


def update_config(name, old_value, new_value):
    url = f'{BASE_URL}/v1/configs/{name}/'
    response = requests.post(
        url, json={'old_value': old_value, 'new_value': new_value},
    )
    print('Update config:', response.status_code, response.text)
    return response.json()


def wait_when_schemas_cache_updated(name):
    for _ in utils.wait_for(WAITING_TIME, ERROR_TIMEOUT_MSG):
        response = get_config(name)
        if response != {
                'code': 'CONFIG_NOT_FOUND',
                'message': f'Config `{name}` not found',
        }:
            return response
    return None


def clean_config(config):
    for field in (
            'services',
            'turn_off_immediately',
            'version',
            'value_version',
            'last_modification_time',
    ):
        config.pop(field, None)


def test():
    actual_commit = get_commit()

    assert (
        update_definitions(
            actual_commit,
            'new_commit',
            {'def.yaml': {'String': {'type': 'string'}}},
        )
        == {}
    )

    assert get_config(NAME) == {
        'code': 'CONFIG_NOT_FOUND',
        'message': f'Config `{NAME}` not found',
    }
    assert (
        update_schemas(
            'new_commit',
            'new_commit2',
            {
                NAME: {
                    'tags': ['notfallback'],
                    'default': 'default_string',
                    'description': 'description for test_config_schema',
                    'schema': {'type': 'string'},
                    'group': 'test_group',
                },
            },
            'test_group',
        )
        == {}
    )

    current_config = wait_when_schemas_cache_updated(NAME)
    clean_config(current_config)
    assert current_config == {
        'default': 'default_string',
        'value': 'default_string',
        'is_fallback': False,
        'is_technical': False,
        'name': 'TEST_CONFIG_SCHEMA',
        'group': 'test_group',
        'schema': {'type': 'string'},
        'description': 'description for test_config_schema',
        'tags': ['notfallback'],
        'maintainers': [],
    }

    assert update_config(NAME, current_config['value'], 'new_string') == {}

    new_config = get_config(NAME)
    clean_config(new_config)
    assert new_config == {
        'default': 'default_string',
        'value': 'new_string',
        'is_fallback': False,
        'is_technical': False,
        'name': 'TEST_CONFIG_SCHEMA',
        'group': 'test_group',
        'schema': {'type': 'string'},
        'description': 'description for test_config_schema',
        'tags': ['notfallback'],
        'maintainers': [],
    }
