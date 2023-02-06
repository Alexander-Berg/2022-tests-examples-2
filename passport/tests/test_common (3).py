# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.exception import (
    InternalProxylibError,
    InvalidTokenProxylibError,
    ProviderUnknownProxylibError,
    TooLongUnexpectedResponseProxylibError,
)
from passport.backend.social.common.misc import trim_message
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
)
from passport.backend.social.common.test.fake_useragent import (
    FakeRequest,
    FakeUseragent,
)
from passport.backend.social.common.test.parameterized import parameterized_expand
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import build_http_pool_manager
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.proxy import RefreshTokenGetter
from passport.backend.social.proxylib.repo import get_repo
from passport.backend.social.proxylib.repo.common import Repo


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        passport.backend.social.proxylib.init()

        LazyLoader.register('http_pool_manager', build_http_pool_manager)

        self.fake_useragent = FakeUseragent()
        self.fake_useragent.start()

    def tearDown(self):
        self.fake_useragent.stop()
        super(BaseTestCase, self).tearDown()


class TestProxyCommon(BaseTestCase):
    r = Repo('fb')

    def setUp(self):
        super(TestProxyCommon, self).setUp()

        self.r.settings = dict(
            birthday_regexp=r'^(?P<month>\d{2})/(?P<day>\d{2})/?(?P<year>\d{4})?$',
            gender_map={'male': 'm', 'female': 'f'},
        )
        self.r.app = mock.Mock(secret='abc')
        self.r.access_token = {'value': 'val'}

    def test_get_proxy(self):
        eq_(get_proxy('fb', {}, mock.Mock()).code, 'fb')

    def test_get_proxy_error(self):
        with self.assertRaises(ProviderUnknownProxylibError):
            get_proxy('xx', {}, mock.Mock())

    def test_get_repo_error(self):
        with self.assertRaises(InternalProxylibError):
            get_repo('xx')

    def test_convert_birthday_ok(self):
        self.r.context = {'processed_data': {'birthday': '12/28/1989'}}
        self.r.convert_birthday()
        eq_(self.r.context['processed_data']['birthday'], '1989-12-28')

    def test_convert_birthday_without_year(self):
        self.r.context = {'processed_data': {'birthday': '12/28'}}
        self.r.convert_birthday()
        eq_(self.r.context['processed_data']['birthday'], '0000-12-28')

    def test_no_birthday(self):
        self.r.context = {'processed_data': {'birthday': ''}}
        self.r.convert_birthday()
        ok_('birthday' not in self.r.context['processed_data'])

    def test_corrupted_birthday(self):
        self.r.context = {'processed_data': {'birthday': 'abrakadabra'}}
        self.r.convert_birthday()
        ok_('birthday' not in self.r.context['processed_data'])

    def test_convert_gender_ok(self):
        self.r.context = {'processed_data': {'gender': 'male'}}
        self.r.convert_gender()
        eq_(self.r.context['processed_data']['gender'], 'm')

    def test_convert_gender_no_gender(self):
        self.r.context = {'processed_data': {}}
        self.r.convert_gender()
        ok_('gender' not in self.r.context['processed_data'])

    def test_convert_gender_invalid_gender(self):
        self.r.context = {'processed_data': {'gender': 'middle'}}
        self.r.convert_gender()
        ok_('gender' not in self.r.context['processed_data'])

    def test_signature_md5(self):
        sig = self.r.generate_md5_signature({'a': 'b', u'c': u'фыва'})
        eq_(sig, 'a52ec41dbf03fe344f74c989648dd74d')

    def test_signature(self):
        sig = self.r.generate_signature({'a': 'b', u'c': u'фыва'})
        eq_(sig, 'b6bbf9249ecc3b9a31f24f8b067eae3e')

    may_be_invalid_token_errors = [
        ('invalid_client', oauth2.refresh_token.InvalidClient),
        ('invalid_scope', oauth2.refresh_token.InvalidScope),
        ('unauthorized_client', oauth2.refresh_token.UnauthorizedClient),
        ('unsupported_grant_type', oauth2.refresh_token.UnsupportedGrantType),
    ]

    @parameterized_expand(may_be_invalid_token_errors)
    def test_not_treat_error_as_invalid_token(self, error, oauth_exception):
        self.fake_useragent.set_response_values(
            [
                oauth2.test.build_error(oauth_exception.error),
            ],
        )
        proxy = get_proxy(
            app=Application(
                identifier=APPLICATION_ID1,
                refresh_token_url='https://refresh.token/url',
                request_from_intranet_allowed=True,
            ),
        )

        self.assertFalse(proxy.SETTINGS.get('treat_%s_as_invalid_token' % error))

        with self.assertRaises(oauth_exception):
            proxy.refresh_token(APPLICATION_TOKEN1)

    @parameterized_expand(may_be_invalid_token_errors)
    def test_treat_error_as_invalid_token(self, error, oauth_exception):
        self.fake_useragent.set_response_values(
            [
                oauth2.test.build_error(oauth_exception.error),
            ],
        )
        proxy = get_proxy(
            app=Application(
                identifier=APPLICATION_ID1,
                refresh_token_url='https://refresh.token/url',
                request_from_intranet_allowed=True,
            ),
        )
        proxy.SETTINGS.update({'treat_%s_as_invalid_token' % error: True})

        with self.assertRaises(InvalidTokenProxylibError):
            proxy.refresh_token(APPLICATION_TOKEN1)

    def test_too_long_non_ascii_response(self):
        response = 'Ё' * 64001
        self.fake_useragent.set_response_values([FakeResponse(response.encode('utf-8'), status_code=200)])
        proxy = get_proxy(
            app=Application(
                identifier=APPLICATION_ID1,
                refresh_token_url='https://refresh.token/url',
                request_from_intranet_allowed=True,
            ),
        )

        with self.assertRaises(TooLongUnexpectedResponseProxylibError) as assertion:
            proxy.refresh_token(APPLICATION_TOKEN1)

        self.assertEqual(assertion.exception.description, 'Response is too long: ' + trim_message(response))


