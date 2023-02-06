# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_IP,
    TEST_PHONE,
    TEST_PHONE_BOUND,
    TEST_PHONE_CONFIRMED,
    TEST_PHONE_DUMP_MASKED,
    TEST_PHONE_OBJECT,
    TEST_PHONE_SECURED,
    TEST_SOCIAL_DISPLAY_NAME,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.counters import login_restore_counter
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
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
from passport.backend.utils.common import deep_merge


TEST_DEVICE_APPLICATION = 'test.device.application'
TEST_FIRSTNAME = u'Петр'
TEST_FIRSTNAME_INEXACT = u'Pertr'
TEST_LASTNAME = u'Петров'
TEST_LASTNAME_INEXACT = u'Petroff'


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    ALLOW_REGISTRATION=True,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=False,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
    )
)
class TestCheckNamesSimpleView(BaseBundleTestViews):
    default_url = '/1/bundle/restore/login/check_names/simple/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_IP,
    }
    http_query_args = {
        'firstname': TEST_FIRSTNAME,
        'lastname': TEST_LASTNAME,
        'allow_disabled': False,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.avatar_size = TEST_AVATAR_SIZE
            track.phone_confirmation_phone_number = TEST_PHONE
            track.phone_confirmation_is_confirmed = True
            track.device_application = TEST_DEVICE_APPLICATION
        self.http_query_args.update(track_id=self.track_id)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'login_restore': ['simple']},
            ),
        )

        accounts = [
            self.build_account(
                uid=1,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME_DATA,
                has_plus=True,
            ),
            self.build_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                firstname=TEST_FIRSTNAME_INEXACT,
                lastname=TEST_LASTNAME_INEXACT,
                alias_type='pdd',
                display_name=TEST_DISPLAY_NAME_DATA,
                has_totp=True,
            ),
            self.build_account(uid=3, firstname='123', lastname='345'),
            self.build_account(
                uid=4,
                disabled_status=ACCOUNT_DISABLED_ON_DELETION,
            ),
            self.build_account(
                uid=5,
                disabled_status=ACCOUNT_DISABLED,
            ),
            self.build_account(
                uid=6,
                alias_type='phonish',
            ),
            self.build_account(
                uid=7,
                has_secure_phone=False,
                has_bound_phone=True,
            ),
            self.build_account(
                uid=8,
                has_secure_phone=False,
                has_bound_phone=False,
            ),
            self.build_account(
                uid=9,
                lastname=None,
            ),
            self.build_account(
                uid=10,
                alias_type='social',
                login='uid-xxx',
                display_name=TEST_SOCIAL_DISPLAY_NAME,
            ),
            self.build_account(
                uid=11,
                alias_type='neophonish',
                login='nphne-xxx',
                display_name=TEST_DISPLAY_NAME_DATA,
            ),
            self.build_account(
                uid=12,
                login='child',
                display_login='the child',
                has_family=True,
                is_child=True,
            )
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts)

    def tearDown(self):
        del self.track_manager
        self.env.stop()
        del self.env

    def build_account(
        self,
        uid=TEST_UID,
        login=TEST_LOGIN,
        alias_type='portal',
        disabled_status=ACCOUNT_ENABLED,
        has_secure_phone=True,
        has_bound_phone=False,
        firstname=TEST_FIRSTNAME,
        lastname=TEST_LASTNAME,
        phone_number=None,
        has_plus=False,
        has_totp=False,
        has_family=False,
        is_child=False,
        **kwargs
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_OBJECT

        kwargs.update({
            'uid': uid,
            'login': login,
            'attributes': {
                'person.firstname': firstname,
                'person.lastname': lastname,
                'account.is_disabled': str(disabled_status),
            },
            'aliases': {
                alias_type: login,
            },
            'default_avatar_key': TEST_AVATAR_KEY,
        })
        if has_plus:
            kwargs['attributes']['account.have_plus'] = '1'
        if is_child:
            kwargs['attributes']['account.is_child'] = '1'
        if has_totp:
            kwargs['attributes']['account.2fa_on'] = '1'
        if has_family:
            kwargs['family_info'] = {
                'family_id': 'f1',
                'admin_uid': 42,
            }
        if has_secure_phone:
            kwargs = deep_merge(
                kwargs,
                build_phone_secured(
                    phone_id=1,
                    phone_number=phone_number.e164,
                    phone_created=TEST_PHONE_BOUND,
                    phone_bound=TEST_PHONE_BOUND,
                    phone_confirmed=TEST_PHONE_CONFIRMED,
                    phone_secured=TEST_PHONE_SECURED,
                ),
            )
        elif has_bound_phone:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=1,
                    phone_number=phone_number.e164,
                    phone_created=TEST_PHONE_BOUND,
                    phone_bound=TEST_PHONE_BOUND,
                    phone_confirmed=TEST_PHONE_CONFIRMED,
                ),
            )

        return kwargs

    def setup_accounts(self, accounts):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple(accounts),
        )

    def setup_phone_bindings(self, accounts, phone_numbers=None):
        if phone_numbers is None:
            phone_numbers = [TEST_PHONE_OBJECT]

        e164_phone_set = {p.e164 for p in phone_numbers}

        phone_bindings = []
        for account in accounts:
            account_bindings = account.get('phone_bindings', [])
            for binding in account_bindings:
                if binding['number'] in e164_phone_set:
                    phone_bindings.append(
                        dict(
                            binding,
                            uid=account['uid'],
                        ),
                    )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 1,
                    'has_plus': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'neophonish',
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

        eq_(login_restore_counter.get_per_phone_buckets().get(TEST_PHONE_OBJECT.digital), 0)
        eq_(login_restore_counter.get_per_ip_buckets().get(TEST_IP), 0)

    def test_ok_with_disabled(self):
        resp = self.make_request(query_args=dict(allow_disabled=True))
        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 1,
                    'has_plus': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 5,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'neophonish',
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

    def test_ok_with_all_account_types(self):
        resp = self.make_request(query_args=dict(allow_social=True, allow_neophonish=True))
        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 1,
                    'has_plus': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': 'uid-xxx',
                    'uid': 10,
                    'primary_alias_type': 6,
                    'display_name': TEST_SOCIAL_DISPLAY_NAME,
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': '',
                    'uid': 11,
                    'primary_alias_type': 21,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'phone_number': TEST_PHONE_DUMP_MASKED,
                    'allowed_auth_flows': ['instant'],
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

    def test_ok_with_instant(self):
        with settings_context(
            GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
            ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=True,
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 1,
                    'has_plus': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'phone_number': TEST_PHONE_DUMP_MASKED,
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'neophonish',
                'portal',
            ],
        )

    def test_nothing_found(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[],
            allowed_registration_flows=[
                'neophonish',
                'portal',
            ],
        )

        eq_(login_restore_counter.get_per_phone_buckets().get(TEST_PHONE_OBJECT.digital), 1)
        eq_(login_restore_counter.get_per_ip_buckets().get(TEST_IP), 1)

    def test_unable_to_register(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        with settings_context(ALLOW_REGISTRATION=False):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[],
            allowed_registration_flows=[],
        )

    def test_unable_to_register_neophonish(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        with settings_context(ALLOW_NEOPHONISH_REGISTRATION=False):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[],
            allowed_registration_flows=[
                'portal',
            ],
        )

    def test_rate_limit_exceeded_by_phone(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        for _ in range(3):
            login_restore_counter.get_per_phone_buckets().incr(TEST_PHONE_OBJECT.digital)

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])

    def test_rate_limit_exceeded_by_ip(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        for _ in range(3):
            login_restore_counter.get_per_ip_buckets().incr(TEST_IP)

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])

    def test_rate_limit_by_ip_whitelisted(self):
        for _ in range(3):
            login_restore_counter.get_per_ip_buckets().incr(TEST_IP)

        with settings_context(
            YANGO_APP_IDS=(TEST_DEVICE_APPLICATION,),
            TRUSTED_YANGO_PHONE_CODES=(TEST_PHONE[:2],),
            GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
            ALLOW_REGISTRATION=True,
            ALLOW_NEOPHONISH_REGISTRATION=True,
            ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=False,
            **mock_counters(
                LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
                LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
            )
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 1,
                    'has_plus': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'neophonish',
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

        eq_(login_restore_counter.get_per_phone_buckets().get(TEST_PHONE_OBJECT.digital), 0)
        eq_(login_restore_counter.get_per_ip_buckets().get(TEST_IP), 3)

    def test_new_ivory_coast_phone(self):
        self.check_ivory_coast_phone(
            account_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_old_ivory_coast_phone(self):
        self.check_ivory_coast_phone(
            account_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_ivory_coast_phone(self, account_phone_number, user_entered_phone_number):
        accounts = [
            self.build_account(
                alias_type='neophonish',
                login='nphne-xxx',
                phone_number=account_phone_number,
                uid=1,
                has_plus=True,
            ),
        ]
        self.setup_accounts(accounts)
        self.setup_phone_bindings(accounts, phone_numbers=[account_phone_number])

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone_number.e164

        resp = self.make_request(query_args=dict(allow_neophonish=True))

        self.assert_ok_response(
            resp,
            accounts=[
                {
                    'allowed_auth_flows': ['instant'],
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'default_avatar': TEST_AVATAR_KEY,
                    'display_name': {'name': ''},
                    'login': '',
                    'phone_number': account_phone_number.as_dict(only_masked=True),
                    'primary_alias_type': 21,
                    'uid': 1,
                    'has_plus': True,
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

        self.env.blackbox.requests[0].assert_query_equals(
            dict(
                format='json',
                method='phone_bindings',
                numbers=','.join(p.e164 for p in [user_entered_phone_number, account_phone_number]),
                type='current',
            ),
        )
