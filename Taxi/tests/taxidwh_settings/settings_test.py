# coding: utf-8
import os
import re
from unittest import TestCase

from itertools import chain
import mock
import pytest

from taxidwh_settings import (
    SettingsError,
    SettingsKeyError,
    SettingsKeyNotFoundError,
    Environment,
    StringToTupleSourceProxy,
    MergedMultiSettingsSource,
    YamlSettingsSource,
    YamlMultiFileSettingsSource,
    EmptySettingsSource,
    DictSettingsSource,
    build_settings,
    _wrap_exception,
    discover,
    PatchedSettingsSourceProxy, convert_keys)


SINGLE_YAML_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'common.yaml'
)
INVALID_YAML_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'invalid.yaml'
)
NON_EXISTS_YAML_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'non_exists.yaml'
)
MULTI_YAML_DIR_PATH = os.path.join(os.path.dirname(__file__), 'data', 'multi')


def test_environment_current():
    env_text = 'development'
    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.os.getenv', return_value=None), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True):
        environment = Environment()
        assert environment.current == env_text

    env_text = 'development\n'
    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.os.getenv', return_value=None), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True):
        environment = Environment()
        assert environment.current == 'development'

    env_text = 'dev'
    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.os.getenv', return_value=None), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True):
        with pytest.raises(SettingsError):
            Environment()

    with mock.patch('taxidwh_settings.os.getenv', return_value=None):
        with pytest.raises(SettingsError):
            Environment(None)

    with mock.patch('taxidwh_settings.os.getenv', return_value='dev'):
        with pytest.raises(SettingsError):
            Environment(None)

    with mock.patch('taxidwh_settings.os.getenv', return_value='development'):
        environment = Environment(None)
        assert environment.current == 'development'

    env_text = 'dev\n'
    with mock.patch('taxidwh_settings.os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True),\
            mock.patch('taxidwh_settings.os.getenv', return_value='development'):
        environment = Environment()
        assert environment.current == 'development'

    env_text = 'development\n'
    with mock.patch('taxidwh_settings.os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True),\
            mock.patch('taxidwh_settings.os.getenv', return_value=None):
        environment = Environment()
        assert environment.current == 'development'

    env_text = 'development\n'
    with mock.patch('taxidwh_settings.os.path.exists', return_value=True), \
            mock.patch('taxidwh_settings.open',
                       mock.mock_open(read_data=env_text),
                       create=True),\
            mock.patch('taxidwh_settings.os.getenv', return_value='dev'):
        with pytest.raises(SettingsError):
            Environment()

    with mock.patch('taxidwh_settings.os.getenv', return_value=None):
        environment = Environment(
            yandex_env_path=None, default_env_name='testing')
        assert environment.current == 'testing'


def test_mergeable_settings_source():

    t = DictSettingsSource(dict(
        a=1,
        b=dict(ba=10, bb=20)
    ))
    assert t(['a']) == 1
    assert t(['a'], default=0) == 1
    assert t(['b']) == dict(ba=10, bb=20)

    # change of result don't affect settings
    t(['b'])['bb'] = 30
    assert t(['b']) == dict(ba=10, bb=20)

    assert ['c'] not in t
    assert t(['c'], default='hello world') == 'hello world'
    with pytest.raises(SettingsKeyNotFoundError):
        t(['c'])

    with pytest.raises(SettingsKeyError):
        non_string_key = type("", (), {})()
        t([non_string_key])


def test_dict_source_info():
    source = DictSettingsSource({'a': 123}, name='src')
    assert '<DictSettingsSource, name=src>' == source.info(('a',))

    source = DictSettingsSource({'a': 123})
    assert re.match(
        r'<DictSettingsSource, .*settings_test.py:\d+>$',
        source.info(('a',)))


class TestMergedMultiSettingsSource(TestCase):
    def test_call(self):
        source = MergedMultiSettingsSource(DictSettingsSource({'a': 123}))
        assert 123 == source(('a', ))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}),
            DictSettingsSource({'a': 123}),
        )
        assert 123 == source(('a',))
        assert 100 == source(('b',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}),
            DictSettingsSource({'a': 123, 'c': 1}),
        )
        assert 123 == source(('a',))
        assert 100 == source(('b',))
        assert 1 == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': 30}),
            DictSettingsSource({'a': 20, 'b': 20}),
            DictSettingsSource({'a': 1, 'c': 1}),
        )
        assert 1 == source(('a',))
        assert 20 == source(('b',))
        assert 1 == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': 30}),
            DictSettingsSource({'a': 20, 'b': 20}),
            DictSettingsSource({'a': 1, 'c': {'ca': -1, 'cb': -1}}),
        )
        assert 1 == source(('a',))
        assert 20 == source(('b',))
        assert {'ca': -1, 'cb': -1} == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': {'cc': -3}}),
            DictSettingsSource({'a': 20, 'b': 20, 'c': None}),
            DictSettingsSource({'a': 1, 'c': {'ca': -1, 'cb': -1}}),
        )
        assert 1 == source(('a',))
        assert 20 == source(('b',))
        assert {'ca': -1, 'cb': -1} == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': {'ca': -3, 'cb': -3}}),
            DictSettingsSource({'a': 20, 'b': None}),
            DictSettingsSource({'a': 1, 'c': 1}),
        )
        assert 1 == source(('a',))
        assert source(('b',)) is None
        assert 1 == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}),
            DictSettingsSource({'c': None}),
            DictSettingsSource({'c': {'ca': -1}}),
        )
        assert {'ca': -1} == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}),
            DictSettingsSource({'c': {'cc': {'cca': 2, 'ccc': 2}}}),
            DictSettingsSource({'c': {'ca': -1, 'cc': {'cca': 1, 'ccb': 1}}}),
        )
        c_value = {'ca': -1, 'cb': -3, 'cc': {'cca': 1, 'ccb': 1, 'ccc': 2}}
        assert c_value == source(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': [10, 20]}),
            DictSettingsSource({'a': [1, 2, 3]}),
        )
        assert [1, 2, 3] == source(('a',))

        with pytest.raises(SettingsKeyError):
            source('a')

        with pytest.raises(SettingsKeyError):
            source(None)

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': {}}),
            DictSettingsSource({'a': {}}),
        )
        assert {} == source(('a',))

        assert 0 == source(('b',), default=0)

        with pytest.raises(SettingsKeyNotFoundError):
            source(('b',))

    def test_contains(self):
        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}),
            DictSettingsSource({'a': 123}),
        )
        assert ('a',) in source
        assert ('b',) in source
        assert ('c',) not in source

        with pytest.raises(SettingsKeyError):
            ('a', 'c') in source

        with pytest.raises(SettingsKeyError):
            ('a', 'c') not in source

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': {'ca': -3, 'cb': -3}}),
            DictSettingsSource({'a': 20, 'b': None}),
            DictSettingsSource({'a': 1, 'c': 1}),
        )
        assert ('a',) in source
        assert ('b',) in source
        assert ('c',) in source

        with pytest.raises(SettingsKeyError):
            'a' in source

        with pytest.raises(SettingsKeyError):
            None in source

        with pytest.raises(SettingsKeyError):
            ('a', 'cb') in source

        with pytest.raises(SettingsKeyError):
            ('a', 'cb') not in source

    def test_info(self):
        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 123}, name='src')
        )
        assert '<DictSettingsSource, name=src>' == source.info(('a',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}, name='src1'),
            DictSettingsSource({'a': 123}, name='src2'),
        )
        assert '<DictSettingsSource, name=src2>' == source.info(('a',))
        assert '<DictSettingsSource, name=src1>' == source.info(('b',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}, name='src1'),
            DictSettingsSource({'a': 123, 'c': 1}, name='src2'),
        )
        assert '<DictSettingsSource, name=src2>' == source.info(('a',))
        assert '<DictSettingsSource, name=src1>' == source.info(('b',))
        assert '<DictSettingsSource, name=src2>' == source.info(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': 30}, name='src1'),
            DictSettingsSource({'a': 20, 'b': 20}, name='src2'),
            DictSettingsSource({'a': 1, 'c': 1}, name='src3'),
        )
        assert '<DictSettingsSource, name=src3>' == source.info(('a',))
        assert '<DictSettingsSource, name=src2>' == source.info(('b',))
        assert '<DictSettingsSource, name=src3>' == source.info(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': 30}, name='src1'),
            DictSettingsSource({'a': 20, 'b': 20}, name='src2'),
            DictSettingsSource(
                {'a': 1, 'c': {'ca': -1, 'cb': -1}}, name='src3'),
        )
        assert '<DictSettingsSource, name=src3>' == source.info(('a',))
        assert '<DictSettingsSource, name=src2>' == source.info(('b',))
        assert '<DictSettingsSource, name=src3>' == source.info(('c',))
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'ca'))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': {'cc': -3}}, name='src1'),
            DictSettingsSource({'a': 20, 'b': 20, 'c': None}, name='src2'),
            DictSettingsSource(
                {'a': 1, 'c': {'ca': -1, 'cb': -1}}, name='src3'),
        )
        assert '<DictSettingsSource, name=src3>' == source.info(('a',))
        assert '<DictSettingsSource, name=src2>' == source.info(('b',))
        assert '<DictSettingsSource, name=src3>' == source.info(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource(
                {'b': 30, 'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource({'a': 20, 'b': None}, name='src2'),
            DictSettingsSource({'a': 1, 'c': 1}, name='src3'),
        )
        assert '<DictSettingsSource, name=src3>' == source.info(('a',))
        assert '<DictSettingsSource, name=src2>' == source.info(('b',))
        assert '<DictSettingsSource, name=src3>' == source.info(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource({'c': None}, name='src2'),
            DictSettingsSource({'c': {'ca': -1}}, name='src3'),
        )
        assert '<DictSettingsSource, name=src3>' == source.info(('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource(
                {'c': {'cc': {'cca': 2, 'ccc': 2}}}, name='src2'),
            DictSettingsSource(
                {'c': {'ca': -1, 'cc': {'cca': 1, 'ccb': 1}}}, name='src3'),
        )
        assert source.info(('c',)) is None
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'ca'))
        assert '<DictSettingsSource, name=src1>' == source.info(('c', 'cb'))
        assert source.info(('c', 'cc')) is None
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'cc', 'cca'))
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'cc', 'ccb'))
        assert '<DictSettingsSource, name=src2>' == source.info(('c', 'cc', 'ccc'))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource(
                {'c': {'cc': {'cca': 2, 'ccc': 2}}}, name='src2'),
            MergedMultiSettingsSource(
                DictSettingsSource(
                    {'c': {'ca': -1, 'cc': {'cca': 1, 'ccb': 1}}}, name='src3'),
                DictSettingsSource(
                    {'a': 1, 'c': {'cc': {'cca': 1, 'ccd': 1}}}, name='src4'),
            )
        )
        assert source.info(('c',)) is None
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'ca'))
        assert '<DictSettingsSource, name=src1>' == source.info(('c', 'cb'))
        assert source.info(('c', 'cc')) is None
        assert '<DictSettingsSource, name=src4>' == source.info(('c', 'cc', 'cca'))
        assert '<DictSettingsSource, name=src3>' == source.info(('c', 'cc', 'ccb'))
        assert '<DictSettingsSource, name=src2>' == source.info(('c', 'cc', 'ccc'))
        assert '<DictSettingsSource, name=src4>' == source.info(('c', 'cc', 'ccd'))
        assert '<DictSettingsSource, name=src4>' == source.info(('a',))

        with pytest.raises(SettingsKeyError):
            source.info(None)

        with pytest.raises(SettingsKeyError):
            source.info(('d', ))

        with pytest.raises(SettingsKeyError):
            source.info(('c', 'dddd'))

    def test_discover(self):
        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 123}, name='src')
        )
        assert 'a: <DictSettingsSource, name=src>' == discover(source, ('a',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': {'aa': 123}}, name='src')
        )
        assert 'a.aa: <DictSettingsSource, name=src>' == discover(source, ('a',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'a': 0, 'b': 100}, name='src1'),
            DictSettingsSource({'a': None}, name='src2'),
        )

        assert 'a: <DictSettingsSource, name=src2>' == discover(source, ('a',))
        assert 'b: <DictSettingsSource, name=src1>' == discover(source, ('b',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'b': 30, 'c': 30}, name='src1'),
            DictSettingsSource({'a': 20, 'b': 20}, name='src2'),
            DictSettingsSource({'a': 1, 'c': 1}, name='src3'),
        )

        assert 'a: <DictSettingsSource, name=src3>' == discover(source, ('a',))
        assert 'b: <DictSettingsSource, name=src2>' == discover(source, ('b',))
        assert 'c: <DictSettingsSource, name=src3>' == discover(source, ('c',))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource(
                {'c': {'cc': {'cca': 2, 'ccc': 2}}}, name='src2'),
            DictSettingsSource(
                {'c': {'ca': -1, 'cc': {'cca': 1, 'ccb': 1}}}, name='src3'),
        )

        c_expected = '\n'.join([
            'c.ca: <DictSettingsSource, name=src3>',
            'c.cb: <DictSettingsSource, name=src1>',
            'c.cc.cca: <DictSettingsSource, name=src3>',
            'c.cc.ccb: <DictSettingsSource, name=src3>',
            'c.cc.ccc: <DictSettingsSource, name=src2>',
        ])

        assert c_expected == discover(source, 'c')
        assert 'c.ca: <DictSettingsSource, name=src3>' == discover(source, ('c', 'ca'))

        cc_expected = '\n'.join([
            'c.cc.cca: <DictSettingsSource, name=src3>',
            'c.cc.ccb: <DictSettingsSource, name=src3>',
            'c.cc.ccc: <DictSettingsSource, name=src2>',
        ])
        assert cc_expected == discover(source, ('c', 'cc'))

        source = MergedMultiSettingsSource(
            DictSettingsSource({'c': {'ca': -3, 'cb': -3}}, name='src1'),
            DictSettingsSource(
                {'c': {'cc': {'cca': 2, 'ccc': 2}}}, name='src2'),
            MergedMultiSettingsSource(
                DictSettingsSource(
                    {'c': {'ca': -1, 'cc': {'cca': 1, 'ccb': 1}}}, name='src3'),
                DictSettingsSource(
                    {'a': 1, 'c': {'cc': {'cca': 1, 'ccd': 1}}}, name='src4'),
            )
        )

        c_expected = '\n'.join([
            'c.ca: <DictSettingsSource, name=src3>',
            'c.cb: <DictSettingsSource, name=src1>',
            'c.cc.cca: <DictSettingsSource, name=src4>',
            'c.cc.ccb: <DictSettingsSource, name=src3>',
            'c.cc.ccc: <DictSettingsSource, name=src2>',
            'c.cc.ccd: <DictSettingsSource, name=src4>',
        ])
        assert c_expected == discover(source, 'c')
        assert 'a: <DictSettingsSource, name=src4>' == discover(source, 'a')


