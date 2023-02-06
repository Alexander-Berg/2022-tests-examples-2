import json

import pytest


def test_empty(taxi_communications):
    response = taxi_communications.post('driver/notification/push')
    assert response.status_code == 400


def test_driver_offline(taxi_communications):
    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver',
    )
    assert response.status_code == 400


def test_no_type(taxi_communications):
    response = taxi_communications.post('driver/notification/push?topic=spam')
    assert response.status_code == 400


@pytest.mark.parametrize(
    'code,action',
    [
        (1, 'OrderRequest'),
        (6, 'OrderCanceled'),
        (9, 'OrderChangePayment'),
        (10, 'OrderChangeStatus'),
        (11, 'OrderUserReady'),
        (12, 'OrderTips'),
        (26, 'OrderSetCarRequest'),
        (27, 'OrderSetCarChain'),
        (100, 'MessageNew'),
        (120, 'NewsItem'),
        (130, 'ChatUpdated'),
        (131, 'ParkMessage'),
        (400, 'StatusChange'),
        (450, 'RobotChange'),
        (500, 'MessageBalance'),
        (701, 'MessageDkkCar'),
        (704, 'MessageDkbChair'),
        (801, 'MessageRate'),
        (820, 'MessageDesiredPaymentType'),
        (830, 'UnreadSupportAnswer'),
        (1100, 'UpdateRequest'),
    ],
)
def test_standard_push(
        taxi_communications, load_json, code, action, mockserver,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['payload']['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    # Params in body
    body = load_json(action + '.json')
    body['dbid'] = '1488'
    body['uuid'] = 'driver'
    body['code'] = code
    body['action'] = action
    body['ttl'] = 10
    body['confirm'] = True
    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200

    # Params in uri
    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver&confirm=true&ttl=10'
        '&action={0}&code={1}'.format(action, code),
        json=load_json(action + '.json'),
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


def test_push_client_id_in_mongo(taxi_communications, load_json, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver&confirm=true'
        '&action=MessageNew&code=100',
        json=load_json('MessageNew.json'),
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'code,action',
    [
        (110, 'WallChanged'),
        (700, 'MessageQc'),
        (840, 'DriverCheck'),
        (999, 'MessageLogout'),
    ],
)
def test_empty_data_push(taxi_communications, code, action, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver&confirm=true'
        '&action={0}&code={1}'.format(action, code),
    )
    assert response.status_code == 200


def test_topic_push(taxi_communications, load_json, mockserver):
    @mockserver.json_handler('/xiva/subscribe/app')
    def mock_xiva_subscribe(request):
        return mockserver.make_response('', 200)

    @mockserver.handler('/xiva/send')
    def mock_xiva_send(request):
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push?topic=PRIVATE&action=WallChanged&code=110',
    )
    assert response.status_code == 200

    response = taxi_communications.post(
        'driver/notification/push?topic=zarplata&action=DriverSpam&code=1200',
        json=load_json('DriverSpam.json'),
    )
    assert response.status_code == 200


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'])
def test_failed_to_send(taxi_communications, load_json, db, mockserver):
    @mockserver.json_handler('/xiva/subscribe/app')
    def mock_xiva_subscribe(request):
        return mockserver.make_response('', 200)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    params = {
        'dbid': '1488',
        'uuid': 'driver',
        'action': 'OrderCanceled',
        'code': 6,
    }

    response = taxi_communications.post(
        'driver/notification/push',
        params=params,
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 200

    message = db.notifications_fallback_queue.find_one()
    assert message['action'] == params['action']
    assert message['code'] == params['code']
    assert message['drivers'] == ['{dbid}_{uuid}'.format(**params)]

    params = {'topic': 'zarplata', 'action': 'DriverSpam', 'code': 1200}

    response = taxi_communications.post(
        'driver/notification/push', params=params,
    )
    assert response.status_code == 200

    message = db.notifications_fallback_queue.find_one({'code': 1200})
    assert message['action'] == params['action']
    assert message['code'] == params['code']
    assert message['topic'] == params['topic']


@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'],
    COMMUNICATIONS_PUSH_ACTION_SETTINGS={
        '__default__': {'ttl_seconds': 30, 'use_fallback_queue': True},
        'OrderCanceled': {'use_fallback_queue': False},
    },
)
def test_failed_to_send_no_fallback(
        taxi_communications, load_json, db, mockserver,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    assert db.notifications_fallback_queue.count() == 0

    params = {
        'dbid': '1488',
        'uuid': 'driver',
        'action': 'OrderCanceled',
        'code': 6,
    }

    response = taxi_communications.post(
        'driver/notification/push',
        params=params,
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 502

    assert db.notifications_fallback_queue.count() == 0

    params = {'topic': 'zarplata', 'action': 'DriverSpam', 'code': 1200}

    response = taxi_communications.post(
        'driver/notification/push', params=params,
    )
    assert response.status_code == 200

    assert db.notifications_fallback_queue.count({'code': 1200}) == 1


@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['device-notify', 'queue'],
    COMMUNICATIONS_PUSH_ACTION_SETTINGS={
        '__default__': {'ttl_seconds': 30, 'use_fallback_queue': True},
        'OrderCanceled': {'use_fallback_queue': False},
    },
)
def test_failed_to_send_no_fallback_client_error(
        taxi_communications, load_json, db, mockserver,
):
    @mockserver.json_handler('/device-notify/v1/send')
    def mock_device_notify(request):
        return {'error': 'Unknown uid'}

    assert db.notifications_fallback_queue.count() == 0

    params = {
        'dbid': '1488',
        'uuid': 'driver',
        'action': 'OrderCanceled',
        'code': 6,
    }

    response = taxi_communications.post(
        'driver/notification/push',
        params=params,
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 404

    assert db.notifications_fallback_queue.count() == 0

    params = {'topic': 'zarplata', 'action': 'DriverSpam', 'code': 1200}

    response = taxi_communications.post(
        'driver/notification/push', params=params,
    )
    assert response.status_code == 200

    assert db.notifications_fallback_queue.count({'code': 1200}) == 1


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'])
def test_disabled_by_config(taxi_communications, db, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    params = {
        'dbid': '1488',
        'uuid': 'driver',
        'action': 'DriverCheck',
        'code': 840,
    }

    response = taxi_communications.post(
        'driver/notification/push', params=params,
    )
    assert response.status_code == 200

    message = db.notifications_fallback_queue.find_one()
    assert message['action'] == params['action']
    assert message['code'] == params['code']
    assert message['drivers'] == ['{dbid}_{uuid}'.format(**params)]


@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'], TVM_ENABLED=True,
)
def test_authorization_bad(taxi_communications):

    params = {
        'dbid': 'park',
        'uuid': 'driver',
        'action': 'DriverCheck',
        'code': 840,
    }

    response = taxi_communications.post(
        'driver/notification/push', params=params,
    )
    assert response.status_code == 401


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['device-notify'])
@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
def test_localization(taxi_communications, mockserver):
    @mockserver.handler('/device-notify/v1/send')
    def mock_device_notify(request):
        data = json.loads(request.get_data())
        if data['uids'] == ['1488_driver']:
            assert data['payload']['data']['data'] == {
                'field': '1',
                'message': 'сообщение1',
                'other_field': {'a': 1, 'b': 2},
                'tarrif': '100 руб.',
            }
        elif data['uids'] == ['1488_driver1']:
            assert data['payload']['data']['data'] == {
                'field': '1',
                'message': 'message2',
                'other_field': {'a': 1, 'b': 2},
                'tarrif': 'fixed',
            }
        elif data['uids'] == ['dbid_uuid']:
            assert data['payload']['data']['data'] == {
                'field': '1',
                'message': 'message1',
                'other_field': {'a': 1, 'b': 2},
                'tarrif': 'fixed',
            }
        elif data['uids'] == ['1488_driver2']:
            data['payload']['data']['data']['push_notification'][
                'notification_text'
            ] == ['fixed']
        else:
            assert False, 'failed with driver {}'.format(data['uids'])

        return mockserver.make_response('', 200)

    params = {'dbid': '1488', 'uuid': 'driver', 'action': 0, 'code': 0}

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'data': {
                'field': '1',
                'other_field': {'a': 1, 'b': 2},
                'message': {'keyset': 'client_messages', 'key': 'key2'},
                'tarrif': {
                    'keyset': 'notify',
                    'key': 'key1',
                    'params': {'cost': 100},
                },
            },
            'collapse_key': '0',
        },
        params=params,
    )
    assert response.status_code == 200

    params = {'dbid': '1488', 'uuid': 'driver1', 'action': 0, 'code': 0}

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'data': {
                'field': '1',
                'other_field': {'a': 1, 'b': 2},
                'message': {'keyset': 'client_messages', 'key': 'key3'},
                'tarrif': {
                    'keyset': 'notify',
                    'key': 'key2',
                    'params': {'cost': 100},
                },
            },
            'collapse_key': '0',
        },
        params=params,
    )
    assert response.status_code == 200

    params = {'dbid': 'dbid', 'uuid': 'uuid', 'action': 0, 'code': 0}
    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'data': {
                'field': '1',
                'other_field': {'a': 1, 'b': 2},
                'message': {'keyset': 'client_messages', 'key': 'key2'},
                'tarrif': {
                    'keyset': 'notify',
                    'key': 'key2',
                    'params': {'cost': 100},
                },
            },
            'collapse_key': '0',
        },
        params=params,
    )
    assert response.status_code == 200

    params = {'dbid': '1488', 'uuid': 'driver2', 'action': 0, 'code': 0}

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'data': {
                'field': '1',
                'other_field': {'a': 1, 'b': 2},
                'message': 'text',
                'tarrif': {
                    'keyset': 'notify',
                    'key': 'key1',
                    'params': {'cost': 100},
                },
                'push_notification': {
                    'notification_text': [{'keyset': 'notify', 'key': 'key2'}],
                },
            },
            'collapse_key': '0',
        },
        params=params,
    )
    assert response.status_code == 200


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['device-notify'])
@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
def test_recursive_localization(taxi_communications, mockserver):
    @mockserver.handler('/device-notify/v1/send')
    def mock_device_notify(request):
        data = json.loads(request.get_data())
        if data['uids'] == ['1488_driver2']:
            data['payload']['data']['data']['push_notification'][
                'notification_text'
            ] == ['fixed']
        else:
            assert False, 'failed with driver {}'.format(data['uids'])

        return mockserver.make_response('', 200)

    params = {'dbid': '1488', 'uuid': 'driver2', 'action': 0, 'code': 0}

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'data': {
                'field': '1',
                'other_field': {'a': 1, 'b': 2},
                'message': 'text',
                'tarrif': {
                    'keyset': 'notify',
                    'key': 'key1',
                    'params': {
                        'cost': {
                            'keyset': 'notify',
                            'key': 'key1',
                            'params': {'cost': 100},
                        },
                    },
                },
                'push_notification': {
                    'notification_text': [{'keyset': 'notify', 'key': 'key2'}],
                },
            },
            'collapse_key': '0',
        },
        params=params,
    )
    assert response.status_code == 200


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'device-notify'])
@pytest.mark.experiments3(
    name='push_to_device_notify',
    consumers=['communications'],
    match={
        'consumers': ['communications'],
        'predicate': {'type': 'true'},
        'enabled': True,
        'driver_id': 'park',
        'park_db_id': 'driver',
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[],
    default_value={},
)
def test_device_notify(taxi_communications, load_json, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/device-notify/v1/send')
    def mock_device_notify(request):
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver&action=OrderCanceled'
        '&code=6',
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 200


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['device-notify', 'xiva'])
@pytest.mark.experiments3(
    name='push_to_device_notify',
    consumers=['communications'],
    match={
        'consumers': ['communications'],
        'predicate': {'type': 'true'},
        'enabled': True,
        'driver_id': '1488',
        'park_db_id': 'driver',
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[],
    default_value={},
)
def test_device_notify_bad_response(
        taxi_communications, load_json, mockserver,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        assert request.args['user'] == '1488-driver'
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/device-notify/v1/send')
    def mock_device_notify(request):
        return {'error': 'ERROR'}

    response = taxi_communications.post(
        'driver/notification/push?dbid=1488&uuid=driver&action=OrderCanceled'
        '&code=6',
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 200
    assert mock_xiva.times_called == 1
    assert mock_device_notify.times_called == 1


@pytest.mark.parametrize('priority, code', [('high', 200), ('normal', 200)])
def test_priority(taxi_communications, mockserver, priority, code):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['payload']['priority'] == priority
        return mockserver.make_response('', 200)

    # Params in body
    body = {
        'collapse_key': 'Alert: 1234567890',
        'priority': priority,
        'data': {'id': '1234567890', 'message': 'New message', 'name': 'Anon'},
    }
    body['dbid'] = '1488'
    body['uuid'] = 'driver'
    body['code'] = 100
    body['action'] = 'MessageNew'
    body['ttl'] = 10
    body['confirm'] = True
    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == code


@pytest.mark.config(COMMUNICATIONS_DBID_UUID_AUTH_MIN_TAXIMETER_VERSION='9.15')
@pytest.mark.parametrize('code,action', [(1, 'OrderRequest')])
@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'])
def test_push_dbid_uuid(
        taxi_communications, load_json, code, action, mockserver,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        assert request.args['user'] == '1488-driver'
        data = json.loads(request.get_data())
        assert data['payload']['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            '{"profiles":[{"data":{"taximeter_version":"9.15 (10782)"},'
            '"park_driver_profile_id":"1488_driver"}]}',
            200,
        )

    body = load_json(action + '.json')
    body['dbid'] = '1488'
    body['uuid'] = 'driver'
    body['code'] = code
    body['action'] = action
    body['ttl'] = 10
    body['confirm'] = True
    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DBID_UUID_AUTH_MIN_TAXIMETER_VERSION='9.15',
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_push_without_session(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        assert request.args['user'] == 'park_id-driver_id'
        return mockserver.make_response('', 200)

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            '{"profiles":[{"data":{"taximeter_version":"9.15 (10782)"},'
            '"park_driver_profile_id":"1488_driver"}]}',
            200,
        )

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'dbid': 'park_id',
            'uuid': 'driver_id',
            'code': 100,
            'action': 'MessageNew',
            'ttl': 10,
            'collapse_key': 'Alert: 1234567890',
            'data': {
                'id': '1234567890',
                'message': 'New message',
                'name': 'Anon',
            },
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
