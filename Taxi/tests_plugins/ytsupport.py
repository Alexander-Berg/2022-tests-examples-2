import pathlib

import pytest

from taxi_testsuite.plugins.databases.yt import discover

USERVER_CONFIG_HOOKS = ['_userver_config_reset_default_yt_proxy']


@pytest.fixture(scope='session')
def yt_service_schemas(yt_service_schemas, testsuite_source_dir: pathlib.Path):
    schemas_yt = testsuite_source_dir.joinpath('schemas', 'yt')
    return discover.find_schemas([schemas_yt])


@pytest.fixture(scope='session')
def _userver_config_reset_default_yt_proxy(yt_proxy):
    def _reset_default_yt_proxy(config, config_vars):
        config_vars['testsuite_yt_cluster'] = yt_proxy

    return _reset_default_yt_proxy
