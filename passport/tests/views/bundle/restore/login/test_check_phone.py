# -*- coding: utf-8 -*-
import json
import random

import mock
from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_LOGIN_RESTORE
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_GPS_PACKAGE_HASH,
    TEST_GPS_PACKAGE_NAME,
    TEST_GPS_PUBLIC_KEY,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_SMS_TEXT,
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
)
from passport.backend.api.views.bundle.restore.login.controllers import (
    RESTORE_STATE_PHONE_CONFIRMED,
    RESTORE_STATE_SUBMITTED,
)
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.octopus import OctopusPermanentError
from passport.backend.core.builders.octopus.faker import octopus_response
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import (
    calls_per_ip,
    calls_per_phone,
    login_restore_counter,
    sms_per_ip,
    sms_per_phone,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_base import (
    CommonTestsMixin,
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    LoginRestoreBaseTestCase,
    TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    TEST_KOLMOGOR_KEYSPACE_FLAG,
)


TEST_BY_CALL_VALIDATION_CODE = '123456'
TEST_BY_CALL_VALIDATION_CODE_BY_3 = '123 456'
TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE = '+7 123456XXXX'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    FLASH_CALL_NUMBERS=['+71234561234'],
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_RETRIES=1,
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_URL='http://localhost',
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_VALIDATION_CODE_LENGTH=6,
    PHONE_VALIDATION_MAX_CALLS_COUNT=10,
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckPhoneByFlashCallTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'check_phone'

    default_url = '/1/bundle/restore/login/check_phone/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreCheckPhoneByFlashCallTestCase, self).setUp()

        self.http_query_args = dict(
            track_id=self.track_id,
            phone_number=TEST_PHONE_LOCAL_FORMAT,
            display_language='ru',
            country='ru',
            confirm_method='by_flash_call',
        )

        self._random_faker = mock.Mock(wraps=random.SystemRandom)
        self._random_faker_patch = mock.patch(
            u'passport.backend.api.views.bundle.phone.helpers.random.SystemRandom',
            self._random_faker,
        )
        self._random_faker_patch.start()

        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))

        self.orig_track.phone_valid_for_flash_call = True

        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def tearDown(self):
        self._random_faker_patch.stop()
        del self._random_faker_patch
        del self._random_faker
        super(LoginRestoreCheckPhoneByFlashCallTestCase, self).tearDown()

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_PHONE_CONFIRMED}
    test_action_not_required_options = None
    invalid_phone_increases_ip_counter = True

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED,
                         process_name=PROCESS_LOGIN_RESTORE, is_captcha_checked=True,
                         is_captcha_recognized=True, **params):
        super(LoginRestoreCheckPhoneByFlashCallTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=is_captcha_checked,
            is_captcha_recognized=is_captcha_recognized,
            phone_valid_for_flash_call=True,
            **params
        )

    def setup_statbox_templates(self):
        super(LoginRestoreCheckPhoneByFlashCallTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['pharma_allowed'],
            _exclude=['action'],
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['pharma_denied'],
            _exclude=['action'],
            operation='confirm',
        )

    def test_invalid_previous_confirm_method(self):
        self.set_track_values(
            phone_confirmation_method='by_call',
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(self.env.kolmogor.requests, [])

    def test_captcha_not_passed(self):
        """Капча не пройдена"""
        self.set_track_values(is_captcha_recognized=False)

        resp = self.make_request()

        self.assert_error_response(resp, ['user.not_verified'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_track_limit_exceeded(self):
        """Аккаунт найден, превышен лимит отправки СМС на номер"""
        self.set_track_values(
            phone_confirmation_calls_count_limit_reached=True,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_flash_call',
            phone_confirmation_calls_count_limit_reached=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_flash_call=True,
        )

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('pharma_allowed'),
            ],
        )

        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_phone_limit_exceeded(self):
        """Аккаунт найден, превышен лимит звонков на телефон"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        buckets = calls_per_phone.get_counter()
        for _ in range(buckets.limit):
            buckets.incr(TEST_PHONE_OBJECT.digital)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_calls_count_limit_reached=True,
            phone_confirmation_method='by_flash_call',
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_flash_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='calls_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                operation='confirm',
                _exclude=['action', 'reason'],
            ),
        ])
        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_ip_rate_exceeded(self):
        """Аккаунт найден, превышена частота звонков на номер"""
        self.set_track_values(
            phone_confirmation_last_send_at=str(int(time.time())),
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        buckets = calls_per_ip.get_counter(TEST_IP)
        for _ in range(buckets.limit):
            buckets.incr(TEST_IP)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_flash_call',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_flash_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='calls_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                operation='confirm',
                _exclude=['action', 'reason'],
            ),
        ])
        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_shut_down(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['calls.shut_down'])
        self.assert_kolmogor_called(1, with_inc=False)
        eq_(self.env.octopus.requests, [])

    def test_octopus_error(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        self.env.octopus.set_response_side_effect('create_flash_call_session', OctopusPermanentError())

        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['create_call.failed'])
        self.assert_kolmogor_called(3, keys=KOLMOGOR_COUNTER_CALLS_FAILED)

    def test_check_phone_passed(self):
        """Аккаунт найден, код выслан"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            code_length=4,  # длина кода в FLASH_CALL_NUMBERS равна 4
            calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code='1234',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_call_session_id='123',
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_flash_call',
            phone_confirmation_calls_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_flash_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'flash_call',
                operation='confirm',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        eq_(len(self.env.octopus.requests), 1)
        self.assert_blackbox_called()
        self.assert_kolmogor_called(3)

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
        # Глобальные счетчики отправки звонков обновились
        eq_(calls_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        eq_(calls_per_phone.get_counter().get(TEST_PHONE_OBJECT.digital), 1)

    def test_check_phone_passed_with_another_phone(self):
        """Аккаунт найден, код выслан на другой номер"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=12345,
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_calls_count=3,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            code_length=4,
            calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code='1234',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_call_session_id='123',
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_flash_call',
            phone_confirmation_last_send_at='12345',
            phone_confirmation_calls_count=1,
            is_successful_phone_passed=False,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_flash_call=True,

        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_sms_resend='0'),
            self.env.statbox.entry(
                'flash_call',
                operation='confirm',
                is_sms_resend='0',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='0',
            ),
        ])
        eq_(len(self.env.octopus.requests), 1)
        self.assert_blackbox_called()
        self.assert_kolmogor_called(3)

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
        # Глобальные счетчики отправки звонков обновились
        eq_(calls_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        eq_(calls_per_phone.get_counter().get(TEST_PHONE_OBJECT.digital), 1)

    def test_pharma_denied(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(
            self.env.antifraud_api.requests[0],
            extra_features=dict(
                phone_confirmation_method='by_flash_call',
                phone_confirmation_language='ru',
            ),
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_RETRIES=1,
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_URL='http://localhost',
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_VALIDATION_CODE_LENGTH=6,
    PHONE_VALIDATION_MAX_CALLS_COUNT=10,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        # SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        # PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckPhoneByCallTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'check_phone'

    default_url = '/1/bundle/restore/login/check_phone/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreCheckPhoneByCallTestCase, self).setUp()

        self.http_query_args = dict(
            track_id=self.track_id,
            phone_number=TEST_PHONE_LOCAL_FORMAT,
            display_language='ru',
            country='ru',
            confirm_method='by_call',
        )

        self._generate_random_code_mock = mock.Mock(return_value=TEST_BY_CALL_VALIDATION_CODE)
        self._generate_random_code_patch = mock.patch(
            'passport.backend.api.views.bundle.phone.helpers.generate_random_code',
            self._generate_random_code_mock,
        )
        self._generate_random_code_patch.start()

        self.env.octopus.set_response_value('create_session', octopus_response(123))

        self.orig_track.phone_valid_for_call = True

        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def tearDown(self):
        self._generate_random_code_patch.stop()
        del self._generate_random_code_patch
        del self._generate_random_code_mock
        super(LoginRestoreCheckPhoneByCallTestCase, self).tearDown()

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_PHONE_CONFIRMED}
    test_action_not_required_options = None
    invalid_phone_increases_ip_counter = True

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED,
                         process_name=PROCESS_LOGIN_RESTORE, is_captcha_checked=True,
                         is_captcha_recognized=True, **params):
        super(LoginRestoreCheckPhoneByCallTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=is_captcha_checked,
            is_captcha_recognized=is_captcha_recognized,
            phone_valid_for_call=True,
            **params
        )

    def setup_statbox_templates(self):
        super(LoginRestoreCheckPhoneByCallTestCase, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['pharma_allowed'],
            _exclude=['action'],
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['pharma_denied'],
            _exclude=['action'],
            operation='confirm',
        )

    def test_invalid_previous_confirm_method(self):
        self.set_track_values(
            phone_confirmation_method='by_flash_call',
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        eq_(self.env.kolmogor.requests, [])

    def test_captcha_not_passed(self):
        """Капча не пройдена"""
        self.set_track_values(is_captcha_recognized=False)

        resp = self.make_request()

        self.assert_error_response(resp, ['user.not_verified'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_track_limit_exceeded(self):
        """Аккаунт найден, превышен лимит отправки СМС на номер"""
        self.set_track_values(
            phone_confirmation_calls_count_limit_reached=True,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            phone_confirmation_calls_count_limit_reached=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_call=True,
        )
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('pharma_allowed'),
            ],
        )
        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_phone_limit_exceeded(self):
        """Аккаунт найден, превышен лимит звонков на телефон"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        buckets = calls_per_phone.get_counter()
        for _ in range(buckets.limit):
            buckets.incr(TEST_PHONE_OBJECT.digital)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_calls_count_limit_reached=True,
            phone_confirmation_method='by_call',
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='calls_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                operation='confirm',
                _exclude=['action', 'reason'],
            ),
        ])
        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_per_ip_rate_exceeded(self):
        """Аккаунт найден, превышена частота звонков на номер"""
        self.set_track_values(
            phone_confirmation_last_send_at=str(int(time.time())),
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        buckets = calls_per_ip.get_counter(TEST_IP)
        for _ in range(buckets.limit):
            buckets.incr(TEST_IP)

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=True,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='calls_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                operation='confirm',
                _exclude=['action', 'reason'],
            ),
        ])
        self.assert_blackbox_called()
        self.assert_kolmogor_called(2, with_inc=False)

    def test_calls_shut_down(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['calls.shut_down'])
        self.assert_kolmogor_called(1, with_inc=False)
        eq_(self.env.octopus.requests, [])

    def test_octopus_error(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        self.env.octopus.set_response_side_effect('create_session', OctopusPermanentError())

        resp = self.make_request()
        self.assert_error_response(resp, error_codes=['create_call.failed'])

    def test_check_phone_passed(self):
        """Аккаунт найден, код выслан"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            code_length=6,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code=TEST_BY_CALL_VALIDATION_CODE_BY_3,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_call_session_id='123',
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            phone_confirmation_calls_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_call=True,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'call_with_code',
                operation='confirm',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        eq_(len(self.env.octopus.requests), 1)
        self.assert_blackbox_called()
        self.assert_kolmogor_called(3)

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
        # Глобальные счетчики отправки звонков обновились
        eq_(calls_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        eq_(calls_per_phone.get_counter().get(TEST_PHONE_OBJECT.digital), 1)

    def test_check_phone_passed_with_another_phone(self):
        """Аккаунт найден, код выслан на другой номер"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=reversed(TEST_BY_CALL_VALIDATION_CODE_BY_3),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=12345,
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_calls_count=3,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            code_length=6,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code=TEST_BY_CALL_VALIDATION_CODE_BY_3,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_call_session_id='123',
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_call',
            phone_confirmation_last_send_at='12345',
            phone_confirmation_calls_count=1,
            is_successful_phone_passed=False,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_valid_for_call=True,

        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_sms_resend='0'),
            self.env.statbox.entry(
                'call_with_code',
                operation='confirm',
                is_sms_resend='0',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='0',
            ),
        ])
        eq_(len(self.env.octopus.requests), 1)
        self.assert_blackbox_called()
        self.assert_kolmogor_called(3)

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
        # Глобальные счетчики отправки звонков обновились
        eq_(calls_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        eq_(calls_per_phone.get_counter().get(TEST_PHONE_OBJECT.digital), 1)

    def test_pharma_denied(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request()

        self.assert_error_response(resp, ['calls_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(
            self.env.antifraud_api.requests[0],
            extra_features=dict(
                phone_confirmation_method='by_call',
                phone_confirmation_language='ru',
            ),
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    SMS_VALIDATION_CODE_LENGTH=6,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckPhoneBySmsTestCase(LoginRestoreBaseTestCase, CommonTestsMixin):

    restore_step = 'check_phone'

    default_url = '/1/bundle/restore/login/check_phone/?consumer=dev'

    http_method = 'POST'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreCheckPhoneBySmsTestCase, self).setUp()
        self.http_query_args = dict(
            track_id=self.track_id,
            phone_number=TEST_PHONE_LOCAL_FORMAT,
            display_language='ru',
            country='ru',
        )
        self._generate_random_code_mock = mock.Mock(return_value=TEST_VALIDATION_CODE)
        self._generate_random_code_patch = mock.patch(
            'passport.backend.api.yasms.utils.generate_random_code',
            self._generate_random_code_mock,
        )
        self._generate_random_code_patch.start()
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def tearDown(self):
        self._generate_random_code_patch.stop()
        del self._generate_random_code_patch
        del self._generate_random_code_mock
        super(LoginRestoreCheckPhoneBySmsTestCase, self).tearDown()

    @property
    def sms_template(self):
        return TEST_SMS_TEXT

    def assert_sms_sent(self, code=TEST_VALIDATION_CODE):
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({
            'identity': 'send_confirmation_code',
            'phone': TEST_PHONE_OBJECT.e164,
            'text': self.sms_template,
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(code)}).encode('utf-8'),
        })

    def set_track_values(self, restore_state=RESTORE_STATE_SUBMITTED,
                         process_name=PROCESS_LOGIN_RESTORE, is_captcha_checked=True,
                         is_captcha_recognized=True, **params):
        super(LoginRestoreCheckPhoneBySmsTestCase, self).set_track_values(
            process_name=process_name,
            restore_state=restore_state,
            is_captcha_required=True,
            is_captcha_checked=is_captcha_checked,
            is_captcha_recognized=is_captcha_recognized,
            **params
        )

    test_invalid_track_state_options = {'restore_state': RESTORE_STATE_PHONE_CONFIRMED}
    test_action_not_required_options = None
    invalid_phone_increases_ip_counter = True

    def test_captcha_not_passed(self):
        """Капча не пройдена"""
        self.set_track_values(is_captcha_recognized=False)

        resp = self.make_request()

        self.assert_error_response(resp, ['user.not_verified'])
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])

    def test_sms_per_phone_limit_exceeded(self):
        """Аккаунт найден, превышен лимит отправки СМС на номер"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        buckets = sms_per_phone.get_per_phone_buckets()
        for _ in range(buckets.limit):
            buckets.incr(TEST_PHONE_OBJECT.digital)

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='sms_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_called()

    def test_sms_per_ip_limit_exceeded(self):
        """Аккаунт найден, превышен лимит отправки СМС на IP"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        buckets = sms_per_ip.get_counter(TEST_IP)
        for _ in range(buckets.limit):
            buckets.incr(TEST_IP)

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='sms_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                reason='ip_limit',
            ),
        ])
        self.assert_blackbox_called()

    def test_sms_per_ip_rate_exceeded(self):
        """Аккаунт найден, превышена частота отправки СМС"""
        self.set_track_values(
            phone_confirmation_last_send_at=str(int(time.time())),
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'])
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='sms_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                reason='rate_limit',
            ),
        ])
        self.assert_blackbox_called()

    def test_yasms_failures(self):
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        errors = [
            (
                yasms_exceptions.YaSmsError('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsAccessDenied('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsLimitExceeded('error message'),
                {u'reason': u'yasms_phone_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsPermanentBlock('error message'),
                {u'errors': [u'phone.blocked']},
                'phone.blocked',
            ),
            (
                yasms_exceptions.YaSmsTemporaryBlock('error message'),
                {u'reason': u'yasms_rate_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsUidLimitExceeded('error message'),
                {u'reason': u'yasms_uid_limit', u'errors': [u'sms_limit.exceeded']},
                'sms_limit.exceeded',
            ),
            (
                yasms_exceptions.YaSmsSecureNumberNotAllowed('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsSecureNumberExists('error message'),
                {u'errors': [u'exception.unhandled']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsPhoneNumberValueError('error message'),
                {u'errors': [u'number.invalid']},
                'sms.isnt_sent',
            ),
            (
                yasms_exceptions.YaSmsDeliveryError('error message'),
                {u'errors': [u'backend.yasms_failed']},
                'sms.isnt_sent',
            ),
        ]

        for index, (yasms_error, info, code) in enumerate(errors):
            self.set_track_values(
                phone_confirmation_code=None,
                phone_confirmation_is_confirmed=False,
                phone_confirmation_last_send_at=None,
                phone_confirmation_phone_number_original=None,
                phone_confirmation_sms_count=0,
            )
            self.env.yasms.set_response_side_effect('send_sms', yasms_error)

            resp = self.make_request()

            self.assert_error_response(resp, info['errors'])
            entry_kwargs = dict(
                error=code,
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            )
            if 'reason' in info:
                entry_kwargs['reason'] = info['reason']
            self.env.statbox.assert_contains(
                [
                    self.env.statbox.entry('pharma_allowed'),
                    self.env.statbox.entry('finished_with_error_with_sms', **entry_kwargs),
                ],
                offset=index,
            )
            self.assert_blackbox_called(call_index=index)

    def test_check_phone_passed_calls_shut_down(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)

        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )

    def test_check_phone_passed(self):
        """Аккаунт найден, код выслан"""
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('code_sent'),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_sms_sent()
        self.assert_blackbox_called()

        ip_buckets = login_restore_counter.get_per_ip_buckets()
        eq_(ip_buckets.get(TEST_IP), 0)
        phone_buckets = login_restore_counter.get_per_phone_buckets()
        eq_(phone_buckets.get(TEST_PHONE_OBJECT.digital), 0)
        # Глобальные счетчики отправки СМС обновились
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        eq_(sms_per_phone.get_per_phone_buckets().get(TEST_PHONE_OBJECT.digital), 1)

    def test_check_phone_passed_code_resent_captcha_not_passed(self):
        """Аккаунт найден, код выслан повторно на тот же номер, капчу не проверяем"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=12345,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_sms_count=3,
            is_captcha_recognized=False,
            is_captcha_checked=False,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request(query_args=dict(phone_number=TEST_PHONE))  # В другом формате

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=4,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE,
            phone_confirmation_method='by_sms',
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_sms_resend='1'),
            self.env.statbox.entry(
                'code_sent',
                sms_count='4',
                is_sms_resend='1',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='1',
            ),
        ])
        self.assert_sms_sent()
        self.assert_blackbox_called()

    def test_check_phone_passed_with_another_phone(self):
        """Аккаунт найден, код выслан на другой номер"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=12345,
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_sms_count=3,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            phone_confirmation_code=str(TEST_VALIDATION_CODE),  # На новый номер выслали другой код
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,  # Число кодов сбросили
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_sms_resend='0'),
            self.env.statbox.entry(
                'code_sent',
                is_sms_resend='0',
            ),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='0',
            ),
        ])
        self.assert_sms_sent()
        self.assert_blackbox_called()

    def test_phone_changed_with_sending_error__track_state_updated(self):
        """Телефон изменили, при ошибке отправки важно полноценно обновить состояние в треке"""
        self.set_track_values(
            phone_confirmation_last_send_at=str(int(time.time())),
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_sms_count=3,
            is_captcha_checked=True,
            is_captcha_recognized=True,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'])
        self.assert_track_updated(
            # Новый номер сохранили, но код и счетчики сбросили
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_code=None,
            phone_confirmation_sms_count=0,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='sms_limit.exceeded',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='0',
                reason='rate_limit',
            ),
        ])
        self.assert_blackbox_called()

    def test_check_phone_passed_after_sending_error_on_phone_change(self):
        """Телефон изменили, произошла ошибка отправки, после чего отправка успешна"""
        self.set_track_values(
            phone_confirmation_last_send_at='12345',
            country='ru',
            display_language='ru',
            phone_confirmation_is_confirmed=False,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_code=None,
            phone_confirmation_sms_count=0,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_sms_resend='1'),
            self.env.statbox.entry('code_sent', is_sms_resend='1'),
            self.env.statbox.entry(
                'passed',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='1',
            ),
        ])
        self.assert_sms_sent()
        self.assert_blackbox_called()

    def test_check_phone_captcha_not_passed_with_another_phone(self):
        """Аккаунт найден, код не выслан на другой номер т.к. капча не пройдена"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at='12345',
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_sms_count=3,
            is_captcha_checked=False,
            is_captcha_recognized=False,
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['user.not_verified'],
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='user.not_verified',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                is_sms_resend='0',
            ),
        ])

    def test_save_used_gate_ids(self):
        self.set_track_values()
        accounts = [self.build_account()]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(used_gate_ids=[1]),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_confirmation_used_gate_ids='1',
        )
        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)

    def test_use_saved_gate_ids(self):
        self.set_track_values(phone_confirmation_used_gate_ids='1')
        accounts = [self.build_account()]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_confirmation_used_gate_ids=None,
        )
        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({'previous_gates': '1'})

    def test_phone_changed_gates_cleared(self):
        """Аккаунт найден, код выслан на другой номер"""
        self.set_track_values(
            country='ru',
            display_language='ru',
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_send_at=12345,
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
            phone_confirmation_sms_count=3,
            phone_confirmation_used_gate_ids='12',
        )
        accounts = [self.build_account()]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            resend_timeout=10,
            code_length=6,
        )
        self.assert_track_updated(
            phone_confirmation_code=str(TEST_VALIDATION_CODE),  # На новый номер выслали другой код
            phone_confirmation_is_confirmed=False,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_method='by_sms',
            phone_confirmation_sms_count=1,  # Число кодов сбросили
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_confirmation_used_gate_ids=None,
        )
        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)

    def test_pharma_denied(self):
        self.set_track_values()
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])


@with_settings_hosts(
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT=TEST_GPS_PUBLIC_KEY,
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    BLACKBOX_URL='localhost',
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckPhoneWithSmsRetrieverTestCase(LoginRestoreCheckPhoneBySmsTestCase):
    """Тесты с форматированием SMS под SmsRetriever в Андроиде"""

    def setUp(self):
        super(LoginRestoreCheckPhoneWithSmsRetrieverTestCase, self).setUp()

        # проверим согласованность настроек
        eq_(hash_android_package(TEST_GPS_PACKAGE_NAME, TEST_GPS_PUBLIC_KEY), TEST_GPS_PACKAGE_HASH)

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name=TEST_GPS_PACKAGE_NAME,
                sms_retriever='1',
            ),
        )

    @property
    def sms_template(self):
        return format_for_android_sms_retriever(
            TEST_SMS_RETRIEVER_TEXT,
            TEST_GPS_PACKAGE_HASH,
        )

    def set_track_values(self, **params):
        return super(LoginRestoreCheckPhoneWithSmsRetrieverTestCase, self).set_track_values(
            gps_package_name=TEST_GPS_PACKAGE_NAME,
            **params
        )
