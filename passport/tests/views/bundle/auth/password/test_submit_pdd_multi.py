# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import AUTHORIZATION_SESSION_POLICY_PERMANENT
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_PDD_YANDEX_LOGIN_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    MDA2_BEACON_VALUE,
    TEST_ALLOWED_PDD_HOSTS,
    TEST_AUTH_ID,
    TEST_CLEANED_PDD_RETPATH,
    TEST_COOKIE_TIMESTAMP,
    TEST_CYRILLIC_PDD_LOGIN,
    TEST_DOMAIN,
    TEST_ENTERED_PDD_LOGIN,
    TEST_FRETPATH,
    TEST_HOST,
    TEST_IDNA_DOMAIN,
    TEST_IP,
    TEST_MODEL_CONFIGS,
    TEST_OLD_AUTH_ID,
    TEST_ORIGIN,
    TEST_PASSWORD,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PDD_UID,
    TEST_PUNYCODE_DOMAIN,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_RETPATH_HOST,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_LANGUAGE,
    TEST_YANDEXUID_COOKIE,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
)
from passport.backend.core.historydb.entry import AuthEntry
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import quote

from .test_submit import BaseSubmitAuthViewTestCase


eq_ = iterdiff(eq_)


class BasePDDSubmitMultiAuthTestCase(BaseSubmitAuthViewTestCase):
    """
    Тесты авторизации ПДД-пользователей
    """

    def get_headers(self, host=None, user_ip=None, cookie=None):
        return mock_headers(
            host=host or 'passport-test.yandex.ru',
            user_agent=TEST_USER_AGENT,
            cookie=cookie or 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
            referer=TEST_REFERER,
        )

    def get_base_query_params(self):
        return {
            'login': TEST_ENTERED_PDD_LOGIN,
            'password': TEST_PASSWORD,

            'retpath': TEST_PDD_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def get_blackbox_login_response_params(self, **kwargs):
        base = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
            # и есть персональная информация + КВ/КО
            subscribed_to=[102],
            crypt_password='1:pwd',
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        return merge_dicts(base, kwargs)

    def setup_cookie_mocks(self):
        self.build_cookies_yx = mock.Mock(return_value=[EXPECTED_YP_COOKIE, EXPECTED_YS_COOKIE])
        self.build_cookie_l = mock.Mock(return_value=EXPECTED_L_COOKIE)
        self.build_cookie_lah = mock.Mock(return_value=EXPECTED_LAH_COOKIE)

        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self.build_cookie_lah,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ])

    def setup_blackbox_responses(self, env):
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params()
        )
        env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                authid=TEST_AUTH_ID,
                ttl=5,
            ),
        )

        createsession_response = blackbox_createsession_response(authid=TEST_AUTH_ID)
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )
        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domain=TEST_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )
        lrandoms_response = blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        self.env.blackbox.set_response_side_effect('sign', [blackbox_sign_response()])

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setUp(self):
        self.patches = []
        # Мокаем сборку некоторых кук - ДО старта ViewTestEnvironment
        # Иначе придется переписывать пути для применения патчей
        self.setup_cookie_mocks()
        self.start_patches()

        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.default_headers = self.get_headers()

        self.setup_trackid_generator()

        self.setup_blackbox_responses(self.env)
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()

    def request_track(self):
        return dict(
            user_entered_login=TEST_ENTERED_PDD_LOGIN,
            retpath=TEST_CLEANED_PDD_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request = self.request_track()
        account = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request, account)

    def base_auth_log_entries(self):
        return {
            'login': TEST_ENTERED_PDD_LOGIN,
            'type': authtypes.AUTH_TYPE_WEB,
            'status': 'ses_create',
            'uid': str(TEST_PDD_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'comment': AuthEntry.format_comment_dict({
                'aid': TEST_AUTH_ID,
                'ttl': 5,
            }),
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }

    def get_expected_cookies(self, with_lah=True):
        specific = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_PDD_YANDEX_LOGIN_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_MDA2_BEACON_COOKIE,
        ]

        cookies = [
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        return sorted(specific + cookies)

    def get_expected_response(self, status='ok', cookies=None,
                              retpath=TEST_CLEANED_PDD_RETPATH, uid=TEST_PDD_UID,
                              domain=None, accounts=None, **kwargs):
        if domain is None:
            domain = {
                'punycode': TEST_DOMAIN,
                'unicode': TEST_DOMAIN,
            }
        if accounts is None:
            accounts = [
                {
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'uid': TEST_PDD_UID,
                    'display_login': TEST_PDD_LOGIN,
                },
            ]

        return self._get_expected_response(
            status=status,
            cookies=cookies,
            retpath=retpath,
            uid=uid,
            domain=domain,
            accounts=accounts,
            **kwargs
        )

    def get_expected_editsession_args(self):
        return {
            'keyspace': 'yandex.ru',
            'method': 'editsession',
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'uid': str(TEST_PDD_UID),
            'new_default': str(TEST_PDD_UID),
            'format': 'json',
            'host': TEST_HOST,
            'sessionid': u'0:old-session',
            'userip': TEST_IP,
            'op': 'add',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }

    def get_expected_createsession_args(self):
        return {
            'keyspace': 'yandex.ru',
            'method': 'createsession',
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'uid': str(TEST_PDD_UID),
            'format': 'json',
            'userip': TEST_IP,
            'ver': '3',
            'is_lite': '0',
            'ttl': '5',
            'host_id': '7f',
            'create_time': TimeNow(),
            'auth_time': TimeNow(as_milliseconds=True),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }

    def assert_response_ok(self, response, **kwargs):
        if 'display_login' not in kwargs:
            kwargs['display_login'] = TEST_PDD_LOGIN
            kwargs['login'] = TEST_PDD_LOGIN
        return super(BasePDDSubmitMultiAuthTestCase, self).assert_response_ok(response, **kwargs)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
    ALLOWED_PDD_HOSTS=TEST_ALLOWED_PDD_HOSTS,
    DISABLE_FAILED_CAPTCHA_LOGGING=False,
    FORCED_CHALLENGE_CHANCE=0.0,
    FORCED_CHALLENGE_PERIOD_LENGTH=3600,
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
)
class PDDSubmitMultiAuthTestCase(BasePDDSubmitMultiAuthTestCase):

    def test_auth__by_cookie__ok__with_allowed_retpath(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        retpath не модифицируем
        """
        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                retpath='http://a.yandex.ru/q/?a=b',
                exclude=['login', 'password'],
            ),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], 'http://a.yandex.ru/q/?a=b')
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_auth__by_cookie__ok__with_allowed_retpath__different_tld_with_passport(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        retpath не модифицируем
        """
        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                retpath='http://a.yandex.ru/q/?a=b',
                exclude=['login', 'password'],
            ),
            self.get_headers(host='passport.yandex.com'),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], 'http://a.yandex.ru/q/?a=b')
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_auth__by_cookie__ok__with_quoted_idna_domain_in_retpath(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        В retpath /for/quote(<idna domain>)
        """
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            authid=TEST_AUTH_ID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        quoted_domain = quote(TEST_IDNA_DOMAIN.encode('utf-8'))
        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                retpath='http://a.yandex.ru/for/%s' % quoted_domain,
                exclude=['login', 'password'],
            ),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], 'http://a.yandex.ru')
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_auth__by_cookie__ok__with_not_quoted_idna_domain_in_retpath(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        В retpath /for/<idna domain>
        """
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            authid=TEST_AUTH_ID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                retpath='http://a.yandex.ru/for/%s' % TEST_IDNA_DOMAIN,
                exclude=['login', 'password'],
            ),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], 'http://a.yandex.ru')
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_auth__by_cookie__ok__without_retpath_for_idna_domain(self):
        """
        Все проходит без ошибок по пути с валидной сессионной кукой без пароля и логина
        Пользователю сообщают "все ОК" и никаких кук не устанавливают
        retpath в ответе не меняется
        """
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            authid=TEST_AUTH_ID,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                exclude=['login', 'password'],
            ),
            self.default_headers,
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['clean'], 'yes')
        eq_(resp['retpath'], TEST_CLEANED_PDD_RETPATH)
        eq_(resp['fretpath'], TEST_FRETPATH)
        self.not_authorized()

    def test_pdd_auth__idna_encoded_login__ok(self):
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                login=TEST_CYRILLIC_PDD_LOGIN,
                aliases={
                    'pdd': TEST_CYRILLIC_PDD_LOGIN,
                },
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domain=TEST_IDNA_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        login = u'%s@%s' % (TEST_PDD_LOGIN, TEST_IDNA_DOMAIN)
        retpath = u'%s/for/%s/' % (TEST_RETPATH, TEST_IDNA_DOMAIN)
        resp = self.make_request(
            self.query_params(
                login=login,
                retpath=retpath,
            ),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        eq_(
            json.loads(resp.data)['account']['domain'],
            {
                'punycode': TEST_PUNYCODE_DOMAIN,
                'unicode': TEST_IDNA_DOMAIN,
            },
        )
        self.assert_track_ok(
            retpath=TEST_CLEANED_PDD_RETPATH,
            user_entered_login=login,
            login=TEST_CYRILLIC_PDD_LOGIN,
        )
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    login=login.encode('utf-8'),
                    retpath=TEST_CLEANED_PDD_RETPATH.encode('utf-8'),
                ),
            ],
        )

    def test_pdd_punycode_success(self):
        login_response = blackbox_login_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
            # и есть персональная информация + КВ/КО
            subscribed_to=[102],
            crypt_password='1:pwd',
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )

        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domain=TEST_IDNA_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        retpath = u'%s/for/%s/' % (TEST_RETPATH, TEST_PUNYCODE_DOMAIN)
        resp = self.make_request(
            self.query_params(
                login=TEST_CYRILLIC_PDD_LOGIN,
                retpath=retpath,
            ),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        eq_(
            json.loads(resp.data)['account']['domain'],
            {
                'punycode': TEST_PUNYCODE_DOMAIN,
                'unicode': TEST_IDNA_DOMAIN,
            },
        )
        self.assert_track_ok(
            retpath=TEST_CLEANED_PDD_RETPATH,
            user_entered_login=TEST_CYRILLIC_PDD_LOGIN,
            login=TEST_CYRILLIC_PDD_LOGIN,
        )
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_create',
                    login=TEST_CYRILLIC_PDD_LOGIN.encode('utf-8'),
                    retpath=TEST_CLEANED_PDD_RETPATH,
                ),
            ],
        )

    def test_pdd_success_retpath_not_allowed_no_fix(self):
        """
        Удостовермися, что больше не фиксим невалидные retpath при включенной мультиавторизации
        """
        expected_retpath = 'http://gmail.yandex.ru'
        resp = self.make_request(self.query_params(retpath='http://gmail.yandex.ru'), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            retpath=expected_retpath,
        )
        self.assert_track_ok(retpath=expected_retpath)

    def test_pdd_success_without_retpath(self):
        resp = self.make_request(self.query_params(retpath=None), self.default_headers)
        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            retpath=None,
        )
        self.assert_track_ok(retpath=None)

    def test_pdd_success_correct_retpath(self):
        resp = self.make_request(self.query_params(retpath=TEST_PDD_RETPATH), self.default_headers)

        self.assert_response_ok(resp, cookies=self.get_expected_cookies())
        self.assert_track_ok()

    def test_pdd_success_correct_retpath_with_last_slash(self):
        retpath = 'https://wordstat.yandex.ru/#!/?words=bla'
        resp = self.make_request(self.query_params(retpath=retpath), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            retpath=retpath,
        )
        self.assert_track_ok(retpath=retpath)

    def test_pdd_clean_retpath_with_last_slash(self):
        retpath = 'https://wordstat.yandex.ru/for/domain/?words=bla'
        cleaned_retpath = 'https://wordstat.yandex.ru/?words=bla'
        resp = self.make_request(self.query_params(retpath=retpath), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            retpath=cleaned_retpath,
        )
        self.assert_track_ok(retpath=cleaned_retpath)

    def test_pdd_clean_retpath_without_last_slash(self):
        retpath = 'https://wordstat.yandex.ru/for/domain?words=bla'
        cleaned_retpath = 'https://wordstat.yandex.ru?words=bla'
        resp = self.make_request(self.query_params(retpath=retpath), self.default_headers)

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            retpath=cleaned_retpath,
        )
        self.assert_track_ok(retpath=cleaned_retpath)

    def test_pdd_success_correct_idna_retpath(self):
        login_response = blackbox_login_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            subscribed_to=[102],
            crypt_password='1:pwd',
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )
        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domain=TEST_IDNA_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        retpath = u'%s' % TEST_RETPATH
        resp = self.make_request(self.query_params(retpath=retpath), self.default_headers)
        eq_(
            json.loads(resp.data)['account']['domain'],
            {
                'punycode': TEST_PUNYCODE_DOMAIN,
                'unicode': TEST_IDNA_DOMAIN,
            },
        )
        self.assert_track_ok(retpath=retpath, login=TEST_CYRILLIC_PDD_LOGIN)

    def test_pdd_auth__account_need_completion_and_password_creation__complete_pdd_with_password_state(self):
        """Не полноценный ПДД-пользователь - не согласился с лицензией (sid=102) и нужен пароль"""
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                # Не принял условия лицензии (sid=102)
                subscribed_to=[],
                crypt_password='',
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                    # Указание что нужна "дорегистрация"
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                },
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_pdd_with_password')
        ok_('hint' in resp['account'])
        eq_(
            resp['account']['hint'],
            {
                'question': {
                    'id': 99,
                    'text': u'вопрос',
                },
                'answer': u'ответ',
            },
        )

        self.assert_track_ok(have_password=False, is_captcha_required=True)

    def test_pdd_auth__account_need_completion_without_control_question__complete_pdd_state(self):
        """У ПДД-пользователя нет КВ/КО -> его нужно дорегистрировать"""
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                # Нет КВ/КО
                dbfields={},
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_pdd')
        ok_('hint' not in resp['account'])

        self.assert_track_ok(have_password=True, is_captcha_required=True)

    def test_pdd_auth__account_need_competion_and_password_changing__complete_pdd_with_password_state(self):
        """Не полноценный ПДД-пользователь - не согласился с лицензией (sid=102)
        Кроме того, установлен флаг 'нужно сменить пароль'"""
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                subscribed_to=[],
                dbfields={
                    'subscription.login_rule.8': 4,
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
                attributes={
                    'password.forced_changing_reason': '1',
                },
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_pdd_with_password')
        ok_('hint' in resp['account'])
        eq_(
            resp['account']['hint'],
            {
                'question': {
                    'id': 99,
                    'text': u'вопрос',
                },
                'answer': u'ответ',
            },
        )

        self.assert_track_ok(have_password=True, is_captcha_required=True)

    def test_pdd_auth__account_need_change_password_but_can_change_password_option_is_false__password_change_forbidden_state(self):
        """Пользователь ПДД проходит по сценарию с верным паролем"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **self.get_blackbox_login_response_params(
                    subscribed_to=[102],
                    dbfields={
                        # Третий бит на восьмом сиде - нужна смена пароля
                        'subscription.login_rule.8': 4,
                        'userinfo_safe.hintq.uid': u'99:вопрос',
                        'userinfo_safe.hinta.uid': u'ответ',
                    },
                    attributes={
                        'password.forced_changing_reason': '1',
                    },
                )
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'password_change_forbidden')

    def test_pdd_auth__strong_password__2fa_is_enabled(self):
        """Пользователь ПДД проходит по сценарию с totp и у него нет пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **self.get_blackbox_login_response_params(
                    subscribed_to=[67, 102],
                    dbfields={
                        'userinfo_safe.hintq.uid': u'99:вопрос',
                        'userinfo_safe.hinta.uid': u'ответ',
                    },
                    attributes={
                        'account.2fa_on': '1',
                        'account.totp.secret': 'secret',
                        'account.totp.secret_ids': '0:0',
                        'account.totp.pin_length': '5',
                    },
                    crypt_password=None,
                )
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.assert_track_ok(
            retpath=TEST_CLEANED_PDD_RETPATH,
            login=TEST_PDD_LOGIN,
            is_strong_password_policy_required=True,
        )

    def test_pdd_auth__need_change_passwd_by_strong_passwd_policy_but_can_change_password_option_is_false__password_change_forbidden_state(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **self.get_blackbox_login_response_params(
                    subscribed_to=[102, 67],
                    dbfields={
                        'password_quality.quality.uid': 50,
                        'userinfo_safe.hintq.uid': u'99:вопрос',
                        'userinfo_safe.hinta.uid': u'ответ',
                    },
                )
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        resp = self.make_request(self.query_params(password='abc'), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'password_change_forbidden')

        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[1][0][1], {
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_pdd_auth__password_expired_but_can_change_password_option_false__password_change_forbidden_state(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                bruteforce_policy=blackbox.BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'password_change_forbidden')
        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[1][0][1], {
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_pdd_auth__need_completion_and_can_change_password_option_is_true__complete_pdd_with_password_state(self):
        """У пользователя ПДД явно выставлен can_users_change_password=1 на домене"""
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password="1",
                domain=TEST_DOMAIN,
            ),
        )
        # FIXME: анти-паттерн вызов другого теста
        self.test_pdd_auth__account_need_completion_and_password_creation__complete_pdd_with_password_state()

    def test_pdd_auth__need_completion_and_options_have_bad_json__complete_pdd_with_password_state(self):
        """У пользователя ПДД в поле options кривой json"""
        hosted_domains_response = json.dumps({
            'hosted_domains': [{
                'options': 'bad json',
            }],
        })
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )
        # FIXME: анти-паттерн вызов другого теста
        self.test_pdd_auth__account_need_completion_and_password_creation__complete_pdd_with_password_state()
        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[1][0][1], {
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_pdd_auth__need_completion_and_passwd_change_but_can_change_password_option_is_false__complete_pdd_state(self):
        """Пользователю ПДД запрещено менять пароль на портале(can_users_change_password=0 на домене)"""
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                subscribed_to=[],
                dbfields={
                    'subscription.login_rule.8': 4,
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_pdd')
        self.assert_track_ok(have_password=True, is_captcha_required=True)

        check_url_contains_params(self.env.blackbox._mock.request.call_args_list[1][0][1], {
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_pdd_auth__need_pdd_completion__complete_pdd_state(self):
        # Не полноценный ПДД-пользователь - не согласился с лицензией (нет sid=102)
        login_response = blackbox_login_response(
            **self.get_blackbox_login_response_params(
                subscribed_to=[],
                dbfields={
                    'userinfo_safe.hintq.uid': u'99:вопрос',
                    'userinfo_safe.hinta.uid': u'ответ',
                },
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        resp = self.make_request(self.query_params(), self.default_headers)

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['state'], 'complete_pdd')
        ok_('hint' in resp['account'])
        eq_(
            resp['account']['hint'],
            {
                'question': {
                    'id': 99,
                    'text': u'вопрос',
                },
                'answer': u'ответ',
            },
        )

        self.assert_track_ok(have_password=True, is_captcha_required=True)

    def test_pdd_auth__pdd_user_cannot_subscribe_to_service__pass_silently(self):
        resp = self.make_request(self.query_params(service='friends'), self.default_headers)
        eq_(resp.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('attributes', 'subscription.26', uid=TEST_UID, db='passportdbshard1')
        track = self.track_manager.read(self.track_id)
        eq_(track.service, 'friends')

    def test_pdd_auth__with_is_pdd_param__ok_with_yandexru_crutch(self):
        pdd_login = '%s@%s' % (TEST_ENTERED_PDD_LOGIN, TEST_DOMAIN)
        resp = self.make_request(
            self.query_params(is_pdd='1', login=pdd_login),
            self.get_headers(cookie=EXPECTED_SESSIONID_COOKIE),
        )

        self.assert_response_ok(resp, cookies=self.get_expected_cookies())
        self.assert_track_ok(user_entered_login=pdd_login)

        assert len(self.env.blackbox.requests) == 4
        calls = self.env.blackbox.get_requests_by_method('hosted_domains')
        assert len(calls) == 1
        calls[0].assert_query_contains({'method': 'hosted_domains'})

        calls = self.env.blackbox.get_requests_by_method('sessionid')
        assert len(calls) == 1
        calls[0].assert_query_contains({'host': 'passport-test.yandex.ru'})

    def test_pdd_auth__with_is_pdd_param_and_plain_login__invalid_login_error(self):
        resp = self.make_request(
            self.query_params(is_pdd='1'),
            self.default_headers,
        )

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['login.invalid_format'])

    def test_pdd_auth__domain_is_not_hosted__error(self):
        hosted_domains_response = blackbox_hosted_domains_response(count=0)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )
        pdd_login = TEST_PDD_LOGIN
        resp = self.make_request(
            self.query_params(is_pdd='1', login=pdd_login),
            self.default_headers,
        )

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['domain.not_hosted'])

        check_url_contains_params(self.env.blackbox._mock.request.call_args[0][1], {
            'domain': TEST_DOMAIN,
            'method': 'hosted_domains',
        })

    def test_pdd_auth__only_eda_cookie__error_invalid_session(self):
        """Пришли только с eda_id при выставленном is_pdd"""
        """Отныне ломаемся"""

        resp = self.make_request(
            self.query_params(is_pdd='1', exclude=['login', 'password']),
            self.get_headers(cookie='Eda_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['sessionid.invalid'])

        self.assert_track_empty()

    def test_pdd_auth__empty_options__error(self):
        """Пустые options в ответе hosted_domains никак не влияют на выписывание кук"""

        hosted_domains_response = blackbox_hosted_domains_response(
            count=1, options_json='{}', domain=TEST_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        pdd_login = TEST_PDD_LOGIN
        resp = self.make_request(
            self.query_params(is_pdd='1', login=pdd_login),
            self.default_headers,
        )
        eq_(resp.status_code, 200)
        self.assert_response_ok(resp, cookies=self.get_expected_cookies())
        self.assert_track_ok(user_entered_login=pdd_login)

    def test_pdd_account_with_validation_method_captcha_not_phone(self):
        """
        Для пользователей специального вида всегда выдаём метод валидации через капчу,
        а не через телефон, потому что им запрещено привязывать защищённый номер телефона
        """
        with settings_context(
            DISABLE_CHANGE_PASSWORD_PHONE_EXPERIMENT=False,
        ):
            login_response = blackbox_login_response(
                **self.get_blackbox_login_response_params(
                    subscribed_to=[102],
                    dbfields={
                        'subscription.login_rule.8': 4,
                        'userinfo_safe.hintq.uid': u'99:вопрос',
                        'userinfo_safe.hinta.uid': u'ответ',
                    },
                    attributes={
                        'password.forced_changing_reason': '1',
                    },
                )
            )
            self.env.blackbox.set_blackbox_response_value(
                'login',
                login_response,
            )

            resp = self.make_request(self.query_params(), self.default_headers)

            eq_(resp.status_code, 200)

            resp = json.loads(resp.data)
            eq_(resp['status'], 'ok')
            eq_(resp['state'], 'change_password')
            eq_(resp['change_password_reason'], 'account_hacked')
            eq_(resp['validation_method'], 'captcha_and_phone')
            self.assertNotIn('number', resp)
            self.assert_track_ok(
                user_entered_login=TEST_ENTERED_PDD_LOGIN,
                is_password_change=True,
                is_captcha_required=True,
                is_captcha_checked=None,
                is_captcha_recognized=None,
                has_secure_phone_number=None,
                can_use_secure_number_for_password_validation=False,
                secure_phone_number=None,
                is_change_password_sms_validation_required=True,
                retpath=TEST_CLEANED_PDD_RETPATH,
            )
            track = self.track_manager.read(self.track_id)
            ok_(track.password_hash)

            self.assert_validation_method_recorded_to_statbox(
                uid=TEST_PDD_UID,
                validation_method='captcha_and_phone',
            )

    def test_pdd_auth_by_passwd_with_eda_cookie__ok(self):
        """
        Пользователь ПДД проходит по сценарию с верным паролем,
        включенной мультиавторизацией и eda кукой.
        Удостоверимся, что не читаем eda.
        """
        login = TEST_PDD_LOGIN
        resp = self.make_request(
            self.query_params(
                is_pdd='1',
                login=login,
            ),
            self.get_headers(cookie='Eda_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            accounts=[
                {
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'uid': TEST_PDD_UID,
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
        )
        assert len(self.env.blackbox.requests) == 3
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains(self.get_expected_createsession_args())

        self.assert_track_ok(user_entered_login=login)
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(status='ses_create', login=login),
            ],
        )

    def test_pdd_auth_by_passwd_with_no_cookies__ok(self):
        """
        Пользователь ПДД проходит по сценарию с верным паролем
        и включенной мультиавторизацией.
        """
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        assert len(self.env.blackbox.requests) == 3
        calls = self.env.blackbox.get_requests_by_method('createsession')
        assert len(calls) == 1
        calls[0].assert_query_contains(self.get_expected_createsession_args())

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            accounts=[
                {
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'uid': TEST_PDD_UID,
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
        )
        self.assert_track_ok()
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(),
            ],
        )

    def test_pdd_auth_by_passwd_with_foreign_cookies__ok(self):
        """
        Пользователь ПДД проходит по сценарию с верным паролем,
        включенной мультиавторизацией и чужой кукой. Добавляем его.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login@other_domain',
                authid=TEST_OLD_AUTH_ID,
                ttl=5,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            self.get_headers(cookie='Session_id=0:old-session;yandexuid=%s' % TEST_YANDEXUID_COOKIE),
        )

        assert len(self.env.blackbox.requests) == 4
        calls = self.env.blackbox.get_requests_by_method('sessionid')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'sessionid': '0:old-session',
            'multisession': 'yes',
        })

        calls = self.env.blackbox.get_requests_by_method('editsession')
        assert len(calls) == 1
        calls[0].assert_query_contains(self.get_expected_editsession_args())

        self.assert_response_ok(
            resp,
            cookies=self.get_expected_cookies(),
            accounts=[
                {
                    'login': 'other_login@other_domain',
                    'display_name': {'name': '', 'default_avatar': ''},
                    'uid': 1234,
                    'display_login': 'other_login@other_domain',
                },
                {
                    'login': TEST_PDD_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'uid': TEST_PDD_UID,
                    'display_login': TEST_PDD_LOGIN,
                },
            ],
        )
        self.assert_track_ok()
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    status='ses_update',
                    uid='1234',
                    comment='aid=%s;ttl=5' % TEST_AUTH_ID,
                    retpath=TEST_CLEANED_PDD_RETPATH,
                    login='other_login@other_domain',
                ),
                self.build_auth_log_entries(),
            ],
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
    ALLOWED_PDD_HOSTS=TEST_ALLOWED_PDD_HOSTS,
    DISABLE_FAILED_CAPTCHA_LOGGING=False,
    FORCED_CHALLENGE_CHANCE=0.0,
    FORCED_CHALLENGE_PERIOD_LENGTH=3600,
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
)
class SubmitAuthMultiPDDIntegrationalTestCase(BaseSubmitAuthViewTestCase):
    """Большой интеграционный тест ручки submit для ПДД-пользователя cо включенной мультиавторизацией"""

    def get_base_query_params(self):
        return {
            'login': TEST_ENTERED_PDD_LOGIN,
            'password': TEST_PASSWORD,

            'retpath': TEST_PDD_RETPATH,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def request_track(self):
        return dict(
            user_entered_login=TEST_ENTERED_PDD_LOGIN,
            retpath=TEST_CLEANED_PDD_RETPATH,
            origin=TEST_ORIGIN,
            authorization_session_policy=AUTHORIZATION_SESSION_POLICY_PERMANENT,
            fretpath=TEST_FRETPATH,
            clean='yes',
        )

    def base_track(self):
        """Поля в треке и их нормальные значения"""
        request_data = self.request_track()
        account_data = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            language=TEST_USER_LANGUAGE,
            # Всякое специфичное
            is_strong_password_policy_required=False,
        )
        return merge_dicts(request_data, account_data)

    def setup_blackbox_responses(self, env):
        # Полноценный ПДД-пользователь
        login_response = blackbox_login_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            subscribed_to=[102],
            crypt_password='1:pwd',
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        lrandoms_response = blackbox_lrandoms_response()
        env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
        )
        env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        createsession_response = blackbox_createsession_response()
        env.blackbox.set_blackbox_response_value(
            'createsession',
            createsession_response,
        )

        hosted_domains_response = blackbox_hosted_domains_response(count=1, domain=TEST_DOMAIN)
        env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )

        self.env.blackbox.set_response_side_effect('sign', [blackbox_sign_response()])

    def setUp(self):
        self.patches = []

        self.setup_env()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.default_headers = self.get_headers(cookie='yandexuid=' + TEST_YANDEXUID_COOKIE)

        self.setup_trackid_generator()

        self.setup_blackbox_responses(self.env)
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()

        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()

    def assert_editsession_called(self):
        assert len(self.env.blackbox.requests) == 6
        calls = self.env.blackbox.get_requests_by_method('editsession')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'keyspace': 'yandex.ru',
            'method': 'editsession',
            'lang': '1',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'uid': str(TEST_PDD_UID),
            'new_default': str(TEST_PDD_UID),
            'format': 'json',
            'host': TEST_HOST,
            'sessionid': u'0:old-session',
            'userip': TEST_IP,
            'op': 'add',
            'sslsessionid': '0:old-sslsession',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru,test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        })

    def test_pdd_auth__by_passwd__ok(self):
        """Авторизация и установка кук для ПДД-пользователя на латинском домене"""
        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            resp,
            self.get_expected_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                retpath=TEST_CLEANED_PDD_RETPATH,
                domain={
                    'unicode': TEST_DOMAIN,
                    'punycode': TEST_DOMAIN,
                },
                display_login=TEST_PDD_LOGIN,
                accounts=[
                    {
                        'login': TEST_PDD_LOGIN,
                        'uid': TEST_PDD_UID,
                        'display_name': {'name': '', 'default_avatar': ''},
                        'display_login': TEST_PDD_LOGIN,
                    },
                ],
                default_uid=TEST_PDD_UID,
            ),
        )

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    uid=str(TEST_PDD_UID),
                    status='ses_create',
                    retpath=TEST_CLEANED_PDD_RETPATH,
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

        eq_(
            len(cookies),
            8,
            'After PDD-auth, there should be these cookies: Session_id, sessionid2, L, lah, yp, ys, yandex_login, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessionid2, yandexlogin_cookie, yp_cookie, ys_cookie = cookies

        self.assert_cookie_ok(l_cookie, 'L', )
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        self.assert_blackbox_createsesion_call()

        self.assert_track_ok()

    def test_pdd_auth__by_passwd_cyrillic_domain__cookies_on_quoted_path(self):
        """Авторизация и установка кук для ПДД-пользователя на кирилическом домене"""
        login_response = blackbox_login_response(
            uid=TEST_PDD_UID,
            login=TEST_CYRILLIC_PDD_LOGIN,
            aliases={
                'pdd': TEST_CYRILLIC_PDD_LOGIN,
            },
            crypt_password='1:pwd',
            subscribed_to=[102],
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            login_response,
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            len(cookies),
            8,
            'After PDD-auth, there should be these cookies: Session_id, Sessionid2, L, lah, yp, ys, yandex_login, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessionid2, yandexlogin_cookie, yp_cookie, ys_cookie = cookies

        self.assert_cookie_ok(l_cookie, 'L', )
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        self.assert_blackbox_createsesion_call()

    def test_pdd_auth__https_by_passwd__with_other_account__ok(self):
        """
        Авторизация и установка безопасных кук для ПДД-пользователя на латинском домене
        по хттпс и с мультикукой, в которой есть другой пользователь
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='123',
                login='other_login',
                ttl=5,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

        resp = self.make_request(
            self.query_params(),
            self.get_headers(
                cookie='Session_id=0:old-session;sessionid2=0:old-sslsession;yandexuid=' + TEST_YANDEXUID_COOKIE,
            ),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            resp,
            self.get_expected_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                retpath=TEST_CLEANED_PDD_RETPATH,
                domain={
                    'unicode': TEST_DOMAIN,
                    'punycode': TEST_DOMAIN,
                },
                display_login=TEST_PDD_LOGIN,
                accounts=[
                    {
                        'login': 'other_login',
                        'display_name': {'name': '', 'default_avatar': ''},
                        'uid': 123,
                        'display_login': 'other_login',
                    },
                    {
                        'login': TEST_PDD_LOGIN,
                        'uid': TEST_PDD_UID,
                        'display_name': {'name': '', 'default_avatar': ''},
                        'display_login': TEST_PDD_LOGIN,
                    },
                ],
                default_uid=TEST_PDD_UID,
            ),
        )

        eq_(
            len(cookies),
            8,
            'After PDD-auth, there should be these cookies: Session_id, sessionid2, L, lah, yp,'
            ' ys, yandex_login, mda2_beacon. But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessionid2_cookie, yandexlogin_cookie, yp_cookie, ys_cookie = cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        assert len(self.env.blackbox.requests) == 6
        calls = self.env.blackbox.get_requests_by_method('sessionid')
        assert len(calls) == 1
        calls[0].assert_query_contains({
            'method': 'sessionid',
            'multisession': 'yes',
            'format': 'json',
            'authid': 'yes',
            'regname': 'yes',
            'get_public_name': 'yes',
            'is_display_name_empty': 'yes',
            'get_login_id': 'yes',
            'host': 'passport-test.yandex.ru',
            'sslsessionid': '0:old-sslsession',
            'sessionid': '0:old-session',
            'full_info': 'yes',
            'userip': '3.3.3.3',
            'aliases': 'all_with_hidden',
            'guard_hosts': 'passport-test.yandex.ru',
            'request_id': mock.ANY,
        })
        self.assert_editsession_called()
        self.assert_track_ok()

    def test_pdd_auth__by_passwd__ok__with_extra_sessguard(self):
        """Авторизация и установка кук для ПДД-пользователя на латинском домене с дополнительным sessguard для поддомена """
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                sessguard_hosts=['passport-test.yandex.ru', TEST_RETPATH_HOST],
            ),
        )
        self.env.blackbox.set_response_side_effect(
            'sign',
            [
                blackbox_sign_response(),
                blackbox_sign_response(),
            ],
        )

        resp = self.make_request(self.query_params(), self.default_headers)
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        cookies = sorted(resp.pop('cookies', []))

        eq_(
            resp,
            self.get_expected_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                retpath=TEST_CLEANED_PDD_RETPATH,
                domain={
                    'unicode': TEST_DOMAIN,
                    'punycode': TEST_DOMAIN,
                },
                display_login=TEST_PDD_LOGIN,
                accounts=[
                    {
                        'login': TEST_PDD_LOGIN,
                        'uid': TEST_PDD_UID,
                        'display_name': {'name': '', 'default_avatar': ''},
                        'display_login': TEST_PDD_LOGIN,
                    },
                ],
                default_uid=TEST_PDD_UID,
                service_guard_container='123.abc',
            ),
        )

        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    uid=str(TEST_PDD_UID),
                    status='ses_create',
                    retpath=TEST_CLEANED_PDD_RETPATH,
                    comment=AuthEntry.format_comment_dict({
                        'aid': TEST_AUTH_ID,
                        'ttl': 5,
                    }),
                ),
            ],
        )

        eq_(
            len(cookies),
            9,
            'After PDD-auth with sessguard, there should be these cookies: Session_id, sessionid2, sessguard, L, lah, yp, ys, yandex_login, mda2_beacon. '
            'But presented: %s' % cookies,
        )
        # Все куки в комплекте - проверим их содержимое
        l_cookie, sessionid_cookie, lah_cookie, mda2_beacon, sessguard, sessionid2, yandexlogin_cookie, yp_cookie, ys_cookie = cookies

        self.assert_cookie_ok(l_cookie, 'L', )
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)
        self.assert_cookie_ok(sessguard, 'sessguard', expires=None, domain='.passport-test.yandex.ru', secure=True, http_only=True)

        self.assert_blackbox_createsesion_call()

        self.assert_track_ok()
