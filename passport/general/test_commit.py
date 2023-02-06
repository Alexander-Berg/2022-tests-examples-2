from unittest import skip

from hamcrest import (
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.helpers.push_challenge import make_trusted_xtoken
from passport.backend.qa.autotests.base.steps.challenge import PassAuthChallengeStep
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.push_2fa_steps import Push2faStep
from passport.backend.qa.autotests.base.steps.push_api_steps import (
    PushApiStep,
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
    story='/1/bundle/auth/password/challenge/commit/',
)
class PassportAuthChallengeTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account, track_id, antifraud_tags=None):
        helper = PassAuthChallengeStep().with_account(account).with_track(track_id)
        helper.set_track_state(antifraud_tags=antifraud_tags)
        helper.challenge_submit()
        return helper

    @with_portal_account_and_track
    def test_challenge_not_enabled_error(self, account, track_id):
        bind_secure_phone(account, random_phone_number())
        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.default_answer = '123'

        rv = helper.challenge_commit(challenge='email', check_response=False)
        assert_that(
            rv,
            has_entries(
                status='error',
                errors=['challenge.not_enabled'],
                track_id=track_id,
            ),
            'res={}'.format(rv),
        )

    @with_portal_account_and_track
    def test_ok_with_phone_confirmation(self, account, track_id):
        bind_secure_phone(account, random_phone_number())
        helper = self.run_prerequisites_and_get_helper(account, track_id)

        rv = helper.challenge_commit()
        assert_that(
            rv,
            has_entries(
                status='ok',
                track_id=track_id,
            ),
            'res={}'.format(rv),
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
            push_helper.subscribe(am_version='7.23.0')

        helper = self.run_prerequisites_and_get_helper(account, track_id)
        helper.set_track_state(antifraud_tags=['push_2fa'])

        push2fa_helper = Push2faStep().with_account(account).with_track(track_id)
        push2fa_helper.send_push()
        code = push2fa_helper.get_code()['otp']
        helper.default_answer = code

        rv = helper.challenge_commit(challenge='push_2fa', check_response=False)
        assert_that(
            rv,
            has_entries(
                status='ok',
                track_id=track_id,
            ),
            'res={}'.format(rv),
        )
