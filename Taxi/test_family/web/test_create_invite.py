# pylint: disable=W0212
import http

import pytest

from family.api import create_invite
from family.repositories import invites as invites_repo
from test_family import conftest

IP_HEADER = {'X-Remote-IP': '127.0.0.1'}
ISSUER_PHONE = '+71111111111'

REQUEST_BODY = {
    'phone': ISSUER_PHONE,
    'image': 'some_image_tag',
    'text': 'Welcome to family account!',
}


@pytest.mark.parametrize(
    'user_uid, expected_status, expected_response',
    [
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            http.HTTPStatus.NOT_FOUND,
            {
                'code': create_invite._DEFAULT_ERROR_CODE,
                'message': 'У пользователя нет семьи в паспорте',
            },
            id='user-without-family-cant-create-invite',
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_OWNER_CANT_CREATE_INVITE,
            http.HTTPStatus.NOT_FOUND,
            {
                'code': create_invite._DEFAULT_ERROR_CODE,
                'message': 'Превышен лимит на пришлашения',
            },
            id='user-with-family--invite-limit-exceeded',
            marks=pytest.mark.skip,
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_OWNER,
            http.HTTPStatus.CREATED,
            None,
            id='user-with-family--success',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxi_family.invite.base_error': {
            'ru': 'Ошибка при создании приглашения',
            'eu': 'stub',
        },
        'taxi_family.invite.limit_exceeded': {
            'ru': 'Превышен лимит на пришлашения',
            'eu': 'stub',
        },
        'taxi_family.invite.no_family_for_user': {
            'ru': 'У пользователя нет семьи в паспорте',
            'eu': 'stub',
        },
        'taxi_family.invite.already_exists': {
            'ru': 'Приглашение уже отправлено этому пользователю',
            'eu': 'stub',
        },
    },
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_create_invite(
        web_app_client,
        mock_all_api,
        web_context,
        user_uid,
        expected_status,
        expected_response,
):
    response = await web_app_client.post(
        '/4.0/family/v1/invite/postcards/create',
        json=REQUEST_BODY,
        headers={**IP_HEADER, 'X-Yandex-UID': user_uid},
    )
    assert response.status == expected_status
    if expected_response is not None:
        assert await response.json() == expected_response
    if response.status == http.HTTPStatus.CREATED:
        invites = await invites_repo.get(
            web_context, conftest.UserPhoneIDs.USER_FAMILY_MEMBER,
        )
        assert len(invites) == 1
