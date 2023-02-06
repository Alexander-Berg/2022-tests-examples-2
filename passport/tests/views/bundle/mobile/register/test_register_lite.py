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
    TEST_EXTERNAL_EMAIL,
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
    TEST_PASSWORD,
    TEST_PHONE_ID1,
    TEST_PUBLIC_ID,
    TEST_SERIALIZED_PASSWORD,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_generate_public_id_response,
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    assert_simple_phone_bound,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_PWD_LOGIN = 'Kl44tuNikt0'
TEST_USER_IP = '37.9.101.188'
TEST_AVATAR_URL = TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE)
TEST_APP_ID = TEST_DEVICE_APP


@with_settings_hosts(
    FRODO_URL='http://localhost/',
    BLACKBOX_URL='http://localhost',
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
    DEFAULT_AVATAR_KEY=TEST_AVATAR_KEY,
    TOKEN_REISSUE_INTERVAL=60,
    MOBILE_LITE_DATA_STATUS_DEFAULT={
        'name': 'not_used',
        'phone_number': 'not_used',
        'password': 'not_used',
    },
    MOBILE_LITE_DATA_STATUS_BY_APP_ID_PREFIX={
        TEST_APP_ID: {
            'name': 'optional',
            'phone_number': 'optional',
            'password': 'optional',
        },
        'ru.yandex.passport': {
            'name': 'required',
            'phone_number': 'required',
            'password': 'required',
        },
    },
    CLEAN_WEB_API_ENABLED=False,
    ALLOW_LITE_REGISTRATION=True,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_APP_ID},
    SENDER_MAIL_SUBSCRIPTION_SERVICES=TEST_MAIL_SUBSCRIPTION_SERVICES,
)
class MobileRegisterLiteViewTestCase(BaseBundleTestViews,
                                     StatboxTestMixin,
                                     ProfileTestMixin,
                                     make_clean_web_test_mixin('test__ok', ['firstname', 'lastname'],
                                                               statbox_action='phone_confirmed'),
                                     EmailTestMixin):
    default_url = '/1/bundle/mobile/register/lite/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
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
                grants={'mobile': ['register_lite']},
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
            mode='register_lite',
            type='mobile',
            ip=TEST_USER_IP,
            user_agent='-',
            track_id=self.track_id,
            consumer='dev',
        )
        super(MobileRegisterLiteViewTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['submitted'],
            _exclude=['user_agent'],
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification'],
            _exclude=['old', 'mode', 'track_id', 'type'],
            operation='created',
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'tokens_issued',
            _exclude=['user_agent'],
            action='tokens_issued',
            uid=str(TEST_UID),
            login=TEST_EXTERNAL_EMAIL,
            password_passed='0',
            x_token_client_id=TEST_X_TOKEN_CLIENT_ID,
            x_token_issued='1',
            client_id=TEST_CLIENT_ID,
            client_token_issued='1',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            app_id=TEST_APP_ID,
            cloud_token=TEST_CLOUD_TOKEN,
        )

    def setup_track(self, user_entered_login=TEST_EXTERNAL_EMAIL, is_magic_link_confirmed=True,
                    country=TEST_COUNTRY_CODE, language=TEST_LANGUAGE,
                    is_phone_confirmed=True, number=TEST_PHONE_NUMBER.e164,
                    is_registered=False, token_created_at=None, allow_create_tokens=True, uid=None,
                    app_id=TEST_APP_ID):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.user_entered_login = user_entered_login
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.device_application = app_id
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.language = language
            track.country = country

            track.magic_link_confirm_time = 123456 if is_magic_link_confirmed else None

            track.phone_confirmation_is_confirmed = is_phone_confirmed
            track.phone_confirmation_phone_number = number if is_phone_confirmed else None

            track.is_successful_registered = is_registered
            track.oauth_token_created_at = token_created_at
            track.allow_oauth_authorization = allow_create_tokens
            track.uid = uid

    def setup_blackbox(self, is_domain_pdd=False):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EXTERNAL_EMAIL: 'free'}),
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
            'hosted_domains',
            blackbox_hosted_domains_response(count=1 if is_domain_pdd else 0),
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

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_successful_registered)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

    def assert_db_ok(self, centraldb_queries=4, sharddb_queries=8,
                     email=TEST_EXTERNAL_EMAIL,
                     with_password=True, pwd_quality=80, with_fio=True,
                     with_phone=True, is_phone_secure=True, unsubscribed_from_maillists=None):
        timenow = TimeNow()
        dtnow = DatetimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'lite', email, uid=TEST_UID, db='passportdbcentral')
        if with_phone and is_phone_secure:
            self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')
        else:
            self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')

        if with_password:
            self.env.db.check('attributes', 'password.quality', '3:%s' % str(pwd_quality), uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'password.quality', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'password.update_datetime', uid=TEST_UID, db='passportdbshard1')

        if with_fio:
            self.env.db.check('attributes', 'person.firstname', TEST_FIRSTNAME, uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'person.lastname', TEST_LASTNAME, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'person.firstname', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'person.lastname', uid=TEST_UID, db='passportdbshard1')

        if unsubscribed_from_maillists:
            self.env.db.check('attributes', 'account.unsubscribed_from_maillists', unsubscribed_from_maillists, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'account.unsubscribed_from_maillists', uid=TEST_UID, db='passportdbshard1')

        if with_phone:
            if is_phone_secure:
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
            else:
                assert_simple_phone_bound.check_db(
                    self.env.db,
                    uid=TEST_UID,
                    phone_attributes={
                        'id': TEST_PHONE_ID1,
                        'number': TEST_PHONE_NUMBER.e164,
                        'created': dtnow,
                        'bound': dtnow,
                        'confirmed': dtnow,
                    },
                )

    def assert_historydb_ok(self, email=TEST_EXTERNAL_EMAIL, is_email_unsafe=False,
                            with_password=True, pwd_quality=80, with_fio=True,
                            with_phone=True, is_phone_secure=True, unsubscribed_from_maillists=None):
        timenow = TimeNow()

        events = [
            {'name': 'action', 'value': 'account_register_lite', 'uid': str(TEST_UID)},
            {'name': 'consumer', 'value': 'dev', 'uid': str(TEST_UID)},
            {'name': 'info.login', 'value': email, 'uid': str(TEST_UID)},
            {'name': 'info.ena', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'info.disabled_status', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True), 'uid': str(TEST_UID)},
            {'name': 'info.country', 'value': TEST_COUNTRY_CODE, 'uid': str(TEST_UID)},
            {'name': 'info.tz', 'value': 'Europe/Moscow', 'uid': str(TEST_UID)},
            {'name': 'info.lang', 'value': TEST_LANGUAGE, 'uid': str(TEST_UID)},
            {'name': 'info.karma_prefix', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma_full', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'alias.lite.add', 'value': email, 'uid': str(TEST_UID)},
            {'name': 'sid.add', 'value': '8|%s' % email, 'uid': str(TEST_UID)},
            {'name': 'email.1', 'value': 'created', 'uid': str(TEST_UID)},
            {'name': 'email.1.address', 'value': email, 'uid': str(TEST_UID)},
            {'name': 'email.1.bound_at', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'email.1.confirmed_at', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'email.1.created_at', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'email.1.is_unsafe', 'value': '1' if is_email_unsafe else '0', 'uid': str(TEST_UID)},
        ]

        if with_fio:
            events += [
                {'name': 'info.firstname', 'value': TEST_FIRSTNAME, 'uid': str(TEST_UID)},
                {'name': 'info.lastname', 'value': TEST_LASTNAME, 'uid': str(TEST_UID)},
            ]

        if with_password:
            password_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
            events += [
                {'name': 'info.password', 'value': password_hash, 'uid': str(TEST_UID)},
                {'name': 'info.password_quality', 'value': str(pwd_quality), 'uid': str(TEST_UID)},
                {'name': 'info.password_update_time', 'value': timenow, 'uid': str(TEST_UID)},
            ]

        if with_phone:
            events += [
                {'name': 'phone.1.action', 'value': 'created', 'uid': str(TEST_UID)},
                {'name': 'phone.1.bound', 'value': timenow, 'uid': str(TEST_UID)},
                {'name': 'phone.1.confirmed', 'value': timenow, 'uid': str(TEST_UID)},
                {'name': 'phone.1.created', 'value': timenow, 'uid': str(TEST_UID)},
                {'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164, 'uid': str(TEST_UID)},
            ]
            if is_phone_secure:
                events += [
                    {'name': 'phone.1.secured', 'value': timenow, 'uid': str(TEST_UID)},
                    {'name': 'phones.secure', 'value': '1', 'uid': str(TEST_UID)},
                    {'name': 'alias.phonenumber.add', 'value': TEST_PHONE_NUMBER.international, 'uid': str(TEST_UID)},
                    {'name': 'info.phonenumber_alias_search_enabled', 'value': '0', 'uid': str(TEST_UID)},
                ]

        if unsubscribed_from_maillists:
            events.append(
                {'name': 'account.unsubscribed_from_maillists', 'value': unsubscribed_from_maillists, 'uid': str(TEST_UID)},
            )

        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )

    def assert_oauth_ok(self, count=2):
        eq_(len(self.env.oauth.requests), count)

    def default_response(self, login=TEST_EXTERNAL_EMAIL, has_password=True, has_fio=True, **kwargs):
        response = {
            'uid': TEST_UID,
            'cloud_token': TEST_CLOUD_TOKEN,
            'x_token': TEST_OAUTH_X_TOKEN,
            'x_token_expires_in': TEST_OAUTH_X_TOKEN_TTL,
            'x_token_issued_at': TimeNow(),
            'access_token': TEST_OAUTH_TOKEN,
            'access_token_expires_in': TEST_OAUTH_TOKEN_TTL,
            'avatar_url': TEST_AVATAR_URL,
            'display_name': login,
            'display_login': login,
            'normalized_display_login': login.lower(),
            'primary_alias_type': 5,
            'is_avatar_empty': True,
            'public_id': TEST_PUBLIC_ID,
        }
        if has_password:
            response.update(has_password=True)
        if has_fio:
            response.update(
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
            )
        response.update(kwargs)
        return response

    def test__ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_oauth_ok()
        ok_(not self.env.mailer.message_count)

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

    def test_without_password__ok(self):
        rv = self.make_request(exclude_args=['password'])

        self.assert_ok_response(
            rv,
            **self.default_response(has_password=False)
        )
        self.assert_track_ok()
        self.assert_db_ok(
            sharddb_queries=6,
            with_password=False,
            is_phone_secure=False,
        )
        self.assert_historydb_ok(
            with_password=False,
            is_phone_secure=False,
            is_email_unsafe=True,
        )
        self.assert_oauth_ok()
        ok_(not self.env.mailer.message_count)

    def test_minimal__ok(self):
        self.setup_track(is_phone_confirmed=False)
        rv = self.make_request(exclude_args=['firstname', 'lastname', 'password'])

        self.assert_ok_response(
            rv,
            **self.default_response(has_fio=False, has_password=False)
        )
        self.assert_track_ok()
        self.assert_db_ok(
            centraldb_queries=3,
            sharddb_queries=3,
            with_fio=False,
            with_password=False,
            with_phone=False,
        )
        self.assert_historydb_ok(
            with_fio=False,
            with_password=False,
            with_phone=False,
            is_email_unsafe=True,
        )
        self.assert_oauth_ok()
        ok_(not self.env.mailer.message_count)

        self.env.social_binding_logger.assert_has_written([])

    def test_all_extra_data_is_prohibited__ok(self):
        self.setup_track(app_id='com.yandex.passport.nothing_used')
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response(has_fio=False, has_password=False)
        )
        self.assert_track_ok()
        self.assert_db_ok(
            centraldb_queries=3,
            sharddb_queries=3,
            with_fio=False,
            with_password=False,
            with_phone=False,
        )
        self.assert_historydb_ok(
            with_fio=False,
            with_password=False,
            with_phone=False,
            is_email_unsafe=True,
        )
        self.assert_oauth_ok()
        ok_(not self.env.mailer.message_count)

    def test_unsubscribe_from_maillists__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='1')
        self.assert_historydb_ok(unsubscribed_from_maillists='1')

    def test_registration_disabled__error(self):
        with settings_context(ALLOW_LITE_REGISTRATION=False):
            rv = self.make_request()
        self.assert_error_response(rv, ['action.impossible'])

    def test_domain_is_pdd__error(self):
        self.setup_blackbox(is_domain_pdd=True)
        rv = self.make_request()
        self.assert_error_response(rv, ['domain.invalid_type'])

    def test_extra_data_required__error(self):
        self.setup_track(app_id='ru.yandex.passport.all_required')
        rv = self.make_request(exclude_args=['firstname', 'lastname', 'password'])

        self.assert_error_response(
            rv,
            [
                'firstname.empty',
                'lastname.empty',
                'password.empty',
            ],
        )

    def test_phone_required__error(self):
        self.setup_track(is_phone_confirmed=False, app_id='ru.yandex.passport.all_required')
        rv = self.make_request()

        self.assert_error_response(rv, ['phone.required'])

    def test_invalid_track_state__error(self):
        self.setup_track(user_entered_login=None)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_not_registered_for_tokens__error(self):
        self.setup_track(is_registered=False, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_already_registered__error(self):
        self.setup_track(is_registered=True, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])
        self.env.statbox.assert_has_written([])

    def test_eula_not_accepted__error(self):
        rv = self.make_request(query_args={'eula_accepted': False})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_login_not_available__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EXTERNAL_EMAIL: 'occupied'}),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['login.notavailable'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_magic_link_not_confirmed__error(self):
        self.setup_track(is_magic_link_confirmed=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

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
        """
        Предыдущим запросом зарегистрировали аккаунт, но при походе в oauth сломались.
        Повторно приходим в эту ручку с треком, аккаунт не регистрируем, только забираем для него токены.
        """
        self.setup_track(is_registered=True, uid=TEST_UID)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_EXTERNAL_EMAIL,
                aliases={
                    'lite': TEST_EXTERNAL_EMAIL,
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
            self.env.statbox.entry('tokens_issued'),
        ])
        self.assert_oauth_ok()
        self.assert_track_ok()

    def test_retrying_for_tokens__ok(self):
        """
        Предыдущим запросом зарегистрировали аккаунт, но похода в oauth не дождались.
        Повторно приходим в эту ручку с треком, аккаунт не регистрируем, только забираем для него токены.
        """
        self.setup_track(is_registered=True, uid=TEST_UID, token_created_at=time() - 1)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_EXTERNAL_EMAIL,
                aliases={
                    'lite': TEST_EXTERNAL_EMAIL
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
            self.env.statbox.entry('tokens_issued'),
        ])
        self.assert_oauth_ok()
        self.assert_track_ok()

    def test_no_uid_for_tokens__error(self):
        self.setup_track(is_registered=True)

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
