from hamcrest import (
    all_of,
    assert_that,
    equal_to,
    not_,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import (
    with_portal_account,
    with_portal_account_and_track,
)
from passport.backend.qa.autotests.base.matchers.token import (
    token_is_for_client,
    token_is_for_user,
    token_is_trusted,
    token_is_valid,
    verify_token,
)
from passport.backend.qa.autotests.base.secrets import secrets
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.challenge import PassAuthChallengeStep
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.token_steps import issue_token_by_sessionid
from passport.backend.qa.autotests.base.steps.tracks import set_track_state
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/oauth/',
    story='/1/bundle/oauth/token_by_sessionid/',
)
class PassportGetTokenBySessionidTestCase(BaseTestCase):
    def build_headers(self, cookie=None):
        return {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Ya-Client-Cookie': cookie,
            'Ya-Consumer-Client-Ip': '46.175.31.223',
        }

    def pass_phone_challenge(self, account, track_id):
        set_track_state(track_id, is_auth_challenge_shown=True, antifraud_tags=['sms'])
        bind_secure_phone(account, random_phone_number())
        helper = PassAuthChallengeStep().with_account(account).with_track(track_id)
        helper.challenge_submit()
        assert_that(helper.default_challenge, equal_to('phone_confirmation'))
        helper.challenge_commit()

    @with_portal_account
    def test_ok(self, account):
        token = issue_token_by_sessionid(
            headers=self.build_headers(cookie=account.cookies),
            client_id=secrets.OAUTH_XTOKEN_CLIENT_ID,
            client_secret=secrets.OAUTH_XTOKEN_CLIENT_SECRET,
        )
        assert_that(
            verify_token(token, get_is_xtoken_trusted=True),
            all_of(
                token_is_valid(),
                token_is_for_user(account),
                token_is_for_client(secrets.OAUTH_XTOKEN_CLIENT_ID),
                not_(token_is_trusted()),
            ),
        )

    @with_portal_account_and_track
    def test_ok_with_track_id(self, account, track_id):
        self.pass_phone_challenge(account, track_id)
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
