# -*- coding: utf-8 -*-
from hamcrest import (
    assert_that,
    has_entry,
    is_not,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.oauth import OAuth
from passport.backend.qa.autotests.base.matchers.token import (
    token_is_valid,
    verify_token,
)
from passport.backend.qa.autotests.base.secrets import secrets
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.steps.token_steps import issue_token
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='oauth: /revoke_token', story='revoke_token')
class OAuthRevokeTokenTestCase(BaseTestCase):
    def test_ok(self):
        with register_portal_account() as user:
            token = issue_token(
                user=user,
                client_id=secrets.OAUTH_YA_LOGIN_CLIENT_ID,
                client_secret=secrets.OAUTH_YA_LOGIN_CLIENT_SECRET,
                device_id='a' * 10,
            )
            rv = OAuth().post(
                path='/revoke_token',
                form_params={
                    'access_token': token,
                    'client_id': secrets.OAUTH_YA_LOGIN_CLIENT_ID,
                    'client_secret': secrets.OAUTH_YA_LOGIN_CLIENT_SECRET,
                },
            )
            assert_that(
                rv,
                has_entry('status', 'ok'),
            )
            assert_that(
                verify_token(token),
                is_not(token_is_valid()),
            )
