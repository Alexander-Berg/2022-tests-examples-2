# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_DISABLED_STATUS,
    BLACKBOX_OAUTH_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_unbound,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    PHONISH_LOGIN1,
    UID1,
    UID2,
    USER_IP1,
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

_PHONE_NUMBER1 = u'+79019988777'
_PHONE_ID = 44


class BindPhonishAccountByUidTestCase(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_phonish_account_by_uid'
    REQUEST_HEADERS = {
        'Ya-Consumer-Authorization': 'Bearer %s' % APPLICATION_TOKEN1,
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }

    YANDEX_UID = UID1
    PHONISH_UID = UID2

    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'uid': PHONISH_UID,
    }

    TIME_DEFAULT_PORTAL_BOUND = datetime(2014, 2, 26, 0, 1, 10)
    TIME_DEFAULT_PORTAL_CONFIRMED = datetime(2014, 2, 26, 0, 1, 30)
    TIME_DEFAULT_PHONISH_BOUND = datetime(2014, 2, 26, 0, 1, 1)
    TIME_DEFAULT_PHONISH_CONFIRMED = datetime(2014, 2, 26, 0, 1, 20)

    PORTAL_PHONE_DATA = dict(
        phone_id=_PHONE_ID,
        phone_number=_PHONE_NUMBER1,
        phone_bound=TIME_DEFAULT_PORTAL_BOUND,
        phone_confirmed=TIME_DEFAULT_PORTAL_CONFIRMED,
    )
    PHONISH_PHONE_DATA = dict(
        phone_id=_PHONE_ID,
        phone_number=_PHONE_NUMBER1,
        phone_bound=TIME_DEFAULT_PHONISH_BOUND,
        phone_confirmed=TIME_DEFAULT_PHONISH_CONFIRMED,
    )

    def setUp(self):
        super(BindPhonishAccountByUidTestCase, self).setUp()

        self._fake_billing_api = FakeBillingApi()
        self._fake_billing_api.start()

        self._setup_statbox_templates()

    def tearDown(self):
        self._fake_billing_api.stop()
        super(BindPhonishAccountByUidTestCase, self).tearDown()

    def _setup_environment(self, master_account=Undefined, slave_account=Undefined,
                           binding_exists=False):
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['bind-phonish-account-by-uid'],
        )

        if master_account is Undefined:
            master_account = self._build_yandex_account()

        if slave_account is Undefined:
            slave_account = self._build_phonish_account()

        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master_account['userinfo'], master_account['oauth'], master_account['phones'])),
            ],
        )

        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**deep_merge(slave_account['userinfo'], slave_account['phones'])),
                blackbox_userinfo_response_multiple([
                    master_account['userinfo'],
                    slave_account['userinfo'],
                ]),
            ]
        )

        if binding_exists:
            self._create_binding(master_account['userinfo']['uid'], Yandex, slave_account['userinfo']['uid'])

        self._fake_billing_api.set_response_value(
            'invalidate_account_bindings',
            billing_api_invalidate_account_bindings_response(),
        )

    def _build_yandex_account(self, uid=YANDEX_UID, enabled=True, phones=None, **kwargs):
        if phones is None:
            phones = build_phone_bound(**self.PORTAL_PHONE_DATA)
        return dict(
            userinfo=dict(
                uid=uid,
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
            phones=phones,
        )

    def _build_phonish_account(self, uid=PHONISH_UID, enabled=True, phones=None, **kwargs):
        if phones is None:
            phones = build_phone_bound(**self.PHONISH_PHONE_DATA)
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
            ),
            oauth=self._build_oauth_token(account_enabled=enabled, **kwargs),
            phones=phones,
        )

    def _setup_statbox_templates(self):
        self._fake_statbox.bind_entry(
            'update_account_bindings',
            action='update_account_yandex_bindings',
            consumer=CONSUMER1,
            ip=USER_IP1,
        )

    def _build_oauth_token(self, token_valid=True, account_enabled=True, token_scope=Undefined, **kwargs):
        if token_scope is Undefined:
            token_scope = X_TOKEN_SCOPE

        oauth = dict(
            scope=token_scope,
            oauth_token_info={'client_id': EXTERNAL_APPLICATION_ID1},
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
        self.assertEqual(binding.username, '')
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
                username='',
                created=now(),
            )
            db.execute(query)

    def build_settings(self):
        settings = super(BindPhonishAccountByUidTestCase, self).build_settings()
        settings['social_config'].update({
            'invalidate_billing_binding_cache': True,
            'billing_http_api_retries': 1,
            'billing_http_api_timeout': 1,
            'billing_http_api_url': 'http://balance-simple.yandex.net:8028/',
            'billing_http_api_service_token': _SERVICE_TOKEN1,
        })
        return settings


