# -*- coding: utf-8 -*-
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test.base_test_data import TEST_USER_IP
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.common import merge_dicts


TEST_USER_COOKIES = 'yandexuid=cookie_yandexuid; fuid01=cookie_fuid01'
TEST_MAX_SMS_COUNT = 5
TEST_MAX_CHECKS_COUNT = 4


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts(
    SMS_VALIDATION_MAX_SMS_COUNT=TEST_MAX_SMS_COUNT,
    SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_MAX_CHECKS_COUNT,
    **mock_counters()
)
class ShowLimitsTestCase(BaseBundleTestViews):
    default_headers = build_headers()

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_limits']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'registration_limit_exceeded',
            action='registration_limit_exceeded',
            limit='registration_with_sms_per_ip',
            track_id=self.track_id,
            user_ip=TEST_USER_IP,
            counter_current_value=str(TEST_MAX_SMS_COUNT + 1),
            counter_limit_value=str(TEST_MAX_SMS_COUNT),
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/account/register/limits/?consumer=dev',
            data=data,
            headers=headers,
        )

    def test_show_limits__limits_are_not_reached__ok(self):
        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=TEST_MAX_SMS_COUNT,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([])

    def test_show_limits__sms_per_ip_for_consumer__ok(self):
        with settings_context(
            **mock_counters(
                DB_NAME_TO_COUNTER={'sms:ip_and_consumer:dev': (24, 3600, TEST_MAX_SMS_COUNT)},
            )
        ):
            counter = sms_per_ip.get_counter(TEST_USER_IP)
            for _ in range(counter.limit):
                counter.incr(TEST_USER_IP)

            response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=TEST_MAX_SMS_COUNT,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([])

    def test_show_limits__authorize_track__ok(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=TEST_MAX_SMS_COUNT,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )

    def test_show_limits__limits_are_near__returns_possible_sms_count(self):
        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        for _ in range(TEST_MAX_SMS_COUNT - 1):
            counter.incr(TEST_USER_IP)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for _ in range(TEST_MAX_CHECKS_COUNT - 2):
                track.phone_confirmation_confirms_count.incr()

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=1,
            confirmation_remained_count=2,
        )
        self.env.statbox.assert_has_written([])

    def test_show_limits__sms_send_limit_reached_in_track__returns_zero(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_count_limit_reached = True

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=0,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([])

    def test_show_limits__sms_limit_for_ip_reached_in_track__returns_zero(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_send_ip_limit_reached = True

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=0,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([])

    def test_show_limits__sms_limit_for_ip_reached_by_counter__returns_zero(self):
        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        for i in range(TEST_MAX_SMS_COUNT + 1):
            counter.incr(TEST_USER_IP)

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=0,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('registration_limit_exceeded'),
        ])

    def test_show_limits__confirmation_limit_reached_in_track__returns_zero(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_confirms_count_limit_reached = True

        response = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            response,
            sms_remained_count=TEST_MAX_SMS_COUNT,
            confirmation_remained_count=0,
        )
        self.env.statbox.assert_has_written([])

    def test_process_name_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self.make_request(self.query_params(), self.default_headers)

        self.assert_ok_response(
            rv,
            sms_remained_count=TEST_MAX_SMS_COUNT,
            confirmation_remained_count=TEST_MAX_CHECKS_COUNT,
        )
        self.env.statbox.assert_has_written([])

    def test_unsupported_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'some-process-name'

        rv = self.make_request(self.query_params(), self.default_headers)
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
        )
