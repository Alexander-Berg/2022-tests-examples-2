# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_OAUTH_TOKEN_TTL,
    TEST_OAUTH_X_TOKEN,
    TEST_OAUTH_X_TOKEN_TTL,
    TEST_PUBLIC_ID,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_COUNTRY_CODE,
    TEST_OAUTH_TOKEN,
    TEST_PHONE_ID3,
    TEST_PHONISH_LOGIN1,
    TEST_PHONISH_LOGIN2,
    TEST_UID,
    TEST_UID2,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_generate_public_id_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import lastauth_response
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_phone,
)
from passport.backend.core.models.phones.faker import (
    assert_simple_phone_bound,
    build_phone_bound,
)
from passport.backend.core.test.events import EventCompositor
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
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge


TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_USER_IP = '37.9.101.188'
TEST_AVATAR_SIZE = 'islands-75'
TEST_AVATAR_URL = TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE)
TEST_TIME1 = datetime(2015, 1, 2, 5, 1, 5)
TEST_RECENT_ACCOUNT_USAGE_PERIOD = timedelta(days=10)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
    DEFAULT_AVATAR_KEY=TEST_AVATAR_KEY,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    RECENT_ACCOUNT_USAGE_PERIOD=TEST_RECENT_ACCOUNT_USAGE_PERIOD,
    PERIOD_OF_PHONE_NUMBER_LOYALTY=timedelta(365),
    TOKEN_REISSUE_INTERVAL=60,
    APP_ID_TO_PHONISH_NAMESPACE={'app_id2': 'space2'},
    IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=True,
    **mock_counters(
        SMS_PER_PHONE_ON_REGISTRATION_LIMIT_COUNTER=(24, 3600, 5),
        REGISTRATION_COMPLETED_WITH_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class RegisterPhonishViewTestCase(BaseBundleTestViews, StatboxTestMixin):
    default_url = '/1/bundle/mobile/register/phonish/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()

        login_mock = mock.Mock()
        login_mock.return_value = TEST_PHONISH_LOGIN1
        self.env.patches.append(mock.patch('passport.backend.core.types.login.login.generate_phonish_login', login_mock))
        self.env.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = {'track_id': self.track_id}
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['register_phonish']},
            ),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            (
                {
                    'access_token': TEST_OAUTH_X_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_X_TOKEN_TTL,
                },
                {
                    'access_token': TEST_OAUTH_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_TOKEN_TTL,
                },
            ),
        )
        self.setup_track()
        self.setup_blackbox()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register_phonish',
            type='mobile',
            ip=TEST_USER_IP,
            user_agent='-',
            track_id=self.track_id,
            consumer='dev',
        )
        super(RegisterPhonishViewTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['submitted'],
            _exclude=['user_agent'],
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _inherit_from=['subscriptions'],
            _exclude=['track_id', 'type', 'mode'],
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification'],
            _exclude=['old', 'mode'],
            operation='created',
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'login_phonish',
            _exclude=['user_agent'],
            action='login_phonish',
            phone_id=str(TEST_PHONE_ID3),
            phone_number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'tokens_issued',
            _exclude=['user_agent'],
            action='tokens_issued',
            uid=str(TEST_UID),
            login=TEST_PHONISH_LOGIN1,
            password_passed='0',
            x_token_client_id=TEST_X_TOKEN_CLIENT_ID,
            x_token_issued='1',
            client_id=TEST_CLIENT_ID,
            client_token_issued='1',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            cloud_token=TEST_CLOUD_TOKEN,
        )

    def setup_track(self, confirmed=True, number=TEST_PHONE_NUMBER.e164, country=TEST_COUNTRY_CODE,
                    registered=False, token_created_at=None, uid=None, allow_create_tokens=True, app_id=None):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.user_entered_login = TEST_PHONISH_LOGIN1
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.avatar_size = TEST_AVATAR_SIZE
            track.device_application = app_id
            track.cloud_token = TEST_CLOUD_TOKEN

            track.phone_confirmation_is_confirmed = confirmed
            track.phone_confirmation_phone_number = number
            track.country = country
            track.is_successful_registered = registered
            track.oauth_token_created_at = token_created_at
            track.allow_oauth_authorization = allow_create_tokens
            if uid:
                track.uid = uid

    def setup_blackbox(self, uid=None, **userinfo_kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN1: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=uid, **userinfo_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
        )

    def build_account(
        self,
        uid=TEST_UID,
        login=TEST_PHONISH_LOGIN1,
        is_disabled=False,
        namespace=None,
        phone_number=None,
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        bound_at = datetime.now() - timedelta(days=30)
        confirmed_at = datetime.now() - timedelta(days=29)

        attributes = {}
        if is_disabled:
            attributes['account.is_disabled'] = '1'
        if namespace is not None:
            attributes['account.phonish_namespace'] = namespace
        account = {
            'userinfo': deep_merge(
                {
                    'uid': uid,
                    'login': login,
                    'aliases': {
                        'phonish': login,
                    },
                    'attributes': attributes,
                    'display_name': {
                        'name': phone_number.e164,
                    },
                    'default_avatar_key': TEST_AVATAR_KEY,
                    'is_avatar_empty': True,
                    'firstname': None,
                    'lastname': None,
                    'birthdate': None,
                    'gender': None,
                    'public_id': TEST_PUBLIC_ID,
                },
                build_phone_bound(
                    phone_id=TEST_PHONE_ID3,
                    phone_number=phone_number.e164,
                    phone_created=bound_at,
                    phone_bound=bound_at,
                    phone_confirmed=confirmed_at,
                    binding_flags=binding_flags,
                ),
            ),
            'lastauth': time() - 3600,
        }
        return account

    def build_statbox_compositor(self):
        def e(event, **kwargs):
            e.lines.append(self.env.statbox.entry(event, **kwargs))
        e.lines = list()
        return e

    def setup_multiple_accounts(self, accounts, phone_number=TEST_PHONE_NUMBER.e164):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([a['userinfo'] for a in accounts]),
        )
        for account in accounts:
            userinfo_kwargs = account['userinfo']
            userinfo_response = blackbox_userinfo_response(**userinfo_kwargs)
            self.env.db.serialize(userinfo_response)

        phone_bindings = []
        for account in accounts:
            account_bindings = account['userinfo'].get('phone_bindings', [])
            for binding in account_bindings:
                if binding['number'] == phone_number:
                    phone_bindings.append(
                        dict(
                            binding,
                            uid=account['userinfo']['uid'],
                        ),
                    )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [lastauth_response(timestamp=a['lastauth']) for a in accounts],
        )

    def assert_track_ok(self, login=TEST_PHONISH_LOGIN1):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.user_entered_login, login)
        ok_(track.is_successful_registered)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

    def assert_db_ok(
        self,
        centraldb_queries=3,
        sharddb_queries=4,
        login=TEST_PHONISH_LOGIN1,
        namespace=None,
        number=None,
    ):
        timenow = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'phonish', login, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=TEST_UID, db='passportdbshard1')
        if namespace is not None:
            self.env.db.check('attributes', 'account.phonish_namespace', namespace, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'account.phonish_namespace', uid=TEST_UID, db='passportdbshard1')

        self.assert_db_phone_ok(number=number)

    def assert_db_phone_ok(
        self,
        number=None,
        phone_id=None,
    ):
        if phone_id is None:
            phone_id = 1

        if number is None:
            number = TEST_PHONE_NUMBER.e164

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': phone_id,
                'number': number,
                'confirmed': DatetimeNow(),
            },
            binding_flags=binding_flags,
        )

    def assert_db_account_global_logout(self):
        self.env.db.check_db_attr(
            TEST_UID,
            'account.global_logout_datetime',
            TimeNow(),
        )

    def assert_historydb_ok(self, login=TEST_PHONISH_LOGIN1, namespace=None):
        timenow = TimeNow()
        events = {
            'action': 'account_register',
            'consumer': 'dev',
            'info.login': login,
            'info.ena': '1',
            'info.disabled_status': '0',
            'info.tz': 'Europe/Moscow',
            'info.lang': 'ru',
            'info.country': 'ru',
            'info.reg_date': DatetimeNow(convert_to_datetime=True),
            'sid.add': ','.join(['|'.join(['8', login]), '|'.join(['68', login])]),
            'alias.phonish.add': login,
            'info.karma': '0',
            'info.karma_prefix': '0',
            'info.karma_full': '0',
            'phone.1.action': 'created',
            'phone.1.number': TEST_PHONE_NUMBER.e164,
            'phone.1.created': timenow,
            'phone.1.confirmed': timenow,
            'phone.1.bound': timenow,
        }
        if namespace is not None:
            events['info.phonish_namespace'] = namespace
        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )

    def assert_statbox_ok(self, login=TEST_PHONISH_LOGIN1, **device_info_kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='account.disabled_status',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'track_id'],
                operation='added',
                entity='aliases',
                type='10',
                value=login,
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='person.language',
                new='ru',
                old='-',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='person.country',
                new='ru',
                old='-',
            ),
            self.env.statbox.entry(
                'account_register',
                _exclude=['track_id', 'type'],
                login=login,
                suid='-',
                user_agent='-',
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='8',
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='68',
            ),
            self.env.statbox.entry(
                'account_created',
                _exclude={
                    'is_suggested_login',
                    'karma',
                    'language',
                    'password_quality',
                    'suggest_generation_number',
                    'user_agent',
                },
                login=login,
                consumer='dev',
            ),
            self.env.statbox.entry('phone_confirmed', _exclude=['user_agent'], consumer='dev'),
            self.env.statbox.entry(
                'simple_phone_bound',
                _exclude=['operation_id', 'user_agent'],
                mode='register_phonish',
                type='mobile',
                number=TEST_PHONE_NUMBER.masked_format_for_statbox,
                track_id=self.track_id,
                ip=TEST_USER_IP,
            ),
            self.env.statbox.entry('tokens_issued', **device_info_kwargs),
        ])

    def assert_oauth_ok(self, count=2):
        eq_(len(self.env.oauth.requests), count)

    def assert_blackbox_phone_bindings_request_ok(self, request, phone_numbers=None):
        if phone_numbers is None:
            phone_numbers = [TEST_PHONE_NUMBER.e164]
        self.env.blackbox.requests[0].assert_query_equals(
            dict(
                format='json',
                method='phone_bindings',
                numbers=','.join(phone_numbers),
                type='current',
            ),
        )

    def default_response(self, **kwargs):
        return dict(
            {
                'uid': TEST_UID,
                'display_name': TEST_PHONE_NUMBER.e164,
                'primary_alias_type': 10,
                'avatar_url': TEST_AVATAR_URL,
                'is_avatar_empty': True,
                'cloud_token': TEST_CLOUD_TOKEN,
                'x_token': TEST_OAUTH_X_TOKEN,
                'x_token_expires_in': TEST_OAUTH_X_TOKEN_TTL,
                'x_token_issued_at': TimeNow(),
                'access_token': TEST_OAUTH_TOKEN,
                'access_token_expires_in': TEST_OAUTH_TOKEN_TTL,
                'public_id': TEST_PUBLIC_ID,
            },
            **kwargs
        )

    def test_without_required_headers__error(self):
        rv = self.make_request(exclude_headers=self.http_headers)
        self.assert_error_response(rv, ['ip.empty'])

    def test_already_registered__error(self):
        self.setup_track(registered=True, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])
        self.env.statbox.assert_has_written([])

    def test_not_registered_for_tokens(self):
        self.setup_track(registered=False, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_user_not_confirmed__error(self):
        self.setup_track(confirmed=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])
        self.env.statbox.assert_has_written([])

    def test_invalid_track_state__error(self):
        self.setup_track(number=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_register_ip_limit_exceeded__error(self):
        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        for _ in range(counter.limit + 1):
            counter.incr(TEST_USER_IP)

        rv = self.make_request()
        self.assert_error_response(rv, ['account.registration_limited'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'registration_with_sms_error',
                _exclude=['type', 'consumer'],
                counter_current_value=str(counter.limit + 1),
                counter_limit_value=str(counter.limit),
                mode='mobile_register_phonish',
            ),
        ])

    def test_register_phone_limit_exceeded__error(self):
        counter = sms_per_phone.get_per_phone_on_registration_buckets()
        for _ in range(counter.limit + 1):
            counter.incr(TEST_PHONE_NUMBER.e164)

        rv = self.make_request()
        self.assert_error_response(rv, ['account.registration_limited'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'registration_with_sms_error',
                _exclude=['type', 'consumer', 'ip', 'is_special_testing_ip'],
                counter_current_value=str(counter.limit + 1),
                counter_limit_value=str(counter.limit),
                mode='mobile_register_phonish',
                is_phonish='0',
                error='registration_sms_per_phone_limit_has_exceeded',
                counter_prefix='registration:sms:phone',
            ),
        ])

    def test__ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_ok()
        self.env.social_binding_logger.assert_has_written([])

    def test_oauth_unavailable__error(self):
        self.env.oauth.set_response_side_effect(
            '_token',
            OAuthTemporaryError(),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['backend.oauth_failed'],
        )

    def test_take_tokens_and_run__ok(self):
        self.setup_track(registered=True, uid=TEST_UID)
        accounts = [
            self.build_account(),
        ]
        self.setup_multiple_accounts(accounts)

        rv = self.make_request()
        self.assert_ok_response(rv, **self.default_response(public_name=TEST_PHONE_NUMBER.e164))
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('tokens_issued'),
        ])
        self.assert_oauth_ok()
        self.assert_track_ok()

    def test_retrying_for_tokens__ok(self):
        self.setup_track(registered=True, uid=TEST_UID, token_created_at=time() - 1)
        accounts = [
            self.build_account(),
        ]
        self.setup_multiple_accounts(accounts)

        rv = self.make_request()
        self.assert_ok_response(rv, **self.default_response(public_name=TEST_PHONE_NUMBER.e164))
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('tokens_issued'),
        ])
        self.assert_oauth_ok()
        self.assert_track_ok()

    def test_disabled_account__error(self):
        accounts = [
            self.build_account(is_disabled=True),
        ]
        self.setup_multiple_accounts(accounts)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'])

    def test_with_existing_phonish_account__ok(self):
        accounts = [
            self.build_account(),
        ]
        self.setup_multiple_accounts(accounts)
        rv = self.make_request()
        self.assert_ok_response(rv, **self.default_response(public_name=TEST_PHONE_NUMBER.e164))
        self.env.db.check_query_counts(shard=2)

        self.assert_db_phone_ok(phone_id=TEST_PHONE_ID3)
        self.assert_db_account_global_logout()
        self.env.event_logger.assert_events_are_logged({
            'action': 'login_phonish',
            'info.glogout': TimeNow(),
            'phone.3.action': 'changed',
            'phone.3.number': TEST_PHONE_NUMBER.e164,
            'phone.3.confirmed': TimeNow(),
            'consumer': 'dev',
        })

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('global_logout', ip=TEST_USER_IP, user_agent='-'),
            self.env.statbox.entry('login_phonish'),
            self.env.statbox.entry('tokens_issued'),
        ])

    def test_with_existing_phonish_account_and_custom_namespace__ok(self):
        accounts = [
            self.build_account(namespace='space2'),
        ]
        self.setup_multiple_accounts(accounts)
        self.setup_track(app_id='app_id2')
        rv = self.make_request()
        self.assert_ok_response(rv, **self.default_response(public_name=TEST_PHONE_NUMBER.e164))
        self.env.db.check_query_counts(shard=2)

        self.assert_db_phone_ok(phone_id=TEST_PHONE_ID3)
        self.assert_db_account_global_logout()
        self.env.event_logger.assert_events_are_logged({
            'action': 'login_phonish',
            'info.glogout': TimeNow(),
            'phone.3.action': 'changed',
            'phone.3.number': TEST_PHONE_NUMBER.e164,
            'phone.3.confirmed': TimeNow(),
            'consumer': 'dev',
        })

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('global_logout', ip=TEST_USER_IP, user_agent='-'),
            self.env.statbox.entry('login_phonish'),
            self.env.statbox.entry('tokens_issued', app_id='app_id2'),
        ])

    def test_existing_phonish_account_from_other_namespace_not_reused__ok(self):
        accounts = [
            self.build_account(uid=TEST_UID2, login=TEST_PHONISH_LOGIN2),
        ]
        self.setup_multiple_accounts(accounts)
        self.setup_track(app_id='app_id2')
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok(namespace='space2')
        self.assert_historydb_ok(namespace='space2')
        self.assert_statbox_ok(app_id='app_id2')
        self.assert_oauth_ok()

    def test_no_uid_for_tokens(self):
        self.setup_track(registered=True)

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_blacklisted_ip(self):
        with mock.patch(
            'passport.backend.api.common.ip.is_ip_blacklisted',
            return_value=True,
        ):
            rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])

    def test_find_phonish_by_new_ivory_coast_phone(self):
        self.check_find_phonish_by_ivory_coast_phone(
            account_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_find_phonish_by_old_ivory_coast_phone(self):
        self.check_find_phonish_by_ivory_coast_phone(
            account_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_find_phonish_by_ivory_coast_phone(self, account_phone_number, user_entered_phone_number):
        """
        Проверяем, что если к фонишу привязан старый (новый) телефон
        Кот-Д'Ивуара, а пользователь входит по новому (старому) телефону, то
        его логинит в существующий аккаунт.
        """
        account = self.build_account()
        userinfo = account['userinfo']
        userinfo['display_name']['name'] = account_phone_number.e164
        userinfo['phone_bindings'][0]['number'] = account_phone_number.e164
        userinfo['phones'][0]['number'] = account_phone_number.e164

        self.setup_multiple_accounts(
            accounts=[account],
            phone_number=account_phone_number.e164,
        )

        self.setup_track(number=user_entered_phone_number.e164)

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response(
                display_name=account_phone_number.e164,
                public_name=account_phone_number.e164,
            )
        )

        self.assert_blackbox_phone_bindings_request_ok(
            self.env.blackbox.requests[0],
            phone_numbers=[user_entered_phone_number.e164, account_phone_number.e164],
        )

        self.assert_db_phone_ok(number=account_phone_number.e164, phone_id=TEST_PHONE_ID3)
        self.assert_db_account_global_logout()

        e = EventCompositor()
        e('action', 'login_phonish')
        e('info.glogout', TimeNow())
        with e.prefix('phone.3.'):
            e('action', 'changed')
            e('number', account_phone_number.e164)
            e('confirmed', TimeNow())
        e('consumer', 'dev')
        self.env.event_logger.assert_events_are_logged(e.to_lines())

        e = self.build_statbox_compositor()
        e('submitted')
        e('global_logout', ip=TEST_USER_IP, user_agent='-')
        e('login_phonish', phone_number=account_phone_number.masked_format_for_statbox)
        e('tokens_issued')
        self.env.statbox.assert_has_written(e.lines)

    def test_new_ivory_coast_phonish_with_deprecated_8_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_ivory_coast_phonish_with_10_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def check_new_ivory_coast_phonish_always_has_10_digits_phone(self, user_entered_phone_number):
        """
        Проверяем, что новые фониши из Кот-Д'Ивуара регистрируются с новым
        номером, даже если пользователь вводит старый.
        """
        self.setup_track(number=user_entered_phone_number.e164)

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response(
                display_name=user_entered_phone_number.e164,
            )
        )
        self.assert_db_ok(number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164)

    def test_new_ivory_coast_phonish_with_not_deprecated_8_digits_phone(self):
        self.setup_track(number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164)

        with settings_context(
            DEFAULT_AVATAR_KEY=TEST_AVATAR_KEY,
            GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
            IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=False,
        ):
            rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response(
                display_name=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
            )
        )
        self.assert_db_ok(number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164)
