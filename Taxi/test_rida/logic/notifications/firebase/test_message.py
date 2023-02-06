from typing import Any
from typing import Dict

import pytest

from rida.generated.service.swagger.models.api import fcm
from rida.logic.notifications.firebase import message as message_module


@pytest.mark.now('2021-11-20T11:00:00')
@pytest.mark.parametrize(
    ['notification', 'expected_message'],
    [
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                title='some_title',
                body='some_body',
                data={'some_key': 'some_value'},
                sound=fcm.PlatformSpecificObj(
                    android='some_android_sound', apns='some_apns_sound',
                ),
                notification_channel=fcm.PlatformSpecificObj(
                    android='some_android_notification_channel',
                    apns='some_apns_notification_channel',
                ),
                wake_application=True,
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'data': {'some_key': 'some_value'},
                    'notification': {
                        'body': 'some_body',
                        'channel_id': 'some_android_notification_channel',
                        'sound': 'some_android_sound',
                        'tag': 'some_id',
                        'title': 'some_title',
                    },
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'alert': {
                                'body': 'some_body',
                                'title': 'some_title',
                            },
                            'badge': 1,
                            'content_available': True,
                            'sound': 'some_apns_sound',
                        },
                        'some_key': 'some_value',
                    },
                },
            },
            id='all_fields',
        ),
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                title='some_title',
                body='some_body',
                sound=fcm.PlatformSpecificObj(apns='some_apns_sound'),
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'notification': {
                        'body': 'some_body',
                        'tag': 'some_id',
                        'title': 'some_title',
                    },
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'alert': {
                                'body': 'some_body',
                                'title': 'some_title',
                            },
                            'badge': 1,
                            'sound': 'some_apns_sound',
                        },
                    },
                },
            },
            # add_bid, passenger_accept_bid, passenger_accept_another_driver,
            # passenger_declined_bid, passenger_offer_cancel, offer_expired,
            # passenger_offer_cancel_bulk
            id='title,body,apns_sound',
        ),
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                title='some_title',
                sound=fcm.PlatformSpecificObj(apns='some_apns_sound'),
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'notification': {'tag': 'some_id', 'title': 'some_title'},
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'alert': {'title': 'some_title'},
                            'badge': 1,
                            'sound': 'default',  # since body is missing
                        },
                    },
                },
            },
            # waiting_ride, cancelled_ride
            id='title,apns_sound',
        ),
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                title='some_title',
                body='some_body',
                data={'offer_guid': 'some_guid', 'push_type': 1},
                sound=fcm.PlatformSpecificObj(apns='some_apns_sound'),
                notification_channel=fcm.PlatformSpecificObj(
                    android='some_android_notification_channel',
                ),
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'data': {'offer_guid': 'some_guid', 'push_type': '1'},
                    'notification': {
                        'body': 'some_body',
                        'channel_id': 'some_android_notification_channel',
                        'tag': 'some_id',
                        'title': 'some_title',
                    },
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'alert': {
                                'body': 'some_body',
                                'title': 'some_title',
                            },
                            'badge': 1,
                            'sound': 'some_apns_sound',
                        },
                        'offer_guid': 'some_guid',
                        'push_type': 1,
                    },
                },
            },
            # new_offer
            id='title,body,data,apns_sound,android_notification_channel',
        ),
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                title='some_title',
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'notification': {'tag': 'some_id', 'title': 'some_title'},
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'alert': {'title': 'some_title'},
                            'badge': 1,
                            'sound': 'default',
                        },
                    },
                },
            },
            # old expire_push_notifications
            id='title',
        ),
        pytest.param(
            fcm.Notification(
                id='some_id',
                firebase_token='firebase_token',
                data={'push_type': 666, 'push_id': 'some_other_id'},
                wake_application=True,
            ),
            {
                'token': 'firebase_token',
                'android': {
                    'data': {'push_type': '666', 'push_id': 'some_other_id'},
                    'priority': 'high',
                    'ttl': '0s',
                },
                'apns': {
                    'headers': {
                        'apns-collapse-id': 'some_id',
                        'apns-expiration': '1637406000',
                        'apns-priority': '10',
                        'apns-topic': 'rida',
                    },
                    'payload': {
                        'aps': {
                            'badge': 1,
                            'content_available': True,
                            'sound': 'default',
                        },
                        'push_type': 666,
                        'push_id': 'some_other_id',
                    },
                },
            },
            # new expire_push_notifications
            id='data,wake_application',
        ),
    ],
)
def test_prepare_message(
        notification: fcm.Notification, expected_message: Dict[str, Any],
):
    message = message_module.prepare_message(notification).serialize()
    assert message == expected_message
