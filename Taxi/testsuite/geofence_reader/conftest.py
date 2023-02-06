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
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.config_service_defaults',
]


@pytest.fixture
def taxi_geofence(_taxi_geofence_client, request):
    marker = request.node.get_marker('taxi_geofence')
    options = marker.kwargs if marker else {}
    if not options.get('skip_propagate_to_master'):
        response = _taxi_geofence_client.post(
            '/input/replication-state', data='MasterOk',
        )
        assert response.status_code == 200
    return _taxi_geofence_client


_taxi_geofence_client = fastcgi.create_client_fixture('taxi_geofence_reader')
