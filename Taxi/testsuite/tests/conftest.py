import os.path

import pytest

from taxi_tests.daemons.asyncio import service_client

pytest_plugins = [
    'taxi_tests.daemons.asyncio.plugins',
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.experiments3',
    'taxi_tests.plugins.localizations',
    'taxi_tests.plugins.mocked_time',
    'taxi_tests.plugins.mocks.asyncio.mock_yt',
    'taxi_tests.plugins.mocks.configs_service',
    'taxi_tests.plugins.mocks.experiments3_proxy',
    'taxi_tests.plugins.mocks.localizations_replica',
    'taxi_tests.plugins.asyncio.loop',
    'taxi_tests.plugins.asyncio.mockserver',
    'taxi_tests.plugins.asyncio.testpoint',
    'tests.plugins.mongodb.mongodb_settings',
]


class Settings:
    def __init__(self):
        # pylint: disable=invalid-name
        self.INITIAL_DATA_PATH = []
        self.POSTGRESQL_CONNECTIONS = ['foo', 'bar']
        self.MONGO_CONNECTIONS = None


def pytest_addoption(parser):
    testsuite_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..'),
    )
    parser.addoption(
        '--build-dir', default=os.path.join(testsuite_dir, 'build'),
    )
    parser.addoption(
        '--testsuite-dir', default=testsuite_dir,
    )


@pytest.fixture(scope='session')
def settings(mongo_host):
    result = Settings()
    result.MONGO_CONNECTIONS = {
        'local_connection': mongo_host,
    }
    return result


@pytest.fixture
def mockserver_client(mockserver, service_client_options):
    return service_client.Client(
        mockserver.base_url, **service_client_options,
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
