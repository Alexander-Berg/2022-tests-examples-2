# -*- coding: utf-8 -*-
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import (
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
    TEST_FIRSTNAME,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_UID,
    TEST_UID2,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_generate_public_id_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.bot_api import BotApiTemporaryError
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.models.phones.faker import (
    assert_phonenumber_alias_missing,
    assert_secure_phone_bound,
    build_phone_secured,
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
from passport.backend.core.types.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge


TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_NEOPHONISH_LOGIN = 'nphne-xxx'
TEST_USER_IP = '37.9.101.188'
TEST_AVATAR_URL = TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE)
TEST_DISPLAY_NAME = TEST_FIRSTNAME + ' ' + TEST_LASTNAME


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    BOT_API_RETRIES=2,
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL=TEST_AVATAR_URL_TEMPLATE,
    DEFAULT_AVATAR_KEY=TEST_AVATAR_KEY,
    TOKEN_REISSUE_INTERVAL=60,
    CLEAN_WEB_API_ENABLED=False,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_DEVICE_APP},
    SENDER_MAIL_SUBSCRIPTION_SERVICES=TEST_MAIL_SUBSCRIPTION_SERVICES,
)
class MobileRegisterNeophonishViewTestCase(BaseBundleTestViews,
                                           StatboxTestMixin,
                                           make_clean_web_test_mixin('test__ok', ['firstname', 'lastname'],
                                                                     statbox_action='phone_confirmed'),
                                           ProfileTestMixin):
    default_url = '/1/bundle/mobile/register/neophonish/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
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
                grants={'mobile': ['register_neophonish']},
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
        self.env.bot_api.set_response_value('send_message', bot_api_response())

        self.patches = []

        login_patch = mock.patch(
            'passport.backend.core.types.login.login.generate_neophonish_login',
            mock.Mock(return_value=TEST_NEOPHONISH_LOGIN),
        )
        login_patch.start()
        self.patches.append(login_patch)

        self.setup_track()
        self.setup_blackbox()
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
            mode='register_neophonish',
            type='mobile',
            ip=TEST_USER_IP,
            user_agent='-',
            track_id=self.track_id,
            consumer='dev',
        )
        super(MobileRegisterNeophonishViewTestCase, self).setup_statbox_templates()
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
            login=TEST_NEOPHONISH_LOGIN,
            password_passed='0',
            x_token_client_id=TEST_X_TOKEN_CLIENT_ID,
            x_token_issued='1',
            client_id=TEST_CLIENT_ID,
            client_token_issued='1',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            app_id=TEST_DEVICE_APP,
            cloud_token=TEST_CLOUD_TOKEN,
        )

    def setup_track(self, country=TEST_COUNTRY_CODE, language=TEST_LANGUAGE,
                    is_phone_confirmed=True, number=TEST_PHONE_NUMBER.e164,
                    is_registered=False, token_created_at=None, allow_create_tokens=True, uid=None):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_application = TEST_DEVICE_APP
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.language = language
            track.country = country

            track.phone_confirmation_is_confirmed = is_phone_confirmed
            track.phone_confirmation_phone_number = number if is_phone_confirmed else None

            track.is_successful_registered = is_registered
            track.oauth_token_created_at = token_created_at
            track.allow_oauth_authorization = allow_create_tokens
            track.uid = uid

    def setup_blackbox(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NEOPHONISH_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_successful_registered)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

    def assert_db_ok(
        self,
        centraldb_queries=3,
        sharddb_queries=6,
        with_phonenumber_alias=True,
        unsubscribed_from_maillists=None,
        phone_number=None,
    ):
        timenow = TimeNow()
        dtnow = DatetimeNow()

        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'neophonish', TEST_NEOPHONISH_LOGIN, uid=TEST_UID, db='passportdbcentral')
        if with_phonenumber_alias:
            self.env.db.check('aliases', 'phonenumber', phone_number.digital, uid=TEST_UID, db='passportdbcentral')
        else:
            self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.env.db.check_missing('attributes', 'account.enable_search_by_phone_alias', uid=TEST_UID, db='passportdbshard1')

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', TEST_FIRSTNAME, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', TEST_LASTNAME, uid=TEST_UID, db='passportdbshard1')

        if unsubscribed_from_maillists:
            self.env.db.check('attributes', 'account.unsubscribed_from_maillists', unsubscribed_from_maillists, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'account.unsubscribed_from_maillists', uid=TEST_UID, db='passportdbshard1')

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': phone_number.e164,
                'created': dtnow,
                'bound': dtnow,
                'confirmed': dtnow,
                'secured': dtnow,
            },
            binding_flags=binding_flags,
        )

    def assert_historydb_ok(self, with_phonenumer_alias=True, unsubscribed_from_maillists=None):
        timenow = TimeNow()

        events = [
            {'name': 'action', 'value': 'account_register_neophonish', 'uid': str(TEST_UID)},
            {'name': 'consumer', 'value': 'dev', 'uid': str(TEST_UID)},
            {'name': 'info.login', 'value': TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
            {'name': 'info.ena', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'info.disabled_status', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True), 'uid': str(TEST_UID)},
            {'name': 'info.country', 'value': TEST_COUNTRY_CODE, 'uid': str(TEST_UID)},
            {'name': 'info.tz', 'value': 'Europe/Moscow', 'uid': str(TEST_UID)},
            {'name': 'info.lang', 'value': TEST_LANGUAGE, 'uid': str(TEST_UID)},
            {'name': 'info.karma_prefix', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma_full', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'alias.neophonish.add', 'value': TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
            {'name': 'sid.add', 'value': '8|%s' % TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
            {'name': 'info.firstname', 'value': TEST_FIRSTNAME, 'uid': str(TEST_UID)},
            {'name': 'info.lastname', 'value': TEST_LASTNAME, 'uid': str(TEST_UID)},
            {'name': 'phone.1.action', 'value': 'created', 'uid': str(TEST_UID)},
            {'name': 'phone.1.bound', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.confirmed', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.created', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phone.1.number', 'value': TEST_PHONE_NUMBER.e164, 'uid': str(TEST_UID)},
            {'name': 'phone.1.secured', 'value': timenow, 'uid': str(TEST_UID)},
            {'name': 'phones.secure', 'value': '1', 'uid': str(TEST_UID)},
        ]
        if with_phonenumer_alias:
            events += [
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

    def assert_social_binding_log_written(self):
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_USER_IP,
            ),
        ])

    def assert_ok_blackbox_get_alias_owner_request(self, request, phone_number=None):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER
        request.assert_post_data_contains(
            dict(
                login=phone_number.digital,
                method='userinfo',
            ),
        )

    def default_response(self, **kwargs):
        response = {
            'uid': TEST_UID,
            'cloud_token': TEST_CLOUD_TOKEN,
            'x_token': TEST_OAUTH_X_TOKEN,
            'x_token_expires_in': TEST_OAUTH_X_TOKEN_TTL,
            'x_token_issued_at': TimeNow(),
            'access_token': TEST_OAUTH_TOKEN,
            'access_token_expires_in': TEST_OAUTH_TOKEN_TTL,
            'avatar_url': TEST_AVATAR_URL,
            'display_name': TEST_DISPLAY_NAME,
            'display_login': TEST_NEOPHONISH_LOGIN,
            'primary_alias_type': 5,
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'is_avatar_empty': True,
            'public_id': TEST_PUBLIC_ID,
        }
        response.update(kwargs)
        return response

    def build_phonenumber_alias_owner_account(
        self,
        phone_id=TEST_PHONE_ID2,
        phone_number=None,
        portal_alias=TEST_LOGIN,
        uid=TEST_UID2,
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        return deep_merge(
            dict(
                aliases=dict(portal=portal_alias),
                login=portal_alias,
                uid=uid,
            ),
            build_phone_secured(
                is_alias=True,
                is_enabled_search_for_alias=False,
                phone_id=phone_id,
                phone_number=phone_number.e164,
            ),
        )

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
        self.assert_social_binding_log_written()
        eq_(len(self.env.bot_api.requests), 1)

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

    def test_new_ivory_coast_phone_when_new_phone_alias_busy(self):
        self.check_new_ivory_coast_phone_alias_busy(TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_old_ivory_coast_phone_when_new_phone_alias_busy(self):
        self.check_new_ivory_coast_phone_alias_busy(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def check_new_ivory_coast_phone_alias_busy(self, user_entered_phone):
        """
        Проверяем регистрацию нового неофониша со старым или новым
        Кот-Д'Ивуарским телефоном, когда старый телефон считается устаревшим и
        новый алиас уже занят.
        """
        userinfo_response = blackbox_userinfo_response(
            **self.build_phonenumber_alias_owner_account(
                phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            )
        )
        self.env.db.serialize(userinfo_response)
        self.env.blackbox.set_response_side_effect('userinfo',  [userinfo_response])

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone.e164

        rv = self.make_request()

        self.assert_ok_response(rv, **self.default_response())
        self.assert_track_ok()
        self.assert_db_ok(
            centraldb_queries=5,
            phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

        assert_phonenumber_alias_missing(db_faker=self.env.db, uid=TEST_UID2)

        self.assert_ok_blackbox_get_alias_owner_request(
            request=self.env.blackbox.requests[1],
            phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_new_ivory_coast_phone_when_old_phone_alias_busy(self):
        self.check_old_ivory_coast_phone_alias_busy(TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_old_ivory_coast_phone_when_old_phone_alias_busy(self):
        self.check_old_ivory_coast_phone_alias_busy(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def check_old_ivory_coast_phone_alias_busy(self, user_entered_phone):
        """
        Проверяем регистрацию нового неофониша со старым или новым
        Кот-Д'Ивуарским телефоном, когда старый телефон считается устаревшим и
        старый алиас уже занят.
        """
        userinfo_response = blackbox_userinfo_response(
            **self.build_phonenumber_alias_owner_account(
                phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            )
        )
        self.env.db.serialize(userinfo_response)
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                userinfo_response,
            ],
        )

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone.e164

        rv = self.make_request()

        self.assert_ok_response(rv, **self.default_response())
        self.assert_track_ok()
        self.assert_db_ok(
            centraldb_queries=5,
            phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

        assert_phonenumber_alias_missing(db_faker=self.env.db, uid=TEST_UID2)

        self.assert_ok_blackbox_get_alias_owner_request(
            request=self.env.blackbox.requests[1],
            phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )
        self.assert_ok_blackbox_get_alias_owner_request(
            request=self.env.blackbox.requests[2],
            phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_bot_api_unavailable__ok(self):
        self.env.bot_api.set_response_side_effect('send_message', BotApiTemporaryError())

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.default_response()
        )
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_oauth_ok()
        self.assert_social_binding_log_written()
        eq_(len(self.env.bot_api.requests), 2)

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
        with settings_context(ALLOW_NEOPHONISH_REGISTRATION=False):
            rv = self.make_request()
        self.assert_error_response(rv, ['action.impossible'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_phone_required__error(self):
        self.setup_track(is_phone_confirmed=False)
        rv = self.make_request()

        self.assert_error_response(rv, ['phone.required'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_not_registered_for_tokens__error(self):
        self.setup_track(is_registered=False, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

    def test_already_registered__error(self):
        self.setup_track(is_registered=True, token_created_at=time() - 3600)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])
        eq_(len(self.env.bot_api.requests), 0)

    def test_eula_not_accepted__error(self):
        rv = self.make_request(query_args={'eula_accepted': False})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])
        self.env.statbox.assert_has_written([self.env.statbox.entry('submitted')])

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
                login=TEST_NEOPHONISH_LOGIN,
                aliases={
                    'neophonish': TEST_NEOPHONISH_LOGIN,
                },
                is_avatar_empty=False,
                default_avatar_key=TEST_AVATAR_KEY,
                display_name={
                    'name': TEST_DISPLAY_NAME,
                },
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
                birthdate=None,
                gender=None,
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request()
        expected = self.default_response(
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
        )
        expected.pop('is_avatar_empty')

        self.assert_ok_response(rv, **expected)
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
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
                login=TEST_NEOPHONISH_LOGIN,
                aliases={
                    'neophonish': TEST_NEOPHONISH_LOGIN
                },
                is_avatar_empty=False,
                default_avatar_key=TEST_AVATAR_KEY,
                display_name={
                    'name': TEST_DISPLAY_NAME,
                },
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
                birthdate=None,
                gender=None,
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request()
        expected = self.default_response(
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
        )
        expected.pop('is_avatar_empty')

        self.assert_ok_response(rv, **expected)
        self.env.db.check_query_counts()
        ok_(not self.env.event_logger.events)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('tokens_issued'),
        ])
        self.assert_oauth_ok()
        self.assert_track_ok()

    def test_no_uid_for_tokens__error(self):
        self.setup_track(is_registered=True)

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])
