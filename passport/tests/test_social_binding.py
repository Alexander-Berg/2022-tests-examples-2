# -*- coding: utf-8 -*-

import mock
from passport.backend.core.logging_utils.loggers.social_binding import (
    BindPhonishAccountByTrackStatboxEvent,
    SocialBindingLogEntry,
)
from passport.backend.core.test.consts import (
    TEST_TRACK_ID1,
    TEST_UID1,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils.utils import PassportTestCase
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


class TestSocialBindingLogEntry(PassportTestCase):
    def test(self):
        self.assertEqual(
            SocialBindingLogEntry(foo='bar').params,
            dict(
                foo='bar',
                timestamp=DatetimeNow(convert_to_datetime=True, format_='%d/%b/%Y:%H:%M:%S'),
                tskv_format='social-binding-log',
                unixtime=TimeNow(),
            ),
        )


class TestBindPhonishAccountByTrackStatboxEvent(PassportTestCase):
    def test(self):
        event = BindPhonishAccountByTrackStatboxEvent(
            ip=TEST_USER_IP1,
            track_id=TEST_TRACK_ID1,
            uid=TEST_UID1,
        )
        fake_logger = mock.Mock()
        event.log(fake_logger)
        fake_logger.log.assert_called_with(
            action='bind_phonish_account_by_track',
            ip=TEST_USER_IP1,
            track_id=TEST_TRACK_ID1,
            uid=TEST_UID1,
        )
