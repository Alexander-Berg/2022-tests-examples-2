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

taxi_fleet_management_api = fastcgi.create_client_fixture(
    'taxi_fleet_management_api',
)


@pytest.fixture(autouse=True)
def dispatcher_access_control(mockserver):
    @mockserver.json_handler(auth.DAC_MOCK_URL)
    def mock_callback(request):
        request.get_data()
        assert request.headers.get(auth.USER_TICKET_HEADER) == auth.USER_TICKET
        return {'grants': [{'id': 'map'}]}

    return mock_callback
