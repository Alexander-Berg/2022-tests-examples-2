from hamcrest import (
    anything,
    assert_that,
    has_entries,
    is_not,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.settings.common import PASSPORT_URL_TEMPLATE
from passport.backend.qa.autotests.base.steps.push_2fa_steps import Push2faStep
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/push/2fa/',
    story='/1/bundle/push/2fa/send',
)
class PassportPush2faSendTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account, track_id):
        helper = Push2faStep().with_account(account).with_track(track_id)

        return helper

    @with_portal_account_and_track
    def test_ok(self, account, track_id):
        helper = self.run_prerequisites_and_get_helper(account, track_id)

        with helper.with_recv_socket(wait_for_subscription=True) as ws:
            helper.send_push()

            assert_that(
                ws.recv(timeout=10),
                has_entries(
                    uid=str(account.uid),
                    service='passport-push',
                    operation='2fa_code',
                    message=has_entries(
                        passp_am_proto='1.0',
                        push_service='2fa',
                        push_id=anything(),
                        event_name='2fa_code',
                        is_silent=False,
                        uid=account.uid,
                        title='Вход в аккаунт на Яндексе',
                        body='Нажмите, чтобы увидеть код подтверждения или сменить пароль, если вы не запрашивали код',
                        webview_url='{}/am/push/getcode?track_id={}'.format(PASSPORT_URL_TEMPLATE % dict(tld='ru'), track_id),
                        require_web_auth=True,
                        min_am_version_android='7.23.0',
                        min_am_version_ios='6.5.0',
                    ),
                ),
            )

        assert_that(helper.get_code_from_track(), is_not(None))
