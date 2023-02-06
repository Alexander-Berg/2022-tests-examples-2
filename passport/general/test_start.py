from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/auth/password/multi_step/',
    story='/1/bundle/auth/password/multi_step/start/',
)
class PassportAuthStartTestCase(BaseTestCase):
    @with_portal_account
    def test_can_authorize_portal_account(self, account: Account):
        helper = AuthMultiStep(account)
        rv = helper.start(check_result=False)
        self.assert_has_entries(
            rv,
            dict(
                status='ok',
                can_authorize=True,
                auth_methods=['password', 'magic_link', 'magic_x_token'],
                preferred_auth_method='password',
            ),
        )
        self.assert_has_keys(rv, ['track_id', 'csrf_token', 'magic_link_email'])
