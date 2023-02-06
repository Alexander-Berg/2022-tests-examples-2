import datetime

import bson
import pytest


async def test_v3_users_update_not_found(taxi_user_api, mongodb):
    request_body = {'id': '0061be2890674631ae73e15a73989777'}

    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 404

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989777'},
    )
    assert not user_doc


@pytest.mark.now('2019-05-01T13:00:00+0000')
async def test_v3_users_update(taxi_user_api, mongodb):
    request_body = {
        'id': '0061be2890674631ae73e15a73989330',
        'application': 'uber_ng',
        'application_version': '7.77.0',
        'yandex_uid': '4007274777',
        'yandex_uid_type': 'portal_ng',
        'phone_id': '5ca344be8979d6fbe05d8777',
        'yandex_uuid': 'cce762d726f04536bbbbd5dae1465777',
        'device_id': 'a111eab0e939cd4bbb67ef898a14396b82306777',
        'apns_token': 'apns_token_ng',
        'apns_type': 'apns_type_ng',
        'c2dm_token': 'c2dm_token_ng',
        'gcm_token': 'gcm_token_ng',
        'hms_token': 'hms_token_ng',
        'mpns_url': 'mpns_url_ng',
        'wns_url': 'wns_url_ng',
        'metrica_device_id': 'metrica_device_id',
        'antifraud': {
            'user_id': '0061be2890674631ae73e15a73989777',
            'application': 'uber_ng',
            'application_version': '7.77.0',
            'yandex_uid': '4007274777',
            'yandex_uuid': 'cce762d726f04536bbbbd5dae1465777',
            'device_id': 'a111eab0e939cd4bbb67ef898a14396b82306777',
            'metrica_uuid': '45a7c6cccc9245c28697ebe3341e6777',
            'metrica_device_id': '5828af99c142a911ac1ae63790a57777',
            'instance_id': 'exKPj46O777',
            'ip': '172.21.133.11',
            'mac': '10:68:3f:72:77:77',
            'user_phone': '+79261234777',
            'zone': 'zone_ng',
            'position': {'dx': 77, 'point': [77.5898026, 77.7340368]},
            'order_id': 'order_id_ng',
            'started_in_emulator': True,
        },
    }

    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 200

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989330'},
    )
    assert _remove_updated(user_doc) == {
        '_id': '0061be2890674631ae73e15a73989330',
        'application': 'uber_ng',
        'application_version': '7.77.0',
        'yandex_uid': '4007274777',
        'yandex_uid_type': 'portal_ng',
        'phone_id': bson.ObjectId('5ca344be8979d6fbe05d8777'),
        'yandex_uuid': 'cce762d726f04536bbbbd5dae1465777',
        'device_id': 'a111eab0e939cd4bbb67ef898a14396b82306777',
        'zuser_id': 'z061be2890674631ae73e15a73989330',
        'has_ya_plus': True,
        'has_cashback_plus': True,
        'yandex_staff': True,
        'authorized': True,
        'token_only': True,
        'apns_token': 'apns_token_ng',
        'apns_type': 'apns_type_ng',
        'c2dm_token': 'c2dm_token_ng',
        'gcm_token': 'gcm_token_ng',
        'hms_token': 'hms_token_ng',
        'mpns_url': 'mpns_url_ng',
        'wns_url': 'wns_url_ng',
        'metrica_device_id': 'metrica_device_id',
        'antifraud': {
            'user_id': '0061be2890674631ae73e15a73989777',
            'application': 'uber_ng',
            'application_version': '7.77.0',
            'yandex_uid': '4007274777',
            'yandex_uuid': 'cce762d726f04536bbbbd5dae1465777',
            'device_id': 'a111eab0e939cd4bbb67ef898a14396b82306777',
            'metrica_uuid': '45a7c6cccc9245c28697ebe3341e6777',
            'metrica_device_id': '5828af99c142a911ac1ae63790a57777',
            'instance_id': 'exKPj46O777',
            'ip': '172.21.133.11',
            'mac': '10:68:3f:72:77:77',
            'user_phone': '+79261234777',
            'zone': 'zone_ng',
            'position': {'dx': 77, 'point': [77.5898026, 77.7340368]},
            'order_id': 'order_id_ng',
            'started_in_emulator': True,
            'updated': datetime.datetime(2019, 5, 1, 13),
        },
        'created': datetime.datetime(2019, 5, 1, 12),
    }


@pytest.mark.now('2019-05-01T13:00:00+0000')
async def test_v3_users_update_false_bools(taxi_user_api, mongodb):
    request_body = {
        'id': '0061be2890674631ae73e15a73989330',
        'has_ya_plus': False,
        'has_cashback_plus': False,
        'yandex_staff': False,
        'authorized': False,
        'token_only': False,
        'antifraud': {'started_in_emulator': False},
    }

    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 200

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989330'},
    )
    assert 'has_ya_plus' not in user_doc
    assert 'has_cashback_plus' not in user_doc
    assert 'yandex_staff' not in user_doc
    assert 'authorized' not in user_doc
    assert 'token_only' not in user_doc
    assert not user_doc['antifraud']['started_in_emulator']


@pytest.mark.now('2019-05-01T13:00:00+0000')
async def test_v3_users_update_drop_yandex_uid(taxi_user_api, mongodb):
    request_body = {'id': '0061be2890674631ae73e15a73989330'}

    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 200

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989330'},
    )
    assert 'yandex_uid' not in user_doc
    assert 'yandex_uid_type' not in user_doc


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'id': '0061be2890674631ae73e15a73989330',
            'application': 'uber',
            'application_version': '3.44.0',
            'yandex_uid': '4007274193',
            'yandex_uid_type': 'portal',
            'phone_id': '5ca344be8979d6fbe05d88c5',
            'yandex_uuid': 'cce762d726f04536bbbbd5dae1465461',
            'device_id': 'a111eab0e939cd4bbb67ef898a14396b8230663e',
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
        },
        {
            'id': '0061be2890674631ae73e15a73989330',
            'yandex_uid': '4007274193',
            'yandex_uid_type': 'portal',
        },
    ],
)
@pytest.mark.now('2019-05-01T13:00:00+0000')
async def test_v3_users_update_no_changes(
        taxi_user_api, mongodb, request_body,
):
    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 200

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989330'},
    )
    assert user_doc == {
        '_id': '0061be2890674631ae73e15a73989330',
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


@pytest.mark.now('2019-05-01T13:00:00+0000')
async def test_v3_users_update_antifraud(taxi_user_api, mongodb):
    request_body = {'id': '0061be2890674631ae73e15a73989330', 'antifraud': {}}

    response = await taxi_user_api.post('v3/users/update', json=request_body)
    assert response.status_code == 200

    user_doc = mongodb.users.find_one(
        {'_id': '0061be2890674631ae73e15a73989330'},
    )
    assert _remove_updated(user_doc)['antifraud'] == {
        'updated': datetime.datetime(2019, 5, 1, 13),
    }


def _remove_updated(user_doc):
    return _remove_fields(user_doc, 'updated')


def _remove_fields(user_doc, *fields):
    return {key: value for key, value in user_doc.items() if key not in fields}
