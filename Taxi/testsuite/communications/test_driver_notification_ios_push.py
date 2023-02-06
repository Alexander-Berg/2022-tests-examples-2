import json

import pytest


@pytest.fixture(autouse=True)
def driver_profiles(mockserver):
    @mockserver.handler('/driver_profiles/v1/driver/app/profiles/retrieve')
    def mock_driver_profiles(request):
        return mockserver.make_response(
            '{"profiles":[{"data":{"taximeter_version":"8.49 (10782)"},'
            '"park_driver_profile_id":"park_iosdriver"}]}',
            200,
        )

    return mock_driver_profiles


@pytest.mark.config(DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'])
def test_ios_push(taxi_communications, mockserver, load_json):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push?dbid=park&uuid=iosdriver'
        '&action=OrderCanceled&code=6',
        json=load_json('OrderCanceled.json'),
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_simple(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {
            'id': '1234567890',
            'message': (
                'Dear driver! Please come to check the license at '
                'Yandex.Taxi office'
            ),
            'name': 'License Verification',
        },
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_background(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'content-available': 1,
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {
            'id': '1234567890',
            'message': (
                'Dear driver! Please come to check the license at '
                'Yandex.Taxi office'
            ),
            'name': 'License Verification',
        },
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
            'badge': 10,
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_badge_in_config(
        taxi_communications, mockserver, load_json,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'badge': (
                        10
                    ),  # from COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK
                    'content-available': 1,
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {
            'id': '1234567890',
            'message': (
                'Dear driver! Please come to check the license at '
                'Yandex.Taxi office'
            ),
            'name': 'License Verification',
        },
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
            'badge': 10,
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_badge_in_data(
        taxi_communications, mockserver, load_json,
):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'badge': 12,  # from payload.data.badge
                    'content-available': 1,
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {
            'id': '1234567890',
            'message': (
                'Dear driver! Please come to check the license at '
                'Yandex.Taxi office'
            ),
            'name': 'License Verification',
            'badge': 12,
        },
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {'title': 'name', 'message': 'message'},
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_empty_repack(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert 'repack' not in data
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {'id': '1234567890', 'key': 'value'},
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={'__default__': {}},
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_disabled(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert 'repack' not in data
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    body = {
        'dbid': 'park',
        'uuid': 'iosdriver',
        'code': 100,
        'action': 'MessageNew',
        'collapse_key': 'Alert: 1234567890',
        'ttl': 59,
        'data': {
            'id': '1234567890',
            'key': 'value',
            'message': (
                'Dear driver! Please come to check the license at '
                'Yandex.Taxi office'
            ),
            'name': 'License Verification',
        },
    }

    response = taxi_communications.post(
        'driver/notification/push',
        json=body,
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
            'badge': 1,
            'sound': 'default',
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_sound(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'badge': 1,
                    'content-available': 1,
                    'sound': 'default',
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'dbid': 'park',
            'uuid': 'iosdriver',
            'code': 100,
            'action': 'MessageNew',
            'collapse_key': 'Alert: 1234567890',
            'ttl': 59,
            'data': {
                'id': '1234567890',
                'key': 'value',
                'message': (
                    'Dear driver! Please come to check the license at '
                    'Yandex.Taxi office'
                ),
                'name': 'License Verification',
            },
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
            'badge': 1,
            'sound': 'default',
            'collapse-id': True,
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_collapse(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'collapse-id': 'Alert: 1234567890',
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'badge': 1,
                    'content-available': 1,
                    'sound': 'default',
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'dbid': 'park',
            'uuid': 'iosdriver',
            'code': 100,
            'action': 'MessageNew',
            'collapse_key': 'Alert: 1234567890',
            'ttl': 59,
            'data': {
                'id': '1234567890',
                'key': 'value',
                'message': (
                    'Dear driver! Please come to check the license at '
                    'Yandex.Taxi office'
                ),
                'name': 'License Verification',
            },
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'background': True,
            'badge': 1,
            'sound': 'default',
            'collapse-id': True,
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_collapse_empty(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data['repack'] == {
            'apns': {
                'collapse-id': '100',
                'aps': {
                    'alert': {
                        'body': (
                            'Dear driver! Please come to check '
                            'the license at Yandex.Taxi office'
                        ),
                        'title': 'License Verification',
                    },
                    'badge': 1,
                    'content-available': 1,
                    'sound': 'default',
                },
                'repack_payload': ['*'],
            },
            'other': {'repack_payload': ['*']},
        }
        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'dbid': 'park',
            'uuid': 'iosdriver',
            'code': 100,
            'action': 'MessageNew',
            'ttl': 59,
            'data': {
                'id': '1234567890',
                'key': 'value',
                'message': (
                    'Dear driver! Please come to check the license at '
                    'Yandex.Taxi office'
                ),
                'name': 'License Verification',
            },
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_DRIVER_NOTIFICATION_REPACK={
        '__default__': {},
        'MessageNew': {
            'title': 'name',
            'message': 'message',
            'collapse-id': True,
            'payload_keys': (
                '{"apns": {"new_apns_key": 11, "aps": {"sound": "ring", '
                '"alert": {"alert_key": "value"}, "presentBadge": true, '
                '"presentSound": true, "some_new_aps_key": '
                '{"a": 5}, "content-available": 1, '
                '"mutable-content": 1, "badge" :1}}}'
            ),
        },
    },
    DRIVER_NOTIFICATION_SEND_CLIENTS=['xiva'],
)
def test_ios_push_repack_tpl(taxi_communications, mockserver):
    @mockserver.handler('/xiva/send')
    def mock_xiva(request):
        data = json.loads(request.get_data())
        assert data == {
            'payload': {
                'action': 100,
                'collapse_key': '100',
                'data': {
                    'id': '1234567890',
                    'key': 'value',
                    'message': (
                        'Dear driver! Please come to check the license at '
                        'Yandex.Taxi office'
                    ),
                    'name': 'License Verification',
                },
                'id': 'idempotency_token',
                'ttl': 59,
            },
            'repack': {
                'apns': {
                    'new_apns_key': 11,
                    'aps': {
                        'alert': {
                            'alert_key': 'value',
                            'body': (
                                'Dear driver! Please come to check the '
                                'license at Yandex.Taxi office'
                            ),
                            'title': 'License Verification',
                        },
                        'badge': 1,
                        'content-available': 1,
                        'mutable-content': 1,
                        'presentBadge': True,
                        'presentSound': True,
                        'some_new_aps_key': {'a': 5},
                        'sound': 'ring',
                    },
                    'collapse-id': '100',
                    'repack_payload': ['*'],
                },
                'other': {'repack_payload': ['*']},
            },
        }

        assert request.args['user'] == 'park-iosdriver'
        return mockserver.make_response('', 200)

    response = taxi_communications.post(
        'driver/notification/push',
        json={
            'dbid': 'park',
            'uuid': 'iosdriver',
            'code': 100,
            'action': 'MessageNew',
            'ttl': 59,
            'data': {
                'id': '1234567890',
                'key': 'value',
                'message': (
                    'Dear driver! Please come to check the license at '
                    'Yandex.Taxi office'
                ),
                'name': 'License Verification',
            },
        },
        headers={'X-Idempotency-Token': 'idempotency_token'},
    )
    assert response.status_code == 200
