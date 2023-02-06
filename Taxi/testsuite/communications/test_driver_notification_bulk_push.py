import json
import random

import pytest


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'])
def test_push(taxi_communications, mockserver):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        data = json.loads(request.get_data())
        assert data['payload']['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert json.loads(data['payload'])['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    # Params in body
    body = {
        'action': 'OrderCanceled',
        'code': 6,
        'ttl': 10,
        'data': {'order': '12345', 'message': 'Take your tips'},
        'collapse_key': 'OrderTips: 12345',
        'drivers': [
            {'dbid': 'testdbid', 'uuid': 'testuuid'},
            {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
        ],
    }
    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Params in uri
    response = taxi_communications.post(
        'driver/notification/bulk-push?action=OrderCanceled&code=6&ttl=10',
        json={
            'data': {'order': '12345', 'message': 'Take your tips'},
            'collapse_key': 'OrderTips: 12345',
            'drivers': [
                {'dbid': 'testdbid', 'uuid': 'testuuid'},
                {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
            ],
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(COMMUNICATIONS_NOTIFICATION_BULK_SEND_MAX_SIZE=4)
def test_limit(taxi_communications, mockserver):
    drivers = []
    for i in range(5):
        driver = {'dbid': 'dbid' + str(i), 'uuid': 'uuid' + str(i)}
        drivers.append(driver)

    response = taxi_communications.post(
        'driver/notification/bulk-push?action=OrderCanceled&code=6&ttl=10',
        json={'data': 'data', 'collapse_key': 'key', 'drivers': drivers},
    )
    assert response.status_code == 400


@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'], XIVA_RETRIES=1,
)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(name)s, ваш баланс %(cost)s руб',
            'en': '%(name)s, your balance is %(cost)s dollars',
        },
    },
    client_messages={
        'key2': {
            'ru': 'Привет, %(driver_name)s!',
            'en': 'Hi, %(driver_name)s!',
        },
    },
)
def test_personal_payload(taxi_communications, mockserver, load_json):
    @mockserver.json_handler('/xiva/batch_send')
    def mock_xiva_batch_send(request):
        assert False, 'xiva/batch_send must not be called in this test'

    @mockserver.json_handler('/xiva/send')
    def mock_xiva_send(request):
        user_data = {
            'dbid0-uuid0': {
                'title': 'default title',
                'message': 'default message',
                'loc_title': 'default driver, your balance is 0 dollars',
                'loc_message': 'Hi, default driver!',
                'text': None,
            },
            'dbid1-uuid1': {
                'title': 'title1',
                'message': 'default message',
                'loc_title': 'default driver, ваш баланс 0 руб',
                'loc_message': 'Привет, default driver!',
                'text': None,
            },
            'dbid2-uuid2': {
                'title': 'title2',
                'message': 'message2',
                'loc_title': ', ваш баланс 10 руб',
                'loc_message': 'Привет, !',
                'text': 'new text field',
            },
            'dbid3-uuid3': {
                'title': 'default title',
                'message': 'default message',
                'loc_title': 'Driver 3, your balance is 100 dollars',
                'loc_message': 'Hi, Driver 3!',
                'text': None,
            },
            'dbid4-uuid4': {
                'title': 'default title',
                'message': 'default message',
                'loc_title': 'Водитель 4, ваш баланс 500 руб',
                'loc_message': 'Привет, Водитель 4!',
                'text': None,
            },
        }

        expected_data = user_data[request.args['user']]

        body = json.loads(request.get_data())
        data = body['payload']['data']
        data['text'] = data.get('text', None)
        assert data == expected_data

        return 'OK'

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        response = json.dumps(
            {
                'profiles': [
                    {
                        'data': {'taximeter_version': '8.49 (10782)'},
                        'park_driver_profile_id': 'dbid0_uuid0',
                    },
                    {
                        'data': {'taximeter_version': '8.49 (10782)'},
                        'park_driver_profile_id': 'dbid1_uuid1',
                    },
                    {
                        'data': {'taximeter_version': '8.49 (10782)'},
                        'park_driver_profile_id': 'dbid2_uuid2',
                    },
                    {
                        'data': {'taximeter_version': '8.49 (10782)'},
                        'park_driver_profile_id': 'dbid3_uuid3',
                    },
                    {
                        'data': {'taximeter_version': '8.49 (10782)'},
                        'park_driver_profile_id': 'dbid4_uuid4',
                    },
                ],
            },
        )
        return mockserver.make_response(response, 200)

    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={
            'action': 'MessageNew',
            'code': 100,
            'data': {
                'title': 'default title',
                'message': 'default message',
                'loc_title': {
                    'keyset': 'notify',
                    'key': 'key1',
                    'params': {'cost': 0, 'name': 'default driver'},
                },
                'loc_message': {
                    'keyset': 'client_messages',
                    'key': 'key2',
                    'params': {'driver_name': 'default driver'},
                },
            },
            'drivers': [
                # ----------------------------------------
                # All defaults
                # Use fallback locale (en)
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                # ----------------------------------------
                # Override fields without localization
                # Use driver locale (ru)
                {'dbid': 'dbid1', 'uuid': 'uuid1', 'title': 'title1'},
                # ----------------------------------------
                # Override fields and localization params, add new field
                # Use driver locale (ru)
                {
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'title': 'title2',
                    'message': 'message2',
                    'text': 'new text field',
                    'loc_title': {'params': {'cost': 10, 'name': ''}},
                    'loc_message': {'params': {'driver_name': ''}},
                },
                # ----------------------------------------
                # Override fields and localization params
                # Use driver locale (en)
                {
                    'dbid': 'dbid3',
                    'uuid': 'uuid3',
                    'loc_title': {'params': {'cost': 100, 'name': 'Driver 3'}},
                    'loc_message': {'params': {'driver_name': 'Driver 3'}},
                },
                # ----------------------------------------
                # Override fields and localization params
                # Use park locale (ru)
                {
                    'dbid': 'dbid4',
                    'uuid': 'uuid4',
                    'loc_title': {
                        'params': {'cost': 500, 'name': 'Водитель 4'},
                    },
                    'loc_message': {'params': {'driver_name': 'Водитель 4'}},
                },
            ],
        },
    )
    assert response.status_code == 200
    assert mock_xiva_send.times_called == 5


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'])
def test_fallback_queue(taxi_communications, mockserver, db):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    drivers = []
    for i in range(15):
        i_ = str(i)
        driver = {'dbid': 'dbid' + i_, 'uuid': 'uuid' + i_}
        drivers.append(driver)

    params = {'action': 'OrderCanceled', 'code': 6, 'ttl': 10}
    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={'data': 'data', 'collapse_key': 'key', 'drivers': drivers},
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert db.notifications_fallback_queue.count() == 1

    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={'data': 'data', 'collapse_key': 'key', 'drivers': drivers},
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert db.notifications_fallback_queue.count() == 2


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'device-notify'])
@pytest.mark.experiments3(
    name='push_to_device_notify',
    consumers=['communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'sample',
            'value': {},
            'predicate': {
                'type': 'eq',
                'init': {'arg_name': 'is_bulk', 'arg_type': 'int', 'value': 1},
            },
        },
    ],
)
def test_device_notify(taxi_communications, mockserver):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/device-notify/v1/send')
    def mock_device_notify(request):
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/bulk-push?action=OrderCanceled&code=6&ttl=10',
        json={
            'data': {'order': '12345', 'message': 'Take your tips'},
            'collapse_key': 'OrderTips: 12345',
            'drivers': [
                {'dbid': 'testdbid', 'uuid': 'testuuid'},
                {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'], XIVA_RETRIES=1)
@pytest.mark.translations(
    taximeter_messages={
        'SurgeNotificationService_HighSurchargeNotification': {
            'en': 'Your balance is %(surcharge)s %(currency_sign)s',
        },
    },
)
def test_huge(taxi_communications, mockserver, mongodb):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        return mockserver.make_response('OK', 200)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        return mockserver.make_response('OK', 200)

    profiles = []
    for i in range(500):
        profiles.append(
            {
                'data': {'taximeter_version': '8.49 (10782)'},
                'park_driver_profile_id': f'huge_uuid{i}',
            },
        )
    driver_profiles_response = json.dumps({'profiles': profiles})

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(driver_profiles_response, 200)

    # Prepare big bulk with random fields
    bulk_size = 500

    drivers = []
    for i in range(bulk_size):
        dbid, uuid = 'huge', 'uuid%s' % i

        driver_push = {'dbid': dbid, 'uuid': uuid}
        # Append new field
        if random.randint(1, 100) > 50:
            driver_push['title'] = 'My title'

        # Override exiting (params only or completelly)
        if random.randint(1, 100) > 50:
            driver_push['message'] = 'My value'
        elif random.randint(1, 100) > 50:
            driver_push['message'] = {
                'params': {
                    'surcharge': random.randint(1, 1000),
                    'currency_sign': random.choice(['₽', '$', '€']),
                },
            }
        drivers.append(driver_push)

    # Send big bulk
    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={
            'code': 100,
            'collapse_key': 'MessageNew',
            'ttl': 300,
            'action': 'MessageNew',
            'data': {
                'message': {
                    'keyset': 'taximeter_messages',
                    'key': (
                        'SurgeNotificationService_HighSurchargeNotification'
                    ),
                    'params': {'currency_sign': 'asdf', 'surcharge': 100},
                },
                'id': '3172d3235f3947ca9ec0923bd9022629',
                'name': 'asdf',
            },
            'drivers': drivers,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_bulk_repack(taxi_communications, mockserver):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        data = json.loads(request.get_data())
        assert data['payload']['id'] == 'idempotency_token'
        assert data['repack'] == {
            'apns': {
                'aps': {'alert': {'body': 'Take your tips'}},
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={
            'action': 'OrderCanceled',
            'code': 6,
            'ttl': 10,
            'data': {'order': '12345', 'message': 'Take your tips'},
            'collapse_key': 'OrderTips: 12345',
            'drivers': [
                {'dbid': 'testdbid', 'uuid': 'testuuid'},
                {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
            ],
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(COMMUNICATIONS_DBID_UUID_AUTH_MIN_TAXIMETER_VERSION='9.15')
@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'])
def test_push_dbid_uuid_bulk(taxi_communications, mockserver):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        data = json.loads(request.get_data())
        assert data['recipients'] == [
            'testdbid-testuuid',
            'testdbid2-testuuid2',
        ]
        return mockserver.make_response('', 200)

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            '{"profiles":[{"data":{"taximeter_version":"8.49 (10782)"},'
            '"park_driver_profile_id":"testdbid_testuuid"},'
            '{"data":{"taximeter_version":"9.15 (10782)"},'
            '"park_driver_profile_id":"testdbid2_testuuid2"}]}',
            200,
        )

    body = {
        'action': 'OrderCanceled',
        'code': 6,
        'ttl': 10,
        'data': {'order': '12345', 'message': 'Take your tips'},
        'collapse_key': 'OrderTips: 12345',
        'drivers': [
            {'dbid': 'testdbid', 'uuid': 'testuuid'},  # old version
            {'dbid': 'testdbid2', 'uuid': 'testuuid2'},  # new version
        ],
    }
    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(name)s, ваш баланс %(cost)s руб',
            'en': '%(name)s, your balance is %(cost)s dollars',
        },
    },
    client_messages={
        'key2': {
            'ru': 'Привет, %(driver_name)s!',
            'en': 'Hi, %(driver_name)s!',
        },
    },
)
@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'])
def test_push_recursive_localizations(taxi_communications, mockserver):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        data = json.loads(request.get_data())
        assert data['payload']['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert json.loads(data['payload'])['id'] == 'idempotency_token'
        return mockserver.make_response('', 200)

    # Params in body
    body = {
        'action': 'OrderCanceled',
        'code': 6,
        'ttl': 10,
        'data': {
            'order': '12345',
            'message': {
                'keyset': 'notify',
                'key': 'key1',
                'params': {
                    'cost': 0,
                    'name': {
                        'keyset': 'notify',
                        'key': 'key1',
                        'params': {'cost': 0, 'name': 'default driver'},
                    },
                },
            },
        },
        'collapse_key': 'OrderTips: 12345',
        'drivers': [
            {'dbid': 'testdbid', 'uuid': 'testuuid'},
            {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
        ],
    }
    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Params in uri
    response = taxi_communications.post(
        'driver/notification/bulk-push?action=OrderCanceled&code=6&ttl=10',
        json={
            'data': {'order': '12345', 'message': 'Take your tips'},
            'collapse_key': 'OrderTips: 12345',
            'drivers': [
                {'dbid': 'testdbid', 'uuid': 'testuuid'},
                {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
            ],
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'taximeter_version,xiva_recipients',
    [
        (
            '9.15 (10782)',
            {
                'testdbid-testuuid',
                'testdbid2-testuuid2',
                'testdbid100-testuuid100',
            },
        ),
        (
            '9.14 (10678)',
            {
                'testdbid-testuuid',
                'testdbid2-testuuid2',
                'testdbid100-testuuid100',
            },
        ),
    ],
)
@pytest.mark.config(
    COMMUNICATIONS_DBID_UUID_AUTH_MIN_TAXIMETER_VERSION='9.15',
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_bulk_push_without_session(
        taxi_communications, mockserver, taximeter_version, xiva_recipients,
):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_bulk(request):
        data = json.loads(request.get_data())
        assert set(data['recipients']) == xiva_recipients
        return mockserver.make_response('', 200)

    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        response = {
            'profiles': [
                {
                    'data': {'taximeter_version': taximeter_version},
                    'park_driver_profile_id': 'testdbid_testuuid',
                },
            ],
        }
        return mockserver.make_response(json.dumps(response), 200)

    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={
            'action': 'OrderCanceled',
            'code': 6,
            'ttl': 10,
            'data': {'order': '12345', 'message': 'Take your tips'},
            'collapse_key': 'OrderTips: 12345',
            'drivers': [
                {'dbid': 'testdbid', 'uuid': 'testuuid'},
                {'dbid': 'testdbid2', 'uuid': 'testuuid2'},
                {'dbid': 'testdbid100', 'uuid': 'testuuid100'},
            ],
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'action,expected_code', [('MessageNew', 500), ('PersonalOffer', 200)],
)
@pytest.mark.config(
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva', 'queue'],
    XIVA_RETRIES=1,
    COMMUNICATIONS_PUSH_ACTION_SETTINGS={
        '__default__': {'use_fallback_queue': True, 'ttl_seconds': 43200},
        'MessageNew': {'use_fallback_queue': False},
    },
    XIVA_CLIENT_BULK_PUSH_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
        '/driver/notification/bulk-push': {'attempts': 2, 'timeout-ms': 100},
    },
)
@pytest.mark.translations(
    notify={
        'key1': {
            'ru': '%(name)s, ваш баланс %(cost)s руб',
            'en': '%(name)s, your balance is %(cost)s dollars',
        },
    },
    client_messages={
        'key2': {
            'ru': 'Привет, %(driver_name)s!',
            'en': 'Hi, %(driver_name)s!',
        },
    },
)
def test_bulk_use_fallback_queue(
        taxi_communications, mockserver, db, action, expected_code,
):
    @mockserver.handler('/xiva/batch_send')
    def mock_xiva_batch_send(request):
        return mockserver.make_response('', 502)

    @mockserver.handler('/xiva/send')
    def mock_xiva_send(request):
        return mockserver.make_response('', 502)

    response = taxi_communications.post(
        'driver/notification/bulk-push',
        json={
            'action': action,
            'code': 100,
            'data': {
                'title': 'default title',
                'message': 'default message',
                'loc_title': {
                    'keyset': 'notify',
                    'key': 'key1',
                    'params': {'cost': 0, 'name': 'default driver'},
                },
                'loc_message': {
                    'keyset': 'client_messages',
                    'key': 'key2',
                    'params': {'driver_name': 'default driver'},
                },
            },
            'drivers': [
                # ----------------------------------------
                # All defaults
                # Use fallback locale (en)
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'ddddd', 'uuid': 'uuuu'},
                # ----------------------------------------
                # Override fields without localization
                # Use driver locale (ru)
                {'dbid': 'dbid1', 'uuid': 'uuid1', 'title': 'title1'},
                # ----------------------------------------
                # Override fields and localization params, add new field
                # Use driver locale (ru)
                {
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'title': 'title2',
                    'message': 'message2',
                    'text': 'new text field',
                    'loc_title': {'params': {'cost': 10, 'name': ''}},
                    'loc_message': {'params': {'driver_name': ''}},
                },
                # ----------------------------------------
                # Override fields and localization params
                # Use driver locale (en)
                {
                    'dbid': 'dbid3',
                    'uuid': 'uuid3',
                    'loc_title': {'params': {'cost': 100, 'name': 'Driver 3'}},
                    'loc_message': {'params': {'driver_name': 'Driver 3'}},
                },
                # ----------------------------------------
                # Override fields and localization params
                # Use park locale (ru)
                {
                    'dbid': 'dbid4',
                    'uuid': 'uuid4',
                    'loc_title': {
                        'params': {'cost': 500, 'name': 'Водитель 4'},
                    },
                    'loc_message': {'params': {'driver_name': 'Водитель 4'}},
                },
            ],
        },
    )
    assert response.status_code == expected_code
    assert mock_xiva_send.times_called == 8
    assert mock_xiva_batch_send.times_called == 1
    if expected_code == 200:
        assert db.notifications_fallback_queue.count() == 5
