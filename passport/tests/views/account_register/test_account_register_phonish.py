# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    error_response as historydb_api_error_response,
    lastauth_response,
)
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_phone,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.phones.faker import (
    assert_simple_phone_bound,
    build_phone_bound,
    build_phone_unbound,
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
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)


TEST_HOST = 'yandex.ru'
TEST_USER_IP = '37.9.101.188'
TEST_USER_AGENT = 'curl'
TEST_RETPATH = 'http://ya.ru'
TEST_USER_COOKIES = 'yandexuid=cookie_yandexuid; fuid01=cookie_fuid01'
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79999999999')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79021213456')
TEST_LOGIN1 = 'phne-test1'
TEST_LOGIN2 = 'phne-test2'
TEST_OPERATION_TTL = timedelta(seconds=60)
TEST_PERIOD_OF_PHONE_NUMBER_LOYALTY = timedelta(hours=2)
TEST_RECENT_ACCOUNT_USAGE_PERIOD = timedelta(minutes=10)
TEST_UID1 = 13
TEST_UID2 = 19
TEST_TIME = datetime(2014, 10, 5, 12)
TEST_PHONE_ID1 = 17
TEST_PHONE_ID2 = 23
TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+22503123456', country='CI', allow_impossible=True)
TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+2250103123456', country='CI', allow_impossible=True)


def build_headers(host=None):
    return mock_headers(
        host=host or TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        x_forwarded_for=True,
        cookie=TEST_USER_COOKIES,
    )


class TestAccountRegisterPhonishBase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        login_mock = mock.Mock()
        login_mock.return_value = TEST_LOGIN1
        self.env.patches.append(mock.patch('passport.backend.core.types.login.login.generate_phonish_login', login_mock))
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_phonish']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN1: 'free'}),
        )

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self._setup_statbox_entries()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def _setup_statbox_entries(self):
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            mode='account_register_phonish',
            track_id=self.track_id,
        )

        env = dict(
            mode='account_register_phonish',
            track_id=self.track_id,
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )

        self.env.statbox.bind_entry(
            'account_created',
            _exclude={
                'is_suggested_login',
                'karma',
                'password_quality',
                'suggest_generation_number',
            },
            action='account_created',
            login=TEST_LOGIN1,
            **env
        )

        self.env.statbox.bind_entry(
            'login_phonish',
            action='login_phonish',
            uid=str(TEST_UID1),
            login=TEST_LOGIN1,
            phone_number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
            phone_id=str(TEST_PHONE_ID1),
            **env
        )

        self.env.statbox.bind_entry(
            'account_modification',
            _exclude={'mode', 'track_id'},
            operation='created',
            old='-',
            **env
        )
        self.env.statbox.bind_entry(
            'alias_phonish',
            _inherit_from='account_modification',
            _exclude={'old'},
            operation='added',
            entity='aliases',
            type=str(ANT['phonish']),
            value=TEST_LOGIN1,
        )
        self.env.statbox.bind_entry(
            'person.language',
            _inherit_from='account_modification',
            entity='person.language',
            new='ru',
        )
        self.env.statbox.bind_entry(
            'person.country',
            _inherit_from='account_modification',
            entity='person.country',
            new='ru',
        )

        self.env.statbox.bind_entry(
            'disabled_status',
            _inherit_from='account_modification',
            entity='account.disabled_status',
            old='-',
            new='enabled',
        )
        self.env.statbox.bind_entry(
            'global_logout',
            _inherit_from='account_modification',
            entity='account.global_logout_datetime',
            operation='updated',
            old=str(datetime.fromtimestamp(1)),
            new=DatetimeNow(convert_to_datetime=True),
            uid=str(TEST_UID1),
        )

        self.env.statbox.bind_entry(
            'frodo_karma',
            _exclude={'mode', 'track_id'},
            action='account_register',
            login=TEST_LOGIN1,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
            **env
        )

        self.env.statbox.bind_entry(
            'subscriptions',
            _exclude={'mode', 'track_id'},
            operation='added',
            **env
        )
        self.env.statbox.bind_entry(
            'passport_sid',
            _inherit_from='subscriptions',
            sid='8',
        )
        self.env.statbox.bind_entry(
            'phonish_sid',
            _inherit_from='subscriptions',
            sid='68',
        )

        phone_env = merge_dicts(
            env,
            {
                'login': TEST_LOGIN1,
                'number': TEST_PHONE_NUMBER1.masked_format_for_statbox,
            },
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _exclude=['operation_id'],
            code_checks_count='0',
            **phone_env
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _exclude=['operation_id'],
            **phone_env
        )
        self.env.statbox.bind_entry(
            'registration_with_sms_limit_exceeded',
            mode='account_register_phonish',
            track_id=self.track_id,
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            ip=TEST_USER_IP,
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )
        self.env.statbox.bind_entry(
            'registration_with_sms_per_phone_limit_exceeded',
            mode='account_register_phonish',
            track_id=self.track_id,
            action='registration_with_sms',
            error='registration_sms_per_phone_limit_has_exceeded',
            is_phonish='1',
            counter_prefix='registration:sms:phonish',
        )

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/account/register/phonish/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def statbox_params(self, **account_created_kwargs):
        phone_entries = [
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('simple_phone_bound'),
        ]

        return (
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('disabled_status'),
                self.env.statbox.entry('alias_phonish'),
                self.env.statbox.entry('person.language'),
                self.env.statbox.entry('person.country'),

                # Карма 0 пишется в любом случае при создании аккаунта.
                self.env.statbox.entry('frodo_karma'),

                self.env.statbox.entry('passport_sid'),
                self.env.statbox.entry('phonish_sid'),
                self.env.statbox.entry('account_created', **account_created_kwargs),
            ] +
            phone_entries
        )

    def get_registration_sms_per_ip_counter(self):
        return sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)

    def get_registration_sms_per_phone_counter(self):
        return sms_per_phone.get_per_phone_on_registration_buckets(is_phonish=True)


