from unittest import skip

from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.helpers.push_challenge import make_trusted_xtoken
from passport.backend.qa.autotests.base.steps.challenge import PassAuthChallengeStep
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.push_api_steps import (
    PushApiStep,
    TEST_APP_ID_BLACKLISTED_ANDROID,
    TEST_DEVICE_ID,
)
from passport.backend.qa.autotests.base.steps.tracks import create_track_for_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/auth/password/challenge/',
    story='/1/bundle/auth/password/challenge/submit/',
)
class PassportAuthChallengeTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account: Account, track_id: str):
        helper = PassAuthChallengeStep().with_account(account).with_track(track_id)
        return helper

    @with_portal_account_and_track
    def test_no_challenges_error(self, account: Account, track_id: str):
        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state()

        rv = helper.challenge_submit(check_response=False)
        assert_that(
            rv,
            has_entries(
                status='error',
                errors=['action.impossible'],
                track_id=track_id,
            ),
        )

    @with_portal_account_and_track
    def test_ok_with_phone_confirmation(self, account: Account, track_id: str):
        secure_phone_number = random_phone_number()
        bind_secure_phone(account, secure_phone_number)

        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state(antifraud_tags=['phone'])

        rv = helper.challenge_submit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                challenges_enabled=has_entries(
                    phone=has_entries(
                        hint=anything(),
                    ),
                ),
                default_challenge='phone',
                track_id=track_id,
            ),
        )

    @skip('push-челленжи временно выключены')
    @with_portal_account_and_track
    def test_ok_with_push_2fa(self, account: Account, track_id: str):
        # Сделать доверенный xtoken и подписаться им на пуши
        with create_track_for_account(account) as another_track_id:
            account.token = make_trusted_xtoken(
                account,
                another_track_id,
                device_info=dict(device_id=TEST_DEVICE_ID),
            )
            push_helper = PushApiStep().with_account(account)

        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state(antifraud_tags=['push_2fa'])

        with push_helper.with_subscription(am_version='7.23.0', wait_for_subscription=True):
            rv = helper.challenge_submit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                challenges_enabled=has_entries(
                    push_2fa=has_entries(
                        hint=None,
                    ),
                ),
                default_challenge='push_2fa',
                track_id=track_id,
            ),
        )

    @with_portal_account_and_track
    def test_push_2fa_blacklisted_app_name(self, account: Account, track_id: str):
        # Сделать доверенный xtoken и подписаться им на пуши
        with create_track_for_account(account) as another_track_id:
            account.token = make_trusted_xtoken(
                account,
                another_track_id,
                device_info=dict(device_id=TEST_DEVICE_ID),
            )
            push_helper = PushApiStep().with_account(account)

        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state(antifraud_tags=['push_2fa'])

        with push_helper.with_subscription(
            am_version='7.23.0',
            app_id=TEST_APP_ID_BLACKLISTED_ANDROID,
            wait_for_subscription=True,
        ):
            rv = helper.challenge_submit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                challenges_enabled=has_entries(
                    phone=has_entries(
                        hint=anything(),
                    ),
                ),
                default_challenge='phone',
                track_id=track_id,
            ),
        )

    @with_portal_account_and_track(register_kwargs={'email': 'test@test.de'})
    def test_ok_with_email_confirmation(self, account: Account, track_id: str):
        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state(antifraud_tags=['email_code'])
        rv = helper.challenge_submit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                challenges_enabled=has_entries(
                    email_code=has_entries(
                        hint=['t***t@t***.de'],
                    ),
                ),
                default_challenge='email_code',
                track_id=track_id,
            ),
        )
