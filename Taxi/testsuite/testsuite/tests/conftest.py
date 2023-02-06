import os
import ssl

import pytest

from taxi_tests.daemons import service_client

pytest_plugins = [
    'taxi_tests.pytest_plugin',
    # Databases
    'taxi_tests.databases.mongo.pytest_plugin',
    'taxi_tests.databases.pgsql.pytest_plugin',
    'taxi_tests.databases.redis.pytest_plugin',
    # taxi plugins
    'taxi_testsuite.plugins.config',
    'taxi_testsuite.plugins.experiments3',
    'taxi_testsuite.plugins.localizations',
    'taxi_testsuite.plugins.mocks.pytest_plugin',
    # Yamlcases
    'taxi_testsuite.plugins.yamlcase.pytest_plugin',
]


@pytest.fixture
def mockserver_client(mockserver, service_client_options):
    return service_client.Client(
        mockserver.base_url,
        service_headers={mockserver.trace_id_header: mockserver.trace_id},
        **service_client_options,
    )


@pytest.fixture
def mockserver_ssl_client(
        mockserver_ssl, mockserver_ssl_info, service_client_options,
):
    ssl_info = mockserver_ssl_info.ssl
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH, cafile=ssl_info.cert_path,
    )
    return service_client.Client(
        mockserver_ssl.base_url,
        service_headers={
            mockserver_ssl.trace_id_header: mockserver_ssl.trace_id,
        },
        ssl_context=ssl_context,
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


@pytest.fixture(scope='session')
def mongo_schema_directory():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'schemas', 'mongo'),
    )
