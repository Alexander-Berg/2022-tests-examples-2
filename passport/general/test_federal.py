from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_key,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.steps.blackbox import userinfo_by_uid
from passport.backend.qa.autotests.base.steps.registration_steps import register_federal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='в ятиме запрещена регистрация')
@allure_setup(
    feature='passport-api: /1/bundle/account/register/',
    story='/1/bundle/account/register/federal/',
)
class TestRegisterFederal(BaseTestCase):
    def test_register__ok(self):
        with register_federal_account() as account:
            userinfo = userinfo_by_uid(
                uid=account.uid,
                aliases='all',
                attributes='27,28',
            )
            assert_that(
                userinfo['users'][0],
                has_entries(
                    aliases=all_of(
                        has_key('7'),
                        has_key('24'),
                    ),
                    attributes=has_entries(**{
                        '27': 'f',
                        '28': 'l',
                    }),
                ),
                'user={}'.format(userinfo['users'][0]),
            )
