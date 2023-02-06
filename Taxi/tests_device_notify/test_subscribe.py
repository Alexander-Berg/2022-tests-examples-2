import json

import pytest


@pytest.fixture(name='iid_service')
def _iid_service(mockserver, fcm_service):
    @mockserver.json_handler('/iid/v1:batchAdd')
    def _iid_batch_add(request):
        return fcm_service.on_register(request)

    @mockserver.json_handler('/iid/v1:batchRemove')
    def _iid_batch_remove(request):
        return fcm_service.on_unregister(request)


# pylint: disable=too-many-locals, too-many-statements
async def test_subscribe(taxi_device_notify, pgsql, iid_service):
    k_api_key_header = 'X-YaTaxi-API-Key'
    # Keys, initialized by secdist_vars.yaml
    k_api_key1 = '2345'
    k_api_key2 = '3456'
    k_service_name1 = 'taximeter'
    k_service_name2 = 'communications'
    # Few tokens
    kfcm_token1 = 'fcm-token-1'
    kfcm_token2 = 'fcm-token-2'
    kfcm_token3 = 'fcm-token-3'
    # Dummy drivers
    k_user1 = 'driver-1'
    k_user2 = 'driver-2'

    def get_users():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT uid FROM devicenotify.users ' ' ORDER BY user_id',
        )
        result = list(row[0] for row in cursor)
        cursor.close()
        return result

    def get_services():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT name FROM devicenotify.services ' ' ORDER BY service_id',
        )
        result = list(row[0] for row in cursor)
        cursor.close()
        return result

    def get_tokens(uid):
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT tk.channel_type, tk.token '
            ' FROM devicenotify.tokens tk, devicenotify.users us '
            ' WHERE us.uid = \'{}\' AND us.user_id = tk.user_id '
            ' ORDER BY tk.user_id, tk.channel_type'.format(uid),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def get_topics(uid, service):
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT UNNEST(tp.topics) '
            ' FROM devicenotify.topics tp, devicenotify.users us, '
            '      devicenotify.services sv '
            ' WHERE us.uid = \'{}\' AND us.user_id = tp.user_id '
            '   AND sv.name = \'{}\' AND sv.service_id = tp.service_id '
            ' ORDER BY 1'.format(uid, service),
        )
        result = list(row[0] for row in cursor)
        cursor.close()
        return result

    assert get_users() == []
    assert get_services() == []

    headers = {k_api_key_header: k_api_key1}
    params = {'uid': k_user1, 'service': k_service_name1, 'event': '_'}

    data = {'channels': [{'type': 'fcm', 'token': kfcm_token1}]}
    # now = datetime.datetime.utcnow()
    params['event'] = 'step1'
    assert get_tokens(k_user1) == []
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_users() == [k_user1]
    assert get_services() == []  # no topics yet, so service_id is not created
    assert get_tokens(k_user1) == [('fcm', kfcm_token1)]

    data = {'topics': ['moscow.online', 'russia.online']}
    # now = datetime.datetime.utcnow()
    params['event'] = 'step2'
    assert get_topics(k_user1, k_service_name1) == []
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_users() == [k_user1]
    assert get_services() == [k_service_name1]
    assert get_tokens(k_user1) == [('fcm', kfcm_token1)]
    assert get_topics(k_user1, k_service_name1) == [
        'moscow.online',
        'russia.online',
    ]

    params['uid'] = k_user2
    data = {
        'channels': [{'type': 'fcm', 'token': kfcm_token2}],
        'topics': ['moscow.online', 'russia.online'],
    }
    # now = datetime.datetime.utcnow()
    params['event'] = 'step3'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_users() == [k_user1, k_user2]
    assert get_services() == [k_service_name1]
    assert get_tokens(k_user2) == [('fcm', kfcm_token2)]
    assert get_topics(k_user2, k_service_name1) == [
        'moscow.online',
        'russia.online',
    ]

    data['topics'] = ['moscow.offline']
    params['event'] = 'step4'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_users() == [k_user1, k_user2]
    assert get_services() == [k_service_name1]
    assert get_tokens(k_user2) == [('fcm', kfcm_token2)]
    assert get_topics(k_user2, k_service_name1) == ['moscow.offline']

    headers[k_api_key_header] = k_api_key2
    params['service'] = k_service_name2
    data['channels'][0]['token'] = kfcm_token3
    data['topics'] = ['russia.offline']
    params['event'] = 'step5'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_users() == [k_user1, k_user2]
    assert get_services() == [k_service_name1, k_service_name2]
    assert get_tokens(k_user2) == [('fcm', kfcm_token3)]
    assert get_topics(k_user2, k_service_name1) == ['moscow.offline']
    assert get_topics(k_user2, k_service_name2) == ['russia.offline']

    # User1 should not be changed since last check
    assert get_tokens(k_user1) == [('fcm', kfcm_token1)]
    assert get_topics(k_user1, k_service_name1) == [
        'moscow.online',
        'russia.online',
    ]
    assert get_topics(k_user1, k_service_name2) == []

    # check invalid tokens
    data['channels'] = [{'type': 'fcm', 'token': 'BLACKLISTED'}]
    params['event'] = 'step6'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'invalid token: BLACKLISTED',
    }

    # Logoff user-1, remove his tokens
    data = {'channels': []}
    params['uid'] = k_user1
    params['event'] = 'step7'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert get_tokens(k_user1) == []
