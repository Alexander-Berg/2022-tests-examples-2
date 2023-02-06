# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import datetime

import cryptography.hazmat.primitives.serialization
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker import exceptions
from passport.backend.social.broker.communicators.communicator import (
    AuthorizeOptions,
    Oauth2State,
)
from passport.backend.social.broker.communicators.EsiaCommunicator import EsiaCommunicator
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common import (
    crypto,
    oauth2,
)
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.context import request_ctx
from passport.backend.social.common.misc import split_scope_string
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Esia import Esia
from passport.backend.social.common.task import Task
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN_TTL1,
    AUTHORIZATION_CODE1,
    CALLBACK_URL1,
    EXTERNAL_APPLICATION_ID1,
    UNIXTIME1,
)
from passport.backend.social.common.test.fake_useragent import FakeRequest
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.useragent import Url
from passport.backend.social.proxylib.EsiaProxy import (
    EsiaPermissions,
    EsiaRefreshToken,
    EsiaToken,
)
from passport.backend.social.proxylib.test import esia as esia_test


# Чтобы сгенерить закрытый ключ нужно выполнить
# openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:512
RSA_512_PRIVATE_KEY = b'''
-----BEGIN PRIVATE KEY-----
MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAwxL1e9i74LR+V+iE
HJskBOoTjU3Zrwjitdb8F2YleCbsOmxh7Dd0RsbU8KImEm4Y8MFSM9cOpczCo+zz
YZ1qgQIDAQABAkBM8yGa5PfXv9tG2hWjIx+mQJ/N0bPY8+xaRp/SqxyEtETCJUB7
fsQOlnZJSL50yfArqpjnNYRr6/wr0+lpjeCxAiEA9iUft/1Jr8LwXIKxGgiPHXM5
Cqg2uzvTosUfd3611JMCIQDK4mFu3gXQvbkIDuMRNlloXNOcupRyS6raojzvN2Zl
GwIgXK21t60i5Y7cubhrvoWifVA5Fg4oLW9lTFA0fOW0yQkCICr7IqEWMC00xEpM
vRYcaXyOjdYaQPClzyBaVoZnOi4ZAiEAtJdKoAFUnMXiZGkPVKycP6U4rai32dXD
t5cQqnHKSHQ=
-----END PRIVATE KEY-----
'''


# Выписать можно так
# openssl req -newkey gost2012_256 -pkeyopt paramset:XA -x509 -out my.crt -keyout my.key -days 3650 -nodes
GOST3410_2012_256_PRIVATE_KEY = b'''
-----BEGIN PRIVATE KEY-----
MEYCAQAwHwYIKoUDBwEBAQEwEwYHKoUDAgIkAAYIKoUDBwEBAgIEIFxxXfLvf2EG
xNY52Jjp3Yf7rF+TH4t4EULUr7qjoNUn
-----END PRIVATE KEY-----
'''


class BaseEsiaCommunicatorTestCase(TestCase):
    def build_settings(self):
        settings = super(BaseEsiaCommunicatorTestCase, self).build_settings()
        settings['providers'] = [
            {
                'id': Esia.id,
                'code': Esia.code,
                'name': 'esia',
            },
        ]
        settings['social_config'].update(
            esia_authorize_url='https://esia-portal1.test.gosuslugi.ru/aas/oauth2/ac',
            esia_jwt_certificate=esia_test.ESIA_YANDEX_CERTIFICATE,
            esia_real_host='esia-portal1.test.gosuslugi.ru',
            esia_token_url='https://esia-portal1.test.gosuslugi.ru/aas/oauth2/te',
            esia_verify_id_token_signature=True,
            esia_yandex_certificate=esia_test.ESIA_YANDEX_CERTIFICATE,
            esia_yandex_private_key=esia_test.ESIA_YANDEX_PRIVATE_KEY,
            esia_yandex_private_key_password=None,
        )
        return settings

    def build_app(self, identifier=APPLICATION_ID1):
        return Application(
            domain='social.yandex.net',
            identifier=identifier,
            id=EXTERNAL_APPLICATION_ID1,
            provider=providers.get_provider_info_by_name(Esia.code),
            request_from_intranet_allowed=True,
        )

    def build_communicator(self, app=None):
        if app is None:
            app = self.build_app()
        return EsiaCommunicator(app)


class TestGetAuthorizeRedirectUrl(BaseEsiaCommunicatorTestCase):
    def test(self):
        comm = self.build_communicator()

        self.fake_chrono.set_timestamp(UNIXTIME1)

        authorization_url = Url(comm.get_authorize_url(AuthorizeOptions(
            CALLBACK_URL1,
            scope='openid foo',
        )))

        client_secret = authorization_url.params.get('client_secret', '')
        authorization_url.remove_params(['client_secret'])

        permissions = authorization_url.params.get('permissions', '')
        authorization_url.remove_params(['permissions'])

        check_url_equals(
            str(authorization_url),
            str(
                Url(
                    'https://esia-portal1.test.gosuslugi.ru/aas/oauth2/ac',
                    params=dict(
                        access_type='offline',
                        client_id=EXTERNAL_APPLICATION_ID1,
                        redirect_uri='https://social.yandex.net/broker/redirect',
                        response_type='code',
                        scope='openid',
                        state=str(Oauth2State.find_by_url(CALLBACK_URL1)),
                        timestamp=esia_test.EsiaApi.esia_datetime_format(datetime.datetime.fromtimestamp(UNIXTIME1)),
                    ),
                ),
            ),
        )

        esia_test.EsiaApi.assert_ok_esia_signature(authorization_url.params, client_secret)
        esia_test.EsiaApi.assert_ok_esia_permissions(dict(scope='openid foo'), EsiaPermissions.from_str(permissions))


