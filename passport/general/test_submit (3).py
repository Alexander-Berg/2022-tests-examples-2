from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.accounts_store import get_account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.challenge import (
    PassStandaloneChallengeStep,
    TEST_CHALLENGE_RETPATH,
)
from passport.backend.qa.autotests.base.steps.cookie_steps import get_cookies
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/challenge/standalone/',
    story='/1/bundle/challenge/standalone/submit/',
)
class PassportChallengeStandaloneSubmitTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account, antifraud_tags=None, **antifraud_kwargs):
        helper = PassStandaloneChallengeStep().with_account(account)
        self.track_id = helper.challenge_create_track(antifraud_tags=antifraud_tags, **antifraud_kwargs)
        helper = helper.with_track(self.track_id)
        return helper

    def test_no_challenges_error(self):
        with register_portal_account() as account:
            account.cookies = get_cookies(account)
            helper = self.run_prerequisites_and_get_helper(account)

            rv = helper.challenge_submit(check_response=False)
            assert_that(
                rv,
                has_entries(
                    status='error',
                    errors=['action.impossible'],
                    track_id=self.track_id,
                    retpath=TEST_CHALLENGE_RETPATH,
                ),
            )

    def test_ok_with_phone_confirmation(self):
        with register_portal_account() as account:
            account.cookies = get_cookies(account)

            secure_phone_number = random_phone_number()
            bind_secure_phone(account, secure_phone_number)

            helper = self.run_prerequisites_and_get_helper(account)

            rv = helper.challenge_submit()
            assert_that(
                rv,
                has_entries(
                    status='ok',
                    challenges_enabled=has_entries(
                        phone_confirmation=has_entries(
                            phone_number=secure_phone_number,
                            phone_id=anything(),
                            hint=anything(),
                        ),
                    ),
                    default_challenge='phone_confirmation',
                    track_id=self.track_id,
                    retpath=TEST_CHALLENGE_RETPATH,
                ),
            )

    def test_ok_with_3ds(self):
        account = get_account('user_with_bound_card')
        account.cookies = get_cookies(account)

        helper = self.run_prerequisites_and_get_helper(
            account,
            antifraud_tags='3ds',
            card_id_for_3ds=account.extra_data['card_id'],
        )

        rv = helper.challenge_submit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                challenges_enabled=has_entries(**{
                    '3ds': has_entries(
                        hint=None,
                    ),
                }),
                default_challenge='3ds',
                track_id=self.track_id,
                retpath=TEST_CHALLENGE_RETPATH,
            ),
        )

    # TODO: add webauthn challenge
