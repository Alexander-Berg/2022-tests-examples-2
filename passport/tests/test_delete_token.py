# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from nose.tools import eq_
from passport.backend.social.common.application import application_eav_configuration
from passport.backend.social.common.db.schemas import (
    refresh_token_table,
    token_table,
)
from passport.backend.social.common.eav import EavSelector
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    PROFILE_ID1,
    UID1,
    UNIXTIME1,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
import sqlalchemy.sql as sql

from .common import TestApiViewsCase


APPLICATIONS_CONF = [
    dict(
        provider_id=1,
        application_id=12,
        application_name='vkontakte-kinopoisk',
        provider_client_id='xxx',
        secret='xxx',
    ),
]


class DeleteTokenTestCase(TestApiViewsCase):
    def setUp(self):
        super(DeleteTokenTestCase, self).setUp()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=['token-delete', 'no-cred-update-token-application:vkontakte-kinopoisk'],
        )

    def build_settings(self):
        settings = super(DeleteTokenTestCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings


class TestDeleteToken(DeleteTokenTestCase):
    def setUp(self):
        super(TestDeleteToken, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(
                Token(
                    uid=UID1,
                    profile_id=PROFILE_ID1,
                    application_id=12,
                    value=APPLICATION_TOKEN1,
                    secret=None,
                    scopes=None,
                    expired=None,
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                db,
            )

    def test_no_token_id(self):
        rv = self.app_client.delete('/api/token')
        self._assert_error_response(rv, 'token_id-empty', status_code=400)

    def test_token_id__in_query(self):
        rv = self.app_client.delete('/api/token', query_string={'token_id': '16'})
        self._assert_error_response(rv, 'token-not-found', status_code=404)

        self._fake_db.assert_executed_queries_equal([
            token_table.select().where(sql.and_(token_table.c.token_id == 16)),
        ])

    def test_token_id__in_post(self):
        rv = self.app_client.delete('/api/token', data={'token_id': '16'})
        self._assert_error_response(rv, 'token-not-found', status_code=404)

        self._fake_db.assert_executed_queries_equal([
            token_table.select().where(sql.and_(token_table.c.token_id == 16)),
        ])

    def test_token_id__letters(self):
        rv = self.app_client.delete('/api/token', query_string={'token_id': 'hello'})
        self._assert_error_response(rv, 'token_id-invalid', status_code=400)

    def test_token_exists(self):
        rv = self.app_client.delete('/api/token', query_string={'token_id': '1'})

        eq_(rv.status_code, 200)
        eq_(rv.data, '')

        self._fake_db.assert_executed_queries_equal([
            token_table.select().where(token_table.c.token_id == 1),
            EavSelector(application_eav_configuration, ['application_id']).index_query([12]),
            EavSelector(application_eav_configuration, ['application_id']).attrs_query([12]),
            refresh_token_table.delete().where(refresh_token_table.c.token_id.in_([1])),
            token_table.delete().where(token_table.c.token_id.in_([1])),
        ])


class TestDeleteTokenUnknownApplication(DeleteTokenTestCase):
    def setUp(self):
        super(TestDeleteTokenUnknownApplication, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(
                Token(
                    uid=UID1,
                    profile_id=PROFILE_ID1,
                    application_id=100500,
                    value=APPLICATION_TOKEN1,
                    secret=None,
                    scopes=None,
                    expired=None,
                    created=datetime.fromtimestamp(UNIXTIME1),
                    verified=datetime.fromtimestamp(UNIXTIME1),
                    confirmed=datetime.fromtimestamp(UNIXTIME1),
                ),
                db,
            )

    def test_ok(self):
        rv = self.app_client.delete('/api/token', query_string={'token_id': '1'})
        self._assert_error_response(rv, 'token-not-found', status_code=404)
