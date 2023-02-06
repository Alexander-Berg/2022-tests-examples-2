# -*- coding: utf-8 -*-
import datetime
from unittest import TestCase

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.models.phones.phones import TrackedConfirmationInfo
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    datetime_to_unixtime,
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tracks.faker import FakeTrackManager


TEST_CONFIRMATION_CODE = '1234'
TEST_DATETIME_LONG_AGO = datetime.datetime(1970, 1, 2)
TEST_TIMESTAMP_LONG_AGO = int(datetime_to_unixtime(TEST_DATETIME_LONG_AGO))
TEST_TIMESTAMP_LONG_AGO_FRACTIONAL = TEST_TIMESTAMP_LONG_AGO + 0.4


@with_settings_hosts()
class TestTrackedConfirmationInfo(TestCase):
    def setUp(self):
        self.manager = FakeTrackManager()
        self.manager.start()
        self.track_manager, self.track_id = self.manager.get_manager_and_trackid('register')

    def tearDown(self):
        self.manager.stop()
        del self.manager
        del self.track_manager

    def setup_track(self, first_sent=TEST_TIMESTAMP_LONG_AGO, last_sent=TEST_TIMESTAMP_LONG_AGO,
                    code=TEST_CONFIRMATION_CODE, sent_count=0, checks_count=0,
                    is_confirmed=False, used_gate_ids=None):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_first_send_at = first_sent
            track.phone_confirmation_last_send_at = last_sent
            track.phone_confirmation_code = code
            for _ in range(sent_count):
                track.phone_confirmation_sms_count.incr()
            for _ in range(checks_count):
                track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_is_confirmed = is_confirmed
            track.phone_confirmation_used_gate_ids = used_gate_ids

    def test_eq(self):
        track = self.track_manager.read(self.track_id)
        conf_info_1 = TrackedConfirmationInfo(track)
        conf_info_2 = TrackedConfirmationInfo(track)
        eq_(conf_info_1, conf_info_2)

        # Нам неважно, какими гейтами уходили смс
        conf_info_1.yasms_used_gate_ids = '1'
        eq_(conf_info_1, conf_info_2)

        conf_info_1.code_first_sent = 123
        ok_(conf_info_1 != conf_info_2)

    def test_empty_track_ok(self):
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)
        ok_(not conf_info.code_value)
        ok_(not conf_info.code_first_sent)
        ok_(not conf_info.code_last_sent)
        eq_(conf_info.code_send_count, 0)
        eq_(conf_info.code_checks_count, 0)
        ok_(not conf_info.code_confirmed)
        ok_(not conf_info.yasms_used_gate_ids)

        conf_info.code_checks_count = 2
        conf_info.code_send_count = 2
        conf_info.code_value = TEST_CONFIRMATION_CODE
        conf_info.code_first_sent = datetime.datetime.now()
        conf_info.code_last_sent = datetime.datetime.now()
        conf_info.code_confirmed = True
        conf_info.yasms_used_gate_ids = '2,123'

        with self.track_manager.transaction(track=track).rollback_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        eq_(conf_info.track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE)
        eq_(track.phone_confirmation_sms_count.get(), 2)
        eq_(track.phone_confirmation_confirms_count.get(), 2)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_used_gate_ids, '2,123')

    def test_not_empty_track_ok(self):
        self.setup_track(sent_count=3, checks_count=2, used_gate_ids='12')
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)
        eq_(conf_info.code_value, TEST_CONFIRMATION_CODE)
        eq_(conf_info.code_first_sent, TEST_DATETIME_LONG_AGO)
        eq_(conf_info.code_last_sent, TEST_DATETIME_LONG_AGO)
        eq_(conf_info.code_send_count, 3)
        eq_(conf_info.code_checks_count, 2)
        eq_(conf_info.yasms_used_gate_ids, '12')
        ok_(not conf_info.code_confirmed)

        conf_info.code_send_count = 4
        conf_info.code_checks_count = 3
        conf_info.code_value = 'TEST_CONFIRMATION_CODE'
        conf_info.code_last_sent = DatetimeNow()
        conf_info.code_confirmed = True
        conf_info.yasms_used_gate_ids = '13'

        with self.track_manager.transaction(track=track).commit_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_first_send_at, str(TEST_TIMESTAMP_LONG_AGO))
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_code, 'TEST_CONFIRMATION_CODE')
        eq_(track.phone_confirmation_sms_count.get(), 4)
        eq_(track.phone_confirmation_confirms_count.get(), 3)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_used_gate_ids, '13')

    def test_reset_phone_ok(self):
        self.setup_track(sent_count=3, checks_count=2, is_confirmed=True, used_gate_ids='2,2,2')
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)
        conf_info.reset_phone()

        eq_(conf_info.code_checks_count, 0)
        ok_(not conf_info.code_confirmed)
        assert_is_none(conf_info.code_value)
        assert_is_none(conf_info.yasms_used_gate_ids)

        with self.track_manager.transaction(track=track).commit_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        assert_is_none(track.phone_confirmation_code)
        eq_(track.phone_confirmation_sms_count.get(default=0), 0)
        eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_used_gate_ids)
        eq_(track.phone_confirmation_first_send_at, str(TEST_TIMESTAMP_LONG_AGO))
        eq_(track.phone_confirmation_last_send_at, str(TEST_TIMESTAMP_LONG_AGO))

    def test_reset_phone_with_missing_code_first_last_sent_ok(self):
        self.setup_track(first_sent=None, last_sent=None)
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)

        conf_info.reset_phone()
        with self.track_manager.transaction(track=track).commit_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        assert_is_none(track.phone_confirmation_code)
        eq_(track.phone_confirmation_sms_count.get(default=0), 0)
        eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_used_gate_ids)
        assert_is_none(track.phone_confirmation_first_send_at)
        assert_is_none(track.phone_confirmation_last_send_at)

    def test_reset_phone_and_increase_counters_ok(self):
        self.setup_track(sent_count=3, checks_count=2, is_confirmed=True)
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)
        conf_info.reset_phone()

        conf_info.code_checks_count = 3
        conf_info.code_send_count = 10

        with self.track_manager.transaction(track=track).commit_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_sms_count.get(), 10)
        eq_(track.phone_confirmation_confirms_count.get(), 3)

    def test_save_code__unset_first_last_sent_value__ok(self):
        self.setup_track()
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)

        conf_info.code_first_sent = conf_info.code_last_sent = None
        with self.track_manager.transaction(track=track).commit_on_error():
            conf_info.save()

        track = self.track_manager.read(self.track_id)
        assert_is_none(track.phone_confirmation_first_send_at)
        assert_is_none(track.phone_confirmation_last_send_at)

    def test_fractional_timestamps_ok(self):
        self.setup_track(first_sent=TEST_TIMESTAMP_LONG_AGO_FRACTIONAL, last_sent=TEST_TIMESTAMP_LONG_AGO_FRACTIONAL)
        track = self.track_manager.read(self.track_id)
        conf_info = TrackedConfirmationInfo(track)
        eq_(conf_info.code_first_sent, TEST_DATETIME_LONG_AGO)
        eq_(conf_info.code_last_sent, TEST_DATETIME_LONG_AGO)
