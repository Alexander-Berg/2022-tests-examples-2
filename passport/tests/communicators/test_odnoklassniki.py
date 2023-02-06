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
)
from passport.backend.social.broker.communicators.OdnoklassnikiCommunicator import OdnoklassnikiCommunicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.communicators import TestCommunicator
from passport.backend.social.common.application import Application
from passport.backend.social.common.misc import dump_to_json_string


class TestOdnoklassniki(TestCommunicator):
    code = '1acd4159dce3e50948797cbcc5e3f78d'
    access_token = '26348ca96f87100ae521bda01c53a937'
    refresh_token = '247c28ad905ad0445b3a2dca56f0c496'
    normal_access_token_response = {
        'refresh_token': refresh_token,
        'expires_in': 86400,
        'access_token': access_token,
        'token_type': 'bearer',
        'x_mailru_vid': '17296813064748254003',
    }
    normal_access_token_response = dump_to_json_string(normal_access_token_response)
    error_access_token_response = (200, '{"error_description":"Invalid code","error":"invalid_request"}')
    user_denied_response = {'error': 'access_denied'}

    provider_code = 'ok'

    def setUp(self):
        super(TestOdnoklassniki, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.OdnoklassnikiProxy.OdnoklassnikiProxy.get_profile',
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
        super(TestOdnoklassniki, self).tearDown()
        self.patcher.stop()

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'POST')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.data.get('code'), self.code)

        redirect_uri = '%s%s%s' % (
            'https://social.yandex.ru/broker/redirect?url=https%3A%2F%2Fsocialdev-1.yandex.ru%2Fbroker2%2F',
            data_in['task_id'],
            '%2Fcallback',
        )
        eq_(
            request.data.get('redirect_uri'),
            redirect_uri,
        )

        ok_('client_id' in request.data, request.data)
        ok_('client_secret' in request.data, request.data)
        eq_(request.data.get('grant_type'), 'authorization_code')

    def test_full_ok_ok(self):
        self.check_basic()


class TestOdnoklassnikiCommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestOdnoklassnikiCommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = OdnoklassnikiCommunicator(app)

    def test_invalid_request(self):
        response = {'error_description': 'Invalid code', 'error': 'invalid_request'}
        response = json.dumps(response)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_invalid_token(self):
        response = {'error_description': 'Session expired', 'error': 'invalid_token'}
        response = json.dumps(response)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)
