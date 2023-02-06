# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.broker.communicators.communicator import AuthorizeOptions
from passport.backend.social.broker.communicators.YandexCommunicator import YandexCommunicator
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.test.consts import (
    CALLBACK_URL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.useragent import Url


class TestYandexCommunicatorGetAuthorizeRedirectUrl(TestCase):
    def setUp(self):
        super(TestYandexCommunicatorGetAuthorizeRedirectUrl, self).setUp()
        app = Application(
            domain='social.yandex.net',
            id=EXTERNAL_APPLICATION_ID1,
        )
        self.communicator = YandexCommunicator(app)

    def test_login_hint(self):
        authorize_url = self.communicator.get_authorize_url(AuthorizeOptions(callback_url=CALLBACK_URL1))
        authorize_url = Url(authorize_url)
        self.assertNotIn('login_hint', authorize_url.params)

        authorize_url = self.communicator.get_authorize_url(AuthorizeOptions(
            callback_url=CALLBACK_URL1,
            login_hint='foo',
        ))
        authorize_url = Url(authorize_url)
        self.assertEqual(authorize_url.params.get('login_hint'), 'foo')
