# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.antifraud import AntifraudApiPermanentError
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_verified_cards_per_uid_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.historydb_api.faker import lastauth_bulk_response
from passport.backend.core.builders.phone_squatter import PhoneSquatterTemporaryError
from passport.backend.core.builders.phone_squatter.faker import phone_squatter_get_change_status_response
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
    ACCOUNT_ENABLED,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.common import deep_merge


TEST_AVATAR_SIZE = 'islands_xxl'

DEFAULT_TEST_SETTINGS = dict(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    ALLOW_REGISTRATION=True,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    USE_PHONE_SQUATTER=True,
    PHONE_SQUATTER_DRY_RUN=False,
)


class BaseSuggestAccountsByPhoneTestCase(BaseBundleTestViews):
    consumer = 'dev'
    http_method = 'GET'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'auth': ['suggest_by_phone']},
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
                uid=2,
            ),
            self.build_account(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                firstname=TEST_FIRSTNAME,
                lastname=TEST_LASTNAME,
                alias_type='pdd',
                display_name=TEST_DISPLAY_NAME_DATA,
                has_totp=True,
            ),
            self.build_account(
                uid=3,
                disabled_status=ACCOUNT_DISABLED_ON_DELETION,
            ),
            self.build_account(
                uid=4,
                disabled_status=ACCOUNT_DISABLED,
                has_family=True,
            ),
            self.build_account(
                uid=5,
                alias_type='phonish',
            ),
            self.build_account(
                uid=6,
                has_secure_phone=False,
                has_bound_phone=True,
            ),
            self.build_account(
                uid=7,
                has_secure_phone=False,
                has_bound_phone=False,
            ),
            self.build_account(
                uid=8,
                alias_type='social',
                login='uid-xxx',
                display_name=TEST_SOCIAL_DISPLAY_NAME,
            ),
            self.build_account(
                uid=9,
                alias_type='neophonish',
                login='nphne-xxx',
                display_name=TEST_DISPLAY_NAME_DATA,
            ),
            self.build_account(
                uid=10,
                phone_age=timedelta(days=367).total_seconds(),
            ),
            self.build_account(
                uid=11,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                phone_age=timedelta(days=90).total_seconds(),
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
        self.env.antifraud_api.set_response_value(
            'uid_cards',
            antifraud_verified_cards_per_uid_response(uids=[1, 8, 9])
        )
        self.env.historydb_api.set_response_value(
            'lastauth_bulk',
            lastauth_bulk_response({
                1: time() - 1,
                2: None,
                4: time() - 4,
                8: time() - 8,
                9: time() - 9,
                10: time() - 10,
                11: time() - 11,
                12: time() - 12,
                TEST_PDD_UID: time() - 42,
            }),
        )
        self.env.phone_squatter.set_response_value(
            'get_change_status',
            phone_squatter_get_change_status_response(change_unixtime=time() - 3600),
        )

    def tearDown(self):
        self.env.stop()

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
        phone_number=TEST_PHONE_NUMBER,
        phone_age=30,
        has_plus=False,
        has_totp=False,
        has_family=False,
        is_child=False,
        **kwargs
    ):
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
                    phone_created=datetime.fromtimestamp(1),
                    phone_bound=datetime.fromtimestamp(1),
                    phone_secured=datetime.fromtimestamp(1),
                    phone_confirmed=datetime.now() - timedelta(seconds=phone_age),
                ),
            )
        elif has_bound_phone:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=1,
                    phone_number=phone_number.e164,
                    phone_created=datetime.fromtimestamp(1),
                    phone_bound=datetime.fromtimestamp(1),
                    phone_confirmed=datetime.now() - timedelta(seconds=phone_age),
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
            phone_numbers = [TEST_PHONE_NUMBER]

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


class TestSuggestAccountsByPhoneCheckAvailabilityView(BaseSuggestAccountsByPhoneTestCase):
    default_url = '/1/bundle/auth/suggest/by_phone/check_availability/'
    http_query_args = {
        'phone_number': TEST_PHONE_NUMBER.e164,
    }

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_suggest_available=True,
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

    def test_nothing_found(self):
        self.setup_accounts([])
        self.setup_phone_bindings([])

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_suggest_available=False,
        )


@with_settings_hosts(**DEFAULT_TEST_SETTINGS)
class TestSuggestAccountsByPhoneListView(BaseSuggestAccountsByPhoneTestCase):
    default_url = '/1/bundle/auth/suggest/by_phone/list/'

    def setUp(self):
        super(TestSuggestAccountsByPhoneListView, self).setUp()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.avatar_size = TEST_AVATAR_SIZE
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
        self.http_query_args.update(track_id=self.track_id)

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
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': 'uid-xxx',
                    'uid': 8,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 6,
                    'display_name': {
                        'name': 'Some User',
                        'social': {
                            'provider': 'fb',
                            'profile_id': 123456,
                        },
                    },
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': '',
                    'uid': 9,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 21,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 4,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

    def test_af_failed__ok(self):
        self.env.antifraud_api.set_response_side_effect('uid_cards', AntifraudApiPermanentError)

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
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 4,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': 'uid-xxx',
                    'uid': 8,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 6,
                    'display_name': {
                        'name': 'Some User',
                        'social': {
                            'provider': 'fb',
                            'profile_id': 123456,
                        },
                    },
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': '',
                    'uid': 9,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 21,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

    def test_phone_squatter_dry_run__ok(self):
        with settings_context(**dict(DEFAULT_TEST_SETTINGS, PHONE_SQUATTER_DRY_RUN=True)):
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
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': 'uid-xxx',
                    'uid': 8,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 6,
                    'display_name': {
                        'name': 'Some User',
                        'social': {
                            'provider': 'fb',
                            'profile_id': 123456,
                        },
                    },
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': '',
                    'uid': 9,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 21,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 4,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 10,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 11,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

        eq_(len(self.env.blackbox.requests), 2)  # phone_bindings & userinfo
        self.env.blackbox.requests[1].assert_post_data_contains({'getphones': 'all'})

    def test_ignore_possible_phone_owner_change(self):
        with settings_context(**dict(DEFAULT_TEST_SETTINGS, IGNORE_POSSIBLE_PHONE_OWNER_CHANGE_FOR_UIDS=[2, 11])):
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
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': 'uid-xxx',
                    'uid': 8,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 6,
                    'display_name': {
                        'name': 'Some User',
                        'social': {
                            'provider': 'fb',
                            'profile_id': 123456,
                        },
                    },
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': '',
                    'uid': 9,
                    'has_plus': False,
                    'has_bank_card': True,
                    'has_family': False,
                    'primary_alias_type': 21,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['instant'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 4,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': True,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 11,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['instant', 'full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_PDD_LOGIN,
                    'uid': 1130000000000001,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 7,
                    'display_name': {'name': TEST_DISPLAY_NAME},
                    'allowed_auth_flows': ['full'],
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'avatar_url': TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
                    'login': TEST_LOGIN,
                    'uid': 2,
                    'has_plus': False,
                    'has_bank_card': False,
                    'has_family': False,
                    'primary_alias_type': 1,
                    'display_name': {'name': ''},
                    'allowed_auth_flows': ['instant', 'full'],
                },
            ],
            allowed_registration_flows=[
                'portal',
            ],
        )

    def test_phone_squatter_failed(self):
        self.env.phone_squatter.set_response_side_effect('get_change_status', PhoneSquatterTemporaryError)

        resp = self.make_request()
        self.assert_error_response(resp, ['backend.phone_squatter_failed'])

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
