import os
import pathlib
import stat
import sys
from typing import Dict
from typing import List

import voluptuous

from codegen.plugin_manager import v3 as plugin_manager

ARC_ROOT_PATH = os.path.join('taxi', 'uservices')


CONFIGS_DIR = pathlib.Path('configs')
SERVICES_DIR = pathlib.Path('services')
TESTSUITE_LOCAL_DIR = pathlib.Path('testsuite')
TESTSUITE_SUBMODULE_DIR = pathlib.Path('submodules', 'testsuite')
USERVER_PYTEST_DIR = pathlib.Path('userver', 'testsuite', 'pytest_plugins')
TAXI_CONFIG_FALLBACK_JSON_PATH = pathlib.Path('taxi_config_fallback.json')
CONFIG_CACHE_JSON_PATH = pathlib.Path(
    'testsuite', 'configs', 'config_cache.json',
)
CONFIG_YAML_PATH = pathlib.Path('config.yaml')
CONFIG_VARS_TESTSUITE_YAML_PATH = pathlib.Path(
    CONFIGS_DIR, 'config_vars.testsuite.yaml',
)
SECDIST_PATH = pathlib.Path(TESTSUITE_LOCAL_DIR, CONFIGS_DIR, 'secdist.json')


class RepositoryGenerator(plugin_manager.PluginBase):
    # pylint: disable=R0201
    def generate(self, manager: plugin_manager.GenerateManager) -> None:
        testsuite_build_dir = pathlib.Path(
            manager.params.root_build_dir, TESTSUITE_LOCAL_DIR,
        )
        testsuite_build_dir.mkdir(parents=True, exist_ok=True)

        testsuite_source_dir = pathlib.Path(
            manager.params.root_dir, TESTSUITE_LOCAL_DIR,
        )

        testsuite_pythonpath = [
            str(manager.params.root_dir),
            str(
                pathlib.Path(manager.params.root_dir, TESTSUITE_SUBMODULE_DIR),
            ),
            str(pathlib.Path(manager.params.root_dir, USERVER_PYTEST_DIR)),
            str(pathlib.Path(testsuite_build_dir, 'service-plugins')),
            str(testsuite_source_dir),
        ]

        ctest_runtests_path = pathlib.Path(
            testsuite_build_dir, 'ctest-runtests',
        )
        runtests_path = pathlib.Path(testsuite_build_dir, 'runtests')
        taxi_env_path = pathlib.Path(testsuite_build_dir, 'taxi-env')

        service_names = list(
            pathlib.Path(manager.params.root_build_dir, SERVICES_DIR).glob(
                '*',
            ),
        )

        testsuite_pytest_dirs = []
        for service in service_names:
            testsuite_pytest_dirs.append(
                str(
                    pathlib.Path(
                        manager.params.root_dir, SERVICES_DIR, service.name,
                    ),
                ),
            )

        unit_paths = sorted(
            pathlib.Path(manager.params.root_build_dir, SERVICES_DIR).glob(
                '*/units/*',
            ),
        )
        for unit in unit_paths:
            testsuite_pythonpath.append(
                str(unit.joinpath('testsuite/service-plugins')),
            )

        manager.write(
            ctest_runtests_path,
            manager.renderer.get_template('ctest-runtests.jinja').render(
                {
                    'testsuite_pytest_dirs': ';'.join(
                        sorted(testsuite_pytest_dirs),
                    ),
                    'testsuite_build_dir': testsuite_build_dir,
                    'root_build_dir': manager.params.root_build_dir,
                    'root_source_dir': manager.params.root_dir,
                },
            ),
        )
        _chmod_executable(ctest_runtests_path)

        manager.write(
            runtests_path,
            manager.renderer.get_template('runtests.jinja').render(
                {
                    'root_build_dir': manager.params.root_build_dir,
                    'testsuite_pythonpath': ':'.join(
                        sorted(testsuite_pythonpath),
                    ),
                    'testsuite_source_dir': testsuite_source_dir,
                    'testsuite_python_binary': sys.executable,
                },
            ),
        )
        _chmod_executable(runtests_path)

        manager.write(
            taxi_env_path,
            manager.renderer.get_template('taxi-env.jinja').render(
                {
                    'testsuite_pythonpath': ':'.join(
                        sorted(testsuite_pythonpath),
                    ),
                    'testsuite_python_binary': sys.executable,
                    'root_build_dir': manager.params.root_build_dir,
                },
            ),
        )
        _chmod_executable(taxi_env_path)


