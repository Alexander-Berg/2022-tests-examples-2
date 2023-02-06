import os
import six
import pytest

import yatest.common as yatc

import metrika.pylib.structures.dotdict as mdd

from metrika.pylib.config import get_xml_config_from_file, get_xml_config_from_bishop
from metrika.pylib.config.parsers import xml_parser
from metrika.pylib.config.providers import bishop_provider
import metrika.pylib.config.errors as errors


class XmlTestException(Exception):
    pass


def test_init():
    config = xml_parser.XmlParser().parse('<yandex></yandex>')

    assert isinstance(config, mdd.DotDict)


def test_valid_xml():
    os.environ['ENVI_TEST_VAR'] = '444'

    config = get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/config.xml'))

    assert isinstance(config.default_is_string, six.string_types)
    assert isinstance(config.int_if_convertable, int)
    assert isinstance(config.force_str, six.string_types)
    assert isinstance(config.cdata_works, six.string_types)
    assert config.cdata_works == 'cdata_value'

    assert isinstance(config.empty_str, six.string_types)
    assert config.empty is None

    assert isinstance(config.space, six.string_types)
    assert config.space == ' '

    assert isinstance(config.empty_list, list)
    assert len(config.empty_list) == 0

    assert isinstance(config.settings.host, mdd.DotDict)

    assert isinstance(config.settings.host.hostname, six.string_types)
    assert config.settings.host.hostname == 'mtgiga001-1.metrika.yandex.net'

    assert isinstance(config.settings.host.port, int)
    assert config.settings.host.port == 666

    assert isinstance(config.settings.host.sampling, float)
    assert config.settings.host.sampling == 0.100

    assert isinstance(config.settings.host.debug, bool)
    assert config.settings.host.debug is True

    assert isinstance(config.settings.host.replicas, list)
    assert config.settings.host.replicas == ['mtgiga001-2.metrika.yandex.net', 'mtgiga001-3.metrika.yandex.net']

    assert isinstance(config.connections, list)
    assert config.connections[0].hosts[0].ip == '::1'
    assert config.connections[0].hosts[0].port == 80
    assert config.connections[1].ip == '127.0.0.1'
    assert config.connections[1].port == 443

    assert isinstance(config.envi, int)
    assert config.envi == 444

    del os.environ['ENVI_TEST_VAR']


def test_from_env():
    # if exist from_env take precedence over text node value
    os.environ['ENVI_TEST_VAR'] = '321'

    config = get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/config.xml'))
    assert config.envi == 321

    del os.environ['ENVI_TEST_VAR']


def test_from_env_multiple():
    # check multiple from_env vars override
    os.environ['ENVI_TEST_VAR'] = '555'
    os.environ['ENVI_TEST_VAR_OVERRIDE'] = '3213'

    config = get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/config.xml'))
    assert config.envi_multiple == 3213

    del os.environ['ENVI_TEST_VAR_OVERRIDE']


def test_from_env_or_default_with_env_var():
    os.environ['FROM_ENV_OR_DEFAULT_ENV_VAR'] = '777'

    config = get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/from_env_or_default.xml'))
    assert config.value == 777
    del os.environ['FROM_ENV_OR_DEFAULT_ENV_VAR']


def test_from_env_or_default_without_env_var():
    config = get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/from_env_or_default.xml'))
    assert config.value == 555


def test_from_env_variables_is_missing():
    with pytest.raises(errors.XMLConfigEnvironmentVariableMissing):
        get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/from_env_variables_is_missing.xml'))


def test_invalid_xml():
    """
    Test XMLConfig error is raised in case of wrong xml (initial exception was cathed)
    """
    with pytest.raises(errors.XMLConfigError):
        get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/invalid_xml.xml'))


def test_from_env_attributes():
    """
    Test XMLConfig error is raised in case of attributes from_env and from_env_or_default is used together
    """
    with pytest.raises(errors.XMLConfigAttributeError):
        get_xml_config_from_file(yatc.source_path('metrika/pylib/config/tests/data/xml/from_env_attributes.xml'))


