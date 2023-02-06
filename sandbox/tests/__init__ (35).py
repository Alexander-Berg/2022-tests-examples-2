import os
import yaml
import json
import pytest

from sandbox.common.utils import singleton
from sandbox.projects.browser.autotests_qa_tools.common import REGRESSION_GROUPS_ACTIVITIES
from sandbox.projects.browser.autotests_qa_tools.configs.regression import (
    RegressionConfigs, SCHEME_FILE_NAME, SETTINGS_SCHEME_FILE_NAME, DEFAULT_SETTINGS_FILE_NAME,
    validate_regression_config, validate_regression_settings)


@singleton
def load_groups():
    import yatest.common
    testing_groups_path = os.path.join(os.path.dirname(yatest.common.test_source_path()),
                                       "..", "testing_groups", "testing_groups.yaml")
    with open(testing_groups_path, "r") as _f:
        all_groups = yaml.load(_f)

    return {
        name: data for name, data in all_groups.iteritems() if any(_x in REGRESSION_GROUPS_ACTIVITIES for _x in data['activity'])
    }


def get_module_configs(module):
    import yatest.common
    base_folder = os.path.join(os.path.abspath(yatest.common.test_source_path()), "..")
    configs_folder = os.path.join(base_folder, os.path.basename(os.path.dirname(module.__file__)))

    with open(os.path.join(configs_folder, SCHEME_FILE_NAME), "r") as _scheme:
        config_scheme_data = json.load(_scheme)
    with open(os.path.join(base_folder, SETTINGS_SCHEME_FILE_NAME), "r") as _scheme:
        settings_scheme_data = json.load(_scheme)

    for config_name in os.listdir(configs_folder):
        if config_name.endswith('.yaml') and config_name != DEFAULT_SETTINGS_FILE_NAME:
            yield {
                "config_scheme": config_scheme_data,
                "settings_scheme": settings_scheme_data,
                "avalible_groups": load_groups(),
                "config_path": os.path.join(configs_folder, config_name),
                "module": module
            }


def get_all_configs():
    for module in [_m.value for _m in RegressionConfigs]:
        for _c in get_module_configs(module):
            yield pytest.param(_c, id="{}/{}".format(os.path.basename(os.path.dirname(_c["config_path"])),
                                                     os.path.basename(_c["config_path"])))


@pytest.mark.parametrize('config', get_all_configs())
def test_config_is_valid(config):
    with open(config["config_path"], "r") as _config:
        config_data = yaml.load(_config)
    validate_regression_config(config_data,
                               config_scheme=config["config_scheme"],
                               settings_scheme=config["settings_scheme"],
                               avalible_groups=config["avalible_groups"],
                               all_settings_required=False)

    assert os.path.basename(config["config_path"]) in config["module"].TEST_SUITE_CONFIGS, (
        'All .yaml files from folder "test_suite_configs" should be '
        'listed in __init__.py file in that directory and vice versa. '
        'Sorry, thats temporary solution')


@pytest.mark.parametrize('module', RegressionConfigs)
def test_default_settings_is_valid(module):

    module = module.value
    import yatest.common

    configs_folder = os.path.join(os.path.abspath(yatest.common.test_source_path()),
                                  "..", os.path.basename(os.path.dirname(module.__file__)))
    with open(os.path.join(configs_folder, DEFAULT_SETTINGS_FILE_NAME), "r") as _f:
        settings = yaml.load(_f)
    with open(os.path.join(os.path.abspath(yatest.common.test_source_path()), "..", SETTINGS_SCHEME_FILE_NAME), "r") as _scheme:
        settings_scheme = json.load(_scheme)

    validate_regression_settings(settings,
                                 settings_scheme,
                                 load_groups(),
                                 all_settings_required=True)
