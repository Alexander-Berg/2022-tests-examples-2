# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import json

from passport.backend.social.broker.communicators.MeethueCommunicator import MeethueCommunicator
from passport.backend.social.broker.exceptions import (
    CommunicationFailedError,
    UserDeniedError,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    APPLICATION_TOKEN_TTL2,
    AUTHORIZATION_CODE1,
    CALLBACK_URL1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.test.types import (
    ApproximateInteger,
    FakeResponse,
)


class TestMeethueCommunicator(TestCase):
    def setUp(self):
        super(TestMeethueCommunicator, self).setUp()
        self.app = Application(
            domain='social.yandex.ru',
            request_from_intranet_allowed=True,
        )
        self.app.id = EXTERNAL_APPLICATION_ID1
        self.app.secret = APPLICATION_SECRET1
        self._communicator = MeethueCommunicator(self.app)

    def test_has_error_in_callback(self):
        query = dict(
            state='ololo',
            redirect_uri='http://localhost',
        )
        with self.assertRaises(UserDeniedError):
            self._communicator.has_error_in_callback(query)

    def test_get_access_token_request(self):
        self.assertTupleEqual(
            self._communicator.get_access_token_request(code='test_code'),
            (
                'https://api.meethue.com/oauth2/token',
                {
                    u'redirect_uri': u'https://social.yandex.ru/broker/redirect',
                    u'code': 'test_code',
                    u'grant_type': u'authorization_code',
                },
                {
                    u'Content-Type': u'application/x-www-form-urlencoded',
                    u'Authorization': 'Basic %s' % (
                        base64.b64encode(EXTERNAL_APPLICATION_ID1 + ':' + APPLICATION_SECRET1)
                    ),
                },
            ),
        )

    def test_get_access_token(self):
        response = {
            "access_token": APPLICATION_TOKEN1,
            "access_token_expires_in": str(APPLICATION_TOKEN_TTL1),
            "refresh_token": APPLICATION_TOKEN2,
            "refresh_token_expires_in": str(APPLICATION_TOKEN_TTL2),
            "token_type": "BearerToken"
        }
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(response), 200),
        )

        self.assertDictEqual(
            self._communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=None,
            ),
            {
                u'expires': ApproximateInteger(now.f() + APPLICATION_TOKEN_TTL1),
                u'value': APPLICATION_TOKEN1,
                u'refresh': APPLICATION_TOKEN2,
                u'scope': None,
            },
        )

    def test_invalid_response(self):
        self._fake_useragent.set_response_value(
            FakeResponse('Invalid json document', 200),
        )
        with self.assertRaises(CommunicationFailedError):
            self._communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=None,
            )

    def test_invalid_autorization_code(self):
        response = {
            "fault": {
                "detail": {
                    "errorcode": "invalid_request"
                },
                "faultstring": "invalid_request"
            }
        }
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(response), 500),
        )
        with self.assertRaises(CommunicationFailedError):
            self._communicator.get_access_token(
                AUTHORIZATION_CODE1,
                CALLBACK_URL1,
                scopes=None,
                request_token=None,
            )
