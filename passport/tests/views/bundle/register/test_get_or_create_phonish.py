# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_CONSUMER,
    TEST_HOST,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_ID3,
    TEST_PHONE_NUMBER1,
    TEST_PHONISH_LOGIN1,
    TEST_UID,
    TEST_UID1,
)
from passport.backend.core.authtypes import AUTH_TYPE_CALLER_ID
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import lastauth_response
from passport.backend.core.counters import register_phonish_by_phone
from passport.backend.core.historydb.statuses import SUCCESSFUL
from passport.backend.core.models.phones.faker import assert_simple_phone_bound
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
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_USER_IP = '37.9.101.188'


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    HISTORYDB_API_URL='http://localhost/',
    IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=True,
    **mock_counters(
        REGISTER_PHONISH_BY_PHONE_PER_CONSUMER_COUNTER=(60, 60, 5),
    )
)
class GetOrCreatePhonishTestCase(BaseBundleTestViews, StatboxTestMixin):
    default_url = '/1/bundle/account/get_or_create/phonish/'
    http_method = 'post'
    consumer = TEST_CONSUMER
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
    )
    base_phone_binding = {
        'bound': datetime.now(),
        'flags': 0,
        'type': 'current',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()

        login_mock = mock.Mock()
        login_mock.return_value = TEST_PHONISH_LOGIN1
        self.env.patches.append(mock.patch('passport.backend.core.types.login.login.generate_phonish_login', login_mock))
        self.env.patches.append(mock.patch('passport.backend.api.views.bundle.register.get_or_create.auth_log', self.env._auth_logger))

        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer=TEST_CONSUMER,
                grants={'account': ['get_or_create_phonish']},
            ),
        )
        self.track_id = None
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register_phonish',
            ip=TEST_USER_IP,
            user_agent='-',
            consumer=TEST_CONSUMER,
        )
        super(GetOrCreatePhonishTestCase, self).setup_statbox_templates()
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
            _exclude=['old', 'mode', 'track_id'],
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
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_phone_base'],
            _exclude=['operation_id'],
            code_checks_count='0',
        )

    def assert_db_ok(
        self,
        centraldb_queries=3,
        sharddb_queries=4,
        login=TEST_PHONISH_LOGIN1,
        phone_number=None,
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        timenow = TimeNow()
        dtnow = DatetimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'phonish', login, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=TEST_UID, db='passportdbshard1')

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = True
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': 1,
                'number': phone_number.e164,
                'confirmed': dtnow,
            },
            binding_flags=binding_flags,
        )

    def assert_historydb_ok(self, login=TEST_PHONISH_LOGIN1):
        timenow = TimeNow()

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_register',
                'consumer': TEST_CONSUMER,
                'info.login': login,
                'info.ena': '1',
                'info.disabled_status': '0',
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
            },
        )

    def assert_statbox_ok(self, login=TEST_PHONISH_LOGIN1):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['track_id'],
                operation='created',
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
                    'track_id',
                    'country',
                    'ip',
                },
                login=login,
                consumer=TEST_CONSUMER,
            ),
            self.env.statbox.entry(
                'phone_confirmed',
                _exclude=['user_agent', 'track_id', 'ip'],
            ),
            self.env.statbox.entry(
                'simple_phone_bound',
                _exclude=['operation_id', 'user_agent', 'track_id', 'ip'],
                mode='register_phonish',
                number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

    def test_rate_limit_error(self):
        counter = register_phonish_by_phone.get_per_consumer_counter()
        for _ in range(5):
            counter.incr(TEST_CONSUMER)
        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})
        self.assert_error_response(rv, ['rate.limit_exceeded'])

    def test_account_exists(self):
        phone_bindings = [
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER.e164,
                phone_id=TEST_PHONE_ID1,
                uid=TEST_UID,
            ),
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER1.e164,
                phone_id=TEST_PHONE_ID2,
                uid=TEST_UID1,
            ),
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'phonish': TEST_PHONISH_LOGIN1},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
                uids=[TEST_UID, TEST_UID1],
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
                lastauth_response(
                    uid=TEST_UID1,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})

        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            new_account=False,
        )

        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            [
                ('login', TEST_PHONISH_LOGIN1),
                ('type', AUTH_TYPE_CALLER_ID),
                ('status', SUCCESSFUL),
                ('uid', str(TEST_UID)),
                ('client_name', 'passport'),
            ],
        )

    def test_create_account_ok(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN1: 'free'}),
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})

        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            new_account=True,
        )
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()

    def test_bad_phone(self):
        rv = self.make_request(query_args={'phone_number': 'bad-phone'})
        self.assert_error_response(
            rv,
            ['phone_number.invalid'],
        )

    def test_account_disabled(self):
        phone_bindings = [
            dict(
                self.base_phone_binding,
                number=TEST_PHONE_NUMBER1.e164,
                phone_id=TEST_PHONE_ID2,
                uid=TEST_UID1,
            ),
        ]

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                enabled=False,
                aliases={'phonish': '_'},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
                uid=TEST_UID1,
            ),
        )
        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID1,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.international})

        self.assert_error_response(rv, ['account.disabled'])

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
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(
                [
                    dict(
                        self.base_phone_binding,
                        number=account_phone_number.e164,
                        phone_id=TEST_PHONE_ID1,
                        uid=TEST_UID,
                    ),
                ],
            ),
        )

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'phonish': TEST_PHONISH_LOGIN1},
                phones=[
                    dict(
                        bound=datetime.now(),
                        confirmed=datetime.now(),
                        created=datetime.now(),
                        id=TEST_PHONE_ID1,
                        number=account_phone_number.e164,
                    ),
                ],
                uid=TEST_UID,
            ),
        )

        self.env.historydb_api.set_response_side_effect(
            'lastauth',
            [
                lastauth_response(
                    uid=TEST_UID,
                    timestamp=datetime_to_integer_unixtime(datetime.now()),
                ),
            ],
        )

        rv = self.make_request(query_args=dict(phone_number=user_entered_phone_number.international))

        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            new_account=False,
        )

        self.env.blackbox.requests[0].assert_query_equals(
            dict(
                format='json',
                method='phone_bindings',
                numbers=','.join([user_entered_phone_number.e164, account_phone_number.e164]),
                type='current',
            ),
        )

    def test_new_ivory_coast_phonish_with_deprecated_8_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_ivory_coast_phonish_with_10_digits_phone(self):
        self.check_new_ivory_coast_phonish_always_has_10_digits_phone(TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def check_new_ivory_coast_phonish_always_has_10_digits_phone(self, user_entered_phone_number):
        """
        Проверяем, что новые фониши из Кот-Д'Ивуара регистрируются с новым
        номером, даже если пользователь вводит старый.
        """
        self.env.blackbox.set_response_value('phone_bindings', blackbox_phone_bindings_response([]))
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN1: 'free'}),
        )

        rv = self.make_request(query_args={'phone_number': user_entered_phone_number.international})

        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            new_account=True,
        )

        self.assert_db_ok(phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_ivory_coast_phonish_with_not_deprecated_8_digits_phone(self):
        self.env.blackbox.set_response_value('phone_bindings', blackbox_phone_bindings_response([]))
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN1: 'free'}),
        )

        with settings_context(IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=False):
            rv = self.make_request(query_args={'phone_number': TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.international})

        self.assert_ok_response(
            rv,
            uid=TEST_UID,
            new_account=True,
        )

        self.assert_db_ok(phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)