class TestYamlSettingsSource(TestCase):
    def test_call(self):
        with pytest.raises(SettingsError):
            YamlSettingsSource(None)

        with pytest.raises(SettingsError):
            YamlSettingsSource(INVALID_YAML_PATH)

        with pytest.raises(SettingsError):
            YamlSettingsSource(NON_EXISTS_YAML_PATH)

        with pytest.raises(SettingsError):
            YamlSettingsSource(MULTI_YAML_DIR_PATH)

        source = YamlSettingsSource(SINGLE_YAML_PATH)

        assert {'aa': 100, 'bb': 200, 'dd': None} == source(('a',))
        assert 200 == source(('a', 'bb'))
        assert 20 == source(('b',))
        assert source(('a', 'dd')) is None
        assert 9999 == source(('a', 'dd', 'zzz'), default=9999)

        with pytest.raises(SettingsKeyError):
            source('a')

        with pytest.raises(SettingsKeyError):
            source(None)

        with pytest.raises(SettingsKeyError):
            source(('c',))

        with pytest.raises(SettingsKeyNotFoundError):
            source(('c',))

        with pytest.raises(SettingsKeyNotFoundError):
            source(('a', 'cc'))

        with pytest.raises(SettingsKeyError):
            source(('b', 'cc'))

        with pytest.raises(SettingsKeyError):
            source(('b', 'cc'), default=0)

        with pytest.raises(SettingsKeyNotFoundError):
            source(('a', 'dd', 'zzz'))

    def test_repr(self):
        source = YamlSettingsSource(SINGLE_YAML_PATH)
        expected_repr = 'YamlSettingsSource("{}")'.format(SINGLE_YAML_PATH)
        assert expected_repr == repr(source)

    def test_contains(self):
        source = YamlSettingsSource(SINGLE_YAML_PATH)

        assert ('a',) in source
        assert ('a', 'aa') in source
        assert ('c',) not in source
        assert ('a', 'cc') not in source
        assert ('a', 'dd') in source
        assert ('a', 'dd', 'zzz') not in source

        with pytest.raises(SettingsKeyError):
            assert 'a' in source

        with pytest.raises(SettingsKeyError):
            assert None in source

        with pytest.raises(SettingsKeyError):
            assert ('b', 'cc') not in source

        with pytest.raises(SettingsKeyError):
            assert ('b', 'cc') in source

    def test_info(self):
        relative_path = os.path.join(
            os.path.dirname(__file__), 'data', os.pardir, 'data', 'common.yaml'
        )
        source = YamlSettingsSource(relative_path)
        expected = '<YamlSettingsSource, {}>'.format(
            os.path.abspath(relative_path)
        )
        assert expected == source.info(('a', ))
        assert expected == source.info(('a', 'aa'))

        with pytest.raises(SettingsKeyError):
            source.info(None)

        with pytest.raises(SettingsKeyError):
            source.info(('d', ))

        with pytest.raises(SettingsKeyError):
            source.info(('b', 'cc'))

    def test_discover(self):
        source = YamlSettingsSource(SINGLE_YAML_PATH)
        source_info = '<YamlSettingsSource, {}>'.format(SINGLE_YAML_PATH)
        expected = '\n'.join([
            'a.aa: ' + source_info,
            'a.bb: ' + source_info,
            'a.dd: ' + source_info,
        ])

        assert expected == discover(source, ('a',))
        assert 'a.bb: ' + source_info == discover(source, ('a', 'bb'))
        assert 'b: ' + source_info == discover(source, ('b',))

    def test_root_item_call(self):
        source = YamlSettingsSource(SINGLE_YAML_PATH, root_item='root')
        assert {
            'a': {'aa': 100, 'bb': 200, 'dd': None},
            'b': 20
        } == source(('root',))
        assert {'aa': 100, 'bb': 200, 'dd': None} == source(('root', 'a'))
        assert 200 == source(('root', 'a', 'bb'))

        with pytest.raises(SettingsKeyNotFoundError):
            source(('a',))

    def test_root_item_contains(self):
        source = YamlSettingsSource(SINGLE_YAML_PATH, root_item='root')

        assert ('root',) in source
        assert ('root', 'a') in source
        assert ('a',) not in source
        assert ('root', 'a', 'aa') in source
        assert ('root', 'c') not in source