def _chmod_executable(path: pathlib.Path) -> None:
    stt = os.stat(path)
    os.chmod(path, stt.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class UnitGenerator(plugin_manager.PluginBase):
    schema = voluptuous.Schema(
        {
            'enabled': bool,
            'mongo': {'extra-connections': [str]},
            'apikeys': {str: [str]},
        },
    )

    def __init__(self):
        self.enabled: bool = True
        self.apikeys: Dict[str, List[str]] = {}

    def activate(self, config: dict) -> None:
        self.schema(config)
        self.enabled = config.get('enabled', self.enabled)
        self.apikeys = config.get('apikeys', self.apikeys)

    def configure(self, manager: plugin_manager.ConfigureManager) -> None:
        manager.add_params(testsuite_apikeys=self.apikeys)

        if not self.enabled:
            return

        if manager.params.unit_name:
            arc_plugins_root = str(
                pathlib.Path('services')
                / manager.params.service_name
                / 'units'
                / manager.params.unit_name
                / 'testsuite'
                / 'service-plugins',
            )
            arc_service_plugins_dir = (
                manager.params.unit_name.replace('-', '_') + '_plugins'
            )
            config_key_prefix = f'testsuite:units/{manager.params.unit_name}/'
            config_path_prefix = (
                pathlib.Path('units') / manager.params.unit_name
            )
        else:
            arc_plugins_root = str(
                pathlib.Path('testsuite') / 'service-plugins',
            )
            arc_service_plugins_dir = (
                manager.params.service_name.replace('-', '_') + '_plugins'
            )
            config_key_prefix = 'testsuite:'
            config_path_prefix = pathlib.Path('.')

        manager.activate(
            'ya-make',
            {
                'testsuite-plugins': [
                    {
                        'plugins-root': arc_plugins_root,
                        'service-plugins-dir': arc_service_plugins_dir,
                    },
                ],
                'testsuite-configs': [
                    {
                        'key': (
                            config_key_prefix + 'config_vars.testsuite.yaml'
                        ),
                        'value': str(
                            config_path_prefix
                            / 'configs'
                            / 'config_vars.testsuite.yaml',
                        ),
                    },
                    {
                        'key': config_key_prefix + 'service.yaml',
                        'value': str(
                            config_path_prefix
                            / 'testsuite'
                            / 'configs'
                            / 'service.yaml',
                        ),
                    },
                    {
                        'key': (config_key_prefix + 'merged_taxi_config.json'),
                        'value': str(
                            config_path_prefix
                            / 'testsuite'
                            / 'taxi_config'
                            / 'config.json',
                        ),
                    },
                ],
            },
        )

        manager.activate(
            'cmake',
            {
                'find_program_required': [
                    'mongod mongodb-server',
                    'mongos mongodb-mongos',
                    'mongo mongodb-shell',
                    'redis-server redis-server',
                    'redis-cli redis-tools',
                    'pg_config postgresql-server-dev-12',
                    'pg_config postgresql-12',
                ],
            },
        )

        manager.activate(
            'debian',
            {
                'build_dependencies': [
                    'mongodb-server',
                    'mongodb-mongos',
                    'mongodb-shell',
                    'redis-server',
                    'redis-tools',
                    'postgresql-server-dev-12',
                    'postgresql-12',
                ],
            },
        )

    # pylint: disable=R0201
    def generate(self, manager: plugin_manager.GenerateManager) -> None:
        if manager.params.unit_name:
            test_dir = pathlib.Path(
                manager.params.service_path,
                'testsuite',
                'tests_{}'.format(
                    manager.params.service_name.replace('-', '_'),
                ),
            )
            unit_test_dir = pathlib.Path(
                test_dir / manager.params.unit_name.replace('-', '_'),
            )

            test_files = []
            for file in os.listdir(test_dir):
                if (
                        file.endswith('.py')
                        and file.startswith('test_')
                        and file != '__init__.py'
                ):
                    test_files.append(file)
            assert not test_files, (
                'If you use units you cannot have test files in the '
                'shared directory: `{}`. \n'
                'Please move the files from shared directory to '
                'the test directory of the unit: `{}`\n'
                'List of files: \n'
                '{}'.format(test_dir, unit_test_dir, '\n'.join(test_files))
            )

        pathlib.Path.mkdir(
            pathlib.Path(manager.params.root_build_dir, 'test-results'),
            exist_ok=True,
        )
