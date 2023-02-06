# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_L_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    TEST_PHONE_NUMBER_DUMP,
)
from passport.backend.core import authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_contains_params
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
)
from passport.backend.core.builders.historydb_api import BaseHistoryDBApiError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    event_item,
    events_response,
)
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.builders.yasms.faker import (
    yasms_confirm_response,
    yasms_send_sms_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import (
    datetime_to_unixtime,
    parse_datetime,
)


TEST_LOGIN = 'test_user'
TEST_SOCIAL_LOGIN = 'uid-test'
TEST_LITE_LOGIN = 'lite@example.com'
TEST_PASSWORD = 'aaa1bbbccc'
TEST_HINT_QUESTION = 'Doroty\'s best friend'
TEST_HINT_ANSWER = 'Toto'
TEST_USER_AGENT = 'curl'
TEST_HOST = 'passport-test.yandex.ru'
TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_IP = '3.3.3.3'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_REFERER = 'http://test.yandex.com/referer'
TEST_USER_MESSAGES = [6666, 6667, 6668]
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_AUTH_ID = '123:1422501443:126'
TEST_SERVICE = get_service(slug='lenta')
TEST_GALATASARAY_SERVICE = get_service(sid=61)
TEST_SERVICE_ATTRIBUTE_NAME = 'subscription.%d' % TEST_SERVICE.sid
TEST_OTHER_SERVICE = get_service(slug='cloud')
TEST_MAIL = get_service(slug='mail')
TEST_YASMS = get_service(slug='yasms')
TEST_BLOCKING = get_service(slug='partner')
TEST_PROTECTED = get_service(slug='vip')
TEST_PASSPORT = get_service(slug='passport')
# Этот сервис использует значения login_rule <= 3 для обозначения заблокированных пользователей
TEST_PROTECTED_LOGIN_RULE_VALUE = '3'  # см passport.services.PROTECTED_SID_TO_LOGIN_RULE
TEST_CUSTOM_LOGIN_RULE = get_service(slug='disk')
TEST_BLOCKING_ON_LOGIN_RULE = get_service(slug='jabber')
TEST_DEFAULT_REGISTRATION_DATETIME = '2010-10-10 10:20:30'
TEST_DEFAULT_REGISTRATION_TIMESTAMP = datetime_to_unixtime(parse_datetime(TEST_DEFAULT_REGISTRATION_DATETIME))

TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488

TEST_DOMAIN = 'okna.ru'

EXPECTED_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'
MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

eq_ = iterdiff(eq_)


class BaseUnsubscribeViewTestCase(BaseBundleTestViews, EmailTestMixin):

    default_url = None
    http_method = 'post'
    http_query_args = dict(
        service=TEST_SERVICE.slug,
        retpath=TEST_RETPATH,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie='Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        user_ip=TEST_IP,
        referer=TEST_REFERER,
    )

    def get_expected_account(self, person=True, login=TEST_LOGIN, display_login=TEST_LOGIN,
                             is_pdd=False, punycode_domain=TEST_DOMAIN,
                             unicode_domain=TEST_DOMAIN):
        uid = self.env.TEST_UID
        if is_pdd:
            uid = self.env.TEST_PDD_UID
        account = {
            'uid': uid,
            'login': login,
            'display_login': display_login,
            'display_name': {
                'default_avatar': '',
                'name': '',
            },
        }
        if person:
            account['person'] = {
                'firstname': u'\\u0414',
                'lastname': u'\\u0424',
                'language': 'ru',
                'gender': 1,
                'birthday': '1963-05-15',
                'country': 'ru',
            }
        if is_pdd:
            account['domain'] = {
                'unicode': unicode_domain,
                'punycode': punycode_domain,
            }
        return account

    def get_expected_secure_phone(self):
        return TEST_PHONE_NUMBER_DUMP

    def get_expected_cookies(self, login=TEST_LOGIN):
        return sorted([
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE % login,
            EXPECTED_L_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ])

    def setup_env(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def setup_userinfo_response(self, sid, uid=None, login_rule='1', **kwargs):
        userinfo_response = blackbox_userinfo_response(
            uid=uid or self.env.TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[sid],
            crypt_password='1:pwd',
            dbfields={
                'subscription.login_rule.%d' % sid: login_rule,
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
            },
            **kwargs
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        return userinfo_response

    def setup_account_and_sessionid_response(self, sid, uid=None, login_rule='1',
                                             session_status=None,
                                             login=TEST_LOGIN, alias_type='portal', have_password=True,
                                             social_sid=False, with_secure_phone=True, **kwargs):
        sid = sid or TEST_SERVICE.sid
        has_galatasaray_alias = sid == TEST_GALATASARAY_SERVICE.sid

        dbfields = {
            'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
            'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
        }

        if login_rule and not has_galatasaray_alias:
            dbfields['subscription.login_rule.%d' % sid] = login_rule

        if sid == TEST_MAIL.sid:
            dbfields['subscription.suid.2'] = 12345

        crypt_password = '1:pwd'
        if not have_password:
            crypt_password = ''

        subscribed_to = []

        if not has_galatasaray_alias:
            subscribed_to += [sid]

        if social_sid:
            subscribed_to += [58]

        phone_secured = {}

        if with_secure_phone:
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )

        kwargs = deep_merge(phone_secured, kwargs)

        if sid == TEST_MAIL.sid:
            kwargs.setdefault('attributes', {})['subscription.mail.status'] = 1

        aliases = {alias_type: login}
        if has_galatasaray_alias:
            aliases.update(altdomain='%s@galatasaray.net' % login)

        sessionid_response = blackbox_sessionid_multi_response(
            status=session_status or blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
            uid=uid or self.env.TEST_UID,
            login=login,
            aliases=aliases,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            authid=TEST_AUTH_ID,
            age=TEST_COOKIE_AGE,
            ttl=0,
            ip=TEST_IP,
            time=TEST_COOKIE_TIMESTAMP,
            subscribed_to=subscribed_to,
            crypt_password=crypt_password,
            dbfields=dbfields,
            **kwargs
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        self.env.db.serialize(sessionid_response)

    def setup_login_response(self, uid=None, login=TEST_LOGIN, sid=None,
                             crypt_password='1:pwd', aliases=None,
                             bruteforce=None, password_status=None):
        sid = sid or TEST_SERVICE.sid
        dbfields = {
            'subscription.login_rule.%d' % sid: '1',
            'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
            'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
        }
        if sid == TEST_MAIL.sid:
            dbfields['subscription.suid.2'] = 12345
        account_info = {
            'uid': uid or self.env.TEST_UID,
            'login': login,
            'crypt_password': crypt_password,
            'emails': [
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            'subscribed_to': [sid],
            'dbfields': dbfields,
            'aliases': aliases,
        }

        if password_status is not None:
            account_info['password_status'] = password_status

        if bruteforce:
            account_info['bruteforce_policy'] = bruteforce

        login_response = blackbox_login_response(**account_info)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

    def setup_editsession_response(self):
        bb_response = blackbox_editsession_response()
        self.env.blackbox.set_response_value(
            'editsession',
            bb_response,
        )

    def setup_lrandoms_response(self):
        bb_response = blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_lrandoms_response_value(bb_response)

    def setup_cookie_mocks(self):
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)

        patches = [
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        for patch in patches:
            patch.start()

        self.patches.extend(patches)

    def setUp(self):
        self.patches = []

        self.setup_env()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['unsubscribe'],
                    'subscription': ['%s.delete' % TEST_SERVICE.sid],
                },
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def stop_patches(self):
        for patch in self.patches:
            patch.stop()

    def tearDown(self):
        self.env.stop()
        self.stop_patches()
        del self.env
        del self.patches
        del self.track_manager

    def base_track(self):
        return dict(
            retpath=TEST_RETPATH,
        )

    def assert_track_ok(self, **kwargs):
        """Трек заполнен полностью и корректно"""
        params = self.base_track()
        params.update(kwargs)
        track = self.track_manager.read(self.track_id)
        for attr_name, value in params.items():
            actual_value = getattr(track, attr_name)
            expected_value = str(value) if type(value) == int else value
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def assert_track_empty(self):
        """Трек пуст в случае какой-либо ошибки"""
        track = self.track_manager.read(self.track_id)
        self.assertIsNone(track.uid)
        self.assertIsNone(track.is_unsubscribed)

    def assert_track_with_account_and_session(self, login=TEST_LOGIN):
        self.assert_track_ok(
            uid=self.env.TEST_UID,
            login=login,
            human_readable_login=login,
            machine_readable_login=login,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            can_use_secure_number_for_password_validation=True,
            have_password=True,
            language='ru',
            country='ru',
            allow_authorization=True,
            allow_oauth_authorization=False,
            is_password_passed=True,
        )

    def assert_statbox_ok(self, sid, uid=None, action='removed', with_check_cookies=False, **kwargs):
        uid = uid or self.env.TEST_UID
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'base',
                unixtime=TimeNow(),
                mode='unsubscribe',
                ip=TEST_IP,
                user_agent=TEST_USER_AGENT,
                uid=str(uid),
                sid=str(sid),
                action=action,
            )
        )
        self.env.statbox.assert_has_written(entries)

    def assert_ok_response(self, response, **kwargs):
        """Переопределяю хэлпер"""
        kwargs['status'] = 'ok'
        eq_(response.status_code, 200)
        actual = json.loads(response.data)
        if 'cookies' in actual:
            actual['cookies'] = sorted(actual['cookies'])
        eq_(
            actual,
            kwargs,
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    YASMS_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
)
class SubmitUnsubscribeViewTestCase(BaseUnsubscribeViewTestCase):

    default_url = '/1/bundle/account/unsubscribe/submit/?consumer=dev'

    def setUp(self):
        super(SubmitUnsubscribeViewTestCase, self).setUp()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        super(SubmitUnsubscribeViewTestCase, self).tearDown()

    def test_no_grant__error(self):
        self.env.grants.set_grants_return_value(
            mock_grants(grants={}),  # нет грантов
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['access.denied'], status_code=403)
        self.assert_track_empty()

    def test_blocking_service__error(self):
        self.setup_account_and_sessionid_response(TEST_BLOCKING.sid)

        resp = self.make_request(query_args=dict(service=TEST_BLOCKING.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()

    def test_protected_service__error(self):
        self.setup_account_and_sessionid_response(TEST_PROTECTED.sid)

        resp = self.make_request(query_args=dict(service=TEST_PROTECTED.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()

    def test_yasms_cant_be_unsubscribed__error(self):
        """Притворяемся, что вообще не знаем о таком сервисе как Я.СМС"""
        self.setup_account_and_sessionid_response(TEST_YASMS.sid)

        resp = self.make_request(query_args=dict(service=TEST_YASMS.sid))

        self.assert_error_response(
            resp,
            ['service.invalid'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()

    def test_account_is_not_subscribed__error(self):
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)

        resp = self.make_request(query_args=dict(service=TEST_OTHER_SERVICE.sid))

        self.assert_error_response(
            resp,
            ['account.not_subscribed'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()

    def test_invalid_session__error(self):
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            session_status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['sessionid.invalid'])
        self.assert_track_empty()

    def test_disabled_session__error(self):
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            session_status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['account.disabled'])
        self.assert_track_empty()

    def test_submit__account_with_regular_subscription_ok(self):
        """Отписка возможна, информация о пользователе и защищенном телефоне в ответе"""
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid, **phone_secured)
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )
        self.assert_track_ok(
            uid=self.env.TEST_UID,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            can_use_secure_number_for_password_validation=True,
        )
        self.assert_statbox_ok(TEST_SERVICE.sid, action='submitted', with_check_cookies=True)

        self.env.blackbox.requests[0].assert_query_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def test_social_account_redirect(self):
        """
        Пользователь без пароля (недорегистрированный соц пользователь)
        не может отписаться от сервиса, пока не дорегистрируется
        """
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            login=TEST_SOCIAL_LOGIN,
            alias_type='social',
            have_password=False,
        )
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='complete_social',
            account=self.get_expected_account(login=TEST_SOCIAL_LOGIN, display_login=''),
        )

    def test_portal_account_with_social_alias(self):
        """У пользователя, подписанного на социальный SID, не установлен пароль"""
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            have_password=False,
            social_sid=True,
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='complete_social',
            account=self.get_expected_account(),
        )

    def test_pdd_clean_retpath_with_last_slash(self):
        retpath = 'https://wordstat.yandex.ru/for/domain/?words=bla'
        cleaned_retpath = 'https://wordstat.yandex.ru/?words=bla'

        pdd_uid = self.env.TEST_PDD_UID
        login = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)

        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            uid=pdd_uid,
            login=login,
            domain=TEST_DOMAIN,
            alias_type='pdd',
        )

        resp = self.make_request(query_args=dict(retpath=retpath))

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(is_pdd=True, login=login, display_login=login),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )
        self.assert_track_ok(retpath=cleaned_retpath)

    def test_lite_unsubscribe__ok(self):
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            login=TEST_LITE_LOGIN,
            alias_type='lite',
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(login=TEST_LITE_LOGIN, display_login=TEST_LITE_LOGIN),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )
        self.assert_track_ok()

    def test_blocking_service_on_login_rule__error(self):
        self.setup_account_and_sessionid_response(TEST_BLOCKING_ON_LOGIN_RULE.sid, login_rule='0')

        resp = self.make_request(query_args=dict(service=TEST_BLOCKING_ON_LOGIN_RULE.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()

    def test_login_rule_undefined_on_subscription__ok(self):
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid, login_rule=None)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )
        self.assert_track_ok(
            uid=self.env.TEST_UID,
            secure_phone_number=TEST_PHONE_NUMBER.e164,
            can_use_secure_number_for_password_validation=True,
        )
        self.assert_statbox_ok(TEST_SERVICE.sid, action='submitted', with_check_cookies=True)

    def test_galatasaray_protected(self):
        self.setup_account_and_sessionid_response(TEST_GALATASARAY_SERVICE.sid)

        resp = self.make_request(query_args=dict(service=TEST_GALATASARAY_SERVICE.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
        )
        self.assert_track_empty()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    YASMS_URL='http://localhost',
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=4,
    PASSPORT_SUBDOMAIN='passport-test',
    **mock_counters()
)
class CommitUnsubscribeViewTestCase(BaseUnsubscribeViewTestCase):

    default_url = '/1/bundle/account/unsubscribe/commit/?consumer=dev'

    def setUp(self):
        super(CommitUnsubscribeViewTestCase, self).setUp()

        self.setup_track()
        self.setup_login_response()
        self.setup_lrandoms_response()
        self.setup_editsession_response()
        self.setup_cookie_mocks()
        self.http_query_args = dict(
            password=TEST_PASSWORD,
            track_id=self.track_id,
        )

    def tearDown(self):
        del self.build_cookies_yx
        del self.build_cookie_l
        super(CommitUnsubscribeViewTestCase, self).tearDown()

    def setup_mail_alias(self):
        """
        Сейчас нет никакого штатного способа записать в БД alias.mail
        Поэтому просто запишем строчку в таблицу
        """
        mail_alias_type = ALIAS_NAME_TO_TYPE['mail']
        self.env.db.insert(
            'aliases',
            type=mail_alias_type,
            value='alias@thirdpartyhost.ru',
            uid=self.env.TEST_UID,
            db='passportdbcentral',
        )

    def setup_track(self, service=TEST_SERVICE, uid=None, phone=False,
                    hint=False, short_form=False, captcha_required=False,
                    captcha_passed=False):
        uid = uid or self.env.TEST_UID
        # Подготовим все поля, которые устанавливались при вызове /submit
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = uid
            track.retpath = TEST_RETPATH
            track.service = service.slug

            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164
            track.can_use_secure_number_for_password_validation = True

            if phone:
                track.phone_confirmation_is_confirmed = True
                track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

            if hint:
                track.is_secure_hint_answer_checked = True

            if short_form:
                track.is_short_form_factors_checked = True

            if captcha_required:
                track.is_captcha_required = True

            if captcha_passed:
                track.is_captcha_checked = True
                track.is_captcha_recognized = True

    def assert_unsubscribed(self, uid=None, sid=None):
        attr_name = 'subscription.%d' % sid if sid else TEST_SERVICE_ATTRIBUTE_NAME
        uid = uid or self.env.TEST_UID
        self.env.db.check_db_attr_missing(
            uid,
            attr_name,
        )

    def assert_mail_unsubscribed(self, uid=None):
        uid = uid or self.env.TEST_UID
        attr_names = (
            'subscription.mail.login_rule',
        )
        for attr_name in attr_names:
            self.env.db.check_db_attr_missing(
                uid,
                attr_name,
            )

        self.env.db.check_missing(
            'aliases',
            'mail',
            uid=uid,
            db='passportdbcentral',
        )

        self.env.db.check_missing(
            'suid2',
            uid=uid,
            db='passportdbcentral',
        )

    def assert_events_ok(self, sid=None, uid=None, login=TEST_LOGIN):
        uid = uid or self.env.TEST_UID
        sid = sid or TEST_SERVICE.sid
        entry = {
            'action': 'unsubscribe',
            'consumer': 'dev',
            'user_agent': 'curl',
            'sid.rm': '%d|%s' % (sid, login),
        }
        if sid == TEST_MAIL.sid:
            entry.update({
                'sid.rm.info': '%d|%s|12345' % (uid, login),
                'mail.rm': '12345',
                'info.mail_status': '-',
            })
        self.assert_events_are_logged(
            self.env.handle_mock,
            entry,
        )

    def assert_statbox_ok(self, service, uid=None, action='removed', is_captcha_passed=False,
                          login=TEST_LOGIN, with_check_cookies=False, **kwargs):
        uid = uid or self.env.TEST_UID
        expected_entries = []
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies'))

        if service == TEST_MAIL:
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.mail_status',
                    operation='deleted',
                    old='active',
                    new='-',
                    ip=TEST_IP,
                    user_agent=TEST_USER_AGENT,
                    consumer='dev',
                ),
            )

        expected_entries += [
            self.env.statbox.entry(
                'account_modification',
                entity='subscriptions',
                operation='removed',
                sid=str(service.sid),
                ip=TEST_IP,
                user_agent=TEST_USER_AGENT,
                consumer='dev',
                **kwargs
            ),
            self.env.statbox.entry(
                'cookie_set',
                user_agent=TEST_USER_AGENT,
                ip=TEST_IP,
                session_method='edit',
                ttl='0',
                old_session_uids='1',
                ip_country='us',
                retpath=TEST_RETPATH,
                authid=TEST_AUTH_ID,
                yandexuid=TEST_YANDEXUID_COOKIE,
                person_country='ru',
                input_login=login,
                captcha_passed='1' if is_captcha_passed else '0',
                track_id=self.track_id,
                **{'from': service.slug}
            ),
            self.env.statbox.entry(
                'base',
                unixtime=TimeNow(),
                user_agent=TEST_USER_AGENT,
                mode='unsubscribe',
                ip=TEST_IP,
                uid=str(uid),
                sid=str(service.sid),
                action=action,
                track_id=self.track_id,
            ),
        ]

        self.env.statbox.assert_has_written(expected_entries)

    def assert_track_unchanged(self):
        """Трек пуст в случае какой-либо ошибки"""
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(self.env.TEST_UID))
        eq_(track.retpath, TEST_RETPATH)
        self.assertIsNone(track.is_unsubscribed)

    def test_no_grant__error(self):
        self.env.grants.set_grants_return_value(
            mock_grants(grants={}),  # нет грантов
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['access.denied'], status_code=403)
        self.assert_track_unchanged()

    def test_account_not_subscribed__error(self):
        self.setup_account_and_sessionid_response(TEST_OTHER_SERVICE.sid)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['account.not_subscribed'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()

    def test_blocking_service__error(self):
        """Блокирующий сервис нельзя отписывать вообще"""
        self.setup_account_and_sessionid_response(TEST_BLOCKING.sid)
        self.setup_track(service=TEST_BLOCKING)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()

    def test_protected_service__error(self):
        """Защищенный сервис также нельзя отписывать"""
        self.setup_account_and_sessionid_response(TEST_PROTECTED.sid)
        self.setup_track(service=TEST_PROTECTED)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()

    def test_passport_service__error(self):
        """От сервиса passport нельзя отписывать ни при каких условиях"""
        self.setup_account_and_sessionid_response(TEST_PROTECTED.sid)
        self.setup_track(service=TEST_PASSPORT)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()

    def test_used_track__error(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_unsubscribed = True

        resp = self.make_request()

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_unknown_uid_in_track__error(self):
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = self.env.TEST_UID + 1  # Какой-то другой uid

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['sessionid.no_uid'],
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_no_uid_in_track__error(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = ''

        resp = self.make_request()

        self.assert_error_response(resp, ['track.invalid_state'])

    def test_captcha_required_but_not_passed__error(self):
        """При прошлой попытке отписаться возникло требование прохода капчи. Капча еще не проходена - ошибка"""
        self.setup_track(captcha_required=True)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['captcha.required'],
        )

    def test_bad_password__error(self):
        """Пользователь ввел неверный пароль"""
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)
        self.setup_login_response(password_status=blackbox.BLACKBOX_PASSWORD_BAD_STATUS)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['password.not_matched'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_captcha_required__error(self):
        """При проверке пароля получили сообщение от ЧЯ о необходимости показа капчи - ошибка"""
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)
        self.setup_login_response(bruteforce=blackbox.BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['captcha.required'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_subscription_is_blocked_by_login_rule__error(self):
        """
        Некоторые сервисы могут блокировать пользователя, что делает отписку невозможной
        Это делается через установку особенного значения в поле login_rule на подписке
        Таких подписок не много, но они могут использовать разные значения для блокировки пользователя
        """
        self.setup_account_and_sessionid_response(
            TEST_CUSTOM_LOGIN_RULE.sid,
            login_rule=TEST_PROTECTED_LOGIN_RULE_VALUE,
        )

        self.setup_track(service=TEST_CUSTOM_LOGIN_RULE)

        resp = self.make_request(query_args=dict(service=TEST_CUSTOM_LOGIN_RULE.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_pdd_account_cant_unsubscribe_mail_service__error(self):
        """ПДД-пользователь по определению не может отказаться от Почты"""
        pdd_uid = self.env.TEST_PDD_UID
        login = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)

        self.setup_account_and_sessionid_response(
            TEST_MAIL.sid,
            uid=pdd_uid,
            login=login,
            domain=TEST_DOMAIN,
            alias_type='pdd',
        )
        self.setup_track(service=TEST_MAIL, uid=pdd_uid)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(is_pdd=True, login=login, display_login=login),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_commit__ok(self):
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_unsubscribed()
        self.assert_statbox_ok(TEST_SERVICE, with_check_cookies=True)
        self.assert_events_ok()

    def test_captcha_required_and_passed__ok(self):
        """Пользователь прошел капчу когда она требовалась -- ОК"""
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid)
        self.setup_track(captcha_required=True, captcha_passed=True)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_unsubscribed()
        self.assert_statbox_ok(TEST_SERVICE, is_captcha_passed=True, with_check_cookies=True)
        self.assert_events_ok()

    def test_mail_unsubscribe_requires_user_validation__error(self):
        """При отписке от Почты пользователь должен подтвердить свою человечность, иначе ошибка"""
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_track(service=TEST_MAIL)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['user.not_verified'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_mail_unsubscribe_with_sms_validation__ok(self):
        """
        Пользователь отписывается от сервиса Почта, он подтвердил свой защищенный номер телефона
        """
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, phone=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_mail_unsubscribed()
        self.assert_statbox_ok(TEST_MAIL, suid='12345', with_check_cookies=True)
        self.assert_events_ok(sid=TEST_MAIL.sid)
        eq_(len(self.env.husky_api.requests), 1)

    def test_mail_unsubscribe_with_hint_answer__ok(self):
        """
        Пользователь отписывается от Почты, он правильно ответил на текущий КВ -- ОК
        """
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, hint=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_mail_unsubscribed()
        self.assert_statbox_ok(TEST_MAIL, suid='12345', with_check_cookies=True)
        self.assert_events_ok(sid=TEST_MAIL.sid)
        eq_(len(self.env.husky_api.requests), 1)

    def test_mail_unsubscribe_with_short_recovery__ok(self):
        """
        Пользователь отписывается от Почты, он прошел короткую анкету восстановления -- ОК
        """
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, short_form=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_mail_unsubscribed()
        self.assert_statbox_ok(TEST_MAIL, suid='12345', with_check_cookies=True)
        self.assert_events_ok(sid=TEST_MAIL.sid)
        eq_(len(self.env.husky_api.requests), 1)

    def test_mail_unsubscribe_husky_temporary__error(self):
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(status='error'),
        )
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, phone=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_error_response(
            resp,
            ['backend.husky_failed'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        eq_(len(self.env.husky_api.requests), 4)

    def test_mail_unsubscribe_husky_already_exists__ok(self):
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(status='error', code=4),
        )
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, phone=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_mail_unsubscribed()
        self.assert_statbox_ok(TEST_MAIL, suid='12345', with_check_cookies=True)
        self.assert_events_ok(sid=TEST_MAIL.sid)
        eq_(len(self.env.husky_api.requests), 1)

    def test_mail_unsubscribe_husky_invalid_response_error(self):
        self.setup_account_and_sessionid_response(TEST_MAIL.sid)
        self.setup_login_response(sid=TEST_MAIL.sid)
        self.env.husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(status='error', code=3),
        )
        self.setup_mail_alias()
        self.setup_track(service=TEST_MAIL, phone=True)

        resp = self.make_request(query_args=dict(service=TEST_MAIL.sid))

        self.assert_error_response(
            resp,
            ['backend.husky_permanent_error'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        eq_(len(self.env.husky_api.requests), 1)

    def test_social_account_redirect(self):
        """
        Пользователь без пароля (недорегистрированный соц пользователь)
        не может отписаться от сервиса, пока не дорегистрируется
        """
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            login=TEST_SOCIAL_LOGIN,
            have_password=False,
            alias_type='social',
        )
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='complete_social',
            account=self.get_expected_account(login=TEST_SOCIAL_LOGIN, display_login=''),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_portal_account_with_social_alias(self):
        """У пользователя, подписанного на социальный SID, не установлен пароль"""
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            have_password=False,
            social_sid=True,
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='complete_social',
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_lite_unsubscribe__ok(self):
        self.setup_account_and_sessionid_response(
            TEST_SERVICE.sid,
            login=TEST_LITE_LOGIN,
            alias_type='lite',
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(login=TEST_LITE_LOGIN, display_login=TEST_LITE_LOGIN),
            accounts=[
                self.get_expected_account(
                    person=False,
                    login=TEST_LITE_LOGIN,
                    display_login=TEST_LITE_LOGIN,
                ),
            ],
            cookies=self.get_expected_cookies(login=TEST_LITE_LOGIN),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session(login=TEST_LITE_LOGIN)
        self.assert_unsubscribed()
        self.assert_statbox_ok(TEST_SERVICE, login=TEST_LITE_LOGIN, with_check_cookies=True)
        self.assert_events_ok(login=TEST_LITE_LOGIN)

    def test_blocking_service_on_login_rule__error(self):
        self.setup_account_and_sessionid_response(TEST_BLOCKING_ON_LOGIN_RULE.sid, login_rule='0')
        self.setup_track(service=TEST_BLOCKING_ON_LOGIN_RULE, short_form=True)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()

    def test_login_rule_undefined_on_subscription__ok(self):
        self.setup_account_and_sessionid_response(TEST_SERVICE.sid, login_rule=None)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_with_account_and_session()
        self.assert_unsubscribed()
        self.assert_statbox_ok(TEST_SERVICE, with_check_cookies=True)
        self.assert_events_ok()

    def test_galatasaray_protected(self):
        self.setup_account_and_sessionid_response(TEST_GALATASARAY_SERVICE.sid)
        self.setup_track(service=TEST_GALATASARAY_SERVICE, short_form=True)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        self.assert_track_unchanged()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    YASMS_URL='http://localhost',
    SMS_LEGACY_VALIDATION_CODE_LENGTH=4,
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=1,
    PASSPORT_SUBDOMAIN='passport-test',
)
class MailUnsubscribeIntegrationTestCase(BaseUnsubscribeViewTestCase):
    """
    Здесь пройдем весь путь с вызовами всех необходимых ручек
      - Отписка от Почты со вводом капчи и валидацией телефона по sms
      - Отписка от Почты с ответом на текущий КВ
      - Отписка от Почты с прохождением мини-анкеты восстановления
    """

    submit_url = SubmitUnsubscribeViewTestCase.default_url
    commit_url = CommitUnsubscribeViewTestCase.default_url
    sid = TEST_MAIL.sid

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['unsubscribe'],
                    'subscription': ['mail.delete'],
                    'captcha': ['*'],
                    'phone_number': ['confirm'],
                    'questions': ['base', 'secure'],
                    'restore': ['semi_auto'],
                },
            ),
        )

    def setup_historydb_api(self):
        auths_items = [
            auth_successful_aggregated_runtime_auths_item(
                auth_items=[
                    auth_successful_aggregated_runtime_auth_item(
                        authtype=authtypes.AUTH_TYPE_IMAP,
                        status='successful',
                        ip_info=auth_successful_aggregated_runtime_ip_info(ip=TEST_IP),
                    ),
                    auth_successful_aggregated_runtime_auth_item(
                        browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                        count=10,
                    ),
                ],
                timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP,
            ),
        ]
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=auths_items),
        )
        ip, ts = TEST_IP, TEST_DEFAULT_REGISTRATION_TIMESTAMP
        events = [
            event_item(name='info.birthday', value='1963-05-15', user_ip=ip, timestamp=ts),
            event_item(name='info.firstname', value=u'Петр', user_ip=ip, timestamp=ts),
            event_item(name='info.lastname', value=u'Петров', user_ip=ip, timestamp=ts),
        ]
        self.env.historydb_api.set_response_value(
            'events',
            events_response(uid=self.env.TEST_UID, events=events),
        )

    def setUp(self):
        super(MailUnsubscribeIntegrationTestCase, self).setUp()

        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.setup_grants()

        self.setup_historydb_api()
        self.setup_userinfo_response(self.sid)

        self.setup_login_response(sid=self.sid)
        self.setup_lrandoms_response()
        self.setup_editsession_response()
        self.setup_cookie_mocks()
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        del self.build_cookies_yx
        del self.build_cookie_l
        super(MailUnsubscribeIntegrationTestCase, self).tearDown()

    def solve_captcha(self):
        """Пройдем проверку капчей"""
        captcha_response = captcha_response_generate(link='test-url', key='test-key')
        self.env.captcha_mock.set_response_value('generate', captcha_response)
        generate_url = '/1/captcha/generate/?consumer=dev'
        post_data = dict(track_id=self.track_id, display_language='ru')

        resp = self.make_request(
            url=generate_url,
            query_args=post_data,
        )

        self.assert_ok_response(
            resp,
            image_url='test-url',
            key='test-key',
        )

        check_url = '/1/captcha/check/?consumer=dev'
        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        post_data = dict(track_id=self.track_id, answer='fake-answer', key='fake-key')

        resp = self.make_request(
            url=check_url,
            query_args=post_data,
        )
        self.assert_ok_response(
            resp,
            correct=True,
        )

    def validate_by_sms(self):
        """Отправим пользователю sms на защищенный телефонный номер и введем код из sms"""
        send_code_response = yasms_send_sms_response()
        self.env.yasms.set_response_value('send_sms', send_code_response)
        send_code_url = '/1/phonenumber/send_confirmation_code/?consumer=dev'
        post_data = dict(
            track_id=self.track_id,
            display_language='ru',
            country='ru',
            phone_number=TEST_PHONE_NUMBER.international,
        )

        resp = self.make_request(
            url=send_code_url,
            query_args=post_data,
        )
        self.assert_ok_response(
            resp,
            code_length=4,
        )

        track = self.track_manager.read(self.track_id)
        code = track.phone_confirmation_code

        confirm_response = yasms_confirm_response()
        self.env.yasms.set_response_value('confirm', confirm_response)
        confirm_url = '/1/phonenumber/confirm/?consumer=dev'
        post_data = dict(track_id=self.track_id, code=code)

        resp = self.make_request(
            url=confirm_url,
            query_args=post_data,
        )
        self.assert_ok_response(
            resp,
            result=True,
        )

    def validate_by_hint(self):
        """Проверим знание текущего КВ/КО"""
        # Симулируем ошибку historydb-api для проверки текущего Контрольного Ответа
        self.env.historydb_api.set_response_side_effect('events', BaseHistoryDBApiError)

        hint_history_url = '/1/account/questions/secure/'
        query_string = dict(display_language='ru', track_id=self.track_id, consumer='dev')

        resp = self.make_request(
            url=hint_history_url,
            method='get',
            query_args=query_string,
        )

        self.assert_ok_response(
            resp,
            question={
                'id': 99,
                'text': TEST_HINT_QUESTION,
            },
            track_id=self.track_id,
        )

        hint_check_url = '/1/account/questions/secure/check/?consumer=dev'
        post_data = dict(
            display_language='ru',
            track_id=self.track_id,
            answer=TEST_HINT_ANSWER,
            question='test-question',
            question_id=0,  # Ответ из предыдущей ручки
        )

        resp = self.make_request(
            url=hint_check_url,
            query_args=post_data,
        )

        self.assert_ok_response(resp)

    def validate_by_short_restore(self):
        """Пройдем коротку анкету восстановления"""
        submit_url = '/1/bundle/restore/semi_auto/submit_with_captcha/?consumer=dev'
        post_data = dict(login=TEST_LOGIN, request_source='restore', track_id=self.track_id)

        resp = self.make_request(
            url=submit_url,
            query_args=post_data,
        )

        self.assert_ok_response(
            resp,
        )

        hint_history_url = '/1/bundle/restore/semi_auto/short_form/?consumer=dev'
        date = TEST_DEFAULT_REGISTRATION_DATETIME.split(' ')[0]
        post_data = dict(
            firstname=u'Петр',
            lastname=u'Петров',
            birthday='1963-05-15',
            eula_accepted='1',
            registration_date=date,
            registration_country=u'Россия',
            track_id=self.track_id,
        )

        resp = self.make_request(
            url=hint_history_url,
            query_args=post_data,
        )

        self.assert_ok_response(
            resp,
        )

    def test_secure_phone_validation__ok(self):
        """
        Отписка от Почты с проверкой по sms с защищенным номером
          - пришел
          - отправили sms и ввел код проверки
          - отписался
        """
        self.setup_account_and_sessionid_response(self.sid)
        submit_response = self.make_request(
            url=self.submit_url,
            query_args=dict(
                uid=self.env.TEST_UID,
                service=self.sid,
            ),
        )
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'method': 'sessionid',
                'getphones': 'all',
            },
            callnum=0,
        )

        self.assert_ok_response(
            submit_response,
            account=self.get_expected_account(),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )

        self.validate_by_sms()

        commit_response = self.make_request(
            url=self.commit_url,
            query_args=dict(
                password=TEST_PASSWORD,
                track_id=self.track_id,
            ),
        )
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'method': 'sessionid',
                'getphones': 'all',
            },
            callnum=1,
        )

        self.assert_ok_response(
            commit_response,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_secure_phone_validation_without_secure_number__error(self):
        """
        Отписка от Почты с проверкой по sms без защищенного номера
          - пришел
          - отправили sms и ввел код проверки
          - не отписался
        """
        self.setup_account_and_sessionid_response(self.sid, with_secure_phone=False)

        submit_response = self.make_request(
            url=self.submit_url,
            query_args=dict(
                uid=self.env.TEST_UID,
                service=self.sid,
            ),
        )

        self.assert_ok_response(
            submit_response,
            account=self.get_expected_account(),
            track_id=self.track_id,
        )

        self.validate_by_sms()

        commit_response = self.make_request(
            url=self.commit_url,
            query_args=dict(
                service=self.sid,
                password=TEST_PASSWORD,
                track_id=self.track_id,
            ),
        )

        self.assert_error_response(
            commit_response,
            ['user.not_verified'],
            account=self.get_expected_account(),
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_validation_with_hint__ok(self):
        """
        Отписка от Почты с проверкой по КВ/КО
          - пришел
          - получили список КВ и проверили введенный КО
          - отписался
        """
        self.setup_account_and_sessionid_response(self.sid)
        submit_response = self.make_request(
            url=self.submit_url,
            query_args=dict(
                service=self.sid,
            ),
        )

        self.assert_ok_response(
            submit_response,
            account=self.get_expected_account(),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )

        self.validate_by_hint()

        commit_response = self.make_request(
            url=self.commit_url,
            query_args=dict(
                service=self.sid,
                password=TEST_PASSWORD,
                track_id=self.track_id,
            ),
        )
        self.assert_ok_response(
            commit_response,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )

    def test_validation_with_short_restore__ok(self):
        """
        Отписка от Почты с проверкой по короткой анкете восстановления
          - пришел
          - прошел короткую анкету восстановления
          - отписался
        """
        self.setup_account_and_sessionid_response(self.sid)
        submit_response = self.make_request(
            url=self.submit_url,
            query_args=dict(
                service=self.sid,
            ),
        )

        self.assert_ok_response(
            submit_response,
            account=self.get_expected_account(),
            track_id=self.track_id,
            number=self.get_expected_secure_phone(),
        )

        self.solve_captcha()  # Мини-анкета требует ввод капчи
        self.validate_by_short_restore()

        commit_response = self.make_request(
            url=self.commit_url,
            query_args=dict(
                service=self.sid,
                password=TEST_PASSWORD,
                track_id=self.track_id,
            ),
        )
        self.assert_ok_response(
            commit_response,
            account=self.get_expected_account(),
            accounts=[self.get_expected_account(person=False)],
            cookies=self.get_expected_cookies(),
            default_uid=self.env.TEST_UID,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
