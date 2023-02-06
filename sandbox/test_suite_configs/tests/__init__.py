import os
import yaml

from sandbox.projects.browser.autotests.regression.dbro.DbroRegressionInit.test_suite_configs import TEST_SUITE_CONFIGS
from sandbox.projects.browser.autotests.regression.common import load_suites_info


def get_configs_path():
    import yatest.common
    return os.path.join(os.path.abspath(yatest.common.test_source_path()), '..')


def get_configs():
    import yatest.common
    configs_path = os.path.join(os.path.abspath(yatest.common.test_source_path()), '..')
    return [config_name for config_name in os.listdir(configs_path) if config_name.endswith('.yaml')]


def check_config_is_valid(config_path):
    with open(config_path, 'r') as f:
        config = yaml.load(f)
    load_suites_info(config)


def test_configs_are_valid():
    for config_name in get_configs():
        check_config_is_valid(os.path.join(get_configs_path(), config_name))


def test_all_configs_are_in_task_parameters():
    configs = get_configs()
    assert set(configs) == set(TEST_SUITE_CONFIGS), ('All .yaml files from folder "test_suite_configs" should be '
                                                     'listed in __init__.py file in that directory and vice versa. '
                                                     'Sorry, thats temporary solution')
