import pathlib
import ssl

import pytest

from testsuite.daemons import service_client

pytest_plugins = [
    'testsuite.pytest_plugin',
    # Databases
    'testsuite.databases.mongo.pytest_plugin',
    'testsuite.databases.pgsql.pytest_plugin',
    'testsuite.databases.redis.pytest_plugin',
    # taxi plugins
    'taxi_testsuite.plugins.config',
    'taxi_testsuite.plugins.experiments3',
    'taxi_testsuite.plugins.localizations',
    'taxi_testsuite.plugins.mocks.pytest_plugin',
    'taxi_testsuite.plugins.databases.yt.pytest_plugin',
    # Yamlcases
    'taxi_testsuite.plugins.yamlcase.pytest_plugin',
]


@pytest.fixture
def mockserver_client(
        mockserver, service_client_default_headers, service_client_options,
):
    return service_client.Client(
        mockserver.base_url,
        headers={
            **service_client_default_headers,
            mockserver.trace_id_header: mockserver.trace_id,
        },
        **service_client_options,
    )


@pytest.fixture
def mockserver_ssl_client(
        mockserver_ssl,
        mockserver_ssl_info,
        service_client_default_headers,
        service_client_options,
):
    ssl_info = mockserver_ssl_info.ssl
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH, cafile=ssl_info.cert_path,
    )
    return service_client.Client(
        mockserver_ssl.base_url,
        ssl_context=ssl_context,
        headers={
            **service_client_default_headers,
            mockserver_ssl.trace_id_header: mockserver_ssl.trace_id,
        },
        **service_client_options,
    )


@pytest.fixture(scope='session')
def config_service_defaults():
    return {}


@pytest.fixture(scope='session')
def mongo_schema_directory():
    return str(
        pathlib.Path(__file__)
        .parent.joinpath('../tests/schemas/mongo')
        .absolute(),
    )
