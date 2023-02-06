# -*- coding: utf-8 -*-
import allure
from hamcrest import (
    all_of,
    assert_that,
    has_entry,
    has_key,
    not_,
)
from passport.backend.qa.autotests.base.accounts_store import get_account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.oauth import OAuth
from passport.backend.qa.autotests.base.builders.proxied.perimeter import Perimeter
from passport.backend.qa.autotests.base.secrets import secrets
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(development=False, testing=False, production=False, description='Периметр существует только в ятиме')
@allure_setup(feature='Периметр', story='/ping')
class PerimeterTestCase(BaseTestCase):
    @allure.step
    def setUp(self):
        super(PerimeterTestCase, self).setUp()
        self.builder = Perimeter()

    @staticmethod
    def default_params(login, password, auth_type='web', is_ip_internal=True, is_ip_robot=False, is_robot=False):
        return {
            'login': login,
            'password': password,
            'auth_type': auth_type,
            'ip': test_env.user_ip,
            'is_ip_internal': '1' if is_ip_internal else '0',
            'is_ip_robot': '1' if is_ip_robot else '0',
            'is_robot': '1' if is_robot else '0',
        }

    def test_param_missing_error(self):
        rv = self.builder.post(path='auth')
        assert_that(
            rv,
            all_of(
                has_entry('status', 'error'),
                has_entry('description', '`login` is missing'),
                has_key('request_id'),
            ),
        )

    def test_password_invalid_error(self):
        account = get_account('user')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password='foobar',
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'password_invalid'),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_internal_ok(self):
        account = get_account('user')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_external_with_email_code_ok(self):
        account = get_account('user')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'second_step_required'),
                has_entry('second_steps', ['email_code']),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_external_with_totp_ok(self):
        account = get_account('user_with_2fa')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'second_step_required'),
                has_entry('second_steps', ['totp']),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_user_from_robot_network_ok(self):
        account = get_account('user_with_2fa')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
                is_ip_robot=True,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'second_step_required'),
                has_entry('second_steps', ['totp']),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_robot_from_robot_network_ok(self):
        account = get_account('robot')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
                is_ip_robot=True,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_robot_from_external_network_error(self):
        account = get_account('robot')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'password_invalid'),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_presumable_robot_from_external_network_error(self):
        account = get_account('user')  # в параметрах передаём, что это робот, поэтому в AD даже не пойдём
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
                is_ip_internal=False,
                is_robot=True,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'password_invalid'),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_ldap_password_change_required(self):
        account = get_account('user_with_password_change_required')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.password,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                has_entry('password_change_required', True),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_mdm_ok(self):
        account = get_account('user')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.extra_data['mdm_password'],
                auth_type='imap',
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_oauth_ok(self):
        account = get_account('user')

        with allure.step('Получение OAuth-токена'):
            rv = OAuth().post(
                path='/token',
                form_params={
                    'grant_type': 'password',
                    'client_id': secrets.OAUTH_MAIL_CLIENT_ID,  # TODO: добавить в секреты
                    'client_secret': secrets.OAUTH_MAIL_CLIENT_SECRET,
                    'username': account.login,
                    'password': account.password,
                },
            )
            assert_that(
                rv,
                has_key('access_token'),
            )
            oauth_token = rv['access_token']

        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=oauth_token,
                auth_type='imap',
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )

    def test_long_ok(self):
        account = get_account('user')
        rv = self.builder.post(
            path='auth',
            form_params=self.default_params(
                login=account.login,
                password=account.extra_data['long_password'],
                auth_type='xmpp',
                is_ip_internal=False,
            ),
        )
        assert_that(
            rv,
            all_of(
                has_entry('status', 'ok'),
                not_(has_key('password_change_required')),
                has_key('description'),
                has_key('request_id'),
            ),
        )
