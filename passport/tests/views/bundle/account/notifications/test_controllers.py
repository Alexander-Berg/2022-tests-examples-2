from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.consts import (
    TEST_LOGIN,
    TEST_UID,
    TEST_USER_IP1,
)
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.utils.string import smart_text


TEST_HOST = 'yandex.ru'


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={
        'login',
        'social_add',
    },
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'social_add'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:login': 5,
            'email:social_add': 5,
            'push:social_add': 5,
        },
    )
)
class TestAccountModificationNotify(
    EmailTestMixin,
    BaseBundleTestViews,
    AccountModificationNotifyTestMixin,
):
    mocked_grants = ['account.modification_notify']
    default_url = '/1/bundle/account/modification/send_notifications/?consumer=dev'
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP1,
    )
    http_method = 'POST'

    def setUp(self):
        super(TestAccountModificationNotify, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.email = self.create_native_email(TEST_LOGIN, 'yandex.ru')
        self.userinfo = dict(self.default_userinfo)
        self.setup_blackbox_response()
        self.start_account_modification_notify_mocks(ip=TEST_USER_IP1)
        self.setup_kolmogor()

    def tearDown(self):
        self.env.stop()
        self.stop_account_modification_notify_mocks()
        super(TestAccountModificationNotify, self).tearDown()

    @property
    def default_userinfo(self):
        return dict(
            emails=[self.email],
            login=TEST_LOGIN,
            uid=TEST_UID,
        )

    def setup_blackbox_response(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.userinfo),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def check_blackbox_request(self):
        r = self.env.blackbox.get_requests_by_method('userinfo')[0]
        r.assert_post_data_contains(dict(emails='getall'))

    def test_no_grants(self):
        self.env.grants.set_grant_list([])
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                event_name='social_add',
            ),
        )
        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def test_wrong_event_name(self):
        rv = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                event_name='wrong',
            ),
        )
        self.assert_error_response(rv, error_codes=['event_name.invalid'])

    def test_push_social_add(self):
        rv = self.make_request(
            query_args=dict(
                event_name='social_add',
                push_enabled='1',
                uid=TEST_UID,
            ),
        )
        self.assert_ok_response(rv)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP1,
            event_name='social_add',
            uid=TEST_UID,
            title='Теперь аккаунт {} связан с соцсетью'.format(TEST_LOGIN),
            body='Если вы её прикрепили, всё в порядке. Если нет, нажмите здесь',
        )
        self.check_blackbox_request()

    def test_mail_social_add(self):
        rv = self.make_request(
            query_args=dict(
                event_name='social_add',
                mail_enabled='1',
                uid=TEST_UID,
                social_provider='vkontakte',
            ),
        )

        self.assert_ok_response(rv)

        self.assert_emails_sent([
            self.create_account_modification_mail(
                'social_add',
                self.email['address'],
                dict(
                    login=self.userinfo['login'],
                    PROVIDER=smart_text('ВКонтакте'),
                    USER_IP=TEST_USER_IP1,
                ),
            ),
        ])
        self.check_blackbox_request()

    def test_mail_login(self):
        rv = self.make_request(
            query_args=dict(
                event_name='login',
                mail_enabled='1',
                uid=TEST_UID,
            ),
        )

        self.assert_ok_response(rv)

        self.assert_emails_sent([
            self.create_account_modification_mail(
                'login',
                self.email['address'],
                dict(
                    login=self.userinfo['login'],
                    USER_IP=TEST_USER_IP1,
                ),
            ),
        ])
        self.check_blackbox_request()

    def test_counter_overflow(self):
        self.setup_kolmogor(rate=5)
        rv = self.make_request(
            query_args=dict(
                event_name='social_add',
                push_enabled='1',
                mail_enabled='1',
                uid=TEST_UID,
            ),
        )

        self.assert_ok_response(rv)
        self.check_account_modification_push_not_sent()
        self.assert_no_emails_sent()

    def test_disabled_by_experiment(self):
        with settings_context(
            ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=7,
        ):
            rv = self.make_request(
                query_args=dict(
                    event_name='social_add',
                    push_enabled='1',
                    mail_enabled='1',
                    uid=TEST_UID,
                ),
            )

        self.assert_ok_response(rv)
        self.check_account_modification_push_not_sent()
        self.assert_no_emails_sent()

    def test_disabled_by_experiment_but_enabled_by_uid(self):
        with settings_context(
            ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=7,
            ACCOUNT_MODIFICATION_NOTIFY_WHITELIST={TEST_UID},
        ):
            rv = self.make_request(
                query_args=dict(
                    event_name='social_add',
                    push_enabled='1',
                    mail_enabled='1',
                    uid=TEST_UID,
                    social_provider='vkontakte',
                ),
            )

        self.assert_ok_response(rv)
        self.check_account_modification_push_sent(
            ip=TEST_USER_IP1,
            event_name='social_add',
            uid=TEST_UID,
            title='Теперь аккаунт {} связан с соцсетью'.format(TEST_LOGIN),
            body='Если вы её прикрепили, всё в порядке. Если нет, нажмите здесь',
        )

        self.assert_emails_sent([
            self.create_account_modification_mail(
                'social_add',
                self.email['address'],
                dict(
                    login=self.userinfo['login'],
                    PROVIDER=smart_text('ВКонтакте'),
                    USER_IP=TEST_USER_IP1,
                ),
            ),
        ])
