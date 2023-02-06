import allure
from hamcrest import (
    assert_that,
    contains,
    has_entries,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.steps.registration_steps import register_scholar_account
from passport.backend.qa.autotests.base.test_env import test_env

from .base import BaseScholarTestCase


@allure_setup(
    feature='Работы с аккаунтом школьника',
    story='Изменение персональных данных школьника',
)
class UpdateScholarTestCase(BaseScholarTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new = dict(
            firstname='Мария',
            lastname='Иванова',
        )

    def test(self):
        with register_scholar_account() as account:
            self.account = account
            self.update_scholar()
            userinfo = self.get_scholar_userinfo_from_blackbox()
            assert_that(userinfo, self.userinfo())

    @allure.step('Изменение персональных данных школьника')
    def update_scholar(self):
        rv = PassportApi().post(
            form_params=dict(
                firstname=self.new['firstname'],
                lastname=self.new['lastname'],
                uid=str(self.account.uid),
            ),
            headers={
                'Ya-Client-User-Agent': test_env.user_agent,
                'Ya-Consumer-Client-Ip': test_env.user_ip,
            },
            path='/1/bundle/scholar/update/',
        )
        assert_that(rv, has_entries(status='ok'))

    def userinfo(self):
        return has_entries(users=contains(self.user()))

    def user(self):
        attrs = {
            'person.firstname': self.new['firstname'],
            'person.lastname': self.new['lastname'],
        }
        attrs = has_entries({str(EavSerializer.attr_name_to_type(a)): attrs[a] for a in attrs})

        return has_entries(
            attributes=attrs,
            uid=has_entries(value=str(self.account.uid)),
        )
