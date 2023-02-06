# pylint: disable=inconsistent-return-statements,unused-variable
from taxi.util import client_session

from taxi_strongbox.components.sessions import vault_session as vs


async def test_vault_session(mockserver):
    @mockserver.json_handler('/vault-api/', prefix=True)
    def _request(request):
        headers = request.headers
        url = request.url
        assert headers['Authorization'] == 'OAuth top secret'
        if 'secrets/' in url:
            assert 'SECRET_NAME_1' in url or 'SECRET_NAME_2' in url
            if 'SECRET_NAME_1' in url:
                return mockserver.make_response(
                    json={
                        'status': 'ok',
                        'secret': {
                            'secret_versions': [
                                {'version': 'uuid_1', 'created_at': 763746300},
                                {'version': 'uuid_2', 'created_at': 763746300},
                            ],
                        },
                    },
                )
            return mockserver.make_response(
                json={
                    'status': 'ok',
                    'secret': {
                        'secret_versions': [
                            {'version': 'uuid_3', 'created_at': 763746300},
                            {'version': 'uuid_4', 'created_at': 763746300},
                        ],
                    },
                },
            )
        if 'versions/' in url:
            assert 'VERSION_UUID_1' in url or 'VERSION_UUID_2' in url
            if 'VERSION_UUID_1' in url:
                return mockserver.make_response(
                    json={
                        'status': 'ok',
                        'version': {
                            'value': [
                                {'key': 'key_1', 'value': 'value_1'},
                                {'key': 'key_2', 'value': 'value_2'},
                            ],
                        },
                    },
                )
            return mockserver.make_response(
                json={
                    'status': 'ok',
                    'version': {
                        'value': [
                            {'key': 'key_3', 'value': 'value_3'},
                            {'key': 'key_4', 'value': 'value_4'},
                        ],
                    },
                },
            )

    vault_session = vs.VaultSession(
        session=client_session.get_client_session(),
        token='top secret',
        log_extra=None,
    )
    secret_versions = await vault_session.get_secret_versions_bulk(
        ['SECRET_NAME_1', 'SECRET_NAME_2'],
    )
    assert secret_versions == {
        'SECRET_NAME_1': [
            vs.SecretVersion('uuid_1', 763746300),
            vs.SecretVersion('uuid_2', 763746300),
        ],
        'SECRET_NAME_2': [
            vs.SecretVersion('uuid_3', 763746300),
            vs.SecretVersion('uuid_4', 763746300),
        ],
    }
    secret_values = await vault_session.get_secret_values_bulk(
        ['VERSION_UUID_1', 'VERSION_UUID_2'],
    )
    assert secret_values == {
        'VERSION_UUID_1': [
            vs.SecretValue('key_1', 'value_1'),
            vs.SecretValue('key_2', 'value_2'),
        ],
        'VERSION_UUID_2': [
            vs.SecretValue('key_3', 'value_3'),
            vs.SecretValue('key_4', 'value_4'),
        ],
    }
