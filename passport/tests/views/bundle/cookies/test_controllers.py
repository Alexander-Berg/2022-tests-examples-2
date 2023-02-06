# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.cookies.cookie_l import CookieLUnpackError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.utils.common import merge_dicts


eq_ = iterdiff(eq_)


TEST_UID = 1
TEST_LOGIN = 'test_user'
TEST_HOST = '.yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIES = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'

COOKIE_L_VALUE = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                  '.1383144488.1002323.298169.6af3100a8920a270bd9a933bbcd48181')

TEST_COOKIE_INFO = {
    'uid': TEST_UID,
    'login': TEST_LOGIN,
}

TEST_L_RANDOM = {
    'body': '2dL9OKKqcKHbljKQI70PMaaB7R08VnEn3jo5iAI62gPeCQ5zgI5fjjczFOMRvvaQ',
    'created_timestamp': 1376769602,
    'id': '1002323',
}


@with_settings_hosts()
class TestParseCookieLView(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'cookies': ['parse_l']}))

        self._cookie_l = mock.Mock()
        self._cookie_l.unpack = mock.Mock(return_value=TEST_COOKIE_INFO)

        self.patches = [
            mock.patch('passport.backend.core.cookies.cookie_l.CookieL', mock.Mock(side_effect=[self._cookie_l])),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self._cookie_l

    def cookie_parse_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/cookies/l/parse/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'cookie': COOKIE_L_VALUE,
        }
        return merge_dicts(base_params, kwargs)

    def build_headers(self):
        return mock_headers(
            host=TEST_HOST,
            user_ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            cookie=TEST_USER_COOKIES,
            referer=TEST_REFERER,
        )

    def test_ok(self):
        rv = self.cookie_parse_request(
            self.query_params(),
            self.build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID,
                'login': TEST_LOGIN,
            },
        )

    def test_bad_cookie(self):
        self._cookie_l.unpack.side_effect = CookieLUnpackError('Signature mismatch')
        rv = self.cookie_parse_request(
            self.query_params(),
            self.build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': ['cookie.invalid'],
            },
        )
