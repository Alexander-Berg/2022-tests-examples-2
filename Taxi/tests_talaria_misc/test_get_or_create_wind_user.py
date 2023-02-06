import typing

import pytest


class MyTestCase(typing.NamedTuple):
    yandex_uid: str = 'new_yandex_uid'
    yandex_user_id: str = ''
    personal_phone_id: str = 'new_personal_phone_id'
    wind_user_id: str = 'new_wind_user_id'
    firebase_local_id: str = 'new_firebase_local_id'
    wind_token: str = 'new_wind_token'
    wind_pd_token: str = 'new_wind_pd_token'


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(), id='new_user'),
        pytest.param(
            MyTestCase(
                yandex_uid='known_yandex_uid',
                yandex_user_id='known_yandex_user_id',
                personal_phone_id='known_personal_phone_id',
                wind_user_id='known_wind_user_id',
                firebase_local_id='known_firebase_local_id',
                wind_token='known_wind_token',
                wind_pd_token='known_wind_pd_token',
            ),
            id='known_user',
        ),
        pytest.param(
            MyTestCase(
                yandex_uid='new_yandex_uid',
                yandex_user_id='known_yandex_user_id',
                personal_phone_id='known_personal_phone_id',
                wind_user_id='known_wind_user_id',
                firebase_local_id='known_firebase_local_id',
                wind_token='known_wind_token',
                wind_pd_token='known_wind_pd_token',
            ),
            id='new_yandex_uid_of_known_user',
        ),
        pytest.param(
            MyTestCase(yandex_uid='known_yandex_uid'),
            id='known_yandex_uid_of_new_user',
        ),
    ],
)
async def test_get_or_create_wind_user(
        mockserver,
        load_json,
        taxi_talaria_misc,
        case,
        wind_user_auth_mock,
        get_users_form_db,
):
    @mockserver.json_handler('/firebase-api/v1/projects/123/accounts')
    def _mock_firebase_create_user_response(request):
        response = load_json('firebase_create_new_user_response.json')
        response['localId'] = case.firebase_local_id
        return response

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        response = load_json('wind_pd_pf_v1_user_response_default.json')[0]
        response['user']['userId'] = case.wind_user_id
        response['firebaseToken'] = 'new_wind_pd_token'
        response['token'] = 'new_wind_token'
        return response

    request = {
        'is_auth_info_required': True,
        'yandex_user_info': {
            'yandex_uid': case.yandex_uid,
            'personal_phone_id': case.personal_phone_id,
        },
    }
    response = await taxi_talaria_misc.post(
        '/talaria/v1/get-or-create-wind-user', json=request,
    )
    assert response.status_code == 200

    # call POST /pf/v1/user only for new users
    if case.personal_phone_id == 'new_personal_phone_id':
        assert _mock_wind_get_user.times_called == 1
    else:
        assert _mock_wind_get_user.times_called == 0

    response_body = response.json()

    assert response_body['wind_user_info'] == {
        'wind_user_id': case.wind_user_id,
        'firebase_local_id': case.firebase_local_id,
    }

    assert response_body['wind_auth_info']['token'] == case.wind_token
    assert response_body['wind_pd_auth_info']['token'] == case.wind_pd_token

    users = get_users_form_db(f'yandex_uid=\'{case.yandex_uid}\'')
    assert len(users) == 1
    assert users[0] == dict(
        yandex_uid=case.yandex_uid,
        yandex_user_id=case.yandex_user_id,
        personal_phone_id=case.personal_phone_id,
        locale='en',
        firebase_local_id=case.firebase_local_id,
        wind_user_id=case.wind_user_id,
        wind_token=case.wind_token,
        wind_pd_token=case.wind_pd_token,
    )
