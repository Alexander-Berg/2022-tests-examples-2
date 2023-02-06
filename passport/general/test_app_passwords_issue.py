# -*- coding: utf-8 -*-
import allure
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.oauth import OAuth
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.settings.env import ENV
from passport.backend.qa.autotests.base.steps.cookie_steps import get_cookies
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


TEST_DEVICE_ID = 'deviceid123'
TEST_MAGNITOLA_CLIENT_ID = {
    'production': 'ce6ed0f691294fd6b5972bc0959335bc',
    'testing': 'bb1c044ac84d4e4f9f1c2de36d2b003b',
    'development': 'bb1c044ac84d4e4f9f1c2de36d2b003b',
}
TEST_MAGNITOLA_CLIENT_ID['rc'] = TEST_MAGNITOLA_CLIENT_ID['production']


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(feature='oauth: /token/app_passwords/issue', story='app_passwords/issue')
class OAuthAppPasswordsIssueTestCase(BaseTestCase):
    @allure.step
    def setUp(self):
        super(OAuthAppPasswordsIssueTestCase, self).setUp()
        self.default_headers = {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': test_env.user_agent,
            'Ya-Consumer-Client-Ip': test_env.user_ip,
        }

    def test_ok(self):
        with register_portal_account() as user:
            cookies = get_cookies(user)
            rv = OAuth().post(
                path='/iface_api/2/token/app_passwords/issue',
                form_params={
                    'grant_type': 'frontend_assertion',
                    'device_id': TEST_DEVICE_ID,
                    'client_id': TEST_MAGNITOLA_CLIENT_ID[ENV],
                    'language': 'ru',
                },
                headers=dict(self.default_headers, **{'Ya-Client-Cookie': cookies}),
            )
            self.assert_has_entries(rv, {'status': 'ok'})
            self.assert_has_keys(rv, ['token', 'token_alias'])
            self.assert_has_entries(rv['token'], {'is_app_password': True})
            self.assert_has_keys(
                rv['token'].get('scopes', {}).get('Пароли для приложений', []),
                ['app_password:magnitola'],
            )
