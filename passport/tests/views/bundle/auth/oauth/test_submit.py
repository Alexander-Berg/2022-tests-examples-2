# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.api.views.bundle.constants import PDD_PARTNER_OAUTH_TOKEN_SCOPE
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.base.faker.fake_builder import (
    assert_builder_requested,
    assert_builder_url_contains_params,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_lrandoms_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import deep_merge
from six.moves.urllib.parse import quote


eq_ = iterdiff(eq_)

TEST_HOST = 'passport.yandex.ru'
TEST_HINT_QUESTION = u'вопрос'
TEST_HINT_QUESTION_ID = 99
TEST_HINT_QUESTION_SERIALIZED = '%d:%s' % (TEST_HINT_QUESTION_ID, TEST_HINT_QUESTION)
TEST_HINT_ANSWER = u'ответ'
TEST_WEAK_PASSWORD_HASH = '1:$1$y0aXFE9w$JqrpPZ74WT1Hi/Mb53cTe.'
TEST_USER_AGENT = 'curl'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_URLQUOTED_DOMAIN = quote(TEST_IDNA_DOMAIN.encode('utf-8'))
TEST_CLEANED_PDD_RETPATH = 'https://mail.yandex.ru'
TEST_DEFAULT_PDD_RETPATH = 'https://mail.yandex.ru/'
TEST_PDD_CYRILIC_DOMAIN_RETPATH = 'http://mail.yandex.ru/for/%s' % TEST_IDNA_DOMAIN
TEST_AUTH_ID = '123:1422501443:126'
TEST_OLD_AUTH_ID = '111:1111111111:111'

TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_YANDEX_GID_COOKIE = 'cookie_yandex_gid'
TEST_USER_COOKIES = 'yandexuid=%s; yandex_gid=%s;' % (
    TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE,
)
TEST_OLD_SESSION_VALUE = 'test-session-value'

SESSION = {
    'session': {
        'domain': '.yandex.ru',
        'expires': 0,
        'value': '2:session',
    },
    'sslsession': {
        'domain': '.yandex.ru',
        'expires': 1370874827,
        'value': '2:sslsession',
    },
}

EXPECTED_SESSIONID_COOKIE = ('Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/'
                             % SESSION['session'])
EXPECTED_SESSIONID_SECURE_COOKIE = ('sessionid2=%(value)s; Domain=%(domain)s; '
                                    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
                                    % SESSION['sslsession'])

EXPECTED_YANDEX_LOGIN_COOKIE = u'yandex_login=%s@%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/' % (
    TEST_LOGIN, TEST_DOMAIN,
)

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Path=/' % COOKIE_YS_VALUE

EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % TEST_COOKIE_L

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_OAUTH_TOKEN = 'Test_token-123'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_TOKEN
TEST_OAUTH_SCOPE = PDD_PARTNER_OAUTH_TOKEN_SCOPE


def build_headers(host=None, user_ip=None, cookie=None,
                  authorization=TEST_OAUTH_HEADER):
    headers = mock_headers(
        host=host or TEST_HOST,
        user_ip=user_ip or TEST_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=cookie or TEST_USER_COOKIES,
        accept_language=TEST_ACCEPT_LANGUAGE,
        authorization=authorization,
    )
    return headers


class BaseOAuthTestCase(BaseBundleTestViews):

    def start_patches(self):
        """Запускаем mocks"""
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        """
        Здесь мы останавливаем все зарегистрированные ранее mocks
        """
        for patch in self.patches:
            patch.stop()

    def setUp(self):
        self.patches = []
        self.setup_cookie_mocks()
        self.start_patches()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_trackid_generator()
        self.setup_statbox_templates()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_oauth': ['base']}),
        )

    def tearDown(self):
        self.env.stop()
        self.stop_patches()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        del self.build_cookie_l
        del self.build_cookie_lah
        del self.build_cookies_yx

    def query_params(self, **kwargs):
        params = {
            'type': 'trusted-pdd-partner',
            'retpath': TEST_CLEANED_PDD_RETPATH,
        }
        params.update(kwargs)
        return params

    def make_request(self, query_params, headers):
        return self.env.client.post(
            '/1/bundle/auth/oauth/?consumer=dev',
            data=query_params,
            headers=headers,
        )

    def setup_blackbox_good_oauth_response(self, login=TEST_PDD_LOGIN, uid=TEST_PDD_UID, **kwargs):
        """Ответ о полноценном ПДД пользователе, которому разрешен вход"""
        subscribed_to = kwargs.get('subscribed_to') or [102]
        dbfields = kwargs.get('dbfields') or {
            'userinfo_safe.hintq.uid': '%s:%s' % (TEST_HINT_QUESTION_ID, TEST_HINT_QUESTION),
            'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
        }
        phone_bound = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        kwargs = deep_merge(kwargs, phone_bound)
        attributes = deep_merge(
            kwargs.pop('attributes', {}),
            {
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=login,
                aliases={
                    'pdd': login,
                },
                uid=uid,
                scope=TEST_OAUTH_SCOPE,
                subscribed_to=subscribed_to,
                dbfields=dbfields,
                attributes=attributes,
                **kwargs
            ),
        )

    def setup_blackbox_lrandoms_response(self):
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

    def setup_blackbox_hosted_domains_response(self, count=1, can_users_change_password='1', domain=TEST_DOMAIN):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=count,
                can_users_change_password=can_users_change_password,
                domain=domain,
            ),
        )

    def setup_trackid_generator(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            yandexuid=TEST_YANDEXUID_COOKIE,
            track_id=self.track_id,
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
            mode='any_auth',
            type='oauth',
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _inherit_from='local_base',
            uid=str(TEST_PDD_UID),
            input_login=TEST_PDD_LOGIN,
            mode='any_auth',
            cookie_version=str(settings.BLACKBOX_SESSION_VERSION),
            action='cookie_set',
            ttl=None,
            authid=TEST_AUTH_ID,
            session_method='create',
            uids_count='1',
            ip_country='us',
            person_country='ru',
            captcha_passed=False,
        )
        self.env.statbox.bind_entry(
            'failed',
            _inherit_from='local_base',
            action='failed',
            mode='any_auth',
            type='oauth',
        )
        self.env.statbox.bind_entry(
            'defined_validation_method',
            action='defined_validation_method',
            mode='change_password_force',
            uid=str(TEST_PDD_UID),
            track_id=self.track_id,
        )

    def get_expected_account(self, uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, domain=None, hint=None, **kwargs):
        account = {
            'uid': uid,
            'login': login,
            'domain': {
                'punycode': TEST_DOMAIN,
                'unicode': TEST_DOMAIN,
            },
            'display_name': {
                'name': '',
                'default_avatar': '',
            },
            'person': {
                'firstname': u'\\u0414',
                'lastname': u'\\u0424',
                'birthday': '1963-05-15',
                'gender': 1,
                'language': 'ru',
                'country': 'ru',
            },
            'display_login': '%s@%s' % (TEST_LOGIN, domain or TEST_DOMAIN),
        }
        if domain is not None:
            account.update(
                domain={
                    'punycode': domain.encode('idna'),
                    'unicode': domain,
                },
            )
        if hint is not None:
            account.update(
                hint={
                    'answer': TEST_HINT_ANSWER,
                    'question': {
                        'text': TEST_HINT_QUESTION,
                        'id': TEST_HINT_QUESTION_ID,
                    },
                },
            )
        account.update(kwargs)
        return account

    def get_expected_response(self, **kwargs):
        params = {
            'status': 'ok',
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'track_id': self.track_id,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'cookies': self.get_expected_cookies(),
            'default_uid': TEST_PDD_UID,
            'account': self.get_expected_account(),
            'accounts': [self.get_expected_short_account()],
        }
        params.update(kwargs)
        return params

    def assert_response__ok(self, response, expected=None):
        expected = expected or self.get_expected_response()
        eq_(response.status_code, 200)
        data = json.loads(response.data)
        if 'cookies' in data:
            data['cookies'] = sorted(data['cookies'])
        eq_(
            data,
            expected,
        )

    def assert_response__error(self, response, errors):
        eq_(response.status_code, 200)
        eq_(
            json.loads(response.data),
            {
                'status': 'error',
                'errors': errors,
            },
        )

    def assert_track__ok(self, uid=TEST_PDD_UID, cache=None,
                         have_password=True, secure_phone=None, domain=TEST_DOMAIN,
                         retpath=TEST_CLEANED_PDD_RETPATH):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        eq_(track.login, TEST_PDD_LOGIN)
        # Только ПДД
        eq_(track.domain, domain.encode('idna'))
        eq_(track.human_readable_login, '%s@%s' % (TEST_LOGIN, domain))
        eq_(track.machine_readable_login, '%s@%s' % (TEST_LOGIN, domain.encode('idna')))

        if have_password:
            eq_(track.have_password, True)
        else:
            eq_(track.have_password, False)
        eq_(track.is_password_passed, False)
        eq_(track.retpath, retpath)
        if cache:
            eq_(track.submit_response_cache, cache)
        if secure_phone:
            eq_(track.can_use_secure_number_for_password_validation, True)
            eq_(track.secure_phone_number, secure_phone)
        else:
            ok_(not track.can_use_secure_number_for_password_validation)

    def assert_statbox_logged__ok(self, ttl=5,
                                  captcha_passed=False, old_session_uids=None,
                                  retpath=None):
        auth_entry = self.env.statbox.entry(
            'cookie_set',
            ttl=str(ttl),
            captcha_passed=tskv_bool(captcha_passed),
            retpath=retpath,
        )
        if old_session_uids:
            auth_entry['old_session_uids'] = old_session_uids

        expected = [
            self.env.statbox.entry('submitted'),
            auth_entry,
        ]
        self.check_statbox_log_entries(self.env.statbox_handle_mock, expected)

    def assert_error_statboxed(self, error):
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('failed', error=error),
            ],
        )

    def assert_historydb_logged__ok(self, status='ses_create'):
        expected = [
            ('login', TEST_PDD_LOGIN),
            ('type', authtypes.AUTH_TYPE_OAUTH),
            ('status', status),
            ('uid', str(TEST_PDD_UID)),
            ('useragent', TEST_USER_AGENT),
            ('yandexuid', TEST_YANDEXUID_COOKIE),
            ('comment', 'aid=123:1422501443:126;ttl=5'),
        ]
        self.check_auth_log_entries(self.env.auth_handle_mock, expected)

    def assert_blackbox_called(self):
        assert_builder_requested(self.env.blackbox)
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'method': 'oauth',
                'oauth_token': TEST_OAUTH_TOKEN,
                'userip': TEST_IP,
            },
            callnum=0,
        )

    def assert_phone_logged(self, uid=TEST_PDD_UID, phone=TEST_PHONE_NUMBER.e164,
                            yandexuid=TEST_YANDEXUID_COOKIE):
        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(uid, phone, yandexuid),
        ])

    def setup_blackbox_sessionid_multi_response(self, login=TEST_ANOTHER_LOGIN, uid=TEST_UID, **kwargs):
        response = blackbox_sessionid_multi_response(
            login=login,
            uid=uid,
            **kwargs
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            response,
        )

    def setup_blackbox_createsession_response(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                ip=TEST_IP,
                session_value=SESSION['session']['value'],
                ssl_session_value=SESSION['sslsession']['value'],
            ),
        )

    def setup_blackbox_edit_session_response(self):
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                default_uid=TEST_PDD_UID,
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )

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

    def get_expected_cookies(self, with_lah=True, with_mda2_beacon=True):
        """Получаем комплект кук без ПДД-специфичных"""
        cookies = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_YP_COOKIE,
        ]
        if with_lah:
            cookies.append(EXPECTED_LAH_COOKIE)
        if with_mda2_beacon:
            cookies.append(EXPECTED_MDA2_BEACON_COOKIE)

        cookies.append(EXPECTED_SESSIONID_SECURE_COOKIE)

        return sorted(cookies)

    def get_expected_short_account(self, uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, display_login=None):
        return {
            'uid': uid,
            'login': login,
            'display_name': {'name': '', 'default_avatar': ''},
            'display_login': login if display_login is None else display_login,
        }

    def assert_create_session_called(self, call_index, extra_guard_host=None):
        # method=createsession
        url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host:
            guard_hosts.append(extra_guard_host)
        check_all_url_params_match(
            url,
            {
                'method': 'createsession',
                'uid': str(TEST_PDD_UID),
                'lang': '1',
                'have_password': '1',
                'ver': '3',
                'format': 'json',
                'keyspace': 'yandex.ru',
                'is_lite': '0',
                'ttl': '5',
                'userip': TEST_IP,
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': ','.join(guard_hosts),
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_edit_session_called(self, call_index, operation='add', ssl_session=None, uid=TEST_PDD_UID, extra_guard_host=None):
        # method=editsession
        url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        guard_hosts = ['passport-test.yandex.ru']
        if extra_guard_host:
            guard_hosts.append(extra_guard_host)
        args = {
            'sessionid': TEST_OLD_SESSION_VALUE,
            'method': 'editsession',
            'op': operation,
            'uid': str(uid),
            'format': 'json',
            'userip': TEST_IP,
            'host': TEST_HOST,
            'create_time': TimeNow(),
            'guard_hosts': ','.join(guard_hosts),
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if operation == 'add':
            args.update({
                'lang': '1',
                'have_password': '1',
                'keyspace': 'yandex.ru',
                'new_default': str(uid),
            })
        if ssl_session:
            args['sslsessionid'] = ssl_session
        check_all_url_params_match(url, args)

    def assert_authlog_records(self, expected_records):
        """Произошел один вызов логгера авторизации - обновление сессии пользователя"""
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )

    def base_auth_log_entries(self, auth_type=authtypes.AUTH_TYPE_OAUTH):
        return {
            'login': TEST_PDD_LOGIN,
            'type': auth_type,
            'status': 'ses_create',
            'uid': str(TEST_PDD_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'comment': 'aid=%s;ttl=0' % TEST_AUTH_ID,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }

    def build_auth_log_entries(self, **kwargs):
        entries = self.base_auth_log_entries()
        entries.update(kwargs)
        return entries.items()


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    DEFAULT_PDD_RETPATH_WITHOUT_TLD='https://mail.yandex.%s/',
    PASSPORT_SUBDOMAIN='passport-test',
)
class OAuthTestCase(BaseOAuthTestCase):

    def test_invalid_token__error(self):
        """Переданный `token` не прошел проверку в ЧЯ"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_LOGIN,
                status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response__error(rv, ['oauth_token.invalid'])
        self.assert_error_statboxed('oauth_token.invalid')

    def test_empty_token__error(self):
        """Передан пустой `token` - не будем даже ходить в ЧЯ"""
        rv = self.make_request(
            self.query_params(),
            build_headers(
                authorization='',
            ),
        )

        self.assert_response__error(rv, ['oauth_token.empty'])
        eq_(self.env.blackbox._mock.call_count, 0)

    def test_disabled_account__error(self):
        """Аккаунт, для которого был выписан `token` заблокирован - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_LOGIN,
                scope=TEST_OAUTH_SCOPE,
                enabled=False,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response__error(rv, ['account.disabled'])

    def test_wrong_scope__error(self):
        """Недопустимое значение параметра `scope` вызывает ошибку"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_LOGIN,
                scope='test-wrong-scope',
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'])
        self.assert_error_statboxed('oauth_scope.invalid')

    def test_wrong_account_type__error(self):
        """Ручка принимает токены только для ПДД-пользователей"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_uncomplete_pdd_account__redirect(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, является незавершенным ПДД - не заполнена анкета пользователя.

        Поэтому его отправляют на страницу завершения регистрации
        см. auth/password/submit
        """
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                scope=TEST_OAUTH_SCOPE,
                attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
            ),
        )
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        expected = {
            'status': 'ok',
            'state': 'complete_pdd',
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'track_id': self.track_id,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'account': self.get_expected_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                domain=TEST_DOMAIN,
            ),
        }
        self.assert_response__ok(rv, expected)
        self.assert_track__ok(uid=TEST_PDD_UID, cache=expected)

    def test_uncomplete_pdd_account_need_pass__redirect(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, является незавершенным ПДД - не установлен пароль.

        Поэтому его отправляют на страницу установки пароля
        см. auth/password/submit
        """
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                    'userinfo_safe.hintq.uid': TEST_HINT_QUESTION_SERIALIZED,
                    'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                },
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        expected = {
            'status': 'ok',
            'state': 'complete_pdd_with_password',
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'track_id': self.track_id,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'account': self.get_expected_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                domain=TEST_DOMAIN,
                hint=True,
            ),
        }
        self.assert_response__ok(rv, expected)
        self.assert_track__ok(uid=TEST_PDD_UID, cache=expected, have_password=False)

    def test_pdd_account_need_create_password_but_cant__suitable_state(self):
        """
        Вырожденный случай.
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, является завершенным ПДД,
        но на аккаунте требуется создание пароля. Кроме того, администратор
        домена запретил смену пароля пользователями.

        Игнорируем это, потому что данный флаг мог остатся только при баге
        на дорегистрации - не удаляли данный флаг, выписываем куки.
        """
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                domain=TEST_DOMAIN,
                subscribed_to=[102],
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                    'userinfo_safe.hintq.uid': TEST_HINT_QUESTION_SERIALIZED,
                    'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                },
                attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        self.setup_blackbox_sessionid_multi_response(ttl=5)
        self.setup_blackbox_edit_session_response()
        self.setup_blackbox_lrandoms_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_hosted_domains_response(can_users_change_password='0')

        rv = self.make_request(
            self.query_params(),
            build_headers(cookie='%s Session_id=%s' % (TEST_USER_COOKIES, TEST_OLD_SESSION_VALUE)),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_CLEANED_PDD_RETPATH,
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'account': self.get_expected_account(),
                'accounts': [
                    self.get_expected_short_account(login=TEST_ANOTHER_LOGIN, uid=TEST_UID, display_login=TEST_ANOTHER_LOGIN),
                    self.get_expected_short_account(),
                ],
            },
        )

        self.assert_edit_session_called(3, extra_guard_host='mail.yandex.ru')
        self.assert_authlog_records([
            self.build_auth_log_entries(
                status='ses_update',
                type=authtypes.AUTH_TYPE_WEB,
                uid=str(TEST_UID),
                login=TEST_ANOTHER_LOGIN,
                comment='aid=%s;ttl=5' % TEST_AUTH_ID,
            ),
            self.build_auth_log_entries(
                status='ses_create',
                type=authtypes.AUTH_TYPE_OAUTH,
                comment='aid=%s;ttl=5' % TEST_AUTH_ID,
            ),
        ])

    def test_need_pass_change_no_secure_phone__redirect(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, скомпрометирован,
        Причем у пользователя нет привязанного защищенного телефона.

        Поэтому его отправляют на страницу принудительной смены пароля
        см. auth/password/submit
        """
        phone_bound = build_phone_bound(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            subscribed_to=[102],
            dbfields={
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION_SERIALIZED,
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
            },
            attributes={
                'password.forced_changing_reason': '1',
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            scope=TEST_OAUTH_SCOPE,
        )
        account_kwargs = deep_merge(account_kwargs, phone_bound)

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(**account_kwargs),
        )
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        expected = {
            'status': 'ok',
            'state': 'change_password',
            'change_password_reason': 'account_hacked',
            'validation_method': None,
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'track_id': self.track_id,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'account': self.get_expected_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                domain=TEST_DOMAIN,
            ),
        }
        self.assert_response__ok(rv, expected)
        self.assert_track__ok(uid=TEST_PDD_UID, cache=expected)
        expected_statbox_lines = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('defined_validation_method'),
        ]
        self.check_statbox_log_entries(self.env.statbox_handle_mock, expected_statbox_lines)

    def test_need_pass_change_with_secure_phone__redirect(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, скомпрометирован,
        Причем у пользователя есть привязанный защищенный телефон.

        Поэтому его отправляют на страницу принудительной смены пароля,
        Защищенный телефон записывается в трек
        см. auth/password/submit
        """
        account_kwargs = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            subscribed_to=[102],
            dbfields={
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION_SERIALIZED,
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
            },
            attributes={
                'password.forced_changing_reason': '1',
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
            scope=TEST_OAUTH_SCOPE,
        )

        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(**account_kwargs),
        )
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        expected = {
            'status': 'ok',
            'state': 'change_password',
            'change_password_reason': 'account_hacked',
            'validation_method': None,
            'uid': TEST_PDD_UID,
            'login': TEST_PDD_LOGIN,
            'track_id': self.track_id,
            'retpath': TEST_CLEANED_PDD_RETPATH,
            'account': self.get_expected_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                domain=TEST_DOMAIN,
            ),
        }
        self.assert_response__ok(rv, expected)
        self.assert_track__ok(
            uid=TEST_PDD_UID,
            cache=expected,
            secure_phone=TEST_PHONE_NUMBER.e164,
        )

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

        expected_statbox_lines = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('defined_validation_method'),
        ]
        self.check_statbox_log_entries(self.env.statbox_handle_mock, expected_statbox_lines)

    def test_valid_token__ok(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке.

        Авторизация проходит с выписыванием новой сессионной куки
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_sessionid_multi_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_lrandoms_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response__ok(rv)
        self.assert_track__ok()
        self.assert_historydb_logged__ok()
        self.assert_statbox_logged__ok(
            retpath=TEST_CLEANED_PDD_RETPATH,
        )
        self.assert_blackbox_called()
        self.assert_phone_logged()

    def test_no_retpath__default_retpath_value(self):
        """
        Передан пустой параметр `retpath`
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке.

        Авторизация проходит с выписыванием новой сессионной куки,
        в ответе указан retpath по умолчанию.
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_sessionid_multi_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_lrandoms_response()

        rv = self.make_request(
            self.query_params(retpath=''),
            build_headers(),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_DEFAULT_PDD_RETPATH,
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'account': self.get_expected_account(),
                'accounts': [self.get_expected_short_account()],
            },
        )
        self.assert_track__ok(retpath=TEST_DEFAULT_PDD_RETPATH)
        self.assert_historydb_logged__ok()
        self.assert_statbox_logged__ok(
            retpath=TEST_DEFAULT_PDD_RETPATH,
        )
        self.assert_blackbox_called()
        self.assert_phone_logged()

    def test_invalid_retpath__fix_to_default_retpath(self):
        """
        Параметр `retpath` недопустим;
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке.

        Авторизация проходит с выписыванием новой сессионной куки,
        Неправильное значение `retpath` заменено на значение по умолчанию
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_sessionid_multi_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_lrandoms_response()

        rv = self.make_request(
            self.query_params(retpath='http://fishing.com/index.php?uid=123'),
            build_headers(),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_DEFAULT_PDD_RETPATH,
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'account': self.get_expected_account(),
                'accounts': [self.get_expected_short_account()],
            },
        )
        self.assert_track__ok(retpath=TEST_DEFAULT_PDD_RETPATH)
        self.assert_historydb_logged__ok()
        self.assert_statbox_logged__ok(
            retpath=TEST_DEFAULT_PDD_RETPATH,
        )
        self.assert_blackbox_called()

    def test_track_has_cached_response_and_redirect_state__reuse_response(self):
        """
        Поступил повторный запрос для этого трека

        Сообщаем об ошибке и повторяем ответ из кэша в треке
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_pdd = True
            track.submit_response_cache = {'cached': True}

        rv = self.make_request(
            self.query_params(track_id=self.track_id),
            build_headers(),
        )

        expected = {
            'status': 'error',
            'errors': ['track.invalid_state'],
            'cached': True,
        }
        self.assert_response__ok(rv, expected=expected)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    DEFAULT_PDD_RETPATH_WITHOUT_TLD='https://mail.yandex.%s/',
    PASSPORT_SUBDOMAIN='passport-test',
)
class MultiAccountOAuthTestCase(BaseOAuthTestCase):

    def test_multisession_full_house__overflow_error(self):
        """
        Приходим с мультикукой в которой уже полно народу --
        ЧЯ говорит, что в куку больше нельзя дописать пользователей.

        Падаем с ошибкой
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_edit_session_response()
        self.setup_blackbox_lrandoms_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_hosted_domains_response()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                time=TEST_COOKIE_TIMESTAMP,
                ip=TEST_IP,
                age='123',
                allow_more_users=False,
            ),
        )
        resp = self.make_request(
            self.query_params(),
            build_headers(cookie='%s Session_id=%s' % (TEST_USER_COOKIES, TEST_OLD_SESSION_VALUE)),
        )

        self.assert_error_response(resp, ['sessionid.overflow'])

    def test_no_multisession_cookie__create_session_for_one_account(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке;
        В браузере не установлены сессионные куки.

        Авторизация проходит с выписыванием новой мульти-сессионной куки
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_sessionid_multi_response()
        self.setup_blackbox_lrandoms_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_CLEANED_PDD_RETPATH,
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'account': self.get_expected_account(),
                'accounts': [
                    self.get_expected_short_account(),
                ],
            },
        )

        self.assert_create_session_called(2, extra_guard_host='mail.yandex.ru')
        self.assert_authlog_records([
            self.build_auth_log_entries(
                status='ses_create',
                type=authtypes.AUTH_TYPE_OAUTH,
                comment='aid=%s;ttl=5' % TEST_AUTH_ID,
            ),
        ])

    def test__multisession_cookie_exists__account_added_to_multisession(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке;
        В браузере установлена мульти-сессионная кука без этого пользователя.

        Авторизация проходит с добавлением аккаунта в мульти-сессионную куку
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_sessionid_multi_response(ttl=5)
        self.setup_blackbox_edit_session_response()
        self.setup_blackbox_lrandoms_response()
        self.setup_blackbox_createsession_response()
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(cookie='%s Session_id=%s' % (TEST_USER_COOKIES, TEST_OLD_SESSION_VALUE)),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_CLEANED_PDD_RETPATH,
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'account': self.get_expected_account(),
                'accounts': [
                    self.get_expected_short_account(login=TEST_ANOTHER_LOGIN, uid=TEST_UID, display_login=TEST_ANOTHER_LOGIN),
                    self.get_expected_short_account(),
                ],
            },
        )

        self.assert_edit_session_called(3, extra_guard_host='mail.yandex.ru')
        self.assert_authlog_records([
            self.build_auth_log_entries(
                status='ses_update',
                type=authtypes.AUTH_TYPE_WEB,
                uid=str(TEST_UID),
                login=TEST_ANOTHER_LOGIN,
                comment='aid=%s;ttl=5' % TEST_AUTH_ID,
            ),
            self.build_auth_log_entries(
                status='ses_create',
                type=authtypes.AUTH_TYPE_OAUTH,
                comment='aid=%s;ttl=5' % TEST_AUTH_ID,
            ),
        ])

    def test__only_this_account_in_multisession__no_action(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке;
        В браузере уже установлена мульти-сессионная кука с этим пользователем в качестве пользователя по умолчанию.

        Авторизация проходит без изменения кук
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_blackbox_sessionid_multi_response(login=TEST_LOGIN, uid=TEST_PDD_UID)
        self.setup_blackbox_edit_session_response()
        self.setup_blackbox_lrandoms_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(cookie='%s Session_id=%s' % (TEST_USER_COOKIES, TEST_OLD_SESSION_VALUE)),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_CLEANED_PDD_RETPATH,
            },
        )
        # oauth, hosted_domains, sessionid
        eq_(self.env.blackbox._mock.request.call_count, 3)

    def test__not_default_account_in_multisession__change_default(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, в порядке;
        В браузере установлена мульти-сессионная кука с этим пользователем.

        Авторизация проходит через изменения аккаунта по умолчанию в мульти-сессионной куке
        """
        self.setup_blackbox_good_oauth_response()
        self.setup_blackbox_hosted_domains_response()
        self.setup_blackbox_edit_session_response()
        self.setup_blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_ANOTHER_LOGIN,
                    authid=TEST_OLD_AUTH_ID,
                    ttl=5,
                ),
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(cookie='%s Session_id=%s' % (TEST_USER_COOKIES, TEST_OLD_SESSION_VALUE)),
        )

        self.assert_response__ok(
            rv,
            {
                'status': 'ok',
                'uid': TEST_PDD_UID,
                'login': TEST_PDD_LOGIN,
                'track_id': self.track_id,
                'retpath': TEST_CLEANED_PDD_RETPATH,
                'account': self.get_expected_account(),
                'cookies': self.get_expected_cookies(),
                'default_uid': TEST_PDD_UID,
                'accounts': [
                    self.get_expected_short_account(
                        uid=TEST_UID,
                        login=TEST_ANOTHER_LOGIN,
                        display_login=TEST_ANOTHER_LOGIN,
                    ),
                    self.get_expected_short_account(
                        uid=TEST_PDD_UID,
                        login=TEST_PDD_LOGIN,
                    ),
                ],
            },
        )

        self.assert_edit_session_called(3, operation='select')
        self.assert_authlog_records([
            {
                'login': TEST_ANOTHER_LOGIN,
                'type': authtypes.AUTH_TYPE_WEB,
                'status': 'ses_update',
                'uid': str(TEST_UID),
                'useragent': TEST_USER_AGENT,
                'yandexuid': TEST_YANDEXUID_COOKIE,
                'comment': 'aid=%s;ttl=5' % TEST_AUTH_ID,
                'ip_from': TEST_IP,
                'client_name': 'passport',
            }.items(),
            {
                'login': TEST_PDD_LOGIN,
                'type': authtypes.AUTH_TYPE_WEB,
                'status': 'ses_update',
                'uid': str(TEST_PDD_UID),
                'useragent': TEST_USER_AGENT,
                'yandexuid': TEST_YANDEXUID_COOKIE,
                'comment': 'aid=%s;ttl=5' % TEST_AUTH_ID,
                'ip_from': TEST_IP,
                'client_name': 'passport',
            }.items(),
        ])

    def test_valid_token_with_2fa__error(self):
        """
        Пришел валидный `token`;
        Аккаунт, для которого был выписан `token`, использует 2FA;

        Отдаем ошибку требования otp и инфо о пользователе
        """
        self.setup_blackbox_good_oauth_response(
            attributes={
                'account.2fa_on': '1',
            },
        )
        self.setup_blackbox_hosted_domains_response()

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['account.2fa_enabled'])
        eq_(
            rv['account'],
            self.get_expected_account(
                is_yandexoid=False,
                is_2fa_enabled=True,
                is_rfc_2fa_enabled=False,
                is_workspace_user=False,
            ),
        )
