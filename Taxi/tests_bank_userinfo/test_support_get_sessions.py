import pytest

from tests_bank_userinfo import common

UID = 'uid'
BUID = 'e3ba1e49-9ed6-4e4b-919a-dc8d530e4580'
PHONE_ID = 'phone_id'
HANDLE_URL = '/userinfo-support/v1/get_sessions'


async def test_get_sessions(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {UID: UID, 'buid': BUID, 'phone_id': PHONE_ID},
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['sessions']) == 2


async def test_get_sessions_with_limit(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'uid': UID}, 'limit': 2},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['sessions']) == 2
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5Ijo3fQ=='


async def test_get_sessions_with_cursor(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    request_cursor = 'eyJjdXJzb3Jfa2V5Ijo3fQ=='
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'uid': UID}, 'cursor': request_cursor, 'limit': 1},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['sessions']) == 1
    response_cursor = 'eyJjdXJzb3Jfa2V5Ijo2fQ=='
    assert resp['cursor'] == response_cursor


async def test_get_sessions_without_user_id(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {}, 'limit': 100},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'session_status, count',
    [('ok', 1), ('invalid_token', 0), ('not_authorized', 1)],
)
async def test_get_sessions_with_status(
        taxi_bank_userinfo,
        mockserver,
        access_control_mock,
        session_status,
        count,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': UID,
                'buid': BUID,
                'phone_id': PHONE_ID,
                'status': session_status,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['sessions']) == count
    assert 'cursor' not in resp


async def test_get_sessions_with_created_at(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': UID,
                'buid': BUID,
                'phone_id': PHONE_ID,
                'created_date_from': '2022-02-06T00:00:00.0+00:00',
                'created_date_to': '2022-02-08T00:00:00.0+00:00',
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['sessions'] == [
        {
            'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd07',
            'uid': UID,
            'buid': BUID,
            'phone_id': PHONE_ID,
            'status': 'not_authorized',
            'created_at': '2022-02-07T20:28:58.838783+00:00',
            'updated_at': '2022-02-08T20:28:58.838783+00:00',
        },
        {
            'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd06',
            'uid': UID,
            'buid': BUID,
            'phone_id': PHONE_ID,
            'status': 'ok',
            'created_at': '2022-02-06T20:28:58.838783+00:00',
            'updated_at': '2022-02-06T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_sessions_with_updated_at(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': UID,
                'buid': BUID,
                'phone_id': PHONE_ID,
                'updated_date_from': '2022-02-06T00:00:00.0+00:00',
                'updated_date_to': '2022-02-08T00:00:00.0+00:00',
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['sessions'] == [
        {
            'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd06',
            'uid': UID,
            'buid': BUID,
            'phone_id': PHONE_ID,
            'status': 'ok',
            'created_at': '2022-02-06T20:28:58.838783+00:00',
            'updated_at': '2022-02-06T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_sessions_with_all_time(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': UID,
                'buid': BUID,
                'phone_id': PHONE_ID,
                'created_date_from': '2022-02-06T00:00:00.0+00:00',
                'created_date_to': '2022-02-08T00:00:00.0+00:00',
                'updated_date_from': '2022-02-05T00:00:00.0+00:00',
                'updated_date_to': '2022-02-07T00:00:00.0+00:00',
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['sessions'] == [
        {
            'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd06',
            'uid': UID,
            'buid': BUID,
            'phone_id': PHONE_ID,
            'status': 'ok',
            'created_at': '2022-02-06T20:28:58.838783+00:00',
            'updated_at': '2022-02-06T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp


async def test_get_sessions_with_all_time_and_status(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'status': 'invalid_token',
                'created_date_from': '2022-02-02T00:00:00.0+00:00',
                'created_date_to': '2022-02-03T00:00:00.0+00:00',
                'updated_date_from': '2022-02-02T00:00:00.0+00:00',
                'updated_date_to': '2022-02-03T00:00:00.0+00:00',
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['sessions'] == [
        {
            'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bd02',
            'buid': BUID,
            'status': 'invalid_token',
            'created_at': '2022-02-02T20:28:58.838783+00:00',
            'updated_at': '2022-02-02T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_sessions_access_deny(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={
            'filters': {UID: UID, 'buid': BUID, 'phone_id': PHONE_ID},
            'limit': 100,
        },
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_get_sessions_filter_by_id(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15bd07'
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {'session_uuid': session_uuid, 'phone_id': PHONE_ID},
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['sessions']) == 1
    assert resp['sessions'][0]['session_uuid'] == session_uuid
