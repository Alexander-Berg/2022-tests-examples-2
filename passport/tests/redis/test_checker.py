# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.redis.checker import RedisChecker
from passport.backend.perimeter.auth_api.test import BaseTestCase
from passport.backend.perimeter.auth_api.utils.hash import hash_string


class TestChecker(BaseTestCase):
    def setUp(self):
        self.checker = RedisChecker()

        self.redis_get_mock = mock.Mock(return_value={'password_hash': hash_string('pass')})
        self.redis_set_mock = mock.Mock(return_value=None)
        redis_mock = mock.Mock()
        redis_mock.get = self.redis_get_mock
        redis_mock.set = self.redis_set_mock
        self.checker._storage = redis_mock

    def test_is_enabled(self):
        assert self.checker.is_enabled

    def test_alias(self):
        assert self.checker.alias == 'Redis'

    def test_check__ok(self):
        assert self.checker.check('login', 'pass', '8.8.8.8', 'web').is_ok

    def test_check__not_found(self):
        self.redis_get_mock.return_value = None
        result = self.checker.check('login', 'pass', '8.8.8.8', 'web')
        assert not result.is_ok
        assert result.description is None

    def test_check__password_not_matched(self):
        self.redis_get_mock.return_value = {'password_hash': hash_string('pass2')}
        result = self.checker.check('login', 'pass', '8.8.8.8', 'web')
        assert not result.is_ok
        assert result.description is None
