# -*- coding: utf-8 -*-
import time

from nose.tools import ok_
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.phone.helpers import FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES
from passport.backend.core.builders.kolmogor import KolmogorPermanentError
from passport.backend.core.builders.octopus import (
    OctopusSessionNotFound,
    OctopusTemporaryError,
)
from passport.backend.core.builders.octopus.faker import octopus_session_log_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    TEST_CALL_SESSION_ID,
    TEST_FAKE_PHONE_NUMBER,
    TEST_PHONE_NUMBER,
)


TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'


@with_settings_hosts(
    CALL_STATUS_IN_PROGRESS='InProgress',
    CALL_STATUS_REJECTED='Rejected',
    CALL_STATUS_NO_ANSWER='NoAnswer',
    CALL_STATUS_UNAVAILABLE='Unavailable',
    CALL_STATUS_SUCCESS='Success',
    CALL_STATUS_INTERRUPTED='Interrupted',
    OCTOPUS_URL='http://localhost',
    OCTOPUS_TIMEOUT=2,
    OCTOPUS_RETRIES=1,
    OCTOPUS_AUTH_TOKEN='key',
    PHONE_CONFIRMATION_CHECK_TIMEOUT=10,
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
)
class TestConfirmCheckStatus(BaseBundleTestViews):
    default_url = '/1/bundle/phone/confirm/check_status/'
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'phone_bundle': ['base', 'confirm_by_call']}),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = dict(track_id=self.track_id)
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response())

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_track(self, call_session_id=TEST_CALL_SESSION_ID, first_called=None, last_called=None,
                    confirm_method='by_call'):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_first_called_at = first_called or int(time.time())
            track.phone_confirmation_last_called_at = last_called or int(time.time())
            if confirm_method:
                track.phone_confirmation_method = confirm_method
            if call_session_id:
                track.phone_call_session_id = call_session_id

    def assert_kolmogor_called(self, counter_key):
        self.env.kolmogor.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/inc',
            post_args={'space': TEST_KOLMOGOR_KEYSPACE_COUNTERS, 'keys': counter_key},
        )

    def test_invalid_state(self):
        self.setup_track(call_session_id=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)

    def test_empty_confirmation_method(self):
        self.setup_track(confirm_method=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)

    def test_bad_confirmation_method(self):
        self.setup_track(confirm_method='nonexistent_yet_confirmation_method')
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)

    def test_too_late(self):
        self.setup_track(last_called=int(time.time() - 11))
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.too_late'])
        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)

    def test_failed(self):
        self.setup_track()
        self.env.octopus.set_response_side_effect('get_session_log', OctopusSessionNotFound())
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.failed'])
        self.assert_kolmogor_called('calls_failed')

    def test_in_progress(self):
        self.setup_track()
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response(status='InProgress'))
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.not_ready'])
        ok_(not self.env.kolmogor.requests)

    def test_hangup(self):
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response(status='Rejected'))
        self.setup_track()
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.user_hangup'])
        ok_(not self.env.kolmogor.requests)

    def test_unavailable_by_call(self):
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response(status='Unavailable'))
        self.setup_track()
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.user_hangup'])
        ok_(not self.env.kolmogor.requests)

    def test_unavailable_by_flash_call(self):
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response(status='Unavailable'))
        self.setup_track(confirm_method='by_flash_call')
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.user_unavailable'])
        ok_(not self.env.kolmogor.requests)

    def test_success(self):
        self.setup_track()
        self.env.octopus.set_response_value('get_session_log', octopus_session_log_response(status='Success'))
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.finished'])
        ok_(not self.env.kolmogor.requests)

    def test_call_failed_inc_failed(self):
        self.env.kolmogor.set_response_side_effect('inc', KolmogorPermanentError)
        self.env.octopus.set_response_side_effect('get_session_log', OctopusTemporaryError())
        self.setup_track()
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.failed'])
        self.assert_kolmogor_called('calls_failed')

    @parameterized.expand([
        (None,),
        (TEST_PHONE_NUMBER.e164,),
    ])
    def test_octopus_fake_session__no_fake_number_in_track(self, phone_number):
        self.setup_track(call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = phone_number
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_octopus_fake_session__with_fake_number_in_track(self):
        self.setup_track(call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_FAKE_PHONE_NUMBER.e164
        rv = self.make_request()
        self.assert_error_response(rv, ['call_confirm.finished'])
        assert self.env.octopus.requests == []
