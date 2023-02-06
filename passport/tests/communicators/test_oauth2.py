# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import json
from urlparse import urlparse

from mock import Mock
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker.communicators.communicator import (
    AuthorizeOptions,
    OAuth2Communicator,
)
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.oauth2.test import oauth2_access_token_response
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    AUTHORIZATION_CODE1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
)
from passport.backend.social.common.test.fake_useragent import FakeZoraUseragent
from passport.backend.social.common.test.types import (
    ApproximateInteger,
    FakeResponse,
)
from passport.backend.social.common.useragent import (
    Url,
    ZoraUseragent,
)


CALLBACK_URL1 = 'https://social.yandex.net/broker/redirect'
ACCESS_TOKEN_URL1 = 'https://access_token/'


class TestOauth2CommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = OAuth2Communicator(app)

    def build_access_token(
        self,
        value=APPLICATION_TOKEN1,
        expires=None,
        refresh=None,
    ):
        access_token = dict(
            value=value,
            expires=expires,
        )
        if refresh is not None:
            access_token.update(refresh=refresh)
        return access_token

    def test_empty_response(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(json.dumps({}))

    def test_too_long_response(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token('1' * 10240)

    def test_response_not_a_dict(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token('1')

    def test_no_expires_in(self):
        response = oauth2_access_token_response(expires_in=None)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(access_token, self.build_access_token(expires=None))

    def test_expires_in_empty(self):
        response = oauth2_access_token_response(expires_in='')
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(access_token, self.build_access_token(expires=None))

    def test_expires_in_integer(self):
        response = oauth2_access_token_response(expires_in=1)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(
                expires=ApproximateInteger(now.i() + 1),
            ),
        )

    def test_expires_in_string_integer(self):
        response = oauth2_access_token_response(expires_in=' %s ' % APPLICATION_TOKEN_TTL1)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(
                expires=ApproximateInteger(now.i() + APPLICATION_TOKEN_TTL1),
            ),
        )

    def test_expires_in_float(self):
        response = oauth2_access_token_response(expires_in=1.0)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(
                expires=ApproximateInteger(now.i() + 1),
            ),
        )

    def test_expires_in_string_float(self):
        response = oauth2_access_token_response(expires_in=' 1.0 ')
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(
                expires=ApproximateInteger(now.i() + 1),
            ),
        )

    def test_expires_in_invalid(self):
        response = oauth2_access_token_response(expires_in='invalid')
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response.data)

    def test_no_access_token(self):
        response = oauth2_access_token_response(access_token=None)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response.data)

    def test_access_token_empty(self):
        response = oauth2_access_token_response(access_token='')
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response.data)

    def test_access_token_too_long(self):
        response = oauth2_access_token_response(access_token='1' * 30001)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response.data)

    def test_access_token_ok(self):
        response = oauth2_access_token_response(access_token=APPLICATION_TOKEN1)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(value=APPLICATION_TOKEN1),
        )

    def test_no_refresh_token(self):
        response = oauth2_access_token_response(refresh_token=None)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertNotIn('refresh', access_token)

    def test_refresh_token_empty(self):
        response = oauth2_access_token_response(refresh_token='')
        access_token = self._communicator.parse_access_token(response.data)
        self.assertNotIn('refresh', access_token)

    def test_refresh_token_too_long(self):
        response = oauth2_access_token_response(refresh_token='1' * 30001)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response.data)

    def test_refresh_token_ok(self):
        response = oauth2_access_token_response(refresh_token=APPLICATION_TOKEN1)
        access_token = self._communicator.parse_access_token(response.data)
        self.assertEqual(
            access_token,
            self.build_access_token(refresh=APPLICATION_TOKEN1),
        )


