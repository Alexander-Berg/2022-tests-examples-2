import json

import pytest

from tests_plugins import fastcgi

from . import auth

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # Testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # Local mocks
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.config_service_defaults',
    'tests_plugins.driver_categories_api',
]

taxi_fleet_api_external = fastcgi.create_client_fixture(
    'taxi_fleet_management_api_fleet_api_external',
)


@pytest.fixture(autouse=True)
def api_keys(mockserver):
    @mockserver.json_handler(auth.API_KEYS_MOCK_URL)
    def mock_callback(request):
        assert request.headers.get('Content-Type') == 'application/json'
        assert request.headers.get(auth.API_KEY_HEADER) == auth.API_KEY
        request_json = json.loads(request.get_data())
        assert request_json['consumer_id'] == auth.CONSUMER_ID
        assert request_json['client_id'] == auth.CLIENT_ID
        assert request_json['entity_id']
        assert request_json['permission_ids']
        return {'key_id': auth.KEY_ID}

    return mock_callback
