import pathlib
from typing import Union

import pytest

_COMMON_PYTEST_PLUGINS = [
    # Testsuite plugins
    'testsuite.pytest_plugin',
    'testsuite.databases.mongo.pytest_plugin',
    'testsuite.databases.pgsql.pytest_plugin',
    'testsuite.databases.redis.pytest_plugin',
    'testsuite.databases.clickhouse.pytest_plugin',
    'testsuite.plugins.envinfo',
    'taxi_testsuite.plugins.servicetest',
    'taxi_testsuite.plugins.config',
    'taxi_testsuite.plugins.mocks.configs_service',
    'taxi_testsuite.plugins.mocks.stq',
    'taxi_testsuite.plugins.profiling',
    'taxi_testsuite.plugins.profiling_junitxml',
    'taxi_testsuite.plugins.yamlcase.pytest_plugin',
    # Local plugins
    'tests_plugins.api_coverage_plugin',
    'tests_plugins.config_service_defaults',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mongodb_settings',
    'tests_plugins.regenerate_config',
    'tests_plugins.service_logs_dumper_plugin',
    'tests_plugins.userver_caches',
    'tests_plugins.userver_dumps',
    'tests_plugins.userver_main',
    # pytest_userver
    'pytest_userver.plugins.log_capture',
    'pytest_userver.plugins.testpoint',
    # Yt support
    'taxi_testsuite.plugins.databases.yt.pytest_plugin',
    'tests_plugins.ytsupport',
    # YDB support
    'tests_plugins.databases.ydb.pytest_plugin',
]

try:
    import yatest.common
    _IS_ARCADIA = True
    pytest_plugins = [
        # YDB support
        *_COMMON_PYTEST_PLUGINS,
    ]
except ImportError:
    _IS_ARCADIA = False
    pytest_plugins = [
        # aiohttp plugin
        'aiohttp.pytest_plugin',
        *_COMMON_PYTEST_PLUGINS,
    ]


@pytest.fixture(scope='session')
def get_source_path(pytestconfig):
    def _get_source_path(path: Union[str, pathlib.Path]) -> pathlib.Path:
        if _IS_ARCADIA:
            full_path = pathlib.Path('taxi/uservices') / path
            return pathlib.Path(yatest.common.source_path(str(full_path)))
        return pathlib.Path(pytestconfig.rootdir) / path

    return _get_source_path


@pytest.fixture(scope='session')
def testsuite_output_dir(testsuite_build_dir):
    if _IS_ARCADIA:
        output_path = pathlib.Path(yatest.common.output_path('testsuite'))
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    return testsuite_build_dir
