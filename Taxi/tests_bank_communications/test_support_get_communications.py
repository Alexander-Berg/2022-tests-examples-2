from tests_bank_communications import common

BUID = 'buid1'
HANDLE_URL = '/communications-support/v1/communications/get_list'


async def test_get_communications(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['communications']) == 3


async def test_get_communications_with_limit(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['communications']) == 1
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjozfQ=='


async def test_get_communications_with_cursor(
        taxi_bank_communications, mockserver, access_control_mock,
):
    request_cursor = 'eyJjdXJzb3Jfa2V5IjozfQ=='
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1, 'cursor': request_cursor},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['communications']) == 1
    response_cursor = 'eyJjdXJzb3Jfa2V5IjoyfQ=='
    assert resp['cursor'] == response_cursor


async def test_get_communications_without_user_id(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {}, 'limit': 100},
    )
    assert response.status_code == 400


async def test_get_communications_with_created_at(
        taxi_bank_communications, mockserver, access_control_mock,
):
    start_time = '2022-02-03T00:00:00.0+00:00'
    end_time = '2022-02-04T00:00:00.0+00:00'
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'created_date_from': start_time,
                'created_date_to': end_time,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['communications'] == [
        {
            'communication_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'buid': BUID,
            'created_at': '2022-02-03T20:28:58.838783+00:00',
        },
    ]
    assert 'cursor' not in resp
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_communications_access_deny(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_get_communications_filter_id(
        taxi_bank_communications, mockserver, access_control_mock,
):
    communication_id = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_communications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'filters': {'communication_id': communication_id}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['communications']) == 1
    assert resp['communications'][0]['communication_id'] == communication_id
