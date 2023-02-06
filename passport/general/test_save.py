from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.challenge import PassStandaloneChallengeStep
from passport.backend.qa.autotests.base.steps.cookie_steps import get_cookies
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/challenge/standalone/',
    story='/1/bundle/challenge/standalone/save/',
)
class PassportChallengeStandaloneSaveTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account):
        helper = PassStandaloneChallengeStep().with_account(account)
        self.track_id = helper.challenge_create_track()
        helper = helper.with_track(self.track_id)
        helper.challenge_submit()
        helper.challenge_commit()
        return helper

    def test_ok(self):
        with register_portal_account() as account:
            account.cookies = get_cookies(account)
            bind_secure_phone(account, random_phone_number())
            self.run_prerequisites_and_get_helper(account)

            rv = PassportApi().post(
                form_params=dict(
                    track_id=self.track_id,
                ),
                headers={
                    'Ya-Client-Host': PASSPORT_HOST,
                    'Ya-Client-User-Agent': test_env.user_agent,
                    'Ya-Client-Cookie': account.cookies,
                    'Ya-Consumer-Client-Ip': test_env.user_ip,
                },
                path='/1/bundle/challenge/standalone/save/',
            )
            assert_that(
                rv,
                has_entries(
                    status='ok',
                    retpath=anything(),
                ),
            )
