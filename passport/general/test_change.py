from hamcrest import (
    all_of,
    assert_that,
    equal_to,
    has_entries,
    has_key,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.steps.account import _get_headers
from passport.backend.qa.autotests.base.steps.blackbox import userinfo_by_uid
from passport.backend.qa.autotests.base.steps.registration_steps import register_federal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='в ятиме запрещена регистрация')
@allure_setup(
    feature='passport-api: /1/bundle/account/federal/',
    story='/1/bundle/account/federal/change/',
)
class TestFederalChange(BaseTestCase):
    def test_change_federal__ok(self):
        with register_federal_account() as account:
            form_params = dict(
                uid=account.uid,
                firstname='new_firstname',
                lastname='new_lastname',
                display_name='new_display_name',
                emails='new_mail@mail.ru',  # доп почта
            )
            rv = PassportApi().post(
                path='/1/bundle/account/federal/change/',
                form_params=form_params,
                headers=_get_headers(),
            )
            self.assert_has_entries(rv, {'status': 'ok'})

            userinfo = userinfo_by_uid(
                uid=account.uid,
                aliases='all',
                attributes='27,28,1009',
                regname='yes',
                getemails='all',
                email_attributes='1',
            )
            print(userinfo)
            assert_that(
                userinfo['users'][0],
                has_entries(
                    aliases=all_of(
                        has_key('7'),
                        has_key('24'),
                    ),
                    attributes=all_of(
                        has_entries(**{
                            '27': form_params['firstname'],
                            '28': form_params['lastname'],
                            '1009': '1',
                        }),
                    ),
                    display_name=has_entries(
                        name=form_params['display_name'],
                        avatar={'default': '0/0-0', 'empty': True},
                    ),
                ),
                'user={}'.format(userinfo['users'][0]),
            )

            user_email = userinfo['users'][0]['emails'][0]['attributes']['1']
            assert_that(user_email, equal_to(form_params['emails']))
