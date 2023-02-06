# -*- coding: utf-8 -*-

from passport.backend.logbroker_client.avatars import events
from passport.backend.logbroker_client.core.events.filters import BasicFilter
from passport.backend.logbroker_client.core.handlers.utils import MessageChunk
from passport.backend.logbroker_client.core.tests.test_events.base import get_headers_event_file


HEADER = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/statbox/avatars.log',
    'server': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}


class TestEvents(object):
    def test_upload_avatar_event(self):
        log_data = "tskv\tmode=upload_by_url\tunixtime=3687\tuid=320738730\tavatar_to_upload=url\tuser_ip=127.0.0.1\n"
        message = MessageChunk(get_headers_event_file('passport_avatars'), log_data)
        events_filter = BasicFilter([events.UploadAvatarEvent])
        event = events_filter.filter(message)[0]

        assert event.uid == 320738730
        assert event.avatar_to_upload == 'url'
        assert event.timestamp == 3687
        assert event.user_ip == '127.0.0.1'
        assert not event.skip_if_set

    def test_upload_avatar_with_skip_if_set_event(self):
        log_data = "tskv\tmode=upload_by_url\tunixtime=3687\tuid=320738730\tavatar_to_upload=url\tuser_ip=127.0.0.1\tskip_if_set=1\n"
        message = MessageChunk(get_headers_event_file('passport_avatars'), log_data)
        events_filter = BasicFilter([events.UploadAvatarEvent])
        event = events_filter.filter(message)[0]

        assert event.uid == 320738730
        assert event.avatar_to_upload == 'url'
        assert event.timestamp == 3687
        assert event.user_ip == '127.0.0.1'
        assert event.skip_if_set
