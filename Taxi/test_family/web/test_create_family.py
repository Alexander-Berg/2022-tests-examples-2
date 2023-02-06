import http

import pytest

from test_family import conftest

DEFAULT_HEADER = {
    'X-Remote-IP': '127.0.0.1',
    'X-Ya-User-Ticket': 'some_ticket',
}


@pytest.mark.parametrize(
    'user_uid, expected_status, expected_response',
    [
        pytest.param(
            conftest.UserUIDs.USER_WITHOUT_FAMILY,
            http.HTTPStatus.CREATED,
            None,
            id='user-without-family-create-success',
        ),
        pytest.param(
            conftest.UserUIDs.USER_FAMILY_OWNER,
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            {
                'code': 'create_family_error',
                'message': 'Вы уже состоите в семейном аккаунте',
            },
            id='user-with-family-create-error',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxi_family.family.already_exists': {
            'ru': 'Вы уже состоите в семейном аккаунте',
            'eu': 'stub',
        },
    },
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_create_family(
        web_app_client,
        mock_all_api,
        web_context,
        user_uid,
        expected_status,
        expected_response,
):
    response = await web_app_client.post(
        '/4.0/family/v1/create',
        headers={**DEFAULT_HEADER, 'X-Yandex-UID': user_uid},
    )
    assert response.status == expected_status
    if expected_response is not None:
        assert await response.json() == expected_response
