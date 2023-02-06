import datetime

import bson
import pytest


@pytest.mark.now('2019-05-01T12:00:00+0000')
async def test_v3_users_create(taxi_user_api, mongodb):
    request_body = {
        'application': 'uber',
        'application_version': '3.44.0',
        'yandex_uid': '4007274193',
        'yandex_uid_type': 'portal',
        'phone_id': '5ca344be8979d6fbe05d88c5',
        'yandex_uuid': 'cce762d726f04536bbbbd5dae1465461',
        'device_id': 'a111eab0e939cd4bbb67ef898a14396b8230663e',
        'zuser_id': 'z061be2890674631ae73e15a73989330',
        'has_ya_plus': True,
        'has_cashback_plus': True,
        'yandex_staff': True,
        'authorized': True,
        'token_only': True,
        'apns_token': 'apns_token',
        'apns_type': 'apns_type',
        'c2dm_token': 'c2dm_token',
        'gcm_token': 'gcm_token',
        'hms_token': 'hms_token',
        'mpns_url': 'mpns_url',
        'wns_url': 'wns_url',
        'metrica_device_id': 'metrica_device_id',
        'antifraud': {
            'user_id': '0061be2890674631ae73e15a73989331',
            'application': 'uber',
            'application_version': '3.44.0',
            'yandex_uid': '4007274193',
            'yandex_uuid': 'cce762d726f04536bbbbd5dae1465461',
            'device_id': 'a111eab0e939cd4bbb67ef898a14396b8230663e',
            'metrica_uuid': '45a7c6cccc9245c28697ebe3341e6824',
            'metrica_device_id': '5828af99c142a911ac1ae63790a57765',
            'instance_id': 'exKPj46OWEM',
            'ip': '172.21.133.25',
            'mac': '10:68:3f:72:73:e7',
            'user_phone': '+79261234567',
            'zone': 'zone',
            'position': {'dx': 28, 'point': [37.5898026, 55.7340368]},
            'order_id': 'order_id',
            'started_in_emulator': True,
        },
    }

    response = await taxi_user_api.post('v3/users/create', json=request_body)
    assert response.status_code == 200

    user_id = response.json()['id']
    user_doc = mongodb.users.find_one({'_id': user_id})
    assert user_doc == {
        '_id': user_id,
        'application': 'uber',
        'application_version': '3.44.0',
        'yandex_uid': '4007274193',
        'yandex_uid_type': 'portal',
        'phone_id': bson.ObjectId('5ca344be8979d6fbe05d88c5'),
        'yandex_uuid': 'cce762d726f04536bbbbd5dae1465461',
        'device_id': 'a111eab0e939cd4bbb67ef898a14396b8230663e',
        'zuser_id': 'z061be2890674631ae73e15a73989330',
        'has_ya_plus': True,
        'has_cashback_plus': True,
        'yandex_staff': True,
        'authorized': True,
        'token_only': True,
        'apns_token': 'apns_token',
        'apns_type': 'apns_type',
        'c2dm_token': 'c2dm_token',
        'gcm_token': 'gcm_token',
        'hms_token': 'hms_token',
        'mpns_url': 'mpns_url',
        'wns_url': 'wns_url',
        'metrica_device_id': 'metrica_device_id',
        'antifraud': {
            'user_id': '0061be2890674631ae73e15a73989331',
            'application': 'uber',
            'application_version': '3.44.0',
            'yandex_uid': '4007274193',
            'yandex_uuid': 'cce762d726f04536bbbbd5dae1465461',
            'device_id': 'a111eab0e939cd4bbb67ef898a14396b8230663e',
            'metrica_uuid': '45a7c6cccc9245c28697ebe3341e6824',
            'metrica_device_id': '5828af99c142a911ac1ae63790a57765',
            'instance_id': 'exKPj46OWEM',
            'ip': '172.21.133.25',
            'mac': '10:68:3f:72:73:e7',
            'user_phone': '+79261234567',
            'zone': 'zone',
            'position': {'dx': 28, 'point': [37.5898026, 55.7340368]},
            'order_id': 'order_id',
            'started_in_emulator': True,
            'updated': datetime.datetime(2019, 5, 1, 12),
        },
        'updated': datetime.datetime(2019, 5, 1, 12),
        'created': datetime.datetime(2019, 5, 1, 12),
    }


@pytest.mark.now('2019-05-01T12:00:00+0000')
async def test_v3_users_create_false_bools(taxi_user_api, mongodb):
    request_body = {
        'has_ya_plus': False,
        'has_cashback_plus': False,
        'yandex_staff': False,
        'authorized': False,
        'token_only': False,
        'antifraud': {'started_in_emulator': False},
    }

    response = await taxi_user_api.post('v3/users/create', json=request_body)
    assert response.status_code == 200

    user_id = response.json()['id']
    user_doc = mongodb.users.find_one({'_id': user_id})
    assert user_doc == {
        '_id': user_id,
        'antifraud': {
            'started_in_emulator': False,
            'updated': datetime.datetime(2019, 5, 1, 12),
        },
        'updated': datetime.datetime(2019, 5, 1, 12),
        'created': datetime.datetime(2019, 5, 1, 12),
    }