class TestMultiYamlSource(TestCase):
    def test_call(self):
        with pytest.raises(SettingsError):
            YamlMultiFileSettingsSource(None)

        with pytest.raises(SettingsError):
            YamlMultiFileSettingsSource(NON_EXISTS_YAML_PATH)

        with pytest.raises(SettingsError):
            YamlMultiFileSettingsSource(SINGLE_YAML_PATH)

        source = YamlMultiFileSettingsSource(
            os.path.join(os.path.dirname(__file__), 'data')
        )
        with pytest.raises(SettingsError):
            source(('invalid',))

        source = YamlMultiFileSettingsSource(MULTI_YAML_DIR_PATH)

        assert {'aa': 100, 'bb': 200, 'dd': None} == source(('a',))
        assert 200 == source(('a', 'bb'))
        assert {'bb': 20} == source(('b',))
        assert source(('a', 'dd')) is None
        assert 9999 == source(('a', 'dd', 'zzz'), default=9999)
        assert {} == source(('d',))

        with pytest.raises(SettingsKeyError):
            source('a')

        with pytest.raises(SettingsKeyError):
            source(None)

        with pytest.raises(SettingsKeyError):
            source(('c',))

        with pytest.raises(SettingsKeyNotFoundError):
            source(('c',))

        with pytest.raises(SettingsKeyNotFoundError):
            source(('a', 'cc'))

        with pytest.raises(SettingsKeyError):
            source(('a', 'bb', 'cc'))

        with pytest.raises(SettingsKeyError):
            source(('a', 'bb', 'cc'), default=0)

        with pytest.raises(SettingsKeyNotFoundError):
            source(('a', 'dd', 'zzz'))

    def test_repr(self):

        config_path = os.path.join(
                os.path.dirname(__file__), 'data', 'multi'
        )
        source = YamlMultiFileSettingsSource(config_path)
        expected_repr = 'YamlMultiFileSettingsSource("{}")'.format(config_path)
        assert expected_repr == repr(source)

    def test_contains(self):
        source = YamlMultiFileSettingsSource(
            os.path.join(
                os.path.dirname(__file__), 'data', 'multi'
            ))

        assert ('a',) in source
        assert ('a', 'aa') in source
        assert ('c',) not in source
        assert ('a', 'cc') not in source
        assert ('a', 'dd') in source
        assert ('a', 'dd', 'zzz') not in source

        with pytest.raises(SettingsKeyError):
            'a' in source

        with pytest.raises(SettingsKeyError):
            None in source

        with pytest.raises(SettingsKeyError):
            ('a', 'bb', 'cc') not in source

    def test_info(self):
        dir_path = os.path.join(
            os.path.dirname(__file__), 'data', os.pardir, 'data', 'multi'
        )
        dir_abs_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'data', 'multi')
        )
        source = YamlMultiFileSettingsSource(dir_path)
        expected = '<YamlMultiFileSettingsSource, {}>'.format(
            os.path.join(dir_abs_path, 'a.yaml')
        )
        assert expected == source.info(('a',))
        assert expected == source.info(('a', 'aa'))

        with pytest.raises(SettingsKeyError):
            source.info(None)

        with pytest.raises(SettingsKeyError):
            source.info(('c',))

        with pytest.raises(SettingsKeyError):
            source.info(('a', 'dd', 'zzz'))

    def test_discover(self):
        source = YamlMultiFileSettingsSource(MULTI_YAML_DIR_PATH)
        a_source_info = '<YamlMultiFileSettingsSource, {}>'.format(
            os.path.join(MULTI_YAML_DIR_PATH, 'a.yaml')
        )
        b_source_info = '<YamlMultiFileSettingsSource, {}>'.format(
            os.path.join(MULTI_YAML_DIR_PATH, 'b.yaml')
        )
        expected = '\n'.join([
            'a.aa: ' + a_source_info,
            'a.bb: ' + a_source_info,
            'a.dd: ' + a_source_info,
        ])
        assert expected == discover(source, 'a')
        assert 'b.bb: ' + b_source_info == discover(source, 'b')


