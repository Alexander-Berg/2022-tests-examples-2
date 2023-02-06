# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.social.broker.communicators.TwitterCommunicator import TwitterCommunicator
from passport.backend.social.broker.exceptions import (
    CommunicationFailedError,
    UserDeniedError,
)
from passport.backend.social.broker.handlers.profile.authz_in_web import (
    CallbackHandler,
    ContinueHandler,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.base import get_callback_request_oauth1
from passport.backend.social.broker.tests.base_broker_test_data import TEST_RETPATH
from passport.backend.social.broker.tests.communicators import (
    get_callback_request,
    reset_fake_redis,
    start_tst_ok,
    TestCommunicator,
)
from passport.backend.social.common.application import Application


class TestTwitter(TestCommunicator):
    normal_request_token_response = "oauth_token=ZqrPdjRGGWSAZvmrigRaWuAeJpdbHB05kzCXJVQrQ&oauth_token_secret=JjJNgbIAbJV4Ox4xvCOk9P5Z71Kxbc3xOhsrlkGJrk&oauth_callback_confirmed=true"
    access_token = '1464326220-0svVcN8RuDh0OmOWu91T1UXvKrS0acmgAqS2xI4'
    normal_access_token_response = 'oauth_token={}&oauth_token_secret=0gXqF9BNcjkvxNfW448t1GyQjW9o5nIgVdSe1eY2XQ&user_id=1464326220&screen_name=PetrTestov'.format(access_token)
    error_request_token_response = 'Бугага: failed to validate oauth signature and token'
    error_request_token_response_unconfirmed = "oauth_token=ZqrPdjRGGWSAZvmrigRaWuAeJpdbHB05kzCXJVQrQ&oauth_token_secret=JjJNgbIAbJV4Ox4xvCOk9P5Z71Kxbc3xOhsrlkGJrk&oauth_callback_confirmed=false"
    error_access_token_response = 'привет'
    code = 'FnfDr0BgJuars4OgwGbxSgZpIlBU0pjnvoEwlTLWo'
    oauth_verifier = 'lxUPP0mVi0c7xEK1VslhvsZaN1U0YroKrWuvBc0OH4'
    oauth_token = 'ZqrPdjRGGWSAZvmrigRaWuAeJpdbHB05kzCXJVQrQ'

    request_token_value = 'ZqrPdjRGGWSAZvmrigRaWuAeJpdbHB05kzCXJVQrQ'
    error_callback_denied = {'denied': request_token_value}
    error_callback_no_oauth_token = {}
    error_callback_invalid_oauth_token = {'oauth_token': '123abc'}

    provider_code = 'tw'

    def setUp(self):
        super(TestTwitter, self).setUp()
        self.patcher = patch('passport.backend.social.proxylib.TwitterProxy.TwitterProxy.get_profile',
                             Mock(return_value={'userid': 100, 'firstname': 'Petr', 'lastname': 'Testov'}))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super(TestTwitter, self).tearDown()

    def test_full_tw_ok(self):
        reset_fake_redis()
        response = Mock(decoded_data=self.normal_request_token_response)
        request = Mock(return_value=response)
        with patch('passport.backend.social.proxylib.useragent.execute_request', request):
            data = start_tst_ok('tw', 'https://api.twitter.com/oauth/authenticate?')
        ok_(request.called)

        request = get_callback_request_oauth1(data['task_id'], oauth_verifier=self.oauth_verifier,
                                              oauth_token=self.oauth_token,
                                              track=data['cookies'][0])
        handler = CallbackHandler(request)

        def check_request_url(method, url, *args, **kwargs):
            eq_(method.upper(), 'GET')
            assert url.startswith(handler.communicator.OAUTH_ACCESS_TOKEN_URL)
            return Mock(decoded_data=self.normal_access_token_response)

        with patch('passport.backend.social.proxylib.useragent.execute_request', check_request_url):
            result = handler.get(data['task_id'])
            request_continue = get_callback_request(data['task_id'], track=json.loads(result.data)['cookies'][0])
            handler_continue = ContinueHandler(request_continue)
            result = handler_continue.get(data['task_id'])

        data = json.loads(result.data)
        eq_(len(data['cookies']), 1)
        location = data['location']
        ok_('status=ok' in location, location)
        ok_('task_id=' in location, location)
        ok_(location.startswith(TEST_RETPATH), [location, TEST_RETPATH])

    @raises(CommunicationFailedError)
    def test_parse_request_token_error(self):
        self.communicator.parse_request_token(self.error_request_token_response)

    @raises(CommunicationFailedError)
    def test_parse_request_token_error_unconfirmed(self):
        self.communicator.parse_request_token(self.error_request_token_response_unconfirmed)

    @raises(CommunicationFailedError)
    def test_parse_access_token_error(self):
        self.communicator.parse_access_token(self.error_access_token_response)

    @raises(UserDeniedError)
    def test_has_error_in_callback(self):
        self.communicator.has_error_in_callback(self.error_callback_denied, self.request_token_value)

    @raises(CommunicationFailedError)
    def test_has_error_in_callback_invalid_request_token(self):
        self.communicator.has_error_in_callback(self.error_callback_denied, '123abc')

    @raises(CommunicationFailedError)
    def test_has_error_in_callback_no_oauth_token(self):
        self.communicator.has_error_in_callback(self.error_callback_no_oauth_token)

    @raises(CommunicationFailedError)
    def test_has_error_in_callback_invalid_oauth_token(self):
        self.communicator.has_error_in_callback(self.error_callback_invalid_oauth_token, self.request_token_value)

    @raises(CommunicationFailedError)
    def test_get_exchange_value_from_callback_error(self):
        self.communicator.get_exchange_value_from_callback(self.error_callback_invalid_oauth_token)


class TestTwitterCommunicator(TestCase):
    def setUp(self):
        super(TestTwitterCommunicator, self).setUp()
        app = Application()
        self._twitter = TwitterCommunicator(app)

    def test_get_request_token_url__with_scope(self):
        _, data, _ = self._twitter.get_request_token_url(scope='abc def')
        self.assertIn('x_auth_access_type', data)
        self.assertEqual(data['x_auth_access_type'], 'abc def')

    def test_get_request_token_url__no_scope(self):
        _, data, _ = self._twitter.get_request_token_url(scope=None)
        self.assertNotIn('x_auth_access_type', data)
