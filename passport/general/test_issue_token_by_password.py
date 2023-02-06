# -*- coding: utf-8 -*-
from hamcrest import (
    all_of,
    assert_that,
    has_key,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.oauth import OAuth
from passport.backend.qa.autotests.base.matchers.token import (
    token_is_for_client,
    token_is_for_user,
    token_is_valid,
    verify_token,
)
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import limit_envs

from .base import BaseIssueTokenTestCase


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='oauth: /token', story='grant_type=password')
class OAuthGtPasswordTestCase(BaseIssueTokenTestCase):
    def test_ok(self):
        with register_portal_account() as user:
            rv = OAuth().post(
                path='/token',
                form_params={
                    'grant_type': 'password',
                    'username': user.login,
                    'password': user.password,
                },
                headers=self.make_auth_headers(),
            )
            assert_that(
                rv,
                has_key('access_token'),
            )
            assert_that(
                verify_token(rv['access_token']),
                all_of(
                    token_is_valid(),
                    token_is_for_user(user),
                    token_is_for_client(self.client_id),
                ),
            )
