from hamcrest import (
    anything,
    assert_that,
    contains,
    has_entries,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.registration_steps import register_scholar_account

from .base import BaseScholarTestCase


@allure_setup(
    feature='Работы с аккаунтом школьника',
    story='Регистрация аккаунта школьника',
)
class RegisterScholarTestCase(BaseScholarTestCase):
    def test(self):
        with register_scholar_account() as account:
            self.account = account

            userinfo = self.get_scholar_userinfo_from_blackbox()

            assert_that(userinfo, self.userinfo())

    def userinfo(self):
        return has_entries(users=contains(self.user()))

    def user(self):
        attrs = {
            'account.scholar_password': anything(),
            'person.firstname': self.account.firstname,
            'person.lastname': self.account.lastname,
        }
        attrs = has_entries({str(EavSerializer.attr_name_to_type(a)): attrs[a] for a in attrs})

        return has_entries(
            aliases={
                str(EavSerializer.alias_name_to_type('scholar')): self.account.login,
            },
            attributes=attrs,
            id=str(self.account.uid),
            uid=has_entries(value=str(self.account.uid)),
        )
