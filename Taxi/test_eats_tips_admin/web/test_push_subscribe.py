import http

from aiohttp import web
import pytest

from test_eats_tips_admin import conftest


def _format_eats_tips_admin_subscribe(
        *,
        device_type='ios',
        device_id,
        channel_name,
        channel_token,
        push_enabled_in_system=True,
):
    return {
        'device_type': device_type,
        'device_id': device_id,
        'channel_name': channel_name,
        'channel_token': channel_token,
        'push_enabled_in_system': push_enabled_in_system,
    }


@pytest.mark.parametrize(
    (
        'jwt_token',
        'params',
        'expected_code',
        'expected_times_called_client_notify',
    ),
    (
        pytest.param(
            conftest.JWT_USER_1,
            _format_eats_tips_admin_subscribe(
                device_type='ios',
                device_id='0000000000000001',
                channel_name='fcm',
                channel_token='00000000-0000-0000-0000-000000000001',
            ),
            http.HTTPStatus.BAD_REQUEST,
            0,
            id='bad_request',
        ),
        pytest.param(
            conftest.JWT_USER_1,
            _format_eats_tips_admin_subscribe(
                device_type='ios',
                device_id='0000000000000001',
                channel_name='apns',
                channel_token='00000000-0000-0000-0000-000000000001',
            ),
            http.HTTPStatus.OK,
            1,
            id='ok-ios',
        ),
        pytest.param(
            conftest.JWT_USER_1,
            _format_eats_tips_admin_subscribe(
                device_type='android',
                device_id='0000000000000001',
                channel_name='fcm',
                channel_token='00000000-0000-0000-0000-000000000001',
            ),
            http.HTTPStatus.OK,
            1,
            id='ok-android',
        ),
        pytest.param(
            conftest.INCORRECT_JWT,
            _format_eats_tips_admin_subscribe(
                device_type='ios',
                device_id='0000000000000001',
                channel_name='apns',
                channel_token='00000000-0000-0000-0000-000000000001',
            ),
            http.HTTPStatus.UNAUTHORIZED,
            0,
            id='not-approve-sms',
        ),
        pytest.param(
            conftest.JWT_USER_1,
            _format_eats_tips_admin_subscribe(
                device_type='ios',
                device_id='0000000000000001',
                channel_name='apns',
                channel_token='00000000-0000-0000-0000-000000000001',
                push_enabled_in_system=False,
            ),
            http.HTTPStatus.OK,
            0,
            id='push_disabled_in_system',
        ),
    ),
)
async def test_push_subscribe(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_client_notify,
        jwt_token,
        params,
        expected_code,
        expected_times_called_client_notify,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    @mock_client_notify('/v1/subscribe')
    async def _mock_v1_subscribe(request):
        return web.json_response({}, status=http.HTTPStatus.OK)

    response = await taxi_eats_tips_admin_web.post(
        '/v1/application/push/subscribe',
        json=params,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code
    assert (
        _mock_v1_subscribe.times_called == expected_times_called_client_notify
    )
    if response.status == http.HTTPStatus.OK:
        assert _mock_alias_to_id.times_called == 1
