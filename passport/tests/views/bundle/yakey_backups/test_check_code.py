# -*- coding: utf-8 -*-
from nose.tools import ok_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONFIRMATION_CODE,
    TEST_PHONE_NUMBER,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import BaseYaKeyBackupTestView


@with_settings_hosts(
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
)
class TestCheckCodeTestCase(BaseYaKeyBackupTestView):
    default_url = '/1/bundle/yakey_backup/check_code/?consumer=mobileproxy'
    http_method = 'post'

    step = 'check_code'

    @property
    def http_query_args(self):
        return {
            'code': TEST_CONFIRMATION_CODE,
            'track_id': self.track_id,
        }

    def get_expected_response(self):
        response = {
            'track_id': self.track_id,
        }
        return response

    def test_no_track_error(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['track_id.empty'])
        self.env.statbox.assert_has_written([])

    def test_track_without_number_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'yakey_backup'
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], **self.get_expected_response())
        self.env.statbox.assert_has_written([])

    def test_wrong_process_name_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'restore'

        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_no_process_name_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original

        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_sms_not_sent(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.process_name = 'yakey_backup'

        resp = self.make_request()
        self.assert_error_response(resp, ['sms.not_sent'], **self.get_expected_response())
        self.env.statbox.assert_has_written([])

    def test_phone_already_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_is_confirmed = True
            track.process_name = 'yakey_backup'

        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], **self.get_expected_response())
        self.env.statbox.assert_has_written([])

    def test_confirmation_limit_exceeded(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.process_name = 'yakey_backup'
            for _ in range(settings.SMS_VALIDATION_MAX_CHECKS_COUNT):
                track.phone_confirmation_confirms_count.incr()

        resp = self.make_request()
        self.assert_error_response(resp, ['confirmations_limit.exceeded'], **self.get_expected_response())
        self.env.statbox.assert_has_written([])

    def test_code_invalid(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.process_name = 'yakey_backup'
            track.phone_confirmation_code = 'invalid code'

        resp = self.make_request()
        self.assert_error_response(resp, ['code.invalid'], **self.get_expected_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'check_code',
                error='code.invalid',
                code_checks_count='1',
            ),
        ])

    def test_checked_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE
            track.process_name = 'yakey_backup'

        ok_(not track.phone_confirmation_is_confirmed)

        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_expected_response())
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('succeeded'),
        ])