def test_convert_keys():
    assert convert_keys(None) is None
    assert convert_keys('') == ('',)
    assert convert_keys('yt') == ('yt',)
    assert convert_keys('yt.') == ('yt', '')
    assert convert_keys('.yt') == ('', 'yt')
    assert convert_keys('yt.hanh') == ('yt', 'hanh')
    assert convert_keys('yt..hanh') == ('yt', '', 'hanh')
    assert convert_keys(('yt', 'hanh')) == ('yt', 'hanh')


class TestStringToTupleSourceProxy(TestCase):

    def test_call(self):
        proxy_source = StringToTupleSourceProxy(
            DictSettingsSource({
                'a': {'aa': 100, 'bb': 200, 'dd': None},
                'b': 20
            }))

        assert {'aa': 100, 'bb': 200, 'dd': None} == proxy_source(('a',))
        assert {'aa': 100, 'bb': 200, 'dd': None} == proxy_source('a')
        assert 200 == proxy_source(('a', 'bb'))
        assert 200 == proxy_source('a.bb')
        assert 20 == proxy_source(('b',))
        assert 20 == proxy_source('b')
        assert proxy_source(('a', 'dd')) is None
        assert proxy_source('a.dd') is None
        assert 9999 == proxy_source(('a', 'dd', 'zzz'), default=9999)
        assert 9999 == proxy_source('a.dd.zzz', default=9999)

        with pytest.raises(SettingsKeyNotFoundError):
            proxy_source(('c',))

        with pytest.raises(SettingsKeyNotFoundError):
            proxy_source('c')

        with pytest.raises(SettingsKeyNotFoundError):
            proxy_source(('a', 'cc'))

        with pytest.raises(SettingsKeyNotFoundError):
            proxy_source('a.cc')

        with pytest.raises(SettingsKeyNotFoundError):
            proxy_source('a.dd.zzz')

        with pytest.raises(SettingsKeyError):
            proxy_source('a.aa.aaa')

    def test_contains(self):
        proxy_source = StringToTupleSourceProxy(
            DictSettingsSource({
                'a': {'aa': 100, 'bb': 200, 'dd': None},
                'b': 20
            }))

        assert ('a',) in proxy_source
        assert 'a' in proxy_source
        assert ('a', 'aa') in proxy_source
        assert 'a.aa' in proxy_source
        assert ('c',) not in proxy_source
        assert 'c' not in proxy_source
        assert ('a', 'cc') not in proxy_source
        assert 'a.cc' not in proxy_source
        assert ('a', 'dd') in proxy_source
        assert 'a.dd' in proxy_source
        assert ('a', 'dd', 'zzz') not in proxy_source
        assert 'a.dd.zzz' not in proxy_source

        with pytest.raises(SettingsKeyError):
            'a.aa.aaa' not in proxy_source

        with pytest.raises(SettingsKeyError):
            'a.aa.aaa' in proxy_source

    def test_info(self):
        proxy_source = StringToTupleSourceProxy(
            DictSettingsSource({
                'a': {'aa': 100, 'bb': 200, 'dd': None},
                'b': 20
            }))

        assert 'DictSettingsSource' in proxy_source.info(('a',))
        assert 'DictSettingsSource' in proxy_source.info(('a', 'aa'))

        with pytest.raises(SettingsKeyError):
            proxy_source.info(None)

        with pytest.raises(SettingsKeyError):
            proxy_source.info(('c',))


