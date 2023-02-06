from hamcrest import (
    assert_that,
    has_entries,
    has_item,
)
from passport.backend.qa.autotests.base.account import Account
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.push_api import PushApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.matchers.token import verify_token
from passport.backend.qa.autotests.base.steps.push_api_steps import (
    PushApiStep,
    TEST_APP_ID_ANDROID,
    TEST_APP_ID_IOS,
    TEST_APP_PLATFORM_IOS,
    TEST_DEVICE_ID,
)
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


TEST_DEVICE_TOKEN = 'A*ASCNASjucnalicbNOAIScLIASCliASC'
TEST_AM_VERSION = '1.2.3'


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/push/',
    story='/1/bundle/push/subscribe/',
)
class PassportSubscribeTestCase(BaseTestCase):
    @with_portal_account(need_xtoken=True)
    def test__ok(self, account: Account):
        helper = PushApiStep().with_account(account)
        with helper.with_subscription(
            app_id=TEST_APP_ID_IOS,
            app_platform=TEST_APP_PLATFORM_IOS,
            wait_for_subscription=True,
        ):
            subscriptions = PushApi().list(account.uid)

        token = verify_token(account.token, get_login_id='yes')

        assert_that(
            subscriptions,
            has_item(has_entries(
                app=TEST_APP_ID_IOS,
                device=TEST_DEVICE_ID,
                platform='apns',
                extra='{"1": "%s"}' % token['login_id'],
            )),
        )

    @with_portal_account(need_xtoken=True)
    def test__with_am_version__ok(self, account: Account):
        helper = PushApiStep().with_account(account)
        with helper.with_subscription(
            app_id=TEST_APP_ID_IOS,
            app_platform=TEST_APP_PLATFORM_IOS,
            am_version='1.2.3',
            wait_for_subscription=True,
        ):
            subscriptions = PushApi().list(account.uid)

        token = verify_token(account.token, get_login_id='yes')

        assert_that(
            subscriptions,
            has_item(has_entries(
                app=TEST_APP_ID_IOS,
                device=TEST_DEVICE_ID,
                platform='apns',
                extra='{"0": "1.2.3", "1": "%s"}' % token['login_id'],
            )),
        )

    @with_portal_account(need_xtoken=True)
    def test__with_app_name_postfix__ok(self, account: Account):
        helper = PushApiStep().with_account(account)
        with helper.with_subscription(
            app_platform='Android 10 Super android',
            wait_for_subscription=True,
        ):
            subscriptions = PushApi().list(account.uid)

        token = verify_token(account.token, get_login_id='yes')

        assert_that(
            subscriptions,
            has_item(has_entries(
                app=TEST_APP_ID_ANDROID + '.passport',
                device=TEST_DEVICE_ID,
                platform='gcm',
                extra='{"1": "%s"}' % token['login_id'],
            )),
        )

    @with_portal_account(need_xtoken=True)
    def test__with_app_version__ok(self, account: Account):
        helper = PushApiStep().with_account(account)
        with helper.with_subscription(
            app_id=TEST_APP_ID_IOS,
            app_platform=TEST_APP_PLATFORM_IOS,
            app_version='8.9.10-megabuild @(*!)@(&!)@',
            wait_for_subscription=True,
        ):
            subscriptions = PushApi().list(account.uid)

        token = verify_token(account.token, get_login_id='yes')

        assert_that(
            subscriptions,
            has_item(has_entries(
                app=TEST_APP_ID_IOS,
                device=TEST_DEVICE_ID,
                platform='apns',
                extra='{"1": "%s", "2": "8.9.10-megabuild @(*!)@(&!)@"}' % token['login_id'],
            )),
        )
