# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    UID1,
    UID2,
    UNIXTIME1,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token

from .common import TestApiViewsCase


APPLICATIONS_CONF = [
    {
        'application_id': APPLICATION_ID1,
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'application_name': APPLICATION_NAME1,
    },
    {
        'application_id': APPLICATION_ID2,
        'provider_client_id': EXTERNAL_APPLICATION_ID2,
        'application_name': APPLICATION_NAME2,
    },
]


class BaseIsTokenAvailableTestCase(TestApiViewsCase):
    def setUp(self):
        super(BaseIsTokenAvailableTestCase, self).setUp()
        self.grants_config.add_consumer('dev', networks=['127.0.0.1'], grants=['token-read'])

    def build_settings(self):
        settings = super(BaseIsTokenAvailableTestCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def _make_request(self, query_string=None):
        query_string = build_dict_from_standard(
            standard=dict(
                uid=UID1,
                application_names=' '.join([APPLICATION_NAME1, APPLICATION_NAME2]),
            ),
            values=query_string or dict(),
        )
        return self.app_client.get('/api/token/available', query_string=query_string)

    def _build_token(self, uid=UID1, application_id=APPLICATION_ID1,
                     expired=None, token=APPLICATION_TOKEN1):
        return Token(
            uid=uid,
            profile_id=None,
            application_id=application_id,
            value=token,
            secret=None,
            scopes=None,
            expired=expired,
            created=datetime.fromtimestamp(UNIXTIME1),
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )


class TestIsTokenAvailableTokenNoTokens(BaseIsTokenAvailableTestCase):
    def test_no_uid(self):
        rv = self._make_request(query_string=dict(uid=None))
        self._assert_error_response(rv, 'uid-empty', status_code=400)

    def test_no_application_names(self):
        rv = self._make_request(query_string=dict(application_names=None))
        self._assert_error_response(rv, 'application_names-empty', status_code=400)

    def test_applications_names_empty(self):
        rv = self._make_request(query_string=dict(application_names=''))
        self._assert_ok_response(rv, [])


class TestIsTokenAvailableTokenTokenExpired(BaseIsTokenAvailableTestCase):
    def setUp(self):
        super(TestIsTokenAvailableTokenTokenExpired, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(self._build_token(expired=now() - timedelta(hours=1)), db)

    def test_ok(self):
        rv = self._make_request()
        self._assert_ok_response(rv, [])


class TestIsTokenAvailableTokenTokenNotExpired(BaseIsTokenAvailableTestCase):
    def setUp(self):
        super(TestIsTokenAvailableTokenTokenNotExpired, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(
                self._build_token(
                    uid=UID1,
                    application_id=APPLICATION_ID1,
                    token=APPLICATION_TOKEN1,
                    expired=now() - timedelta(hours=1),
                ),
                db,
            )
            save_token(
                self._build_token(
                    uid=UID1,
                    application_id=APPLICATION_ID2,
                    token=APPLICATION_TOKEN2,
                    expired=now() + timedelta(hours=1),
                ),
                db,
            )

    def test_application1(self):
        rv = self._make_request(query_string=dict(application_names=APPLICATION_NAME1))
        self._assert_ok_response(rv, [])

    def test_application2(self):
        rv = self._make_request(query_string=dict(application_names=APPLICATION_NAME2))
        self._assert_ok_response(rv, [dict(application_name=APPLICATION_NAME2)])

    def test_both_applications(self):
        rv = self._make_request(
            query_string=dict(
                application_names=' '.join([APPLICATION_NAME1, APPLICATION_NAME2]),
            ),
        )

        self._assert_ok_response(rv, [dict(application_name=APPLICATION_NAME2)])

    def test_unknown_application(self):
        rv = self._make_request(
            query_string=dict(
                application_names=' '.join([APPLICATION_NAME2, 'unknown']),
            ),
        )

        self._assert_ok_response(rv, [dict(application_name=APPLICATION_NAME2)])

    def test_different_uid(self):
        rv = self._make_request(
            query_string=dict(
                uid=UID2,
                application_names=APPLICATION_NAME2,
            ),
        )

        self._assert_ok_response(rv, [])


class TestIsTokenAvailableTokenManyTokens(BaseIsTokenAvailableTestCase):
    def setUp(self):
        super(TestIsTokenAvailableTokenManyTokens, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(
                self._build_token(
                    application_id=APPLICATION_ID1,
                    expired=None,
                ),
                db,
            )
            save_token(
                self._build_token(
                    application_id=APPLICATION_ID2,
                    expired=now() + timedelta(hours=1),
                ),
                db,
            )

    def test_ok(self):
        rv = self._make_request(
            query_string=dict(
                application_names=' '.join([APPLICATION_NAME1, APPLICATION_NAME2]),
            ),
        )

        self._assert_ok_response(
            rv,
            [
                dict(application_name=APPLICATION_NAME1),
                dict(application_name=APPLICATION_NAME2),
            ],
        )


class TestIsTokenAvailablePostRequest(BaseIsTokenAvailableTestCase):
    def setUp(self):
        super(TestIsTokenAvailablePostRequest, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(
                self._build_token(
                    uid=UID1,
                    application_id=APPLICATION_ID1,
                    token=APPLICATION_TOKEN1,
                    expired=now() + timedelta(hours=1),
                ),
                db,
            )

    def _make_request(self, data=None):
        data = build_dict_from_standard(
            standard=dict(uid=UID1),
            values=data or dict(),
        )
        return self.app_client.post('/api/token/available', data=data)

    def test(self):
        rv = self._make_request(data=dict(application_names=APPLICATION_NAME1))
        self._assert_ok_response(rv, [dict(application_name=APPLICATION_NAME1)])
