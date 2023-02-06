# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pathlib
import string

import pytest
from stq_runner_plugins import *  # noqa: F403 F401
import yaml
import yatest.common

USERVER_CONFIG_HOOKS = ['userver_config_stq_runner']


@pytest.fixture(scope='session')
def userver_config_stq_runner(
        worker_id, testsuite_build_dir, service_source_dir,
):
    def patch_config(config, config_vars):
        if 'stq_config_path' not in config_vars:
            return
        stq_config_path = yatest.common.source_path(
            'taxi/uservices/services/stq-runner/'
            'testsuite/configs/stq_config.yaml',
        )
        config_vars['stq_config_path'] = stq_config_path
        with pathlib.Path(stq_config_path).open() as fp:
            stq_config = yaml.safe_load(fp)

        new_path = testsuite_build_dir.joinpath(f'stq_config_{worker_id}.yaml')
        substitution_vars = {
            'stq_service_source_dir': service_source_dir,
            'stq_worker_executer': yatest.common.binary_path(
                'taxi/uservices/services/stq-runner/testsuite/workers/workers',
            ),
        }

        stq_config = _do_substitution(stq_config, substitution_vars)

        testsuite_build_dir.mkdir(parents=True, exist_ok=True)
        with new_path.open('w') as fp:
            yaml.safe_dump(stq_config, fp, default_flow_style=False)

        config_vars['stq_config_path'] = str(new_path)

    return patch_config


def _do_substitution(root, substitution_vars):
    if isinstance(root, str):
        resolved = string.Template(root)
        resolved = resolved.substitute(substitution_vars)
        return resolved
    if isinstance(root, list):
        new_list = []
        for value in root:
            new_list.append(_do_substitution(value, substitution_vars))
        return new_list
    if isinstance(root, dict):
        new_dict = {}
        for key, value in root.items():
            new_dict[key] = _do_substitution(value, substitution_vars)
        return new_dict
    return root
