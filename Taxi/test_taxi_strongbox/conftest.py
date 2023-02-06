# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name
# pylint: disable=inconsistent-return-statements,unused-variable
import pytest

from taxi_strongbox.components.sessions import clownductor_session as clowns
import taxi_strongbox.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi_strongbox.generated.service.pytest_plugins',
    'task_processor_lib.cubes_pytest_plugin',
]


@pytest.fixture
def patch_clownductor_session(patch_aiohttp_session, response_mock):
    def _patch_clownductor_session(clownductor_response):
        @patch_aiohttp_session(clowns.ClownductorSession.base_url, 'GET')
        def request(method, url, *args, **kwargs):
            return response_mock(json=clownductor_response)

        return request

    return _patch_clownductor_session


@pytest.fixture
def added_roles_from_secdist():
    return [
        {'abc_id': 1234, 'role': 'READER'},
        {'abc_id': 2345, 'role': 'READER'},
        {'abc_id': 5678, 'role': 'OWNER'},
    ]


@pytest.fixture(name='clown_roles_mock')
def _clown_roles_mock(mockserver):
    def _wrapper(responsibles=None):
        @mockserver.json_handler(
            '/clownductor/permissions/v1/roles/responsibles/',
        )
        async def _responsibles(request):
            if responsibles is not None:
                return {'responsibles': responsibles}
            return {
                'responsibles': [
                    {
                        'id': 1,
                        'login': 'super',
                        'role': 'role',
                        'is_super': True,
                    },
                ],
            }

        return _responsibles

    return _wrapper


@pytest.fixture(name='vault_versions_mock')
def _vault_versions_mock(mockserver):
    def _make_mock(secret_uuid, response_version_uuid='version_uuid_1'):
        @mockserver.json_handler(f'vault-api/secrets/YAV_UUID_2/versions/')
        def _request(request):
            return mockserver.make_response(
                json={'status': 'ok', 'secret_version': response_version_uuid},
            )

        return _request

    return _make_mock


@pytest.fixture(name='add_secret')
def _add_secret(web_app_client):
    async def _wrapper(method, headers, body):
        request = {'POST': web_app_client.post, 'PUT': web_app_client.put}.get(
            method,
        )
        response = await request('/v1/secrets/', headers=headers, json=body)
        return response

    return _wrapper


@pytest.fixture(name='edit_secret')
def _edit_secret(web_app_client):
    async def _wrapper(headers, body):
        response = await web_app_client.post(
            '/v1/secrets/edit/', headers=headers, json=body,
        )
        return response

    return _wrapper


@pytest.fixture(name='config_service_overrides', scope='session')
def _config_service_overrides():
    return {
        'STRONGBOX_FEATURES': {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'auto_discover_scope': True,
                        'arcadia_pr_creation': True,
                    },
                },
            },
        },
    }


@pytest.fixture(name='config_service_defaults', scope='session')
def _config_service_defaults(
        config_service_defaults, config_service_overrides,
):
    defaults = {**config_service_defaults}
    defaults.update(config_service_overrides)
    return defaults
