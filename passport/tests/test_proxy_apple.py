# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

import jwt
from jwt import PyJWS
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.exception import (
    InvalidTokenProxylibError,
    UnexpectedResponseProxylibError,
)
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.providers.Apple import Apple
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EMAIL1,
    EMAIL2,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
)
from passport.backend.social.common.test.parameterized import parameterized_expand
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import ApproximateInteger
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.AppleProxy import APPLE_TOKEN_ISSUER
from passport.backend.social.proxylib.test import apple as apple_test
from passport.backend.social.proxylib.test.base import FakeResponse


class BaseAppleProxyTestCase(TestCase):
    def setUp(self):
        super(BaseAppleProxyTestCase, self).setUp()
        self.fake_proxy = apple_test.FakeProxy().start()
        passport.backend.social.proxylib.init()

        self.fake_proxy.set_response_value(
            'get_public_keys',
            apple_test.AppleApi.get_public_keys(),
        )

    def tearDown(self):
        self.fake_proxy.stop()
        super(BaseAppleProxyTestCase, self).tearDown()

    def build_settings(self):
        settings = super(BaseAppleProxyTestCase, self).build_settings()
        settings['social_config'].update(
            apple_jwt_certificate_id=apple_test.APPLE_JSON_WEB_KEY1['kid'],
            apple_team_id=apple_test.APPLE_TEAM_ID1,
        )
        settings['social_config'].update({
            'apple_jwt_certificate_' + apple_test.APPLE_JSON_WEB_KEY1['kid']: apple_test.APPLE_PRIVATE_KEY1,
            'apple_jwt_certificate_' + apple_test.APPLE_JSON_WEB_KEY2['kid']: apple_test.APPLE_PRIVATE_KEY2,
        })
        return settings

    def build_id_token(
        self,
        id_token=None,
        exclude_attrs=None,
        private_key=apple_test.APPLE_PRIVATE_KEY1,
        key_id=apple_test.APPLE_JSON_WEB_KEY1['kid'],
        algorithm=None,
    ):
        default_kwargs = dict(
            email=EMAIL1,
            email_verified='true',
            exp=int(now.f() + APPLICATION_TOKEN_TTL1),
            is_private_email='false',
            sub=SIMPLE_USERID1,
        )
        id_token = build_dict_from_standard(default_kwargs, id_token)
        return apple_test.build_id_token(
            id_token=id_token,
            exclude_attrs=exclude_attrs,
            private_key=private_key,
            key_id=key_id,
            algorithm=algorithm,
        )

    def build_token_dict(self, value):
        return dict(value=value)

    def build_proxy(self, token):
        return get_proxy(Apple.code, token)

    def build_app(self):
        return Application(
            domain='social.yandex.net',
            id=EXTERNAL_APPLICATION_ID1,
            request_from_intranet_allowed=True,
        )


