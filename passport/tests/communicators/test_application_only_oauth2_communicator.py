# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.broker.communicators.communicator import ApplicationOnlyOAuth2Communicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common import oauth2
from passport.backend.social.common.application import Application
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID1,
)


class TestParseAccessToken(TestCase):
    def build_app(self, identifier=APPLICATION_ID1):
        return Application(
            authorization_url='https://authorize/',
            domain='social.yandex.net',
            id=EXTERNAL_APPLICATION_ID1,
            identifier=identifier,
            request_from_intranet_allowed=True,
            token_url='https://token/',
        )

    def build_communicator(self):
        app = self.build_app()
        return ApplicationOnlyOAuth2Communicator(app, 'popup')

    def test(self):
        """
        Считаем отказ invalid_client от приложений Станции равносильным
        недействительному авторизационному коду.
        """
        communicator = self.build_communicator()
        response = oauth2.test.build_error('invalid_client')

        with self.assertRaises(CommunicationFailedError):
            communicator.parse_access_token(response.value)
