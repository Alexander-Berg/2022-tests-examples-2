import os

import pathlib

from dmp_suite.py_env.utils import get_root_config_path
from tests.workflow_test import assert_config_extensions, valid_config_file


def test_root_config_extensions():
    config_path = pathlib.Path(get_root_config_path())
    assert_config_extensions(config_path)


def path_is_relative_to(path, parent):
    # TODO DMPDEV-4193 use pathlib.Path.is_relative_to
    return parent in path.parents


def test_no_local_configs(inside_ci):
    if not inside_ci:
        # local configs are allowed for local development
        return

    config_path = pathlib.Path(get_root_config_path())
    local_path = config_path / 'local'
    templates_path = local_path / 'templates'
    local_configs = []
    for path in local_path.rglob('*'):
        if path.is_file():
            # templates are allowed
            if not path_is_relative_to(path, templates_path):
                if valid_config_file(path):
                    local_configs.append(path)

    msg = (
        f'Local config files: {", ".join(str(f) for f in local_configs)}. '
        'Make sure not to commit these files'
    )
    assert not local_configs, msg
