from tests_bank_communications import common

BUID = '7948e3a9-623c-4524-a390-9e4264d27a11'
URL = '/communications-support/v1/push_subscriptions/get_list'


async def test_get_push_subscriptions(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['subscriptions']) == 3


async def test_get_push_subscriptions_with_limit(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['subscriptions']) == 1
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjozfQ=='


async def test_get_push_subscriptions_with_cursor(
        taxi_bank_communications, mockserver, access_control_mock,
):
    request_cursor = 'eyJjdXJzb3Jfa2V5IjozfQ=='
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID}, 'limit': 1, 'cursor': request_cursor},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['subscriptions']) == 1
    response_cursor = 'eyJjdXJzb3Jfa2V5IjoyfQ=='
    assert resp['cursor'] == response_cursor


async def test_get_push_subscriptions_without_user_id(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {}, 'limit': 100},
    )
    assert response.status_code == 400


async def test_get_push_subscriptions_with_created_at(
        taxi_bank_communications, mockserver, access_control_mock,
):
    start_time = '2022-02-03T00:00:00.0+00:00'
    end_time = '2022-02-04T00:00:00.0+00:00'
    response = await taxi_bank_communications.post(
        URL,
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
    assert resp['subscriptions'] == [
        {
            'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a03',
            'buid': BUID,
            'created_at': '2022-02-03T20:28:58.838783+00:00',
            'updated_at': '2022-02-03T20:28:58.838783+00:00',
            'status': 'ACTIVE',
        },
    ]
    assert 'cursor' not in resp


async def test_get_push_subscriptions_with_time_filters_1(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': BUID,
                'created_date_from': '2022-02-02T00:00:00.0+00:00',
                'created_date_to': '2022-02-03T00:00:00.0+00:00',
                'updated_date_from': '2022-02-04T00:00:00.0+00:00',
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['subscriptions'] == [
        {
            'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a02',
            'buid': BUID,
            'created_at': '2022-02-02T20:28:58.838783+00:00',
            'updated_at': '2022-02-04T20:28:58.838783+00:00',
            'status': 'INACTIVE',
        },
    ]
    assert 'cursor' not in resp


async def test_get_inactive_push_subscriptions(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {'buid': BUID, 'status': 'INACTIVE'}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['subscriptions'] == [
        {
            'subscription_id': '7948e3a9-623c-4524-a390-9e4264d27a02',
            'buid': BUID,
            'created_at': '2022-02-02T20:28:58.838783+00:00',
            'updated_at': '2022-02-04T20:28:58.838783+00:00',
            'status': 'INACTIVE',
        },
    ]
    assert 'cursor' not in resp


async def test_access_deny(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(''),
        json={'filters': {'buid': BUID}, 'limit': 100},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert access_control_mock.handler_path == URL


async def test_get_push_subscriptions_id_filter(
        taxi_bank_communications, mockserver, access_control_mock,
):
    subscription_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    response = await taxi_bank_communications.post(
        URL,
        headers=common.get_support_headers(),
        json={'filters': {'subscription_id': subscription_id}, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['subscriptions']) == 1
    assert resp['subscriptions'][0]['subscription_id'] == subscription_id
