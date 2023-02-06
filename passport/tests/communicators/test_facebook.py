# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from mock import (
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.social.broker.communicators.FacebookCommunicator import FacebookCommunicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.communicators import TestCommunicator
from passport.backend.social.common.application import Application
from passport.backend.social.common.misc import dump_to_json_string


class TestFacebook(TestCommunicator):
    code = 'AQBZ_P5xRueYTw9qTEFkwrUpl62EL15nmLdb05jfttgfsNnbBeCniH2Y1t-bqToFHTZ2G4it2bTqWG_ziblwMUrM-pNsfjz'
    access_token = 'CAADEZBFep6zkBAP4UAt7nlLPLnaIQBp1G1Hy9ND2NLi7sZA7H0f2FxozZCaEnvmZAFq87RqwHP0BKJqAonJTYciZATfy3LiA8QjlZAYHZA5QaWYVjOmRKHTEPluoGN78ZCMVMIKlHRvbLAZA6vSwiuAqV'
    normal_access_token_response = {
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 5177711,
    }
    normal_access_token_response = dump_to_json_string(normal_access_token_response)

    error_access_token_response = (400, '{"error":{"message":"Invalid verification code format.","type":"OAuthException","code":100}}')
    user_denied_response = {'error': 'access_denied', 'error_reason': 'user_denied'}
    invalid_scope_response = {'error': 'invalid_scope'}
    provider_code = 'fb'

    def setUp(self):
        super(TestFacebook, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.FacebookProxy.FacebookProxy.get_profile',
            Mock(
                return_value={
                    'userid': 100,
                    'firstname': 'Petr',
                    'lastname': 'Testov',
                    'username': 'luigi',
                },
            ),
        )
        self.patcher.start()

    def tearDown(self):
        super(TestFacebook, self).tearDown()
        self.patcher.stop()

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'GET')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.query.get('code'), self.code)
        eq_(request.query.get('redirect_uri'), 'https://social.yandex.ru/broker/redirect')

    def test_full_fb_ok(self):
        self.check_basic()

    def test_access_request_parsing_user_denied(self):
        with self.assertRaises(CommunicationFailedError):
            self.communicator.has_error_in_callback(self.invalid_scope_response)


class TestFacebookCommunicatorParseAcessToken(TestCase):
    def setUp(self):
        super(TestFacebookCommunicatorParseAcessToken, self).setUp()
        app = Application()
        self._communicator = FacebookCommunicator(app)

    def test_invalid_authorization_code(self):
        response = {
            'error': {
                'code': 100,
                'message': 'This authorization code has been used.',
            },
        }
        response = json.dumps(response)

        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_unknown_error(self):
        response = {'error': {'code': 100500}}
        response = json.dumps(response)

        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)
