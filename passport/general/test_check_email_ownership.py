from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.steps.email_steps import (
    confirm_email_ownership_send_code,
    confirm_email_ownership_with_code,
)
from passport.backend.qa.autotests.base.steps.tracks import read_track
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/email/check_ownership/',
    story='/1/bundle/email/check_ownership/send_code/',
)
class CheckEmailOwnershipSendCodeTestCase(BaseTestCase):
    @with_portal_account_and_track
    def test_ok(self, track_id: str, account: Account):
        confirm_email_ownership_send_code(track_id=track_id)
        rv = read_track(track_id)
        assert_that(
            rv,
            has_entries(
                email_check_ownership_code=anything(),
            ),
        )


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/email/check_ownership/',
    story='/1/bundle/email/check_ownership/confirm/',
)
class CheckEmailOwnershipSendConfirmTestCase(BaseTestCase):
    @with_portal_account_and_track
    def test_ok(self, track_id: str, account: Account):
        confirm_email_ownership_send_code(track_id=track_id)
        rv = read_track(track_id)
        assert_that(
            rv,
            has_entries(
                email_check_ownership_code=anything(),
            ),
        )
        code = rv['email_check_ownership_code']
        confirm_email_ownership_with_code(track_id, account.uid, code)
