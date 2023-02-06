from hamcrest import (
    all_of,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.matchers.token import (
    token_is_for_client,
    token_is_for_user,
    token_is_trusted,
    token_is_valid,
    verify_token,
)
from passport.backend.qa.autotests.base.secrets import secrets
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.steps.phone import (
    bind_and_aliasify_secure_phone,
    confirm_phone_in_track,
)
from passport.backend.qa.autotests.base.steps.token_steps import issue_token_by_sessionid
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/auth/password/multi_step/',
    story='/1/bundle/auth/password/multi_step/commit_sms_code/',
)
class PassportAuthBySmsCodeTestCase(BaseTestCase):
    def build_headers(self, cookie=None):
        return {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Ya-Client-Cookie': cookie,
            'Ya-Consumer-Client-Ip': '46.175.31.223',
        }

    def assert_oauth_tokens_are_trusted_for_track(self, account: Account, track_id: str):
        token = issue_token_by_sessionid(
            headers=self.build_headers(cookie=account.cookies),
            client_id=secrets.OAUTH_XTOKEN_CLIENT_ID,
            client_secret=secrets.OAUTH_XTOKEN_CLIENT_SECRET,
            track_id=track_id,
        )
        assert_that(
            verify_token(token, get_is_xtoken_trusted='yes'),
            all_of(
                token_is_valid(),
                token_is_for_user(account),
                token_is_for_client(secrets.OAUTH_XTOKEN_CLIENT_ID),
                token_is_trusted(),
            ),
        )

    @with_portal_account
    def test_can_authorize_portal_account(self, account: Account):
        phone_number = random_phone_number()
        bind_and_aliasify_secure_phone(account, phone_number)

        helper = AuthMultiStep(account)
        rv = helper.start(check_result=True, with_cookie_lah=True)
        track_id = rv.get('track_id')

        confirm_phone_in_track(track_id=track_id, phone_number=phone_number)
        rv = helper.auth_by_sms_code(track_id)
        assert_that(
            rv,
            has_entries(
                status='ok',
                track_id=track_id,
            ),
        )
        self.assert_oauth_tokens_are_trusted_for_track(account, track_id)
