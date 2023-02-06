import allure
from hamcrest import (
    all_of,
    anything,
    assert_that,
    contains,
    has_entries,
    has_key,
    is_not,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.builders.proxied.social import SocialApi
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.auth import SocialAuthSubmitStep
from passport.backend.qa.autotests.base.steps.challenge import (
    enable_force_challenge,
    PassAuthChallengeStep,
)
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.steps.registration_steps import register_social_account
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(
    description='В проде нельзя создавать произвольные таски Социализма',
    production=False,
)
@limit_envs(
    description='Для ятима пока нет тестовых аккаунтов',
    intranet_production=False,
    intranet_testing=False,
)
@allure_setup(
    feature='Челлендж на соц. авторизации',
    story='Прохождение соц. авторизации, когда требуется челлендж',
)
class SocialAuthWithChallengeTestCase(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = None
        self.secure_phone = None
        self.track_id = None

    def test_challenge_passed(self):
        with register_social_account() as account:
            self.account = account
            self.secure_phone = random_phone_number()

            bind_secure_phone(account, self.secure_phone)
            enable_force_challenge(account)

            with allure.step('Начало соц. авторизации с обязательным челленджем'):
                result = self.social_auth_submit()
                assert_that(
                    result.callback_response,
                    all_of(
                        is_not(has_key('account')),
                        is_not(has_key('cookies')),
                        has_entries(
                            state='auth_challenge',
                            status='ok',
                            track_id=anything(),
                        ),
                    ),
                )
            self.track_id = result.callback_response.get('track_id')

            self.pass_challenge()

            with allure.step('Получение credentials после прохождения челленджа'):
                rv = self.social_issue_credentials()
                assert_that(
                    rv,
                    has_entries(
                        account=anything(),
                        cookies=anything(),
                        state='auth',
                        status='ok',
                    ),
                )

    def test_challenge_not_passed(self):
        with register_social_account() as account:
            self.account = account
            self.secure_phone = random_phone_number()

            bind_secure_phone(account, self.secure_phone)
            enable_force_challenge(account)

            with allure.step('Начало соц. авторизации с обязательным челленджем'):
                result = self.social_auth_submit()
                assert_that(
                    result.callback_response,
                    all_of(
                        is_not(has_key('account')),
                        is_not(has_key('cookies')),
                        has_entries(
                            state='auth_challenge',
                            status='ok',
                            track_id=anything(),
                        ),
                    ),
                )
            self.track_id = result.callback_response.get('track_id')

            with allure.step('Попытка получить credentials без прохождения челленджа'):
                rv = self.social_issue_credentials()
                assert_that(
                    rv,
                    all_of(
                        is_not(has_key('account')),
                        is_not(has_key('cookies')),
                        has_entries(
                            state='auth_challenge',
                            status='ok',
                            track_id=anything(),
                        ),
                    ),
                )

    def social_auth_submit(self):
        rv = SocialApi().get(
            path='/api/profiles',
            query_params=dict(uid=str(self.account.uid)),
        )
        assert_that(
            rv,
            has_entries(
                profiles=contains(
                    has_entries(
                        allow_auth=True,
                        uid=self.account.uid,
                        userid=anything(),
                    ),
                ),
            ),
        )
        social_userid = rv.get('profiles')[0].get('userid') if rv.get('profiles') else None

        return SocialAuthSubmitStep.from_profile_userid(social_userid).execute()

    @allure.step('Получение credentials после прохождения соц. авторизации')
    def social_issue_credentials(self):
        return PassportApi().post(
            form_params=dict(
                track_id=self.track_id,
            ),
            headers={
                'Ya-Client-Accept-Language': '',
                'Ya-Client-Host': PASSPORT_HOST,
                'Ya-Client-User-Agent': test_env.user_agent,
                'Ya-Consumer-Client-Ip': test_env.user_ip,
            },
            path='/1/bundle/auth/social/issue_credentials/',
        )

    def pass_challenge(self):
        PassAuthChallengeStep().with_track(self.track_id).execute()
