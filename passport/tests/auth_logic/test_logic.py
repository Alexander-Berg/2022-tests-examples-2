# -*- coding: utf-8 -*-
import mock
from passport.backend.perimeter.auth_api.auth_logic.logic import AuthLogic
from passport.backend.perimeter.auth_api.common.base_checker import CheckStatus
from passport.backend.perimeter.auth_api.test import BaseTestCase


class TestAuthLogic(BaseTestCase):
    def setUp(self):
        self.redis_mock = self.make_checker_mock('Redis', is_ok=False, description='Redis auth not found')
        self.ldap_mock = self.make_checker_mock('LDAP')
        self.totp_mock = self.make_checker_mock('TOTP', description='TOTP is enabled')
        self.motp_mock = self.make_checker_mock('MOTP')
        self.long_mock = self.make_checker_mock('Long')
        self.mdm_mock = self.make_checker_mock('MDM')
        self.oauth_mock = self.make_checker_mock('OAuth')

        self.redis_cache_mock = mock.Mock()
        self.redis_cache_mock.set = mock.Mock(return_value=None)

        self.logic = AuthLogic()
        self.logic._checkers = {
            'redis': self.redis_mock,
            'ldap': self.ldap_mock,
            'totp': self.totp_mock,
            'motp': self.motp_mock,
            'long': self.long_mock,
            'mdm': self.mdm_mock,
            'oauth': self.oauth_mock,
        }
        self.logic._redis_cache = self.redis_cache_mock

    def make_checker_mock(self, alias, is_ok=True, description=None):
        checker_mock = mock.Mock()
        checker_mock.is_enabled = True
        checker_mock.alias = alias
        self.set_checker_status(
            checker_mock,
            is_ok=is_ok,
            description=description or '%s auth successful' % alias,
        )
        return checker_mock

    @staticmethod
    def set_checker_status(checker_mock, is_ok, description, extra_data=None):
        method_name = 'check_if_totp_is_on' if checker_mock.alias.lower() == 'totp' else 'check'
        setattr(
            checker_mock,
            method_name,
            mock.Mock(return_value=CheckStatus(is_ok=is_ok, description=description, extra_data=extra_data or {})),
        )

    def check_response(self, result, description, used_checkers,
                       is_password_ok=True, got_errors=False, second_steps=None):
        assert result.description == description
        assert result.is_ok == is_password_ok
        assert result.got_errors == got_errors
        assert result.require_second_steps == (second_steps or set())
        assert self.redis_cache_mock.set.called == is_password_ok

        for checker_name, checker in self.logic._checkers.items():
            method_name = 'check_if_totp_is_on' if checker_name == 'totp' else 'check'
            assert getattr(checker, method_name).called == (checker_name in used_checkers)

    def test_redis_ok(self):
        self.set_checker_status(self.redis_mock, True, description='Redis auth successful')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=True,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(result, 'Redis auth successful', used_checkers={'redis'})

    def test_motp_ok(self):
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(result, 'Redis auth not found; MOTP auth successful', used_checkers={'redis', 'motp'})

    def test_internal_ldap_ok(self):
        self.set_checker_status(self.motp_mock, False, description='MOTP not enabled')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=True,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(
            result,
            'Redis auth not found; MOTP not enabled; LDAP auth successful',
            used_checkers={'redis', 'motp', 'ldap'},
        )

    def test_external_ldap_totp_ok(self):
        self.set_checker_status(self.motp_mock, False, description='MOTP not enabled')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(
            result,
            'Redis auth not found; MOTP not enabled; LDAP auth successful',
            second_steps={'totp'},
            used_checkers={'redis', 'motp', 'ldap', 'totp'},
        )

    def test_external_ldap_email_ok(self):
        self.set_checker_status(self.motp_mock, False, description='MOTP not enabled')
        self.set_checker_status(self.totp_mock, False, description='TOTP not enabled')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(
            result,
            'Redis auth not found; MOTP not enabled; LDAP auth successful',
            second_steps={'email_code'},
            used_checkers={'redis', 'motp', 'ldap', 'totp'},
        )

    def test_ldap_user_from_robot_network(self):
        self.set_checker_status(self.motp_mock, False, description='MOTP not enabled')
        self.set_checker_status(self.ldap_mock, True, description='LDAP auth successful', extra_data={'is_account_robot': False})
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=True,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(
            result,
            'Redis auth not found; MOTP not enabled; LDAP auth successful',
            second_steps={'totp'},
            used_checkers={'redis', 'motp', 'ldap', 'totp'},
        )

    def test_ldap_robot_from_robot_network(self):
        self.set_checker_status(self.motp_mock, False, description='MOTP not enabled')
        self.set_checker_status(self.ldap_mock, True, description='LDAP auth successful', extra_data={'is_account_robot': True})
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=True,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(
            result,
            'Redis auth not found; MOTP not enabled; LDAP auth successful',
            used_checkers={'redis', 'motp', 'ldap'},
        )

    def test_mdm_ok(self):
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='imap',
        )
        self.check_response(result, 'Redis auth not found; MDM auth successful', used_checkers={'redis', 'mdm'})

    def test_oauth_ok(self):
        self.set_checker_status(self.mdm_mock, False, description='MDM user not found')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='imap',
        )
        self.check_response(
            result,
            'Redis auth not found; MDM user not found; OAuth auth successful',
            used_checkers={'redis', 'mdm', 'oauth'},
        )

    def test_long_ok(self):
        self.set_checker_status(self.mdm_mock, False, description='MDM user not found')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='xmpp',
        )
        self.check_response(
            result,
            'Redis auth not found; MDM user not found; Long auth successful',
            used_checkers={'redis', 'mdm', 'long'},
        )

    def test_method_disabled(self):
        self.redis_mock.is_enabled = False
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='web',
        )
        self.check_response(result, 'Redis disabled; MOTP auth successful', used_checkers={'motp'})

    def test_all_failed(self):
        self.logic._checkers['mdm'].check.return_value = CheckStatus(False, 'MDM user not found')
        self.logic._checkers['long'].check.return_value = CheckStatus(False, 'Long user not found')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='calendar',
        )
        self.check_response(
            result,
            'Redis auth not found; MDM user not found; Long user not found',
            is_password_ok=False,
            used_checkers={'redis', 'mdm', 'long'},
        )

    def test_method_got_errors_but_other_successful(self):
        self.logic._checkers['mdm'].check.return_value = CheckStatus(False, 'MDM failed', got_errors=True)
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='calendar',
        )
        self.check_response(
            result,
            'Redis auth not found; MDM failed; Long auth successful',
            used_checkers={'redis', 'mdm', 'long'},
        )

    def test_all_got_errors(self):
        self.logic._checkers['redis'].check.return_value = CheckStatus(False, 'Redis failed', got_errors=True)
        self.logic._checkers['mdm'].check.return_value = CheckStatus(False, 'MDM failed', got_errors=True)
        self.logic._checkers['long'].check.return_value = CheckStatus(False, 'Long failed', got_errors=True)
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='calendar',
        )
        self.check_response(
            result,
            'Redis failed; MDM failed; Long failed',
            is_password_ok=False,
            got_errors=True,
            used_checkers={'redis', 'mdm', 'long'},
        )

    def test_some_got_errors_and_other_failed(self):
        self.logic._checkers['mdm'].check.return_value = CheckStatus(False, 'MDM failed', got_errors=True)
        self.logic._checkers['long'].check.return_value = CheckStatus(False, 'Long password invalid')
        result = self.logic.perform_auth(
            login='login',
            password='pass',
            ip='8.8.8.8',
            is_ip_internal=False,
            is_ip_robot=False,
            is_robot=False,
            auth_type='calendar',
        )
        self.check_response(
            result,
            'MDM failed',
            is_password_ok=False,
            got_errors=True,
            used_checkers={'redis', 'mdm', 'long'},
        )
