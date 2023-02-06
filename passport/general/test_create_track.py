import json

from hamcrest import (
    assert_that,
    has_entries,
    has_key,
    is_not,
)
from passport.backend.qa.autotests.base.accounts_store import get_account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.challenge import (
    PassStandaloneChallengeStep,
    TEST_CHALLENGE_RETPATH,
)
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.steps.tracks import read_track
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/challenge/standalone/',
    story='/1/bundle/challenge/standalone/create_track/',
)
class PassportChallengeStandaloneCreateTrackTestCase(BaseTestCase):
    def test_ok(self):
        with register_portal_account() as account:
            track_id = PassStandaloneChallengeStep().with_account(account).challenge_create_track()

        track_data = read_track(track_id)
        assert_that(
            track_data,
            has_entries(
                uid=str(account.uid),
                retpath=TEST_CHALLENGE_RETPATH,
            ),
            is_not(has_key('antifraud_tags'))
        )

    def test_ok_with_optional_params(self):
        with register_portal_account() as account:
            track_id = PassStandaloneChallengeStep().with_account(account).challenge_create_track(
                retpath=TEST_CHALLENGE_RETPATH,
                antifraud_tags=['call', 'sms'],
            )

        track_data = read_track(track_id)
        assert_that(
            track_data,
            has_entries(
                uid=str(account.uid),
                retpath=TEST_CHALLENGE_RETPATH,
                antifraud_tags=json.dumps(['call', 'sms']),
            ),
        )

    def test_ok_with_3ds(self):
        account = get_account('user_with_bound_card')
        track_id = PassStandaloneChallengeStep().with_account(account).challenge_create_track(
            antifraud_tags=['3ds'],
            card_id_for_3ds=account.extra_data['card_id'],
        )

        track_data = read_track(track_id)
        assert_that(
            track_data,
            has_entries(
                uid=str(account.uid),
                antifraud_tags=json.dumps(['3ds']),
                paymethod_id=account.extra_data['card_id'],
            ),
        )
