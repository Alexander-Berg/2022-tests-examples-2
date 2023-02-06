from time import time

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_key,
    not_,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import (
    obtain_account_credentials,
    obtain_account_credentials_by_track,
)
from passport.backend.qa.autotests.base.steps.auth import AuthMultiStep
from passport.backend.qa.autotests.base.steps.phone import confirm_phone_in_track
from passport.backend.qa.autotests.base.steps.registration_steps import (
    register_lite_account,
    register_neophonish_account,
    register_portal_account,
)
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='в ятиме дорегистрация не имеет смысла')
@allure_setup(
    feature='passport-api: /1/bundle/complete/',
    story='/1/bundle/complete/status/',
)
class PassportCompleteStatusTestCase(BaseTestCase):
    @staticmethod
    def create_track_with_confirmed_phone():
        phone_number = random_phone_number()

        helper = AuthMultiStep(Account(login=phone_number))

        rv = helper.start(check_result=False, with_cookie_lah=False)
        track_id = rv.get('track_id')

        confirm_phone_in_track(track_id=track_id, phone_number=phone_number)

        return track_id

    @staticmethod
    def make_request(x_token, query_params=None):
        return PassportApi().get(
            path='/1/bundle/complete/status/',
            query_params=query_params,
            headers={
                'Ya-Consumer-Authorization': f'OAuth {x_token}',
                'Ya-Consumer-Client-Ip': test_env.user_ip,
            },
        )

    def test_portal_ok(self):
        with register_portal_account() as account:
            obtain_account_credentials(account, need_cookies=False, need_xtoken=True)
            rv = self.make_request(x_token=account.token)

            assert_that(
                rv,
                all_of(
                    has_entries(
                        status='ok',
                        is_complete=True,
                        is_completion_available=False,
                        is_completion_recommended=False,
                        is_completion_required=False,
                    ),
                    not_(has_key('completion_url')),
                ),
            )

    def test_lite_ok(self):
        with register_lite_account() as account:
            obtain_account_credentials(account, need_cookies=False, need_xtoken=True)
            rv = self.make_request(x_token=account.token)

            assert_that(
                rv,
                all_of(
                    has_entries(
                        status='ok',
                        is_complete=False,
                        is_completion_available=True,
                        is_completion_recommended=False,
                        is_completion_required=False,
                    ),
                    has_key('completion_url'),
                ),
            )

    def test_neophonish_ok(self):
        track_id = self.create_track_with_confirmed_phone()
        with register_neophonish_account(track_id=track_id) as account:
            obtain_account_credentials_by_track(account, track_id=track_id)
            rv = self.make_request(x_token=account.token)

            assert_that(
                rv,
                all_of(
                    has_entries(
                        status='ok',
                        is_complete=False,
                        is_completion_available=True,
                        is_completion_recommended=False,
                        is_completion_required=False,
                    ),
                    has_key('completion_url'),
                ),
            )

    def test_neophonish_without_fio_ok(self):
        track_id = self.create_track_with_confirmed_phone()
        with register_neophonish_account(track_id=track_id, firstname=None, lastname=None) as account:
            obtain_account_credentials_by_track(account, track_id=track_id)
            rv = self.make_request(x_token=account.token)

            assert_that(
                rv,
                all_of(
                    has_entries(
                        status='ok',
                        is_complete=False,
                        is_completion_available=True,
                        is_completion_recommended=True,
                        is_completion_required=False,
                    ),
                    has_key('completion_url'),
                ),
            )

    def test_neophonish_without_fio_postponed_completion_ok(self):
        track_id = self.create_track_with_confirmed_phone()
        with register_neophonish_account(track_id=track_id, firstname=None, lastname=None) as account:
            obtain_account_credentials_by_track(account, track_id=track_id)
            rv = self.make_request(
                x_token=account.token,
                query_params=dict(
                    completion_postponed_at=int(time()) - 3600,
                ),
            )

            assert_that(
                rv,
                all_of(
                    has_entries(
                        status='ok',
                        is_complete=False,
                        is_completion_available=True,
                        is_completion_recommended=False,
                        is_completion_required=False,
                    ),
                    has_key('completion_url'),
                ),
            )
