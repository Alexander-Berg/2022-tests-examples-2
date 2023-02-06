# -*- coding: utf-8 -*-
from passport.backend.logbroker_client.account_events.events import AccountOtpEnabledEvent
from passport.backend.logbroker_client.account_events.filter import ServiceFilter
from passport.backend.logbroker_client.core.events import events
from passport.backend.logbroker_client.core.utils import importobj


class TestServiceFilter(object):
    service_filter = ServiceFilter(
        events_classes=[
            importobj('passport.backend.logbroker_client.core.events.events.AccountDisableEvent'),
            importobj('passport.backend.logbroker_client.core.events.events.AccountEnableEvent'),
            importobj('passport.backend.logbroker_client.account_events.events.AccountOtpEnabledEvent'),
        ],
        sid=5,
    )

    def test_ok_without_sids(self):
        evnts = [
            events.SessionKillEvent(2, 123, 123),
            events.AccountEnableEvent(1, 123),
        ]
        result = self.service_filter.filter(evnts)
        assert len(result) == 1
        assert result[0].NAME == 'account.enable'

    def test_ok_with_sids(self):
        event1 = events.SessionKillEvent(2, 123, 123)
        event2 = events.AccountEnableEvent(1, 123)
        event3 = events.AccountDisableEvent(1, 123)
        event4 = AccountOtpEnabledEvent(1, 123)

        events_sids = {
            event1: [5, 44],
            event2: [44],
            event3: [5, 44],
            event4: [5],
        }

        result = self.service_filter.filter([event1, event2, event3, event4], events_sids)
        assert len(result) == 2
        assert result[0].NAME == 'account.disable'
        assert result[1].NAME == 'account.otp_enabled'