class TestGetAccessToken(BaseEsiaCommunicatorTestCase):
    def test_ok(self):
        self.fake_chrono.set_timestamp(UNIXTIME1)

        task = request_ctx.task = Task()
        task.callback_url = CALLBACK_URL1
        task.scope = 'foo openid poo'

        state = Oauth2State.find_by_url(task.callback_url)

        self._fake_useragent.set_response_value(
            oauth2.test.oauth2_access_token_response(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
                extra=dict(
                    id_token=APPLICATION_TOKEN3,
                    state=str(state),
                ),
                refresh_token=APPLICATION_TOKEN2,
            ),
        )

        comm = self.build_communicator()

        token = comm.get_access_token(
            callback_url=task.callback_url,
            exchange=AUTHORIZATION_CODE1,
            request_token=None,
            scopes=split_scope_string(task.scope),
        )

        assert token == dict(
            expires=UNIXTIME1 + APPLICATION_TOKEN_TTL1,
            id_token=APPLICATION_TOKEN3,
            refresh=EsiaRefreshToken(
                id_token=APPLICATION_TOKEN3,
                scope=task.scope,
                state=str(state),
                value=APPLICATION_TOKEN2,
                version=1,
            ).serialize(),
            scope=task.scope,
            value=EsiaToken(
                access_token=APPLICATION_TOKEN1,
                id_token=APPLICATION_TOKEN3,
                scope=task.scope,
                version=1,
            ).serialize(),
        )

        assert len(self._fake_useragent.requests) == 1

        client_secret = self._fake_useragent.requests[0].data.pop('client_secret', '')

        self.assertEqual(
            self._fake_useragent.requests[0],
            FakeRequest(
                data=dict(
                    client_id=EXTERNAL_APPLICATION_ID1,
                    code=AUTHORIZATION_CODE1,
                    grant_type='authorization_code',
                    redirect_uri='https://social.yandex.net/broker/redirect',
                    scope='openid',
                    state=str(state),
                    timestamp=esia_test.EsiaApi.esia_datetime_format(datetime.datetime.fromtimestamp(UNIXTIME1)),
                ),
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'yandex-social-useragent/0.1',
                },
                method='POST',
                url='https://esia-portal1.test.gosuslugi.ru/aas/oauth2/te',
            ),
        )

        esia_test.EsiaApi.assert_ok_esia_signature(self._fake_useragent.requests[0].data, client_secret)

    def test_invalid_authorization_code(self):
        task = request_ctx.task = Task()
        task.callback_url = CALLBACK_URL1
        task.scope = 'foo'

        self._fake_useragent.set_response_value(oauth2.test.build_error('invalid_grant'))

        comm = self.build_communicator()

        with self.assertRaises(exceptions.CommunicationFailedError):
            comm.get_access_token(
                callback_url=task.callback_url,
                exchange=AUTHORIZATION_CODE1,
                request_token=None,
                scopes=task.scope,
            )


class TestSanitizeServerToken(BaseEsiaCommunicatorTestCase):
    def test_ok(self):
        self.check(esia_test.EsiaApi.build_id_token())

    def test_header_corrupted(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check('invalid')

    def test_invalid_aud(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check(esia_test.EsiaApi.build_id_token(dict(aud='invalid')))

    def test_old_exp(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            day = datetime.timedelta(days=1)
            self.check(esia_test.EsiaApi.build_id_token(dict(exp=now.f() - day.total_seconds())))

    def test_invalid_iss(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check(esia_test.EsiaApi.build_id_token(dict(iss='invalid')))

    def test_future_nbf(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            day = datetime.timedelta(days=1)
            self.check(esia_test.EsiaApi.build_id_token(dict(nbf=now.f() + day.total_seconds())))

    def test_future_nbf_small_error(self):
        self.check(esia_test.EsiaApi.build_id_token(dict(nbf=now.f() + 13)))

    def test_invalid_sbt(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check(esia_test.EsiaApi.build_id_token(headers=dict(sbt='invalid')))

    def test_invalid_signature(self):
        other_private_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
            GOST3410_2012_256_PRIVATE_KEY,
            None,
            crypto.get_social_cryptography_backend(),
        )
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check(esia_test.EsiaApi.build_id_token(private_key=other_private_key))

    def test_unexpected_signature_algorithm(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            self.check(esia_test.EsiaApi.build_id_token(private_key=RSA_512_PRIVATE_KEY, algorithm='RS256'))

    def test_invalid_subject_type(self):
        with self.assertRaises(exceptions.CommunicationFailedError):
            id_token = copy.deepcopy(esia_test.EsiaApi.default_id_token)
            id_token.get('urn:esia:sbj', dict()).update({'urn:esia:sbj:typ': 'Z'})
            self.check(esia_test.EsiaApi.build_id_token(id_token))

    def check(self, id_token):
        comm = self.build_communicator()
        esia_token = EsiaToken(
            access_token=APPLICATION_TOKEN1,
            id_token=id_token,
            scope='foo',
            version=1,
        )

        token_dict = comm.sanitize_server_token(
            server_token=Token(
                scopes=split_scope_string(esia_token.scope),
                value=esia_token.serialize(),
            ),
            refresh_token=None,
        )

        assert token_dict == dict(
            application=None,
            expires=None,
            scope=esia_token.scope,
            secret=None,
            token_id=None,
            value=esia_token.serialize(),
        )
