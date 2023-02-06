# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.db.checkers import get_totp_checker
from passport.backend.perimeter.auth_api.db.schemas import totp_users_table
from passport.backend.perimeter.auth_api.test import BaseDbTestCase
import pytest
from sqlalchemy.exc import OperationalError


class TestTotpChecker(BaseDbTestCase):
    def setUp(self):
        super(TestTotpChecker, self).setUp()
        self.insert_data(totp_users_table, username='login')
        self.checker = get_totp_checker()

    def test_is_enabled(self):
        assert self.checker.is_enabled

    def test_alias(self):
        assert self.checker.alias == 'TOTP'

    def test_check__error(self):
        with pytest.raises(NotImplementedError):
            self.checker.check(login='login', password='pass')

    def test_check_if_totp_is_on__ok(self):
        result = self.checker.check_if_totp_is_on('login')
        assert result.is_ok
        assert result.description == 'TOTP is enabled'

    def test_check_if_totp_is_on__totp_disabled(self):
        result = self.checker.check_if_totp_is_on('login2')
        assert not result.is_ok
        assert result.description == 'TOTP not enabled'

    def test_check_if_totp_is_on__db_error(self):
        with mock.patch.object(
            self.db_connection,
            '_execute',
            mock.Mock(side_effect=OperationalError('', '', '')),
        ):
            result = self.checker.check_if_totp_is_on('login')
        assert not result.is_ok
        assert result.description == 'TOTP DB error'
