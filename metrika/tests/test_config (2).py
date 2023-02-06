import os

import pytest

from yatest.common import source_path


import requests_mock
import metrika.pylib.bishop as bp

from metrika.pylib.structures.dotdict import DotDict

from metrika.pylib.config import get_yaml_config_from_file, get_yaml_config_from_bishop
from metrika.pylib.config.parsers import yaml_parser
from metrika.pylib.config.providers import file_provider
from metrika.pylib.config.providers import builtin_provider
import metrika.pylib.config.errors as errors


class ConfigTestError(Exception):
    pass


def test_parse_config(vault_response, vault_client):
    os.environ["VAR1"] = '12'
    os.environ["VAR2"] = 'qwe'
    os.environ["VAR3"] = '[1, 2, {"a": 3}]'

    config = get_yaml_config_from_file(source_path('metrika/pylib/config/tests/data/yaml/config.yaml'), vault_client=vault_client)
    assert isinstance(config, DotDict)

    assert sorted(config.keys()) == ['key1', 'key2', 'key3', 'key4', 'key5', 'key6']
    assert config.key1[0].key12 == 'value12'
    assert config.key2[1] == 'item22'
    assert config.key3 == 'secret_value'
    assert config.key4[0] == 'asd'
    assert config.key4[1] == 12
    assert config.key4[2] == {'key5': 'qwe', 'key6': None, 'key7': [1, 2, {'a': 3}]}
    assert config.key5 == {u'passwd': u'qwerty', u'client': u'zxc'}
    assert config.key6 == 'qwerty'


def test_config_error_on_missing():
    fname = source_path('metrika/pylib/config/tests/data/yaml/this_is_missing_config_filename')

    with pytest.raises(errors.ConfigDoesNotExist):
        get_yaml_config_from_file(fname)


def test_config_error_on_missing_include():
    fname = source_path('metrika/pylib/config/tests/data/yaml/config_include_missing.yaml')

    with pytest.raises(errors.ConfigDoesNotExist):
        get_yaml_config_from_file(fname)


def test_config_error_on_invalid_yaml():
    fname = source_path('metrika/pylib/config/tests/data/yaml/invalid_yaml.yaml')

    with pytest.raises(errors.ConfigYAMLError):
        get_yaml_config_from_file(fname)


def test_config_error_on_access_denied(monkeypatch):
    fname = source_path('metrika/pylib/config/tests/data/yaml/config.yaml')

    def mock_access(*args, **kwargs):
        return False

    monkeypatch.setattr(os, 'access', mock_access)

    with pytest.raises(errors.ConfigAccessError):
        get_yaml_config_from_file(fname)


def test_config_error_on_io_error(monkeypatch):
    def mock_read_file(*args, **kwargs):
        raise IOError("Hello")

    def mock_os(*args, **kwargs):
        return True

    monkeypatch.setattr(os.path, 'isfile', mock_os)
    monkeypatch.setattr(os, 'access', mock_os)
    monkeypatch.setattr(file_provider.FileProvider, 'read_file', mock_read_file)

    with pytest.raises(errors.ConfigIOError):
        get_yaml_config_from_file('lol')


def test_get_bishop_config_error_on_bishop_exception(bishop, monkeypatch):
    def mock_get_config(*args, **kwargs):
        raise ConfigTestError("Test Error")

    monkeypatch.setattr(bishop, 'get_config', mock_get_config)

    with pytest.raises(errors.ConfigError):
        get_yaml_config_from_bishop(
            'superd',
            'superd.environment',
            client=bishop,
        )


def test_get_bishop_config_error_on_missing_version_attribute(bishop):
    url = bp.API_URL + '/v2/config/superd/superd.environment'

    with requests_mock.Mocker() as m:
        m.get(url, json={'text': 'hello:world\n'})

        with pytest.raises(errors.ConfigError):
            get_yaml_config_from_bishop(
                'superd',
                'superd.environment',
                client=bishop,
            )


def test_get_bishop_config_error_on_missing_text_attribute(bishop):
    url = bp.API_URL + '/v2/config/superd/superd.environment'

    with requests_mock.Mocker() as m:
        m.get(url, json={'version': 1})

        with pytest.raises(errors.ConfigError):
            get_yaml_config_from_bishop(
                'superd',
                'superd.environment',
                client=bishop,
            )


def test_get_bishop_config_yaml_error_on_invalid_yaml_syntax(bishop):
    url = bp.API_URL + '/v2/config/superd/superd.environment'

    with requests_mock.Mocker() as m:
        headers = {
            'bishop-config-version': '1',
            'bishop-config-format': 'yaml',
        }
        m.get(url, text='hello:\n    asdf\nasdf', headers=headers)

        with pytest.raises(errors.ConfigYAMLError):
            get_yaml_config_from_bishop(
                'superd',
                'superd.environment',
                client=bishop,
            )


def test_get_bishop_config_return(bishop):
    url = bp.API_URL + '/v2/config/superd/superd.environment'

    with requests_mock.Mocker() as m:
        headers = {
            'bishop-config-version': '666',
            'bishop-config-format': 'yaml',
        }
        m.get(url, text='hello: world\n', headers=headers)
        result = get_yaml_config_from_bishop(
            'superd',
            'superd.environment',
            client=bishop,
        )
        assert isinstance(result, DotDict)
        assert result.hello == 'world'


def test_parse_text_config(vault_response, vault_client):
    os.environ["VAR1"] = '12'
    os.environ["VAR2"] = 'qwe'
    os.environ["VAR3"] = '[1, 2, {"a": 3}]'
    f_name = source_path('metrika/pylib/config/tests/data/yaml/config.yaml')
    cwd = os.getcwd()
    os.chdir(os.path.dirname(f_name))

    with open(f_name) as f_h:
        config = yaml_parser.YamlParser(vault_client=vault_client).parse(f_h.read())
    assert isinstance(config, DotDict)

    assert sorted(config.keys()) == ['key1', 'key2', 'key3', 'key4', 'key5', 'key6']
    assert config.key1[0].key12 == 'value12'
    assert config.key2[1] == 'item22'
    assert config.key3 == 'secret_value'
    assert config.key4[0] == 'asd'
    assert config.key4[1] == 12
    assert config.key4[2] == {'key5': 'qwe', 'key6': None, 'key7': [1, 2, {'a': 3}]}
    assert config.key5 == {u'passwd': u'qwerty', u'client': u'zxc'}
    assert config.key6 == 'qwerty'

    os.chdir(cwd)


def test_text_config_error_on_invalid_yaml():
    fname = source_path('metrika/pylib/config/tests/data/yaml/invalid_yaml.yaml')

    with open(fname) as f_h:
        with pytest.raises(errors.ConfigYAMLError):
            yaml_parser.YamlParser().parse(f_h.read())


def test_builtin_provider():
    provider = builtin_provider.BuiltinProvider('builtin.xml')
    assert provider.content is not None


def test_builtin_provider_missing():
    provider = builtin_provider.BuiltinProvider('missing_builtin_config.xml')
    assert provider.content is None
