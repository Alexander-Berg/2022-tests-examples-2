# -*- coding: utf-8 -*-

from passport.backend.logbroker_client.account_events import events
from passport.backend.logbroker_client.core.events.filters import BasicFilter
from passport.backend.logbroker_client.core.handlers.utils import MessageChunk

from .utils import get_headers_event_file


class TestEvents(object):
    def test_account_unsubscribe_disk_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 83 passport 320738730 sid.rm 59|allaneifeld724 2a02:6b8:0:1427::1:24 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountUnsubscribeDiskEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 320738730
        assert events_res[0].name == 'sid.rm'
        assert events_res[0].timestamp == 3687
        assert events_res[0].sid == 59

    def test_account_otp_enabled_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 83 passport 320738730 info.totp enabled 2a02:6b8:0:1427::1:24 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountOtpEnabledEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 320738730
        assert events_res[0].name == 'account.otp_enabled'
        assert events_res[0].timestamp == 3687

    def test_account_otp_disabled_event(self):
        log_data = "1 1970-01-01T05:01:27.697373+04 83 passport 320738730 info.totp disabled 2a02:6b8:0:1427::1:24 - - - -\n"
        message = MessageChunk(get_headers_event_file('event'), log_data)
        events_filter = BasicFilter([events.AccountOtpDisabledEvent])
        events_res = events_filter.filter(message)

        assert events_res[0].uid == 320738730
        assert events_res[0].name == 'account.otp_disabled'
        assert events_res[0].timestamp == 3687
