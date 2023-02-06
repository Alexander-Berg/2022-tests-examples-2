# -*- coding: utf-8 -*-

import json

import mock
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import (
    AccountValidityTestsMixin,
    CommonMethodTestsMixin,
    CommonTestsMixin,
    eq_,
    RestoreBaseTestCase,
)
from passport.backend.api.views.bundle.restore.base import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.counters import restore_counter
from passport.backend.core.models.persistent_track import TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    TimeSpan,
)
from passport.backend.core.types.login.login import masked_login


RESTORE_BY_LINK_TEMPLATE_URL = 'https://0.passportdev.yandex.%(tld)s/restoration/?key=%(key)s'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    NATIVE_EMAIL_DOMAINS=('yandex.ru', 'yandex.com.tr', u'яндекс.рф'),
    DOMAINS_SERVED_BY_SUPPORT={TEST_PDD_DOMAIN, TEST_PDD_CYRILLIC_DOMAIN},
    SHOW_SEMI_AUTO_FORM_ON_AUTO_RESTORE_DENOMINATOR=1,
    EMAIL_CHECK_ERRORS_COUNT_LIMIT=2,
    RESTORATION_EMAILS_COUNT_LIMIT=3,
    RESTORATION_AUTO_LINK_LIFETIME_SECONDS=600,
    RESTORE_BY_LINK_TEMPLATE_URL=RESTORE_BY_LINK_TEMPLATE_URL,
    PHONE_QUARANTINE_SECONDS=TEST_OPERATION_TTL.total_seconds(),
    **mock_counters()
)
class RestoreCheckEmailTestCase(RestoreBaseTestCase, CommonTestsMixin, EmailTestMixin,
                                AccountValidityTestsMixin, CommonMethodTestsMixin):

    restore_step = 'check_email'

    default_url = '/1/bundle/restore/email/check/'

    def setUp(self):
        super(RestoreCheckEmailTestCase, self).setUp()
        self._generate_persistent_track_id_mock = mock.Mock(return_value=TEST_PERSISTENT_TRACK_ID)
        self._generate_persistent_track_id_patch = mock.patch(
            'passport.backend.core.models.persistent_track.generate_track_id',
            self._generate_persistent_track_id_mock,
        )
        self._generate_persistent_track_id_patch.start()
        self.env.statbox.bind_entry(
            'passed_with_email',
            _inherit_from='passed',
            matched_emails_count='1',
            is_email_confirmed='1',
            is_email_external='1',
            is_email_rpop='0',
            is_email_silent='0',
            is_email_suitable='1',
            is_email_unsafe='0',
        )
        self.setup_messenger_api_responses()

    def tearDown(self):
        self._generate_persistent_track_id_patch.stop()
        del self._generate_persistent_track_id_patch
        del self._generate_persistent_track_id_mock
        super(RestoreCheckEmailTestCase, self).tearDown()

    def set_track_values(self, restore_state=RESTORE_STATE_METHOD_SELECTED,
                         current_restore_method=RESTORE_METHOD_EMAIL,
                         **params):
        params.update(
            restore_state=restore_state,
            current_restore_method=current_restore_method,
        )
        super(RestoreCheckEmailTestCase, self).set_track_values(**params)

    def setup_messenger_api_responses(self):
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_DEFAULT_UID))

    def assert_persistent_track_created(self, uid=TEST_DEFAULT_UID, user_entered_login=TEST_USER_ENTERED_LOGIN,
                                        user_entered_email=TEST_EMAIL, retpath=None, db='passportdbshard1'):
        eq_(self.env.db.query_count(db), 1)
        args_to_check = {
            'uid': uid,
            'created': DatetimeNow(),
            'expired': DatetimeNow(timestamp=datetime.now() + timedelta(seconds=600)),
        }
        for field, value in args_to_check.items():
            self.env.db.check('tracks', field, value, db=db, track_id=TEST_PERSISTENT_TRACK_ID)

        expected_content = {
            'user_entered_login': user_entered_login,
            'user_entered_email': user_entered_email,
            'retpath': retpath,
            'type': TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
            'initiator_track_id': self.track_id,
        }
        content = self.env.db.get(
            'tracks',
            'content',
            db=db,
        )
        eq_(json.loads(content), expected_content)

    def assert_restoration_email_sent(self, email, user_entered_login=TEST_USER_ENTERED_LOGIN,
                                      restoration_key=TEST_EMAIL_RESTORATION_KEY, is_simple_format=False):
        email_context = {
            'language': 'ru',
            'addresses': [email],
            'subject': 'restore.auto.email_restoration_message_subject',
        }
        if is_simple_format:
            email_context['message_body'] = restoration_key
        else:
            restoration_link = RESTORE_BY_LINK_TEMPLATE_URL % dict(tld='ru', key=restoration_key)
            email_context['tanker_keys'] = {
                'greeting': {'FIRST_NAME': TEST_DEFAULT_FIRSTNAME},
                'restore.auto.email_restoration_message.notice': {
                    'LOGIN': masked_login(user_entered_login),
                    'RESTORATION_LINK': restoration_link,
                    'RESTORATION_URL_BEGIN': '<a href=\'%s\'>' % restoration_link,
                    'RESTORATION_URL_END': '</a>',
                },
                'restore.auto.email_restoration_message.alternative': {
                    'RESTORATION_KEY': restoration_key,
                },
                'restore.auto.email_restoration_message.surprise': {
                    'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                    'ACCESS_CONTROL_URL_END': '</a>',
                },
                'signature.secure': {},
                'feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
            }

        self.assert_emails_sent([email_context])

    def query_params(self, display_language='ru', email=TEST_EMAIL, is_simple_format=None, **kwargs):
        return dict(
            email=email,
            display_language=display_language,
            is_simple_format=is_simple_format,
        )

    def test_global_counter_overflow_fails(self):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.global_counter_overflow_case(RESTORE_METHOD_EMAIL)

    def test_email_check_counter_in_track_overflow_fails(self):
        """Переполнен счетчик проверок email-адреса в треке"""
        self.set_track_values(email_checks_count=2)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['email.check_limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='email.check_limit_exceeded',
                current_restore_method=RESTORE_METHOD_EMAIL,
                email_checks_count='2',
            ),
        ])

    def test_restoration_emails_counter_in_track_overflow_fails(self):
        """Переполнен счетчик отправок писем на email-адрес в треке"""
        self.set_track_values(restoration_emails_count=3)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['email.send_limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='email.send_limit_exceeded',
                current_restore_method=RESTORE_METHOD_EMAIL,
                restoration_emails_count='3',
            ),
        ])

    def test_email_restore_no_more_available_fails(self):
        """Восстановление по email-адресу более недоступно для аккаунта"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
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
                current_restore_method=RESTORE_METHOD_EMAIL,
            ),
        ])
        self.assert_blackbox_userinfo_called()

    def base_email_not_suitable_for_restore_case(self, entered_email, email_options=None):
        """Общий код тестов для случая email-адреса, не подходящего для восстановления"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(email=entered_email),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['email.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            user_entered_email=entered_email,
            email_checks_count=1,
            is_email_check_passed=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='email.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                email_checks_count='1',
                is_hint_masked='1',
                is_simple_format='0',
                **(email_options or {})
            ),
        ])

    def test_email_not_suitable_for_restore_fails(self):
        """Введен email-адрес, не подходящий для восстановления"""
        self.base_email_not_suitable_for_restore_case(
            entered_email='%s@other_mail.ru' % TEST_DEFAULT_LOGIN,
            email_options=dict(matched_emails_count='0'),
        )

    def test_rpop_email_not_suitable_for_restore_fails(self):
        """Введен rpop email-адрес, не подходящий для восстановления"""
        self.base_email_not_suitable_for_restore_case(
            entered_email='%s@mail.ru' % TEST_DEFAULT_LOGIN,
            email_options=dict(
                matched_emails_count='1',
                is_email_confirmed='1',
                is_email_external='1',
                is_email_rpop='1',
                is_email_silent='0',
                is_email_suitable='0',
                is_email_unsafe='0',
            ),
        )

    def test_native_email_not_suitable_for_restore_fails(self):
        """Введен нативный email-адрес от восстанавливаемого аккаунту, такой адрес не подходит для восстановления"""
        self.base_email_not_suitable_for_restore_case(
            entered_email='%s@yandex.ru' % TEST_DEFAULT_LOGIN,
            email_options=dict(
                matched_emails_count='1',
                is_email_confirmed='0',
                is_email_external='0',
                is_email_rpop='0',
                is_email_silent='0',
                is_email_suitable='0',
                is_email_unsafe='0',
            ),
        )

    def test_other_native_email_not_suitable_for_restore_fails(self):
        """Введен нативный email-адрес от другого аккаунта, не подходящий для восстановления"""
        self.base_email_not_suitable_for_restore_case(
            entered_email='login2@yandex.ru',
            email_options=dict(matched_emails_count='0'),
        )

    def test_email_changed_to_not_suitable_for_restore_fails(self):
        """Введен email-адрес, не подходящий для восстановления; до этого вводился другой валидный адрес"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        self.set_track_values(
            user_entered_email=TEST_EMAIL,
            restoration_key_created_at=TEST_RESTORATION_KEY_CREATE_TIMESTAMP,
            is_email_check_passed=True,
        )
        entered_email = '%s@mail.ru' % TEST_DEFAULT_LOGIN

        resp = self.make_request(
            self.query_params(email=entered_email),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['email.not_matched'],
            **self.base_expected_response()
        )
        self.assert_track_updated(
            user_entered_email=entered_email,
            email_checks_count=1,
            restoration_key_created_at=None,
            is_email_check_passed=False,
        )
        counter = restore_counter.get_per_ip_buckets()
        eq_(counter.get(TEST_IP), 1)  # обновление глобального счетчика
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='email.not_matched',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                is_email_changed='1',
                email_checks_count='1',
                is_hint_masked='1',
                is_simple_format='0',
                matched_emails_count='1',
                is_email_confirmed='1',
                is_email_external='1',
                is_email_rpop='1',
                is_email_silent='0',
                is_email_suitable='0',
                is_email_unsafe='0',
            ),
        ])

    def test_email_restoration_not_suitable_with_account_forced_password_changing(self):
        """Базовый тест для случая ввода правильного email-адреса, но у аккаунта принуждение к смене пароля"""
        email = '%s@gmail.com' % TEST_DEFAULT_LOGIN

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(*email.split('@')),
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                ],
                password_changing_required=True,
            ),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(email=email),
            headers=self.get_headers(),
        )

        self.assert_error_response(
            resp,
            ['method.not_allowed'],
            **self.base_expected_response()
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='method.not_allowed',
                suitable_restore_methods=','.join([RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                is_hint_masked='1',
            ),
        ])

    def base_email_check_passed_case(self, account_email, entered_email):
        """Базовый тест для случая ввода правильного email-адреса"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(*account_email.split('@')),
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'mail.ru', rpop=True),
                    self.create_native_email(TEST_DEFAULT_LOGIN, 'yandex.ru'),
                ],
            ),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(email=entered_email),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            user_entered_email=entered_email,
            restoration_emails_count=1,
            restoration_key_created_at=TimeNow(),
            is_email_check_passed=True,
        )
        self.assert_persistent_track_created(
            user_entered_email=entered_email,
        )
        self.assert_restoration_email_sent(entered_email)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                restoration_emails_count='1',
                is_hint_masked='1',
                is_simple_format='0',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])

    def test_external_email_check_passed_ok(self):
        """Введен правильный email-адрес, создан и отправлен ключ восстановления"""
        email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_check_passed_case(account_email=email, entered_email=email)

    def test_external_email_with_normalization_check_passed_ok(self):
        """Введен правильный email-адрес, отличается регистр"""
        email = '%s@gmail.com' % TEST_DEFAULT_LOGIN
        self.base_email_check_passed_case(account_email=email, entered_email=email.upper())

    def test_yandex_email_as_external_with_different_domains_check_passed_ok(self):
        """Введен правильный email-адрес, являющийся нативным для аккаунта на Яндексе, учтена нормализация и
        различные домены"""
        self.base_email_check_passed_case(
            account_email=u'Login.Login@яндекс.рф',
            entered_email=u'login-login@yandex.com.tr',
        )

    def test_yandex_email_as_external_multiple_domains_ok(self):
        """К аккаунту привязаны адреса от другого аккаунта на Яндексе, один пригоден для восстановления, другой нет"""
        entered_email = 'Login.Login@yandex.com.tr'
        account_email_1 = u'Login.Login@яндекс.рф'
        account_email_2 = u'Login.Login@yandex.ru'
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                emails=[
                    self.create_validated_external_email(*account_email_1.split('@')),
                    dict(self.create_validated_external_email(*account_email_2.split('@')), unsafe=True),
                ],
            ),
        )
        self.set_track_values()

        resp = self.make_request(
            self.query_params(email=entered_email),
            headers=self.get_headers(),
        )

        self.assert_ok_response(resp, **self.base_expected_response())
        self.assert_track_updated(
            user_entered_email=entered_email,
            restoration_emails_count=1,
            restoration_key_created_at=TimeNow(),
            is_email_check_passed=True,
        )
        self.assert_persistent_track_created(
            user_entered_email=entered_email,
        )
        self.assert_restoration_email_sent(entered_email)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                restoration_emails_count='1',
                is_hint_masked='1',
                is_simple_format='0',
                matched_emails_count='2',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])

    def test_email_check_passed_with_simple_format_with_retpath_for_pdd_ok(self):
        """Введен правильный email-адрес, создан и отправлен ключ восстановления простого формата для ПДД-пользователя"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_CYRILLIC_LOGIN,
                subscribed_to=[102],
                emails=[
                    self.create_validated_external_email(TEST_DEFAULT_LOGIN, 'gmail.com'),
                    self.create_native_email(TEST_DEFAULT_LOGIN, TEST_PDD_CYRILLIC_DOMAIN_PUNYCODE),
                ],
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='1',
                domain=TEST_PDD_CYRILLIC_DOMAIN,
            ),
        )
        self.set_track_values(
            uid=TEST_PDD_UID,
            login=TEST_PDD_CYRILLIC_LOGIN,
            user_entered_login=TEST_PDD_CYRILLIC_LOGIN,
            retpath=TEST_PDD_RETPATH,
        )
        entered_email = '%s@gmail.com' % TEST_DEFAULT_LOGIN

        resp = self.make_request(
            self.query_params(email=entered_email, is_simple_format=True),
            headers=self.get_headers(),
        )

        self.assert_ok_response(
            resp,
            **self.base_expected_response(user_entered_login=TEST_PDD_CYRILLIC_LOGIN)
        )
        self.assert_track_updated(
            user_entered_email=entered_email,
            restoration_emails_count=1,
            restoration_key_created_at=TimeNow(),
            is_email_check_passed=True,
        )
        self.assert_persistent_track_created(
            user_entered_email=entered_email,
            user_entered_login=TEST_PDD_CYRILLIC_LOGIN,
            retpath=TEST_PDD_RETPATH,
            uid=TEST_PDD_UID,
            db='passportdbshard2',
        )
        self.assert_restoration_email_sent(
            entered_email,
            is_simple_format=True,
            restoration_key=TEST_PDD_EMAIL_RESTORATION_KEY,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'passed_with_email',
                suitable_restore_methods=','.join([RESTORE_METHOD_EMAIL, RESTORE_METHOD_SEMI_AUTO_FORM]),
                current_restore_method=RESTORE_METHOD_EMAIL,
                restoration_emails_count='1',
                is_hint_masked='1',
                uid=str(TEST_PDD_UID),
                login=TEST_PDD_CYRILLIC_LOGIN,
                retpath=TEST_PDD_RETPATH,
                is_simple_format='1',
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
