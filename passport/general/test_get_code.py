from hamcrest import (
    assert_that,
    equal_to,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.helpers.account_manager import get_cookies_by_token
from passport.backend.qa.autotests.base.helpers.push_challenge import make_trusted_xtoken
from passport.backend.qa.autotests.base.steps.push_2fa_steps import Push2faStep
from passport.backend.qa.autotests.base.steps.tracks import create_track_for_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/push/2fa/',
    story='/1/bundle/push/2fa/get_code',
)
class PassportPush2faSendTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account, track_id):
        helper = Push2faStep().with_account(account).with_track(track_id)
        helper.send_push()

        return helper

    @with_portal_account_and_track
    def test_ok(self, account, track_id):
        # Сделать доверенный xtoken и положить в аккаунт
        with create_track_for_account(account) as another_track_id:
            account.token = make_trusted_xtoken(account, another_track_id)

        # Получить куки из доверенного xtoken
        account.cookies = get_cookies_by_token(account.token)

        helper = self.run_prerequisites_and_get_helper(account, track_id)
        rv = helper.get_code()

        assert_that(rv['otp'], equal_to(helper.get_code_from_track()))
