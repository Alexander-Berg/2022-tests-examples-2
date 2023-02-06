# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.tests.communicators import TestCommunicator
from passport.backend.social.common.misc import dump_to_json_string


class TestMailRu(TestCommunicator):
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
    error_access_token_response = (400, '{"error":"invalid_grant","error_description":"Code is invalid or expired."}')
    user_denied_response = {'error': 'access_denied'}
    invalid_scope_response = {'error': 'invalid_scope'}

    provider_code = 'mr'

    def setUp(self):
        super(TestMailRu, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.MailRuProxy.MailRuProxy.get_profile',
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
        super(TestMailRu, self).tearDown()
        self.patcher.stop()

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'POST')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.data.get('code'), self.code)

        redirect_uri = request.data.get('redirect_uri') or ''
        ok_(
            redirect_uri.startswith('https://social.yandex.ru/broker/redirect?'),
            request.data.get('redirect_uri'),
        )

        ok_('client_id' in request.data, request.data)
        ok_('client_secret' in request.data, request.data)
        eq_(request.data.get('grant_type'), 'authorization_code')

    def test_full_mr_ok(self):
        self.check_basic()

    def test_access_request_parsing_user_denied(self):
        with self.assertRaises(CommunicationFailedError):
            self.communicator.has_error_in_callback(self.invalid_scope_response)