class TestBindPhonishAccountByUid(BindPhonishAccountByUidTestCase):
    def test_bind(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self._assert_binding_exists(
            uid=self.YANDEX_UID,
            provider=Yandex,
            userid=self.PHONISH_UID,
        )
        self._assert_binding_not_exist(
            uid=self.PHONISH_UID,
            provider=Yandex,
            userid=self.YANDEX_UID,
        )

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
            'getphones': 'all',
        })
        requests[1].assert_post_data_contains({
            'method': 'userinfo',
            'uid': str(self.PHONISH_UID),
            'aliases': 'all',
            'getphones': 'all',
        })
        requests[2].assert_post_data_contains({
            'method': 'userinfo',
            'uid': ','.join(map(str, [self.YANDEX_UID, self.PHONISH_UID])),
        })

    def test_yataxi_pay_scope(self):
        self._setup_environment(master_account=self._build_yandex_account(token_scope='yataxi:pay'))
        rv = self._make_request()
        self._assert_ok_response(rv)

    def test_no_yandex_token(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Authorization'])
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_no_user_ip(self):
        self._setup_environment()
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])

    def test_no_uid(self):
        self._setup_environment()
        rv = self._make_request(exclude_data=['uid'])
        self._assert_error_response(rv, ['uid.empty'])

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
            provider=Yandex,
            userid=self.PHONISH_UID,
        )

    def test_binding_already_exists(self):
        self._setup_environment(binding_exists=True)
        rv = self._make_request()
        self._assert_ok_response(rv)

    def test_master_account_is_phonish(self):
        self._setup_environment(master_account=self._build_phonish_account(uid=self.YANDEX_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_slave_account_is_not_phonish(self):
        self._setup_environment(slave_account=self._build_yandex_account(uid=self.PHONISH_UID))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_non_existent_account(self):
        self._setup_environment(slave_account=self._build_phonish_account(uid=None))
        rv = self._make_request()
        self._assert_error_response(rv, ['account.not_found'])

    def test_requests_to_billing(self):
        self._setup_environment()
        rv = self._make_request()
        self._assert_ok_response(rv)
        self.assertEqual(len(self._fake_billing_api.requests), 1)
        self._fake_billing_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://balance-simple.yandex.net:8028/trust-payments/v2/passport/%s/invalidate' % self.YANDEX_UID,
            headers={'X-Service-Token': _SERVICE_TOKEN1},
        )

    def test_no_portal_phones(self):
        self._setup_environment(master_account=self._build_yandex_account(phones={}))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_portal_phone_unbound(self):
        self._setup_environment(master_account=self._build_yandex_account(phones=build_phone_unbound(_PHONE_ID, _PHONE_NUMBER1)))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_portal_bound_after_phonish_confirmed(self):
        self._setup_environment(master_account=self._build_yandex_account(phones=build_phone_bound(**dict(self.PORTAL_PHONE_DATA, phone_bound=self.TIME_DEFAULT_PORTAL_CONFIRMED))))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])

    def test_portal_confirmed_before_phonish_confirmed(self):
        self._setup_environment(master_account=self._build_yandex_account(phones=build_phone_bound(**dict(self.PORTAL_PHONE_DATA, phone_confirmed=self.TIME_DEFAULT_PORTAL_BOUND))))
        rv = self._make_request()
        self._assert_error_response(rv, ['profile.not_allowed'])
