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
    'tests_plugins.mock_bss',
    'tests_plugins.mock_candidates',
    'tests_plugins.mock_conductor',
    'tests_plugins.mock_individual_tariffs',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_tracker',
    'tests_plugins.mock_geoareas',
    'tests_plugins.mock_geofence',
    'tests_plugins.mock_billing_orders',
    'tests_plugins.mock_driver_tags',
    'tests_plugins.mock_cars_catalog',
    'tests_plugins.pgsupport_fixture',
    'tests_plugins.config_service_defaults',
]


@pytest.fixture(autouse=True)
def mock_expired_drivers(mockserver):
    @mockserver.json_handler('/tracker/service/exp_gps_drivers')
    def mock_nearest_drivers(request):
        return {'ids': []}


taxi_labor = fastcgi.create_client_fixture(
    'taxi_labor', scope='function', daemon_deps=('geofence',),
)