class TestEmptySettingSource(TestCase):
    def test_call(self):
        source = EmptySettingsSource()
        assert source(('a',)) is None
        assert source(('a', 'aa')) is None
        assert source(('a', 'aa'), default=100) is None

    def test_contains(self):
        source = EmptySettingsSource()
        assert ('a',) not in source
        assert ('a', 'aa') not in source


class TestBuildSettings(TestCase):
    def test_empty_no_raises(self):
        build_settings()
        build_settings(None)
        build_settings(None, None)

    def test_non_exist_path_no_raises(self):
        build_settings(NON_EXISTS_YAML_PATH)

    def _helper_none_source(self, sources, assert_callback):
        assert_callback(build_settings(*sources))
        assert_callback(build_settings(*chain(sources, (None,))))
        assert_callback(build_settings(*chain((None,), sources)))

    def _helper_none_source_single(self, source, assert_callback):
        self._helper_none_source((source,), assert_callback)

    def test_single_source(self):
        single_source = DictSettingsSource({
            'a': {'aa': 100, 'bb': 200, 'dd': None},
            'b': 20
        })

        def assert_1(result_source):
            assert 20 == result_source('b')
            assert 200 == result_source('a.bb')

        self._helper_none_source_single(single_source, assert_1)
        self._helper_none_source_single(SINGLE_YAML_PATH, assert_1)

        def assert_multi_yaml(result_source):
            assert 20 == result_source('b.bb')
            assert 200 == result_source('a.bb')

        self._helper_none_source_single(MULTI_YAML_DIR_PATH, assert_multi_yaml)

    def test_heterogeneous_source(self):
        dict_source = DictSettingsSource({
            'a': {'dd': 5000},
        })

        self._helper_none_source(
            (dict_source, SINGLE_YAML_PATH),
            lambda s: self.assertEqual(s('a.dd'), None)
        )
        self._helper_none_source(
             (SINGLE_YAML_PATH, dict_source),
             lambda s: self.assertEqual(s('a.dd'), 5000)
        )


