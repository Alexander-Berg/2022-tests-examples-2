# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.db.checkers import get_long_checker
from passport.backend.perimeter.auth_api.db.schemas import long_users_table
from passport.backend.perimeter.auth_api.test import BaseDbTestCase
from sqlalchemy.exc import OperationalError


class TestLongChecker(BaseDbTestCase):
    def setUp(self):
        super(TestLongChecker, self).setUp()
        self.insert_data(long_users_table, username='user1', password='pass1')
        self.insert_data(
            long_users_table,
            username='user2',
            password='pass2',
        )
        self.checker = get_long_checker()

    def test_enabled(self):
        assert self.checker.is_enabled

    def test_ok(self):
        check_result = self.checker.check(login='user1', password='pass1')
        assert check_result.is_ok
        assert check_result.description == 'Long auth successful'

    def test_ok_when_not_connected(self):
        self.db_connection.disconnect()
        check_result = self.checker.check(login='user1', password='pass1')
        assert check_result.is_ok
        assert check_result.description == 'Long auth successful'

    def test_unknown_login(self):
        check_result = self.checker.check(login='user3', password='pass')
        assert not check_result.is_ok
        assert check_result.description == 'Long user not found'

    def test_password_not_matched(self):
        check_result = self.checker.check(login='user1', password='pass2')
        assert not check_result.is_ok
        assert check_result.description == 'Long password not matched'

    def test_db_error(self):
        with mock.patch.object(
            self.db_connection,
            '_execute',
            mock.Mock(side_effect=OperationalError('', '', '')),
        ):
            check_result = self.checker.check(login='user1', password='pass1')
        assert not check_result.is_ok
        assert check_result.description == 'Long DB error'

    def test_db_error_when_not_connected(self):
        self.db_connection.disconnect()
        with mock.patch.object(
            self.db_connection._engine,
            'connect',
            mock.Mock(side_effect=OperationalError('', '', '')),
        ):
            check_result = self.checker.check(login='user1', password='pass1')
        assert not check_result.is_ok
        assert check_result.description == 'Long DB error'
