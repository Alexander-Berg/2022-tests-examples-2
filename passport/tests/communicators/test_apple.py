# -*- coding: utf-8 -*-

from passport.backend.social.broker.communicators.AppleCommunicator import AppleCommunicator
from passport.backend.social.broker.exceptions import ApplicationUnknownError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.exception import InvalidTokenProxylibError
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Apple import Apple
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    FIRSTNAME1,
    LASTNAME1,
)
from passport.backend.social.common.test.parameterized import parameterized_expand
from passport.backend.social.common.token.domain import Token
from passport.backend.social.proxylib.test import apple as apple_test


class BaseAppleCommunicatorTestCase(TestCase):
    def setUp(self):
        super(BaseAppleCommunicatorTestCase, self).setUp()
        self.fake_proxy = apple_test.FakeProxy().start()

    def tearDown(self):
        self.fake_proxy.stop()
        del self.fake_proxy
        super(BaseAppleCommunicatorTestCase, self).tearDown()

    def build_settings(self):
        settings = super(BaseAppleCommunicatorTestCase, self).build_settings()
        settings['providers'] = [
            {
                'id': Apple.id,
                'code': Apple.code,
                'name': 'apple',
            },
        ]
        return settings

    def build_token(
        self,
        app=None,
        expires_at=None,
        key_id=None,
        client_token_userinfo=None,
        client_token_exclude_attrs=None,
    ):
        if app is None:
            app = self.build_app()
        id_token = self.build_id_token(
            exp=expires_at,
            key_id=key_id,
        )

        if client_token_userinfo is None:
            client_token_userinfo = dict(
                firstname=FIRSTNAME1,
                lastname=LASTNAME1,
            )
        client_token = dict(id_token=id_token)
        client_token.update(client_token_userinfo)
        client_token = apple_test.build_client_token_v1(client_token, client_token_exclude_attrs)

        token = Token(
            application_id=app.identifier,
            value=client_token,
        )
        return token

    def build_app(self, identifier=APPLICATION_ID1):
        return Application(
            domain='social.yandex.net',
            identifier=identifier,
            id=EXTERNAL_APPLICATION_ID1,
            provider=providers.get_provider_info_by_name(Apple.code),
            request_from_intranet_allowed=True,
        )

    def build_id_token(self, exp=None, key_id=None):
        if exp is None:
            exp = int(now.f() + APPLICATION_TOKEN_TTL1)
        return apple_test.build_id_token(
            id_token=dict(exp=exp),
            key_id=key_id,
        )

    def build_communicator(self, app=None):
        if app is None:
            app = self.build_app()
        return AppleCommunicator(app)


class TestSanitizeClientToken(BaseAppleCommunicatorTestCase):
    def test_ok(self):
        public_keys_response = apple_test.AppleApi.get_public_keys()
        self.fake_proxy.set_response_values(
            'get_public_keys',
            [
                public_keys_response,
                public_keys_response,
            ],
        )
        app = self.build_app(identifier=APPLICATION_ID1)
        expires_at = int(now.f() + APPLICATION_TOKEN_TTL1)
        token = self.build_token(app=app, expires_at=expires_at)
        comm = self.build_communicator(app)

        server_token, refresh_token = comm.sanitize_client_token(token)

        id_token = self.build_id_token(exp=expires_at)
        self.assertEqual(
            server_token,
            Token(
                application_id=APPLICATION_ID1,
                expired=expires_at,
                value=id_token,
            ),
        )
        self.assertIsNone(refresh_token)

    def test_invalid_signature(self):
        self.fake_proxy.set_response_values(
            'get_public_keys',
            [
                apple_test.AppleApi.get_public_keys([apple_test.APPLE_JSON_WEB_KEY2]),
            ],
        )
        comm = self.build_communicator()
        token_expires_at = int(now.f() + APPLICATION_TOKEN_TTL1)
        token = self.build_token(
            expires_at=token_expires_at,
            key_id=apple_test.APPLE_JSON_WEB_KEY2['kid'],
        )

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            comm.sanitize_client_token(token)

        self.assertEqual(
            str(assertion.exception),
            'Token corrupted: %s' % self.build_id_token(
                exp=token_expires_at,
                key_id=apple_test.APPLE_JSON_WEB_KEY2['kid'],
            ),
        )


class TestGetAuthorizeRedirectUrl(BaseAppleCommunicatorTestCase):
    def test(self):
        comm = self.build_communicator()

        with self.assertRaises(ApplicationUnknownError):
            comm.get_authorize_url()


class TestClientTokenToSocialUserinfo(BaseAppleCommunicatorTestCase):
    def build_userinfo(self, userinfo=None, exclude_attrs=None):
        default_userinfo = dict(
            firstname=FIRSTNAME1,
            lastname=LASTNAME1,
        )
        return build_dict_from_standard(default_userinfo, userinfo, exclude_attrs)

    def test_ok(self):
        comm = self.build_communicator()
        token = self.build_token(
            client_token_userinfo=dict(
                firstname=FIRSTNAME1,
                lastname=LASTNAME1,
            ),
        )
        userinfo = comm.client_token_to_social_userinfo(token)

        self.assertEqual(
            userinfo,
            self.build_userinfo(
                dict(
                    firstname=FIRSTNAME1,
                    lastname=LASTNAME1,
                ),
            ),
        )

    @parameterized_expand(
        [
            ('firstname',),
            ('lastname',),
        ],
    )
    def test_none_attr_dont_get_to_useinfo(self, name):
        comm = self.build_communicator()
        token = self.build_token(
            client_token_userinfo={
                name: None,
            },
        )
        userinfo = comm.client_token_to_social_userinfo(token)

        self.assertEqual(
            userinfo,
            self.build_userinfo(exclude_attrs=[name]),
        )

    @parameterized_expand(
        [
            ('firstname',),
            ('lastname',),
        ],
    )
    def test_missing_attr_dont_get_to_userinfo(self, name):
        comm = self.build_communicator()
        token = self.build_token(
            client_token_exclude_attrs=[name],
        )
        userinfo = comm.client_token_to_social_userinfo(token)

        self.assertEqual(
            userinfo,
            self.build_userinfo(exclude_attrs=[name]),
        )

    @parameterized_expand(
        [
            ('firstname',),
            ('lastname',),
        ],
    )
    def test_empty_str_attr_dont_get_to_userinfo(self, name):
        comm = self.build_communicator()
        token = self.build_token(
            client_token_userinfo={
                name: '',
            },
        )
        userinfo = comm.client_token_to_social_userinfo(token)

        self.assertEqual(
            userinfo,
            self.build_userinfo(exclude_attrs=[name]),
        )
