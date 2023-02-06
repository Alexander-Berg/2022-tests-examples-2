# -*- coding: utf-8 -*-

import allure
from hamcrest import (
    assert_that,
    has_entry,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.cookie_steps import parse_cookies
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='passport-api: /1/bundle/auth/password/', story='/1/bundle/auth/password/submit/')
class PassportAuthTestCase(BaseTestCase):
    @allure.step
    def setUp(self):
        super(PassportAuthTestCase, self).setUp()
        self.default_headers = {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': test_env.user_agent,
            'Ya-Client-Cookie': '',
            'Ya-Consumer-Client-Ip': test_env.user_ip,
        }

    def test_should_authorize(self):
        with register_portal_account() as user:
            rv = PassportApi().post(
                path='/1/bundle/auth/password/submit/',
                form_params={
                    'login': user.login,
                    'password': user.password,
                },
                headers=self.default_headers,
            )
            assert_that(
                rv,
                has_entry('status', 'ok'),
            )
            parse_cookies(rv['cookies'])
