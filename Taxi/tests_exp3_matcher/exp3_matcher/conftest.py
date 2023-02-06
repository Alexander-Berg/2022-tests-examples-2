# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from exp3_matcher_plugins import *  # noqa: F403 F401
import pytest


USERVER_CONFIG_HOOKS = ['patch_exp3_logger']


@pytest.fixture(scope='session')
def patch_exp3_logger(worker_id, testsuite_build_dir):
    def patch_config(config, config_vars):
        exp3_log_file_path = testsuite_build_dir / 'exp3-matched.log'
        if exp3_log_file_path.exists():
            exp3_log_file_path.unlink()
        config['components_manager']['components']['logging']['loggers'][
            'exp3'
        ]['file_path'] = str(exp3_log_file_path)

    return patch_config


@pytest.fixture(autouse=True)
def always_flush_exp3_log_in_tests(testpoint):
    @testpoint('exp3::need_flush_log')
    def _need_flush_log(data):
        pass
