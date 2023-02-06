import dataclasses
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import pytest

import codegen.plugin_manager as plugin_manager
import codegen.plugins.pilorama.plugin_generator as pilorama_plugin


logging.basicConfig(level=logging.INFO)


class ExamplePlugin:
    name = 'example'
    scope = 'unit'
    depends = ['pilorama']

    def __init__(self):
        self.config = None

    def activate(self, config: dict):
        self.config = config

    def configure(self, manager: plugin_manager.ConfigureManager):
        if not self.config:
            return
        manager.activate('pilorama', {'path': self.config['log_path']})


@dataclasses.dataclass
class ConfigTestParams:
    config: Dict
    test_data_path: Optional[str] = 'test_pilorama/basic'
    plugins: Optional[List[Type]] = dataclasses.field(
        default_factory=lambda: [ExamplePlugin],
    )


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ConfigTestParams(
                config={'pilorama': {'enable': True}},
                test_data_path='test_pilorama/enabled',
            ),
            id='no config',
        ),
        pytest.param(
            ConfigTestParams(
                config={
                    'pilorama': {
                        'config': {
                            'extra_logs': ['/my/nice/file.log'],
                            'file': {'discover_interval': '5s'},
                        },
                    },
                },
            ),
            id='basic config',
        ),
        pytest.param(
            ConfigTestParams(
                config={ExamplePlugin.name: {'log_path': '/my/nice/file.log'}},
                test_data_path=None,
            ),
            id='unit without config',
        ),
        pytest.param(
            ConfigTestParams(
                config={
                    ExamplePlugin.name: {'log_path': '/my/nice/file.log'},
                    'pilorama': {'enable': False},
                },
                test_data_path=None,
            ),
            id='unit with disabled codegen',
        ),
        pytest.param(
            ConfigTestParams(
                config={
                    ExamplePlugin.name: {'log_path': '/my/nice/file.log'},
                    'pilorama': {
                        'config': {'file': {'discover_interval': '5s'}},
                    },
                },
            ),
            id='unit with config',
        ),
        pytest.param(
            ConfigTestParams(
                config={
                    ExamplePlugin.name: {'log_path': '/my/nice/file.*.log'},
                    'pilorama': {
                        'config': {
                            'unstable': {'file': {'read_interval': '100ms'}},
                            'testing': {
                                'file': {'read_interval': '20ms'},
                                'extra_logs': ['/*'],
                            },
                            'production': {
                                'file': {
                                    'discover_interval': '5s',
                                    'read_interval': '20ms',
                                },
                                'filter': {
                                    'removals': ['foo', 'bar'],
                                    'put_message': True,
                                    'input_format': 'json',
                                    'time_formats': ['%Y-%m-%d', '%H:%M:%S'],
                                    'escaping': 'simple-escape-bypass',
                                },
                                'output': {
                                    'hosts': ['http://foo/1', 'http://foo/2'],
                                    'index': 'my-index-%Y.%m.%d',
                                    'error_index': 'my-errors-%Y.%m.%d',
                                },
                            },
                        },
                    },
                },
                test_data_path='test_pilorama/full',
            ),
            id='complex config',
        ),
    ],
)
def test_configs(
        tmpdir,
        plugin_manager_test,
        dir_comparator,
        base_service,
        params: ConfigTestParams,
):
    tmp_dir = tmpdir.mkdir('repo')

    config = {'my_unit_name': params.config}

    plugin_manager_test(
        tmp_dir, service=base_service, units=config, plugins=params.plugins,
    )

    if params.test_data_path:
        dir_comparator(tmp_dir, params.test_data_path, 'base')
    else:
        dir_comparator(tmp_dir, 'base')


class BadActivationPlugin(ExamplePlugin):
    def configure(self, manager: plugin_manager.ConfigureManager):
        if not self.config:
            return
        manager.activate('pilorama', {'path': self.config['log_path']})
        manager.activate(
            'pilorama', {'config': {'file': {'read_interval': '1337s'}}},
        )


@dataclasses.dataclass
class BadConfigTestParams(ConfigTestParams):
    error: str = 'exception on activation'


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            BadConfigTestParams(
                {'pilorama': {'config': {'file': {'read_interval': '5c'}}}},
                error='Must be a number with suffix d/h/m/s/ms',
            ),
            id='incorrect time format',
        ),
        pytest.param(
            BadConfigTestParams(
                {'pilorama': {'config': {'filter': {'escaping': 'new'}}}},
                error='value is not allowed',
            ),
            id='unknown enum member',
        ),
        pytest.param(
            BadConfigTestParams(
                {
                    'pilorama': {
                        'config': {'output': {'hosts': ['not-an-url']}},
                    },
                },
                error='expected a URL',
            ),
            id='invalid host url',
        ),
        pytest.param(
            BadConfigTestParams(
                {
                    'pilorama': {'config': {'file': {'read_interval': '5s'}}},
                    'example': {'log_path': '/foobar'},
                },
                plugins=[BadActivationPlugin],
                error='Plugin does not support multiple log configs',
            ),
            id='multiple activations',
        ),
        pytest.param(
            BadConfigTestParams(
                {
                    'pilorama': {'enable': True},
                    'example': {'log_path': './foobar'},
                },
            ),
            id='relative log path',
        ),
    ],
)
def test_bad_configs(
        tmpdir,
        plugin_manager_test,
        base_service,
        capsys,
        params: BadConfigTestParams,
):
    tmp_dir = tmpdir.mkdir('repo')

    config = {'unit': params.config}

    with pytest.raises(SystemExit):
        plugin_manager_test(
            tmp_dir,
            service=base_service,
            units=config,
            plugins=params.plugins,
        )
    capture = capsys.readouterr()
    assert params.error in capture.err


def test_time_regex():
    assert pilorama_plugin.RE_TIMESPAN.match('5s')
    assert pilorama_plugin.RE_TIMESPAN.match('55m')
    assert not pilorama_plugin.RE_TIMESPAN.match('5y')
    assert not pilorama_plugin.RE_TIMESPAN.match('5')


@pytest.mark.parametrize(
    'first,second,result',
    [
        pytest.param('a', 'b', 'b', id='merge basic types'),
        pytest.param(
            {'foo': 1, 'bar': {'b': 2}, 'baz': [1]},
            {'foo': 2, 'bar': {'a': 1}, 'baz': [2]},
            {'foo': 2, 'bar': {'a': 1, 'b': 2}, 'baz': [2]},
            id='merge dicts',
        ),
    ],
)
def test_merge_recursive(first, second, result):
    assert pilorama_plugin.merge_recursive(first, second) == result


@pytest.mark.parametrize(
    'first,second, error',
    [
        pytest.param(
            {'foo': {'a': 1}},
            {'foo': ['bar']},
            './foo: must be dict',
            id='dict with non-dict',
        ),
        pytest.param(
            {'foo': [1]},
            {'foo': 'bar'},
            './foo: must be list',
            id='list with non-list',
        ),
        pytest.param(
            {'foo': 1},
            {'foo': 'bar'},
            './foo: must be int',
            id='type mismatch',
        ),
    ],
)
def test_merge_recursive_throws(first, second, error):
    with pytest.raises(pilorama_plugin.ConfigMergeError, match=error):
        pilorama_plugin.merge_recursive(first, second)
