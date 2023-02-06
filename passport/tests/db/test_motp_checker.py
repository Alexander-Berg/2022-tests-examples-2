# -*- coding: utf-8 -*-
import hashlib

import mock
from passport.backend.perimeter.auth_api.db.checkers import get_motp_checker
from passport.backend.perimeter.auth_api.db.schemas import motp_users_table
from passport.backend.perimeter.auth_api.test import BaseDbTestCase
from sqlalchemy.exc import OperationalError


TEST_TIME = 142


class TestMOTPChecker(BaseDbTestCase):
    def setUp(self):
        super(TestMOTPChecker, self).setUp()
        self.insert_data(motp_users_table, username='user1', initsecret='secret1', pin=123)
        self.insert_data(
            motp_users_table,
            username='user2',
            initsecret='secret2',
            pin=321,
        )
        self.checker = get_motp_checker()

        self.time_mock = mock.Mock(return_value=TEST_TIME)
        self.time_patch = mock.patch('time.time', self.time_mock)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        super(TestMOTPChecker, self).tearDown()

    def _make_otp(self, secret, pin, time=TEST_TIME):
        hasher = hashlib.md5()
        hasher.update(b'%d%s%s' % (int(time / 10), secret.encode(), str(pin).encode()))
        return hasher.hexdigest()[0:6]

    def test_enabled(self):
        assert self.checker.is_enabled

    def test_ok(self):
        check_result = self.checker.check(login='user1', password=self._make_otp(secret='secret1', pin=123))
        assert check_result.is_ok
        assert check_result.description == 'MOTP auth successful'

    def test_ok_when_not_connected(self):
        self.db_connection.disconnect()
        check_result = self.checker.check(login='user1', password=self._make_otp(secret='secret1', pin=123))
        assert check_result.is_ok
        assert check_result.description == 'MOTP auth successful'

    def test_unknown_login(self):
        check_result = self.checker.check(login='user3', password='pass')
        assert not check_result.is_ok
        assert check_result.description == 'MOTP user not found'

    def test_password_not_matched(self):
        check_result = self.checker.check(login='user1', password=self._make_otp(secret='secret1', pin=123, time=9999))
        assert not check_result.is_ok
        assert check_result.description == 'MOTP password not matched'

    def test_db_error(self):
        with mock.patch.object(
            self.db_connection,
            '_execute',
            mock.Mock(side_effect=OperationalError('', '', '')),
        ):
            check_result = self.checker.check(login='user1', password='pass')
        assert not check_result.is_ok
        assert check_result.description == 'MOTP DB error'

    def test_db_error_when_not_connected(self):
        self.db_connection.disconnect()
        with mock.patch.object(
            self.db_connection._engine,
            'connect',
            mock.Mock(side_effect=OperationalError('', '', '')),
        ):
            check_result = self.checker.check(login='user1', password='pass')
        assert not check_result.is_ok
        assert check_result.description == 'MOTP DB error'
