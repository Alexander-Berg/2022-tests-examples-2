from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.phone import get_confirmation_code_from_track
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/phone/',
    story='/1/bundle/phone/confirm_and_bind/',
)
class PassportConfirmAndBindSimpleTestCase(BaseTestCase):
    @with_portal_account
    def test_ok(self, account):
        phone_number = random_phone_number()

        rv = PassportApi().post(
            form_params=dict(
                display_language='ru',
                number=phone_number,
            ),
            headers={
                'Ya-Client-Cookie': account.cookies,
                'Ya-Client-Host': PASSPORT_HOST,
                'Ya-Client-User-Agent': test_env.user_agent,
                'Ya-Consumer-Client-Ip': test_env.user_ip,
            },
            path='/1/bundle/phone/confirm_and_bind/submit/',
        )
        assert_that(
            rv,
            has_entries(
                status='ok',
                track_id=anything(),
            ),
            'resp={}'.format(rv),
        )
        track_id = rv.get('track_id')

        confirmation_code = get_confirmation_code_from_track(track_id)

        for _ in range(2):
            # убеждаемся, что при ретраях коммит-ручки потребитель получит не ошибку, а ожидаемый ответ
            rv = PassportApi().post(
                form_params=dict(
                    code=confirmation_code,
                    track_id=track_id,
                ),
                headers={
                    'Ya-Client-Cookie': account.cookies,
                    'Ya-Client-Host': PASSPORT_HOST,
                    'Ya-Client-User-Agent': test_env.user_agent,
                    'Ya-Consumer-Client-Ip': test_env.user_ip,
                },
                path='/1/bundle/phone/confirm_and_bind/commit/',
            )
            assert_that(
                rv,
                has_entries(
                    status='ok',
                ),
                'resp={}'.format(rv),
            )
