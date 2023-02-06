# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from urlparse import urlparse

from mock import Mock
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.broker.communicators.communicator import (
    AuthorizeOptions,
    OAuthCommunicator,
)
from passport.backend.social.broker.exceptions import (
    CommunicationFailedError,
    UserDeniedError,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.misc import urlencode
from passport.backend.social.common.oauth1.test import oauth1_temporary_credentials_response
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.fake_useragent import FakeZoraUseragent
from passport.backend.social.common.useragent import ZoraUseragent
from passport.backend.utils.common import remove_none_values


CALLBACK_URL1 = 'https://social.yandex.net/broker/redirect'
REQUEST_TOKEN_URL1 = 'https://request_token/'
ACCESS_TOKEN_URL1 = 'https://access_token/'


class TestOauthCommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestOauthCommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = OAuthCommunicator(app)

    def _build_response(self, **values):
        defaults = {
            'oauth_token': APPLICATION_TOKEN1,
            'oauth_token_secret': APPLICATION_SECRET1,
        }
        for key in defaults:
            values.setdefault(key, defaults[key])
        values = remove_none_values(values)
        return urlencode(values)

    def test_not_urlencoded(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token('fail')

    def test_no_oauth_token(self):
        response = self._build_response(oauth_token=None)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_no_oauth_token_secret(self):
        response = self._build_response(oauth_token_secret=None)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_error_in_response(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(urlencode({'error': '1'}))

    def test_oauth_problem_permission_denied(self):
        response = self._build_response(oauth_problem='permission_denied')
        with self.assertRaises(UserDeniedError):
            self._communicator.parse_access_token(response)

    def test_oauth_problem_unknown(self):
        response = self._build_response(oauth_problem='unknown')
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)


class TestOauthCommunicatorUsesZora(TestCase):
    def setUp(self):
        super(TestOauthCommunicatorUsesZora, self).setUp()
        self._communicator = self._build_communicator()
        self._fake_zora_useragent = FakeZoraUseragent().start()

        zora_useragent = ZoraUseragent(Mock(name='tvm_credentials_manager'))
        LazyLoader.register('zora_useragent', lambda: zora_useragent)

    def tearDown(self):
        self._fake_zora_useragent.stop()
        super(TestOauthCommunicatorUsesZora, self).tearDown()

    def _build_communicator(self, request_from_intranet_allowed=False):
        app = Application(
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            request_from_intranet_allowed=request_from_intranet_allowed,
            domain=urlparse(CALLBACK_URL1).hostname,
        )
        communicator = OAuthCommunicator(app)
        communicator.OAUTH_ACCESS_TOKEN_URL = ACCESS_TOKEN_URL1
        communicator.OAUTH_REQUEST_TOKEN_URL = 'https://request_token/'
        communicator.REQUEST_METHOD = 'POST'
        return communicator

    def test_get_authorize_url(self):
        def _get_authorize_url(communicator):
            communicator.get_authorize_url(AuthorizeOptions(CALLBACK_URL1))

        self._fake_zora_useragent.set_response_value(oauth1_temporary_credentials_response())

        _get_authorize_url(self._communicator)

        self.assertEqual(len(self._fake_zora_useragent.requests), 1)
        self.assertEqual(self._fake_zora_useragent.requests[0].url, 'https://request_token/')
        self.assertEqual(len(self._fake_useragent.requests), 0)

        self._fake_useragent.set_response_value(oauth1_temporary_credentials_response())
        communicator = self._build_communicator(request_from_intranet_allowed=True)

        _get_authorize_url(communicator)

        self.assertEqual(len(self._fake_useragent.requests), 1)
        self.assertEqual(self._fake_useragent.requests[0].url, 'https://request_token/')
        self.assertEqual(len(self._fake_zora_useragent.requests), 1)
