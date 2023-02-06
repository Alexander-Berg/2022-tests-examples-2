import json

import pytest

from tests_dispatcher_access_control import utils

ACTIVATE_ENDPOINT = 'v1/parks/users/confirm'

PARK_ID = 'park_valid1'
UID = 'uid_valid'

HEADERS = {
    'X-Idempotency-Token': 'extra_super_token',
    'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
}

PERSONAL = {'123': '+71231231212', '456': '+74564564545'}


@pytest.fixture(name='personal_phones_store')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock(request):
        assert request.json['id'] in PERSONAL
        return {
            'value': PERSONAL[request.json['id']],
            'id': request.json['id'],
        }

    return _mock


def build_request(
        user_id='user_id',
        phone_pd_id='123',
        group_id='group_valid1',
        name='User',
        passport_uid=UID,
        created_at='2019-01-01T01:00:00+00:00',
        is_multifactor_authentication_required=False,
        is_enabled=False,
):
    request = {
        'user_id': user_id,
        'phone_pd_id': phone_pd_id,
        'group_id': group_id,
        'name': name,
        'passport_uid': passport_uid,
        'created_at': created_at,
        'is_multifactor_authentication_required': (
            is_multifactor_authentication_required
        ),
        'is_enabled': is_enabled,
    }
    return request


def build_get_users_request(passport_uid='100'):
    return {
        'query': {
            'park': {'id': 'park_valid1'},
            'user': {'passport_uid': [passport_uid]},
        },
    }


def build_get_users_response(request):
    user = {
        'created_at': request.get('created_at', ''),
        'display_name': request.get('name', ''),
        'group_id': request.get('group_id', ''),
        'group_name': 'Administrators',
        'id': request.get('user_id', ''),
        'is_confirmed': False,
        'is_enabled': request.get('is_enabled', True),
        'is_multifactor_authentication_required': request.get(
            'is_multifactor_authentication_required', '',
        ),
        'is_superuser': False,
        'is_usage_consent_accepted': False,
        'park_id': PARK_ID,
        'passport_uid': request.get('passport_uid', ''),
        'yandex_uid': request.get('passport_uid', ''),
        'phone': PERSONAL[request['phone_pd_id']],
    }
    return {'offset': 0, 'users': [user]}


def get_park_bindings(park_id=b'park_valid1', user_id='user_valid1'):
    return {park_id: str.encode(user_id)}


@pytest.mark.redis_store(
    [
        'hmset',
        f'UserGroup:Items:{PARK_ID}',
        {'group_valid1': json.dumps({'Name': 'Administrators'})},
    ],
)
async def test_create_user_success(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        personal_phones_store,
):
    request = build_request()
    response = await taxi_dispatcher_access_control.post(
        ACTIVATE_ENDPOINT,
        headers=HEADERS,
        params={'park_id': PARK_ID},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'park_id': PARK_ID,
        'user_id': request['user_id'],
    }

    assert redis_store.hgetall(f'User:Items:{PARK_ID}') == {
        b'user_id': (
            b'{'
            b'"Group":"group_valid1",'
            b'"Enable":false,'
            b'"YandexUid":"uid_valid",'
            b'"IsSuperUser":false,'
            b'"IsYandex":true,'
            b'"Name":"User",'
            b'"Phones":"+71231231212",'
            b'"CreatedAt":"2019-01-01T01:00:00+00:00",'
            b'"IsMultiFactorAuthenticationRequired":false}'
        ),
    }


@pytest.mark.redis_store(
    [
        'hmset',
        f'UserGroup:Items:{PARK_ID}',
        {'group_valid1': json.dumps({'Name': 'Administrators'})},
    ],
    [
        'hmset',
        f'User:Items:{PARK_ID}',
        {
            'user_id': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexUid': UID,
                },
            ),
        },
    ],
)
async def test_user_already_created(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        personal_phones_store,
):
    request = build_request()
    response = await taxi_dispatcher_access_control.post(
        ACTIVATE_ENDPOINT,
        headers=HEADERS,
        params={'park_id': PARK_ID},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'park_id': PARK_ID,
        'user_id': request['user_id'],
    }

    assert redis_store.hgetall(f'User:Items:{PARK_ID}') == {
        b'user_id': (
            b'{"Enable": true, '
            b'"Group": "group_valid1", '
            b'"Name": "User", '
            b'"YandexConfirmed": true, '
            b'"IsSuperUser": false, '
            b'"YandexUid": "uid_valid"}'
        ),
    }


@pytest.mark.redis_store(
    [
        'hmset',
        f'UserGroup:Items:{PARK_ID}',
        {'group_valid1': json.dumps({'Name': 'Administrators'})},
    ],
    [
        'hmset',
        f'User:Items:{PARK_ID}',
        {
            'user_id1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexUid': UID,
                },
            ),
        },
    ],
)
async def test_user_with_uid_exists(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        personal_phones_store,
):
    request = build_request()
    response = await taxi_dispatcher_access_control.post(
        ACTIVATE_ENDPOINT,
        headers=HEADERS,
        params={'park_id': PARK_ID},
        json=request,
    )

    assert response.status_code == 400

    assert redis_store.hgetall(f'User:Items:{PARK_ID}') == {
        b'user_id1': (
            b'{"Enable": true, '
            b'"Group": "group_valid1", '
            b'"Name": "User", '
            b'"YandexConfirmed": true, '
            b'"IsSuperUser": false, '
            b'"YandexUid": "uid_valid"}'
        ),
    }
