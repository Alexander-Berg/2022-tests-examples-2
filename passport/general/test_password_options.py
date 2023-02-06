from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.helpers.blackbox import check_blackbox_userinfo_by_uid
from passport.backend.qa.autotests.base.steps.account import set_password_options
from passport.backend.qa.autotests.base.steps.ticket_steps import get_userticket
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /2/account/',
    story='/2/account/.../password_options/',
)
class PassportAccountResetTestCase(BaseTestCase):
    @with_portal_account
    def test_set_is_changing_required__ok(self, account: Account):
        set_password_options(
            account,
            is_changing_required=True,
            changing_requirement_reason='PASSWORD_CHANGING_REASON_PWNED',
        )

    @with_portal_account
    def test_unset_is_changing_required__with_suspension__ok(self, account: Account):
        user_ticket = get_userticket(account)
        set_password_options(
            account,
            user_ticket=user_ticket,
            is_changing_required=True,
            changing_requirement_reason='PASSWORD_CHANGING_REASON_PWNED',
        )
        set_password_options(
            account,
            user_ticket=user_ticket,
            is_changing_required=False,
        )

        check_blackbox_userinfo_by_uid(
            account.uid,
            attributes_values={
                'password.pwn_forced_changing_suspended_at': TimeNow(),
            },
        )
