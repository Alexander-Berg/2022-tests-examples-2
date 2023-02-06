import re
import pytest
import requests_mock
import metrika.pylib.bishop as bp
import metrika.pylib.vault as mtv

from library.python.vault_client import instances


@pytest.fixture(scope='session')
def bishop():
    bishop = bp.Bishop(
        token='',
    )
    return bishop


@pytest.fixture()
def vault_client():
    return mtv.VaultClient(auth_type='rsa')


@pytest.fixture()
def vault_missing_version_response(monkeypatch):
    monkeypatch.setattr(mtv, '_get_rsa', lambda x: None)

    with requests_mock.Mocker() as m:
        response = {
            u'api_request_id': u'862dbf1fbf910d3b627050b5cc07d367',
            u'class': u'SecretVersion',
            u'code': u'nonexistent_entity_error',
            u'environment': u'production',
            u'hostname': u'vault-v5.passport.yandex.net',
            u'id': u'01e6gm3ed0pnwrh9pdv6ezwar9',
            u'message': u'Requested a non-existent entity (SecretVersion, 01e6gm3ed0pnwrh9pdv6ezwar9)',
            u'status': u'error',
        }
        m.get(
            re.compile(
                instances.VAULT_PRODUCTION_API + '.*/versions/ver-01e6gm3ed0pnwrh9pdv6ezwar9'
            ),
            json=response,
            status_code=400,
        )
        yield


@pytest.fixture()
def vault_response(monkeypatch):
    monkeypatch.setattr(mtv, '_get_rsa', lambda x: None)

    with requests_mock.Mocker() as m:
        version_response = {
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
        secret_response = {
            u'status': u'ok',
            u'secret': {
                u'uuid': u'sec-01cj4wmjqzas7dgggj55fx4dzt',
                u'name': u'mtutils_vault_test',
                u'created_at': 1531320093.44,
                u'updated_at': 1531931494.286,
                u'creator_login': u'velom',
                u'secret_versions': [
                    {
                        u'keys': [
                            u'client',
                            u'passwd'
                        ],
                        u'created_at': 1531320093.445,
                        u'creator_login': u'velom',
                        u'version': u'ver-01cj4wmjr4y307q7ps39cxv9bt',
                        u'created_by': 1120000000018097
                    }
                ],
                u'updated_by': 1120000000018097
            },
            u'page': 0,
            u'page_size': 50
        }

        m.get(re.compile(instances.VAULT_PRODUCTION_API + '.*secret.*'), json=secret_response)
        m.get(re.compile(instances.VAULT_PRODUCTION_API + '.*version.*'), json=version_response)
        yield
