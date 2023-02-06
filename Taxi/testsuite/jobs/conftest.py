import os

import pytest

from taxi_tests.utils import yaml_util


pytest_plugins = [
    # Self client fixture
    'jobs.taxi_jobs',
    # Settings fixture
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
    'tests_plugins.mock_geoareas',
    'tests_plugins.config_service_defaults',
]


@pytest.fixture(scope='session')
def service_yaml():
    service_yaml_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../service.yaml'),
    )
    return yaml_util.load_file(service_yaml_path)


@pytest.fixture(scope='session')
def mongodb_local(mongodb_local_create, service_yaml):
    return mongodb_local_create(
        service_yaml.get('mongo', {}).get('collections', []),
    )
