# -*- coding: utf-8 -*-
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_track_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.models.persistent_track import TRACK_TYPE_EMAIL_CONFIRMATION_CODE
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.email.email import mask_email_for_statbox

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_ANOTHER_EMAIL,
    TEST_CYRILLIC_EMAIL_ID,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_IP,
    TEST_LOGIN,
    TEST_NATIVE_EMAIL,
    TEST_PERSISTENT_TRACK_ID,
    TEST_PUNYCODE_EMAIL,
    TEST_SHORT_CODE,
    TEST_UID,
    TEST_USER_AGENT,
)


TEST_AUTH_ID = 'auth_id'


class BaseConfirmEmailTestCase(BaseEmailBundleTestCase, EmailTestMixin, AccountModificationNotifyTestMixin):
    def setUp(self):
        super(BaseConfirmEmailTestCase, self).setUp()
        self.default_account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:something',
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
                    },
                },
                {
                    'id': TEST_EMAIL_ID + 1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL,
                        EMAIL_NAME_MAPPING['confirmed']: 1,
                    },
                },
                {
                    'id': TEST_CYRILLIC_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_PUNYCODE_EMAIL,
                    },
                },
            ],
        )
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(authid=TEST_AUTH_ID, **self.default_account_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid=TEST_UID,
                track_id=TEST_PERSISTENT_TRACK_ID,
                content={
                    'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                    'address': TEST_EMAIL,
                    'short_code': TEST_SHORT_CODE,
                },
            ),
        )
        self.setup_statbox_templates()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='email_bundle',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'confirmed',
            address=mask_email_for_statbox(TEST_EMAIL),
            authid=TEST_AUTH_ID,
            uid=str(TEST_UID),
            ip='127.0.0.1',
            user_agent=TEST_USER_AGENT,
            status='ok',
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

    def check_history_db(self, email_id=TEST_EMAIL_ID, email=TEST_EMAIL):
        self.check_historydb_records([
            ('action', 'validator_confirm'),
            ('email.%d' % email_id, 'updated'),
            ('email.%d.address' % email_id, email),
            ('email.%d.bound_at' % email_id, TimeNow()),
            ('email.%d.confirmed_at' % email_id, TimeNow()),
            ('user_agent', TEST_USER_AGENT),
        ])

    def check_emails_sent(self, confirmed_address=TEST_EMAIL):
        self.assert_emails_sent(sorted([
            self.create_account_modification_mail(
                event_name='email_add',
                email_address=confirmed_address,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_add',
                email_address=TEST_ANOTHER_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=False,
            ),
            self.create_account_modification_mail(
                event_name='email_add',
                email_address=TEST_NATIVE_EMAIL,
                context=dict(
                    USER_IP=TEST_IP,
                    login=TEST_LOGIN,
                    UID=TEST_UID,
                ),
                is_native=True,
            ),
        ], key=lambda e: e['addresses'][0]))


class CommonConfirmTests(object):
    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.check_history_db()
        self.check_emails_sent()
        self.env.statbox.assert_contains([
            self.env.statbox.entry('confirmed', action=self.action),
        ])
        self._check_account_modification_push_sent()

    def test_ok_by_token(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                scope='passport:bind_email',
                **self.default_account_kwargs
            ),
        )
        rv = self.make_request(
            headers={'authorization': 'OAuth foo'},
            exclude_headers=['cookie'],
        )
        self.assert_ok_response(rv)
        self.check_history_db()
        self.check_emails_sent()
        self.env.statbox.assert_contains([
            self.env.statbox.entry('confirmed', action=self.action, _exclude=['authid']),
        ])

    def test_ok_with_cyrillic_email(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid=TEST_UID,
                track_id=TEST_PERSISTENT_TRACK_ID,
                content={
                    'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                    'address': TEST_PUNYCODE_EMAIL,
                    'short_code': TEST_SHORT_CODE,
                },
            ),
        )
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.check_history_db(email_id=TEST_CYRILLIC_EMAIL_ID, email=TEST_PUNYCODE_EMAIL)
        self.check_emails_sent(
            confirmed_address=TEST_PUNYCODE_EMAIL,
        )

    def test_already_confirmed(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid=TEST_UID,
                track_id=TEST_PERSISTENT_TRACK_ID,
                content={
                    'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                    'address': TEST_ANOTHER_EMAIL,
                    'short_code': TEST_SHORT_CODE,
                },
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['email.already_confirmed'])
        self.check_account_modification_push_not_sent()

    def test_email_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                uid=TEST_UID,
                track_id=TEST_PERSISTENT_TRACK_ID,
                content={
                    'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                    'address': TEST_ANOTHER_EMAIL + '2',
                    'short_code': TEST_SHORT_CODE,
                },
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['email.incorrect_key'])


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'email_add'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'email_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:email_add': 5,
            'push:email_change': 5,
        },
    )
)
class TestConfirmEmailByLink(BaseConfirmEmailTestCase,
                             CommonConfirmTests):
    default_url = '/1/bundle/email/confirm/by_link/?consumer=dev'
    action = 'confirm_by_link'
    http_query_args = {'key': TEST_PERSISTENT_TRACK_ID}

    def _check_account_modification_push_sent(self):
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='email_change',
            uid=TEST_UID,
            title='Новая резервная почта в аккаунте {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
        )

    def test_empty_key(self):
        rv = self.make_request(query_args={'key': ''})
        self.assert_error_response(rv, ['key.empty'])

    def test_incorrect_key(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(TEST_UID, TEST_PERSISTENT_TRACK_ID, is_found=False),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['email.incorrect_key'])


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'email_add'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'email_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:email_add': 5,
            'push:email_change': 5,
        },
    )
)
class TestConfirmEmailByCode(BaseConfirmEmailTestCase,
                             CommonConfirmTests):
    default_url = '/1/bundle/email/confirm/by_code/?consumer=dev'
    action = 'confirm_by_code'

    def setUp(self):
        super(TestConfirmEmailByCode, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.persistent_track_id = TEST_PERSISTENT_TRACK_ID

        self.http_query_args = {
            'track_id': self.track_id,
            'key': TEST_SHORT_CODE,
        }

        self.env.statbox.bind_entry('confirmed',  track_id=self.track_id, _inherit_from='confirmed')

    def _check_account_modification_push_sent(self):
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='email_change',
            uid=TEST_UID,
            title='Новая резервная почта в аккаунте {}'.format(TEST_LOGIN),
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_invalid_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.persistent_track_id = None
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_incorrect_key(self):
        rv = self.make_request(query_args={'key': 'foo'})
        self.assert_error_response(rv, ['email.incorrect_key'], attempts_left=2)

    def test_key_check_limit_exceeded(self):
        for _ in range(settings.ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT):
            self.make_request(query_args={'key': 'foo'})

        rv = self.make_request(query_args={'key': 'foo'})
        self.assert_error_response(rv, ['email.key_check_limit_exceeded'])
