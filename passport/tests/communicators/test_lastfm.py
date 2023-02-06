# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker.communicators.communicator import AuthorizeOptions
from passport.backend.social.broker.communicators.LastFmCommunicator import LastFmCommunicator
from passport.backend.social.broker.exceptions import CommunicationFailedError
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    AUTHORIZATION_CODE1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    RETPATH1,
)
from passport.backend.social.common.useragent import Url


class TestLastFmCommunicatorParseAccessToken(TestCase):
    def setUp(self):
        super(TestLastFmCommunicatorParseAccessToken, self).setUp()
        app = Application()
        self._communicator = LastFmCommunicator(app)

    def test_ok(self):
        response = {
            'session': {
                'name': 'andrey1931',
                'key': APPLICATION_TOKEN1,
                'subscriber': 0,
            },
        }
        token = self._communicator.parse_access_token(json.dumps(response))

        self.assertEqual(token, {'value': APPLICATION_TOKEN1, 'expires': None})

    def test_no_session(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(json.dumps({}))

    def test_no_session_key(self):
        response = {
            'session': {
                'name': 'andrey1931',
                'subscriber': 0,
            },
        }
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(json.dumps(response))

    def test_invalid_authorization_code(self):
        response = {
            'error': 4,
            'message': 'Unauthorized Token - This token has not been issued',
        }
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(json.dumps(response))

    def test_unknown_error(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token(json.dumps({'error': 12431551}))

    def test_not_json_document(self):
        with self.assertRaises(CommunicationFailedError):
            self._communicator.parse_access_token('')


class TestLastFmCommunicatorGetAuthorizeRedirectUrl(TestCase):
    def setUp(self):
        super(TestLastFmCommunicatorGetAuthorizeRedirectUrl, self).setUp()
        app = Application(
            id=EXTERNAL_APPLICATION_ID1,
            domain='social.yandex.net',
        )
        self._communicator = LastFmCommunicator(app)

    def _build_authorize_url(self, callback_url, client_id=EXTERNAL_APPLICATION_ID1):
        return str(
            Url(
                url='https://www.last.fm/api/auth',
                params={
                    'api_key': client_id,
                    'cb': str(
                        Url(
                            url='https://social.yandex.net/broker/redirect',
                            params={'url': callback_url},
                        ),
                    ),
                },
            ),
        )

    def test_callback_url(self):
        check_url_equals(
            self._communicator.get_authorize_url(AuthorizeOptions(callback_url=RETPATH1)),
            self._build_authorize_url(callback_url=RETPATH1),
        )

    def test_client_id(self):
        check_url_equals(
            self._communicator.get_authorize_url(AuthorizeOptions(
                callback_url=RETPATH1,
                client_id=EXTERNAL_APPLICATION_ID2,
            )),
            self._build_authorize_url(
                callback_url=RETPATH1,
                client_id=EXTERNAL_APPLICATION_ID2,
            ),
        )


class TestLastFmCommunicatorGetAccessTokenUrl(TestCase):
    def setUp(self):
        super(TestLastFmCommunicatorGetAccessTokenUrl, self).setUp()
        app = Application(
            id=EXTERNAL_APPLICATION_ID1,
            secret=APPLICATION_SECRET1,
        )
        self._communicator = LastFmCommunicator(app)

    def _build_access_token_url(self, signature, verifier=AUTHORIZATION_CODE1,
                                client_id=EXTERNAL_APPLICATION_ID1):
        return str(
            Url(
                url='https://ws.audioscrobbler.com/2.0',
                params={
                    'method': 'auth.getSession',
                    'format': 'json',
                    'api_sig': signature,
                    'token': verifier,
                    'api_key': client_id,
                },
            ),
        )

    def _build_kwargs(self, **kwargs):
        kwargs.setdefault('code', AUTHORIZATION_CODE1)
        return kwargs

    def test_code(self):
        url, data, headers = self._communicator.get_access_token_request(
            **self._build_kwargs(
                code=AUTHORIZATION_CODE1,
            )
        )

        check_url_equals(
            url,
            self._build_access_token_url(
                verifier=AUTHORIZATION_CODE1,
                signature='63fd3f223aa6f75e4d6372e312642d50',
            ),
        )
        self.assertIsNone(data)
        self.assertIsNone(headers)

    def test_client_id(self):
        url, data, headers = self._communicator.get_access_token_request(
            **self._build_kwargs(
                client_id=EXTERNAL_APPLICATION_ID2,
            )
        )

        check_url_equals(
            url,
            self._build_access_token_url(
                client_id=EXTERNAL_APPLICATION_ID2,
                signature='7382b171d7aefe42592b7ff1a2fbc5d5',
            ),
        )
        self.assertIsNone(data)
        self.assertIsNone(headers)

    def test_location(self):
        url, data, headers = self._communicator.get_access_token_request(
            **self._build_kwargs(
                callback_url=RETPATH1,
            )
        )

        check_url_equals(
            url,
            self._build_access_token_url(
                # Location не указывается в access_token_url, поэтому не
                # учитывается в подписи.
                signature='63fd3f223aa6f75e4d6372e312642d50',
            ),
        )
        self.assertIsNone(data)
        self.assertIsNone(headers)
