from hamcrest import (
    assert_that,
    contains,
    has_entries,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.registration_steps import register_scholar_account

from .base import BaseScholarTestCase


@allure_setup(
    feature='Работы с аккаунтом школьника',
    story='Удаление аккаунта школьника',
)
class DeleteScholarTestCase(BaseScholarTestCase):
    def test(self):
        with register_scholar_account() as account:
            self.account = account

        userinfo = self.get_scholar_userinfo_from_blackbox()
        assert_that(userinfo, self.userinfo())

    def userinfo(self):
        return has_entries(users=contains(self.user()))

    def user(self):
        return has_entries(
            id=str(self.account.uid),
            uid=dict(),
        )
