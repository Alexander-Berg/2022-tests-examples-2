# -*- coding: utf-8 -*-
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_ANOTHER_EMAIL,
    TEST_CYRILLIC_EMAIL_ID,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_IP,
    TEST_LOGIN,
    TEST_NATIVE_EMAIL,
    TEST_PUNYCODE_EMAIL,
    TEST_UID,
    TEST_USER_AGENT,
)


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'email_delete'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'email_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:email_delete': 5,
            'push:email_change': 5,
        },
    )
)
class TestDeleteEmail(
    BaseEmailBundleTestCase,
    EmailTestMixin,
    AccountModificationNotifyTestMixin,
):
    default_url = '/1/bundle/email/delete/?consumer=dev'
    http_query_args = {'email': TEST_EMAIL}

    def setUp(self):
        super(TestDeleteEmail, self).setUp()
        self.setup_blackbox_response()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )

    def setup_blackbox_response(self, age=100, **kwargs):
        blackbox_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:something',
            age=age,
            emails=[
                {
                    'address': TEST_NATIVE_EMAIL,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                        EMAIL_NAME_MAPPING['confirmed']: '1',
                    },
                },
                {
                    'id': TEST_EMAIL_ID + 1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL,
                        EMAIL_NAME_MAPPING['is_rpop']: '1',
                        EMAIL_NAME_MAPPING['is_silent']: '1',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
                {
                    'id': TEST_EMAIL_ID + 2,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL + '2',
                        EMAIL_NAME_MAPPING['confirmed']: '1',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
                {
                    'id': TEST_CYRILLIC_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_PUNYCODE_EMAIL,
                        EMAIL_NAME_MAPPING['confirmed']: '1',
                        EMAIL_NAME_MAPPING['is_silent']: '1',
                    },
                },
            ],
        )
        blackbox_kwargs.update(kwargs)
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **blackbox_kwargs
            ),
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def check_emails_sent(self):
        self.assert_emails_sent([
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_ANOTHER_EMAIL + '2',
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_NATIVE_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
            ),
        ])

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_historydb_records([
            ('action', 'validator_delete'),
            ('email.%d' % TEST_EMAIL_ID, 'deleted'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_EMAIL),
            ('user_agent', TEST_USER_AGENT),
        ])
        self.check_emails_sent()
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='email_change',
            uid=TEST_UID,
            title='Новая резервная почта в аккаунте {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
        )

    def test_ok_with_cyrillic_email(self):
        rv = self.make_request(query_args={'email': TEST_PUNYCODE_EMAIL})

        self.assert_ok_response(rv)
        self.check_historydb_records([
            ('action', 'validator_delete'),
            ('email.%d' % TEST_CYRILLIC_EMAIL_ID, 'deleted'),
            ('email.%d.address' % TEST_CYRILLIC_EMAIL_ID, TEST_PUNYCODE_EMAIL),
            ('user_agent', TEST_USER_AGENT),
        ])
        self.assert_emails_sent(sorted([
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_PUNYCODE_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_ANOTHER_EMAIL + '2',
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_delete',
                email_address=TEST_NATIVE_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
            ),
        ], key=lambda email: email['addresses'][0]))

    def test_ok_with_2fa(self):
        self.setup_blackbox_response(
            attributes={
                'account.2fa_on': True,
            },
            crypt_password=None,
        )
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_historydb_records([
            ('action', 'validator_delete'),
            ('email.%d' % TEST_EMAIL_ID, 'deleted'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_EMAIL),
            ('user_agent', TEST_USER_AGENT),
        ])
        self.check_emails_sent()

    def test_email_not_found(self):
        rv = self.make_request(query_args={'email': 'blabla@gmail.com'})

        self.assert_error_response(rv, ['email.not_found'])
        self.check_account_modification_push_not_sent()

    def test_email_is_native(self):
        rv = self.make_request(query_args={'email': TEST_NATIVE_EMAIL})

        self.assert_error_response(rv, ['email.is_native'])

    def test_no_password_required_for_unsafe_email(self):
        self.setup_blackbox_response(age=100500)

        rv = self.make_request(query_args={'email': TEST_ANOTHER_EMAIL + '2'})

        self.assert_ok_response(rv)

    def test_no_emails_sent_for_unconfirmed(self):
        rv = self.make_request(query_args={'email': TEST_ANOTHER_EMAIL})

        self.assert_ok_response(rv)
        self.assert_emails_sent([])
