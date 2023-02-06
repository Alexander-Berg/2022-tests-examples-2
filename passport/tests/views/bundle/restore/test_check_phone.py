# -*- coding: utf-8 -*-

import json
import time

import mock
from nose_parameterized import parameterized
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_IP,
    TEST_OPERATION_TTL,
    TEST_PDD_CYRILLIC_DOMAIN,
    TEST_PDD_DOMAIN,
    TEST_PHONE,
    TEST_PHONE2,
    TEST_PHONE2_OBJECT,
    TEST_PHONE_LOCAL_FORMAT,
    TEST_PHONE_OBJECT,
    TEST_USER_ENTERED_LOGIN,
    TEST_VALIDATION_CODE,
    TEST_VALIDATION_CODE_2,
)
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    eq_,
    RestoreBaseTestCase,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_GPS_PACKAGE_HASH,
    TEST_GPS_PACKAGE_NAME,
    TEST_GPS_PUBLIC_KEY,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_SMS_TEXT,
    TEST_UID,
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.octopus import OctopusPermanentError
from passport.backend.core.builders.octopus.faker import octopus_response
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'
KOLMOGOR_COUNTER_SESSIONS_CREATED = 'sessions_created'
KOLMOGOR_COUNTER_CALLS_FAILED = 'calls_failed'
KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG = 'calls_shut_down'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_RETRIES=1,
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_URL='http://localhost',
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    **mock_counters()
)
class RestoreCheckPhoneTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'check_phone'

    default_url = '/1/bundle/restore/phone/check/'

    def setUp(self):
        super(RestoreCheckPhoneTestCase, self).setUp()
        self._generate_random_code_mock = mock.Mock(return_value=str(TEST_VALIDATION_CODE))
        self._generate_random_code_patch = mock.patch(
            'passport.backend.api.yasms.utils.generate_random_code',
            self._generate_random_code_mock,
        )
        self._generate_random_code_patch.start()

        self.env.kolmogor.set_response_value('inc', 'OK')
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }
        self.env.kolmogor.set_response_side_effect('get', [flag, counters])
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def tearDown(self):
        self._generate_random_code_patch.stop()
        del self._generate_random_code_mock
        del self._generate_random_code_patch
        super(RestoreCheckPhoneTestCase, self).tearDown()

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_PHONE,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
        )
        super(RestoreCheckPhoneTestCase, self).set_track_values(**params)

    def query_params(
        self,
        display_language='ru',
        phone_number=TEST_PHONE_LOCAL_FORMAT,
        country=None,
        confirm_method=None,
        code_format=None,
        **kwargs
    ):
        params = dict(
            phone_number=phone_number,
            display_language=display_language,
            country=country or 'ru',
            code_format=code_format,
        )
        if confirm_method is not None:
            params.update(confirm_method=confirm_method)
        return params

    @property
    def sms_template(self):
        return TEST_SMS_TEXT

    def assert_sms_sent(self, code=TEST_VALIDATION_CODE):
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({
            'identity': 'restore.check_phone.send_confirmation_code',
            'text': self.sms_template,
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(code)}).encode('utf-8'),
        })

    def setup_statbox_templates(self, sms_retriever_kwargs=None):
        super(RestoreCheckPhoneTestCase, self).setup_statbox_templates(sms_retriever_kwargs)
        self.env.statbox.bind_entry(
            'restore_check_phone',
            _inherit_from=['local_base'],
            suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
            current_restore_method=RESTORE_METHOD_PHONE,
            is_hint_masked='1',
        )
        self.env.statbox.bind_entry(
            'restore_check_phone.call_with_code',
            _inherit_from=['restore_check_phone', 'call_with_code'],
            is_phone_confirmed='1',
            is_phone_found='1',
            is_phone_suitable='1',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['restore_check_phone'],
            action='restore.check_phone.send_confirmation_code',
            antifraud_reason='some-reason',
            antifraud_tags='',
            is_phone_confirmed='1',
            is_phone_found='1',
            is_phone_suitable='1',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            scenario='restore',
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_allowed.call_with_code',
            _inherit_from=['pharma_allowed'],
            action='restore.check_phone',
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )

    def assert_equals_to_octopus_request(self, request):
        request.assert_properties_equal(
            method='POST',
            url='https://platform.telephony.yandex.net/v0/create-call',
            json_data={
                'firstCode': 123,
                'secondCode': 456,
                'caller': '+78006009639',
                'callee': TEST_PHONE,
                'locale': 'ru',
            },
        )

    def assert_kolmogor_called(self, calls=1, with_inc=True, keys='sessions_created'):
        eq_(len(self.env.kolmogor.requests), calls)
        if with_inc:
            self.env.kolmogor.requests[-1].assert_properties_equal(
                method='POST',
                url='http://localhost/inc',
                post_args={'space': TEST_KOLMOGOR_KEYSPACE_COUNTERS, 'keys': keys},
            )

    def assert_ok_pharma_request(self, request, extra_features=None):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=TEST_PHONE_OBJECT,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.uid = TEST_UID
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = '/1/bundle/restore/phone/check/'
        features.add_headers_features(self.get_headers())
        features.scenario = 'restore'
        features.add_dict_features(extra_features)
        assert request_data == features.as_score_dict()

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_PHONE)
        eq_(self.env.kolmogor.requests, [])

    def test_phone_check_counter_in_track_overflow_fails(self):
        """Переполнен счетчик проверок телефона в треке"""
        self.set_track_values(secure_phone_checks_count=2)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['phone.check_limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.check_limit_exceeded',
                current_restore_method=RESTORE_METHOD_PHONE,
                phone_checks_count='2',
            ),
        ])
        eq_(self.env.kolmogor.requests, [])

    def test_phone_is_already_confirmed_fails(self):
        """Телефон уже подтвержден в процессе восстановления"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=True)
        eq_(self.env.kolmogor.requests, [])

    def test_phone_restore_no_more_available_fails(self):
        """Восстановление по телефону более недоступно для аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=False,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
        eq_(self.env.kolmogor.requests, [])

    def test_phone_not_suitable_for_restore_fails(self):
        """Введенный телефон не может быть использован для восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['phone.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            secure_phone_checks_count=1,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_found='0',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
        eq_(self.env.kolmogor.requests, [])

    def base_sms_send_limit_overflow_case(
        self,
        set_track_kwargs,
        expected_track_kwargs=None,
        global_sms_ip_limit_reached=False,
        extra_statbox_kwargs=None,
        pharma_reached=False,
    ):
        """Общий код тестов превышения лимита отправки СМС, проверяемого в конфирматоре"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(**set_track_kwargs)
        if global_sms_ip_limit_reached:
            counter = sms_per_ip.get_counter(TEST_IP)
            for _ in range(counter.limit):
                counter.incr(TEST_IP)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            **self.base_expected_response()
        )
        expected_track_kwargs = expected_track_kwargs or {}
        self.assert_track_updated(
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            **expected_track_kwargs
        )
        expected_ip_counter_value = counter.limit if global_sms_ip_limit_reached else 0
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), expected_ip_counter_value)

        statbox = list()
        if pharma_reached:
            statbox += [
                self.env.statbox.entry('pharma_allowed'),
            ]
        statbox += [
            self.env.statbox.entry(
                'finished_with_error_with_sms',
                error='sms_limit.exceeded',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_confirmed='1',
                is_phone_found='1',
                is_phone_suitable='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                **(extra_statbox_kwargs or {})
            ),
        ]
        self.env.statbox.assert_has_written(statbox)

        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
        eq_(self.env.kolmogor.requests, [])

    def test_send_count_by_ip_limit_reached_fails(self):
        """Достигнут глобальный лимит отправки СМС по IP, выставляем значение флага в треке"""
        self.base_sms_send_limit_overflow_case(
            {},
            global_sms_ip_limit_reached=True,
            extra_statbox_kwargs=dict(
                reason='ip_limit',
            ),
        )
        eq_(self.env.kolmogor.requests, [])

    def test_send_count_track_limit_reached_fails(self):
        """Достигнут лимит отправки СМС по локальным счетчикам, выставляем значение флага в треке"""
        self.base_sms_send_limit_overflow_case(
            dict(phone_confirmation_sms_count=2),
            extra_statbox_kwargs=dict(
                reason='track_limit',
            ),
            pharma_reached=True,
        )
        eq_(self.env.kolmogor.requests, [])

    def test_resend_within_timeout_fails(self):
        """Повторная отправка СМС слишком рано"""
        self.base_sms_send_limit_overflow_case(
            dict(
                phone_confirmation_sms_count=1,
                phone_confirmation_last_send_at=str(int(time.time())),
            ),
            extra_statbox_kwargs=dict(
                reason='rate_limit',
            ),
        )
        eq_(self.env.kolmogor.requests, [])

    @parameterized.expand([
        (None, '657196'),
        ('by_3_dash', '657-196'),
    ])
    def test_phone_suitable_for_restore_sms_sent_ok(self, code_format, sent_code):
        u"""Введенный телефон подходит для восстановления, отправляем СМС"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(code_format=code_format), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=sent_code,
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_sms_count=1,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_confirmed='1',
                is_phone_found='1',
                is_phone_suitable='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent(code=sent_code)
        eq_(self.env.kolmogor.requests, [])

    def test_phone_suitable_for_restore_sms_resent_ok(self):
        """Повторная отправка СМС на тот же номер"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            # проверим, что код валидации будет использован тот же
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time() - 10)),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_is_confirmed=False,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        # проверим, что код не генерировался (был взят тот же код из трека)
        eq_(self._generate_random_code_mock.call_count, 0)
        self.assert_track_updated(
            # поля, выставляемые конфирматором
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=2,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_phone_changed='0'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_changed='0',
                is_phone_confirmed='1',
                is_phone_found='1',
                is_phone_suitable='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                sms_count='2',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent(code=TEST_VALIDATION_CODE_2)
        eq_(self.env.kolmogor.requests, [])

    def test_phone_changed_sms_sent_ok_calls_shut_down(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=2,
        )

        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)

        resp = self.make_request(self.query_params(phone_number=TEST_PHONE2), headers=self.get_headers())
        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        eq_(self.env.kolmogor.requests, [])

    def test_phone_changed_sms_sent_ok(self):
        """Введенный телефон подходит для восстановления, отличается от ранее введенного, отправляем СМС и
        сбрасываем счетчики в треке"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=2,
        )

        resp = self.make_request(self.query_params(phone_number=TEST_PHONE2), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        # проверим, что код генерировался (так как телефон изменён)
        eq_(self._generate_random_code_mock.call_count, 1)
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE2,
            secure_phone_number=TEST_PHONE2,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            # поля, выставляемые конфирматором
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=1,  # счетчик был сброшен и увеличен на единицу
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=0,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_phone_changed='1'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_changed='1',
                is_phone_confirmed='1',
                is_phone_found='1',
                is_phone_suitable='1',
                number=TEST_PHONE2_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()

    def test_phone_changed_to_not_suitable_fails(self):
        """Введенный телефон не подходит для восстановления, отличается от ранее введенного, который подходил"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=2,
            phone_confirmation_is_confirmed=False,
        )

        resp = self.make_request(self.query_params(phone_number=TEST_PHONE2), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['phone.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            user_entered_phone_number=TEST_PHONE2,
            secure_phone_number=TEST_PHONE2,
            phone_confirmation_code=None,
            secure_phone_checks_count=1,
            phone_confirmation_confirms_count=0,
            phone_confirmation_sms_count=0,
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 0)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_changed='1',
                is_phone_found='0',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)
        eq_(self.env.kolmogor.requests, [])

    def base_yasms_send_sms_error_case(self, exception_class, error_code, statbox_error_code=None, **extra_statbox):
        """Базовый тест обработки ошибки отправки СМС"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_side_effect(
            'send_sms',
            exception_class,
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, [error_code], **self.base_expected_response())
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 0)
        if error_code != 'exception.unhandled':
            self.env.statbox.assert_has_written([
                self.env.statbox.entry('pharma_allowed'),
                self.env.statbox.entry(
                    'finished_with_error_with_sms',
                    error=statbox_error_code or error_code,
                    number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                    suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                    current_restore_method=RESTORE_METHOD_PHONE,
                    is_hint_masked='1',
                    is_phone_confirmed='1',
                    is_phone_found='1',
                    is_phone_suitable='1',
                    **extra_statbox
                ),
            ])
        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_phone.send_confirmation_code'})
        eq_(self.env.kolmogor.requests, [])

    def test_send_sms_limit_exceeded_fails(self):
        """Превышен лимит на стороне ЯСМС"""
        self.base_yasms_send_sms_error_case(
            yasms_exceptions.YaSmsLimitExceeded,
            'sms_limit.exceeded',
            reason='yasms_phone_limit',
        )

    def test_send_sms_phone_blocked_fails(self):
        """Телефон заблокирован"""
        self.base_yasms_send_sms_error_case(yasms_exceptions.YaSmsPermanentBlock, 'phone.blocked')

    def test_send_sms_delivery_error_fails(self):
        """Ошибка отправки СМС"""
        self.base_yasms_send_sms_error_case(
            yasms_exceptions.YaSmsDeliveryError,
            'backend.yasms_failed',
            statbox_error_code='sms.isnt_sent',
        )

    def test_send_sms_unknown_error_fails(self):
        """Неизвестная ошибка"""
        self.base_yasms_send_sms_error_case(yasms_exceptions.YaSmsError, 'exception.unhandled')

    def test_save_used_gates(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(used_gate_ids=[2, 14]),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_sms_count=1,
            phone_confirmation_used_gate_ids='2,14',
            phone_confirmation_method='by_sms',
        )
        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)
        eq_(self.env.kolmogor.requests, [])

    def test_use_saved_gates(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(used_gate_ids=[18]),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='123456',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_used_gate_ids='1,15',
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        self.assert_track_updated(
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_used_gate_ids='18',
            phone_confirmation_is_confirmed=False,
            phone_confirmation_sms_count=2,
            phone_confirmation_method='by_sms',
        )
        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains(
            {'previous_gates': '1,15'},
        )
        eq_(self.env.kolmogor.requests, [])

    def test_used_gates_cleared_when_phone_changed(self):
        """Введенный телефон подходит для восстановления, отличается от ранее введенного, отправляем СМС и
        сбрасываем счетчики в треке"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(used_gate_ids=[32]),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=2,
            phone_confirmation_used_gate_ids='15',
            phone_confirmation_method='by_sms',
        )

        resp = self.make_request(self.query_params(phone_number=TEST_PHONE2), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        # проверим, что код генерировался (так как телефон изменён)
        eq_(self._generate_random_code_mock.call_count, 1)
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE2,
            secure_phone_number=TEST_PHONE2,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            # поля, выставляемые конфирматором
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=1,  # счетчик был сброшен и увеличен на единицу
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_confirms_count=0,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_used_gate_ids='32',
            phone_confirmation_method='by_sms',
        )

        self.assert_sms_sent()
        eq_(len(self.env.yasms.requests), 1)
        eq_(self.env.kolmogor.requests, [])

    def test_calls_shut_down(self):
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
        )

        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        resp = self.make_request(
            self.query_params(confirm_method='by_call'),
            headers=self.get_headers(),
        )
        self.assert_error_response(resp, error_codes=['calls.shut_down'])
        self.assert_kolmogor_called(1, with_inc=False)
        eq_(self.env.octopus.requests, [])

    def test_octopus_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
        )

        self.env.code_generator.set_return_value('123456')
        self.env.octopus.set_response_side_effect('create_session', OctopusPermanentError())

        resp = self.make_request(
            self.query_params(confirm_method='by_call'),
            headers=self.get_headers(),
        )
        self.assert_error_response(
            resp,
            error_codes=['create_call.failed'],
            track_id=self.track_id,
            user_entered_login=TEST_USER_ENTERED_LOGIN,
        )
        self.assert_kolmogor_called(3, keys=KOLMOGOR_COUNTER_CALLS_FAILED)

    @parameterized.expand([
        (None, '123 456'),
        ('by_3_dash', '123-456'),
    ])
    def test_phone_suitable_for_restore_code_called_ok(self, code_format, code_in_track):
        u"""
        Введенный телефон подходит для восстановления
        Диктуем код в телефон.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
        )
        self.env.code_generator.set_return_value('123456')
        self.env.octopus.set_response_value('create_session', octopus_response('123'))

        resp = self.make_request(
            self.query_params(confirm_method='by_call', code_format=code_format),
            headers=self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            code_length=6,
            **self.base_expected_response()
        )

        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_is_confirmed=False,

            # поля, выставляемые конфирматором
            country='ru',
            phone_call_session_id='123',
            phone_confirmation_calls_count=1,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code=code_in_track,
            phone_confirmation_confirms_count=0,
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed.call_with_code'),
            self.env.statbox.entry('restore_check_phone.call_with_code'),
        ])

        eq_(len(self.env.octopus.requests), 1)
        self.assert_equals_to_octopus_request(self.env.octopus.requests[0])
        self.assert_kolmogor_called(3)

    def test_phone_suitable_for_restore_code_recalled_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,

            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,

            # поля, выставляемые конфирматором
            country='ru',
            phone_call_session_id='321',
            phone_confirmation_calls_count=1,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code='123 456',
            phone_confirmation_confirms_count=1,
            phone_confirmation_first_called_at=str(int(time.time()) - 10),
            phone_confirmation_last_called_at=str(int(time.time()) - 10),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
        )
        self.env.octopus.set_response_value('create_session', octopus_response('123'))
        # Код не должен перегенериться, но, если перегенирится, он не должен
        # совпадать с исходным.
        self.env.code_generator.set_return_value('654321')

        resp = self.make_request(
            self.query_params(confirm_method='by_call'),
            headers=self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            code_length=6,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            # поля, выставляемые конфирматором
            phone_call_session_id='123',
            phone_confirmation_calls_count=2,
            phone_confirmation_last_called_at=TimeNow(),
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed.call_with_code', is_phone_changed='0'),
            self.env.statbox.entry(
                'restore_check_phone.call_with_code',
                calls_count='2',
                is_phone_changed='0',
            ),
        ])

        eq_(len(self.env.octopus.requests), 1)
        self.assert_equals_to_octopus_request(self.env.octopus.requests[0])
        self.assert_kolmogor_called(3)

    def test_phone_changed_code_called_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,

            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE2,
            secure_phone_number=TEST_PHONE2,

            # поля, выставляемые конфирматором
            country='ru',
            phone_call_session_id='321',
            phone_confirmation_calls_count=2,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code='654 321',
            phone_confirmation_confirms_count=2,
            phone_confirmation_first_called_at=str(int(time.time()) - 10),
            phone_confirmation_last_called_at=str(int(time.time()) - 10),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number_original=TEST_PHONE2,
        )
        self.env.code_generator.set_return_value('123456')
        self.env.octopus.set_response_value('create_session', octopus_response('123'))

        resp = self.make_request(
            self.query_params(
                phone_number=TEST_PHONE_LOCAL_FORMAT,
                confirm_method='by_call',
            ),
            headers=self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            code_length=6,
            **self.base_expected_response()
        )

        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,

            # поля, выставляемые конфирматором
            is_successful_phone_passed=False,
            phone_call_session_id='123',
            # счетчик был сброшен и увеличен на единицу
            phone_confirmation_calls_count=1,
            phone_confirmation_code='123 456',
            phone_confirmation_confirms_count=0,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed.call_with_code', is_phone_changed='1'),
            self.env.statbox.entry(
                'restore_check_phone.call_with_code',
                is_phone_changed='1',
            ),
        ])

        eq_(len(self.env.octopus.requests), 1)
        self.assert_equals_to_octopus_request(self.env.octopus.requests[0])
        self.assert_kolmogor_called(3)

    def test_change_method_sms_to_call(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            # поля, выставляемые конфирматором
            phone_confirmation_code='654321',
            phone_confirmation_first_send_at='1234',
            phone_confirmation_last_send_at=str(int(time.time() - 10)),
            phone_confirmation_sms_count=1,
            phone_confirmation_send_count_limit_reached=False,
            phone_confirmation_send_ip_limit_reached=False,
            phone_confirmation_is_confirmed=False,
        )
        self.env.code_generator.set_return_value('123456')
        self.env.octopus.set_response_value('create_session', octopus_response('123'))

        resp = self.make_request(
            self.query_params(confirm_method='by_call'),
            headers=self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            code_length=6,
            **self.base_expected_response()
        )

        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_sms_count=0,

            # поля, выставляемые конфирматором
            country='ru',
            is_successful_phone_passed=False,
            phone_call_session_id='123',
            phone_confirmation_calls_count=1,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code='123 456',
            phone_confirmation_confirms_count=0,
            phone_confirmation_first_called_at=TimeNow(),
            phone_confirmation_last_called_at=TimeNow(),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed.call_with_code', is_phone_changed='0'),
            self.env.statbox.entry(
                'restore_check_phone.call_with_code',
                is_phone_changed='0',
            ),
        ])

        eq_(len(self.env.octopus.requests), 1)
        self.assert_equals_to_octopus_request(self.env.octopus.requests[0])
        self.assert_kolmogor_called(3)

    def test_change_method_call_to_sms(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,

            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,

            # поля, выставляемые конфирматором
            country='ru',
            phone_call_session_id='321',
            phone_confirmation_calls_count=1,
            phone_confirmation_calls_count_limit_reached=False,
            phone_confirmation_calls_ip_limit_reached=False,
            phone_confirmation_code='654 321',
            phone_confirmation_confirms_count=1,
            phone_confirmation_first_called_at=str(int(time.time()) - 10),
            phone_confirmation_last_called_at=str(int(time.time()) - 10),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_phone_number_original=TEST_PHONE_LOCAL_FORMAT,
        )
        self.env.code_generator.set_return_value(TEST_VALIDATION_CODE)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(resp, resend_timeout=5, **self.base_expected_response())
        self.assert_track_updated(
            # поля, выставляемые в ручке
            phone_confirmation_confirms_count=0,
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            secure_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_is_confirmed=False,
            phone_confirmation_sms_count=1,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_phone_changed='0'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_PHONE, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_PHONE,
                is_hint_masked='1',
                is_phone_confirmed='1',
                is_phone_found='1',
                is_phone_suitable='1',
                is_phone_changed='0',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()
        eq_(self.env.kolmogor.requests, [])

    def test_pharma_denied_sms(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            **self.base_expected_response()
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])

    def test_pharma_denied_call(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.set_track_values(
            phone_valid_for_call=True,
            phone_validated_for_call=TEST_PHONE,
        )
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request(
            self.query_params(confirm_method='by_call'),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['calls_limit.exceeded'],
            **self.base_expected_response()
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'pharma_denied',
                    action='restore.check_phone',
                    operation='confirm',
                ),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(
            self.env.antifraud_api.requests[0],
            extra_features=dict(
                is_secure_phone=True,
                phone_confirmation_method='by_call',
                phone_confirmation_language='ru',
            ),
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT=TEST_GPS_PUBLIC_KEY,
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    **mock_counters()
)
class RestoreCheckPhoneWithSmsRetrieverTestCase(RestoreCheckPhoneTestCase):
    """Тесты с форматированием SMS под SmsRetriever в Андроиде"""

    def setUp(self):
        super(RestoreCheckPhoneWithSmsRetrieverTestCase, self).setUp()

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
        return super(RestoreCheckPhoneWithSmsRetrieverTestCase, self).set_track_values(
            gps_package_name=TEST_GPS_PACKAGE_NAME,
            **params
        )
