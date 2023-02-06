import functools
import os
import subprocess
from typing import List
from typing import Optional

import pytest

from taxi_schemas import configs

ADDED = 'A'
MODIFIED = 'M'

pytest_plugins = [
    # Taxi Testsuite
    'testsuite.pytest_plugin',
    'testsuite.databases.mongo.pytest_plugin',
    'testsuite.plugins.envinfo',
    # Schemas plugins
    'tests.plugins.mongo_plugin',
]


class GitRemoteException(Exception):
    """Raise when there is no taxi/schemas.git somehow."""


def pytest_addoption(parser):
    parser.addoption(
        '--modified-config-path',
        action='append',
        default=[],
        help='list of modified configs paths',
    )
    parser.addoption(
        '--new-config-path',
        action='append',
        default=[],
        help='list of new configs paths',
    )
    parser.addoption(
        '--new-and-modified-config-path',
        action='append',
        default=[],
        help='list of new and modified configs paths',
    )
    parser.addoption(
        '--check-configs',
        nargs='+',
        help=(
            'check custom configs. '
            'Example name `taxi-exp/EXP_ALERT_SETTINGS.yaml`'
        ),
    )
    parser.addoption(
        '--with-local-changes',
        action='store_true',
        help='Also test configs changed only locally and not committed',
    )
    parser.addoption(
        '--no-fetch',
        action='store_true',
        help='Do not fetch upstream before check (to use locally)',
    )


def pytest_generate_tests(metafunc):
    if 'specific_check_path' in metafunc.fixturenames:
        paths = get_specific_paths(
            metafunc.config.getoption('--check-configs'),
        )
        metafunc.parametrize('specific_check_path', paths)
        if paths:
            return
    if not metafunc.config.getoption('--no-fetch'):
        fetch()
    with_local = metafunc.config.getoption('--with-local-changes')
    get_config_paths_func = functools.partial(
        get_modified_configs_paths, with_local=with_local,
    )
    if 'modified_config_path' in metafunc.fixturenames:
        paths = get_config_paths_func(MODIFIED)
        metafunc.parametrize('modified_config_path', paths)
    if 'new_config_path' in metafunc.fixturenames:
        paths = get_config_paths_func(ADDED)
        metafunc.parametrize('new_config_path', paths)
    if 'new_and_modified_config_path' in metafunc.fixturenames:
        paths = get_config_paths_func(ADDED + MODIFIED)
        metafunc.parametrize('new_and_modified_config_path', paths)

    if 'new_and_modified_definition_path' in metafunc.fixturenames:
        paths = get_modified_definition_paths(
            ADDED + MODIFIED, with_local=with_local,
        )
        metafunc.parametrize('new_and_modified_definition_path', paths)
    if 'config_with_possible_modification' in metafunc.fixturenames:
        defs_modified = get_modified_definition_paths(
            MODIFIED, with_local=with_local,
        )
        if defs_modified:
            paths = []
            for path in configs.get_all_config_files_path():
                with open(path, 'r') as cfg:
                    config_raw = cfg.read()
                    if any(
                            def_path.lstrip(configs.DEFINITIONS_PATH + '/')
                            in config_raw
                            for def_path in defs_modified
                    ):
                        paths.append(path)
            paths.extend(get_config_paths_func(ADDED + MODIFIED))
            metafunc.parametrize('config_with_possible_modification', paths)
        else:
            paths = get_config_paths_func(ADDED + MODIFIED)
            metafunc.parametrize('config_with_possible_modification', paths)


@pytest.fixture(scope='session')
def mongo_extra_connections():
    return ('connection_foo',)


def _get_remote_name() -> str:
    stdout, _ = subprocess.Popen(
        'git remote -v'.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).communicate()
    for line in stdout.decode('utf-8').split('\n'):
        if 'taxi/schemas.git' in line:
            return line.split('\t')[0]
    raise GitRemoteException(
        'There is no taxi/schemas.git. "git remote -v" returns:\n{}'.format(
            stdout.decode('utf-8'),
        ),
    )


def fetch():
    subprocess.run(['git', 'fetch', _get_remote_name()], check=True)


def get_merge_base():
    process = subprocess.run(
        ['git', 'merge-base', 'HEAD', '{}/develop'.format(_get_remote_name())],
        stdout=subprocess.PIPE,
        encoding='utf-8',
        check=True,
    )
    return process.stdout.strip()


def get_modified_configs_paths(diff_filter, with_local=False):
    paths = get_modified_paths(
        'schemas/configs/declarations/', diff_filter, with_local,
    )
    return paths


def get_modified_definition_paths(diff_filter, with_local=False):
    return get_modified_paths(
        'schemas/configs/definitions', diff_filter, with_local,
    )


def get_modified_paths(dir_path, diff_filter, with_local=False):
    merge_base = get_merge_base()
    main_part = [
        'git',
        'diff',
        '--name-only',
        f'--diff-filter={diff_filter}',
        merge_base,
    ]
    if not with_local:
        main_part.append('HEAD')
        path_part = ['--', dir_path]
    else:
        path_part = ['--', dir_path + '/**.yaml']
    process = subprocess.run(
        main_part + path_part,
        stdout=subprocess.PIPE,
        encoding='utf-8',
        check=True,
    )
    paths = process.stdout.splitlines()
    if with_local and ADDED in diff_filter:
        process_untracked = subprocess.run(
            [
                'git',
                'ls-files',
                '--others',
                '--exclude-standard',
                '--',
                dir_path + '/**.yaml',
            ],
            stdout=subprocess.PIPE,
            encoding='utf-8',
            check=True,
        )
        paths.extend(process_untracked.stdout.splitlines())

    return [path.strip() for path in paths]


def get_specific_paths(names: Optional[List[str]]) -> List[str]:
    configs_files = []
    for name in names or []:
        if configs.YAML_EXT not in name:
            name += configs.YAML_EXT
        path = os.path.join(configs.PATH_TO_CONFIG_YAML_FILES, name)
        if not os.path.exists(path):
            raise ValueError(f'Config {name} not found')
        if not os.path.isfile(path):
            raise TypeError(f'Config {name} is not file')

        configs_files.append(path)
    return configs_files
