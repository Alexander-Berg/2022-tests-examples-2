import pytest

from taxi_tests.daemons import service_client
from taxi_tests.utils import tracing

pytest_plugins = [
    'taxi_tests.daemons.plugins',
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.experiments3',
    'taxi_tests.plugins.localizations',
    'taxi_tests.plugins.mocked_time',
    'taxi_tests.plugins.mocks.stq',
    'taxi_tests.plugins.mocks.configs_service',
    'taxi_tests.plugins.mocks.experiments3_proxy',
    'taxi_tests.plugins.mocks.localizations_replica',
    'taxi_tests.plugins.loop',
    'taxi_tests.plugins.mockserver',
    'taxi_tests.plugins.testpoint',
    'tests.plugins.mongodb.mongo_schema_directory',
    # taxi plugins
    'taxi_testsuite.plugins.yamlcase.pytest_plugin',
]


@pytest.fixture
def mockserver_client(mockserver, service_client_options, trace_id):
    return service_client.Client(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: trace_id},
        **service_client_options,
    )


@pytest.fixture(scope='session')
def config_service_defaults():
    return {}


@pytest.fixture
def create_service_client(service_client_options):
    def _create_service_client(*args, **kwargs):
        options = {**service_client_options, **kwargs}
        return service_client.Client(*args, **options)

    return _create_service_client
