from hamcrest import (
    anything,
    assert_that,
    has_entries,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.push_api import (
    WsSession,
    WsTimeoutError,
)
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.steps.push_api_steps import (
    PushApiStep,
    TEST_APP_ID_BLACKLISTED_ANDROID,
    TEST_APP_PLATFORM_ANDROID,
)
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.common import noneless_dict


TEST_PUSH_SERVICE = 'some_service'
TEST_EVENT_NAME = 'some_event'
TEST_PUSH_TITLE = 'Это тестовый пуш'
TEST_PUSH_SUBTITLE = 'Тест'
TEST_PUSH_BODY = 'Тело тестового пуша'
TEST_PUSH_WEBVIEW_URL = 'https://ya.ru/чтоэтотакое'


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/push',
    story='/1/bundle/push/send/am/',
)
class PassportPush2faSendTestCase(BaseTestCase):
    def run_prerequisites_and_get_helper(self, account):
        return PushApiStep().with_account(account)

    def _assert_am_push_received(
        self,
        account: Account,
        ws: WsSession,
        subtitle=None,
        body=None,
        webview_url=None,
        require_web_auth=None,
    ):
        assert_that(
            ws.recv(timeout=10),
            has_entries(
                uid=str(account.uid),
                service='passport-push',
                operation=TEST_EVENT_NAME,
                message=has_entries(**noneless_dict(
                    passp_am_proto='1.0',
                    push_service=TEST_PUSH_SERVICE,
                    push_id=anything(),
                    event_name=TEST_EVENT_NAME,
                    is_silent=False,
                    uid=account.uid,
                    title=TEST_PUSH_TITLE,
                    subtitle=subtitle,
                    body=body,
                    webview_url=webview_url,
                    require_web_auth=require_web_auth,
                    min_am_version_android='7.23.0',
                    min_am_version_ios='6.5.0',
                )),
            ),
        )

    def _assert_am_push_not_received(self, ws: WsSession):
        """
        Этот кейс лучше не проверять избыточно:
        он гарантированно занимает несколько секунд
        """
        with self.assertRaises(WsTimeoutError):
            ws.recv(5)

    @with_portal_account
    def test__simple__ok(self, account):
        helper = self.run_prerequisites_and_get_helper(account)
        with helper.with_recv_socket(wait_for_subscription=True) as ws:
            rv = helper.send_am(
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT_NAME,
                title=TEST_PUSH_TITLE,
                check_response=False,
            )
            assert_that(rv, has_entries(status='ok'), 'resp: {}'.format(rv))
            self._assert_am_push_received(account=account, ws=ws)

    @with_portal_account
    def test__extended__ok(self, account):
        helper = self.run_prerequisites_and_get_helper(account)

        with helper.with_recv_socket(wait_for_subscription=True) as ws:
            rv = helper.send_am(
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT_NAME,
                title=TEST_PUSH_TITLE,
                body=TEST_PUSH_BODY,
                subtitle=TEST_PUSH_SUBTITLE,
                webview_url=TEST_PUSH_WEBVIEW_URL,
                require_web_auth=True,
                check_response=False,
            )
            assert_that(rv, has_entries(status='ok'), 'resp: {}'.format(rv))
            self._assert_am_push_received(
                account=account,
                ws=ws,
                subtitle=TEST_PUSH_SUBTITLE,
                body=TEST_PUSH_BODY,
                webview_url=TEST_PUSH_WEBVIEW_URL,
                require_web_auth=True,
            )

    @with_portal_account(need_xtoken=True)
    def test__check_subscriptions__ok(self, account):
        helper = self.run_prerequisites_and_get_helper(account)

        with helper.with_subscription(am_version='10.10.10', wait_for_subscription=True):
            with helper.with_recv_socket(wait_for_subscription=True) as ws:
                rv = helper.send_am(
                    push_service=TEST_PUSH_SERVICE,
                    event_name=TEST_EVENT_NAME,
                    title=TEST_PUSH_TITLE,
                    body=TEST_PUSH_BODY,
                    check_subscriptions=True,
                    check_response=False,
                )
                assert_that(rv, has_entries(status='ok'), 'resp: {}'.format(rv))
                self._assert_am_push_received(account=account, ws=ws)

    @with_portal_account
    def test__check_subscriptions__no_subscriptions(self, account):
        helper = self.run_prerequisites_and_get_helper(account)

        with helper.with_recv_socket(wait_for_subscription=True) as ws:
            rv = helper.send_am(
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT_NAME,
                title=TEST_PUSH_TITLE,
                body=TEST_PUSH_BODY,
                check_subscriptions=True,
                check_response=False,
            )
            assert_that(
                rv,
                has_entries(status='error', errors=['push_api.no_subscriptions']),
                'resp: {}'.format(rv),
            )
            self._assert_am_push_not_received(ws=ws)

    @with_portal_account(need_xtoken=True)
    def test__check_subscriptions__blacklist__no_subscriptions(self, account):
        helper = self.run_prerequisites_and_get_helper(account)

        with helper.with_subscription(
            am_version='10.10.10',
            app_platform=TEST_APP_PLATFORM_ANDROID,
            app_id=TEST_APP_ID_BLACKLISTED_ANDROID,
            wait_for_subscription=True,
        ):
            with helper.with_recv_socket(wait_for_subscription=True) as ws:
                rv = helper.send_am(
                    push_service=TEST_PUSH_SERVICE,
                    event_name=TEST_EVENT_NAME,
                    title=TEST_PUSH_TITLE,
                    body=TEST_PUSH_BODY,
                    check_subscriptions=True,
                    check_response=False,
                )
                assert_that(
                    rv,
                    has_entries(status='error', errors=['push_api.no_subscriptions']),
                    'resp: {}'.format(rv),
                )
                self._assert_am_push_not_received(ws=ws)
