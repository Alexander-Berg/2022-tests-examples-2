# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.social.common.chrono import (
    datetime_to_unixtime,
    now,
)
from passport.backend.social.common.exception import NetworkProxylibError
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import save_refresh_token
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN_ID1,
    APPLICATION_TOKEN_ID2,
    APPLICATION_TOKEN_TTL1,
    PROFILE_ID1,
    UID1,
    UNIXTIME1,
)
from passport.backend.social.common.test.types import (
    ApproximateInteger,
    DatetimeNow,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
from passport.backend.social.proxylib.test import google as google_test

from .common import TestApiViewsCase


APPLICATIONS_CONF = [
    dict(
        provider_id=1,
        application_id=12,
        application_name='vkontakte-kinopoisk',
        provider_client_id='xxx',
        secret='xxx',
    ),
    dict(
        provider_id=5,
        application_id=52,
        application_name='google-oauth2',
        default='1',
        provider_client_id='yyy',
        secret='yyy',
    ),
]


class GetTokenTestCase(TestApiViewsCase):
    def setUp(self):
        super(GetTokenTestCase, self).setUp()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'token-read',
                'no-cred-read-token-application:google-oauth2',
                'no-cred-read-token-application:vkontakte-kinopoisk',
            ],
        )

    def build_settings(self):
        settings = super(GetTokenTestCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings


class TestGetTokenNotExpired(GetTokenTestCase):
    def setUp(self):
        super(TestGetTokenNotExpired, self).setUp()
        token = Token(
            uid=UID1,
            profile_id=PROFILE_ID1,
            application_id=12,
            value=APPLICATION_TOKEN1,
            secret='secret',
            scopes=['bar', 'foo'],
            expired=now() + timedelta(hours=1),
            created=datetime.fromtimestamp(UNIXTIME1),
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )
        with self._fake_db.no_recording():
            save_token(token, self._fake_db.get_engine())
        assert token.token_id == APPLICATION_TOKEN_ID1

    def test_no_token(self):
        rv = self.app_client.get('/api/token')
        self._assert_error_response(rv, 'token_id-empty', status_code=400)

    def test_in_query__not_found(self):
        rv = self.app_client.get('/api/token', query_string={'token_id': APPLICATION_TOKEN_ID2})
        self._assert_error_response(rv, 'token-not-found', status_code=404)

    def test_in_body__not_found(self):
        rv = self.app_client.get('/api/token', data={'token_id': APPLICATION_TOKEN_ID2})
        self._assert_error_response(rv, 'token-not-found', status_code=404)

    def test_found(self):
        rv = self.app_client.get('/api/token', query_string={'token_id': APPLICATION_TOKEN_ID1})
        self._assert_ok_response(
            rv,
            {
                'token': {
                    'token_id': APPLICATION_TOKEN_ID1,
                    'uid': UID1,
                    'profile_id': PROFILE_ID1,
                    'application': 'vkontakte-kinopoisk',
                    'value': APPLICATION_TOKEN1,
                    'secret': 'secret',
                    'scope': 'bar foo',
                    'expired': DatetimeNow(convert_to_datetime=True) + timedelta(hours=1),
                    'expired_ts': ApproximateInteger(datetime_to_unixtime(now() + timedelta(hours=1))),
                    'created': str(datetime.fromtimestamp(UNIXTIME1)),
                    'created_ts': UNIXTIME1,
                    'confirmed': str(datetime.fromtimestamp(UNIXTIME1)),
                    'confirmed_ts': UNIXTIME1,
                    'verified': str(datetime.fromtimestamp(UNIXTIME1)),
                    'verified_ts': UNIXTIME1,
                },
            },
        )


class TestGetTokenExpiredWithRefreshToken(GetTokenTestCase):
    def setUp(self):
        super(TestGetTokenExpiredWithRefreshToken, self).setUp()

        self._fake_google = google_test.FakeProxy()
        self._fake_google.start()

        token = Token(
            uid=UID1,
            profile_id=PROFILE_ID1,
            application_id=52,
            value=APPLICATION_TOKEN1,
            secret=None,
            scopes=['bar', 'foo'],
            expired=datetime.fromtimestamp(UNIXTIME1),
            created=datetime.fromtimestamp(UNIXTIME1),
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )
        refresh_token = RefreshToken(
            token_id=1,
            value=APPLICATION_TOKEN2,
            expired=None,
            scopes=['bar', 'foo'],
        )

        with self._fake_db.no_recording():
            save_token(token, self._fake_db.get_engine())
            save_refresh_token(refresh_token, self._fake_db.get_engine())

    def tearDown(self):
        self._fake_google.stop()
        super(TestGetTokenExpiredWithRefreshToken, self).tearDown()

    def test_refresh_token_invalid(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_invalid_grant_error(),
        )
        rv = self.app_client.get('/api/token', query_string={'token_id': '1'})
        self._assert_error_response(rv, 'token-not-found', status_code=404)

    def test_refresh_token_network_fail(self):
        self._fake_google.set_response_value('refresh_token', NetworkProxylibError())
        rv = self.app_client.get('/api/token', query_string={'token_id': '1'})
        self._assert_ok_response(
            rv,
            {
                'token': {
                    'token_id': 1,
                    'uid': UID1,
                    'profile_id': PROFILE_ID1,
                    'application': 'google-oauth2',
                    'value': APPLICATION_TOKEN1,
                    'secret': None,
                    'scope': 'bar foo',
                    'expired': str(datetime.fromtimestamp(UNIXTIME1)),
                    'expired_ts': UNIXTIME1,
                    'created': str(datetime.fromtimestamp(UNIXTIME1)),
                    'created_ts': UNIXTIME1,
                    'confirmed': str(datetime.fromtimestamp(UNIXTIME1)),
                    'confirmed_ts': UNIXTIME1,
                    'verified': str(datetime.fromtimestamp(UNIXTIME1)),
                    'verified_ts': UNIXTIME1,
                },
            },
        )

    def test_refresh_token_valid(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN3),
        )
        rv = self.app_client.get('/api/token', query_string={'token_id': '1'})
        self._assert_ok_response(
            rv,
            {
                'token': {
                    'token_id': 1,
                    'uid': UID1,
                    'profile_id': PROFILE_ID1,
                    'application': 'google-oauth2',
                    'value': APPLICATION_TOKEN3,
                    'secret': None,
                    'scope': 'bar foo',
                    'expired': DatetimeNow(convert_to_datetime=True) + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                    'expired_ts': ApproximateInteger(datetime_to_unixtime(now() + timedelta(seconds=APPLICATION_TOKEN_TTL1))),
                    'created': str(datetime.fromtimestamp(UNIXTIME1)),
                    'created_ts': UNIXTIME1,
                    'confirmed': str(datetime.fromtimestamp(UNIXTIME1)),
                    'confirmed_ts': UNIXTIME1,
                    'verified': str(datetime.fromtimestamp(UNIXTIME1)),
                    'verified_ts': UNIXTIME1,
                },
            },
        )
