# -*- coding: utf-8 -*-
import json
from time import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    make_clean_web_test_mixin,
    ProfileTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_APP,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_MAIL_SUBSCRIPTION_SERVICES,
    TEST_OAUTH_TOKEN_TTL,
    TEST_OAUTH_X_TOKEN,
    TEST_OAUTH_X_TOKEN_TTL,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_COUNTRY_CODE,
    TEST_DISPLAY_NAME,
    TEST_FIRSTNAME,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PASSWORD,
    TEST_PHONE_ID1,
    TEST_PUBLIC_ID,
    TEST_SERIALIZED_PASSWORD,
    TEST_SUID,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_generate_public_id_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_phone,
)
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_phonenumber_alias_missing,
    assert_secure_phone_bound,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.login.login import normalize_login
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_PWD_LOGIN = 'Kl44tuNikt0'
TEST_USER_IP = '37.9.101.188'
TEST_AVATAR_URL = TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_URL='http://localhost',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
    DEFAULT_AVATAR_KEY=TEST_AVATAR_KEY,
    TOKEN_REISSUE_INTERVAL=60,
    CLEAN_WEB_API_ENABLED=False,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_DEVICE_APP},
    SENDER_MAIL_SUBSCRIPTION_SERVICES=TEST_MAIL_SUBSCRIPTION_SERVICES,
    **mock_counters(
        SMS_PER_PHONE_ON_REGISTRATION_LIMIT_COUNTER=(24, 3600, 5),
        REGISTRATION_COMPLETED_WITH_SMS_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class MobileRegisterViewTestCase(BaseBundleTestViews,
                                 StatboxTestMixin,
                                 ProfileTestMixin,
                                 make_clean_web_test_mixin('test__ok', ['firstname', 'lastname'], statbox_action='phone_confirmed'),
                                 EmailTestMixin):
    default_url = '/1/bundle/mobile/register/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
        'login': TEST_LOGIN,
        'password': TEST_PASSWORD,
        'firstname': TEST_FIRSTNAME,
        'lastname': TEST_LASTNAME,
        'eula_accepted': True,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args.update(track_id=self.track_id)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['register']},
            ),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')
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
        self.patches = []

        self.setup_track()
        self.setup_blackbox()
        self.setup_shakur()
        self.setup_statbox_templates()
        self.setup_profile_patches()

    def tearDown(self):
        self.teardown_profile_patches()
        for p in reversed(self.patches):
            p.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register',
            type='mobile',
            ip=TEST_USER_IP,
            user_agent='-',
            track_id=self.track_id,
            consumer='dev',
        )
        super(MobileRegisterViewTestCase, self).setup_statbox_templates()
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
            'phonenumber_alias_added',
            _inherit_from=['phonenumber_alias_added'],
            _exclude=['track_id', 'mode'],
            type='11',
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'password_validation_error',
            _exclude=['ip', 'mode', 'user_agent', 'type', 'consumer'],
            action='password_validation_error',
            policy='basic',
        )
        self.env.statbox.bind_entry(
            'tokens_issued',
            _exclude=['user_agent'],
            action='tokens_issued',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
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
                    registered=False, token_created_at=None, allow_create_tokens=True, uid=None, app_id=TEST_DEVICE_APP):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.user_entered_login = TEST_LOGIN
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_application = app_id
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.language = TEST_LANGUAGE
            track.country = TEST_COUNTRY_CODE

            track.phone_confirmation_is_confirmed = confirmed
            track.phone_confirmation_phone_number = number
            track.country = country
            track.is_successful_registered = registered
            track.oauth_token_created_at = token_created_at
            track.allow_oauth_authorization = allow_create_tokens
            if uid:
                track.uid = uid

    def setup_blackbox(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
        )

    def setup_shakur(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def assert_track_ok(self, login=TEST_LOGIN):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.user_entered_login, login)
        ok_(track.is_successful_registered)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

    def assert_db_ok(self, centraldb_queries=5, sharddb_queries=6,
                     login=TEST_LOGIN, pwd_quality=80, phonenumber_alias_given_out=True,
                     unsubscribed_from_maillists=None):
        timenow = TimeNow()
        dtnow = DatetimeNow()

        norm_login = normalize_login(login)

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'portal', norm_login, uid=TEST_UID, db='passportdbcentral')

        if phonenumber_alias_given_out:
            assert_account_has_phonenumber_alias(self.env.db, TEST_UID, TEST_PHONE_NUMBER.digital, enable_search=False)
        else:
            assert_phonenumber_alias_missing(self.env.db, TEST_UID)

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:%s' % str(pwd_quality), uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', TEST_FIRSTNAME, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', TEST_LASTNAME, uid=TEST_UID, db='passportdbshard1')

        if unsubscribed_from_maillists:
            self.env.db.check('attributes', 'account.unsubscribed_from_maillists', unsubscribed_from_maillists, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'account.unsubscribed_from_maillists', uid=TEST_UID, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'karma.value', uid=TEST_UID, db='passportdbshard1')

        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': TEST_PHONE_NUMBER.e164,
                'created': dtnow,
                'bound': dtnow,
                'confirmed': dtnow,
                'secured': dtnow,
            },
        )

    def assert_historydb_ok(self, login=TEST_LOGIN, pwd_quality=80, phonenumber_alias_given_out=True,
                            unsubscribed_from_maillists=None):
        timenow = TimeNow()
        norm_login = normalize_login(login)

        events = [
            {'name': 'info.login', 'value': norm_login, 'uid': str(TEST_UID)},
            {'name': 'info.ena', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'info.disabled_status', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True), 'uid': str(TEST_UID)},
            {'name': 'info.firstname', 'value': TEST_FIRSTNAME, 'uid': str(TEST_UID)},
            {'name': 'info.lastname', 'value': TEST_LASTNAME, 'uid': str(TEST_UID)},
            {'name': 'info.country', 'value': TEST_COUNTRY_CODE, 'uid': str(TEST_UID)},
            {'name': 'info.tz', 'value': 'Europe/Moscow', 'uid': str(TEST_UID)},
            {'name': 'info.lang', 'value': TEST_LANGUAGE, 'uid': str(TEST_UID)},
            {'name': 'info.password', 'value': self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1'), 'uid': str(TEST_UID)},
            {'name': 'info.password_quality', 'value': str(pwd_quality), 'uid': str(TEST_UID)},
            {'name': 'info.password_update_time', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'info.karma_prefix', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma_full', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'alias.portal.add', 'value': norm_login, 'uid': str(TEST_UID)},
        ]
        if phonenumber_alias_given_out:
            events.extend([
                {'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER.international, 'uid': str(TEST_UID)},
                {'name': 'info.phonenumber_alias_search_enabled', 'value': '0', 'uid': str(TEST_UID)},
            ])
        events.extend([
            {'name': 'mail.add', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'info.mail_status', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'sid.add', 'value': '8|%s,2' % login, 'uid': str(TEST_UID)},
            {'name': 'phone.1.action', 'value': 'created', 'uid': str(TEST_UID)},
            {'name': 'phone.1.bound', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.confirmed', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.created', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164, 'uid': str(TEST_UID)},
            {'name': 'phone.1.secured', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phones.secure', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'action', 'value': 'account_register', 'uid': str(TEST_UID)},
            {'name': 'consumer', 'value': 'dev', 'uid': str(TEST_UID)},
        ])
        if norm_login != login:
            events.append(
                {'name': 'info.login_wanted', 'value': login, 'uid': str(TEST_UID)},
            )
        if unsubscribed_from_maillists:
            events.append(
                {'name': 'account.unsubscribed_from_maillists', 'value': unsubscribed_from_maillists, 'uid': str(TEST_UID)},
            )

        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )

    def assert_statbox_ok(self, login=TEST_LOGIN, pwd_quality=80, unsubscribed_from_maillists=None,
                          app_id=TEST_DEVICE_APP):
        norm_login = normalize_login(login)

        entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'aliasify',
                _exclude=['user_agent'],
                uid='-',
                login=login,
                consumer='dev',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='account.disabled_status',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='account.mail_status',
                old='-',
                new='active',
            ),
        ]
        if login != norm_login:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['track_id', 'type'],
                    entity='user_defined_login',
                    new=TEST_PWD_LOGIN,
                    old='-',
                ),
            )
        entries += [
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'track_id'],
                operation='added',
                entity='aliases',
                type='1',
                value=norm_login,
            ),
            self.env.statbox.entry('phonenumber_alias_added'),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='phones.secure',
                old='-',
                old_entity_id='-',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                new_entity_id='1',
            ),
        ]

        names_values = []
        if unsubscribed_from_maillists:
            names_values.append(
                ('account.unsubscribed_from_maillists', {'old': '-', 'new': unsubscribed_from_maillists}),
            )
        names_values += [
            ('person.firstname', {'old': '-', 'new': TEST_FIRSTNAME}),
            ('person.lastname', {'old': '-', 'new': TEST_LASTNAME}),
            ('person.language', {'old': '-', 'new': TEST_LANGUAGE}),
            ('person.country', {'old': '-', 'new': TEST_COUNTRY_CODE}),
            ('person.fullname', {'old': '-', 'new': '{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME)}),
            ('password.encrypted', {}),
            ('password.encoding_version', {'old': '-', 'new': '6'}),
            ('password.quality', {'old': '-', 'new': str(pwd_quality)}),
        ]
        entries += [
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity=entity,
                **kwargs
            )
            for entity, kwargs in names_values
        ] + [
            self.env.statbox.entry(
                'account_register',
                _exclude=['track_id', 'type'],
                login=norm_login,
                user_agent='-',
            ),
            self.env.statbox.entry('subscriptions', sid='8'),
            self.env.statbox.entry('subscriptions', sid='2', suid=str(TEST_SUID)),
            self.env.statbox.entry('subscriptions', sid='65'),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id', 'type'],
                entity='phonenumber_alias.enable_search',
                new='0',
                old='-',
            ),
        ]
        app_id_kwargs = {'app_id': app_id} if app_id is not None else {}
        entries += [
            self.env.statbox.entry('phone_confirmed', _exclude=['user_agent'], consumer='dev'),
            self.env.statbox.entry('secure_phone_bound', _exclude=['user_agent'], consumer='dev'),
            self.env.statbox.entry(
                'account_created',
                _exclude=['language', 'user_agent'],
                aliasify='1',
                consumer='dev',
                login=norm_login,
                password_quality=str(pwd_quality),
            ),
            self.env.statbox.entry('tokens_issued', login=login, **app_id_kwargs),
        ]
        self.env.statbox.assert_has_written(entries)

    def assert_oauth_ok(self, count=2):
        eq_(len(self.env.oauth.requests), count)

    def default_response(self, login=TEST_LOGIN, **kwargs):
        normalized_display_login = normalize_login(login)
        return dict({
            'uid': TEST_UID,
            'cloud_token': TEST_CLOUD_TOKEN,
            'x_token': TEST_OAUTH_X_TOKEN,
            'x_token_expires_in': TEST_OAUTH_X_TOKEN_TTL,
            'x_token_issued_at': TimeNow(),
            'access_token': TEST_OAUTH_TOKEN,
            'access_token_expires_in': TEST_OAUTH_TOKEN_TTL,
            'avatar_url': TEST_AVATAR_URL,
            'display_name': login,
            'has_password': True,
            'display_login': login,
            'normalized_display_login': normalized_display_login,
            'primary_alias_type': 1,
            'is_avatar_empty': True,
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'public_id': TEST_PUBLIC_ID,
        }, **kwargs)

    def test_without_required_headers__error(self):
        rv = self.make_request(exclude_headers=self.http_headers)
        self.assert_error_response(rv, ['ip.empty'])

    def test_password_forbidden_spaces__error(self):
        rv = self.make_request(query_args={'password': ' password'})
        self.assert_error_response(rv, ['password.prohibitedsymbols'])

    def test_not_registered_for_tokens(self):
        self.setup_track(registered=False, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_eula_not_accepted__error(self):
        rv = self.make_request(query_args={'eula_accepted': False})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_already_registered__error(self):
        self.setup_track(registered=True, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])
        self.env.statbox.assert_has_written([])

    def test_login_not_available__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'occupied'}),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['login.notavailable'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_user_not_confirmed__error(self):
        self.setup_track(confirmed=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_invalid_track_state__error(self):
        self.setup_track(number=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

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
                mode='mobile',
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
                mode='mobile',
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
        ok_(not self.env.mailer.message_count)

        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(
                TEST_UID,
                TEST_PHONE_NUMBER.e164,
                yandexuid='',
            ),
        ])
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_USER_IP,
            ),
        ])

        profile = self.make_user_profile(
            raw_env={
                'ip': TEST_USER_IP,
                'yandexuid': None,
                'user_agent_info': {},
                'device_id': TEST_DEVICE_ID,
                'cloud_token': TEST_CLOUD_TOKEN,
                'is_mobile': True,
            },
        )
        self.assert_profile_written_to_auth_challenge_log(profile)

    def test_password_like_login__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PWD_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None, login=TEST_PWD_LOGIN),
        )

        rv = self.make_request(query_args={'login': TEST_PWD_LOGIN, 'password': TEST_PWD_LOGIN})

        self.assert_error_response(rv, ['password.weak'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('password_validation_error', like_login='1'),
        ])

    def test_password_like_phone__error(self):
        rv = self.make_request(query_args={'password': TEST_PHONE_NUMBER.digital})

        self.assert_error_response(rv, ['password.likephonenumber'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('password_validation_error', like_phone_number='1'),
        ])

    def test_frodo_failed__ok(self):
        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_oauth_ok()
        self.assert_statbox_ok()

    def test_unsubscribe_from_maillists__known_app_id__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='1')
        self.assert_historydb_ok(unsubscribed_from_maillists='1')
        self.assert_statbox_ok(unsubscribed_from_maillists='1')

    def test_unsubscribe_from_maillists__no_app_id__ok(self):
        self.setup_track(app_id=None)
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='all')
        self.assert_historydb_ok(unsubscribed_from_maillists='all')
        self.assert_statbox_ok(unsubscribed_from_maillists='all', app_id=None)

    def test_unsubscribe_from_maillists__unknown_app_id__ok(self):
        self.setup_track(app_id='smth.weird')
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='all')
        self.assert_historydb_ok(unsubscribed_from_maillists='all')
        self.assert_statbox_ok(unsubscribed_from_maillists='all', app_id='smth.weird')

    def test_busy_phonenumber_alias(self):
        blackbox_response_with_alias = blackbox_userinfo_response(
            uid=TEST_OTHER_UID,
            login=TEST_PHONE_NUMBER.digital,
            aliases={
                'portal': TEST_OTHER_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            emails=[{
                'default': True,
                'native': True,
                'validated': True,
                'address': 'withalias@yandex.ru',
            }],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response_with_alias,
        )
        self.env.db.serialize(blackbox_response_with_alias)
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_OTHER_UID, db='passportdbcentral')

        rv = self.make_request()
        self.assert_ok_response(rv, **self.default_response())
        self.assert_track_ok()
        self.assert_db_ok(
            centraldb_queries=5,
            sharddb_queries=5,
            phonenumber_alias_given_out=False,
        )

        assert_account_has_phonenumber_alias(
            self.env.db,
            TEST_OTHER_UID,
            TEST_PHONE_NUMBER.digital,
            enable_search=False,
        )

        self.assert_historydb_ok(phonenumber_alias_given_out=False)
        self.assert_oauth_ok()
        eq_(self.env.mailer.message_count, 0)

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
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'portal': TEST_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'password.encrypted': '1:testpassword'},
                is_avatar_empty=False,
                default_avatar_key=TEST_AVATAR_KEY,
                display_name={
                    'name': TEST_DISPLAY_NAME,
                },
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
                birthdate=None,
                gender=None,
                emails=[self.create_native_email(TEST_LOGIN, 'yandex.com')],
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request()
        expected = self.default_response(
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            native_default_email='%s@yandex.com' % TEST_LOGIN,
        )
        expected.pop('is_avatar_empty')

        self.assert_ok_response(rv, **expected)
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('tokens_issued', app_id=TEST_DEVICE_APP),
        ])
        self.assert_oauth_ok()

    def test_retrying_for_tokens__ok(self):
        self.setup_track(registered=True, uid=TEST_UID, token_created_at=time() - 1)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'portal': TEST_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'password.encrypted': '1:testpassword'},
                is_avatar_empty=False,
                default_avatar_key=TEST_AVATAR_KEY,
                display_name={
                    'name': TEST_DISPLAY_NAME,
                },
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
                birthdate=None,
                gender=None,
                emails=[self.create_native_email(TEST_LOGIN, 'yandex.com')],
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request()
        expected = self.default_response(
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            native_default_email='%s@yandex.com' % TEST_LOGIN,
        )
        expected.pop('is_avatar_empty')

        self.assert_ok_response(rv, **expected)
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('tokens_issued', app_id=TEST_DEVICE_APP),
        ])
        self.assert_oauth_ok()

    def test_no_uid_for_tokens__error(self):
        self.setup_track(registered=True)

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
