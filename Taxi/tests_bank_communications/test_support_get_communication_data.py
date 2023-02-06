from tests_bank_communications import common

BUID = 'buid1'
HANDLE_URL = '/communications-support/v1/communications/get_by_id'


async def test_get_communication_data_not_found(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'communication_id': '7948e3a9-623c-4524-a390-9e4264d27a00'},
    )
    assert response.status_code == 404


async def test_get_communication_data_communication_not_uuid(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'communication_id': 'communication_id'},
    )
    assert response.status_code == 400


async def test_get_communication_data_communication_is_empty(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'communication_id': ''},
    )
    assert response.status_code == 400


async def test_get_communication_data_ok_1(
        taxi_bank_communications, mockserver, access_control_mock,
):
    communication_id = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'communication_id': communication_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'communication_id': communication_id,
        'buid': BUID,
        'created_at': '2022-02-01T20:28:58.838783+00:00',
        'yasms': [],
        'pushes': [],
    }


async def test_get_communication_data_ok_2(
        taxi_bank_communications, mockserver, access_control_mock,
):
    communication_id = '7948e3a9-623c-4524-a390-9e4264d27a22'
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'communication_id': communication_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'communication_id': communication_id,
        'buid': BUID,
        'created_at': '2022-02-02T20:28:58.838783+00:00',
        'yasms': [
            {
                'yasms_id': '7948e3a9-623c-4524-a390-9e4264d27b11',
                'created_at': '2022-02-02T20:28:58.838783+00:00',
                'message_sent_id': 'message_id',
                'phone_number': '+79990001122',
                'status': 'SENT',
            },
        ],
        'pushes': [
            {
                'notification_id': '7948e3a9-623c-4524-a390-9e4264d27b11',
                'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
                'created_at': '2022-02-02T20:28:58.838783+00:00',
                'message_text': 'text',
                'status': 'SENT',
                'updated_at': '2022-02-02T20:28:58.838783+00:00',
            },
        ],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_communication_data_suggest_access_deny(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'communication_id': '7948e3a9-623c-4524-a390-9e4264d27a00'},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
