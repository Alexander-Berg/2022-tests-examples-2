from aiohttp import web
import pytest

from generated.clients import ok
import generated.models.ok as ok_module
from taxi.codegen import swaggen_serialization

from client_ok import components as client_ok


@pytest.mark.parametrize(
    'token, body, response_status',
    [
        pytest.param(
            'token1234',
            {
                'object_id': 'LEEMURQUEUE-9',
                'text': 'Согласуем согласование',
                'stages': [
                    {'approver': 'leemurus'},
                    {
                        'need_all': False,
                        'stages': [
                            {'approver': 'trusienkodv'},
                            {'approver': 'artemzaxarov'},
                        ],
                    },
                ],
            },
            201,
            id='simple test',
        ),
        pytest.param(
            'token1234',
            {
                'object_id': 'LEEMURQUEUE-9',
                'text': 'Согласуем согласование',
                'stages': [],
            },
            400,
            id='incorrect stages',
        ),
        pytest.param(
            'token1234',
            {
                'object_id': 'LEEMURQUEUE-9',
                'stages': [{'approver': 'leemurus'}],
            },
            400,
            id='no text',
        ),
        pytest.param(
            'token1234',
            {
                'object_id': 'LEEMURQUEUE-9',
                'text': 'Согласуем согласование',
                'stages': [{'approver': 'leemurus'}],
            },
            403,
            id='incorrect token',
        ),
    ],
)
async def test_create(
        library_context,
        set_custom_token,
        load_json,
        mock_ok,
        token,
        body,
        response_status,
):
    set_custom_token(token)
    client = client_ok.OKClient(library_context, None, None)
    response = load_json('response.json')

    @mock_ok('/api/approvements/')
    def create_approvement(request):
        auth_token = client.AUTHORIZATION_FORMAT.format(token)
        assert request.headers.get('Authorization') == auth_token

        return web.json_response(response, status=response_status)

    try:
        resp = await client.create_approvement(
            body=ok_module.CreateApprovementBody.deserialize(body),
        )
    except (ok.ApiApprovementsPost400, ok.ApiApprovementsPost403) as error:
        resp = error
        assert resp.status == response_status
        return
    except swaggen_serialization.ValidationError:
        assert response_status != 200
        return

    assert resp.status == 201
    assert resp.body.status == 'in_progress'
    assert resp.body.object_id == 'LEEMURQUEUE-9'
    assert create_approvement.times_called == 1
