# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta
import json

from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.undefined import Undefined
from passport.backend.social.broker.communicators.communicator import AuthorizeOptions
from passport.backend.social.broker.communicators.MtsCommunicator import (
    MtsV2Communicator,
    MtsV3Communicator,
)
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Mts import Mts
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    CALLBACK_URL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.parameterized import parameterized_expand
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.useragent import Url
from passport.backend.social.proxylib.test import mts as mts_test


class TestMtsV2CommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestMtsV2CommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = MtsV2Communicator(app)

    def test_invalid_request(self):
        response = {'error': 'invalid_request'}
        response = json.dumps(response)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_invalid_grant(self):
        response = {'error': 'invalid_grant'}
        response = json.dumps(response)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)

    def test_error_null(self):
        response = oauth2.test.oauth2_access_token_response(extra={'error': None})
        access_token = self._communicator.parse_access_token(response.data)

        assert access_token.get('value') == APPLICATION_TOKEN1


class TestMtsV2CommunicatorGetAuthorizeRedirectUrl(TestCase):
    def setUp(self):
        super(TestMtsV2CommunicatorGetAuthorizeRedirectUrl, self).setUp()
        self._app = Application(
            id=EXTERNAL_APPLICATION_ID1,
            domain='social.yandex.net',
        )
        self._communicator = MtsV2Communicator(self._app)

    def test_basic(self):
        authz_url = self._communicator.get_authorize_url(AuthorizeOptions(callback_url=CALLBACK_URL1))
        authz_url = Url(authz_url)

        self.assertEqual(authz_url.paramless, 'https://login.mts.ru/amserver/UI/Login')

        self.assertEqual(
            sorted(authz_url.params.keys()),
            [
                'access_type',
                'auth-service',
                'goto',
                'service',
            ],
        )

        self.assertEqual(authz_url.params['access_type'], 'offline')
        self.assertEqual(authz_url.params['auth-service'], 'music2')
        self.assertEqual(authz_url.params['service'], 'music2')

        check_url_equals(
            'https://login.mts.ru' + authz_url.params['goto'],
            str(
                Url(
                    'https://login.mts.ru/amserver/oauth2/auth',
                    {
                        'response_type': 'code',
                        'redirect_uri': 'https://social.yandex.net/broker/redirect',
                        'access_type': 'offline',
                        'client_id': EXTERNAL_APPLICATION_ID1,
                        'state': CALLBACK_URL1,
                        'auth-service': 'login',
                        'sms': 'forced',
                        'srcsvc': 'music',
                    },
                ),
            ),
        )


class TestMtsV3SantizeClientToken(TestCase):
    def setUp(self):
        super(TestMtsV3SantizeClientToken, self).setUp()
        self.app = Application(
            engine_id='mts_v3',
            id=EXTERNAL_APPLICATION_ID1,
            identifier=APPLICATION_ID1,
            provider=providers.get_provider_info_by_name(Mts.code),
            request_from_intranet_allowed=True,
        )
        self.communicator = MtsV3Communicator(self.app)

    def build_access_token(
        self,
        expired=Undefined,
        scopes=Undefined,
    ):
        if expired is Undefined:
            expired = DatetimeNow(timestamp=now() + timedelta(seconds=APPLICATION_TOKEN_TTL1))
        if scopes is Undefined:
            scopes = 'phone profile'
        return Token(
            application_id=self.app.identifier,
            expired=expired,
            scopes=scopes,
            value=APPLICATION_TOKEN1,
        )

    def build_refresh_token(self, scopes=Undefined):
        if scopes is Undefined:
            scopes = 'phone profile'
        return RefreshToken(scopes=scopes, value=APPLICATION_TOKEN2)

    def test_ok(self):
        server_token, refresh_token = self.communicator.sanitize_client_token(
            Token(
                application_id=self.app.identifier,
                value=mts_test.build_client_token_v1(),
            ),
        )

        self.assertEqual(server_token, self.build_access_token())
        self.assertEqual(refresh_token, self.build_refresh_token())

    @parameterized_expand(
        [
            ('access_token',),
            ('version',),
        ],
    )
    def test_no_required_attr(self, required_attr):
        with self.assertRaises(InvalidTokenProxylibError):
            self.communicator.sanitize_client_token(
                Token(
                    application_id=self.app.identifier,
                    value=mts_test.build_client_token_v1(exclude_attrs=[required_attr]),
                ),
            )

    def test_no_expires_in(self):
        server_token, refresh_token = self.communicator.sanitize_client_token(
            Token(
                application_id=self.app.identifier,
                value=mts_test.build_client_token_v1(exclude_attrs=['expires_in']),
            ),
        )

        self.assertEqual(server_token, self.build_access_token(expired=None))
        self.assertEqual(refresh_token, self.build_refresh_token())

    def test_no_scope(self):
        server_token, refresh_token = self.communicator.sanitize_client_token(
            Token(
                application_id=self.app.identifier,
                value=mts_test.build_client_token_v1(exclude_attrs=['scope']),
            ),
        )

        self.assertEqual(server_token, self.build_access_token(scopes=None))
        self.assertEqual(refresh_token, self.build_refresh_token(scopes=None))

    def test_no_refresh_token(self):
        server_token, refresh_token = self.communicator.sanitize_client_token(
            Token(
                application_id=self.app.identifier,
                value=mts_test.build_client_token_v1(exclude_attrs=['refresh_token']),
            ),
        )

        self.assertEqual(server_token, self.build_access_token())
        self.assertIsNone(refresh_token)
