# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_USER_IP
from passport.backend.api.views.bundle.account.app_passwords.forms import APP_TYPES
from passport.backend.api.views.bundle.account.app_passwords.manage import GRANT
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)


TEST_UID = 42
TEST_LOGIN = 'test_user'

TEST_DEVICE_NAME = u'Почта на айфоне %<b>'
TEST_APP_TYPE = 'mail'
TEST_APP_NAME = TEST_DEVICE_NAME
TEST_ESCAPED_APP_NAME = u'Почта на айфоне &amp;#37;&lt;b&gt;'


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'app_password_add'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:app_password_add': 5,
            'email:app_password_add': 5,
        },
    )
)
class CreateAppPasswordTestcase(
    BaseBundleTestViews,
    EmailTestMixin,
    AccountModificationNotifyTestMixin,
):

    default_url = '/1/bundle/account/app_passwords/create/send_notifications/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
        app_type=TEST_APP_TYPE,
        app_name=TEST_APP_NAME,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host='yandex.ru',
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list([GRANT])
        self.setup_blackbox_response()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.env.stop()
        del self.env

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def setup_blackbox_response(self, totp_is_set=True):
        bb_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={
                'account.enable_app_password': True,
                'account.2fa_on': totp_is_set,
            },
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            bb_response,
        )

    def check_emails_sent(self):
        self.assert_emails_sent([
            self.create_account_modification_mail(
                event_name='app_password_add',
                email_address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                context=dict(
                    USER_IP=TEST_USER_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='app_password_add',
                email_address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                context=dict(
                    USER_IP=TEST_USER_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=True,
            ),
        ])

    @parameterized.expand([
        [app_type]
        for app_type in APP_TYPES
    ])
    def test_ok(self, app_type):
        rv = self.make_request(query_args=dict(app_type=app_type))

        self.assert_ok_response(rv)
        self.check_emails_sent()
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP,
            event_name='app_password_add',
            uid=TEST_UID,
            title='Пароль приложения в {} успешно создан'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
        )

    def test_push_disabled(self):
        with settings_context(ACCOUNT_MODIFICATION_PUSH_ENABLE={'smth_else'}):
            rv = self.make_request(query_args=dict(app_type=TEST_APP_TYPE))

        self.assert_ok_response(rv)
        self.check_account_modification_push_not_sent()

    @parameterized.expand([
        [app_type]
        for app_type in APP_TYPES
    ])
    def test_app_name_empty(self, app_type):
        rv = self.make_request(query_args=dict(app_type=app_type, app_name=None))

        self.assert_ok_response(rv)
        self.check_emails_sent()

    def test_2fa_off(self):
        self.setup_blackbox_response(totp_is_set=False)
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_emails_sent()
