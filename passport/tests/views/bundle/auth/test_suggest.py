# -*- coding: utf-8 -*-
from copy import deepcopy
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_profiles_response,
    profile_item,
)
from passport.backend.core.cookies import cookie_lah
from passport.backend.core.cookies.cookie_lah import (
    AuthHistoryContainer,
    CookieLAHUnpackError,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)


TEST_UID4 = 4
TEST_LOGIN4 = 'login4'
TEST_UID5 = 5
TEST_LOGIN5 = 'login5'
TEST_UID6 = 6
TEST_LOGIN6 = 'login6'
TEST_UID7 = 7
TEST_LOGIN7 = 'login7'
TEST_UID8 = 8
TEST_LOGIN8 = 'login8'
TEST_UNKNOWN_UID = 100
TEST_UNKNOWN_METHOD = 100500
TEST_DEFAULT_PERSON_INFO = {
    'display_name': {
        'default_avatar': u'',
        'name': u'',
    },
    'primary_alias_type': 1,
}


TEST_EXPECTED_ACCOUNTS_RESPONSE = [
    {
        'account': dict(
            display_login=TEST_LOGIN2,
            login=TEST_LOGIN2,
            uid=TEST_UID2,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_x_token',
            'social_fb',
        ],
        'preferred_auth_method': 'social_fb',  # взяли из истории
    },
    {
        'account': dict(
            display_login=TEST_LOGIN,
            login=TEST_LOGIN,
            uid=TEST_UID,
            has_plus=True,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'magic',
            'otp',
        ],
        'preferred_auth_method': 'magic',  # подобрали наиболее подходящий, так как предыдущий недоступен
    },
    {
        'account': dict(
            display_login=TEST_PDD_LOGIN,
            login=TEST_PDD_LOGIN,
            uid=TEST_PDD_UID,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_x_token',
        ],
        'preferred_auth_method': 'password',  # взяли из истории
    },
    {
        'account': dict(
            display_login=TEST_LOGIN3,
            login=TEST_LOGIN3,
            uid=TEST_UID3,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_x_token',
        ],
        'preferred_auth_method': 'password',  # подобрали наиболее подходящий, так как предыдущий неизвестен
    },
    {
        'account': dict(
            display_login=TEST_LOGIN4,
            login=TEST_LOGIN4,
            uid=TEST_UID4,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_x_token',
        ],
        'preferred_auth_method': 'password',  # подобрали наиболее подходящий, так как предыдущий не внесён в наши настройки
    },
    {
        'account': dict(
            display_login=TEST_LOGIN5,
            login=TEST_LOGIN5,
            uid=TEST_UID5,
            default_email='%s@yandex.ru' % TEST_LOGIN5,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_link',
            'magic_x_token',
        ],
        'preferred_auth_method': 'magic_link',
    },
    {
        'account': dict(
            display_login=TEST_LOGIN6,
            login=TEST_LOGIN6,
            uid=TEST_UID6,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [],
        'preferred_auth_method': None,
    },
    {
        # у пользователя отключен magic_link вход
        'account': dict(
            display_login=TEST_LOGIN7,
            login=TEST_LOGIN7,
            uid=TEST_UID7,
            default_email='%s@yandex.ru' % TEST_LOGIN7,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_x_token',
        ],
        'preferred_auth_method': 'password',
    },
    {
        # у пользователя отключен magic_x_token вход
        'account': dict(
            display_login=TEST_LOGIN8,
            login=TEST_LOGIN8,
            uid=TEST_UID8,
            default_email='%s@yandex.ru' % TEST_LOGIN8,
            **TEST_DEFAULT_PERSON_INFO
        ),
        'allowed_auth_methods': [
            'password',
            'magic_link',
        ],
        'preferred_auth_method': 'magic_link',
    },
]


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
)
class BaseSuggestTestCase(BaseBundleTestViews, EmailTestMixin):
    grants = {'account_suggest': ['read']}
    http_headers = {
        'cookie': 'lah=old_lah',
        'host': TEST_HOST,
        'user_ip': TEST_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants=self.grants))
        self.setup_service_responses()

        container = AuthHistoryContainer()
        container.add(TEST_UID, 123, 1, TEST_LOGIN)
        container.add(TEST_UID2, 456, 22, TEST_OTHER_LOGIN)
        container.add(TEST_PDD_UID, 789, 1, TEST_PDD_CYRILLIC_LOGIN)
        container.add(TEST_UNKNOWN_UID, 987, 2)
        container.add(TEST_UID3, 999, 0)
        container.add(TEST_UID4, 1000, TEST_UNKNOWN_METHOD)
        container.add(TEST_UID5, 1000, 4, TEST_LOGIN5)
        container.add(TEST_UID6, 1000, 5, TEST_LOGIN6)
        container.add(TEST_UID7, 1000, 4, TEST_LOGIN7)
        container.add(TEST_UID8, 1000, 4, TEST_LOGIN8)
        self._cookie_lah_unpack = mock.Mock(return_value=container)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.patches = (
            mock.patch.object(
                cookie_lah.CookieLAH,
                'unpack',
                self._cookie_lah_unpack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
        )
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self._cookie_lah_pack
        del self._cookie_lah_unpack

    def setup_service_responses(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {
                    'uid': TEST_UID,
                    'id': TEST_UID,
                    'login': TEST_LOGIN,
                    'attributes': {
                        'account.2fa_on': '1',
                        'account.have_plus': '1',
                    },
                },
                {
                    'uid': TEST_UID2,
                    'id': TEST_UID2,
                    'login': TEST_LOGIN2,
                    'crypt_password': '1:pwd',
                },
                {
                    'uid': TEST_UID3,
                    'id': TEST_UID3,
                    'login': TEST_LOGIN3,
                    'crypt_password': '1:pwd',
                },
                {
                    'uid': TEST_UID4,
                    'id': TEST_UID4,
                    'login': TEST_LOGIN4,
                    'crypt_password': '1:pwd',
                },
                {
                    'uid': TEST_UID5,
                    'id': TEST_UID5,
                    'login': TEST_LOGIN5,
                    'crypt_password': '1:pwd',
                    'emails': [self.env.email_toolkit.create_native_email(TEST_LOGIN5, 'yandex.ru')],
                },
                {
                    'uid': TEST_UID6,
                    'id': TEST_UID6,
                    'login': TEST_LOGIN6,
                    'subscribed_to': [67],
                    'attributes': {
                        'account.qr_code_login_forbidden': '1',
                    },
                },
                {
                    'uid': TEST_UID7,
                    'id': TEST_UID7,
                    'login': TEST_LOGIN7,
                    'crypt_password': '1:pwd',
                    'emails': [self.env.email_toolkit.create_native_email(TEST_LOGIN7, 'yandex.ru')],
                    'attributes': {
                        'account.magic_link_login_forbidden': '1',
                    },
                },
                {
                    'uid': TEST_UID8,
                    'id': TEST_UID8,
                    'login': TEST_LOGIN8,
                    'crypt_password': '1:pwd',
                    'emails': [self.env.email_toolkit.create_native_email(TEST_LOGIN8, 'yandex.ru')],
                    'attributes': {
                        'account.qr_code_login_forbidden': '1',
                    },
                },
                {
                    'uid': TEST_PDD_UID,
                    'id': TEST_PDD_UID,
                    'login': TEST_PDD_LOGIN,
                    'crypt_password': '1:pwd',
                    'attributes': {
                        'account.global_logout_datetime': '100500',
                    },
                },
                {
                    'id': TEST_UNKNOWN_UID,
                    'uid': None,
                },
            ]),
        )
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([
                profile_item(uid=TEST_UID2),
            ]),
        )


