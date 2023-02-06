# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.validate.common_phone_validate_tests.common_phone_call_tests import (
    CommonValidateForCallTests,
)
from passport.backend.core.counters import calls_per_phone
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.phone_number.phone_number import (
    mask_for_statbox,
    mask_phone_number,
    PhoneNumber,
)


TEST_USER_IP = '37.9.101.188'
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
    )


@with_settings_hosts(
    PHONE_CONFIRMATION_CALL_ENABLED=True,
    PHONE_DIGITAL_PREFIXES_BLACKLIST=['7999', '7954'],
    TEST_VALID_PHONE_NUMBER_PREFIX='+70001',
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    OCTOPUS_GATES_WORKING_THRESHOLD=0.9,
    PHONE_CONFIRMATION_FLASH_CALL_COUNTRIES=('by', 'ru',),
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
class TestPhoneNumberValidate(BaseBundleTestViews, CommonValidateForCallTests):
    default_url = '/1/bundle/mobile/validate/phone_number/'
    consumer = 'dev'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = {'track_id': self.track_id}
        self.setup_statbox_templates()

        self.phone_response = {
            'phone_number': {
                'e164': TEST_PHONE_NUMBER.e164,
                'original': TEST_PHONE_NUMBER.original,
                'international': TEST_PHONE_NUMBER.international,

                'masked_e164': mask_phone_number(TEST_PHONE_NUMBER.e164),
                'masked_original': mask_phone_number(TEST_PHONE_NUMBER.original),
                'masked_international': mask_phone_number(TEST_PHONE_NUMBER.international),
            },
        }
        self.setup_kolmogor()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

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

    def ok_response(self, number=TEST_PHONE_NUMBER):
        return {
            'status': 'ok',
            'phone_number': {
                'e164': number.e164,
                'original': number.original,
                'international': number.international,

                'masked_e164': mask_phone_number(number.e164),
                'masked_original': mask_phone_number(number.original),
                'masked_international': mask_phone_number(number.international),
            },
        }

    def assert_track_ok(self, valid_for_call=True):
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_valid_for_call, valid_for_call)
        eq_(track.phone_valid_for_flash_call, valid_for_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'sanitize_phone_number',
            action='sanitize_phone_number',
            track_id='',
            sanitize_phone_result=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def test_international_ok(self):
        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.e164})

        self.assert_ok_response(rv, **self.phone_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                track_id=self.track_id,
            ),
        ])
        track = self.track_manager.read(self.track_id)
        eq_(track.country, 'ru')
        ok_(not track.sanitize_phone_error)
        eq_(track.sanitize_phone_count.get(), 1)

        sanitize_phone_first_call = track.sanitize_phone_first_call
        sanitize_phone_last_call = track.sanitize_phone_last_call
        eq_(sanitize_phone_first_call, TimeNow())
        eq_(sanitize_phone_last_call, TimeNow())

        # Вызываем второй раз и смотрим, что счетчик увеличился,
        # а время первого вызова не изменилось
        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.e164})
        self.assert_ok_response(rv, **self.phone_response)
        track = self.track_manager.read(self.track_id)
        eq_(track.sanitize_phone_count.get(), 2)
        eq_(track.sanitize_phone_first_call, sanitize_phone_first_call)
        ok_(track.sanitize_phone_last_call > sanitize_phone_last_call)

    def test_local_ok(self):
        rv = self.make_request(query_args={'phone_number': '89261234567', 'country': 'ru'})

        self.phone_response['phone_number']['original'] = '89261234567'
        self.phone_response['phone_number']['masked_original'] = '8926*****67'
        self.assert_ok_response(rv, **self.phone_response)
        track = self.track_manager.read(self.track_id)
        eq_(track.country, 'ru')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                track_id=self.track_id,
            ),
        ])

    def test_invalid_number(self):
        rv = self.make_request(query_args={'phone_number': '26726472346234'})

        self.assert_error_response(rv, ['phone_number.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                sanitize_phone_result=mask_for_statbox('26726472346234'),
                sanitize_phone_error='badPhoneNumber',
                track_id=self.track_id,
            ),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(track.sanitize_phone_error)
        ok_(not track.country)

    def test_invalid_short_number(self):
        rv = self.make_request(query_args={'phone_number': '+712345'})

        self.assert_error_response(rv, ['phone_number.invalid'])
        self.env.statbox.assert_has_written([])

    def test_validate_for_call(self):
        rv = self.make_request(
            query_args={
                'phone_number': TEST_PHONE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            },
        )
        self.assert_ok_response(
            rv,
            valid_for_call=True,
            valid_for_flash_call=True,
            **self.phone_response
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number', track_id=self.track_id),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_valid_for_call)
        ok_(track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

    def test_calls_limit_exceeded(self):
        counter = calls_per_phone.get_counter()
        while not counter.hit_limit(TEST_PHONE_NUMBER.digital):
            counter.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(
            query_args={
                'phone_number': TEST_PHONE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            },
        )
        self.assert_ok_response(
            rv,
            valid_for_call=False,
            valid_for_flash_call=False,
            **self.phone_response
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                track_id=self.track_id,
                error='calls_limit.exceeded',
            ),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_valid_for_call)
        ok_(not track.phone_valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

    @parameterized.expand([
        (True, True),
        (True, False),
        (False, True),
        # при false,false тэги не влияют на принятие решения об ответе, это поведение проверено всеми остальными тестами
    ])
    def test_validate_considering_antifraud_tags(self, valid_for_call, valid_for_flash_call):
        af_tags = []
        if valid_for_call:
            af_tags.append('call')
        if valid_for_flash_call:
            af_tags.append('flash_call')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = af_tags

        rv = self.make_request(
            query_args={
                'phone_number': TEST_PHONE_NUMBER.e164,
                'validate_for_call': 'yes',
                'track_id': self.track_id,
            },
        )
        self.assert_ok_response(
            rv,
            valid_for_call=valid_for_call,
            valid_for_flash_call=valid_for_flash_call,
            **self.phone_response
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number', track_id=self.track_id),
        ])
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_valid_for_call, valid_for_call)
        eq_(track.phone_valid_for_flash_call, valid_for_flash_call)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)
