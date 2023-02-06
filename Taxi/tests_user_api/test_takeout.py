import bson
import pytest

DELETE_ENDPOINT = '/v1/takeout/delete'
STATUS_ENDPOINT = '/v1/takeout/status'


def check_phone_type_change(phone_type, request_id):
    base_type = 'deleted:yandex:' + request_id + ':'
    assert phone_type.startswith(base_type)
    assert len(phone_type) == len(base_type) + 32


def check_user_not_authorized(mongodb, phone_id_oid):
    cursor = mongodb.users.find({'phone_id': phone_id_oid})
    for doc in cursor:
        assert 'authorized' not in doc


async def test_non_existing_uid(taxi_user_api):
    uid = 'unknown_uid'
    request_data = {
        'request_id': '12345',
        'yandex_uids': [{'uid': uid, 'is_portal': True}],
    }

    response = await taxi_user_api.post(DELETE_ENDPOINT, json=request_data)
    assert response.status_code == 200


async def test_bad_phone_id(taxi_user_api):
    request_data = {
        'request_id': '12345',
        'yandex_uids': [{'uid': '4004000001', 'is_portal': True}],
        'phone_ids': ['bad_phone_id'],
    }

    response = await taxi_user_api.post(DELETE_ENDPOINT, json=request_data)
    assert response.status_code == 500


async def test_takeout_delete(taxi_user_api, mongodb, testpoint):
    @testpoint('deleted-user-phones-count')
    def _check_deleted_user_phones_count(count):
        assert count == 2

    @testpoint('updated-users-count')
    def _check_updated_users_count(count):
        assert count == 3

    uids = ['4004000001', '4004000002']

    request_id = '12345'
    request_data = {'request_id': request_id}
    request_data['yandex_uids'] = [
        {'uid': uid, 'is_portal': True} for uid in uids
    ]

    # One emails db item has no yandex uid, but it has phone id,
    # so first phone id is for this item.
    # Another phone ids are for deletion by phone.
    phone_ids = [
        '666777e7ed2c89a5e0300003',
        '539e99e1e7e5b1f5397ad000',
        '539e99e1e7e5b1f5397ad001',
    ]
    request_data['phone_ids'] = phone_ids
    user_ids = [
        '000000000000000000000011',
        '000000000000000000000012',
        '000000000000000000000013',
        '000000000000000000000014',
    ]
    request_data['user_ids'] = user_ids

    response = await taxi_user_api.post(DELETE_ENDPOINT, json=request_data)
    assert response.status_code == 200

    # check that emails were deleted successfully
    mongo_query = {'yandex_uid': {'$in': uids}}
    assert mongodb.user_emails.find_one(mongo_query) is None

    phone_id_bsons = [bson.ObjectId(phone_id) for phone_id in phone_ids]

    mongo_query = {'phone_id': phone_id_bsons[0]}
    assert mongodb.user_emails.find_one(mongo_query) is None

    # Check that user phones were removed successfully.
    # Check that item with yandex phone type has been changed
    mongo_query = {'_id': phone_id_bsons[1]}
    doc = mongodb.user_phones.find_one(mongo_query)
    check_phone_type_change(doc['type'], request_id)
    check_user_not_authorized(mongodb, phone_id_bsons[1])

    # Check that item without phone type has been changed
    mongo_query = {'_id': phone_id_bsons[2]}
    doc = mongodb.user_phones.find_one(mongo_query)
    check_phone_type_change(doc['type'], request_id)
    check_user_not_authorized(mongodb, phone_id_bsons[2])


@pytest.mark.parametrize(
    'request_data',
    [
        pytest.param(
            {
                'request_id': '12345',
                'yandex_uids': [
                    {'uid': '4004000001', 'is_portal': True},
                    {'uid': '4004000002', 'is_portal': False},
                ],
            },
            id='find_user_emails_by_yandex_uids',
        ),
        pytest.param(
            {
                'request_id': '12345',
                'yandex_uids': [{'uid': '4004000001', 'is_portal': True}],
                'phone_ids': ['666777e7ed2c89a5e0300003'],
            },
            id='find_user_email_by_phone_id',
        ),
        pytest.param(
            {
                'request_id': '12345',
                'yandex_uids': [{'uid': '4004000001', 'is_portal': True}],
                'phone_ids': [
                    '539e99e1e7e5b1f5397ad000',
                    '539e99e1e7e5b1f5397ad001',
                ],
            },
            id='find_user_phones_by_phone_ids',
        ),
        pytest.param(
            {
                'request_id': '12345',
                'yandex_uids': [{'uid': '4004000001', 'is_portal': True}],
                'user_ids': [
                    '000000000000000000000011',
                    '000000000000000000000012',
                    '000000000000000000000013',
                    '000000000000000000000014',
                ],
            },
            id='find_authorized_users_by_user_ids',
        ),
    ],
)
async def test_takeout_status_ready_to_delete(taxi_user_api, request_data):
    response = await taxi_user_api.post(STATUS_ENDPOINT, json=request_data)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['data_state'] == 'ready_to_delete'


async def test_takeout_status_empty(taxi_user_api):
    uids = ['4004000001', '4004000002']

    request_id = '12345'
    request_data = {'request_id': request_id}
    request_data['yandex_uids'] = [
        {'uid': uid, 'is_portal': True} for uid in uids
    ]

    phone_ids = [
        '666777e7ed2c89a5e0300003',
        '539e99e1e7e5b1f5397ad000',
        '539e99e1e7e5b1f5397ad001',
    ]
    request_data['phone_ids'] = phone_ids
    user_ids = [
        '000000000000000000000011',
        '000000000000000000000012',
        '000000000000000000000013',
        '000000000000000000000014',
    ]
    request_data['user_ids'] = user_ids

    response = await taxi_user_api.post(DELETE_ENDPOINT, json=request_data)
    assert response.status_code == 200

    response = await taxi_user_api.post(STATUS_ENDPOINT, json=request_data)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['data_state'] == 'empty'
