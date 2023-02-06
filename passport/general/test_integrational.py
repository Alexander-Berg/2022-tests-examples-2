from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.cookie_steps import get_cookies
from passport.backend.qa.autotests.base.steps.otp import EnableOtpStep
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


TEST_PIN = '424242'
TEST_DEVICE_ID = 'device-id'


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/otp/',
    story='/1/bundle/otp/enable',
)
class PassportChallengeStandaloneCommitTestCase(BaseTestCase):
    def test_minimal_ok(self):
        with register_portal_account() as account:
            account.cookies = get_cookies(account)
            bind_secure_phone(account, random_phone_number())
            helper = EnableOtpStep().with_account(account)

            helper.execute()

    def test_custom_ok(self):
        with register_portal_account() as account:
            account.cookies = get_cookies(account)
            bind_secure_phone(account, random_phone_number())
            helper = EnableOtpStep().with_account(account)

            helper.execute(custom_pin=TEST_PIN, device_id=TEST_DEVICE_ID)
