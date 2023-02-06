import http

from aiohttp import web
import pytest

from test_eats_tips_admin import conftest


def _format_eats_tips_admin_unsubscribe(*, device_id):
    return {'device_id': device_id}


@pytest.mark.parametrize(
    ('jwt_token', 'params', 'expected_code'),
    (
        pytest.param(
            conftest.INCORRECT_JWT,
            _format_eats_tips_admin_unsubscribe(device_id='0000000000000001'),
            http.HTTPStatus.UNAUTHORIZED,
            id='not-founded-partner',
        ),
        pytest.param(
            conftest.JWT_USER_1,
            _format_eats_tips_admin_unsubscribe(device_id='0000000000000001'),
            http.HTTPStatus.OK,
            id='ok',
        ),
    ),
)
async def test_push_unsubscribe(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_client_notify,
        jwt_token,
        params,
        expected_code,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    @mock_client_notify('/v1/unsubscribe')
    async def _mock_v1_subscribe(request):
        return web.json_response({}, status=http.HTTPStatus.OK)

    response = await taxi_eats_tips_admin_web.post(
        '/v1/application/push/unsubscribe',
        json=params,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        assert _mock_v1_subscribe.times_called == 1
        assert _mock_alias_to_id.times_called == 1