@with_settings_hosts(
    AUTH_PHONISH_BY_PHONE_CONFIRMATION_ENABLED=True,
    FRODO_URL='http://localhost/',
    IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=True,
    **mock_counters()
)
class TestAccountRegisterPhonish(TestAccountRegisterPhonishBase):
    def test_without_need_headers(self):

        rv = self.account_register_request(
            self.query_params(),
            {},
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Missing required headers: "Ya-Client-User-Agent, Ya-Consumer-Client-Ip"',
                    u'code': u'missingheader',
                }],
            },
        )

    def test_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'User was not verified',
                    u'code': u'usernotverifiederror',
                }],
            },
        )

    def test_phone_confirmed_by_flash_call(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_flash_call'

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'User was not verified',
                    u'code': u'usernotverifiederror',
                }],
            },
        )

    def test_register(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_register_phonish_response(rv)

        self.assert_ok_db()

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'info.login': TEST_LOGIN1,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.tz': 'Europe/Moscow',
                'info.lang': 'ru',
                'info.country': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'sid.add': ','.join(['|'.join(['8', TEST_LOGIN1]), '|'.join(['68', TEST_LOGIN1])]),
                'alias.phonish.add': TEST_LOGIN1,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',

                'phone.1.action': 'created',
                'phone.1.number': TEST_PHONE_NUMBER1.e164,
                'phone.1.created': TimeNow(),
                'phone.1.confirmed': TimeNow(),
                'phone.1.bound': TimeNow(),
            },
        )

        self.env.statbox.assert_has_written(self.statbox_params(retpath=TEST_RETPATH))

        counter = self.get_registration_sms_per_ip_counter()
        eq_(counter.get(TEST_USER_IP), 1)

    def test_registration_already_completed_error(self):

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        # Счетчик СМС увеличивается только один раз
        counter = self.get_registration_sms_per_ip_counter()
        eq_(counter.get(TEST_USER_IP), 1)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': None,
                    u'message': u'Repeated usage of the same track for registration',
                    u'code': u'registrationalreadycompletederror',
                }],
            },
        )
        eq_(counter.get(TEST_USER_IP), 1)

    def test_register_phonish__sms_limit_per_ip_exceeded__statbox_not_logged(self):
        counter = self.get_registration_sms_per_ip_counter()
        for i in range(counter.limit - 1):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        self.assert_ok_register_phonish_response(rv)
        ok_(counter.hit_limit(TEST_USER_IP))
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_blacklisted_ip_register_phonish(self):
        with mock.patch(
            'passport.backend.api.common.ip.is_ip_blacklisted',
            return_value=True,
        ):
            rv = self.account_register_request(
                self.query_params(),
                build_headers(),
            )
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        ok_('error' not in self.get_events_from_handler(self.env.statbox_handle_mock))

    def test_register_phonish__sms_limit_per_ip_already_exceeded__error_and_statbox_logged(self):
        counter = self.get_registration_sms_per_ip_counter()
        for i in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'Reached limit for sms per ip in registration',
                    'code': 'registrationsmssendperiplimitexceeded',
                }],
            },
        )

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'registration_with_sms_limit_exceeded',
                    counter_current_value=str(counter.limit),
                    counter_limit_value=str(counter.limit),
                ),
            ],
            offset=-1,
        )

    def test_register_phonish_sms_limit_per_phone_already_exceeded__error_and_statbox_logged(self):
        counter = self.get_registration_sms_per_phone_counter()
        for i in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER1.e164)

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'Reached limit for sms per ip in registration',
                    'code': 'registrationsmssendperiplimitexceeded',
                }],
            },
        )

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'registration_with_sms_per_phone_limit_exceeded',
                    counter_current_value=str(counter.limit),
                    counter_limit_value=str(counter.limit),
                ),
            ],
            offset=-1,
        )

    def test_with_phone_is_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164

        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_register_phonish_response(rv)

        self.assert_ok_db()

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': 'dev',
                'info.login': TEST_LOGIN1,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.tz': 'Europe/Moscow',
                'info.lang': 'ru',
                'info.country': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'sid.add': ','.join(['|'.join(['8', TEST_LOGIN1]), '|'.join(['68', TEST_LOGIN1])]),
                'alias.phonish.add': TEST_LOGIN1,
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'user_agent': 'curl',

                'phone.1.action': 'created',
                'phone.1.number': TEST_PHONE_NUMBER1.e164,
                'phone.1.created': TimeNow(),
                'phone.1.confirmed': TimeNow(),
                'phone.1.bound': TimeNow(),
            },
        )

        self.env.statbox.assert_has_written(self.statbox_params())

    def test_new_ivory_coast_phonish_with_deprecated_8_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_ivory_coast_phonish_with_10_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def check_new_ivory_coast_phonish_always_has_10_digits_phone(self, user_entered_phone_number):
        """
        Проверяем, что новые фониши из Кот-Д'Ивуара регистрируются с новым
        номером, даже если пользователь вводит старый.
        """
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone_number.e164

        rv = self.account_register_request(self.query_params(), build_headers())

        self.assert_ok_register_phonish_response(rv)
        self.assert_ok_db(phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_ivory_coast_phonish_with_not_deprecated_8_digits_phone(self):
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164

        with settings_context(IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=False):
            rv = self.account_register_request(self.query_params(), build_headers())

        self.assert_ok_register_phonish_response(rv)
        self.assert_ok_db(phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def assert_ok_register_phonish_response(self, rv):
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def assert_ok_db(self, phone_number=None):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER1

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=1,
            phone_attributes={
                'id': 1,
                'number': phone_number.e164,
                'confirmed': DatetimeNow(),
            },
            binding_flags=binding_flags,
        )

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 4)

        self.env.db.check('aliases', 'phonish', TEST_LOGIN1, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', TimeNow(), uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.user_defined_login', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.firstname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.lastname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.timezone', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.language', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.quality', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.update_datetime', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')


@with_settings_hosts(
    APP_ID_TO_PHONISH_NAMESPACE={'app_id2': 'space2'},
    AUTH_PHONISH_BY_PHONE_CONFIRMATION_ENABLED=True,
    PERIOD_OF_PHONE_NUMBER_LOYALTY=TEST_PERIOD_OF_PHONE_NUMBER_LOYALTY,
    RECENT_ACCOUNT_USAGE_PERIOD=TEST_RECENT_ACCOUNT_USAGE_PERIOD,
    **mock_counters()
)
class TestReusePhonishAccount(TestAccountRegisterPhonishBase):
    def setUp(self):
        # Привязанный к фонишу телефон
        self.phonish_phone_number = TEST_PHONE_NUMBER1
        super(TestReusePhonishAccount, self).setUp()

    def test_ok(self):
        self._given_account()

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID1,
                'is_new_account': False,
            },
        )

        self._assert_db_phonish_phone_bound_ok()
        self._assert_db_account_global_logout()

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID1))
        eq_(track.login, TEST_LOGIN1)
        ok_(track.is_web_sessions_logout)
        ok_(track.allow_oauth_authorization)

        self.env.blackbox.requests[0].assert_query_contains({
            'method': 'phone_bindings',
            'type': 'current',
        })
        self.assert_blackbox_phone_bindings_request_ok(self.env.blackbox.requests[0])
        self.env.blackbox.requests[1].assert_post_data_contains({
            'method': 'userinfo',
        })

        ok_(
            self.env.historydb_api.requests[0].method_equals(
                'lastauth',
                self.env.historydb_api,
            ),
        )

        self.env.event_logger.assert_events_are_logged({
            'action': 'login_phonish',
            'info.glogout': TimeNow(),
            'phone.17.action': 'changed',
            'phone.17.number': TEST_PHONE_NUMBER1.e164,
            'phone.17.confirmed': TimeNow(),
            'user_agent': TEST_USER_AGENT,
            'consumer': 'dev',
        })

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('global_logout'),
            self.env.statbox.entry('login_phonish'),
        ])

    def test_ok_with_custom_namespace(self):
        self._given_account(namespace='space2')

        rv = self.account_register_request(self.query_params(app_id='app_id2'), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID1,
                'is_new_account': False,
            },
        )

    def test_not_phonish(self):
        """
        Есть аккаунт с привязанным номером, но не phonish.
        """
        self._given_account(is_phonish=False, login=TEST_LOGIN2)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_another_namespace(self):
        """
        Есть аккаунт с привязанным номером, но в другом неймспейсе.
        """
        self._given_account(login=TEST_LOGIN2)

        rv = self.account_register_request(self.query_params(app_id='app_id2'), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_phone_not_bound(self):
        """
        Нет аккаунтов с подтвеждённым номером.
        """
        self._given_account(is_phonish=False, bound_at=None, login=TEST_LOGIN2)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_phone_bindings_fail(self):
        self._given_account()
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_json_error_response('DB_EXCEPTION'),
        )

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 503)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'Blackbox failed',
                    'code': 'blackboxfailed',
                }],
            },
        )

    def test_userinfo_fail(self):
        self._given_account()
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_json_error_response('DB_EXCEPTION'),
        )

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 503)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'Blackbox failed',
                    'code': 'blackboxfailed',
                }],
            },
        )

    def test_confirmation_too_old(self):
        self._given_account(
            login=TEST_LOGIN2,
            confirmed_at=datetime.now() - TEST_PERIOD_OF_PHONE_NUMBER_LOYALTY,
        )

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_no_lastauth(self):
        """
        Записи lastauth нет, но аккаунт зарегистрирован недавно.
        """
        self._given_account(lastauth_at=None)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID1,
                'is_new_account': False,
            },
        )

    def test_old_but_active(self):
        """
        Аккаунт зарегистрирован давно, но использовался недавно.
        """
        self._given_account(registered_at=datetime.now() - TEST_RECENT_ACCOUNT_USAGE_PERIOD)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID1,
                'is_new_account': False,
            },
        )

    def test_old_not_active(self):
        """
        Аккаунтом давно не пользовались.
        """
        self._given_account(
            login=TEST_LOGIN2,
            registered_at=datetime.now() - TEST_RECENT_ACCOUNT_USAGE_PERIOD,
            lastauth_at=time.time() - TEST_RECENT_ACCOUNT_USAGE_PERIOD.total_seconds(),
        )

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_lastauth_failed(self):
        self._given_account()
        self.env.historydb_api.set_response_value(
            'lastauth',
            historydb_api_error_response(),
        )

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 503)
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [{
                    'field': None,
                    'message': 'HistoryDB API failed',
                    'code': 'historydbapifailed',
                }],
            },
        )

    def test_race__unbind_phone(self):
        """
        Номер отвязали от учётной записи между вызовами phone_bindings и
        userinfo.
        """
        before = self._build_account(login=TEST_LOGIN2)
        self._setup_multi_phone_bindings([before])
        after = self._build_account(login=TEST_LOGIN2, bound_at=None)
        self._setup_multi_userinfo([after])
        self._setup_multi_db([after])

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
                'is_new_account': True,
            },
        )

    def test_many__last_active_uid1(self):
        self._test_many__select_last_active(
            uid1_lastauth_at=time.time(),
            uid2_lastauth_at=time.time() - 60,
            expected_uid=TEST_UID1,
        )

    def test_many__last_active_uid2(self):
        self._test_many__select_last_active(
            uid1_lastauth_at=time.time() - 120,
            uid2_lastauth_at=time.time() - 60,
            expected_uid=TEST_UID2,
        )

    def _test_many__select_last_active(self, uid1_lastauth_at, uid2_lastauth_at,
                                       expected_uid):
        account1 = self._build_account(lastauth_at=uid1_lastauth_at)
        account2 = self._build_account(
            login=TEST_LOGIN2,
            uid=TEST_UID2,
            phone_id=TEST_PHONE_ID2,
            phone_number=TEST_PHONE_NUMBER1,
            lastauth_at=uid2_lastauth_at,
        )
        self._setup_multi_accounts([account1, account2])

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': expected_uid,
                'is_new_account': False,
            },
        )

    def test_account_disabled(self):
        self._given_account(is_disabled=True)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [
                    {
                        'code': 'accountdisabled',
                        'message': 'Account is disabled',
                        'field': None,
                    },
                ],
            },
        )

    def test_account_disabled__many_accounts(self):
        account1 = self._build_account(
            lastauth_at=time.time(),
            is_disabled=True,
        )
        account2 = self._build_account(
            login=TEST_LOGIN2,
            uid=TEST_UID2,
            phone_id=TEST_PHONE_ID2,
            phone_number=TEST_PHONE_NUMBER1,
            lastauth_at=time.time() - 60,
        )
        self._setup_multi_accounts([account1, account2])

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'error',
                'errors': [
                    {
                        'code': 'accountdisabled',
                        'message': 'Account is disabled',
                        'field': None,
                    },
                ],
            },
        )

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
        self.phonish_phone_number = account_phone_number

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone_number.e164

        self._given_account(phone_number=account_phone_number)

        rv = self.account_register_request(self.query_params(), build_headers())

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': TEST_UID1,
                'is_new_account': False,
            },
        )

        self._assert_db_phonish_phone_bound_ok()

        self.assert_blackbox_phone_bindings_request_ok(
            self.env.blackbox.requests[0],
            phone_numbers=[user_entered_phone_number.e164, account_phone_number.e164],
        )

        e = EventCompositor()
        e('action', 'login_phonish')
        e('info.glogout', TimeNow())
        with e.prefix('phone.17.'):
            e('action', 'changed')
            e('number', account_phone_number.e164)
            e('confirmed', TimeNow())
        e('user_agent', TEST_USER_AGENT)
        e('consumer', 'dev')
        self.env.event_logger.assert_events_are_logged(e.to_lines())

        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('global_logout'),
                self.env.statbox.entry(
                    'login_phonish',
                    phone_number=account_phone_number.masked_format_for_statbox,
                ),
            ],
        )

    def _given_account(self, **kwargs):
        account = self._build_account(**kwargs)
        self._setup_multi_accounts([account])

    def _setup_multi_accounts(self, accounts):
        self._setup_multi_userinfo(accounts)
        self._setup_multi_db(accounts)
        self._setup_multi_phone_bindings(accounts)
        self._setup_multi_lastauth(accounts)

    def _setup_multi_userinfo(self, accounts):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([a['userinfo'] for a in accounts]),
        )

    def _setup_multi_db(self, accounts):
        for account in accounts:
            userinfo_kwargs = account['userinfo']
            userinfo_response = blackbox_userinfo_response(**userinfo_kwargs)
            self.env.db.serialize(userinfo_response)

    def _setup_multi_phone_bindings(self, accounts):
        phone_bindings = []
        for account in accounts:
            account_bindings = account['userinfo'].get('phone_bindings', [])
            for binding in account_bindings:
                if binding['number'] == self.phonish_phone_number.e164:
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

    def _setup_multi_lastauth(self, accounts):
        responses = []
        for account in accounts:
            if account['lastauth'] is not None:
                response = lastauth_response(timestamp=account['lastauth'])
            else:
                response = lastauth_response(_type=None)
            responses.append(response)
        self.env.historydb_api.set_response_side_effect('lastauth', responses)

    def _build_account(self, registered_at=None, is_phonish=True,
                       bound_at=Undefined, confirmed_at=Undefined,
                       login=TEST_LOGIN1, uid=TEST_UID1,
                       phone_id=TEST_PHONE_ID1,
                       phone_number=Undefined, is_disabled=False,
                       lastauth_at=Undefined, namespace=None, **kwargs):
        if bound_at is Undefined:
            bound_at = TEST_TIME
        if phone_number is Undefined:
            phone_number = self.phonish_phone_number

        if registered_at is None:
            registered_at = datetime.now() - TEST_RECENT_ACCOUNT_USAGE_PERIOD + timedelta(minutes=1)

        if confirmed_at is Undefined:
            # Телефон подтвеждался не очень давно
            confirmed_at = datetime.now() - TEST_PERIOD_OF_PHONE_NUMBER_LOYALTY + timedelta(minutes=1)

        kwargs = {'uid': uid}

        kwargs['dbfields'] = {'userinfo.reg_date.uid': registered_at.strftime('%Y-%m-%d %H:%M:%S')}
        kwargs['attributes'] = {'account.is_disabled': str(int(is_disabled))}

        if is_phonish:
            kwargs['aliases'] = {'phonish': login}

        if namespace is not None:
            kwargs['attributes']['account.phonish_namespace'] = namespace

        if bound_at is not None:
            binding_flags = PhoneBindingsFlags()
            if is_phonish:
                binding_flags.should_ignore_binding_limit = True

            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=phone_id,
                    phone_number=phone_number.e164,
                    phone_created=bound_at,
                    phone_bound=bound_at,
                    phone_confirmed=confirmed_at,
                    binding_flags=binding_flags,
                ),
            )
        elif confirmed_at is not None:
            kwargs = deep_merge(
                kwargs,
                build_phone_unbound(
                    phone_id=phone_id,
                    phone_number=phone_number.e164,
                    phone_created=confirmed_at,
                    phone_confirmed=confirmed_at,
                ),
            )

        if lastauth_at is Undefined:
            # Пользователь входил не очень давно
            lastauth_at = time.time() - TEST_RECENT_ACCOUNT_USAGE_PERIOD.total_seconds() + 60

        return {
            'userinfo': kwargs,
            'lastauth': lastauth_at,
        }

    def _assert_db_phonish_phone_bound_ok(self):
        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID1,
            phone_attributes={
                'id': TEST_PHONE_ID1,
                'number': self.phonish_phone_number.e164,
                'confirmed': DatetimeNow(),
            },
            binding_flags=binding_flags,
        )

    def _assert_db_account_global_logout(self):
        self.env.db.check_db_attr(
            TEST_UID1,
            'account.global_logout_datetime',
            TimeNow(),
        )

    def assert_blackbox_phone_bindings_request_ok(self, request, phone_numbers=None):
        if phone_numbers is None:
            phone_numbers = [TEST_PHONE_NUMBER1.e164]
        self.env.blackbox.requests[0].assert_query_equals(
            dict(
                format='json',
                method='phone_bindings',
                numbers=','.join(phone_numbers),
                type='current',
            ),
        )


@with_settings_hosts(
    FRODO_URL='http://localhost/',
    PERMANENT_COOKIE_TTL=5,
    AUTH_PHONISH_BY_PHONE_CONFIRMATION_ENABLED=True,
)
class TestAccountRegisterPhonishTrackContent(TestAccountRegisterPhonishBase):
    def test_basic(self):
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1')
        eq_(track.login, TEST_LOGIN1)
        eq_(track.human_readable_login, TEST_LOGIN1)
        eq_(track.machine_readable_login, TEST_LOGIN1)

        eq_(track.language, 'ru')
        eq_(track.country, 'ru')
        eq_(track.have_password, False)
        eq_(track.is_successful_registered, True)
        eq_(track.allow_authorization, False)
        eq_(track.allow_oauth_authorization, True)
