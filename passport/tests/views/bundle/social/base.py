# -*- coding: utf-8 -*-

import time
import urllib

from nose.tools import eq_
from passport.backend.api.common.authorization import encode_udn
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.conf import settings
from passport.backend.core.test.cookies import (
    assert_cookie_equals,
    assert_l_cookie_equals,
    assert_yp_cookie_contain,
    assert_ys_cookie_contain,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.core.types.display_name import DisplayName


TEST_LOGIN = 'test-login'
TEST_DISPLAY_NAME = DisplayName('test-display-name')
TEST_USER_IP = '1.2.3.4'
TEST_UID = 123
TEST_OTHER_UID = 321
TEST_SESSIONID = 'test_sessionid'
TEST_NEW_SESSIONID = 'test_new_sessionid'
TEST_SSL_SESSIONID = '2:sslsession'
TEST_HOST = 'yandex.ru'
TEST_SID = 2
TEST_PROFILE_ID = 100
TEST_PASSWORD = 'password'
TEST_PASSWORD_HASH = '1:1$123123'
TEST_NOT_USERS_PROFILE_ID = 1
TEST_AUTH_ON = 1
TEST_AUTH_OFF = 0
TEST_ACCOUNT_DATA = {
    u'account': {
        u'display_login': u'test',
        u'display_name': {
            u'default_avatar': u'',
            u'name': u''
        },
        u'login': u'test',
        u'person': {
            u'birthday': u'1963-05-15',
            u'country': u'ru',
            u'firstname': u'\\u0414',
            u'gender': 1,
            u'language': u'ru',
            u'lastname': u'\\u0424'
        },
        u'uid': 123,
    },
}
TEST_USER_COOKIE = 'Session_id=%s;sessionid2=%s' % (TEST_SESSIONID, TEST_SSL_SESSIONID)
TEST_INVALID_SESSIONID_COOKIE = 'Session_id=;sessionid2=%s' % TEST_SSL_SESSIONID
TEST_MISSING_SESSIONID_COOKIE = 'yandexuid=123'

TRACK_TYPE = 'authorize'

SOCIAL_DEFAULT_SUBSCRIPTION = [
    {
        'name': 'mail',
        'sid': 2,
        'providers': [
            'facebook',
            'odnoklassniki',
        ],
    },
    {
        'name': 'market',
        'sid': 25,
        'providers': [
            'vkontakte',
            'facebook',
            'twitter',
            'mailru',
            'google',
            'odnoklassniki',
        ],
    },
    {
        'name': 'social',
        'sid': 58,
        'providers': [],
    },
    {
        'name': 'text',
        'sid': 74,
        'providers': [
            'vkontakte',
            'facebook',
            'twitter',
            'mailru',
            'google',
            'odnoklassniki',
        ],
    },
    {
        'name': 'news',
        'sid': 83,
        'providers': [
            'vkontakte',
            'facebook',
            'twitter',
        ],
    },
]

SOCIAL_AUTH_PROVIDERS = [
    'vkontakte',
    'facebook',
    'twitter',
    'mailru',
    'google',
    'odnoklassniki',
]


ALLOWED_SIDS = [str(social_subscription['sid']) for social_subscription in SOCIAL_DEFAULT_SUBSCRIPTION]


class BaseSocialTestCase(BaseBundleTestViews):
    ok_params = {}  # правильные параметры для тестирования ручки

    def setUp(self):
        self.track_id = None
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={
            'social_profiles': ['base']
        }))
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='social_profiles',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
        )
        for action in (
            'initialized',
            'cookie_edit',
            'listed',
            'set_subscription',
            'deleted_subscription',
            'deleted',
            'unset_auth',
            'set_auth',
        ):
            self.env.statbox.bind_entry(
                action,
                action=action,
                track_id=self.track_id,
            )

    def build_headers(self, cookie=None, host=TEST_HOST):
        return mock_headers(
            user_ip=TEST_USER_IP,
            cookie=cookie,
            host=host,
        )

    def make_request(self, headers, params=None):
        raise NotImplementedError()  # pragma: no cover

    def set_blackbox_response(self, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**kwargs),
        )

    def check_blackbox_params(self, **kwargs):
        self.env.blackbox.requests[0].assert_query_contains(kwargs)

    def check_social_put_params(self, profile_id, index=0, **kwargs):
        self.env.social_api.requests[index].assert_properties_equal(
            method='POST',
            url='http://socialdev-2.yandex.ru/api/profile/%s?consumer=passport' % profile_id,
            post_args=kwargs
        )

    def check_social_get_list_params(self, uid, index=0, with_include=True):
        url = 'http://socialdev-2.yandex.ru/api/user/{a}/profile'.format(a=uid)
        query = [('consumer', 'passport')]
        if with_include:
            query.insert(0, ('include', 'subscriptions,tokens,person'))
        url = url + '?' + urllib.urlencode(query)

        self.env.social_api.requests[index].assert_properties_equal(method='GET', url=url)

    def check_social_delete_params(self, profile_id, index=0):
        self.env.social_api.requests[index].assert_properties_equal(
            method='DELETE',
            url='http://socialdev-2.yandex.ru/api/profile/%s?consumer=passport' % profile_id,
        )

    def check_social_subscr_delete_params(self, profile_id, sid, index=0):
        self.env.social_api.requests[index].assert_properties_equal(
            method='DELETE',
            url='http://socialdev-2.yandex.ru/api/profile/{a}/subscription/{b}?consumer=passport'.format(a=profile_id, b=sid),
        )

    def check_social_subscr_set_params(self, profile_id, sid, index=0):
        self.env.social_api.requests[index].assert_properties_equal(
            method='PUT',
            url='http://socialdev-2.yandex.ru/api/profile/{a}/subscription/{b}?consumer=passport'.format(a=profile_id, b=sid),
        )

    def assert_cookies_ok(self, cookies):
        assert_l_cookie_equals(cookies, TEST_UID, TEST_LOGIN)
        assert_yp_cookie_contain(
            cookies,
            [{
                'name': 'udn',
                'value': encode_udn(TEST_DISPLAY_NAME),
                'expire': TimeSpan(
                    time.time() + settings.COOKIE_YP_DISPLAY_NAME_AGE,
                ),
            }],
        )
        assert_ys_cookie_contain(
            cookies,
            [{
                'name': 'udn',
                'value': encode_udn(TEST_DISPLAY_NAME),
            }],
        )
        assert_cookie_equals(cookies, 'yandex_login', TEST_LOGIN)
        assert_cookie_equals(cookies, 'Session_id', TEST_NEW_SESSIONID)
        assert_cookie_equals(cookies, 'sessionid2', TEST_SSL_SESSIONID)

    def build_auth_log_entries(self, status, uid, **kwargs):
        entries = {
            'type': authtypes.AUTH_TYPE_WEB,
            'status': status,
            'uid': str(uid),
            'ip_from': TEST_USER_IP,
            'client_name': 'passport',
        }
        entries.update(kwargs)
        return entries.items()

    def assert_auth_log(self, expected_records):
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )


