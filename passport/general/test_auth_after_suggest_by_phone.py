from hamcrest import (
    assert_that,
    has_entries,
    has_items,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import (
    obtain_account_credentials,
    with_portal_account,
)
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.steps.phone import (
    bind_secure_phone,
    confirm_phone_in_track,
)
from passport.backend.qa.autotests.base.steps.registration_steps import (
    FORCE_CHALLENGE_LOGIN_PREFIX,
    register_portal_account,
)
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
class PassportAuthAfterSuggestByPhoneTestCase(BaseTestCase):
    def build_headers(self):
        return {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Ya-Consumer-Client-Ip': '46.175.31.223',
        }

    @with_portal_account
    def test_auth(self, account: Account):
        phone_number = random_phone_number()
        bind_secure_phone(account, phone_number)

        with register_portal_account() as account2:
            obtain_account_credentials(account2)
            bind_secure_phone(account2, phone_number)

            helper = AuthMultiStep(account)
            rv = helper.start(check_result=True, with_cookie_lah=True)
            track_id = rv.get('track_id')

            rv = helper.check_account_suggest_by_phone_availability(phone_number=phone_number)
            assert rv['is_suggest_available']

            confirm_phone_in_track(track_id=track_id, phone_number=phone_number)

            rv = helper.get_account_suggest_by_phone(track_id=track_id)
            assert_that(
                rv['accounts'],
                has_items(
                    has_entries(uid=account.uid, allowed_auth_flows=['instant', 'full']),
                    has_entries(uid=account2.uid, allowed_auth_flows=['instant', 'full']),
                ),
            )

            rv = helper.auth_after_suggest_by_phone(track_id=track_id)
            assert sorted(list(rv.keys())) == ['status', 'track_id']

    @with_portal_account(
        login_prefix=FORCE_CHALLENGE_LOGIN_PREFIX,
        email='test@test.com',
        allow_challenge=True,
    )
    def test_with_challenge(self, account: Account):
        phone_number = random_phone_number()
        bind_secure_phone(account, phone_number)

        with register_portal_account() as account2:
            obtain_account_credentials(account2)
            bind_secure_phone(account2, phone_number)

            helper = AuthMultiStep(account)
            rv = helper.start(check_result=True, with_cookie_lah=False)
            track_id = rv.get('track_id')

            confirm_phone_in_track(track_id=track_id, phone_number=phone_number)
            rv = helper.auth_after_suggest_by_phone(track_id=track_id)

            assert_that(rv, has_entries(
                status='ok',
                state='auth_challenge',
            ))
