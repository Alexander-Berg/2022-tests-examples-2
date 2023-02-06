# -*- coding: utf-8 -*-
import ldap
import mock
from passport.backend.perimeter.auth_api.ldap.checker import LdapChecker
from passport.backend.perimeter.auth_api.test import BaseTestCase
import pytest


TEST_DN = 'CN=Cool User,CN=Users,DC=tst,DC=virtual'
TEST_ROBOT_DN = 'CN=Cool Robot,OU=TechUsers,DC=tst,DC=virtual'


class TestCheckerBalancer(BaseTestCase):
    def setUp(self):
        self.checker = LdapChecker()

        self.get_best_server_mock = mock.Mock(return_value='best_server')
        self.get_random_server_mock = mock.Mock(return_value='random_server')
        self.report_time_mock = mock.Mock(return_value=None)
        self.checker._balancer = mock.Mock()
        self.checker._balancer.get_best_server = self.get_best_server_mock
        self.checker._balancer.get_random_server = self.get_random_server_mock
        self.checker._balancer.report_time = self.report_time_mock

    def test_get_best__ok(self):
        ld = self.checker._get_connection()
        assert ld
        assert ld._uri == 'ldap://best_server:389'

    def test_get_random__ok(self):
        ld = self.checker._get_connection(use_best_server=False)
        assert ld
        assert ld._uri == 'ldap://random_server:389'

    def test_get_best__no_servers_available(self):
        self.get_best_server_mock.return_value = None
        ld = self.checker._get_connection()
        assert ld is None

    def test_report_time__ok(self):
        self.checker._report_time('best_server', 100500)
        assert self.report_time_mock.called


class TestChecker(BaseTestCase):
    def setUp(self):
        self.checker = LdapChecker()

        self.bind_mock = mock.Mock(return_value=None)
        self.search_mock = mock.Mock(return_value=[(TEST_DN, {})])
        ldap_mock = mock.Mock()
        ldap_mock.simple_bind_s = self.bind_mock
        ldap_mock.search_s = self.search_mock
        self.get_connection_mock = mock.Mock(return_value=ldap_mock)
        self.checker._get_connection = self.get_connection_mock
        self.checker.current_server = 'best_server'

        self.report_time_mock = mock.Mock(return_value=None)
        self.checker._report_time = self.report_time_mock

    def assert_time_reported(self, time_elapsed):
        assert self.report_time_mock.call_args[1]['time_elapsed'] == pytest.approx(time_elapsed, abs=0.1)

    def assert_time_not_reported(self):
        assert not self.report_time_mock.called

    def test_is_enabled(self):
        assert self.checker.is_enabled

    def test_alias(self):
        assert self.checker.alias, 'LDAP'

    def test_check__ok(self):
        result = self.checker.check('login', 'pass')
        assert result.is_ok
        assert not result.require_password_change
        assert result.description == 'LDAP auth successful'
        self.assert_time_reported(0)

    def test_check__invalid_password(self):
        self.bind_mock.side_effect = ldap.INVALID_CREDENTIALS({})
        result = self.checker.check('login', 'pass')
        assert not result.is_ok
        assert result.description == 'LDAP password invalid'
        self.assert_time_reported(0)

    def test_check__ldap_error(self):
        self.bind_mock.side_effect = ldap.LDAPError
        result = self.checker.check('login', 'pass')
        assert not result.is_ok
        assert result.description == 'LDAP server error'
        self.assert_time_reported(4)

    def test_check__no_servers_available(self):
        self.get_connection_mock.return_value = None
        result = self.checker.check('login', 'pass')
        assert not result.is_ok
        assert result.description == 'LDAP server unavailable'
        self.assert_time_not_reported()

    def test_check__account_in_wrong_ou(self):
        self.search_mock.return_value = []
        result = self.checker.check('login', 'pass')
        assert not result.is_ok
        assert result.description == 'LDAP account probably in wrong OU'

    def test_check__robot_ok(self):
        self.search_mock.return_value = [(TEST_ROBOT_DN, {})]
        result = self.checker.check('login', 'pass')
        assert result.is_ok
        assert not result.require_password_change
        assert result.description == 'LDAP auth successful'

    def test_check__no_robots_ok(self):
        result = self.checker.check('login', 'pass', forbid_robots=True)
        assert result.is_ok
        assert not result.require_password_change
        assert result.description == 'LDAP auth successful'

    def test_check__robot_detected(self):
        self.search_mock.return_value = [(TEST_ROBOT_DN, {})]
        result = self.checker.check('login', 'pass', forbid_robots=True)
        assert not result.is_ok
        assert result.description == 'LDAP account not suitable'
        assert self.bind_mock.called
        assert self.search_mock.called

    def test_check__robot_reported(self):
        result = self.checker.check('login', 'pass', is_robot=True, forbid_robots=True)
        assert not result.is_ok
        assert result.description == 'LDAP account not suitable'
        assert not self.bind_mock.called
        assert not self.search_mock.called

    def test_check__password_change_required_via_error_code(self):
        self.bind_mock.side_effect = ldap.INVALID_CREDENTIALS({
            'info': '80090308: LdapErr: DSID-0C090447, comment: AcceptSecurityContext error, data 773, v3839',
        })
        result = self.checker.check('login', 'pass')
        assert result.is_ok
        assert result.require_password_change
        assert result.description == 'LDAP auth successful'

    def test_check__password_change_required_via_attr(self):
        self.search_mock.return_value = [(TEST_DN, {'pwdLastSet': [b'0']})]
        result = self.checker.check('login', 'pass')
        assert result.is_ok
        assert result.require_password_change
        assert result.description == 'LDAP auth successful'

    def test_check__password_change_required_but_robot(self):
        self.search_mock.return_value = [(TEST_DN, {'pwdLastSet': [b'0'], 'userAccountControl': [b'66048']})]
        result = self.checker.check('login', 'pass')
        assert result.is_ok
        assert not result.require_password_change
        assert result.description == 'LDAP auth successful'
