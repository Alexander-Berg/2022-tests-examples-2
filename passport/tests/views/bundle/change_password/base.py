# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    nottest,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_hosted_domains_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import check_all_url_params_match
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import (
    deep_merge,
    remove_none_values,
)

from .base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_COOKIE,
    TEST_COOKIE_AGE,
    TEST_COOKIE_TIMESTAMP,
    TEST_DOMAIN,
    TEST_HOST,
    TEST_LOGIN,
    TEST_OLD_SERIALIZED_PASSWORD,
    TEST_PASSWORD_QUALITY,
    TEST_PASSWORD_QUALITY_VERSION,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_SESSIONID,
    TEST_SOCIAL_LOGIN,
    TEST_SSL_SESSIONID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COUNTRY,
    TEST_USER_IP,
    TEST_USER_LANGUAGE,
    TEST_USER_TIMEZONE,
)


@nottest
class BaseChangePasswordTestCase(BaseBundleTestViews, EmailTestMixin):

    http_method = 'POST'

    def setup_track(self, uid=TEST_UID, login=TEST_LOGIN, origin=None, retpath=None):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.login = login
            track.is_password_change = True
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True
            track.is_fuzzy_hint_answer_checked = True
            track.origin = origin
            track.retpath = retpath

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['change_password'],
        }))

        self.setup_blackbox_responses()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.setup_track()
        self.setup_statbox_templates()

        self.http_headers = dict(
            host=TEST_HOST,
            user_ip=TEST_USER_IP,
            cookie=TEST_COOKIE,
            user_agent=TEST_USER_AGENT,
            accept_language=TEST_ACCEPT_LANGUAGE,
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_blackbox_responses(self, uid=TEST_UID, login=TEST_LOGIN, **kwargs):
        account_kwargs = self.account_kwargs(uid=uid, login=login, **kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_USER_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        blackbox_response = blackbox_userinfo_response(**account_kwargs)
        self.env.db.serialize(blackbox_response)

    def account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN, phone=TEST_PHONE_NUMBER, emails=None, **kwargs):
        params = dict(
            uid=uid,
            login=login,
            dbfields={
                'password_quality.quality.uid': TEST_PASSWORD_QUALITY,
                'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
            },
            attributes={
                'person.country': TEST_USER_COUNTRY,
                'person.timezone': TEST_USER_TIMEZONE,
                'person.language': TEST_USER_LANGUAGE,
                'password.encrypted': TEST_OLD_SERIALIZED_PASSWORD,
            },
            emails=emails or [
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        if phone:
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
                is_default=False,
            )
            params = deep_merge(params, phone_secured)

        return deep_merge(params, kwargs)

    def get_expected_response(self, state=None, uid=TEST_UID, is_pdd=False, retpath=None,
                              punycode_domain=TEST_DOMAIN, unicode_domain=TEST_DOMAIN,
                              login=TEST_LOGIN, display_login=None, **kwargs):
        response = {
            'account': {
                'uid': uid,
                'login': login,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': login if display_login is None else display_login,
            },
        }

        if is_pdd:
            response['account']['domain'] = {
                'unicode': unicode_domain,
                'punycode': punycode_domain,
            }
        if state:
            response['state'] = state
        if retpath:
            response['retpath'] = retpath
        return response

    def assert_ok_response_with_cookies(self, rv, expected_response, default_uid=TEST_UID, with_sessguard=False):
        eq_(rv.status_code, 200)
        rv = json.loads(rv.data)
        cookies = rv.pop('cookies', [])
        eq_(
            rv,
            dict(expected_response, status='ok', default_uid=default_uid),
        )

        self.assert_cookies_ok(cookies, with_sessguard=with_sessguard)

    def assert_cookies_ok(self, cookies, with_sessguard=False):
        eq_(len(cookies), 8 if with_sessguard else 7)
        sorted_cookies = sorted(cookies)
        if with_sessguard:
            sessguard_cookie = sorted_cookies.pop(3)
            self.assert_cookie_ok(
                sessguard_cookie, 'sessguard', value='1.sessguard', domain='.%s' % TEST_HOST,
                path='/', http_only=True, secure=True, expires=None,
            )
        l_cookie, sessionid_cookie, mda2_beacon, sessionid2_cookie, yalogin_cookie, yp_cookie, ys_cookie = sorted_cookies
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None)
        self.assert_cookie_ok(yalogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

    def check_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_password_change, False)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_checked, True)
        eq_(track.is_captcha_recognized, True)
        eq_(track.have_password, True)
        ok_(track.session)
        eq_(track.old_session_ttl, '0')

    def historydb_entry(self, uid=1, name=None, value=None):
        entry = {
            'uid': str(uid),
            'name': name,
            'value': value,
        }
        return remove_none_values(entry)

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_USER_IP),
        ]

    def assert_sessionid_called(self, call_index=0):
        self.env.blackbox.requests[call_index].assert_query_contains({
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
            'sslsessionid': TEST_SSL_SESSIONID,
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[call_index].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def assert_editsession_called(self, uid=TEST_UID, call_index=3):
        check_all_url_params_match(
            self.env.blackbox._mock.request.call_args_list[call_index][0][1],
            {
                'uid': str(uid),
                'format': 'json',
                'sessionid': TEST_SESSIONID,
                'host': 'passport-test.yandex.ru',
                'userip': TEST_USER_IP,
                'method': 'editsession',
                'op': 'add',
                'lang': '1',
                'password_check_time': TimeNow(),
                'have_password': '1',
                'new_default': str(uid),
                'keyspace': u'yandex.ru',
                'sslsessionid': TEST_SSL_SESSIONID,
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def test_missing_header_ip__error(self):
        self.http_headers.pop('user_ip')
        rv = self.make_request()

        self.assert_error_response(rv, ['ip.empty'])

    def test_invalid_process_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'abyrvalg'

        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_captcha_required_and_not_passed__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['captcha.required'],
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_recognized, False)

    def test_2fa_account_invalid_type(self):
        """
        Проверяем, что попытка смены пароля у пользователя со включенным 2FA
        оборвется выдачей ошибки.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    attributes={
                        'account.2fa_on': '1',
                    },
                )
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.2fa_enabled'])

    def test_pdd_account_password_change_forbidden__redirect_state(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.account_kwargs(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            )),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                can_users_change_password='0',
                domain=TEST_DOMAIN,
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID
            track.login = TEST_PDD_LOGIN

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                state='password_change_forbidden',
                is_pdd=True,
                uid=TEST_PDD_UID,
                validation_method=None,
                login=TEST_PDD_LOGIN,
            )
        )

    def test_social_account__redirect_state(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                state='complete_social',
                login=TEST_SOCIAL_LOGIN,
                validation_method=None,
                display_login='',
            )
        )

    def test_portal_account_with_social_alias__redirect_state(self):
        """У пользователя, подписанного на социальный SID, не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                subscribed_to=[58],
                attributes={'password.encrypted': ''},
            ),
        )
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.get_expected_response(
                state='complete_social',
                login=TEST_LOGIN,
                validation_method=None,
            )
        )

    def test_password_not_set__redirect_state(self):
        bb_response = blackbox_sessionid_multi_response(
            **self.account_kwargs(attributes={'password.encrypted': ''})
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.without_password'],
            **self.get_expected_response(validation_method=None)
        )

    def test_invalid_session_cookie__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.account_kwargs(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_disabled_session_cookie__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.account_kwargs(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            )),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])

    def test_disabled_on_deletion_session_cookie__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                    attributes={
                        'account.is_disabled': '2',
                    },
                )
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def test_foreign_session_cookie__error(self):
        """В треке и в куке разные uid'ы - ошибка состояния"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 42

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['sessionid.no_uid'],
        )
