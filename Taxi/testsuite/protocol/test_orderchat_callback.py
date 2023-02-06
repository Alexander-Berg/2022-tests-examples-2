import pytest

URL = 'internal/orderchat-callback?user_id=someuserid&order_id=someorderid'
URL_NO_ORDER_ID = 'internal/orderchat-callback?user_id=someuserid'


def test_base(taxi_protocol, db):
    request = {
        'chat_id': 'chatid',
        'text': 'message text',
        'newest_message_id': '101',
        'sender': {'id': 'sender_id', 'role': 'driver'},
    }

    response = taxi_protocol.post(URL, request)
    assert response.status_code == 200
    data = response.json()
    push_id = data['id']
    assert push_id == 'chatid_someuserid_101'

    doc = db.push_events.find_one({'_id': push_id})
    doc.pop('created')
    assert doc == {
        'repack': {
            'wns': {'toast': {'text1': 'message text'}},
            'apns': {
                'aps': {
                    'content-available': 1,
                    'alert': 'message text',
                    'sound': 'default',
                },
            },
            'fcm': {
                'notification': {'sound': 'default', 'title': 'message text'},
            },
            'hms': {'sound': 'default', 'notification_title': 'message text'},
            'mpns': {'toast': {'text1': 'message text'}},
        },
        '_id': 'chatid_someuserid_101',
        'payload': {
            'extra': {
                'chat_notify': 'server',
                'msg_id': '101',
                'order_id': 'someorderid',
            },
            'fake_empty': 'Nothing',
        },
        'recipients': ['someuserid'],
    }

    request['sender']['role'] = 'system'
    response = taxi_protocol.post(URL, request)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_base_no_orderid(taxi_protocol, db):
    # TODO(denis-isaev): remove this test after deploying the python part of
    # TAXIBACKEND-15914 and checking that we always have orderid in logs.

    request = {
        'chat_id': 'chatid',
        'text': 'message text',
        'newest_message_id': '101',
        'sender': {'id': 'sender_id', 'role': 'driver'},
    }

    response = taxi_protocol.post(URL_NO_ORDER_ID, request)
    assert response.status_code == 200
    data = response.json()
    push_id = data['id']
    assert push_id == 'chatid_someuserid_101'

    doc = db.push_events.find_one({'_id': push_id})
    doc.pop('created')
    assert doc == {
        'repack': {
            'wns': {'toast': {'text1': 'message text'}},
            'apns': {
                'aps': {
                    'content-available': 1,
                    'alert': 'message text',
                    'sound': 'default',
                },
            },
            'fcm': {
                'notification': {'sound': 'default', 'title': 'message text'},
            },
            'hms': {'sound': 'default', 'notification_title': 'message text'},
            'mpns': {'toast': {'text1': 'message text'}},
        },
        '_id': 'chatid_someuserid_101',
        'payload': {
            'extra': {
                'chat_notify': 'server',
                'msg_id': '101',
                'order_id': '',
            },
            'fake_empty': 'Nothing',
        },
        'recipients': ['someuserid'],
    }

    request['sender']['role'] = 'system'
    response = taxi_protocol.post(URL_NO_ORDER_ID, request)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.translations(
    notify={
        'chat.title.driver': {'en': 'Driver wrote', 'ru': 'Водитель написал'},
    },
)
def test_with_title(taxi_protocol, db):
    request = {
        'chat_id': 'chatid',
        'text': 'message text',
        'newest_message_id': '101',
        'sender': {'id': 'sender_id', 'role': 'driver'},
    }

    response = taxi_protocol.post(
        URL, request, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    push_id = data['id']
    assert push_id == 'chatid_someuserid_101'

    doc = db.push_events.find_one({'_id': push_id})
    doc.pop('created')
    assert doc == {
        'repack': {
            'wns': {'toast': {'text1': 'message text'}},
            'apns': {
                'aps': {
                    'content-available': 1,
                    'alert': {
                        'title': 'Водитель написал',
                        'body': 'message text',
                    },
                    'sound': 'default',
                },
            },
            'fcm': {
                'notification': {
                    'sound': 'default',
                    'title': 'Водитель написал',
                    'body': 'message text',
                },
            },
            'hms': {
                'sound': 'default',
                'notification_title': 'Водитель написал',
                'notification_body': 'message text',
            },
            'mpns': {'toast': {'text1': 'message text'}},
        },
        '_id': 'chatid_someuserid_101',
        'payload': {
            'extra': {
                'chat_notify': 'server',
                'msg_id': '101',
                'order_id': 'someorderid',
            },
            'fake_empty': 'Nothing',
        },
        'recipients': ['someuserid'],
    }

    request['sender']['role'] = 'system'
    response = taxi_protocol.post(URL, request)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
