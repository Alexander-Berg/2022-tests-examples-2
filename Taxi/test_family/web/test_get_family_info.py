import http

import pytest

from test_family import conftest

IP_HEADER = {'X-Remote-IP': '127.0.0.1'}

# TODO return with new tests
@pytest.mark.skip('Temp skip')
@pytest.mark.parametrize(
    'user_uid, phone_id, expected_code, expected_response',
    [
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            conftest.UserPhoneIDs.USER_WITHOUT_INVITE,
            http.HTTPStatus.OK,
            {},
            id='user-without-family',
        ),
    ],
)
async def test_get_family_info(
        web_app_client,
        mock_all_api,
        user_uid,
        phone_id,
        expected_code,
        expected_response,
):
    response = await web_app_client.post(
        '/4.0/family/v1/info/',
        headers={
            **IP_HEADER,
            'X-Yandex-UID': user_uid,
            'X-YaTaxi-PhoneId': phone_id,
        },
    )
    assert response.status == expected_code
    assert await response.json() == expected_response
