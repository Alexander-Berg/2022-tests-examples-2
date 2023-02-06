import re
import pytest

import requests_mock
from library.python.vault_client import instances

import metrika.pylib.auth as mta
import metrika.pylib.vault as mtv


class VaultTestError(Exception):
    pass


@pytest.fixture()
def valid_response():
    with requests_mock.Mocker() as m:
        response = {
            u'status': u'ok',
            u'version': {
                u'version': u'ver-01cj4wmjr4y307q7ps39cxv9bt',
                u'created_at': 1531320093.445,
                u'value': [
                    {
                        u'value': u'qwerty',
                        u'key': u'passwd'
                    },
                    {
                        u'value': u'zxc',
                        u'key': u'client'
                    },
                ],
                u'secret_uuid': u'sec-01cj4wmjqzas7dgggj55fx4dzt',
                u'creator_login': u'velom',
                u'created_by': 1120000000018097,
                u'secret_name': u'mtutils_vault_test',
            },
        }
        m.get(re.compile(instances.VAULT_PRODUCTION_API), json=response)
        yield


def test_vault(monkeypatch, valid_response):
    monkeypatch.setattr(mtv, '_get_rsa', lambda x: None)
    secret = mtv.Secret('sec-01cj4wmjqzas7dgggj55fx4dzt', auth_type='rsa')

    data = secret.get_secret(version='ver-01cj4wmjr4y307q7ps39cxv9bt')

    assert data['passwd'] == 'qwerty'
    assert data['client'] == 'zxc'


def test_auth_type_check():
    with pytest.raises(mtv.VaultError):
        mtv.Secret('123', auth_type='hello')


def test_get_robot_oauth_token_called_when_oauth_token_is_none(monkeypatch):
    def mock_get_robot_oauth_token(*args, **kwargs):
        raise VaultTestError
    monkeypatch.setattr(mta, 'get_robot_oauth_token', mock_get_robot_oauth_token)

    with pytest.raises(VaultTestError):
        mtv.Secret('123', auth_type='oauth')


def test_vault_client(monkeypatch, valid_response):
    monkeypatch.setattr(mtv, '_get_rsa', lambda x: None)
    client = mtv.VaultClient(auth_type='rsa')
    secret = mtv.Secret('sec-01cj4wmjqzas7dgggj55fx4dzt', vault_client=client)

    data = secret.get_secret(version='ver-01cj4wmjr4y307q7ps39cxv9bt')

    assert data['passwd'] == 'qwerty'
    assert data['client'] == 'zxc'


def test_get_robot_secrets(monkeypatch):
    monkeypatch.setattr(mta, 'get_robot_oauth_token', lambda: 'fake token')
    monkeypatch.setattr(mtv.Secret, 'get_latest_secret', lambda x: {"Hello": "World"})
    data = mtv.get_robot_secrets()
    assert type(data) is dict
    assert data['Hello'] == 'World'

    with pytest.raises(mtv.VaultError):
        mtv.get_robot_secrets(secret_key='missing')
