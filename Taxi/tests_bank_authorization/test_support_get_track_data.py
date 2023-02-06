from tests_bank_authorization import common

BUID = 'buid1'
HANDLE_URL = '/authorization-support/v1/get_track_data'


async def test_get_track_data_not_found(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a00',
            'buid': BUID,
        },
    )
    assert response.status_code == 404


async def test_get_track_data_track_not_uuid(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'track_id': 'track_id', 'buid': BUID},
    )
    assert response.status_code == 400


async def test_get_track_data_track_is_empty(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'track_id': '', 'buid': BUID},
    )
    assert response.status_code == 400


async def test_get_track_data_ok_1(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    track_id = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'track_id': track_id, 'buid': BUID},
    )
    assert response.status_code == 200
    assert response.json() == {
        'track_id': track_id,
        'buid': 'buid1',
        'operation_type': 'start_session',
        'created_at': '2022-02-01T20:28:58.838783+00:00',
        'updated_at': '2022-02-01T20:28:58.838783+00:00',
        'codes': [],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_track_data_ok_2(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    track_create_time = '2022-02-02T20:28:58.838783+00:00'
    first_code_create_time = '2022-02-02T20:28:58.838783+00:00'
    second_code_create_time = '2022-02-03T20:28:58.838783+00:00'
    attempt_create_time = '2022-02-03T20:30:58.838783+00:00'
    track_id = '7948e3a9-623c-4524-a390-9e4264d27a22'
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'track_id': track_id, 'buid': BUID},
    )
    assert response.status_code == 200
    assert response.json() == {
        'track_id': track_id,
        'buid': 'buid1',
        'operation_type': 'new_card',
        'created_at': track_create_time,
        'updated_at': track_create_time,
        'codes': [
            {
                'code_id': '7948e3a9-623c-4524-a390-9e4264d27b88',
                'attempts_left': 2,
                'created_at': second_code_create_time,
                'updated_at': attempt_create_time,
                'attempts': [
                    {
                        'attempt_id': '97081435-272c-42d1-8950-fd74df92e651',
                        'created_at': attempt_create_time,
                        'updated_at': attempt_create_time,
                    },
                ],
            },
            {
                'code_id': '7948e3a9-623c-4524-a390-9e4264d27b77',
                'attempts_left': 3,
                'created_at': first_code_create_time,
                'updated_at': first_code_create_time,
                'attempts': [],
            },
        ],
    }


async def test_get_track_data_access_deny(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a00',
            'buid': BUID,
        },
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