class TestOauth2CommunicatorRetriesOnHttpStatus5xx(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorRetriesOnHttpStatus5xx, self).setUp()
        app = Application(
            request_from_intranet_allowed=True,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            domain='social.yandex.net',
        )
        self._communicator = OAuth2Communicator(app)
        self._communicator.OAUTH_ACCESS_TOKEN_URL = 'https://access.token/url'

    def build_settings(self):
        settings = super(TestOauth2CommunicatorRetriesOnHttpStatus5xx, self).build_settings()
        settings['social_config'].update(
            dict(
                retries=2,
            ),
        )
        return settings

    def test(self):
        self._fake_useragent.set_response_values(
            [
                FakeResponse('', 500),
                oauth2_access_token_response(),
            ],
        )

        self._communicator.get_access_token(
            AUTHORIZATION_CODE1,
            callback_url=CALLBACK_URL1,
            scopes=None,
            request_token=None,
        )

        self.assertEqual(len(self._fake_useragent.requests), 2)


class TestOauth2CommunicatorUsesZora(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorUsesZora, self).setUp()
        self._communicator = self._build_communicator()
        self._fake_zora_useragent = FakeZoraUseragent().start()

        zora_useragent = ZoraUseragent(Mock(name='tvm_credentials_manager'))
        LazyLoader.register('zora_useragent', lambda: zora_useragent)

    def tearDown(self):
        self._fake_zora_useragent.stop()
        super(TestOauth2CommunicatorUsesZora, self).tearDown()

    def _build_communicator(self, request_from_intranet_allowed=False):
        app = Application(
            request_from_intranet_allowed=request_from_intranet_allowed,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            domain=urlparse(CALLBACK_URL1).hostname,
        )
        communicator = OAuth2Communicator(app)
        communicator.OAUTH_ACCESS_TOKEN_URL = 'https://access_token/'
        communicator.ACCESS_TOKEN_REQUEST_TYPE = 'POST'
        return communicator

    def test_get_access_token(self):
        def _get_access_token(communicator):
            communicator.get_access_token(
                AUTHORIZATION_CODE1,
                callback_url=CALLBACK_URL1,
                scopes=None,
                request_token=None,
            )

        self._fake_zora_useragent.set_response_value(oauth2_access_token_response())

        _get_access_token(self._communicator)

        self.assertEqual(len(self._fake_zora_useragent.requests), 1)
        self.assertEqual(self._fake_zora_useragent.requests[0].url, 'https://access_token/')
        self.assertEqual(len(self._fake_useragent.requests), 0)

        self._fake_useragent.set_response_value(oauth2_access_token_response())
        communicator = self._build_communicator(request_from_intranet_allowed=True)

        _get_access_token(communicator)

        self.assertEqual(len(self._fake_useragent.requests), 1)
        self.assertEqual(self._fake_useragent.requests[0].url, 'https://access_token/')
        self.assertEqual(len(self._fake_zora_useragent.requests), 1)


