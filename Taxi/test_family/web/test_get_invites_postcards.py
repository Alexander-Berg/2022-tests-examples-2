import http

import pytest

from test_family import conftest

DEFAULT_HEADER = {'X-Remote-IP': '127.0.0.1', 'X-Yandex-UID': '1234'}


@pytest.mark.parametrize(
    'phone_id, expected_code, expected_response',
    [
        pytest.param(
            conftest.UserPhoneIDs.USER_WITHOUT_INVITE,
            http.HTTPStatus.NOT_FOUND,
            None,
            id='no-invite-in-db',
        ),
        pytest.param(
            conftest.UserPhoneIDs.USER_FAMILY_MEMBER,
            http.HTTPStatus.NOT_FOUND,
            None,
            id='invite-in-db-but-inactive-in-passport',
            marks=pytest.mark.skip,
        ),
        pytest.param(
            conftest.UserPhoneIDs.USER_FAMILY_VALID_INVITE,
            http.HTTPStatus.OK,
            {
                'family_invites': [
                    {
                        'button_text': 'Принять приглашение и узнать о семье',
                        'deeplink': (
                            'yandextaxi://coopaccount?type=family&'
                            'action=invite&invite_id=valid_invite'
                        ),
                        'id': 'valid_invite',
                        'image': 'image1',
                        'link': (
                            'https://passport-test.yandex.ru/profile/'
                            'family/invite/valid_invite'
                        ),
                        'member_phone_id': '00aaaaaaaaaaaaaaaaaaaa02',
                        'text': 'text1',
                    },
                    {
                        'button_text': 'Принять приглашение и узнать о семье',
                        'deeplink': (
                            'yandextaxi://coopaccount?type=family&'
                            'action=invite&invite_id=valid_invite_2'
                        ),
                        'id': 'valid_invite_2',
                        'image': 'image2',
                        'link': (
                            'https://passport-test.yandex.ru/profile/'
                            'family/invite/valid_invite_2'
                        ),
                        'member_phone_id': '00aaaaaaaaaaaaaaaaaaaa02',
                        'text': 'text2',
                    },
                ],
            },
            id='valid-invites-for-user',
            marks=pytest.mark.skip,
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxi_family.accept_family_invite.button_text': {
            'ru': 'Принять приглашение и узнать о семье',
            'eu': 'stub',
        },
    },
)
async def test_get_invites_postcards(
        web_app_client,
        mock_all_api,
        phone_id,
        expected_code,
        expected_response,
):
    response = await web_app_client.post(
        '/4.0/family/v1/invite/postcards/get',
        headers={**DEFAULT_HEADER},
        params={'phone_id': phone_id},
    )
    assert response.status == expected_code
    if expected_response is not None:
        assert await response.json() == expected_response
