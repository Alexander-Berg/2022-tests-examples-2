from aiohttp import web
import pytest


from generated.clients import sup
import generated.models.sup as sup_module
from taxi.codegen import swaggen_serialization

from client_sup import components as client_sup


@pytest.mark.parametrize(
    'dry_run, token, body, response_status',
    [
        pytest.param(
            False,
            'token_adsadas1231',
            {
                'receiver': ['0b558ec99d89465baaf719d59ff6d46'],
                'project': 'crm',
                'notification': {
                    'title': 'Hello',
                    'body': 'Hello Peter Parker',
                    'link': 'yandex.ru',
                },
                'ttl': 200,
            },
            200,
            id='simple test',
        ),
        pytest.param(
            False,
            'token_adsadas1231',
            {
                'receiver': ['0b558ec99d89465baaf719d59ff6d46'],
                'project': 'crm',
                'notification': {
                    'body': 'Hello Peter Parker',
                    'link': 'yandex.ru',
                },
                'ttl': 200,
            },
            200,
            id='no title',
        ),
        pytest.param(
            False,
            'token_adsadas1231',
            {
                'receiver': ['0b558ec99d89465baaf719d59ff6d46'],
                'project': 'crm',
                'notification': {'title': 'Hello', 'link': 'yandex.ru'},
                'ttl': 200,
            },
            200,
            id='no body',
        ),
        pytest.param(
            False,
            'token_adsadas1231',
            {
                'receiver': ['0b558ec99d89465baaf719d59ff6d46'],
                'project': 'crm',
                'notification': {'title': '', 'link': 'yandex.ru'},
                'ttl': 200,
            },
            0,
            id='incorrect title',
        ),
        pytest.param(
            False,
            'token_adsadas1231',
            {
                'receiver': ['0b558ec99d89465baaf719d59ff6d46'],
                'project': 'crm',
                'ttl': 3500,
            },
            200,
            id='no notification field',
        ),
        pytest.param(
            False,
            'token_12312asdasdsa',
            {
                'receiver': ['0b558ec99d89465ac234af719d59ff6d46'],
                'project': '',
                'notification': {
                    'title': 'Hello',
                    'body': 'Hello Peter Parker',
                    'link': 'yandex.ru',
                },
            },
            400,
            id='empty project',
        ),
        pytest.param(
            False,
            'token_12312asdasdsa',
            {
                'receiver': ['0b558ec99d89465ac234af719d59ff6d46'],
                'notification': {
                    'title': 'Hello',
                    'body': 'Hello Peter Parker',
                    'link': 'yandex.ru',
                },
            },
            400,
            id='no project',
        ),
        pytest.param(
            False,
            None,
            {
                'receiver': ['0b558ec99d89465ac234af719d59ff6d46'],
                'project': 'crm',
                'notification': {
                    'title': 'Hello',
                    'body': 'Hello Peter Parker',
                    'link': 'yandex.ru',
                },
            },
            401,
            id='empty token',
        ),
    ],
)
async def test_request(
        library_context,
        set_custom_token,
        mock_sup,
        load_json,
        dry_run,
        token,
        body,
        response_status,
):
    response_body = dict(body, **{'is_data_only': False})

    set_custom_token(token)
    client = client_sup.SUPClient(library_context, None, None)

    @mock_sup('/pushes')
    def send_push(request):
        auth_token = client.AUTHORIZATION_FORMAT.format(token)
        assert request.headers.get('Authorization') == auth_token

        return web.json_response(response_body, status=response_status)

    try:
        resp = await client.send_push(
            dry_run=dry_run, body=sup_module.PushBody.deserialize(body),
        )

        assert resp.body.serialize() == response_body
    except (
        sup.PushesPost400,
        sup.PushesPost401,
        sup.PushesPost503,
        sup.PushesPost504,
    ) as error:
        resp = error
    except swaggen_serialization.ValidationError:
        assert response_status != 200
        return

    assert resp.status == response_status
    assert send_push.times_called == 1
