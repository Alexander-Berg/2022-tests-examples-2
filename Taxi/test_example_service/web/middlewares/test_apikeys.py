import typing

import pytest

from taxi import settings

from example_service.generated.web.api_key import plugin as apikeys_plugin


APIKEY_HEADER = 'X-YaTaxi-Api-Key'
ERROR_MESSAGE = 'Access is forbidden'
ERROR_CODE = 'FORBIDDEN'
INTERNAL_ERROR_MESSAGE = 'Internal server error'
INTERNAL_ERROR_CODE = 'INTERNAL_SERVER_ERROR'


class Params(typing.NamedTuple):
    environment: str
    apikey_token: typing.Optional[str]
    url: str
    expected_content: typing.Any
    status: int
    do_pop_apikey: typing.Optional[str] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                environment=settings.TESTING,
                apikey_token=None,
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {
                        'reason': '%s header is missing' % APIKEY_HEADER,
                    },
                },
                status=403,
            ),
            id='empty header testing',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token=None,
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {},
                },
                status=403,
            ),
            id='empty header production',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token=None,
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {
                        'reason': '%s header is missing' % APIKEY_HEADER,
                    },
                },
                status=403,
            ),
            id='empty header development',
        ),
        pytest.param(
            Params(
                environment=settings.TESTING,
                apikey_token=None,
                url='/middlewares/check_api_admin_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {
                        'reason': '%s header is missing' % APIKEY_HEADER,
                    },
                },
                status=403,
            ),
            id='empty header api admin testing',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token=None,
                url='/middlewares/check_api_admin_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {},
                },
                status=403,
            ),
            id='empty header api admin production',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token=None,
                url='/middlewares/check_api_admin_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {
                        'reason': '%s header is missing' % APIKEY_HEADER,
                    },
                },
                status=403,
            ),
            id='empty header api admin development',
        ),
        pytest.param(
            Params(
                environment=settings.TESTING,
                apikey_token='SOME_APIKEY_TOKEN',
                url='/middlewares/check_absent_token_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {
                        'reason': 'No token absent_token in tokens list',
                    },
                },
                status=500,
            ),
            id='absent token testing',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token='SOME_APIKEY_TOKEN',
                url='/middlewares/check_absent_token_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {},
                },
                status=500,
            ),
            id='absent token production',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token='ABACABA',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {},
                },
                status=403,
            ),
            id='invalid token production',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='ABACABA',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {'reason': 'Invalid %s header' % APIKEY_HEADER},
                },
                status=403,
            ),
            id='invalid token development',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token='ABACABA',
                url='/middlewares/check_api_admin_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {},
                },
                status=403,
            ),
            id='invalid token api admin production',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='ABACABA',
                url='/middlewares/check_api_admin_apikeys',
                expected_content={
                    'message': ERROR_MESSAGE,
                    'code': ERROR_CODE,
                    'details': {'reason': 'Invalid %s header' % APIKEY_HEADER},
                },
                status=403,
            ),
            id='invalid token api admin development',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='SOME_SECRET',
                url='/middlewares/check_apikeys',
                expected_content='OK',
                status=200,
            ),
            id='correct token',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='HIDDEN_SECRET',
                url='/middlewares/check_api_admin_apikeys',
                expected_content='OK',
                status=200,
            ),
            id='correct api admin token',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token='SOME_SECRET',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {},
                },
                status=500,
                do_pop_apikey='API_ADMIN_SERVICES_TOKENS',
            ),
            id='secdist absent api admin token production',
        ),
        pytest.param(
            Params(
                environment=settings.PRODUCTION,
                apikey_token='SOME_SECRET',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {},
                },
                status=500,
                do_pop_apikey='SOME_APIKEY',
            ),
            id='secdist absent token production',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='SOME_SECRET',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {
                        'reason': (
                            'No admin token example_service_web in secdist'
                        ),
                    },
                },
                status=500,
                do_pop_apikey='API_ADMIN_SERVICES_TOKENS',
            ),
            id='secdist absent api admin token development',
        ),
        pytest.param(
            Params(
                environment=settings.DEVELOPMENT,
                apikey_token='SOME_SECRET',
                url='/middlewares/check_apikeys',
                expected_content={
                    'message': INTERNAL_ERROR_MESSAGE,
                    'code': INTERNAL_ERROR_CODE,
                    'details': {
                        'reason': 'No token some_token_name in secdist',
                    },
                },
                status=500,
                do_pop_apikey='SOME_APIKEY',
            ),
            id='secdist absent token development',
        ),
    ],
)
async def test_apikeys_plugin(
        web_app_client, monkeypatch, simple_secdist, params: Params,
):
    if params.do_pop_apikey:
        # pylint: disable=W0212
        apikeys_plugin.ApikeysBackendMiddleware._api_tokens = None
        # pylint: enable=W0212
        simple_secdist['settings_override'].pop(params.do_pop_apikey)

    monkeypatch.setattr('taxi.settings.ENVIRONMENT', params.environment)

    headers: dict = {}
    if params.apikey_token:
        headers = {'X-YaTaxi-Api-Key': params.apikey_token}
    response = await web_app_client.get(params.url, headers=headers)
    assert response.status == params.status
    if params.status == 200:
        content = await response.text()
    else:
        content = await response.json()
    assert content == params.expected_content
    if params.do_pop_apikey:
        # pylint: disable=W0212
        assert apikeys_plugin.ApikeysBackendMiddleware._api_tokens is None
        # pylint: enable=W0212


async def test_no_api_key_required(web_app_client):
    response = await web_app_client.get('/no-api-key-required')
    assert response.status == 200
    assert await response.text() == 'hello, world'
