from collections import namedtuple

import pytest

from taxi_maintenance.stuff import send_user_chat_push

UUID4 = '2830227ea6944f95b894d27df5f9ace4'


@pytest.mark.filldb()
@pytest.inline_callbacks
@pytest.mark.translations([
    ('notify', 'user_chat.new_message', 'ru', 'push ru'),
    ('notify', 'user_chat.new_message', 'en', 'push en'),
])
def test_send_push(patch):

    @patch('taxi_maintenance.stuff.send_user_chat_push._need_send_push')
    def mock_need_send_push(doc, minutes_from_incident, push_time,
                            cities_timezones, log_extra=None):
        return True

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = namedtuple('uuid4', 'hex')
        return uuid4_(UUID4)

    push_kwargs = []

    @patch('taxi.internal.notifications._pusher.push')
    def mock_pusher(*args, **kwargs):
        kwargs.pop('log_extra')
        push_kwargs.append(kwargs)
        return True

    yield send_user_chat_push.do_stuff()
    assert push_kwargs == [
        {
            'index': 1,
            'user_id': 'user_uber_android',
            'text': 'push ru',
            'destination': 'ya_uber',
            'event': 'gcm.notify_chat_message',
            'key': 'push_uber_2019-07-01T00:00:00',
            'destination_type': 'gcm',
            'payload': {
                'msg': 'push ru',
                'timestamp': '2019-07-01T00:00:00+0000',
                'deeplink': 'ubermlbv://chat',
                'id': UUID4,
                'new_messages': 2,
            },
        },
        {
            'destination': 'ya_yandex',
            'destination_type': 'apns',
            'event': 'apns.notify_chat_message',
            'index': 1,
            'key': 'push_yandex_2019-07-10T00:00:00',
            'payload': {
                'deeplink': 'yandextaxi://chat',
                'id': UUID4,
                'msg': 'push en',
                'new_messages': 3,
                'sound': 'default',
                'timestamp': '2019-07-10T00:00:00+0000',
            },
            'text': 'push en',
            'user_id': 'user_iphone',
        },
    ]
