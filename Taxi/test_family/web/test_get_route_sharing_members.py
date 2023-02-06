import http

import pytest

from test_family import conftest

IP_HEADER = {'X-Remote-IP': '127.0.0.1'}


@pytest.mark.parametrize(
    'user_uid, expected_code, expected_response',
    [
        pytest.param(
            conftest.UserUIDs.NON_EXISTENT_UID,
            http.HTTPStatus.NOT_FOUND,
            None,
            id='no-user-in-passport',
            marks=pytest.mark.skip,
        ),
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            http.HTTPStatus.NOT_FOUND,
            None,
            id='user-without-family-info',
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_OWNER,
            http.HTTPStatus.OK,
            {'members': []},
            id='user-family-owner--cant-share-ride',
            marks=pytest.mark.skip,
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_MEMBER,
            http.HTTPStatus.OK,
            {
                'members': [
                    {'name': 'member', 'role': 'owner', 'yandex_uid': '1'},
                ],
            },
            id='user-family-member--can-share-ride',
            marks=pytest.mark.skip,
        ),
    ],
)
async def test_get_route_sharing_members(
        web_app_client,
        mock_passport_api,
        user_uid,
        expected_code,
        expected_response,
):
    response = await web_app_client.get(
        '/4.0/family/v1/route_sharing_members',
        headers={**IP_HEADER, 'X-Yandex-UID': user_uid},
    )
    assert response.status == expected_code
