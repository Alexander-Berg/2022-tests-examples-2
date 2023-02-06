# -*- coding: utf-8 -*-

import json

import mock
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
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
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.counters.change_password_counter import get_per_phone_number_buckets
from passport.backend.core.support_link_types import SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_PER_IP_COUNTER_LIMIT_FOR_SUPPORT_LINK=10,
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    **mock_counters()
)
class RestoreCheckNewPhoneTestCase(RestoreBaseTestCase, CommonTestsMixin,
                                   AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'check_new_phone'

    default_url = '/1/bundle/restore/new_phone/check/'

    account_validity_tests_extra_statbox_params = {
        'support_link_type': SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    }
    common_tests_mixin_extra_statbox_context = account_validity_tests_extra_statbox_params
    test_invalid_support_link_types = False
    require_enabled_account = False
    allow_missing_password_with_portal_alias = True

    def setUp(self):
        super(RestoreCheckNewPhoneTestCase, self).setUp()
        self._generate_random_code_mock = mock.Mock(return_value=TEST_VALIDATION_CODE)
        self._generate_random_code_patch = mock.patch(
            'passport.backend.api.yasms.utils.generate_random_code',
            self._generate_random_code_mock,
        )
        self._generate_random_code_patch.start()
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def tearDown(self):
        self._generate_random_code_patch.stop()
        del self._generate_random_code_mock
        del self._generate_random_code_patch
        super(RestoreCheckNewPhoneTestCase, self).tearDown()

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_PASSED,
                         current_restore_method=RESTORE_METHOD_LINK,
                         support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
            # Сейчас привязка телефона возможна только при восстановлении по ссылке на ввод нового пароля
            support_link_type=support_link_type,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
        )
        super(RestoreCheckNewPhoneTestCase, self).set_track_values(**params)

    def query_params(self, display_language='ru', phone_number=TEST_PHONE_LOCAL_FORMAT, country=None, **kwargs):
        return dict(
            phone_number=phone_number,
            display_language=display_language,
            country=country or 'ru',
        )

    @property
    def sms_template(self):
        return TEST_SMS_TEXT

    def assert_sms_sent(self, code=TEST_VALIDATION_CODE):
        eq_(len(self.env.yasms.requests), 1)
        self.env.yasms.requests[0].assert_query_contains({
            'identity': 'restore.check_new_phone.send_confirmation_code',
            'text': self.sms_template,
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            'text_template_params': json.dumps({'code': str(code)}).encode('utf-8'),
        })

    def setup_statbox_templates(self, sms_retriever_kwargs=None):
        super(RestoreCheckNewPhoneTestCase, self).setup_statbox_templates(sms_retriever_kwargs)
        self.env.statbox.bind_entry(
            'resotore_check_new_phone',
            current_restore_method='link',
            suitable_restore_methods='link,semi_auto',
            support_link_type='1',
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['resotore_check_new_phone', 'local_base'],
            action='restore.check_new_phone.send_confirmation_code',
            antifraud_reason='some-reason',
            antifraud_tags='',
            number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            scenario='restore',
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )

    def assert_ok_pharma_request(self, request):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=TEST_PHONE_OBJECT,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.uid = TEST_DEFAULT_UID
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = '/1/bundle/restore/new_phone/check/'
        features.scenario = 'restore'
        features.add_headers_features(self.get_headers())
        assert request_data == features.as_score_dict()

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_LINK)

    def test_new_phone_not_allowed_fails(self):
        """Процессом не предусмотрена привязка нового телефона"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                phone=TEST_PHONE,
                is_phone_secure=True,
            ),
        )
        self.track_invalid_state_case(
            support_link_type=None,
            extra_response_params=self.base_expected_response(),
        )

    def test_phone_is_already_confirmed_fails(self):
        """Телефон уже подтвержден в процессе восстановления"""
        self.track_invalid_state_case(phone_confirmation_is_confirmed=True)

    def test_phone_is_compromised_fails(self):
        """Использованный номер телефона нельзя привязать как защищенный"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(
            current_restore_method=RESTORE_METHOD_HINT,
            support_link_type=None,
        )
        counter = get_per_phone_number_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE)
        eq_(counter.get(TEST_PHONE), counter.limit)

        resp = self.make_request(
            self.query_params(),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['phone.compromised'],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        eq_(counter.get(TEST_PHONE), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='phone.compromised',
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
        ])

    def base_sms_send_limit_overflow_case(
        self,
        set_track_kwargs, expected_track_kwargs=None,
        global_sms_ip_limit_reached=False,
        statbox_kwargs=None,
        pharma_reached=False,
    ):
        """Общий код тестов превышения лимита отправки СМС, проверяемого в конфирматоре"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            **set_track_kwargs
        )
        if global_sms_ip_limit_reached:
            counter = sms_per_ip.get_counter(TEST_IP)
            for _ in range(counter.limit):
                counter.incr(TEST_IP)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        expected_track_kwargs = expected_track_kwargs or {}
        self.assert_track_updated(
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            country='ru',
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
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                **(statbox_kwargs or {})
            ),
        ]
        self.env.statbox.assert_has_written(statbox)

        self.assert_blackbox_userinfo_called()
        eq_(len(self.env.yasms.requests), 0)

    def test_send_count_by_ip_limit_reached_fails(self):
        """Достигнут глобальный лимит отправки СМС по IP, выставляем значение флага в треке"""
        self.base_sms_send_limit_overflow_case(
            {},
            global_sms_ip_limit_reached=True,
            statbox_kwargs=dict(
                reason='ip_limit',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
        )

    def test_send_count_track_limit_reached_fails(self):
        """Достигнут лимит отправки СМС по локальным счетчикам, выставляем значение флага в треке"""
        self.base_sms_send_limit_overflow_case(
            dict(phone_confirmation_sms_count=2),
            statbox_kwargs=dict(
                reason='track_limit',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
            ),
            pharma_reached=True,
        )

    def test_resend_within_timeout_fails(self):
        """Повторная отправка СМС слишком рано"""
        self.base_sms_send_limit_overflow_case(
            dict(
                phone_confirmation_sms_count=1,
                phone_confirmation_last_send_at=str(int(time.time())),
            ),
            statbox_kwargs=dict(
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                reason='rate_limit',
            ),
        )

    def test_phone_valid_sms_sent_ok(self):
        """Отправляем СМС на введенный номер"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                # Несмотря на наличие защищенного номера, позволяем привязать новый, так как
                # все данные будут сброшены
                phone=TEST_PHONE2,
                is_phone_secure=True,
            ),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            resend_timeout=5,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            country='ru',
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                sms_id='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                sms_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_new_phone.send_confirmation_code'})

    def test_phone_valid_sms_resent_ok(self):
        """Повторная отправка СМС на тот же номер"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        send_time = str(int(time.time()) - 10)
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            country='ru',
            # проверим, что код валидации будет использован тот же
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            # поля, выставляемые конфирматором
            phone_confirmation_first_send_at=send_time,
            phone_confirmation_last_send_at=send_time,
            phone_confirmation_sms_count=1,
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            resend_timeout=5,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        # проверим, что код не генерировался (был взят тот же код из трека)
        eq_(self._generate_random_code_mock.call_count, 0)
        self.assert_track_updated(
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=2,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_phone_changed='0'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                is_phone_changed='0',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                sms_id='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                sms_count='2',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent(code=TEST_VALIDATION_CODE_2)
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_new_phone.send_confirmation_code'})

    def test_phone_changed_sms_sent_ok(self):
        """Введенный телефон отличается от ранее введенного, отправляем СМС и сбрасываем счетчики в треке"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE_2),
            country='ru',
            phone_confirmation_last_send_at=str(int(time.time()) - 10),
            phone_confirmation_sms_count=1,
            phone_confirmation_confirms_count=2,
        )

        resp = self.make_request(self.query_params(phone_number=TEST_PHONE2), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            resend_timeout=5,
            number=TEST_PHONE_DUMP_2,
            **self.base_expected_response()
        )
        # проверим, что код генерировался (так как телефон изменён)
        eq_(self._generate_random_code_mock.call_count, 1)
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE2,
            phone_confirmation_phone_number=TEST_PHONE2,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=1,  # счетчик был сброшен и увеличен на единицу
            phone_confirmation_confirms_count=0,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed', is_phone_changed='1'),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_LINK,
                is_phone_changed='1',
                support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                sms_id='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                sms_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_new_phone.send_confirmation_code'})

    def test_voluntary_phone_valid_sms_sent_ok(self):
        """Отправляем СМС на введенный номер, добровольная привязка номера"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_track_values(support_link_type=None, current_restore_method=RESTORE_METHOD_HINT)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_ok_response(
            resp,
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            resend_timeout=5,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            phone_confirmation_code=str(TEST_VALIDATION_CODE),
            country='ru',
            phone_confirmation_first_send_at=TimeNow(),
            phone_confirmation_last_send_at=TimeNow(),
            phone_confirmation_sms_count=1,
            phone_confirmation_is_confirmed=False,
            phone_confirmation_method='by_sms',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'pharma_allowed',
                _exclude=['support_link_type'],
                current_restore_method=RESTORE_METHOD_HINT,
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
            ),
            self.env.statbox.entry(
                'passed_with_sms',
                suitable_restore_methods=','.join([RESTORE_METHOD_HINT, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_HINT,
                sms_id='1',
                number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                sms_count='1',
            ),
        ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_new_phone.send_confirmation_code'})

    def base_yasms_send_sms_error_case(self, exception_class, error_code, statbox_error_code=None, statbox_kwargs=None):
        """Базовый тест обработки ошибки отправки СМС"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.env.yasms.set_response_side_effect(
            'send_sms',
            exception_class,
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            [error_code],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )
        self.assert_track_updated(
            # поля, выставляемые в ручке
            user_entered_phone_number=TEST_PHONE_LOCAL_FORMAT,
            phone_confirmation_phone_number=TEST_PHONE,
            country='ru',
        )
        eq_(sms_per_ip.get_counter(TEST_IP).get(TEST_IP), 0)
        if error_code != 'exception.unhandled':
            self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
                self.env.statbox.entry(
                    'finished_with_error_with_sms',
                    error=statbox_error_code or error_code,
                    number=TEST_PHONE_OBJECT.masked_format_for_statbox,
                    suitable_restore_methods=','.join([RESTORE_METHOD_LINK, RESTORE_METHOD_SEMI_AUTO_FORM]),
                    current_restore_method=RESTORE_METHOD_LINK,
                    support_link_type=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
                    **(statbox_kwargs or {})
                ),
            ])
        self.assert_blackbox_userinfo_called()
        self.assert_sms_sent()
        self.env.yasms.requests[0].assert_query_contains({'identity': 'restore.check_new_phone.send_confirmation_code'})

    def test_send_sms_limit_exceeded_fails(self):
        """Превышен лимит на стороне ЯСМС"""
        self.base_yasms_send_sms_error_case(
            yasms_exceptions.YaSmsLimitExceeded,
            'sms_limit.exceeded',
            statbox_kwargs=dict(reason='yasms_phone_limit'),
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

    def test_pharma_denied(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['sms_limit.exceeded'],
            number=TEST_PHONE_DUMP_WITH_LOCAL_FORMAT,
            **self.base_expected_response()
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    SECURE_PHONE_CHECK_ERRORS_COUNT_LIMIT=2,
    SMS_VALIDATION_MAX_SMS_COUNT=2,
    SMS_VALIDATION_RESEND_TIMEOUT=5,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    RESTORE_PER_IP_COUNTER_LIMIT_FOR_SUPPORT_LINK=10,
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT=TEST_GPS_PUBLIC_KEY,
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    **mock_counters()
)
class RestoreCheckNewPhoneWithSmsRetrieverTestCase(RestoreCheckNewPhoneTestCase):
    """Тесты с форматированием SMS под SmsRetriever в Андроиде"""

    def setUp(self):
        super(RestoreCheckNewPhoneWithSmsRetrieverTestCase, self).setUp()

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
        return super(RestoreCheckNewPhoneWithSmsRetrieverTestCase, self).set_track_values(
            gps_package_name=TEST_GPS_PACKAGE_NAME,
            **params
        )