class TestGetSuggestView(BaseSuggestTestCase):
    default_url = '/1/bundle/auth/suggest/'
    http_method = 'GET'
    http_query_args = {'consumer': 'dev'}

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=TEST_EXPECTED_ACCOUNTS_RESPONSE,
            cookies=[
                EXPECTED_LAH_COOKIE,
            ],
            ignore_order_for=['accounts'],
        )

        new_container = self._cookie_lah_pack.call_args[1]['container']
        eq_(len(new_container), 9)
        eq_(new_container[0].uid, TEST_UID)
        eq_(new_container[1].uid, TEST_UID2)
        eq_(new_container[2].uid, TEST_PDD_UID)
        eq_(new_container[3].uid, TEST_UID3)
        eq_(new_container[4].uid, TEST_UID4)
        eq_(new_container[5].uid, TEST_UID5)
        eq_(new_container[6].uid, TEST_UID6)
        eq_(new_container[7].uid, TEST_UID7)
        eq_(new_container[8].uid, TEST_UID8)

        social_uids = [
            TEST_UID2, TEST_UID3, TEST_UID4, TEST_UID5, TEST_UID7, TEST_UID8,
            TEST_PDD_UID,
        ]
        eq_(len(self.env.social_api.requests), 1)
        self.env.social_api.requests[0].assert_query_equals(
            dict(
                consumer='passport',
                uids=','.join(map(str, social_uids)),
            )
        )

    def test_intranet_ok(self):
        with settings_context(
            BLACKBOX_URL='localhost',
            PASSPORT_SUBDOMAIN='passport-test',
            IS_INTRANET=True,
        ):
            resp = self.make_request()

        expected_accounts_response = deepcopy(TEST_EXPECTED_ACCOUNTS_RESPONSE)
        for exp in expected_accounts_response:
            if 'magic_x_token' in exp['allowed_auth_methods']:
                exp['allowed_auth_methods'].remove('magic_x_token')

        expected_accounts_response[0].update(
            allowed_auth_methods=[
                'password',
            ],
            preferred_auth_method='password',
        )
        self.assert_ok_response(
            resp,
            accounts=expected_accounts_response,
            cookies=[
                EXPECTED_LAH_COOKIE,
            ],
            ignore_order_for=['accounts'],
        )
        ok_(not self.env.social_api.requests)

    def test_unable_to_parse_cookie(self):
        self._cookie_lah_unpack.side_effect = CookieLAHUnpackError
        self._cookie_lah_pack.return_value = ''

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            accounts=[],
            cookies=[
                EMPTY_COOKIE_LAH,
            ],
        )
        new_container = self._cookie_lah_pack.call_args[1]['container']
        ok_(not new_container)


