from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    has_key,
    not_,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.matchers.phone import equals_to_phone_number
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.steps.blackbox import userinfo_by_uid
from passport.backend.qa.autotests.base.steps.phone import confirm_phone_in_track
from passport.backend.qa.autotests.base.steps.registration_steps import register_neophonish_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='в ятиме запрещена регистрация')
@allure_setup(
    feature='passport-api: /1/bundle/account/register/',
    story='/1/bundle/account/register/neophonish/',
)
class TestRegisterNeophonish(BaseTestCase):

    def test_register__ok(self):
        phone_number = random_phone_number()

        helper = AuthMultiStep(Account(login=phone_number))

        rv = helper.start(check_result=False, with_cookie_lah=False)
        track_id = rv.get('track_id')

        confirm_phone_in_track(track_id=track_id, phone_number=phone_number)

        with register_neophonish_account(track_id=track_id) as account:
            userinfo = userinfo_by_uid(
                uid=account.uid,
                getphones='bound',
                aliases='all',
                attributes='27,28',
                phone_attributes='1',
            )
            assert_that(
                userinfo['users'][0],
                has_entries(
                    aliases=has_key('21'),
                    attributes=has_entries(**{
                        '27': 'f',
                        '28': 'l',
                    }),
                    phones=has_item(
                        has_entries(
                            attributes=has_entry(
                                '1',
                                equals_to_phone_number(phone_number, add_plus_if_needed=True),
                            ),
                        ),
                    ),
                ),
                'user={}'.format(userinfo['users'][0]),
            )

    def test_register__without_fio__ok(self):
        phone_number = random_phone_number()

        helper = AuthMultiStep(Account(login=phone_number))

        rv = helper.start(check_result=False, with_cookie_lah=False)
        track_id = rv.get('track_id')

        confirm_phone_in_track(track_id=track_id, phone_number=phone_number)

        with register_neophonish_account(track_id=track_id, firstname=None, lastname=None) as account:
            userinfo = userinfo_by_uid(
                uid=account.uid,
                getphones='bound',
                aliases='all',
                attributes='27,28',
                phone_attributes='1',
            )
            assert_that(
                userinfo['users'][0],
                has_entries(
                    aliases=has_key('21'),
                    attributes=not_(has_key('27')),
                    phones=has_item(
                        has_entries(
                            attributes=has_entry(
                                '1',
                                equals_to_phone_number(phone_number, add_plus_if_needed=True),
                            ),
                        ),
                    ),
                ),
                'user={}'.format(userinfo['users'][0]),
            )
