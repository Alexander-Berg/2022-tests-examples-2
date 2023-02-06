from metrika.pylib.config import get_json_config_from_bishop
from metrika.pylib.config.parsers.json_parser import JsonParser
from metrika.pylib.config.providers import bishop_provider


def test_secret(vault_response, vault_client):
    assert JsonParser(vault_client=vault_client).parse('{"test_secret": "!secret sec-01cj4wmjqzas7dgggj55fx4dzt"}') == {
        'test_secret': {'passwd': 'qwerty', 'client': 'zxc'}
    }


def test_secret_key(vault_response, vault_client):
    assert JsonParser(vault_client=vault_client).parse('{"test_secret": "!secret_key sec-01cj4wmjqzas7dgggj55fx4dzt passwd"}') == {
        'test_secret': 'qwerty'
    }


def test_bishop_json_config(bishop, vault_client, monkeypatch):
    def mock_fetch(obj, *args, **kwargs):
        obj._version = 777
        obj._content = '{"hello": 777}'

    monkeypatch.setattr(bishop_provider.BishopProvider, 'fetch', mock_fetch)

    config = get_json_config_from_bishop('program', 'environment', client=bishop, vault_client=vault_client)

    assert config.hello == 777
