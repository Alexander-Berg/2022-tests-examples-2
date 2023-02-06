# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from passport.backend.social.broker.communicators.AmediatekaCommunicator import AmediatekaCommunicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.test.consts import (
    AUTHORIZATION_CODE1,
    CALLBACK_URL1,
)
from passport.backend.social.common.test.types import FakeResponse


class TestAmediatekaCommunicator(TestCase):
    def setUp(self):
        super(TestAmediatekaCommunicator, self).setUp()
        app = Application(
            domain='social.yandex.ru',
            request_from_intranet_allowed=True,
        )
        self._communicator = AmediatekaCommunicator(app)

    def test_invalid_autorization_code(self):
        response = {
            'id': 'invalid_or_expired_code',
            'message': 'Код неверен либо истёк',
            'meta': {'status': '400'},
            'object': 'external_amediateka_error',
        }
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(response), 200),
        )
        with self.assertRaises(CommunicationFailedError):
            self._communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=None,
            )

    def test_unknown_response_type(self):
        response = {'id': 'unknown'}
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(response), 200),
        )
        with self.assertRaises(CommunicationFailedError):
            self._communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=None,
            )
