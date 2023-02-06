# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.mixins.phone import (
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    KOLMOGOR_COUNTER_SESSIONS_CREATED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.test.consts import (
    TEST_DATETIME1,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge


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


@with_settings_hosts(
    PHONE_CONFIRMATION_CALL_ENABLED=True,
    PHONE_CONFIRMATION_FLASH_CALL_COUNTRIES=('by', 'ru',),
    PHONE_DIGITAL_PREFIXES_BLACKLIST=['7999', '7954'],
    TEST_VALID_PHONE_NUMBER_PREFIX='+70001',
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    OCTOPUS_GATES_WORKING_THRESHOLD=0.9,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    **mock_counters(
        CALLS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 2),
        PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
        UNTRUSTED_PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER=(24, 3600, 1),
    )
)
class TestPhoneNumberValidate(BaseBundleTestViews):
    default_url = '/1/bundle/validate/phone_id/'
    consumer = 'dev'
    http_headers = {
        'user_ip': TEST_USER_IP,
        'host': 'passport-test.yandex.ru',
    }

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

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_id': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID1
        self.http_query_args = {'track_id': self.track_id, 'phone_id': TEST_PHONE_ID1}
        self.setup_kolmogor()
        self.setup_blackbox()

    def setup_blackbox(self, uid=TEST_UID1, phone_number=TEST_PHONE_NUMBER, enabled=True):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **deep_merge(
                    dict(
                        uid=uid,
                        enabled=enabled,
                    ),
                    build_phone_bound(
                        TEST_PHONE_ID1,
                        phone_number.e164,
                        phone_created=TEST_DATETIME1,
                        phone_bound=TEST_DATETIME1,
                        phone_confirmed=TEST_DATETIME1,
                    ),
                )
            ),
        )

    def ok_response(self, valid_for_call=True, valid_for_flash_call=True):
        return {
            'status': 'ok',
            'valid_for_call': valid_for_call,
            'valid_for_flash_call': valid_for_flash_call,
        }

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def assert_track_ok(self, valid_for_call=True, valid_for_flash_call=True, phone_number=TEST_PHONE_NUMBER):
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_valid_for_call, valid_for_call)
        eq_(track.phone_valid_for_flash_call, valid_for_flash_call)
        eq_(track.phone_validated_for_call, phone_number.e164)

    def assert_graphite_log(self, call_status='calls_shut_down'):
        self.env.graphite_logger.assert_contains([
            {
                'call_status': call_status,
                'service': 'octopus-calls',
                'tskv_format': 'passport-log',
                'timestamp': self.env.graphite_logger.get_timestamp_mock(),
                'unixtime': self.env.graphite_logger.get_unixtime_mock(),
            },
        ], offset=-1)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, **self.ok_response())
        self.assert_track_ok()
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_no_track(self):
        rv = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(rv, ['track_id.empty'])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_ok__only_flashcall(self):
        self.setup_blackbox(phone_number=TEST_PHONE_NUMBER_BY)
        rv = self.make_request()
        self.assert_ok_response(rv, **self.ok_response(valid_for_call=False))
        self.assert_track_ok(valid_for_call=False, phone_number=TEST_PHONE_NUMBER_BY)
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_ok__number_with_no_country(self):
        self.setup_blackbox(phone_number=TEST_PHONE_NUMBER_NO_COUNTRY)
        rv = self.make_request()
        self.assert_ok_response(rv, **self.ok_response(valid_for_call=False, valid_for_flash_call=False))
        self.assert_track_ok(valid_for_call=False, valid_for_flash_call=False, phone_number=TEST_PHONE_NUMBER_NO_COUNTRY)
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_with_uid_ok(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_id': ['validate', 'by_uid']}))
        rv = self.make_request(query_args={'uid': TEST_UID2})
        self.assert_ok_response(rv, **self.ok_response())
        self.assert_track_ok()
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_wrong_phone_id(self):
        rv = self.make_request(query_args={'phone_id': TEST_PHONE_ID2})
        self.assert_error_response(rv, ['phone.not_found'])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_no_grant_for_uid(self):
        rv = self.make_request(query_args={'uid': TEST_UID2})
        self.assert_error_response(rv, ['access.denied'], status_code=403)
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_account_disabled(self):
        self.setup_blackbox(enabled=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_account_not_exists(self):
        self.setup_blackbox(uid=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.not_found'])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_no_uid_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_validate_for_call__fake_number_but_wrong_consumer(self):
        self.setup_blackbox(phone_number=TEST_FAKE_NUMBER)
        rv = self.make_request()
        self.assert_ok_response(rv, **self.ok_response(valid_for_call=False, valid_for_flash_call=False))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])
        self.assert_track_ok(valid_for_call=False, valid_for_flash_call=False, phone_number=TEST_FAKE_NUMBER)

    def test_validate_for_call__fake_number_ok(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='kopusha',
                grants={'phone_id': ['validate']},
            ),
        )
        self.setup_blackbox(phone_number=TEST_FAKE_NUMBER)
        rv = self.make_request(consumer='kopusha')
        self.assert_ok_response(rv, **self.ok_response(valid_for_call=True, valid_for_flash_call=True))
        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])
        self.assert_track_ok(valid_for_call=True, valid_for_flash_call=True, phone_number=TEST_FAKE_NUMBER)