def test_list_multiple_types():
    """
    Lists should consist of objects with same type
    """
    text = "<yandex><a type='list'><b>123</b><c><d>123</d></c></a></yandex>"

    with pytest.raises(errors.XMLConfigMultipleListTypes):
        xml_parser.XmlParser().parse(text)


def test_uncovertable_int():
    """
    Test error is raised if cant convert value to integer
    """
    text = "<yandex><a type='int'>asdf</a></yandex>"

    with pytest.raises(errors.XMLConfigConvertError):
        xml_parser.XmlParser().parse(text)


def test_uncovertable_float():
    """
    Test error is raised if cant convert value to float
    """
    text = "<yandex><a type='float'>asdf</a></yandex>"

    with pytest.raises(errors.XMLConfigConvertError):
        xml_parser.XmlParser().parse(text)


def test_uncovertable_bool():
    """
    Test error is raised if cant convert value to boolean
    """
    text = "<yandex><a type='bool'>tr3yt</a></yandex>"

    with pytest.raises(errors.XMLConfigConvertError):
        xml_parser.XmlParser().parse(text)


def test_bishop_xml_config(bishop, monkeypatch):
    def mock_fetch(obj, *args, **kwargs):
        obj._version = 777
        obj._content = '<yandex><hello>777</hello></yandex>'

    monkeypatch.setattr(bishop_provider.BishopProvider, 'fetch', mock_fetch)

    config = get_xml_config_from_bishop('program', 'environment', client=bishop)

    assert config.hello == 777


def test_from_yav(vault_response, vault_client):
    config = get_xml_config_from_file(
        yatc.source_path('metrika/pylib/config/tests/data/xml/from_yav.xml'),
        vault_client=vault_client,
    )
    assert isinstance(config.secret, six.string_types)
    assert config.secret == 'qwerty'


def test_from_yav_missing_version(vault_missing_version_response, vault_client):
    with pytest.raises(errors.XMLConfigAttributeError):
        get_xml_config_from_file(
            yatc.source_path('metrika/pylib/config/tests/data/xml/from_yav_missing_version.xml'),
            vault_client=vault_client,
        )


def test_from_yav_invalid_format(vault_missing_version_response, vault_client):
    with pytest.raises(errors.XMLConfigAttributeError):
        get_xml_config_from_file(
            yatc.source_path('metrika/pylib/config/tests/data/xml/from_yav_invalid_format.xml'),
            vault_client=vault_client,
        )


def test_from_yav_missing_key_in_secret(vault_response, vault_client):
    with pytest.raises(errors.XMLConfigAttributeError):
        get_xml_config_from_file(
            yatc.source_path('metrika/pylib/config/tests/data/xml/from_yav_missing_key_in_secret.xml'),
            vault_client=vault_client,
        )


def test_vault_client_overrides():
    vault_client = "wowow"
    parser = xml_parser.XmlParser(vault_client=vault_client)

    assert parser.vault_client == vault_client


def test_secret_is_cached(vault_missing_version_response, vault_response, vault_client, monkeypatch):
    def mock_get_secret(*args, **kwargs):
        return {'passwd': 'mocked_get_secret_value'}

    parser = xml_parser.XmlParser(vault_client=vault_client)
    secret = parser.get_text_from_yav(value='ver-01cj4wmjr4y307q7ps39cxv9bt/passwd')

    monkeypatch.setattr(parser, 'get_secret', mock_get_secret)

    # get_secret was not called for second request with same value
    second_call_secret = parser.get_text_from_yav(value='ver-01cj4wmjr4y307q7ps39cxv9bt/passwd')
    assert secret == second_call_secret

    # get_secret called for another version request
    another_secret = parser.get_text_from_yav(value='ver-01e6gm3ed0pnwrh9pdv6ezwar9/passwd')
    assert another_secret == "mocked_get_secret_value"
