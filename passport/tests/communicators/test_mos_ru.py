# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from passport.backend.social.broker.communicators.communicator import AuthorizeOptions
from passport.backend.social.broker.communicators.MosRuCommunicator import MosRuCommunicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application


class TestMosRuCommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestMosRuCommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = MosRuCommunicator(app)

    def test_invalid_client(self):
        # Mos.ru отвечает invalid_client, когда мы пытаемся обменять
        # недействительный авторизационный код на токен.
        response = {'error': 'invalid_client'}
        response = json.dumps(response)
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(response)


class TestMosRuCommunicatorGetAuthorizeRedirect(TestCase):
    def setUp(self):
        super(TestMosRuCommunicatorGetAuthorizeRedirect, self).setUp()
        app = Application()
        self._communicator = MosRuCommunicator(app)

    def build_settings(self):
        settings = super(TestMosRuCommunicatorGetAuthorizeRedirect, self).build_settings()
        settings['social_config']['mos_ru_broker_redirect_uri'] = 'https://social.yandex.ru/broker/redirect'
        settings['social_config']['mos_ru_oauth_authorize_url'] = 'https://mos.ru/auth/authorize'
        return settings

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


class TestMosRuCommunicatorGetScope(TestCase):
    def setUp(self):
        super(TestMosRuCommunicatorGetScope, self).setUp()
        app = Application()
        self._communicator = MosRuCommunicator(app)

    def test_minimal_scope(self):
        assert self._communicator.get_scope(list()) == 'openid profile'

    def test_user_scope(self):
        assert self._communicator.get_scope(['zoo', 'foo']) == 'openid foo profile zoo'
