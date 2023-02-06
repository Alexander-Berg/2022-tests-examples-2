import pytest

import configs_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['configs_admin.generated.service.pytest_plugins']


@pytest.fixture
def static_config(monkeypatch):
    def _patcher(config):
        monkeypatch.setattr('configs_admin.static.STATIC_CONFIG', config)

    return _patcher


@pytest.fixture
def patcher_tvm_ticket_check(patch):
    def _patcher(src_service_name):
        return _patch_tvm_ticket_check(patch, src_service_name)

    return _patcher


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'expected_service_name')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def objected_client(web_app_client):
    class Client:
        def __init__(self, app):
            self.app = app

        async def get_config(self, name):
            url = f'/v1/configs/{name}/'
            response = await self.app.get(url)
            return await response.json()

        async def update_config(
                self, name, old_value, new_value, verbose=False,
        ):
            url = f'/v1/configs/{name}/'
            response = await self.app.post(
                url, json={'old_value': old_value, 'new_value': new_value},
            )
            if verbose:
                return await response.json()
            assert response.status == 200, await response.text()

        async def update_definitions(
                self, actual_commit, new_commit, definitions, verbose=False,
        ):
            url = '/v1/schemas/definitions/'
            response = await self.app.post(
                url,
                json={
                    'actual_commit': actual_commit,
                    'new_commit': new_commit,
                    'definitions': definitions,
                },
            )
            if verbose:
                return await response.json()
            assert response.status == 200, await response.text()

        async def get_last_commit(self):
            url = '/v1/schemas/actual_commit/'
            response = await self.app.get(url)

            return (await response.json()).get('commit') or ''

        async def update_schemas(
                self, actual_commit, new_commit, schemas, group, verbose=False,
        ):
            url = '/v1/schemas/'
            response = await self.app.post(
                url,
                json={
                    'actual_commit': actual_commit,
                    'new_commit': new_commit,
                    'schemas': schemas,
                    'group': group,
                },
            )
            if verbose:
                return await response.json()
            assert response.status == 200, await response.text()

    return Client(web_app_client)
