# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    make_clean_web_test_mixin,
    ProfileTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_ANOTHER_NON_NATIVE_EMAIL,
    TEST_EMAIL,
    TEST_NON_NATIVE_EMAIL,
    TEST_SERIALIZED_PASSWORD,
    TEST_SHORT_CODE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COUNTRY,
    TEST_USER_FIRSTNAME,
    TEST_USER_IP,
    TEST_USER_LASTNAME,
    TEST_USER_PASSWORD,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
)
from passport.backend.core.counters import register_email_per_email
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.test.consts import (
    TEST_FIRSTNAME1,
    TEST_LASTNAME1,
    TEST_PROCESS_UUID1,
)
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
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
from passport.backend.utils.time import get_unixtime


TEST_IP = '123.123.123.123'
TEST_YANDEXUID = 'yuid12345'
TEST_VERSION = 1
TEST_ALLOWED_PROVIDER_CODE = 'wk'
TEST_ORIGIN = 'origin'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=5,
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=2,
    ALLOW_LITE_REGISTRATION=True,
    AUTH_ALLOWED_PROVIDERS=[TEST_ALLOWED_PROVIDER_CODE],
    **mock_counters()
)
class TestAccountRegisterLiteSubmit(BaseBundleTestViews, EmailTestMixin):
    track_type = 'register'
    default_url = '/1/bundle/account/register/lite/submit/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_mail'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)

        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.http_query_args = {
            'login': TEST_NON_NATIVE_EMAIL,
            'language': 'ru',
            'track_id': self.track_id,
        }

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.is_captcha_required = False

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NON_NATIVE_EMAIL: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='register_by_email',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            track_id=self.track_id,
            yandexuid=TEST_YANDEXUID,
        )
        self.env.statbox.bind_entry(
            'new_code',
            _inherit_from=['local_base'],
            action='new_code',
        )
        self.env.statbox.bind_entry(
            'send_email',
            _inherit_from=['local_base'],
            action='send_confirmation_email',
            confirmation_checks_count='0',
        )

    def tearDown(self):
        self.code_generator_faker.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.code_generator_faker

    def build_email(self, address, short_code, human_readable_address=None, language=TEST_ACCEPT_LANGUAGE):
        return {
            'language': language,
            'addresses': [address],
            'subject': 'emails.registration_confirmation_email_sent.subject',
            'SHORT_CODE': short_code,
            'tanker_keys': {
                'emails.registration_confirmation_email_sent.message': {
                    'ADDRESS': human_readable_address or address,
                },
                'emails.registration_confirmation_email_sent.short_code_age': {},
                'emails.registration_confirmation_email_sent.dont_worry': {},
            },
        }

    def check_email_sent(self,
                         address=TEST_NON_NATIVE_EMAIL,
                         human_readable_address=None,
                         short_code=TEST_SHORT_CODE):
        self.assert_emails_sent([
            self.build_email(
                address=address,
                human_readable_address=human_readable_address,
                short_code=short_code,
            ),
        ])

    def test_registration_disabled(self):
        with settings_context(ALLOW_LITE_REGISTRATION=False):
            rv = self.make_request()
        self.assert_error_response(rv, ['action.impossible'])

    def test_no_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = None
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'restore'
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_already_confirmed__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = get_unixtime()
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL

        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['email.already_confirmed'])

    def test_no_captcha_when_required(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
        rv = self.make_request()
        self.assert_error_response(rv, ['captcha.required'])

    def test_native_email_error(self):
        rv = self.make_request(query_args={'login': TEST_EMAIL})
        self.assert_error_response(rv, ['login.native'])

    def test_pdd_domain(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1),
        )

        rv = self.make_request(query_args={'email': TEST_NON_NATIVE_EMAIL})
        self.assert_error_response(rv, ['domain.invalid_type'])

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            code_required=True,
            email=TEST_NON_NATIVE_EMAIL,
        )

        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        ok_(not track.email_confirmation_passed_at)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])
        counter = register_email_per_email.get_counter()
        eq_(counter.get(TEST_NON_NATIVE_EMAIL), 1)

    def test_confirm_new_email(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = get_unixtime()
            track.email_confirmation_address = TEST_ANOTHER_NON_NATIVE_EMAIL
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_code = '123'

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            code_required=True,
            email=TEST_NON_NATIVE_EMAIL,
        )

        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        ok_(not track.email_confirmation_passed_at)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='1',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])
        counter = register_email_per_email.get_counter()
        eq_(counter.get(TEST_NON_NATIVE_EMAIL), 1)

    def test_no_login(self):
        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.empty'])

    def test_social_profile_with_confirmed_email(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                email=TEST_NON_NATIVE_EMAIL,
                firstname=TEST_FIRSTNAME1,
                lastname=TEST_LASTNAME1,
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
            )
            track.process_uuid = TEST_PROCESS_UUID1

        rv = self.make_request(exclude_args=['login'])

        self.assert_ok_response(
            rv,
            code_required=False,
            email=TEST_NON_NATIVE_EMAIL,
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            social_provider_code=TEST_ALLOWED_PROVIDER_CODE,
        )

        self.env.statbox.assert_has_written(list())
        self.assert_emails_sent(list())

        track = self.track_manager.read(self.track_id)
        ok_(not track.email_confirmation_passed_at)
        ok_(not track.email_confirmation_address)

    def test_social_profile_without_name(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                email=TEST_NON_NATIVE_EMAIL,
                firstname=None,
                lastname=None,
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
            )
            track.process_uuid = TEST_PROCESS_UUID1

        rv = self.make_request(exclude_args=['login'])

        self.assert_ok_response(
            rv,
            code_required=False,
            email=TEST_NON_NATIVE_EMAIL,
            social_provider_code=TEST_ALLOWED_PROVIDER_CODE,
        )

    def test_social_profile_with_confirmed_email_not_available(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
                email=TEST_NON_NATIVE_EMAIL,
            )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NON_NATIVE_EMAIL: 'occupied'}),
        )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.notavailable'])

    def test_social_profile_with_unconfirmed_email(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code='zz',
                email=TEST_NON_NATIVE_EMAIL,
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.empty'])

    def test_social_profile_with_invalid_email(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
                email='ya-ne-email',
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.invalid'])

    def test_social_profile_with_native_email(self):
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
                email='hello@yandex.ru',
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.native'])


@with_settings_hosts(
    AUTH_ALLOWED_PROVIDERS=[TEST_ALLOWED_PROVIDER_CODE],
    BLACKBOX_URL='localhost',
    FRODO_URL='http://localhost/',
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    SENDER_MAIL_SUBSCRIPTION_SERVICES=[
        {
            'id': 1,
            'origin_prefixes': [TEST_ORIGIN],
            'app_ids': [],
            'slug': None,
            'external_list_ids': [],
        },
        {
            'id': 2,
            'origin_prefixes': ['other'],
            'app_ids': [],
            'slug': None,
            'external_list_ids': [],
        },
    ],
    **mock_counters()
)
class TestAccountRegisterLiteCommit(BaseBundleTestViews,
                                    StatboxTestMixin,
                                    make_clean_web_test_mixin('test_successful_register', ['firstname', 'lastname']),
                                    ProfileTestMixin):
    track_type = 'register'
    default_url = '/1/bundle/account/register/lite/commit/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_require_confirmed_email'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)

        self.http_query_args = {
            'login': TEST_NON_NATIVE_EMAIL,
            'password': TEST_USER_PASSWORD,
            'firstname': TEST_USER_FIRSTNAME,
            'lastname': TEST_USER_LASTNAME,
            'language': TEST_ACCEPT_LANGUAGE,
            'country': TEST_USER_COUNTRY,
            'version': TEST_VERSION,
            'track_id': self.track_id,
            'eula_accepted': True,
        }

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NON_NATIVE_EMAIL: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        self.setup_track()
        self.patches = []
        self.setup_profile_patches()
        self.setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.teardown_profile_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches

    def setup_track(self, registered=False, confirmed=True, address=TEST_NON_NATIVE_EMAIL):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.is_successful_registered = registered
            track.email_confirmation_address = address
            track.email_confirmation_passed_at = get_unixtime() - 3600 if confirmed else None
            track.process_uuid = TEST_PROCESS_UUID1

    def check_db(self, with_password=True, unsubscribed_from_maillists=None):
        timenow = TimeNow()
        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 3)

        shard_params = dict(uid=TEST_UID, db='passportdbshard1')
        central_params = dict(uid=TEST_UID, db='passportdbcentral')

        self.env.db.check('aliases', 'lite', TEST_NON_NATIVE_EMAIL, **central_params)
        self.env.db.check_missing('attributes', 'account.user_defined_login', **shard_params)
        self.env.db.check('attributes', 'account.registration_datetime', timenow, **shard_params)

        if with_password:
            self.env.db.check('attributes', 'password.update_datetime', timenow, **shard_params)
            self.env.db.check('attributes', 'password.quality', '3:80', **shard_params)
            ok_(self.env.db.get('attributes', 'password.encrypted', **shard_params))
        else:
            self.env.db.check_missing('attributes', 'password.encrypted', **shard_params)

        self.env.db.check('attributes', 'person.firstname', TEST_USER_FIRSTNAME, **shard_params)
        self.env.db.check('attributes', 'person.lastname', TEST_USER_LASTNAME, **shard_params)
        self.env.db.check_missing('attributes', 'person.gender', **shard_params)
        self.env.db.check_missing('attributes', 'person.birthday', **shard_params)
        self.env.db.check_missing('attributes', 'person.timezone', **shard_params)
        self.env.db.check_missing('attributes', 'person.city', **shard_params)

        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'account.display_name', **shard_params)
        self.env.db.check_missing('attributes', 'account.is_disabled', **shard_params)

        self.env.db.check_missing('attributes', 'karma.value', **shard_params)

        if unsubscribed_from_maillists:
            self.env.db.check('attributes', 'account.unsubscribed_from_maillists', unsubscribed_from_maillists, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'account.unsubscribed_from_maillists', uid=TEST_UID, db='passportdbshard1')

        expected = [
            ('address', TEST_NON_NATIVE_EMAIL),
            ('created', TimeNow()),
            ('bound', TimeNow()),
            ('confirmed', TimeNow()),
        ]

        for attr, value in expected:
            self.env.db.check(
                'extended_attributes',
                'value',
                value,
                uid=1,
                type=EMAIL_NAME_MAPPING[attr],
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                db='passportdbshard1',
            )
        self.env.db.check(
            'email_bindings',
            'address',
            TEST_NON_NATIVE_EMAIL,
            uid=1,
            email_id=1,
            db='passportdbshard1',
        )

    def check_events(self, with_password=True, unsubscribed_from_maillists=None):
        timenow = TimeNow()
        expected = {
            'action': 'account_register_lite',
            'consumer': 'dev',
            'email.1.address': TEST_NON_NATIVE_EMAIL,
            'email.1': 'created',
            'email.1.bound_at': TimeNow(),
            'email.1.confirmed_at': TimeNow(),
            'email.1.created_at': TimeNow(),
            'email.1.is_unsafe': '0',
            'info.login': TEST_NON_NATIVE_EMAIL,
            'info.ena': '1',
            'info.disabled_status': '0',
            'info.firstname': TEST_USER_FIRSTNAME,
            'info.lastname': TEST_USER_LASTNAME,
            'info.country': 'ru',
            'info.lang': 'ru',
            'info.tz': 'Europe/Moscow',
            'info.reg_date': DatetimeNow(convert_to_datetime=True),
            'sid.add': '8|%s' % TEST_NON_NATIVE_EMAIL,
            'alias.lite.add': TEST_NON_NATIVE_EMAIL,
            'info.karma': '0',
            'info.karma_prefix': '0',
            'info.karma_full': '0',
            'user_agent': 'curl',
        }
        if with_password:
            eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
            expected.update(
                {
                    'info.password_quality': '80',
                    'info.password': eav_pass_hash,
                    'info.password_update_time': timenow,
                },
            )
        if unsubscribed_from_maillists:
            expected.update(
                {
                    'account.unsubscribed_from_maillists': unsubscribed_from_maillists,
                },
            )
        self.assert_events_are_logged(self.env.handle_mock, expected)

    def check_statbox(self, with_password=True, unsubscribed_from_maillists=None):
        entries = [
            self.env.statbox.entry(
                'submitted',
                mode='register_lite',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='created',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old'],
                entity='aliases',
                operation='added',
                value=TEST_NON_NATIVE_EMAIL,
                type='5',
            ),
            self.env.statbox.entry(
                'account_modification',
                bound_at=DatetimeNow(convert_to_datetime=True),
                confirmed_at=DatetimeNow(convert_to_datetime=True),
                created_at=DatetimeNow(convert_to_datetime=True),
                email_id='1',
                is_suitable_for_restore='1',
                is_unsafe='0',
                entity='account.emails',
                operation='added',
                new=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ]
        if unsubscribed_from_maillists:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='account.unsubscribed_from_maillists',
                    new=unsubscribed_from_maillists,
                ),
            )
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='person.firstname',
                new=TEST_USER_FIRSTNAME,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.lastname',
                new=TEST_USER_LASTNAME,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.language',
                new=TEST_ACCEPT_LANGUAGE,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.country',
                new=TEST_USER_COUNTRY,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.fullname',
                new='{} {}'.format(TEST_USER_FIRSTNAME, TEST_USER_LASTNAME),
            ),
        ])

        if with_password:
            entries.extend(
                [
                    self.env.statbox.entry(
                        'account_modification',
                        _exclude=['old'],
                        entity='password.encrypted',
                    ),
                    self.env.statbox.entry(
                        'account_modification',
                        entity='password.encoding_version',
                        new='6',
                    ),
                    self.env.statbox.entry(
                        'account_modification',
                        entity='password.quality',
                        new='80',
                    ),
                ]
            )

        entries.extend([
            self.env.statbox.entry(
                'account_register',
                action='account_register_lite',
                login=TEST_NON_NATIVE_EMAIL,
                suid='-',
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='8',
            ),
        ])

        exclude_from_entry = ['is_suggested_login', 'suggest_generation_number']
        if not with_password:
            exclude_from_entry.append('password_quality')
        entries.append(
            self.env.statbox.entry(
                'account_created',
                _exclude=exclude_from_entry,
                login=TEST_NON_NATIVE_EMAIL,
                mode='register_lite',
                process_uuid=TEST_PROCESS_UUID1,
            ),
        )

        self.env.statbox.assert_has_written(entries)

    def check_track(self, with_password=True):
        track = self.track_manager.read(self.track_id)
        ok_(track.is_successful_registered)
        eq_(track.user_entered_login, TEST_NON_NATIVE_EMAIL)
        ok_(track.is_password_passed is with_password)
        ok_(track.allow_authorization)
        ok_(not track.allow_oauth_authorization)

    def test_not_confirmed__error(self):
        self.setup_track(confirmed=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])

    def test_confirmed_different_address(self):
        self.setup_track(address=TEST_ANOTHER_NON_NATIVE_EMAIL)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])

    def test_already_registered__error(self):
        self.setup_track(registered=True)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])

    def test_eula_not_accepted__error(self):
        rv = self.make_request(query_args={'eula_accepted': '0'})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])

    def test_successful_register(self):
        rv = self.make_request()
        self.assert_ok_response(rv, uid=TEST_UID)
        self.check_db()
        self.check_events()
        self.check_statbox()
        self.check_track()

    def test_unsubscribe_from_maillists__known_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True, origin=TEST_ORIGIN))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.check_db(unsubscribed_from_maillists='1')
        self.check_events(unsubscribed_from_maillists='1')
        self.check_statbox(unsubscribed_from_maillists='1')

    def test_unsubscribe_from_maillists__no_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.check_db(unsubscribed_from_maillists='all')
        self.check_events(unsubscribed_from_maillists='all')
        self.check_statbox(unsubscribed_from_maillists='all')

    def test_unsubscribe_from_maillists__unknown_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True, origin='weird'))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.check_db(unsubscribed_from_maillists='all')
        self.check_events(unsubscribed_from_maillists='all')
        self.check_statbox(unsubscribed_from_maillists='all')

    def test_no_login(self):
        rv = self.make_request(exclude_args=['login'])
        self.assert_error_response(rv, ['login.empty'])

    def test_register_superlite_with_social_profile_email(self):
        self.setup_track(
            address=None,
            confirmed=False,
        )
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                email=TEST_NON_NATIVE_EMAIL,
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
            )

        rv = self.make_request(exclude_args=['login', 'password'])

        self.assert_ok_response(rv, uid=TEST_UID)
        self.check_db(with_password=False)
        self.check_events(with_password=False)
        self.check_statbox(with_password=False)
        self.check_track(with_password=False)

    def test_social_profile_email_not_available(self):
        self.setup_track(
            address=None,
            confirmed=False,
        )
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                email=TEST_NON_NATIVE_EMAIL,
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
            )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NON_NATIVE_EMAIL: 'occupied'}),
        )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.notavailable'])

    def test_social_profile_email_unconfirmed(self):
        self.setup_track(
            address=None,
            confirmed=False,
        )
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code='zz',
                email=TEST_NON_NATIVE_EMAIL,
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.empty'])

    def test_social_profile_email_invalid(self):
        self.setup_track(
            address=None,
            confirmed=False,
        )
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
                email='ya-ne-email',
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.invalid'])

    def test_social_profile_email_native(self):
        self.setup_track(
            address=None,
            confirmed=False,
        )
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
                email='hello@yandex.ru',
            )

        rv = self.make_request(exclude_args=['login'])

        self.assert_error_response(rv, ['login.native'])

    def test_unconfirmed_email_and_social_profile_email(self):
        self.setup_track(confirmed=False)
        with self.track_transaction() as track:
            track.social_task_data = self.env.social_broker.get_task_by_token_response(
                email=TEST_ANOTHER_NON_NATIVE_EMAIL,
                provider_code=TEST_ALLOWED_PROVIDER_CODE,
            )

        rv = self.make_request()

        self.assert_error_response(rv, ['user.not_verified'])


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    FRODO_URL='http://localhost/',
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CONFIRM_EMAIL_WITHOUT_CODE_ENABLED=False,
    CLEAN_WEB_API_ENABLED=False,
    **mock_counters()
)
class TestIntegrational(BaseBundleTestViews, EmailTestMixin, ProfileTestMixin):
    http_method = 'POST'
    track_type = 'register'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_mail', 'register_require_confirmed_email'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.is_captcha_required = False

        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NON_NATIVE_EMAIL: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        self.patches = []
        self.setup_profile_patches()

    def tearDown(self):
        self.teardown_profile_patches()
        for patch in reversed(self.patches):
            patch.stop()
        self.code_generator_faker.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self.track_manager
        del self.code_generator_faker

    def submit(self, code_required=True):
        url = '/1/bundle/account/register/lite/submit/?consumer=dev'
        query_args = {
            'login': TEST_NON_NATIVE_EMAIL,
            'language': 'ru',
            'track_id': self.track_id,
            'version': 1,
        }
        rv = self.make_request(url=url, query_args=query_args)

        self.assert_ok_response(
            rv,
            code_required=code_required,
            email=TEST_NON_NATIVE_EMAIL,
        )

        track = self.track_manager.read(self.track_id)

        if code_required:
            ok_(track.email_confirmation_checks_count.get() is None)
            ok_(not track.email_confirmation_passed_at)
            eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
            eq_(track.email_confirmation_code, TEST_SHORT_CODE)
        else:
            ok_(bool(track.email_confirmation_passed_at))
            ok_(not track.email_confirmation_code, TEST_SHORT_CODE)

    def confirm(self):
        url = '/1/bundle/account/register/confirm_email/by_code/?consumer=dev'
        query_args = {
            'key': TEST_SHORT_CODE,
            'track_id': self.track_id,
        }
        rv = self.make_request(url=url, query_args=query_args)
        self.assert_ok_response(rv)

        track = self.track_manager.read(self.track_id)
        eq_(track.email_confirmation_checks_count.get(), 1)
        ok_(bool(track.email_confirmation_passed_at))

    def commit(self):
        url = '/1/bundle/account/register/lite/commit/?consumer=dev'
        query_args = {
            'login': TEST_NON_NATIVE_EMAIL,
            'password': TEST_USER_PASSWORD,
            'firstname': TEST_USER_FIRSTNAME,
            'lastname': TEST_USER_LASTNAME,
            'language': TEST_ACCEPT_LANGUAGE,
            'country': TEST_USER_COUNTRY,
            'track_id': self.track_id,
            'eula_accepted': True,
        }
        rv = self.make_request(url=url, query_args=query_args)
        self.assert_ok_response(rv, uid=TEST_UID)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_successful_registered)
        eq_(track.user_entered_login, TEST_NON_NATIVE_EMAIL)
        ok_(track.is_password_passed)
        ok_(track.allow_authorization)
        ok_(not track.allow_oauth_authorization)

    def test_with_sending_email(self):
        self.submit()
        self.confirm()
        self.commit()

    def test_without_sending_email(self):
        with settings_context(
                CONFIRM_EMAIL_WITHOUT_CODE_ENABLED=True,
                CLEAN_WEB_API_ENABLED=False,
        ):
            self.submit(code_required=False)
            self.commit()