class TestGetProfile(BaseAppleProxyTestCase):
    def test_email_public_verified(self):
        token = self.build_token_dict(
            self.build_id_token(
                dict(
                    email=EMAIL1,
                    sub=SIMPLE_USERID1,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        profile = proxy.get_profile()

        self.assertEqual(
            profile,
            dict(
                email=EMAIL1,
                userid=SIMPLE_USERID1,
            ),
        )

    def test_email_not_public_verified(self):
        token = self.build_token_dict(
            self.build_id_token(
                dict(
                    email=EMAIL1,
                    sub=SIMPLE_USERID1,
                    is_private_email='true',
                ),
            ),
        )
        proxy = self.build_proxy(token)

        profile = proxy.get_profile()

        self.assertEqual(
            profile,
            dict(
                userid=SIMPLE_USERID1,
            ),
        )

    def test_email_public_not_verified(self):
        token = self.build_token_dict(
            self.build_id_token(
                dict(
                    email=EMAIL1,
                    sub=SIMPLE_USERID1,
                ),
                exclude_attrs=['email_verified'],
            ),
        )
        proxy = self.build_proxy(token)

        profile = proxy.get_profile()

        self.assertEqual(
            profile,
            dict(
                userid=SIMPLE_USERID1,
            ),
        )

    def test_email_at_privaterelay_domain(self):
        token = self.build_token_dict(
            self.build_id_token(
                dict(
                    email='hello@privaterelay.appleid.com',
                    sub=SIMPLE_USERID1,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        profile = proxy.get_profile()

        self.assertEqual(
            profile,
            dict(
                userid=SIMPLE_USERID1,
            ),
        )

    def test_no_sub(self):
        id_token = self.build_id_token(None, exclude_attrs=['sub'])
        token = self.build_token_dict(id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(UnexpectedResponseProxylibError) as assertion:
            proxy.get_profile()

        self.assertEqual(str(assertion.exception), 'Invalid sub: ' + id_token)

    def test_invalid_token(self):
        id_token = self.build_id_token(None, private_key=apple_test.APPLE_PRIVATE_KEY2)
        token = self.build_token_dict(id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_profile()

        self.assertEqual(str(assertion.exception), 'Token corrupted: ' + id_token)


class TestGetTokenInfo(BaseAppleProxyTestCase):
    def build_token_info(self, token_info=None, exclude_attrs=None):
        expires_at = ApproximateInteger(int(now.f() + APPLICATION_TOKEN_TTL1))
        default_kwargs = dict(
            client_id=EXTERNAL_APPLICATION_ID1,
            email=EMAIL1,
            email_verified=True,
            expires=expires_at,
            is_private_email=False,
            userid=SIMPLE_USERID1,
        )
        return build_dict_from_standard(default_kwargs, token_info, exclude_attrs)

    @parameterized_expand(
        [
            (
                dict(aud=EXTERNAL_APPLICATION_ID1),
                dict(client_id=EXTERNAL_APPLICATION_ID1),
            ),
            (
                dict(aud=EXTERNAL_APPLICATION_ID2),
                dict(client_id=EXTERNAL_APPLICATION_ID2),
            ),
            (
                dict(email=EMAIL1),
                dict(email=EMAIL1),
            ),
            (
                dict(email=EMAIL2),
                dict(email=EMAIL2),
            ),
            (
                dict(email_verified='true'),
                dict(email_verified=True),
            ),
            (
                dict(email_verified='false'),
                dict(email_verified=False),
            ),
            (
                dict(is_private_email='true'),
                dict(is_private_email=True),
            ),
            (
                dict(is_private_email='false'),
                dict(is_private_email=False),
            ),
            (
                dict(sub=SIMPLE_USERID1),
                dict(userid=SIMPLE_USERID1),
            ),
            (
                dict(sub=SIMPLE_USERID2),
                dict(userid=SIMPLE_USERID2),
            ),
        ],
    )
    def test_valid_key_value(self, id_token_args, token_info_args):
        token = self.build_token_dict(
            value=self.build_id_token(id_token_args),
        )
        proxy = self.build_proxy(token)

        token_info = proxy.get_token_info()

        self.assertEqual(
            token_info,
            self.build_token_info(token_info_args),
        )

    @parameterized_expand(
        [
            ('email_verified', 'hello'),
            ('is_private_email', 'hello'),
        ],
    )
    def test_invalid_key_value(self, key, value):
        id_token = self.build_id_token({key: value})
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(UnexpectedResponseProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Invalid %s: %s' % (key, id_token))

    @parameterized_expand(
        [
            ('aud',),
            ('sub',),
        ],
    )
    def test_required_key(self, key):
        id_token = self.build_id_token(None, exclude_attrs=[key])
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(UnexpectedResponseProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Invalid %s: %s' % (key, id_token))

    @parameterized_expand(
        [
            ('email',),
            ('email_verified',),
            ('is_private_email',),
        ],
    )
    def test_optional_key(self, key):
        id_token = self.build_id_token(None, exclude_attrs=[key])
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        token_info = proxy.get_token_info()

        self.assertNotIn(key, token_info)

    def test_exp_key_required(self):
        id_token = self.build_id_token(None, exclude_attrs=['exp'])
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Token expired: %s' % id_token)

    def test_exp_valid_value(self):
        exp = int(now.f() + APPLICATION_TOKEN_TTL1)
        id_token = self.build_id_token(dict(exp=exp))
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        token_info = proxy.get_token_info()

        self.assertEqual(
            token_info,
            self.build_token_info(dict(expires=ApproximateInteger(exp))),
        )

    @parameterized_expand(
        [
            ('hello',),
            (-1,),
        ],
    )
    def test_exp_invalid_value(self, value):
        id_token = self.build_id_token(dict(exp=value))
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Token expired: ' + id_token)

    def test_invalid_token(self):
        id_token = self.build_id_token(None, private_key=apple_test.APPLE_PRIVATE_KEY2)
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Token corrupted: ' + id_token)

    def test_token_algo_forbidden(self):
        id_token = self.build_id_token(algorithm='HS512')
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Token corrupted: ' + id_token)

    def test_public_key_algo_forbidden(self):
        id_token = self.build_id_token()
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)
        self.fake_proxy.set_response_value(
            'get_public_keys',
            apple_test.AppleApi.get_public_keys(alg='HS512'),
        )

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Forbidden Public Key JSON Web Algorithm: HS512')

    def test_token_algo_none(self):
        id_token = self.build_id_token(algorithm='none', private_key=None)
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Token corrupted: ' + id_token)

    def test_public_key_algo_none(self):
        id_token = self.build_id_token()
        token = self.build_token_dict(value=id_token)
        proxy = self.build_proxy(token)
        self.fake_proxy.set_response_value(
            'get_public_keys',
            apple_test.AppleApi.get_public_keys(alg='none'),
        )

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.get_token_info()

        self.assertEqual(str(assertion.exception), 'Forbidden Public Key JSON Web Algorithm: none')


class TestExchangeToken(BaseAppleProxyTestCase):
    def test_ok(self):
        id_token = self.build_id_token()
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        rv = proxy.exchange_token()

        self.assertEqual(
            rv,
            dict(
                value=id_token,
            ),
        )

    def test_expired(self):
        exp = now.i()
        id_token = self.build_id_token(dict(exp=exp))
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Token expired: ' + id_token)

    def test_no_exp(self):
        id_token = self.build_id_token(None, exclude_attrs=['exp'])
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Token expired: ' + id_token)

    def test_invalid_iss(self):
        id_token = self.build_id_token(dict(iss='invalid'))
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(
            str(assertion.exception),
            'Token iss should be %s: %s' % (APPLE_TOKEN_ISSUER, id_token),
        )

    def test_no_iss(self):
        id_token = self.build_id_token(None, exclude_attrs=['iss'])
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(
            str(assertion.exception),
            'Token iss should be %s: %s' % (APPLE_TOKEN_ISSUER, id_token),
        )

    def test_invalid_signature(self):
        id_token = self.build_id_token(None, private_key=apple_test.APPLE_PRIVATE_KEY2)
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Token corrupted: ' + id_token)

    def test_invalid_type(self):
        id_token = PyJWS().encode(
            '1234',
            apple_test.APPLE_PRIVATE_KEY1,
            algorithm='RS256',
            headers={'kid': apple_test.APPLE_JSON_WEB_KEY1['kid']},
        )
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Token is not object: ' + id_token)

    def test_invalid_json_body(self):
        id_token = PyJWS().encode(
            ':)',
            apple_test.APPLE_PRIVATE_KEY1,
            algorithm='RS256',
            headers={'kid': apple_test.APPLE_JSON_WEB_KEY1['kid']},
        )
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Invalid JSON: ' + id_token)

    def test_invalid_header(self):
        id_token = PyJWS().encode(
            json.dumps(dict()),
            apple_test.APPLE_PRIVATE_KEY1,
            algorithm='RS256',
        )
        id_token = id_token.split('.')
        id_token[0] = 'invalid_header'
        id_token = '.'.join(id_token)
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Token header corrupted: ' + id_token)

    def test_unknown_public_key(self):
        id_token = self.build_id_token(key_id='unknown')
        token = self.build_token_dict(
            value=apple_test.build_client_token_v1(
                dict(
                    id_token=id_token,
                ),
            ),
        )
        proxy = self.build_proxy(token)

        with self.assertRaises(InvalidTokenProxylibError) as assertion:
            proxy.exchange_token()

        self.assertEqual(str(assertion.exception), 'Unknown signing key: ' + id_token)


class TestGetPublicKey(BaseAppleProxyTestCase):
    def test_ok(self):
        proxy = get_proxy(Apple.code)

        rv = proxy.get_public_keys()

        self.assertEqual(
            rv,
            [
                dict(
                    alg='RS256',
                    e='AQAB',
                    kid='ApbNwEcP5MUMfH9IIwN_8QVAdKzjxjZKN6Dz8xR4I0E',
                    kty='RSA',
                    n='wxL1e9i74LR-V-iEHJskBOoTjU3Zrwjitdb8F2YleCbsOmxh7Dd0RsbU8KImEm4Y8MFSM9cOpczCo-zzYZ1qgQ',
                    use='sig',
                ),
            ],
        )

    def test_error(self):
        self.fake_proxy.set_response_value(
            'get_public_keys',
            FakeResponse('Internal server error', 500),
        )
        proxy = get_proxy(Apple.code)

        with self.assertRaises(UnexpectedResponseProxylibError) as assertion:
            proxy.get_public_keys()

        self.assertEqual(str(assertion.exception), 'Response is not JSON')

    def test_no_keys(self):
        response = json.dumps(dict())
        self.fake_proxy.set_response_value(
            'get_public_keys',
            FakeResponse(response, 200),
        )

        proxy = get_proxy(Apple.code)

        with self.assertRaises(UnexpectedResponseProxylibError) as assertion:
            proxy.get_public_keys()

        self.assertEqual(str(assertion.exception), 'Failed to get public keys')

    def test_empty_keys(self):
        response = json.dumps({'keys': list()})
        self.fake_proxy.set_response_value(
            'get_public_keys',
            FakeResponse(response, 200),
        )

        proxy = get_proxy(Apple.code)

        rv = proxy.get_public_keys()

        self.assertEqual(rv, list())


class TestRevokeToken(BaseAppleProxyTestCase):
    @property
    def proxy(self):
        return get_proxy(
            Apple.code,
            self.build_token_dict(APPLICATION_TOKEN1),
            self.build_app(),
        )

    def test_ok(self):
        self.fake_proxy.set_response_value(
            'revoke_token',
            apple_test.AppleApi.revoke_token(),
        )

        self.proxy.revoke_token()

        assert len(self.fake_proxy.requests) == 1
        self.assertEqual(
            self.fake_proxy.requests[0],
            dict(
                data=dict(
                    client_id=EXTERNAL_APPLICATION_ID1,
                    client_secret=self.proxy.get_client_secret(),
                    token=APPLICATION_TOKEN1,
                    token_type_hint='access_token',
                ),
                headers=None,
                url='https://appleid.apple.com/auth/revoke',
            ),
        )

    def test_invalid_grant(self):
        self.fake_proxy.set_response_value(
            'revoke_token',
            oauth2.test.build_error('invalid_grant'),
        )

        self.proxy.revoke_token()

    def test_unauthorized_client(self):
        self.fake_proxy.set_response_value(
            'revoke_token',
            oauth2.test.build_error('unauthorized_client'),
        )

        with self.assertRaises(oauth2.token.UnauthorizedClient):
            self.proxy.revoke_token()


class TestGetClientSecret(BaseAppleProxyTestCase):
    def test_default(self):
        proxy = get_proxy(Apple.code, self.build_token_dict(APPLICATION_TOKEN1), self.build_app())

        client_secret = proxy.get_client_secret()

        assert jwt.get_unverified_header(client_secret) == dict(
            alg='ES256',
            kid=apple_test.APPLE_JSON_WEB_KEY1['kid'],
            typ='JWT',
        )

        assert jwt.decode(
            client_secret,
            options=dict(verify_aud=False, verify_signature=False),
        ) == dict(
            aud=APPLE_TOKEN_ISSUER,
            exp=now.i() + int(datetime.timedelta(hours=1).total_seconds()),
            iat=now.i(),
            iss=apple_test.APPLE_TEAM_ID1,
            sub=str(EXTERNAL_APPLICATION_ID1),
        )

    def test_app_specific(self):
        app = self.build_app()
        app.apple_jwt_certificate_id = apple_test.APPLE_JSON_WEB_KEY2['kid']
        app.apple_team_id = apple_test.APPLE_TEAM_ID2

        proxy = get_proxy(Apple.code, self.build_token_dict(APPLICATION_TOKEN1), app)
        client_secret = proxy.get_client_secret()

        assert jwt.get_unverified_header(client_secret) == dict(
            alg='ES256',
            kid=apple_test.APPLE_JSON_WEB_KEY2['kid'],
            typ='JWT',
        )

        assert jwt.decode(
            client_secret,
            options=dict(verify_aud=False, verify_signature=False),
        ) == dict(
            aud=APPLE_TOKEN_ISSUER,
            exp=now.i() + int(datetime.timedelta(hours=1).total_seconds()),
            iat=now.i(),
            iss=apple_test.APPLE_TEAM_ID2,
            sub=str(EXTERNAL_APPLICATION_ID1),
        )
