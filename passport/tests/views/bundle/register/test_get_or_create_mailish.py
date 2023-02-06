# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_broker import (
    SocialBrokerInvalidPkceVerifierError,
    SocialBrokerInvalidTaskIdError,
    SocialBrokerTaskNotFoundError,
)
from passport.backend.core.builders.social_broker.faker.social_broker import check_pkce_ok_response
from passport.backend.core.counters import register_mailish
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox


TEST_CONSUMER = 'dev'

TEST_HOST = 'yandex.ru'
TEST_USER_IP = '37.9.101.188'
TEST_UID = 1

TEST_EMAIL = 'AdMiN@Gmail.Com'
TEST_EMAIL_ID = 1
TEST_EMAIL_NORMALIZED = 'admin@gmail.com'
TEST_YNDX_EMAIL = 'yndx-Test-mailish-admin@gmail.com'
TEST_NATIVE_EMAIL = 'admin@yandex.ru'

TEST_MAILISH_ID_EMAIL = 'neadmin@gmail.com'
TEST_MAILISH_ID = 'ORSXg5BNNvqws3djoNUC22LE'
TEST_MAILISH_LOWER_ID = TEST_MAILISH_ID.lower()

TEST_CLIENT_ID = 'foo'
TEST_CLIENT_SECRET = 'bar'
TEST_DEVICE_ID = 'c3po'
TEST_DEVICE_NAME = 'IFridge'
TEST_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_TOKEN_TYPE = 'bearer'

