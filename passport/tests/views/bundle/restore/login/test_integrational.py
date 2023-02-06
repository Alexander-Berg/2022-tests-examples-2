# -*- coding: utf-8 -*-
import random

import mock
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.mixins.phone import (
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    KOLMOGOR_COUNTER_SESSIONS_CREATED,
)
from passport.backend.api.views.bundle.restore.login.controllers import (
    RESTORE_STATE_PHONE_CONFIRMED,
    RESTORE_STATE_SUBMITTED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_phone_bindings_response
from passport.backend.core.builders.octopus.faker import (
    octopus_response,
    octopus_session_log_response,
    TEST_STATUS_IN_PROGRESS,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .test_base import (
    LoginRestoreBaseTestCase,
    TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    TEST_KOLMOGOR_KEYSPACE_FLAG,
)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    SMS_VALIDATION_RESEND_TIMEOUT=10,
    PHONE_CONFIRMATION_FLASH_CALL_COUNTRIES=('ru',),
    PHONE_VALIDATION_CODE_LENGTH=6,
    PHONE_VALIDATION_MAX_CALLS_COUNT=10,
    FLASH_CALL_NUMBERS=['+71234561234'],
    PHONE_CONFIRMATION_CALL_ENABLED=True,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class LoginRestoreCheckPhoneByFlashCallIntegrationalTestCase(LoginRestoreBaseTestCase):
    restore_step = 'STUB'

    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
    )

    def setUp(self):
        super(LoginRestoreCheckPhoneByFlashCallIntegrationalTestCase, self).setUp()

        self.http_query_args = dict(
            track_id=self.track_id,
            phone_number=TEST_PHONE_LOCAL_FORMAT,
            display_language='ru',
            country='ru',
            confirm_method='by_flash_call',
        )

        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'login_restore': ['base'],
                    'phone_number': ['validate'],
                    'phone_bundle': ['base', 'confirm_by_call'],
                },
            ),
        )

        # для смс
        self._generate_yasms_random_code_mock = mock.Mock(return_value=TEST_VALIDATION_CODE)
        self._generate_yasms_random_code_patch = mock.patch(
            'passport.backend.api.yasms.utils.generate_random_code',
            self._generate_yasms_random_code_mock,
        )
        self._generate_yasms_random_code_patch.start()

        # для flash call
        self._random_faker = mock.Mock(wraps=random.SystemRandom)
        self._random_faker_patch = mock.patch(
            u'passport.backend.api.views.bundle.phone.helpers.random.SystemRandom',
            self._random_faker,
        )
        self._random_faker_patch.start()

        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))

        # для звонка с диктовкой
        self._generate_random_code_mock = mock.Mock(return_value='123456')
        self._generate_random_code_patch = mock.patch(
            'passport.backend.api.views.bundle.phone.helpers.generate_random_code',
            self._generate_random_code_mock,
        )
        self._generate_random_code_patch.start()

        self.env.octopus.set_response_value('create_session', octopus_response(123))
        self.env.octopus.set_response_side_effect('get_session_log', [
            octopus_session_log_response(status=TEST_STATUS_IN_PROGRESS),
            octopus_session_log_response(status='Success'),
        ])

        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.kolmogor.set_response_value('inc', 'OK')
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters] * 2)

    def tearDown(self):
        self._random_faker_patch.stop()
        del self._random_faker_patch
        del self._random_faker
        self._generate_random_code_patch.stop()
        del self._generate_random_code_patch
        del self._generate_random_code_mock
        self._generate_yasms_random_code_patch.stop()
        del self._generate_yasms_random_code_patch
        del self._generate_yasms_random_code_mock
        super(LoginRestoreCheckPhoneByFlashCallIntegrationalTestCase, self).tearDown()

    def setup_phone_bindings(self, accounts):
        phone_bindings = []
        for account in accounts:
            account_bindings = account.get('phone_bindings', [])
            for binding in account_bindings:
                if binding['number'] == TEST_PHONE_OBJECT.e164:
                    phone_bindings.append(
                        dict(
                            binding,
                            uid=account['uid'],
                        ),
                    )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )

    def run_integrational_scenario(self, confirm_method, code, human_readable_code):
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        # начинаем процесс восстановления логина
        rv = self.make_request(
            '/1/bundle/restore/login/submit/?consumer=dev',
            method='POST',
        )
        self.assert_ok_response(rv, track_id=self.track_id)

        self.assert_track_updated(
            is_created=True,
            created=TimeNow(),
            is_captcha_required=True,
            restore_state=RESTORE_STATE_SUBMITTED,
            process_name='login_restore',
            phone_operation_confirmations=[],
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        # проверяем состояние восстановления
        rv = self.make_request(
            '/1/bundle/restore/login/get_state/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
            },
        )
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            retpath=None,
            restore_state=RESTORE_STATE_SUBMITTED,
        )

        # допустим, что пользователь прошёл каптчу
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        # попытка подтвердить телефон по звонку, нужна предварительная валидация телефона для звонка
        rv = self.make_request(
            '/1/bundle/restore/login/check_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'display_language': 'ru',
                'confirm_method': confirm_method,
            },
        )
        self.assert_error_response(rv, ['track.invalid_state'])

        # валидируем телефон для звонков
        rv = self.make_request(
            '/1/bundle/validate/phone_number/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'validate_for_call': '1',
            },
        )
        self.assert_ok_response(
            rv,
            check_all=False,
            valid_for_call=True,
            valid_for_flash_call=True,
        )
        self.assert_track_updated(
            # сайд-эффект мнимого прохождения каптчи, см. выше по тесту
            is_captcha_checked=True,
            is_captcha_recognized=True,
            # всё что ниже - результат вызова ручки
            sanitize_phone_error=0,
            sanitize_phone_count=1,
            sanitize_phone_first_call=TimeNow(),
            sanitize_phone_last_call=TimeNow(),
            phone_valid_for_flash_call=True,
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE_OBJECT.e164,
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        # вторая попытка подтвердить телефон, уже после валидации телефона
        rv = self.make_request(
            '/1/bundle/restore/login/check_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'display_language': 'ru',
                'confirm_method': confirm_method,
            },
        )
        expected_response_values = dict(
            code_length=len(code)
        )
        if confirm_method == 'by_flash_call':
            expected_response_values.update(
                calling_number_template='+7 123456XXXX',
            )
        self.assert_ok_response(
            rv,
            **expected_response_values
        )

        self.assert_track_updated(
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_call_session_id='123',
            phone_confirmation_code=human_readable_code,
            country='ru',
            display_language='ru',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_method=confirm_method,
            phone_confirmation_phone_number=TEST_PHONE_OBJECT.e164,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_calls_count=1,
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        # проверяем, удалось ли дозвониться
        rv = self.make_request(
            '/1/bundle/phone/confirm/check_status/',
            method='GET',
            query_args={
                'consumer': 'dev',
            },
        )
        self.assert_error_response(rv, ['call_confirm.not_ready'])

        # вводим код для подтверждения телефона
        rv = self.make_request(
            '/1/bundle/restore/login/confirm_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'code': code,
            },
        )
        self.assert_ok_response(
            rv,
        )
        self.assert_track_updated(
            restore_state=RESTORE_STATE_PHONE_CONFIRMED,
            phone_confirmation_confirms_count_limit_reached=False,
            phone_confirmation_first_checked=TimeNow(),
            phone_confirmation_is_confirmed=True,
            phone_confirmation_last_checked=TimeNow(),
            phone_confirmation_confirms_count=1,
        )

        # проверяем, удалось ли дозвониться
        rv = self.make_request(
            '/1/bundle/phone/confirm/check_status/',
            method='GET',
            query_args={
                'consumer': 'dev',
            },
        )
        self.assert_error_response(rv, ['call_confirm.finished'])

    def test_integrational_flash_call_ok(self):
        self.run_integrational_scenario('by_flash_call', '1234', '1234')

    def test_integrational_call_ok(self):
        self.run_integrational_scenario('by_call', '123456', '123 456')

    def test_change_call_to_sms(self):
        accounts = [
            self.build_account(),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

        # начинаем процесс восстановления логина
        rv = self.make_request(
            '/1/bundle/restore/login/submit/?consumer=dev',
            method='POST',
        )
        self.assert_ok_response(rv, track_id=self.track_id)

        self.assert_track_updated(
            is_created=True,
            created=TimeNow(),
            is_captcha_required=True,
            restore_state=RESTORE_STATE_SUBMITTED,
            process_name='login_restore',
            phone_operation_confirmations=[],
            restore_methods_select_order=[],
            suggested_logins=[],
            totp_push_device_ids=[],
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        # проверяем состояние восстановления
        rv = self.make_request(
            '/1/bundle/restore/login/get_state/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
            },
        )
        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            retpath=None,
            restore_state=RESTORE_STATE_SUBMITTED,
        )

        # допустим, что пользователь прошёл каптчу
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        # валидируем телефон для звонков
        rv = self.make_request(
            '/1/bundle/validate/phone_number/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'validate_for_call': '1',
            },
        )
        self.assert_ok_response(
            rv,
            check_all=False,
            valid_for_call=True,
            valid_for_flash_call=True,
        )
        self.assert_track_updated(
            # сайд-эффект мнимого прохождения каптчи, см. выше по тесту
            is_captcha_checked=True,
            is_captcha_recognized=True,
            # всё что ниже - результат вызова ручки
            sanitize_phone_error=0,
            sanitize_phone_count=1,
            sanitize_phone_first_call=TimeNow(),
            sanitize_phone_last_call=TimeNow(),
            phone_valid_for_flash_call=True,
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE_OBJECT.e164,
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        # попытка подтвердить телефон после валидации телефона
        rv = self.make_request(
            '/1/bundle/restore/login/check_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'display_language': 'ru',
                'confirm_method': 'by_call',
            },
        )
        self.assert_ok_response(
            rv,
            code_length=6,
        )

        self.assert_track_updated(
            is_captcha_checked=False,
            is_captcha_recognized=False,
            phone_call_session_id='123',
            phone_confirmation_code='123 456',
            country='ru',
            display_language='ru',
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE_OBJECT.e164,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_calls_count=1,
        )
        self.orig_track = self.track_manager.read(self.track_id).snapshot()

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        # пробуем отослать код через смс
        rv = self.make_request(
            '/1/bundle/restore/login/check_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'phone_number': TEST_PHONE_LOCAL_FORMAT,
                'display_language': 'ru',
                'confirm_method': 'by_sms',
            },
        )
        self.assert_ok_response(
            rv,
            code_length=6,
            resend_timeout=10,
        )

        self.assert_track_updated(
            phone_confirmation_method='by_sms',
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_sms_count=1,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_is_confirmed=0,
            phone_confirmation_last_send_at=TimeNow(),
        )

        assert len(self.env.yasms.requests) == 1

        rv = self.make_request(
            '/1/bundle/restore/login/confirm_phone/?consumer=dev',
            method='POST',
            query_args={
                'track_id': self.track_id,
                'code': TEST_VALIDATION_CODE,
            },
        )
        self.assert_ok_response(
            rv,
        )
