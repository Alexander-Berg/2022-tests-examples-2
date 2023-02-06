import json
import os
import yaml

import pytest

from sandbox.projects.browser.autotests_qa_tools.configs.functionalities import UPLOAD_CONFIG_NAME


def configs_path():
    import yatest.common
    return os.path.join(os.path.abspath(yatest.common.test_source_path()), '..')


def get_configs():
    configs_folder = configs_path()
    for r, d, f in os.walk(configs_folder):
        for component_file in f:
            if component_file.endswith('.yaml'):
                config_path = os.path.join(r, component_file)
                yield pytest.param(config_path, id=os.path.relpath(config_path, configs_folder))


def get_projects():
    configs_folder = configs_path()
    for project_folder in next(os.walk(configs_folder))[1]:
        if project_folder == 'tests':
            continue
        yield pytest.param(os.path.join(configs_folder, project_folder), id=project_folder)


@pytest.mark.parametrize('config_path', get_configs())
def test_configs_are_valid(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    assert config is None or isinstance(config, dict)


@pytest.mark.parametrize('project_directory', get_projects())
def test_all_projects_have_upload_configs(project_directory):
    upload_config = str(os.path.join(project_directory, UPLOAD_CONFIG_NAME))
    assert os.path.isfile(upload_config)
    with open(upload_config, 'r') as f:
        config = json.load(f)
    assert 'testpalm_projects' in config
    assert isinstance(config['testpalm_projects'], list)