class TestOauth2CommunicatorAccessToken(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorAccessToken, self).setUp()
        self._communicator = self.build_communicator()

        self._fake_useragent.set_response_values([
            oauth2_access_token_response(),
        ])

    def build_communicator(self, app=None):
        if app is None:
            app = self.build_application()
        com = OAuth2Communicator(app)
        com.ACCESS_TOKEN_REQUEST_TYPE = 'POST'
        com.OAUTH_ACCESS_TOKEN_URL = 'https://access.token/url'
        return com

    def build_application(self):
        return Application(
            domain='social.yandex.net',
            id=EXTERNAL_APPLICATION_ID1,
            request_from_intranet_allowed=True,
            secret=APPLICATION_SECRET1,
        )

    def get_access_token_simple(self, communicator=None):
        if communicator is None:
            communicator = self._communicator
        return communicator.get_access_token(
            AUTHORIZATION_CODE1,
            callback_url=CALLBACK_URL1,
            scopes=None,
            request_token=None,
        )

    def test_ok(self):
        self.get_access_token_simple()

        self.assertEqual(len(self._fake_useragent.requests), 1)
        self.assertEqual(
            self._fake_useragent.requests[0].headers,
            {
                'User-Agent': 'yandex-social-useragent/0.1',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )
        self.assertEqual(self._fake_useragent.requests[0].method, 'POST')
        self.assertDictContainsSubset(
            {
                'grant_type': 'authorization_code',
                'code': AUTHORIZATION_CODE1,
                'client_id': EXTERNAL_APPLICATION_ID1,
                'client_secret': APPLICATION_SECRET1,
            },
            self._fake_useragent.requests[0].data,
        )
        self.assertIn('redirect_uri', self._fake_useragent.requests[0].data)

    def test_custom_provider_client_id(self):
        app = self.build_application()
        app.custom_provider_client_id = EXTERNAL_APPLICATION_ID2

        self.get_access_token_simple(self.build_communicator(app))

        assert len(self._fake_useragent.requests) == 1
        assert self._fake_useragent.requests[0].data.get('client_id') == EXTERNAL_APPLICATION_ID2


class TestOauth2CommunicatorAccessTokenBasicAuth(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorAccessTokenBasicAuth, self).setUp()
        app = Application(
            request_from_intranet_allowed=True,
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            domain='social.yandex.net',
        )
        self._communicator = OAuth2Communicator(app)
        self._communicator.OAUTH_AUTH_TYPE_BASIC = True
        self._communicator.ACCESS_TOKEN_REQUEST_TYPE = 'POST'
        self._communicator.OAUTH_ACCESS_TOKEN_URL = 'https://access.token/url'

    def test(self):
        self._fake_useragent.set_response_values([
            oauth2_access_token_response(),
        ])

        self._communicator.get_access_token(
            AUTHORIZATION_CODE1,
            callback_url=CALLBACK_URL1,
            scopes=None,
            request_token=None,
        )

        self.assertEqual(len(self._fake_useragent.requests), 1)
        auth_basic = 'Basic %s' % base64.b64encode('%s:%s' % (
            EXTERNAL_APPLICATION_ID1,
            APPLICATION_SECRET1,
        ))
        self.assertEqual(
            self._fake_useragent.requests[0].headers,
            {
                'User-Agent': 'yandex-social-useragent/0.1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': auth_basic,
            },
        )
        self.assertEqual(self._fake_useragent.requests[0].method, 'POST')
        self.assertDictContainsSubset(
            {
                'grant_type': 'authorization_code',
                'code': AUTHORIZATION_CODE1,
            },
            self._fake_useragent.requests[0].data,
        )
        self.assertIn('redirect_uri', self._fake_useragent.requests[0].data)
        self.assertNotIn('client_id', self._fake_useragent.requests[0].data)
        self.assertNotIn('client_secret', self._fake_useragent.requests[0].data)


class TestOauth2CommunicatorGetAuthorizeRedirectUrl(TestCase):
    def setUp(self):
        super(TestOauth2CommunicatorGetAuthorizeRedirectUrl, self).setUp()
        self._communicator = self.build_communicator()

    def build_communicator(self, app=None):
        if app is None:
            app = self.build_application()
        com = OAuth2Communicator(app)
        com.IS_CALLBACK_IN_STATE = True
        com.OAUTH_AUTHORIZE_URL = 'https://authori.ze/url'
        return com

    def build_application(self):
        return Application(
            domain='social.yandex.net',
            id=EXTERNAL_APPLICATION_ID1,
        )

    def test_ok(self):
        authorization_url = Url(self._communicator.get_authorize_url(AuthorizeOptions('state')))

        check_url_equals(
            str(authorization_url),
            str(
                Url(
                    'https://authori.ze/url',
                    params=dict(
                        client_id=EXTERNAL_APPLICATION_ID1,
                        redirect_uri='https://social.yandex.net/broker/redirect',
                        response_type='code',
                        state='state',
                    ),
                ),
            ),
        )

    def test_custom_provider_client_id(self):
        app = self.build_application()
        app.custom_provider_client_id = EXTERNAL_APPLICATION_ID2
        com = self.build_communicator(app)

        authorization_url = Url(com.get_authorize_url(AuthorizeOptions('state')))

        assert authorization_url.params.get('client_id') == EXTERNAL_APPLICATION_ID2