TEST_TASK_ID = 'deadbeef'
TEST_CODE_VERIFIER = 'code_verifier'


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    ALLOW_NATIVE_MAILISH_EMAILS=False,
    **mock_counters(
        REGISTER_MAILISH_PER_CONSUMER_COUNTER=(60, 60, 5),
    )
)
class TestGetOrCreateMailish(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/get_or_create/mailish/'
    http_method = 'post'
    http_query_args = dict(
        email=TEST_EMAIL,
        mailish_id=TEST_MAILISH_ID,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        device_id=TEST_DEVICE_ID,
        device_name=TEST_DEVICE_NAME,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
    )
    consumer = TEST_CONSUMER

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(
            grants={
                'account': [
                    'get_or_create_mailish.base',
                    'get_or_create_mailish',
                ],
            },
        ))

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_TOKEN,
                'token_type': TEST_TOKEN_TYPE,
            },
        )

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            mode='account_get_or_create_mailish',
        )
        self.env.statbox.bind_entry(
            'local_base_with_uid',
            _inherit_from='local_base',
            uid=str(TEST_UID),
            login=TEST_EMAIL_NORMALIZED,
        )
        self.env.statbox.bind_entry(
            'account_modification_base',
            event='account_modification',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent='-',
        )

        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'account_modification_alias_added',
            _inherit_from='account_modification_base',
            entity='aliases',
            operation='added',
        )
        self.env.statbox.bind_entry(
            'account_modification_karma',
            _inherit_from='account_modification_base',
            entity='karma',
            action='account_register',
            destination='frodo',
            old='-',
            new='0',
            suid='1',
            login='admin@gmail.com',
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'account_modification_rpop_added',
            _inherit_from='account_modification_base',
            entity='account.emails',
            confirmed_at=DatetimeNow(convert_to_datetime=True),
            bound_at=DatetimeNow(convert_to_datetime=True),
            created_at=DatetimeNow(convert_to_datetime=True),
            email_id=str(TEST_EMAIL_ID),
            is_rpop='1',
            is_unsafe='1',
            operation='added',
            new=mask_email_for_statbox(TEST_EMAIL_NORMALIZED),
            old='-',
            uid=str(TEST_UID),
            is_suitable_for_restore='0',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_2',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='2',
            suid='1',
        )
        self.env.statbox.bind_entry(
            'account_modification_subscription_8',
            _inherit_from='account_modification_base',
            entity='subscriptions',
            operation='added',
            sid='8',
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base_with_uid',
            action='account_created',
        )
        self.env.statbox.bind_entry(
            'token_created',
            _inherit_from='local_base_with_uid',
            action='token_created',
            client_id=TEST_CLIENT_ID,
        )

    def check_response_ok(self, rv, is_new_account):
        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            oauth_token=TEST_TOKEN,
            is_new_account=is_new_account,
        )

    def check_db_ok(self, shard_count=3, mailish_id=TEST_MAILISH_LOWER_ID, email=TEST_EMAIL_NORMALIZED):
        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), shard_count)

        self.env.db.check_db_attr(TEST_UID, 'account.registration_datetime', TimeNow())

        self.env.db.check('aliases', 'mailish', mailish_id, uid=1, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'portal', uid=1, db='passportdbcentral')

        self.env.db.check_db_attr(TEST_UID, 'account.default_email', email)
        self.env.db.check_db_attr(TEST_UID, 'account.display_name', 'p:%s' % email)

        self.env.db.check_db_attr_missing(TEST_UID, 'account.user_defined_login')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.gender')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.birthday')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.country')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.city')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.language')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.timezone')
        self.env.db.check_db_attr_missing(TEST_UID, 'password.encrypted')

    def check_historydb_ok(self, email_created=True, account_created=True,
                           mailish_id=TEST_MAILISH_LOWER_ID, email=TEST_EMAIL_NORMALIZED):
        historydb_entries = []

        if account_created:
            historydb_entries += [
                {'name': 'info.login', 'value': mailish_id},
                {'name': 'info.ena', 'value': '1'},
                {'name': 'info.disabled_status', 'value': '0'},
                {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
                {'name': 'info.default_email', 'value': email},
                {'name': 'info.mail_status', 'value': '1'},
                {'name': 'info.display_name', 'value': 'p:%s' % email},
                {'name': 'info.karma_prefix', 'value': '0'},
                {'name': 'info.karma_full', 'value': '0'},
                {'name': 'info.karma', 'value': '0'},
                {'name': 'alias.mailish.add', 'value': mailish_id},
                {'name': 'mail.add', 'value': '1'},
                {'name': 'sid.add', 'value': '8|%(login)s,2|%(login)s' % {'login': mailish_id}},
            ]

        if email_created:
            now = TimeNow()
            if mailish_id and not account_created:
                historydb_entries += [
                    {'name': 'info.default_email', 'value': email},
                    {'name': 'info.display_name', 'value': 'p:%s' % email},
                ]
            historydb_entries += [
                {'name': 'email.1', 'value': 'created'},
                {'name': 'email.1.address', 'value': email},
                {'name': 'email.1.confirmed_at', 'value': now},
                {'name': 'email.1.created_at', 'value': now},
                {'name': 'email.1.bound_at', 'value': now},
                {'name': 'email.1.is_rpop', 'value': '1'},
                {'name': 'email.1.is_unsafe', 'value': '1'},
            ]

        if account_created or email_created:
            historydb_entries += [
                {'name': 'action', 'value': 'account_register'},
                {'name': 'consumer', 'value': 'dev'},
            ]

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            historydb_entries,
        )

    def check_statbox(self, registered=False, rpop_added=False, token_created=False, mailish_id=TEST_MAILISH_LOWER_ID,
                      email=TEST_EMAIL_NORMALIZED, previous_display_name=None):
        entries = [
            self.env.statbox.entry('submitted'),
        ]
        if registered:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification_base',
                    entity='account.disabled_status',
                    operation='created',
                    old='-',
                    new='enabled',
                ),
                self.env.statbox.entry(
                    'account_modification_base',
                    entity='account.mail_status',
                    operation='created',
                    old='-',
                    new='active',
                ),
                self.env.statbox.entry(
                    'account_modification_alias_added',
                    type=str(ANT['mailish']),
                    value=mailish_id,
                ),
                self.env.statbox.entry('account_modification_rpop_added'),
                self.env.statbox.entry(
                    'account_modification_base',
                    entity='person.display_name',
                    operation='created',
                    old='-',
                    new='p:%s' % email,
                ),
                self.env.statbox.entry('account_modification_karma', login=mailish_id),
                self.env.statbox.entry('account_modification_subscription_8'),
                self.env.statbox.entry('account_modification_subscription_2'),
                self.env.statbox.entry('account_created', login=mailish_id),
            ])
        elif rpop_added:
            entries.extend([
                self.env.statbox.entry('account_modification_rpop_added'),
                self.env.statbox.entry(
                    'account_modification_base',
                    entity='person.display_name',
                    operation='created' if previous_display_name is None else 'updated',
                    old='-' if previous_display_name is None else previous_display_name,
                    new='p:%s' % email,
                ),
            ])
        if token_created:
            entries.extend(
                [
                    self.env.statbox.entry(
                        'token_created',
                        login=mailish_id,
                    ),
                ],
            )

        self.env.statbox.assert_has_written(entries)

    def check_oauth_ok(self):
        eq_(len(self.env.oauth.requests), 1)
        self.env.oauth.requests[0].assert_post_data_contains({
            'client_id': TEST_CLIENT_ID,
            'client_secret': TEST_CLIENT_SECRET,
        })
        self.env.oauth.requests[0].assert_query_contains({
            'device_id': TEST_DEVICE_ID,
            'device_name': TEST_DEVICE_NAME,
        })

    def check_blackbox_called(self, login=TEST_MAILISH_LOWER_ID):
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'sid': 'mailish',
            'login': login,
            'emails': 'getall',
            'getemails': 'all',
            'email_attributes': 'all',
        })

    def test_rate_limit_error_on_register(self):
        counter = register_mailish.get_per_consumer_counter()
        for _ in range(5):
            counter.incr(TEST_CONSUMER)
        rv = self.make_request()
        self.assert_error_response(rv, ['rate.limit_exceeded'])

    def test_rate_limit_error_on_updating_email(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_UID,
                    login=TEST_EMAIL_NORMALIZED,
                    aliases={
                        'mailish': TEST_EMAIL_NORMALIZED,
                    },
                ),
            ],
        )
        counter = register_mailish.get_per_consumer_counter()
        for _ in range(5):
            counter.incr(TEST_CONSUMER)
        rv = self.make_request()
        self.assert_error_response(rv, ['rate.limit_exceeded'])

    def test_rate_limit_ok(self):
        counter = register_mailish.get_per_consumer_counter()
        for _ in range(4):
            counter.incr(TEST_CONSUMER)
        rv = self.make_request()
        self.check_response_ok(rv, is_new_account=True)

    def test_register_account_ok(self):
        rv = self.make_request()

        self.check_response_ok(rv, is_new_account=True)
        self.check_db_ok()
        self.check_historydb_ok()
        self.check_statbox(
            registered=True,
            rpop_added=True,
            token_created=True,
        )
        self.check_oauth_ok()
        self.check_blackbox_called()

    def test_get_and_finalize__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_MAILISH_ID,
                aliases={
                    'mailish': TEST_MAILISH_ID,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                attributes={
                    'account.default_email': TEST_YNDX_EMAIL,
                },
            ),
        )
        rv = self.make_request()

        self.check_response_ok(rv, is_new_account=False)
        self.check_historydb_ok(account_created=False)
        self.check_statbox(
            registered=False,
            rpop_added=True,
            token_created=True,
            previous_display_name='p:%s' % TEST_DISPLAY_NAME,
        )
        self.check_oauth_ok()
        self.check_blackbox_called()

    def test_get_finalized__ok(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_UID,
                    login=TEST_MAILISH_LOWER_ID,
                    aliases={
                        'mailish': TEST_MAILISH_LOWER_ID,
                    },
                    emails=[
                        self.create_validated_external_email(*TEST_EMAIL_NORMALIZED.split('@'), rpop=True),
                    ],
                ),
            ],
        )
        rv = self.make_request()

        self.check_response_ok(rv, is_new_account=False)
        self.check_historydb_ok(
            account_created=False,
            email_created=False,
        )
        self.check_statbox(registered=False, rpop_added=False, token_created=True)
        self.check_oauth_ok()
        self.check_blackbox_called()

    def test_base_grant_insufficient__error(self):
        self.env.grants.set_grants_return_value(mock_grants(
            grants={
                'account': [
                    'get_or_create_mailish.base',
                ],
            },
        ))

        rv = self.make_request()

        self.assert_error_response(
            rv,
            error_codes=['access.denied'],
            status_code=403,
        )

    def test_special_login__ok(self):
        self.env.grants.set_grants_return_value(mock_grants(
            grants={
                'account': [
                    'get_or_create_mailish.base',
                ],
            },
        ))

        rv = self.make_request(query_args=dict(email=TEST_YNDX_EMAIL))

        self.check_response_ok(rv, is_new_account=True)

    def test_invalid_oauth_credentials__error(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'status': 'error',
                'error': 'invalid_client',
                'error_description': 'Wrong client secret',
            },
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_codes=['oauth.client_auth_invalid'],
        )
        self.check_statbox(
            registered=True,
            rpop_added=True,
            token_created=False,
        )
        self.check_blackbox_called()

    def test_task_id_invalid__error(self):
        self.env.social_broker.set_response_side_effect(
            'check_pkce',
            SocialBrokerInvalidTaskIdError,
        )

        rv = self.make_request(query_args=dict(task_id=TEST_TASK_ID, code_verifier=TEST_CODE_VERIFIER))

        self.assert_error_response(rv, error_codes=['task_id.invalid'])

    def test_task_not_found__error(self):
        self.env.social_broker.set_response_side_effect(
            'check_pkce',
            SocialBrokerTaskNotFoundError,
        )

        rv = self.make_request(query_args=dict(task_id=TEST_TASK_ID, code_verifier=TEST_CODE_VERIFIER))

        self.assert_error_response(rv, error_codes=['task.not_found'])

    def test_check_pkce__ok(self):
        self.env.social_broker.set_response_value(
            'check_pkce',
            check_pkce_ok_response(),
        )

        rv = self.make_request(query_args=dict(task_id=TEST_TASK_ID, code_verifier=TEST_CODE_VERIFIER))

        self.check_response_ok(rv, is_new_account=True)

    def test_check_pkce__error(self):
        self.env.social_broker.set_response_side_effect(
            'check_pkce',
            SocialBrokerInvalidPkceVerifierError,
        )

        rv = self.make_request(query_args=dict(task_id=TEST_TASK_ID, code_verifier=TEST_CODE_VERIFIER))

        self.assert_error_response(rv, error_codes=['pkce.invalid'])

    def test_email_native__error(self):
        rv = self.make_request(query_args=dict(email=TEST_NATIVE_EMAIL))

        self.assert_error_response(rv, error_codes=['email.native'])

    def test_native_emails_allowed__ok(self):
        with settings_context(ALLOW_NATIVE_MAILISH_EMAILS=True):
            rv = self.make_request(query_args=dict(email=TEST_NATIVE_EMAIL))

        self.check_response_ok(rv, is_new_account=True)
