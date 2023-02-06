import allure
from hamcrest import (
    assert_that,
    equal_to,
    greater_than,
    has_entries,
    is_not,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.steps.registration_steps import register_scholar_account
from passport.backend.qa.autotests.base.test_env import test_env

from .base import BaseScholarTestCase


@allure_setup(
    feature='Работы с аккаунтом школьника',
    story='Смена пароля школьника',
)
class ChangePasswordTestCase(BaseScholarTestCase):
    def test_ok(self):
        with register_scholar_account() as account:
            self.account = account
            old_password = self.get_attribute_from_userinfo(
                self.get_scholar_userinfo_from_blackbox(),
                'account.scholar_password',
            )

            self.change_password()

            new_password = self.get_attribute_from_userinfo(
                self.get_scholar_userinfo_from_blackbox(),
                'account.scholar_password',
            )
            assert_that(new_password, is_not(equal_to(old_password)))

    def test_revoke_credentials(self):
        with register_scholar_account() as account:
            self.account = account

            old_global_logout_datetime = self.get_attribute_from_userinfo(
                self.get_scholar_userinfo_from_blackbox(),
                'account.global_logout_datetime',
            )

            self.change_password(revoke_credentials=True)

            new_global_logout_datetime = self.get_attribute_from_userinfo(
                self.get_scholar_userinfo_from_blackbox(),
                'account.global_logout_datetime',
            )

            assert_that(new_global_logout_datetime, greater_than(old_global_logout_datetime or 0))

    @allure.step('Смена пароля школьника')
    def change_password(self, revoke_credentials=False):
        rv = PassportApi().post(
            form_params=dict(
                password='миртрудмай',
                revoke_credentials='1' if revoke_credentials else '0',
                uid=str(self.account.uid),
            ),
            headers={
                'Ya-Client-User-Agent': test_env.user_agent,
                'Ya-Consumer-Client-Ip': test_env.user_ip,
            },
            path='/1/bundle/scholar/change_password/',
        )
        assert_that(rv, has_entries(status='ok'))

    def get_attributes_from_userinfo(self, userinfo, attributes):
        all_attrs = userinfo.get('users', [dict()])[0].get('attributes', dict())
        return {a: all_attrs.get(str(EavSerializer.attr_name_to_type(a))) for a in attributes}

    def get_attribute_from_userinfo(self, userinfo, attribute):
        return self.get_attributes_from_userinfo(userinfo, [attribute]).get(attribute)
