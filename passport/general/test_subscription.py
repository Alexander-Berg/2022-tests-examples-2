from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.helpers.blackbox import check_blackbox_userinfo_by_uid
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/account/',
    story='/1/account/.../subscription/',
)
class PassportAccountSubscribeTestCase(BaseTestCase):
    @with_portal_account
    def test_subscribe_and_unsubscribe_user_to_bank(self, account):
        rv = PassportApi().post(
            path='/1/account/%s/subscription/bank/' % account.uid,
        )

        self.assert_has_entries(rv, {'status': 'ok'})

        check_blackbox_userinfo_by_uid(
            account.uid,
            attributes_values={
                'account.bank_subscription': '1',
            },
        )

        rv = PassportApi().delete(
            path='/1/account/%s/subscription/bank/' % account.uid,
        )

        self.assert_has_entries(rv, {'status': 'ok'})

        check_blackbox_userinfo_by_uid(
            account.uid,
            attributes_values={
                'account.bank_subscription': None,
            },
        )
