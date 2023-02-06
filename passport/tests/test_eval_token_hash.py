# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.db.execute import execute
from passport.backend.social.common.db.schemas import token_table
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    EXTERNAL_APPLICATION_ID1,
    UID1,
)
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.token.db import TokenRecord
from passport.backend.social.common.token.domain import Token
from passport.backend.social.utils.init import init
from passport.backend.social.utils.one_time_job import eval_token_hash
from sqlalchemy import sql


class EvalTokenHashTestCase(TestCase):
    def setUp(self):
        super(EvalTokenHashTestCase, self).setUp()
        self._fake_redis = FakeRedisClient()
        self._redis_patch = RedisPatch(self._fake_redis).start()
        init()

        self.tokens = [
            Token(
                uid=UID1,
                application_id=APPLICATION_ID1,
                value=APPLICATION_TOKEN1,
            ),
            Token(
                uid=UID1,
                application_id=APPLICATION_ID1,
                value=APPLICATION_TOKEN2,
            ),
        ]
        self.tokens = [TokenRecord.from_model(t) for t in self.tokens]
        self.tokens[1].value_hash = 'missing'
        for token in self.tokens:
            token.save(self._fake_db.get_engine())

    def build_settings(self):
        settings = super(EvalTokenHashTestCase, self).build_settings()
        settings['applications'] = [
            dict(
                application_id=APPLICATION_ID1,
                application_name=APPLICATION_NAME1,
                provider_client_id=EXTERNAL_APPLICATION_ID1,
                domain='social.yandex.net',
            ),
        ]
        return settings

    def tearDown(self):
        self._redis_patch.stop()
        super(EvalTokenHashTestCase, self).tearDown()

    def assert_value_hash_missing(self, token_idx):
        assert self.get_token(token_idx).value_hash == 'missing'

    def assert_value_hash_ok(self, token_idx):
        token = self.get_token(token_idx)
        assert token.value_hash == TokenRecord.eval_value_hash(token.value)

    def get_token(self, token_idx):
        return execute(
            self._fake_db.get_engine(),
            token_table.select()
            .where(
                sql.and_(
                    token_table.c.token_id == self.tokens[token_idx].token_id,
                ),
            ),
        ).fetchone()


class TestEvalTokenHash(EvalTokenHashTestCase):
    def test_setup(self):
        self.assert_value_hash_ok(0)
        self.assert_value_hash_missing(1)

    def test_hashed_already(self):
        eval_token_hash(self.tokens[0].token_id)

        self.assert_value_hash_ok(0)
        self.assert_value_hash_missing(1)

    def test_invalid_hash(self):
        eval_token_hash(self.tokens[1].token_id)

        self.assert_value_hash_ok(0)
        self.assert_value_hash_ok(1)

    def test_not_found(self):
        eval_token_hash(3232)

        self.assert_value_hash_ok(0)
        self.assert_value_hash_missing(1)
