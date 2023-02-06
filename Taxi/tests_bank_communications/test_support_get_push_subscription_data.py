from tests_bank_communications import common

URL = '/communications-support/v1/push_subscriptions/get_by_id'


async def test_get_subscription_data_ok(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a01'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a01',
        'buid': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'device_id': 'deviceid1',
        'uuid': 'uuid1',
        'locale': 'ru',
        'status': 'ACTIVE',
        'created_at': '2022-02-01T20:28:58.838783+00:00',
        'updated_at': '2022-02-02T20:28:58.838783+00:00',
    }


async def test_get_subscription_data_with_masked_buid(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a02'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a02',
        'buid': '7948e3a9-623c-4524-a390-9e4264d27a12',
        'device_id': 'deviceid2',
        'uuid': 'uuid2',
        'locale': 'ru',
        'masked_buid': '11111111-1111-1111-1111-111111111111',
        'status': 'ACTIVE',
        'created_at': '2022-02-01T20:28:58.838783+00:00',
        'updated_at': '2022-02-02T20:28:58.838783+00:00',
    }


async def test_get_subscription_data_not_found(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a00'},
    )
    assert response.status_code == 404


async def test_get_subscription_data_not_uuid(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'subscription_id': 'subscription_id'},
    )
    assert response.status_code == 400


async def test_access_deny(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(''),
        json={'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a01'},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert access_control_mock.handler_path == URL
