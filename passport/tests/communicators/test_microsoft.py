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


TEST_ACCESS_TOKEN = (
    'EwBwAul3BAAUo4xeBIbHjhBxWOFekj4Xy2fhaGQAAbcedGKcaMI/NC%2bWb%2bx3jII/d74fu'
    'amAv93y2O/R5d/8ddXCXhzFSizTjqXw4ZUD3Rq9JKxW8JlvHKpP0iETz4xjEXyKnktgGoQ6X4'
    'gfBHN1VJbPs49zwja4Gh6SfeLixHkx9fQ/SmP46uivSRFM5aqASWJChlzBXr6wA8TBwvN3pCw'
    'hY0V7qQ4KK6UuMMjy7uCpZYa8oyG6tw8Cj9kDmSWbGs8Em7svPPC7Qeir2rSnqv37SjAKtm4u'
    '0g7f5NzpUE98NaLh/q4hNo0E/7ACeD8rpINqWJ9cYEm2xfOYaN%2bfJsUgAf3a6NOfBdfQyrP'
    'juF1qarkE%2bOaOJr/4YOZvn00DZgAACNYu2Oy4j%2bCoQAHhH3ex37GYPWS/kjuOhUGM1wYP'
    '9QCMka4wv8upxwRmdzXkLg8XGeZ/q3UwEAHUJYaPGkjYuUuf12TnC/VDUG%2befijNPqw%2by'
    'dSbaAR0u6T%2bv7Frv5Fx3p4Je7EKYKbK1tJqcrQvKCv0l0%2b6%2bwv1kKI5qaLYmmZTbyoo'
    'n5Phn52fNVnH/ZMZwDSwta9tV01r/1q9Fpq2IAac3YlOqY6QYrwaasdG47cJAgMXQXGeeymR1'
    '33hV1pgt4OXzMOqTeohIUZBoCoGEzUe/oXxAU7sAQgV2j/kP7fYGBNIi6ADztRe5zU/M4YIoj'
    'ogDXxEexz%2bUl/CEfwLGnw/aIdv4/REZCQlhue4TS1TRyyEQ5BU2somBkvsl8cPCNfjNBGB5'
    'OK2SYUGplKwaBX1g5jUR0j2Loj42gSWVkjiZRRIE82sy7tqLV4C'
)


class TestMicrosoft(TestCommunicator):
    code = 'AQBZ_P5xRueYTw9qTEFkwrUpl62EL15nmLdb05jfttgfsNnbBeCniH2Y1t-bqToFHTZ2G4it2bTqWG_ziblwMUrM-pNsfjz'
    normal_access_token_response = '{"access_token": "%s", "expires_in": 5173492}' % TEST_ACCESS_TOKEN
    access_token = TEST_ACCESS_TOKEN
    error_access_token_response = (400, '{"error":"invalid_grant","error_description":"The provided value for the \'code\' parameter is not valid."}')
    user_denied_response = {'error': 'access_denied'}
    invalid_scope_response = {'error': 'invalid_scope'}
    provider_code = 'ms'

    def setUp(self):
        super(TestMicrosoft, self).setUp()
        self.patcher = patch(
            'passport.backend.social.proxylib.MicrosoftProxy.MicrosoftProxy.get_profile',
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
        self.patcher.stop()
        super(TestMicrosoft, self).tearDown()

    def check_request_url(self, request, handler=None, data_in=None, **kwargs):
        eq_(request.method, 'POST')
        eq_(request.url, handler.communicator.OAUTH_ACCESS_TOKEN_URL)
        eq_(request.data.get('code'), self.code)

        redirect_uri = request.data.get('redirect_uri') or ''
        ok_(
            redirect_uri.startswith('https://social.yandex.net/broker/redirect?'),
            request.data.get('redirect_uri'),
        )

        ok_('client_id' in request.data, request.data)
        ok_('client_secret' in request.data, request.data)
        eq_(request.data.get('grant_type'), 'authorization_code')

    def test_full_ms_ok(self):
        self.check_basic()

    def test_access_request_parsing_user_denied(self):
        with self.assertRaises(CommunicationFailedError):
            self.communicator.has_error_in_callback(self.invalid_scope_response)
