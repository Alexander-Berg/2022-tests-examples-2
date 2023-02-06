# -*- coding: utf-8 -*-
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
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COUNTRY,
    TEST_USER_IP,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_UID2,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.builders.phone_squatter.exceptions import PhoneSquatterTemporaryError
from passport.backend.core.builders.phone_squatter.faker import phone_squatter_start_tracking_response
from passport.backend.core.models.phones.faker import (
    assert_phonenumber_alias_missing,
    assert_secure_phone_bound,
    build_phone_secured,
)
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
from passport.backend.core.types.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import deep_merge


TEST_IP = '123.123.123.123'
TEST_YANDEXUID = 'yuid12345'
TEST_NEOPHONISH_LOGIN = 'nphne-xxx'
TEST_ORIGIN = 'origin'


TEST_SETTINGS = dict(
    BLACKBOX_URL='localhost',
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
    UFO_API_RETRIES=1,
    UFO_API_URL='http://localhost/',
    USE_NEW_SUGGEST_BY_PHONE=False,
    PHONE_SQUATTER_RETRIES=1,
    USE_PHONE_SQUATTER=True,
    PHONE_SQUATTER_DRY_RUN=False,
    **mock_counters()
)


@with_settings_hosts(**TEST_SETTINGS)
class TestAccountRegisterNeophonish(BaseBundleTestViews,
                                    StatboxTestMixin,
                                    make_clean_web_test_mixin('test_successful_register', ['firstname', 'lastname']),
                                    ProfileTestMixin):
    default_url = '/1/bundle/account/register/neophonish/'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_neophonish'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')

        self.setup_query_args()

        self.env.bot_api.set_response_value('send_message', bot_api_response())
        self.env.phone_squatter.set_response_value('start_tracking', phone_squatter_start_tracking_response())
        self.setup_blackbox()
        self.setup_track()

        self.patches = []
        login_patch = mock.patch(
            'passport.backend.core.types.login.login.generate_neophonish_login',
            mock.Mock(return_value=TEST_NEOPHONISH_LOGIN),
        )
        login_patch.start()
        self.patches.append(login_patch)

        self.setup_statbox_templates()
        self.setup_profile_patches()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.teardown_profile_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches

    def setup_query_args(self, with_fio=True):
        self.http_query_args = dict(
            language=TEST_ACCEPT_LANGUAGE,
            country=TEST_USER_COUNTRY,
            track_id=self.track_id,
            eula_accepted=True,
        )
        if with_fio:
            self.http_query_args.update(
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
            )

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

    def setup_track(self, registered=False, confirmed=True, number=TEST_PHONE_NUMBER.e164):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_successful_registered = registered
            track.phone_confirmation_is_confirmed = confirmed
            track.phone_confirmation_phone_number = number if confirmed else None

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_successful_registered)
        ok_(track.allow_authorization)
        ok_(not track.allow_oauth_authorization)

    def assert_db_ok(
        self,
        centraldb_queries=3,
        sharddb_queries=6,
        with_phonenumber_alias=True,
        unsubscribed_from_maillists=None,
        phone_number=None,
        with_fio=True,
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

        self.env.db.check_missing('attributes', 'account.enable_search_by_phone_alias', uid=TEST_UID,
                                  db='passportdbshard1')

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        if with_fio:
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

    def assert_historydb_ok(
        self,
        with_phonenumer_alias=True,
        unsubscribed_from_maillists=None,
        with_fio=True,
    ):
        timenow = TimeNow()

        events = [
            {'name': 'action', 'value': 'account_register_neophonish', 'uid': str(TEST_UID)},
            {'name': 'consumer', 'value': 'dev', 'uid': str(TEST_UID)},
            {'name': 'user_agent', 'value': 'curl', 'uid': str(TEST_UID)},
            {'name': 'info.login', 'value': TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
            {'name': 'info.ena', 'value': '1', 'uid': str(TEST_UID)},
            {'name': 'info.disabled_status', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True), 'uid': str(TEST_UID)},
            {'name': 'info.country', 'value': TEST_USER_COUNTRY, 'uid': str(TEST_UID)},
            {'name': 'info.tz', 'value': 'Europe/Moscow', 'uid': str(TEST_UID)},
            {'name': 'info.lang', 'value': TEST_ACCEPT_LANGUAGE, 'uid': str(TEST_UID)},
            {'name': 'info.karma_prefix', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma_full', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'info.karma', 'value': '0', 'uid': str(TEST_UID)},
            {'name': 'alias.neophonish.add', 'value': TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
            {'name': 'sid.add', 'value': '8|%s' % TEST_NEOPHONISH_LOGIN, 'uid': str(TEST_UID)},
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
        if with_fio:
            events += [
                {'name': 'info.firstname', 'value': TEST_FIRSTNAME, 'uid': str(TEST_UID)},
                {'name': 'info.lastname', 'value': TEST_LASTNAME, 'uid': str(TEST_UID)},
            ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )

    def assert_ok_blackbox_get_alias_owner_request(self, request, phone_number=None):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER
        request.assert_post_data_contains(
            dict(
                login=phone_number.digital,
                method='userinfo',
            ),
        )

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

    def test_not_confirmed__error(self):
        self.setup_track(confirmed=False)
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])

    def test_already_registered__error(self):
        self.setup_track(registered=True)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.already_registered'])
        eq_(len(self.env.bot_api.requests), 0)

    def test_eula_not_accepted__error(self):
        rv = self.make_request(query_args={'eula_accepted': '0'})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])

    def test_successful_register(self):
        rv = self.make_request()
        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        eq_(len(self.env.bot_api.requests), 1)
        eq_(len(self.env.phone_squatter.requests), 0)

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
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone.e164

        rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)
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

        self.assert_ok_response(rv, uid=TEST_UID)
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

    def test_unsubscribe_from_maillists__known_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True, origin=TEST_ORIGIN))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='1')
        self.assert_historydb_ok(unsubscribed_from_maillists='1')

    def test_unsubscribe_from_maillists__no_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='all')
        self.assert_historydb_ok(unsubscribed_from_maillists='all')

    def test_unsubscribe_from_maillists__unknown_origin__ok(self):
        rv = self.make_request(query_args=dict(unsubscribe_from_maillists=True, origin='weird'))

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track_ok()
        self.assert_db_ok(unsubscribed_from_maillists='all')
        self.assert_historydb_ok(unsubscribed_from_maillists='all')

    def test_without_fio__disabled__error(self):
        self.setup_query_args(with_fio=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['firstname.empty', 'lastname.empty'])
        eq_(len(self.env.bot_api.requests), 0)

    def test_without_fio__enabled__successful_register(self):
        self.setup_query_args(with_fio=False)

        with settings_context(**dict(TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=True)):
            rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track_ok()
        self.assert_db_ok(with_fio=False)
        self.assert_historydb_ok(with_fio=False)
        eq_(len(self.env.bot_api.requests), 1)
        eq_(len(self.env.phone_squatter.requests), 1)

    def test_without_fio__enabled__phone_squatter_error(self):
        self.env.phone_squatter.set_response_side_effect('start_tracking', PhoneSquatterTemporaryError)
        self.setup_query_args(with_fio=False)

        with settings_context(**dict(TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=True)):
            rv = self.make_request()

        self.assert_error_response(rv, ['backend.phone_squatter_failed'])

    def test_without_fio__enabled__phone_squatter_dry_run(self):
        self.env.phone_squatter.set_response_side_effect('start_tracking', PhoneSquatterTemporaryError)
        self.setup_query_args(with_fio=False)

        with settings_context(**dict(TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=True, PHONE_SQUATTER_DRY_RUN=True)):
            rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)
        eq_(len(self.env.phone_squatter.requests), 1)

    def test_without_fio__enabled__phone_squatter_disabled(self):
        self.setup_query_args(with_fio=False)

        with settings_context(**dict(TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=True, USE_PHONE_SQUATTER=False)):
            rv = self.make_request()

        self.assert_ok_response(rv, uid=TEST_UID)
        eq_(len(self.env.phone_squatter.requests), 0)
