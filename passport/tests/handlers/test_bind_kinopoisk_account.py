# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_DISABLED_STATUS,
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Kinopoisk import Kinopoisk
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    KINOPOISK_APPLICATION_ID1,
    KINOPOISK_APPLICATION_NAME1,
    PHONISH_LOGIN1,
    UID1,
    UID2,
    UID3,
    USER_IP1,
    USERNAME1,
    YANDEX_APPLICATION_ID2,
    YANDEX_APPLICATION_NAME2,
)
from passport.backend.social.common.test.fake_billing_api import (
    billing_api_invalidate_account_bindings_response,
    FakeBillingApi,
)
from passport.backend.social.common.test.types import DatetimeNow
from passport.backend.utils.common import deep_merge
from sqlalchemy import (
    and_ as sql_and,
    select as sql_select,
)


_SERVICE_TOKEN1 = 'service_token1'

_SESSION_ID_1 = 'session_id_1'
_SESSION_ID_2 = 'session_id_2'
_KINOPOISK_LOGIN = 'kinopoisk_login'
_KINOPOISK_USER_ID = '65432'
_KINOPOISK_CLIENT_ID = 'kinopoisk_client_id'
_YANDEX_SESSION_ID_1 = 'yandex_session_id_1'


class BindKinopoiskAccountTestCase(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_kinopoisk_account_by_token'
    REQUEST_HEADERS = {
        'Ya-Consumer-Authorization': 'Bearer %s' % APPLICATION_TOKEN1,
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'kinopoisk_session_id': _SESSION_ID_1,
        'kinopoisk_username': _KINOPOISK_LOGIN,
    }

    YANDEX_UID = UID1
    KINOPOISK_UID = UID2

    def setUp(self):
        super(BindKinopoiskAccountTestCase, self).setUp()

        self._fake_billing_api = FakeBillingApi()
        self._fake_billing_api.start()

        self._setup_statbox_templates()

    def tearDown(self):
        self._fake_billing_api.stop()
        super(BindKinopoiskAccountTestCase, self).tearDown()

    def _setup_environment(self, master_account=Undefined, slave_account=Undefined,
                           binding_exists=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['bind-kinopoisk-account-by-token'],
        )

        if master_account is Undefined:
            master_account = self._build_yandex_account()

        if slave_account is Undefined:
            slave_account = self._build_kinopoisk_account()

        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_response(**deep_merge(slave_account['userinfo'], slave_account['session'])),
            ],
        )

        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master_account['userinfo'], master_account['oauth'])),
            ],
        )

        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([
                    master_account['userinfo'],
                    slave_account['userinfo'],
                ]),
            ]
        )

        if binding_exists:
            self._create_binding(master_account['userinfo']['uid'], Kinopoisk, slave_account['userinfo']['uid'])

        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_invalidate_account_bindings_response(),
        )

    def _build_yandex_account(self, uid=YANDEX_UID, enabled=True, **kwargs):
        return dict(
            userinfo=dict(uid=uid),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
        )

    def _build_kinopoisk_account(self, uid=KINOPOISK_UID, enabled=True, completed=False, **kwargs):
        aliases = dict(kinopoisk=_KINOPOISK_USER_ID)
        if completed:
            aliases['portal'] = 'FOOBAR'
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=aliases,
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
            session=dict(
                status=BLACKBOX_SESSIONID_VALID_STATUS if enabled else BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

    def _build_phonish_account(self, uid=YANDEX_UID, enabled=True, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
                display_name={'name': USERNAME1},
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
        )

    def _setup_statbox_templates(self):
        self._fake_statbox.bind_entry(
            'update_account_bindings',
            action='update_account_yandex_bindings',
            consumer=CONSUMER1,
            ip=USER_IP1,
        )

    def _build_oauth_token(self, token_valid=True, account_enabled=True, token_scope=Undefined,
                           token_client_id=EXTERNAL_APPLICATION_ID1, **kwargs):
        if token_scope is Undefined:
            token_scope = X_TOKEN_SCOPE

        oauth = dict(
            scope=token_scope,
            client_id=token_client_id,
        )

        if token_valid:
            if not account_enabled:
                oauth.update(status=BLACKBOX_OAUTH_DISABLED_STATUS)
        else:
            oauth.update(status=BLACKBOX_OAUTH_INVALID_STATUS)

        return oauth

    def _assert_binding_exists(self, uid, provider, userid, username=_KINOPOISK_LOGIN):
        bindings = self._find_bindings(uid, provider, userid)
        self.assertEqual(len(bindings), 1)
        binding = bindings[0]

        self.assertEqual(binding.allow_auth, 0)
        self.assertEqual(binding.username, username)
        self.assertEqual(binding.created, DatetimeNow())
        self.assertEqual(binding.yandexuid, '')

    def _assert_binding_not_exist(self, uid, provider, userid):
        bindings = self._find_bindings(uid, provider, userid)
        self.assertEqual(len(bindings), 0)

    def _find_bindings(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = (
                sql_select([profile_table])
                .where(
                    sql_and(
                        profile_table.c.uid == uid,
                        profile_table.c.provider_id == provider.id,
                        profile_table.c.userid == userid,
                    ),
                )
            )
            return db.execute(query).fetchall()

    def _create_binding(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                uid=uid,
                provider_id=provider.id,
                userid=userid,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def build_settings(self):
        settings = super(BindKinopoiskAccountTestCase, self).build_settings()
        settings['social_config'].update(
            billing_http_api_retries=1,
            billing_http_api_timeout=1,
            billing_http_api_url='http://balance-simple.yandex.net:8028',
            billing_http_api_service_token=_SERVICE_TOKEN1,
            invalidate_billing_binding_cache=True,
        )
        return settings


class TestBindKinopoiskAccount(BindKinopoiskAccountTestCase):
    def test_bind(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=self.KINOPOISK_UID,
            provider=Kinopoisk,
            userid=self.YANDEX_UID,
        )

    def test_no_yandex_token(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Authorization'])
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_no_user_ip(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])

    def test_no_session_id(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['kinopoisk_session_id'])
        self._assert_error_response(rv, ['kinopoisk_session_id.empty'])

    def test_no_username(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['kinopoisk_username'])
        self._assert_error_response(rv, ['kinopoisk_username.empty'])

    def test_username(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': 'CUSTOM'})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='CUSTOM',
        )

    def test_username_empty(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': ''})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='',
        )

    def test_username_spaces(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': '   '})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='',
        )

    def test_no_grants(self):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[],
        )
        rv = self._make_request(
            data={'consumer': CONSUMER1},
            headers={'Ya-Consumer-Client-Ip': CONSUMER_IP1},
        )
        self._assert_error_response(rv, ['access.denied'])

    def test_statbox(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(self.YANDEX_UID),
            ),
        ])

    def test_invalid_yandex_token(self):
        self._setup_environment(master_account=self._build_yandex_account(enabled=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_token.invalid'])
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

    def test_invalind_kinopoisk_session(self):
        self._setup_environment(slave_account=self._build_kinopoisk_account(enabled=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['provider_token.invalid'])
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

    def test_binding_already_exists(self):
        self._setup_environment(binding_exists=True)
        rv = self._make_request()
        self._assert_ok_response(rv)

    def test_master_account_is_kinopoisk(self):
        self._setup_environment(master_account=self._build_kinopoisk_account(uid=self.YANDEX_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_master_account_is_phonish(self):
        self._setup_environment(master_account=self._build_phonish_account(uid=self.YANDEX_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_slave_account_is_completed_kinopoisk(self):
        self._setup_environment(slave_account=self._build_kinopoisk_account(completed=True))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_requests_to_blackbox(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        requests = self._fake_blackbox.requests
        self.assertEqual(len(requests), 3)
        requests[0].assert_query_contains({
            'method': 'oauth',
            'oauth_token': APPLICATION_TOKEN1,
            'userip': USER_IP1,
        })
        requests[1].assert_query_contains({
            'method': 'sessionid',
            'host': 'kinopoisk.ru',
            'sessionid': _SESSION_ID_1,
            'userip': USER_IP1,
        })
        requests[2].assert_post_data_contains({
            'method': 'userinfo',
            'uid': ','.join(map(str, [self.YANDEX_UID, self.KINOPOISK_UID])),
        })

    def test_requests_to_billing(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 2)
        for i, uid in enumerate([self.YANDEX_UID, self.KINOPOISK_UID]):
            self._fake_billing_api.requests[i].assert_properties_equal(
                method='POST',
                url='http://balance-simple.yandex.net:8028/trust-payments/v2/passport/%s/invalidate' % uid,
                headers={'X-Service-Token': _SERVICE_TOKEN1},
            )

    def test_bind_kp_binding_already_exists(self):
        self._setup_environment()
        self._create_binding(self.YANDEX_UID, Kinopoisk, UID3)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            username=USERNAME1,
            provider=Kinopoisk,
            userid=UID3,
        )

        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=UID3,
        )

    def test_bind_yandex_binding_already_exists(self):
        self._setup_environment()
        self._create_binding(UID3, Kinopoisk, self.KINOPOISK_UID)
        self._assert_binding_exists(
            uid=UID3,
            username=USERNAME1,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=UID3,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )


class TestBindKinopoiskAccountTokenFromKinopoisk(BindKinopoiskAccountTestCase):
    def build_settings(self):
        settings = super(TestBindKinopoiskAccountTokenFromKinopoisk, self).build_settings()
        settings['applications'] = [
            {
                'provider_id': Yandex.id,
                'application_id': YANDEX_APPLICATION_ID2,
                'application_name': YANDEX_APPLICATION_NAME2,
                'provider_client_id': _KINOPOISK_CLIENT_ID,
                'secret': APPLICATION_SECRET1,
                'domain': '.yandex.ru',
                'request_from_intranet_allowed': '1',
            },
            {
                'provider_id': Kinopoisk.id,
                'application_id': KINOPOISK_APPLICATION_ID1,
                'application_name': KINOPOISK_APPLICATION_NAME1,
                'provider_client_id': KINOPOISK_APPLICATION_NAME1,
                'secret': '',
                'domain': 'social.yandex.ru',
                'request_from_intranet_allowed': '1',
            },
        ]
        return settings

    def test_token_by_kinopoisk(self):
        self._setup_environment(
            master_account=self._build_yandex_account(
                token_scope='ololo:ololo',
                token_client_id=_KINOPOISK_CLIENT_ID,
            ),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_token_by_not_kinopoisk(self):
        self._setup_environment(
            master_account=self._build_yandex_account(
                token_scope='ololo:ololo',
                token_client_id='ololo',
            ),
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['yandex_token.invalid'])


class TestBindKinopoiskAccountBySessionId(BindKinopoiskAccountTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_kinopoisk_account_by_session_id'
    REQUEST_HEADERS = {
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'yandex_session_id': _YANDEX_SESSION_ID_1,
        'kinopoisk_session_id': _SESSION_ID_1,
        'kinopoisk_username': _KINOPOISK_LOGIN,
    }
    YANDEX_UID = UID1

    def _setup_environment(self, master_account=Undefined, slave_account=Undefined,
                           binding_exists=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['bind-kinopoisk-account-by-session-id'],
        )

        if master_account is Undefined:
            master_account = self._build_yandex_account()

        if slave_account is Undefined:
            slave_account = self._build_kinopoisk_account()

        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_response(**deep_merge(master_account['userinfo'], master_account['session'])),
                blackbox_sessionid_response(**deep_merge(slave_account['userinfo'], slave_account['session'])),
            ],
        )

        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([
                    master_account['userinfo'],
                    slave_account['userinfo'],
                ]),
            ]
        )

        if binding_exists:
            self._create_binding(master_account['userinfo']['uid'], Kinopoisk, slave_account['userinfo']['uid'])

        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_invalidate_account_bindings_response(),
        )

    def _build_yandex_account(self, uid=YANDEX_UID, enabled=True, **kwargs):
        return dict(
            userinfo=dict(uid=uid),
            session=dict(
                status=BLACKBOX_SESSIONID_VALID_STATUS if enabled else BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

    def _build_phonish_account(self, uid=YANDEX_UID, enabled=True, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
                display_name={'name': USERNAME1},
            ),
            session=dict(
                status=BLACKBOX_SESSIONID_VALID_STATUS if enabled else BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

    def test_bind(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=self.KINOPOISK_UID,
            provider=Kinopoisk,
            userid=self.YANDEX_UID,
        )

    def test_no_yandex_session_id(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['yandex_session_id'])
        self._assert_error_response(rv, ['yandex_session_id.empty'])

    def test_no_user_ip(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])

    def test_no_session_id(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['kinopoisk_session_id'])
        self._assert_error_response(rv, ['kinopoisk_session_id.empty'])

    def test_no_username(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['kinopoisk_username'])
        self._assert_error_response(rv, ['kinopoisk_username.empty'])

    def test_username(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': 'CUSTOM'})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='CUSTOM',
        )

    def test_username_empty(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': ''})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='',
        )

    def test_username_spaces(self):
        self._setup_environment()
        rv = self._make_request(data={'kinopoisk_username': '   '})
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
            username='',
        )

    def test_no_grants(self):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=[],
        )
        rv = self._make_request(
            data={'consumer': CONSUMER1},
            headers={'Ya-Consumer-Client-Ip': CONSUMER_IP1},
        )
        self._assert_error_response(rv, ['access.denied'])

    def test_statbox(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._fake_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(self.YANDEX_UID),
            ),
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(self.KINOPOISK_UID),
            ),
        ])

    def test_invalid_yandex_session_id(self):
        self._setup_environment(master_account=self._build_yandex_account(enabled=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_session.invalid'])
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

    def test_invalind_kinopoisk_session(self):
        self._setup_environment(slave_account=self._build_kinopoisk_account(enabled=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['provider_token.invalid'])
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

    def test_binding_already_exists(self):
        self._setup_environment(binding_exists=True)
        rv = self._make_request()
        self._assert_ok_response(rv)

    def test_master_account_is_kinopoisk(self):
        self._setup_environment(master_account=self._build_kinopoisk_account(uid=self.YANDEX_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_master_account_is_phonish(self):
        self._setup_environment(master_account=self._build_phonish_account(uid=self.YANDEX_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_slave_account_is_completed_kinopoisk(self):
        self._setup_environment(slave_account=self._build_kinopoisk_account(completed=True))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_requests_to_blackbox(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        requests = self._fake_blackbox.requests
        self.assertEqual(len(requests), 3)
        requests[0].assert_query_contains({
            'method': 'sessionid',
            'host': 'kinopoisk.ru',
            'sessionid': _YANDEX_SESSION_ID_1,
            'userip': USER_IP1,
        })
        requests[1].assert_query_contains({
            'method': 'sessionid',
            'host': 'kinopoisk.ru',
            'sessionid': _SESSION_ID_1,
            'userip': USER_IP1,
        })
        requests[2].assert_post_data_contains({
            'method': 'userinfo',
            'uid': ','.join(map(str, [self.YANDEX_UID, self.KINOPOISK_UID])),
        })

    def test_requests_to_billing(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 2)
        for i, uid in enumerate([self.YANDEX_UID, self.KINOPOISK_UID]):
            self._fake_billing_api.requests[i].assert_properties_equal(
                method='POST',
                url='http://balance-simple.yandex.net:8028/trust-payments/v2/passport/%s/invalidate' % uid,
                headers={'X-Service-Token': _SERVICE_TOKEN1},
            )

    def test_bind_kp_binding_already_exists(self):
        self._setup_environment()
        self._create_binding(self.YANDEX_UID, Kinopoisk, UID3)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            username=USERNAME1,
            provider=Kinopoisk,
            userid=UID3,
        )

        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=UID3,
        )

    def test_bind_yandex_binding_already_exists(self):
        self._setup_environment()
        self._create_binding(UID3, Kinopoisk, self.KINOPOISK_UID)
        self._assert_binding_exists(
            uid=UID3,
            username=USERNAME1,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )

        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
        self._assert_binding_not_exist(
            uid=UID3,
            provider=Kinopoisk,
            userid=self.KINOPOISK_UID,
        )
