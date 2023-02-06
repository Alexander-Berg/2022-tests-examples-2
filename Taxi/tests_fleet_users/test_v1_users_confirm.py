import pytest

from tests_fleet_users import base_mocks
from tests_fleet_users import utils

ENDPOINT = 'v1/users/confirm'

PARK_ID = '111'
USER_ID = 'user_id1'
UID = 'passport_uid'
PHONE = '+71231231212'
NAME = 'passport_name'


def build_headers(park_id=PARK_ID):
    return {'X-Park-ID': park_id}


def build_request(passport_uid=UID, phone=PHONE, passport_name=NAME):
    return {
        'passport_uid': passport_uid,
        'phone': phone,
        'passport_name': passport_name,
    }


@pytest.fixture(name='dac_parks_users_confirm')
def _mock_dac_parks_group_list(mockserver):
    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/confirm',
    )
    def _mock(request):
        return {'park_id': PARK_ID, 'user_id': USER_ID}

    return _mock


async def test_success(
        taxi_fleet_users,
        dac_parks_users_confirm,
        personal_phones_store,
        pgsql,
):
    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 200

    user = utils.get_user_by_passport_uid(pgsql, PARK_ID, UID)
    assert user['is_confirmed']
    assert user['confirmed_at']


async def test_success_already_confirmed(
        taxi_fleet_users,
        dac_parks_users_confirm,
        personal_phones_store,
        pgsql,
):
    request_body = build_request('passport_uid3', '+71231231212', 'Jane Doe')
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(park_id='333'), json=request_body,
    )

    assert response.status == 200

    user = utils.get_user_by_passport_uid(pgsql, '333', 'passport_uid3')
    assert user['is_confirmed']
    assert user['confirmed_at']


async def test_user_not_found(taxi_fleet_users, pgsql, personal_phones_store):
    phone = '+74564564545'
    request_body = build_request(phone=phone)
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 400

    utils.get_user_by_phone_id(
        pgsql, PARK_ID, base_mocks.PERSONAL_STORE[phone], False,
    )


async def test_user_is_not_enable(
        taxi_fleet_users, pgsql, personal_phones_store,
):
    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(park_id='444'), json=request_body,
    )

    assert response.status == 400

    user = utils.get_user_by_phone_id(
        pgsql, PARK_ID, base_mocks.PERSONAL_STORE[PHONE],
    )
    assert not user['is_confirmed']
    assert not user['confirmed_at']


async def test_user_with_uid_exists(
        taxi_fleet_users, personal_phones_store, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/confirm',
    )
    def _mock(request):
        return mockserver.make_response(
            status=400,
            json={'code': 'user_with_uid_exists', 'message': 'error'},
        )

    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 400

    user = utils.get_user_by_phone_id(
        pgsql, PARK_ID, base_mocks.PERSONAL_STORE[PHONE],
    )
    assert not user['is_confirmed']
    assert not user['confirmed_at']
