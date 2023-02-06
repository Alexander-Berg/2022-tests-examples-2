from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.steps.otp import EnableOtpStep
from passport.backend.qa.autotests.base.steps.phone import bind_and_aliasify_secure_phone
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/auth/password/multi_step/',
    story='/1/bundle/auth/password/multi_step/commit_magic/',
)
class PassportAuthByMagicTestCase(BaseTestCase):
    def build_headers(self, cookie=None):
        return {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Ya-Client-Cookie': cookie,
            'Ya-Consumer-Client-Ip': '46.175.31.223',
        }

    @with_portal_account
    def test_ok(self, account):
        phone_number = random_phone_number()
        bind_and_aliasify_secure_phone(account, phone_number)

        enable_otp_helper = EnableOtpStep().with_account(account)
        auth_helper = AuthMultiStep(account)

        enable_otp_helper.execute()

        rv = auth_helper.start()
        track_id = rv['track_id']
        csrf_token = rv['csrf_token']

        otp = enable_otp_helper.make_otp()
        auth_helper.fill_track_with_otp(track_id=track_id, otp=otp)
        auth_helper.auth_by_magic(track_id=track_id, csrf_token=csrf_token)
