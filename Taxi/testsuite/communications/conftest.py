import pytest

from tests_plugins import fastcgi

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
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_driver_tags',
    'tests_plugins.mock_territories',
    'tests_plugins.config_service_defaults',
    'tests_plugins.mock_driver_authorizer',
]

taxi_communications = fastcgi.create_client_fixture('taxi_communications')


@pytest.fixture(autouse=True)
def driver_profiles(mockserver):
    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            '{"profiles":[{"data":{"taximeter_version":"8.49 (10782)"},'
            '"park_driver_profile_id":"1488_driver"}]}',
            200,
        )

    return mock_driver_profiles
