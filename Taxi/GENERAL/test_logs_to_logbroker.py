import dataclasses
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import pytest

import codegen.plugin_manager as plugin_manager


logging.basicConfig(level=logging.INFO)


class LogsWriter:
    name = 'logs_writer'
    scope = 'unit'
    depends = ['logs-to-logbroker']

    def __init__(self):
        self.config = None

    def activate(self, config: dict):
        self.config = config

    def configure(self, manager: plugin_manager.ConfigureManager):
        if not self.config:
            return
        for path in self.config['log_paths']:
            manager.activate('logs-to-logbroker', {'logs_path': path})


@dataclasses.dataclass
class ConfigTestParams:
    units: Dict
    service_extend: Dict
    test_data_path: Optional[str] = 'test_logs_to_logbroker/empty'
    plugins: Optional[List[Type]] = dataclasses.field(
        default_factory=lambda: [LogsWriter],
    )


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ConfigTestParams(units={'first-unit': {}}, service_extend={}),
            id='not enabled without logs',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                    },
                },
                service_extend={},
            ),
            id='not enabled with logs',
        ),
        pytest.param(
            ConfigTestParams(
                units={'first-unit': {}},
                service_extend={'logs-to-logbroker': {'enable': False}},
            ),
            id='disabled without logs',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                    },
                },
                service_extend={'logs-to-logbroker': {'enable': False}},
            ),
            id='disabled with logs',
        ),
        pytest.param(
            ConfigTestParams(
                units={'first-unit': {}},
                service_extend={'logs-to-logbroker': {'enable': True}},
            ),
            id='enabled without logs',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                    },
                },
                service_extend={'logs-to-logbroker': {'enable': True}},
                test_data_path='test_logs_to_logbroker/one_unit_simple',
            ),
            id='one unit simple',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                    },
                },
                service_extend={
                    'logs-to-logbroker': {
                        'enable': True,
                        'environments': {
                            'production': False,
                            'unstable': False,
                            'testing': True,
                        },
                    },
                },
                test_data_path='test_logs_to_logbroker/'
                'one_unit_service_envs_customization',
            ),
            id='one unit with service envs customization',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {
                                'production': {'enable': False},
                                'unstable': {'enable': False},
                            },
                        },
                    },
                },
                service_extend={'logs-to-logbroker': {'enable': True}},
                test_data_path='test_logs_to_logbroker/'
                'one_unit_envs_customization',
            ),
            id='one unit with unit envs customization',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {
                                'production': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-prod'
                                    ),
                                },
                                'unstable': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-unstable'
                                    ),
                                },
                            },
                        },
                    },
                },
                service_extend={'logs-to-logbroker': {'enable': True}},
                test_data_path='test_logs_to_logbroker/'
                'one_unit_topics_customization',
            ),
            id='one unit with topics customization',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {
                                'production': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-prod'
                                    ),
                                },
                                'unstable': {'enable': True},
                            },
                        },
                    },
                },
                service_extend={
                    'logs-to-logbroker': {
                        'enable': True,
                        'environments': {
                            'production': True,
                            'unstable': False,
                            'testing': True,
                        },
                    },
                },
                test_data_path='test_logs_to_logbroker/'
                'one_unit_all_customizations',
            ),
            id='one unit with all customizations',
        ),
    ],
)
def test_simple(
        tmpdir,
        plugin_manager_test,
        dir_comparator,
        base_service,
        params: ConfigTestParams,
):
    tmp_dir = tmpdir.mkdir('repo')

    base_service.update(params.service_extend)

    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units=params.units,
        plugins=params.plugins,
    )

    if params.test_data_path:
        dir_comparator(tmp_dir, params.test_data_path, 'base')
    else:
        dir_comparator(tmp_dir, 'base')


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {
                                'production': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-prod'
                                    ),
                                },
                                'unstable': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-unstable'
                                    ),
                                    'enable': True,
                                },
                            },
                        },
                        'debian': {
                            'binary_package_name': 'first-unit-package',
                        },
                    },
                    'second-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/second-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {'testing': {'enable': False}},
                        },
                        'debian': {
                            'binary_package_name': 'second-unit-package',
                        },
                    },
                },
                service_extend={
                    'logs-to-logbroker': {
                        'enable': True,
                        'environments': {
                            'production': True,
                            'unstable': False,
                            'testing': True,
                        },
                    },
                },
                test_data_path='test_logs_to_logbroker/multiple_units',
            ),
            id='multiple units',
        ),
    ],
)
def test_multiunit(
        tmpdir,
        plugin_manager_test,
        dir_comparator,
        base_service,
        params: ConfigTestParams,
):
    tmp_dir = tmpdir.mkdir('repo')

    base_service.update(params.service_extend)
    base_service['debian'].pop('binary_package_name')

    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units=params.units,
        plugins=params.plugins,
    )

    if params.test_data_path:
        dir_comparator(tmp_dir, params.test_data_path, 'base')
    else:
        dir_comparator(tmp_dir, 'base')


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': [
                                '/path/to/first-unit.logs',
                                '/path/to/second/file/of/first-unit.logs',
                            ],
                        },
                    },
                },
                service_extend={'logs-to-logbroker': {'enable': True}},
            ),
            id='one unit with two log files',
        ),
        pytest.param(
            ConfigTestParams(
                units={
                    'first-unit': {
                        'logs_writer': {
                            'log_paths': ['/path/to/first-unit.logs'],
                        },
                        'logs-to-logbroker': {
                            'environments': {
                                'production': {
                                    'topic': (
                                        'taxi/custom-topic-first-unit-prod'
                                    ),
                                },
                            },
                        },
                    },
                },
                service_extend={
                    'logs-to-logbroker': {
                        'enable': True,
                        'environments': {
                            'production': False,
                            'unstable': False,
                            'testing': True,
                        },
                    },
                },
            ),
            id='disabled unit with custom topic',
        ),
    ],
)
def test_error(
        tmpdir,
        plugin_manager_test,
        dir_comparator,
        base_service,
        params: ConfigTestParams,
):
    tmp_dir = tmpdir.mkdir('repo')

    base_service.update(params.service_extend)

    with pytest.raises(SystemExit):
        plugin_manager_test(
            tmp_dir,
            service=base_service,
            units=params.units,
            plugins=params.plugins,
        )
