# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.mixins.phone import (
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    KOLMOGOR_COUNTER_SESSIONS_CREATED,
)
from passport.backend.core.builders.kolmogor import KolmogorPermanentError
from passport.backend.core.counters import (
    calls_per_ip,
    calls_per_phone,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import settings_context
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_USER_IP = '37.9.101.188'
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_PHONE_NUMBER_BY = PhoneNumber.parse('+375291234567')
TEST_PHONE_NUMBER_NO_COUNTRY = PhoneNumber.parse('+70001234567')
TEST_PHONE_FIXED_LINE_NUMBER = PhoneNumber.parse('+74955550101')
TEST_PHONE_BLACKLISTED_NUMBER = PhoneNumber.parse('+79547922245')
TEST_PHONE_USA = PhoneNumber.parse('+18779339101')
TEST_FAKE_NUMBER = PhoneNumber.parse('+70001000099')
TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'


class CommonValidateForCallTests(object):
    def setup_kolmogor(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])

    def assert_kolmogor_called(self, calls, with_shut_down=True):
        eq_(len(self.env.kolmogor.requests), calls)
        if with_shut_down:
            self.env.kolmogor.requests[-1].assert_properties_equal(
                method='POST',
                url='http://localhost/inc',
                post_args={'space': TEST_KOLMOGOR_KEYSPACE_FLAG, 'keys': 'calls_shut_down'},
            )

    def test_with_validate_for_call_with_track__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=True, valid_for_flash_call=True)

        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('sanitize_phone_number', track_id=self.track_id),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_valid_for_call)
        ok_(track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

    def test_with_validate_for_call__only_flashcall_with_track__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER_BY.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(status='ok', valid_for_call=False, valid_for_flash_call=True)

        self.assert_ok_response(rv, check_all=False, **expected_response)
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER_BY.e164)

    def test_validate_for_call__phone_limits__with_track__ok(self):
        buckets = calls_per_phone.get_counter()
        for _ in range(buckets.limit):
            buckets.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })
        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    track_id=self.track_id,
                    error='calls_limit.exceeded',
                ),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

    def test_validate_for_call__ip_limit__ok(self):
        buckets = calls_per_ip.get_counter(TEST_USER_IP)
        for _ in range(buckets.limit):
            buckets.incr(TEST_USER_IP)

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.e164, 'validate_for_call': 'yes'})
        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    error='calls_limit.exceeded',
                    track_id=self.track_id,
                ),
            ],
        )

    def test_validate_for_call__phone_not_mobile__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_FIXED_LINE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })
        expected_response = dict(self.ok_response(TEST_PHONE_FIXED_LINE_NUMBER), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    track_id=self.track_id,
                    sanitize_phone_result=TEST_PHONE_FIXED_LINE_NUMBER.masked_format_for_statbox,
                ),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_FIXED_LINE_NUMBER.e164)

    def test_validate_for_call__phone_blacklisted__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_BLACKLISTED_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })
        expected_response = dict(self.ok_response(TEST_PHONE_BLACKLISTED_NUMBER), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    track_id=self.track_id,
                    sanitize_phone_result=TEST_PHONE_BLACKLISTED_NUMBER.masked_format_for_statbox,
                ),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_BLACKLISTED_NUMBER.e164)

    def test_validate_for_call__phone_not_ru__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_USA.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })
        expected_response = dict(self.ok_response(TEST_PHONE_USA), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    track_id=self.track_id,
                    sanitize_phone_result=TEST_PHONE_USA.masked_format_for_statbox,
                ),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_USA.e164)

    def test_validate_for_call__already_reached__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_calls_ip_limit_reached = True

        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })
        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number', track_id=self.track_id),
        ])

    def test_validate_for_call__not_enabled__ok(self):
        with settings_context(PHONE_CONFIRMATION_CALL_ENABLED=False):
            rv = self.make_request(query_args={
                'phone_number': TEST_PHONE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            })

        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number', track_id=self.track_id),
        ])

    def test_validate_for_call__number_with_no_country__ok(self):
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER_NO_COUNTRY.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(TEST_PHONE_NUMBER_NO_COUNTRY), valid_for_call=False, valid_for_flash_call=False)

        self.assert_ok_response(rv, **expected_response)
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry(
                    'sanitize_phone_number',
                    track_id=self.track_id,
                    sanitize_phone_result=TEST_PHONE_NUMBER_NO_COUNTRY.masked_format_for_statbox,
                ),
            ],
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER_NO_COUNTRY.e164)

    def test_validate_for_call__fake_number_but_wrong_consumer(self):
        rv = self.make_request(
            query_args={
                'phone_number': TEST_FAKE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            },
        )
        expected_response = dict(self.ok_response(TEST_FAKE_NUMBER), valid_for_call=False, valid_for_flash_call=False)
        self.assert_ok_response(rv, **expected_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                track_id=self.track_id,
                sanitize_phone_result=TEST_FAKE_NUMBER.masked_format_for_statbox,
            ),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_FAKE_NUMBER.e164)

    def test_validate_for_call__fake_number_ok(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='kopusha',
                grants={'phone_number': ['validate']},
            ),
        )
        rv = self.make_request(
            query_args={
                'phone_number': TEST_FAKE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            },
            consumer='kopusha',
        )
        expected_response = dict(self.ok_response(TEST_FAKE_NUMBER), valid_for_call=True, valid_for_flash_call=True)
        self.assert_ok_response(rv, **expected_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                track_id=self.track_id,
                sanitize_phone_result=TEST_FAKE_NUMBER.masked_format_for_statbox,
            ),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_valid_for_call)
        ok_(track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_FAKE_NUMBER.e164)

    def test_validate_for_call__shut_down(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=False)
        self.assert_kolmogor_called(1, with_shut_down=False)
        self.assert_graphite_log()

    def test_validate_for_call__not_enough_sessions_ok(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 0,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=True, valid_for_flash_call=True)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=True)
        self.assert_kolmogor_called(2, with_shut_down=False)

    def test_validate_for_call__gates_failing_ok(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 10,
            KOLMOGOR_COUNTER_CALLS_FAILED: 9,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=False)
        self.assert_kolmogor_called(3)
        self.assert_graphite_log()

    def test_validate_for_call__available_ok(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 13,
            KOLMOGOR_COUNTER_CALLS_FAILED: 1,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=True, valid_for_flash_call=True)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=True)
        self.assert_kolmogor_called(2, with_shut_down=False)

    def test_validate_for_call__kolmogor_failed_ok(self):
        self.env.kolmogor.set_response_side_effect('get', KolmogorPermanentError)
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=True, valid_for_flash_call=True)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=True)
        self.assert_kolmogor_called(1, with_shut_down=False)

    def test_validate_for_call__kolmogor_failed_while_shut_down(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 10,
            KOLMOGOR_COUNTER_CALLS_FAILED: 10,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])
        self.env.kolmogor.set_response_side_effect('inc', KolmogorPermanentError)
        rv = self.make_request(query_args={
            'phone_number': TEST_PHONE_NUMBER.e164,
            'validate_for_call': 'yes',
            'track_id': self.track_id,
        })

        expected_response = dict(self.ok_response(), valid_for_call=False, valid_for_flash_call=False)

        self.assert_ok_response(rv, **expected_response)
        self.assert_track_ok(valid_for_call=False)
        self.assert_kolmogor_called(3, with_shut_down=True)
        self.assert_graphite_log()
