# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.broker.communicators.communicator import AuthorizeOptions
from passport.backend.social.broker.communicators.DnevnikRuCommunicator import DnevnikRuCommunicator
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.oauth2.token import InvalidClient
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    CALLBACK_URL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.types import ApproximateInteger
from passport.backend.social.proxylib.test.dnevnik_ru import DnevnikRuApi


class _BaseTestDnevnikRu(TestCase):
    def setUp(self):
        super(_BaseTestDnevnikRu, self).setUp()
        app = Application(
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
            domain='social.yandex.net',
            request_from_intranet_allowed=True,
        )
        self._communicator = DnevnikRuCommunicator(app)

    def build_settings(self):
        settings = super(_BaseTestDnevnikRu, self).build_settings()
        settings['social_config']['dnevnik_ru_broker_redirect_uri'] = 'https://social.yandex.ru/broker/redirect'
        settings['social_config']['dnevnik_ru_oauth_authorize_url'] = 'https://api.dnevnik.ru/oauth2'
        settings['social_config']['dnevnik_ru_oauth_token_url'] = 'https://api.dnevnik.ru/v2.0/authorizations'
        return settings


class TestDnevnikRuCommunicatorParseAccessToken(_BaseTestDnevnikRu):
    def test_ok_response(self):
        self._fake_useragent.set_response_value(DnevnikRuApi.access_token())
        token = self._communicator.get_access_token(
            callback_url=CALLBACK_URL1,
            exchange='foo',
            scopes=None,
            request_token=None,
        )

        self.assertEqual(len(self._fake_useragent.requests), 1)
        request = self._fake_useragent.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url, 'https://api.dnevnik.ru/v2.0/authorizations')

        self.assertEqual(
            token,
            {
                'expires': ApproximateInteger(now.f() + APPLICATION_TOKEN_TTL1),
                'value': APPLICATION_TOKEN1,
                'scope': 'CommonInfo',
            },
        )

    def test_parse_error(self):
        self._fake_useragent.set_response_value(
            DnevnikRuApi.build_token_request_error(),
        )
        with self.assertRaises(InvalidClient):
            self._communicator.get_access_token(
                callback_url=CALLBACK_URL1,
                exchange='foo',
                scopes=None,
                request_token=None,
            )

        self.assertEqual(len(self._fake_useragent.requests), 1)
        request = self._fake_useragent.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url, 'https://api.dnevnik.ru/v2.0/authorizations')


class TestDnevnikRuCommunicatorGetAuthorizeRedirect(_BaseTestDnevnikRu):
    def test_force_prompt(self):
        redirect_url = self._communicator.get_authorize_url(AuthorizeOptions(
            'https://callback.me',
            force_prompt=True,
            client_id='client-id',
        ))
        assert 'prompt=login' in redirect_url
        redirect_url = self._communicator.get_authorize_url(AuthorizeOptions(
            'https://callback.me',
            force_prompt=False,
            client_id='client-id',
        ))
        assert 'prompt=login' not in redirect_url