class TestRefreshToken(BaseTestCase):
    def setUp(self):
        super(TestRefreshToken, self).setUp()
        self.fake_useragent.set_response_values([oauth2.test.oauth2_access_token_response()])

    def build_repo(self, app=None):
        if app is None:
            app = self.build_application()
        rep = Repo('xx')
        rep.app = app
        rep.settings = dict(
            oauth_refresh_token_url='https://refresh.token/url',
        )
        return rep

    def build_application(self):
        return Application(
            id=EXTERNAL_APPLICATION_ID1,
            request_from_intranet_allowed=True,
            secret=APPLICATION_SECRET1,
        )

    def get_refresh_token_simple(self, repo=None):
        if repo is None:
            repo = self.build_repo()
        return RefreshTokenGetter(
            repo=repo,
            refresh_token=APPLICATION_TOKEN1,
        ).get_refresh_token()

    def test_ok(self):
        token = self.get_refresh_token_simple()

        assert token == dict(access_token=APPLICATION_TOKEN1)

        assert len(self.fake_useragent.requests) == 1
        self.assertEqual(
            self.fake_useragent.requests[0],
            FakeRequest(
                data=dict(
                    client_id=EXTERNAL_APPLICATION_ID1,
                    client_secret=APPLICATION_SECRET1,
                    grant_type='refresh_token',
                    refresh_token=APPLICATION_TOKEN1,
                ),
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': mock.ANY,
                },
                method='POST',
                url='https://refresh.token/url',
            ),
        )

    def test_custom_provider_client_id(self):
        app = self.build_application()
        app.custom_provider_client_id = EXTERNAL_APPLICATION_ID2
        self.get_refresh_token_simple(repo=self.build_repo(app))

        assert len(self.fake_useragent.requests) == 1
        assert self.fake_useragent.requests[0].data.get('client_id') == EXTERNAL_APPLICATION_ID2