class BaseSocialTrackRequiredTestCase(BaseSocialTestCase):
    def setUp(self):
        super(BaseSocialTrackRequiredTestCase, self).setUp()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(TRACK_TYPE)
        self.setup_track()
        self.setup_statbox_templates()

    def tearDown(self):
        del self.track_manager
        super(BaseSocialTrackRequiredTestCase, self).tearDown()

    def setup_track(self, uid=TEST_UID):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid

    def check_track(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        eq_(track.track_type, TRACK_TYPE)
        eq_(track.uid, str(uid))

    def get_expected_ok_response(self, **kwargs):
        return dict(
            status='ok',
            track_id=self.track_id,
            **kwargs
        )


class BaseSocialTrackRequiredMixin(object):
    """
    Этот класс является вспомогательным для базовых тестовых проверок.
    Необходимо наследоваться от него после наследования от BaseSocialTrackRequiredMixin
    """

    def test_missing_headers(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        response = self.make_request(
            headers={},
            params=params,
        )
        self.assert_error_response(response, ['host.empty', 'ip.empty'])

    def test_missing_host(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        response = self.make_request(
            headers=self.build_headers(
                cookie=TEST_USER_COOKIE,
                host=None,
            ),
            params=params,
        )
        self.assert_error_response(response, ['host.empty'])

    def test_missing_sessionid(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_MISSING_SESSIONID_COOKIE),
            params=params,
        )
        self.assert_error_response_with_track_id(response, ['sessionid.invalid'])

    def test_invalid_sessionid(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        self.set_blackbox_response(
            uid=TEST_UID,
            status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_INVALID_SESSIONID_COOKIE),
            params=params,
        )

        self.assert_error_response_with_track_id(response, ['sessionid.invalid'])

    def test_disabled_account(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        self.set_blackbox_response(
            uid=TEST_UID,
            enabled=False,
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )

        self.assert_error_response_with_track_id(response, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        self.set_blackbox_response(
            uid=TEST_UID,
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            }
        )

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )

        self.assert_error_response_with_track_id(response, ['account.disabled_on_deletion'])

    def test_missing_track(self):
        params = self.ok_params.copy()

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )
        self.assert_error_response(response, ['track_id.empty'])

    def test_different_uid_in_track_and_in_session(self):
        params = self.ok_params.copy()
        params['track_id'] = self.track_id

        self.set_blackbox_response(
            uid=TEST_UID,
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 321  # uid не как в сессии

        response = self.make_request(
            headers=self.build_headers(cookie=TEST_USER_COOKIE),
            params=params,
        )

        self.assert_error_response_with_track_id(response, ['track.invalid_state'])
