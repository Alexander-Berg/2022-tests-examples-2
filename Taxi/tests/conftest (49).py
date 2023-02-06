import functools
import pathlib
import subprocess
from typing import List
from typing import Optional

import pytest
import yaml

from taxi_schemas import configs


ADDED = 'new file'
MODIFIED = 'modified'


pytest_plugins = [
    # Taxi Testsuite
    'testsuite.pytest_plugin',
    'testsuite.databases.mongo.pytest_plugin',
    'testsuite.plugins.envinfo',
    # Schemas plugins
    'tests.plugins.mongo_plugin',
]


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
    parser.addoption(
        '--all-configs',
        action='store_true',
        help='Check all configs files (use after change tests)',
    )


def pytest_generate_tests(metafunc):
    if 'check_path_all' in metafunc.fixturenames:
        paths = []
        if metafunc.config.getoption('--all-configs'):
            paths = configs.get_all_configs_paths()
        metafunc.parametrize('check_path_all', paths)
        if paths:
            return

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
        paths = get_config_paths_func([MODIFIED])
        metafunc.parametrize('modified_config_path', paths)
    if 'new_config_path' in metafunc.fixturenames:
        paths = get_config_paths_func([ADDED])
        metafunc.parametrize('new_config_path', paths)
    if 'new_and_modified_config_path' in metafunc.fixturenames:
        paths = get_config_paths_func([ADDED, MODIFIED])
        metafunc.parametrize('new_and_modified_config_path', paths)

    if 'new_and_modified_definition_path' in metafunc.fixturenames:
        paths = get_modified_definition_paths(
            [ADDED, MODIFIED], with_local=with_local,
        )
        metafunc.parametrize('new_and_modified_definition_path', paths)
    if 'config_with_possible_modification' in metafunc.fixturenames:
        defs_modified = get_modified_definition_paths(
            [MODIFIED], with_local=with_local,
        )
        if defs_modified:
            paths = []
            for path in configs.get_all_configs_paths():
                with open(path, 'r') as cfg:
                    config_raw = cfg.read()
                    if any(
                            str(def_path).split(configs.DEFINITIONS_PATH)[1]
                            in config_raw
                            for def_path in defs_modified
                    ):
                        paths.append(path)
            paths.extend(get_config_paths_func([ADDED, MODIFIED]))
            metafunc.parametrize('config_with_possible_modification', paths)
        else:
            paths = get_config_paths_func([ADDED, MODIFIED])
            metafunc.parametrize('config_with_possible_modification', paths)


@pytest.fixture(scope='session')
def mongo_extra_connections():
    return ('connection_foo',)


def fetch() -> None:
    subprocess.run(['arc', 'fetch', 'trunk'], check=True)


def get_merge_base():
    process = subprocess.run(
        ['arc', 'merge-base', 'HEAD', 'arcadia/trunk'],
        stdout=subprocess.PIPE,
        encoding='utf-8',
        check=True,
    )

    return process.stdout.strip()


def get_modified_configs_paths(
        filter_opt: List[str], with_local: bool = False,
) -> List[pathlib.Path]:
    paths = []

    for declarations_dir in configs.get_declarations_dirs():

        modified_configs = get_modified_paths(
            declarations_dir, filter_opt, with_local,
        )

        paths.extend(modified_configs)
    return paths


def get_modified_definition_paths(
        filter_opt: List[str], with_local: bool = False,
) -> List[pathlib.Path]:
    paths = []

    for definitions_dir in configs.get_definitions_dirs():
        modifiied_definitions = get_modified_paths(
            definitions_dir, filter_opt, with_local,
        )
        paths.extend(modifiied_definitions)

    return paths


def get_modified_paths(
        dir_path: pathlib.Path,
        filter_opt: List[str],
        with_local: bool = False,
) -> List[pathlib.Path]:
    merge_base = get_merge_base()
    paths = extract_paths(merge_base, filter_opt, with_local, dir_path)

    if with_local and ADDED in filter_opt:
        untracked_paths = get_untracked_paths(dir_path)
        paths.extend(untracked_paths)

    return paths


def extract_paths(
        merge_base: str,
        diff_filter: List[str],
        with_local: bool,
        dir_path: pathlib.Path,
) -> List[pathlib.Path]:
    cmd = ['arc', 'diff', '--name-status', '--json', merge_base]
    filter_yaml = False
    if not with_local:
        cmd.append('HEAD')
    else:
        filter_yaml = True

    cmd.extend(['--', str(dir_path.relative_to(configs.ARCADIA_ROOT))])

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        encoding='utf-8',
        check=True,
        cwd=configs.ARCADIA_ROOT,
    )
    output = process.stdout
    content = yaml.load(output, getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
    if not content:
        return []
    changes = content[0].get('names', [])
    paths = []
    for change in changes:
        status = change.get('status')
        path = change.get('path')
        if not status or not path:
            continue
        if status in diff_filter:
            paths.append(configs.ARCADIA_ROOT / path)
    if filter_yaml:
        return [path for path in paths if path.suffix == '.yaml']
    return paths


def get_untracked_paths(dir_path: pathlib.Path) -> List[pathlib.Path]:

    process = subprocess.run(
        [
            'arc',
            'status',
            '--json',
            '--',
            str(dir_path.relative_to(configs.ARCADIA_ROOT)),
        ],
        stdout=subprocess.PIPE,
        encoding='utf-8',
        check=True,
        cwd=configs.ARCADIA_ROOT,
    )
    output = process.stdout
    content = yaml.load(output, getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
    untracked_list = content['status'].get('untracked', [])
    return [pathlib.Path(entry['path']) for entry in untracked_list]


def get_specific_paths(names: Optional[List[str]]) -> List[pathlib.Path]:
    configs_files = []

    for name in names or []:
        if configs.YAML_EXT not in name:
            name += configs.YAML_EXT

            config_abspath = get_config_abspath(name)
            configs_files.append(config_abspath)

    return configs_files


# pylint: disable=useless-else-on-loop
def get_config_abspath(name: str) -> pathlib.Path:
    for declarations_dir in configs.get_declarations_dirs():
        path = declarations_dir / name
        if path.exists():
            if not path.is_file():
                raise TypeError(f'Config {name} is not file')
            return path
    else:
        raise FileNotFoundError(f'Config {name} not found')
