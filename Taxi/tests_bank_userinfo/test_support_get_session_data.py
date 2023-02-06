from tests_bank_userinfo import common

HANDLE_URL = '/userinfo-support/v1/get_session_data'


async def test_get_session_data_empty_id(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'session_uuid': ''},
    )
    assert response.status_code == 400


async def test_get_session_data_not_found(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd00'},
    )
    assert response.status_code == 404


async def test_get_session_data_ok_partial_data(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15bd01'
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'session_uuid': session_uuid},
    )
    assert response.status_code == 200
    assert response.json() == {
        'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd01',
        'status': 'invalid_token',
        'created_at': '2022-02-01T20:28:58.838783+00:00',
        'updated_at': '2022-02-02T18:28:58.838783+00:00',
        'antifraud_info': {},
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_session_data_ok_full_data(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15bd02'
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'session_uuid': session_uuid},
    )
    assert response.status_code == 200
    assert response.json() == {
        'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd02',
        'uid': 'uid',
        'buid': 'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580',
        'phone_id': 'phone_id',
        'status': 'ok',
        'old_session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd01',
        'created_at': '2022-02-02T20:28:58.838783+00:00',
        'updated_at': '2022-02-03T18:28:58.838783+00:00',
        'antifraud_info': {'device_id': 'device_id', 'qwe': 'asd'},
        'authorization_track_id': 'authorization_track_id',
        'app_vars': 'X-Platform=fcm, app_name=sdk_example',
        'locale': 'ru',
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_session_data_access_deny(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'session_uuid': 'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580'},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
