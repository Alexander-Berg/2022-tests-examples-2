from aiohttp import web
import pytest

from generated.clients import ok
from taxi.codegen import swaggen_serialization

from client_ok import components as client_ok


@pytest.mark.parametrize(
    'token, uuid, response_status',
    [
        pytest.param(
            'token1234',
            '848601b7-945d-4ae5-9775-fefa62c27c66',
            200,
            id='simple test',
        ),
        pytest.param(
            'token1235',
            '848601b7-945d-4ae5-9775-fefa62c27c66',
            403,
            id='incorrect token',
        ),
        pytest.param(
            'token1235',
            '848601b7-945d-4ae5-9775-fefa62c27c66',
            404,
            id='uuid not found',
        ),
        pytest.param('token1234', 1, 500, id='incorrect uuid'),
    ],
)
async def test_close(
        library_context,
        set_custom_token,
        load_json,
        mock_ok,
        token,
        uuid,
        response_status,
):
    set_custom_token(token)
    client = client_ok.OKClient(library_context, None, None)
    response = load_json('response.json')

    @mock_ok(f'/api/approvements/{uuid}/close/')
    def close_approvement(request):
        auth_token = client.AUTHORIZATION_FORMAT.format(token)
        assert request.headers.get('Authorization') == auth_token

        return web.json_response(response, status=response_status)

    try:
        resp = await client.close_approvement(uuid=uuid)
    except (
        ok.ApiApprovementsUuidClosePost403,
        ok.ApiApprovementsUuidClosePost404,
    ) as error:
        resp = error
        assert resp.status == response_status
        return
    except swaggen_serialization.ValidationError:
        assert response_status != 200
        return

    assert resp.status == 200
    assert resp.body.status == 'in_progress'
    assert resp.body.object_id == 'LEEMURQUEUE-9'
    assert close_approvement.times_called == 1