def test_wrap_exception():
    def raise_for_test():
        raise RuntimeError("internal message")

    with pytest.raises(SettingsError) as excinfo:
        with _wrap_exception("wrapped message", (RuntimeError,)):
            raise_for_test()
    expected_msg = "wrapped message Caused by: RuntimeError: internal message"
    assert expected_msg in str(excinfo.value)


class TestPatchedSettingsSourceProxy(object):

    one_patch_values = [
        (
            # changes:
            [('a.aa', 300), ('a.v.vv', 500)],
            # kwarg_changes:
            {}
        ),
        (
            # changes:
            [('a.aa', 300), ('a.v.vv', 500), {}],
            # kwarg_changes:
            {}
        ),
        (
            # changes:
            [{"a": {"aa": 300,
                    "v": {"vv": 500}}}],
            # kwarg_changes:
            {}
        ),
        (
            # changes:
            [('a.aa', 0),
             {"a": {"aa": 300,
                    "v": {"vv": 500}}}],
            # kwarg_changes:
            {}
        ),
        (
            # changes:
            [],
            # kwarg_changes:
            {"a": {"aa": 300,
                   "v": {"vv": 500}}}
        ),
        (
            # changes:
            [('a.aa', 0), ('a.v.vv', 0)],
            # kwarg_changes:
            {"a": {"aa": 300,
                   "v": {"vv": 500}}}
        )
    ]

    @pytest.fixture
    def settings(self):
        return PatchedSettingsSourceProxy(DictSettingsSource({
            'a': {'aa': 100, 'bb': 200, 'dd': None},
            'b': 20
        }))

    @staticmethod
    def assert_no_patch(settings_):
        assert 100 == settings_('a.aa')
        assert 200 == settings_('a.bb')
        assert 'a.v' not in settings_

    @pytest.mark.parametrize('changes, kwarg_changes', one_patch_values)
    def test_context(self, changes, kwarg_changes, settings):
        with settings.patch(*changes, **kwarg_changes):
            assert 300 == settings('a.aa')
            assert 200 == settings('a.bb')
            assert dict(vv=500) == settings('a.v')

        self.assert_no_patch(settings)

    @pytest.mark.parametrize('changes, kwarg_changes', one_patch_values)
    def test_one_decorator(self, changes, kwarg_changes, settings):
        @settings.patch(*changes, **kwarg_changes)
        def foo():
            assert 300 == settings('a.aa')
            assert 200 == settings('a.bb')
            assert dict(vv=500) == settings('a.v')

        foo()
        self.assert_no_patch(settings)

    @pytest.mark.parametrize('changes, kwarg_changes', [
        (
            # changes:
            [()],
            # kwarg_changes:
            {}
        ),
        (
            # changes:
            [('a.aa', 300), (), ('a.v.vv', 500)],
            # kwarg_changes:
            {}
        ),
    ])
    def test_raise(self, changes, kwarg_changes, settings):
        with pytest.raises(SettingsError):
            with settings.patch(*changes, **kwarg_changes):
                pass

    def test_multi_decorator(self, settings):
        @settings.patch(
            ('a.aa', 300),
            ('a.v.vv', 500),
        )
        @settings.patch(
            ('a.aa', 400),
            ('a.v.vvv', 600),
        )
        @settings.patch(
            {'a': {'aa': 400}},
            {'a': {'v': {'vvv': 400}}},
         )
        def foo():
            assert 400 == settings('a.aa')
            assert 200 == settings('a.bb')
            assert dict(vv=500, vvv=400) == settings('a.v')

        foo()
        self.assert_no_patch(settings)

    def test_multi_context(self, settings):

        def assert_patch_1():
            assert 300 == settings('a.aa')
            assert 200 == settings('a.bb')
            assert dict(vv=300) == settings('a.v')

        with settings.patch(a={'aa': 300, 'v': {'vv': 300}}):
            assert_patch_1()
            with settings.patch(a={'aa': 400, 'v': {'vvv': 400}}):
                assert 400 == settings('a.aa')
                assert 200 == settings('a.bb')
                assert dict(vv=300, vvv=400) == settings('a.v')
            assert_patch_1()

        self.assert_no_patch(settings)
