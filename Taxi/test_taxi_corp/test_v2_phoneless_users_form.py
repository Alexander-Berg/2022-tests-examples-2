import datetime

import pytest

from test_taxi_corp import corp_users_util

USER_PHONES_CONFIG = dict(
    CORP_USER_PHONES_SUPPORTED=corp_users_util.CORP_USER_PHONES_SUPPORTED,
)
NOW = datetime.datetime(2022, 4, 23, 11, 00, 00)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['params', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {'link_id': 'active_link_id'},
            200,
            {
                'client_name': 'client3_name',
                'user_fullname': 'phoneless user draft',
            },
            id='active link_id',
        ),
        pytest.param(
            {'link_id': 'not_existed_link_id'},
            404,
            {'text': 'Link not found', 'code': 'GENERAL'},
            id='not existed link_id',
        ),
        pytest.param(
            {'link_id': 'used_link_id'},
            410,
            {
                'text': 'error.phoneless_users.link_already_used',
                'code': 'LINK_ALREADY_USED',
            },
            id='expired link_id',
        ),
        pytest.param(
            {'link_id': 'expired_link_id'},
            410,
            {
                'text': 'error.phoneless_users.link_expired',
                'code': 'LINK_EXPIRED',
            },
            id='already used link',
        ),
        pytest.param(
            {},
            400,
            {'text': 'link_id field is required.', 'code': 'GENERAL'},
            id='missing link_id in query',
        ),
    ],
)
async def test_get_phoneless_users_form_info(
        taxi_corp_auth_client, params, expected_code, expected_response,
):
    response = await taxi_corp_auth_client.get(
        '/2.0/phoneless-users/form/info', params=params,
    )

    assert response.status == expected_code
    response_data = await response.json()

    if expected_code == 200:
        assert response_data == expected_response
    else:
        assert response_data['errors'][0] == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['link_id', 'user_id', 'post_content', 'expected_code', 'error_response'],
    [
        pytest.param(
            'active_link_id',
            'phoneless_user1',
            {'phone': '+79997778877', 'email': 'example@yandex.ru'},
            200,
            None,
            id='insert phone',
        ),
        pytest.param(
            'active_link_id_2',
            'phoneless_user2',
            {'phone': '+79997778877'},
            200,
            None,
            id='update phone',
        ),
        pytest.param(
            'active_link_id',
            'phoneless_user1',
            {'phone': '+39997778877'},
            400,
            {
                'text': 'phone number should starts with: [\'+79\']',
                'code': 'GENERAL',
            },
            id='invalid phone',
        ),
        pytest.param(
            'active_link_id_2',
            'phoneless_user2',
            {'phone': '+79646667777'},
            406,
            {
                'text': 'error.duplicate_user_phone_error_code',
                'code': 'DUPLICATE_USER_PHONE',
            },
            id='invalid phone',
        ),
    ],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_phoneless_users_set_phone(
        taxi_corp_auth_client,
        pd_patch,
        db,
        link_id,
        user_id,
        post_content,
        expected_code,
        error_response,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_auth_client.post(
        '/2.0/phoneless-users/form/set-phone',
        params={'link_id': link_id},
        json=post_content,
    )

    assert response.status == expected_code
    response_data = await response.json()

    if expected_code == 200:
        db_user = await db.corp_users.find_one(
            {'_id': user_id}, projection=['is_draft', 'phone', 'email'],
        )
        assert not db_user['is_draft']

        for key, value in db_user.items():
            if key in post_content:
                assert value == post_content[key]

        link = await db.corp_phoneless_user_links.find_one(
            {'_id': link_id}, projection=['is_used'],
        )
        assert link['is_used']
    else:
        assert response_data['errors'][0] == error_response