class TestDeleteFromSuggestView(BaseSuggestTestCase):
    default_url = '/1/bundle/auth/suggest/forget/?consumer=dev'
    http_method = 'POST'
    http_query_args = {'uid': TEST_UID}
    grants = {'account_suggest': ['read', 'edit']}

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cookies=[
                EXPECTED_LAH_COOKIE,
            ],
        )

        new_container = self._cookie_lah_pack.call_args[1]['container']
        eq_(len(new_container), 8)
        eq_(new_container[0].uid, TEST_UID2)
        eq_(new_container[1].uid, TEST_PDD_UID)
        eq_(new_container[2].uid, TEST_UID3)
        eq_(new_container[3].uid, TEST_UID4)
        eq_(new_container[4].uid, TEST_UID5)
        eq_(new_container[5].uid, TEST_UID6)
        eq_(new_container[6].uid, TEST_UID7)
        eq_(new_container[7].uid, TEST_UID8)

    def test_unable_to_parse_cookie(self):
        self._cookie_lah_unpack.side_effect = CookieLAHUnpackError
        self._cookie_lah_pack.return_value = ''

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cookies=[
                EMPTY_COOKIE_LAH,
            ],
        )
        new_container = self._cookie_lah_pack.call_args[1]['container']
        ok_(not new_container)


class TestGetSuggestedInputLoginView(BaseSuggestTestCase):
    default_url = '/1/bundle/auth/suggest/get_input_login/'
    http_method = 'GET'
    http_query_args = {'consumer': 'dev', 'uid': TEST_UID}
    grants = {'account_suggest': ['read']}

    def setUp(self):
        super(TestGetSuggestedInputLoginView, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            input_login=TEST_LOGIN,
        )

    def test_ok_for_cyrillic_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_CYRILLIC_LOGIN,
            ),
        )
        resp = self.make_request(query_args=dict(uid=TEST_PDD_UID))
        self.assert_ok_response(
            resp,
            input_login=TEST_PDD_CYRILLIC_LOGIN,
        )

    def test_empty_login(self):
        resp = self.make_request(query_args={'uid': TEST_UID3})
        self.assert_ok_response(
            resp,
            input_login=None,
        )

    def test_unknown_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            input_login=None,
        )

    def test_uid_mismatch(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_OTHER_UID,
                login=TEST_LOGIN,
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            input_login=None,
        )

    def test_uid_not_in_suggest(self):
        resp = self.make_request(query_args=dict(uid=42))
        self.assert_error_response(resp, ['account.not_in_suggest'])

    def test_unable_to_parse_cookie(self):
        self._cookie_lah_unpack.side_effect = CookieLAHUnpackError
        self._cookie_lah_pack.return_value = ''

        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_in_suggest'])


class TestCheckSuggestAvailabilityView(BaseSuggestTestCase):
    default_url = '/1/bundle/auth/suggest/check/'
    http_method = 'GET'
    http_query_args = {'consumer': 'dev'}

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_suggest_available=True,
        )

    def test_cookie_empty(self):
        self._cookie_lah_unpack.return_value = AuthHistoryContainer()

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_suggest_available=False,
        )

    def test_unable_to_parse_cookie(self):
        self._cookie_lah_unpack.side_effect = CookieLAHUnpackError

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            is_suggest_available=False,
        )
