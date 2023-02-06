# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_DISABLED_STATUS,
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_OAUTH_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import (
    profile_table,
    token_table,
)
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    NEOPHONISH_LOGIN1,
    PHONISH_LOGIN1,
    UID1,
    UID2,
    UID3,
    USER_IP1,
    USER_IP2,
    USERNAME1,
    YANDEX_APPLICATION_ID1,
    YANDEX_TOKEN2,
)
from passport.backend.social.common.test.fake_billing_api import (
    billing_api_fail_response,
    billing_api_invalidate_account_bindings_response,
    FakeBillingApi,
)
from passport.backend.social.common.test.types import DatetimeNow
from passport.backend.social.common.useragent import RequestError
from passport.backend.social.proxylib.test import yandex as yandex_test
from passport.backend.utils.common import deep_merge
from sqlalchemy import (
    and_ as sql_and,
    select as sql_select,
)


SERVICE_TOKEN1 = 'service_token1'
PHONE_ID1 = 1
PHONE_NUMBER1 = '+79259162525'


class BindYandexAccountByTokenTestCase(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_yandex_by_token'
    REQUEST_HEADERS = {
        'Ya-Consumer-Authorization': 'Bearer %s' % APPLICATION_TOKEN1,
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'token': YANDEX_TOKEN2,
        'client_id': EXTERNAL_APPLICATION_ID1,
    }

    PORTAL_UID = UID1
    PHONISH_UID = UID2
    NEOPHONISH_UID = UID3

    def setUp(self):
        super(BindYandexAccountByTokenTestCase, self).setUp()

        self._fake_billing_api = FakeBillingApi()
        self._fake_passport = FakePassport()
        self._fake_yandex_proxy = yandex_test.FakeProxy()

        self.__patches = [
            self._fake_billing_api,
            self._fake_passport,
            self._fake_yandex_proxy,
        ]
        for patch in self.__patches:
            patch.start()

        self._setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(BindYandexAccountByTokenTestCase, self).tearDown()

    def _setup_environment(self, master_account=Undefined, slave_account=Undefined,
                           binding_exists=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['bind-yandex-account-by-token'],
        )

        if master_account is Undefined:
            master_account = self._build_portal_account()

        if slave_account is Undefined:
            slave_account = self._build_phonish_account()

        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master_account['userinfo'], master_account['oauth'])),
                blackbox_oauth_response(**deep_merge(slave_account['userinfo'], slave_account['oauth'])),
            ],
        )

        slave_oauth_status = slave_account['oauth'].get('status')
        if slave_oauth_status is None or slave_oauth_status == BLACKBOX_OAUTH_VALID_STATUS:
            get_profile_response = yandex_test.YandexApi.get_profile(
                user=dict(
                    id=str(slave_account['userinfo']['uid']),
                    display_name=slave_account['userinfo'].get('display_name', {}).get('name'),
                ),
            )
        elif slave_oauth_status in {BLACKBOX_OAUTH_INVALID_STATUS, BLACKBOX_OAUTH_DISABLED_STATUS}:
            get_profile_response = yandex_test.YandexApi.build_error()

        self._fake_yandex_proxy.set_response_value('get_profile', get_profile_response)

        self._setup_blackbox_batch_response_about_master_and_slave(master_account, slave_account)

        if binding_exists:
            self._create_binding(master_account['userinfo']['uid'], Yandex, slave_account['userinfo']['uid'])

        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_invalidate_account_bindings_response(),
        )

        self._fake_passport.set_response_side_effect(
            'bind_phone_from_phonish_to_portal',
            [
                passport_ok_response(),
            ],
        )

        phone_bindings = [
            dict(
                type='current',
                number=PHONE_NUMBER1,
            ),
        ]
        self._fake_blackbox.set_response_side_effect(
            'phone_bindings',
            [
                blackbox_phone_bindings_response(phone_bindings),
            ],
        )

    def _setup_statbox_templates(self):
        self._fake_statbox.bind_entry(
            'update_account_bindings',
            action='update_account_yandex_bindings',
            consumer=CONSUMER1,
            ip=USER_IP1,
        )

    def _setup_blackbox_batch_response_about_master_and_slave(self, master_account, slave_account):
        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**slave_account['userinfo']),
                blackbox_userinfo_response_multiple([
                    master_account['userinfo'],
                    slave_account['userinfo'],
                ]),
            ]
        )

    def _build_portal_account(self, uid=PORTAL_UID, enabled=True, **kwargs):
        return dict(
            userinfo=dict(uid=uid),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
        )

    def _build_neophonish_account(self, uid=NEOPHONISH_UID, enabled=True, **kwargs):
        return dict(
            userinfo=deep_merge(
                dict(
                    uid=uid,
                    aliases=dict(neophonish=NEOPHONISH_LOGIN1),
                ),
                build_phone_bound(PHONE_ID1, PHONE_NUMBER1),
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
        )

    def _build_phonish_account(self, uid=PHONISH_UID, enabled=True, **kwargs):
        return dict(
            userinfo=deep_merge(
                dict(
                    uid=uid,
                    aliases=dict(phonish=PHONISH_LOGIN1),
                    display_name={'name': USERNAME1},
                ),
                build_phone_bound(PHONE_ID1, PHONE_NUMBER1),
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
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

    def _assert_binding_exists(self, uid, provider, userid):
        bindings = self._find_bindings(uid, provider, userid)
        self.assertEqual(len(bindings), 1)
        binding = bindings[0]

        self.assertEqual(binding.allow_auth, 0)
        self.assertEqual(binding.username, USERNAME1)
        self.assertEqual(binding.created, DatetimeNow())
        self.assertEqual(binding.yandexuid, '')

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

    def _assert_token_not_exist(self, value):
        tokens = self._find_tokens(value)
        self.assertEqual(len(tokens), 0)

    def _find_tokens(self, value):
        with self._fake_db.no_recording() as db:
            query = (
                sql_select([token_table])
                .where(token_table.c.value == value)
            )
            return db.execute(query).fetchall()

    def _assert_invalidate_account_bindings_in_billing_requested(self, uid):
        self.assertEqual(len(self._fake_billing_api.requests), 1)
        self._fake_billing_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://balance-simple.yandex.net:8028/trust-payments/v2/passport/%s/invalidate' % self.PORTAL_UID,
            headers={'X-Service-Token': SERVICE_TOKEN1},
        )

    def _assert_invalidate_account_bindings_in_billing_not_requested(self):
        self.assertEqual(len(self._fake_billing_api.requests), 0)

    def build_settings(self):
        settings = super(BindYandexAccountByTokenTestCase, self).build_settings()
        settings['social_config'].update({
            'billing_http_api_retries': 1,
            'billing_http_api_timeout': 1,
            'billing_http_api_url': 'http://balance-simple.yandex.net:8028/',
            'billing_http_api_service_token': SERVICE_TOKEN1,
            'invalidate_billing_binding_cache': True,
            'yandex_get_profile_url': 'https://login.yambex.ru/info',
            'yandex_avatar_url_template': 'https://avatars.mds.yambex.net/get-yapic/%s/',
            'passport_api_consumer': 'communizm',
            'passport_api_url': 'https://passport-infernal.google.com',
            'passport_api_timeout': 1,
            'passport_api_retries': 3,
        })
        settings['applications'] = [
            {
                'provider_id': Yandex.id,
                'application_id': YANDEX_APPLICATION_ID1,
                'application_name': 'yandex-account-manager',
                'provider_client_id': EXTERNAL_APPLICATION_ID1,
                'secret': APPLICATION_SECRET1,
                'request_from_intranet_allowed': '1',
            },
        ]
        return settings


class TestBindYandexAccountByToken(BindYandexAccountByTokenTestCase):
    def test_master_portal_and_slave_phonish(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )
        self._assert_binding_not_exist(
            uid=self.PHONISH_UID,
            provider=Yandex,
            userid=self.PORTAL_UID,
        )

    def test_master_phonish(self):
        self._setup_environment(
            master_account=self._build_phonish_account(uid=UID1),
            slave_account=self._build_phonish_account(uid=UID2),
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])
        self._assert_binding_not_exist(uid=UID1, provider=Yandex, userid=UID2)

    def test_master_neophonish(self):
        self._setup_environment(
            master_account=self._build_neophonish_account(uid=UID3),
            slave_account=self._build_phonish_account(uid=UID2),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.NEOPHONISH_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )
        self._assert_binding_not_exist(
            uid=self.PHONISH_UID,
            provider=Yandex,
            userid=self.NEOPHONISH_UID,
        )

    def test_slave_portal(self):
        self._setup_environment(
            master_account=self._build_portal_account(uid=UID1),
            slave_account=self._build_portal_account(uid=UID2),
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])
        self._assert_binding_not_exist(uid=UID1, provider=Yandex, userid=UID2)

    def test_single_account(self):
        portal = self._build_portal_account()
        self._setup_environment(master_account=portal, slave_account=portal)

        rv = self._make_request()

        self._assert_error_response(rv, ['profile.not_allowed'])
        self._assert_binding_not_exist(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PORTAL_UID,
        )

    def test_master_token_invalid(self):
        self._setup_environment(master_account=self._build_portal_account(token_valid=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_master_token_invalid_prefix(self):
        self._setup_environment()
        rv = self._make_request(headers={'Ya-Consumer-Authorization': 'Ololo'})
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_unknown_application_client_id(self):
        self._setup_environment()
        rv = self._make_request(data={'client_id': 'unknown'})
        self._assert_error_response(rv, ['application.unknown'])

    def test_unknown_application_token(self):
        phonish_account = self._build_phonish_account(token_client_id='unknown')
        self._setup_environment(slave_account=phonish_account)
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_token_not_exist(YANDEX_TOKEN2)

    def test_slave_token_invalid(self):
        self._setup_environment(slave_account=self._build_phonish_account(token_valid=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['provider_token.invalid'])

    def test_no_consumer(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['consumer'])
        self._assert_error_response(rv, ['consumer.empty'])

    def test_no_slave_token(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['token'])
        self._assert_error_response(rv, ['token.empty'])

    def test_no_master_token(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Authorization'])
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_no_user_ip(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])

    def test_no_consumer_ip(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['X-Real-Ip'])
        self._assert_error_response(rv, ['consumer_ip.empty'])

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

    def test_master_account_disabled(self):
        self._setup_environment(master_account=self._build_portal_account(enabled=False))
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_slave_account_disabled(self):
        self._setup_environment(slave_account=self._build_phonish_account(enabled=False))

        rv = self._make_request()

        self._assert_error_response(rv, ['provider_token.invalid'])

    def test_binding_exists(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(),
            binding_exists=True,
        )
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_master_token_scope_social_broker(self):
        self._setup_environment(
            master_account=self._build_portal_account(token_scope='social:broker'),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_master_token_scope_social_broker__unknown_token_client_id(self):
        self._setup_environment(
            master_account=self._build_portal_account(
                token_scope='social:broker',
                token_client_id='unknown',
            ),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_slave_token_scope_social_broker(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(token_scope='social:broker'),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_slave_token_scope_social_broker__unknown_token_client_id(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(
                token_scope='social:broker',
                token_client_id='unknown',
            ),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_master_token_scope_unsuitable(self):
        self._setup_environment(
            master_account=self._build_portal_account(
                token_scope='social:unsuitable',
                token_client_id='unknown',
            ),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['yandex_token.invalid'])
        self._assert_binding_not_exist(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_master_token_scope_unsuitable__known_token_client_id(self):
        self._setup_environment(
            master_account=self._build_portal_account(
                token_scope='social:unsuitable',
                token_client_id=EXTERNAL_APPLICATION_ID1,
            ),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_slave_token_scope_unsuitable(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(
                token_scope='social:unsuitable',
                token_client_id='unknown',
            ),
        )

        rv = self._make_request()

        self._assert_error_response(rv, ['provider_token.invalid'])
        self._assert_binding_not_exist(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_slave_token_scope_unsuitable__known_token_client_id(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(
                token_scope='social:unsuitable',
                token_client_id=EXTERNAL_APPLICATION_ID1,
            ),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_invalidate_account_bindings_in_billing(self):
        self._setup_environment(master_account=self._build_portal_account())

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_invalidate_account_bindings_in_billing_requested(uid=self.PORTAL_UID)

    def test_invalidate_account_bindings_in_billing_failed(self):
        self._setup_environment()
        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_fail_response(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_invalidate_account_bindings_in_billing_network_failed(self):
        self._setup_environment()
        self._fake_billing_api.set_response_side_effect('invalidate_account_bindings', RequestError())

        rv = self._make_request()

        self._assert_ok_response(rv)

    def test_statbox(self):
        self._setup_environment(master_account=self._build_portal_account())

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._fake_long_statbox.assert_contains([
            self._fake_statbox.entry(
                'update_account_bindings',
                uid=str(self.PORTAL_UID),
            ),
        ])

    def test_bind_phone_from_phonish_to_portal_in_passport_ok(self):
        portal_account = self._build_portal_account(uid=UID1)
        phonish_account = self._build_phonish_account(uid=UID2)
        self._setup_environment(
            master_account=portal_account,
            slave_account=phonish_account,
        )

        rv = self._make_request(headers={'Ya-Consumer-Client-Ip': USER_IP2})

        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_passport.requests), 1)
        self._fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='https://passport-infernal.google.com/2/bundle/phone/bind_phone_from_phonish_to_portal/?consumer=communizm',
            post_args={
                'portal_uid': str(UID1),
                'phonish_uid': str(UID2),
            },
            headers={
                'X-Ya-Service-Ticket': self.get_ticket_from_tvm_alias('passport'),
                'Ya-Consumer-Client-Ip': USER_IP2,
            },
        )

    def test_bind_phone_from_phonish_to_portal_in_passport_network_failed(self):
        self._setup_environment()
        self._fake_passport.set_response_side_effect(
            'bind_phone_from_phonish_to_portal',
            RequestError(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv, response={'failed_to_bind_phone': True})

    def test_bind_phone_from_phonish_to_portal_in_passport_unknown_fail(self):
        self._setup_environment()
        self._fake_passport.set_response_side_effect(
            'bind_phone_from_phonish_to_portal',
            [passport_bundle_api_error_response('unknown.error')],
        )

        rv = self._make_request()

        self._assert_ok_response(rv, response={'failed_to_bind_phone': True})


class TestBindYandexAccountByTokenBlackboxSwappedMasterAndSlave(BindYandexAccountByTokenTestCase):
    def _setup_blackbox_batch_response_about_master_and_slave(self, master_account, slave_account):
        (
            super(TestBindYandexAccountByTokenBlackboxSwappedMasterAndSlave, self)
            ._setup_blackbox_batch_response_about_master_and_slave(slave_account, master_account)
        )

    def test(self):
        self._setup_environment(
            master_account=self._build_portal_account(),
            slave_account=self._build_phonish_account(),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.PORTAL_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )


class TestBindYandexAccountByTokenInvalidateBillingBindingCacheDisabled(BindYandexAccountByTokenTestCase):
    def build_settings(self):
        settings = super(TestBindYandexAccountByTokenInvalidateBillingBindingCacheDisabled, self).build_settings()
        settings['social_config'].pop('billing_http_api_url', None)
        settings['social_config'].update({'invalidate_billing_binding_cache': False})
        return settings

    def test(self):
        self._setup_environment()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_invalidate_account_bindings_in_billing_not_requested()


class TestBindYandexAccountByTokenDoRetriesToBillingOnUnknownError(BindYandexAccountByTokenTestCase):
    def build_settings(self):
        settings = super(TestBindYandexAccountByTokenDoRetriesToBillingOnUnknownError, self).build_settings()
        settings['social_config'].update(
            dict(
                billing_http_api_retries=2,
            ),
        )
        return settings

    def test_unknown_error(self):
        self._setup_environment()
        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_fail_response(status_code='unknown_error'),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 2)

    def test_no_error(self):
        self._setup_environment()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 1)

    def test_not_unknown_error(self):
        self._setup_environment()
        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_fail_response(status_code='permanent_error'),
        )

        rv = self._make_request()

        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 1)
