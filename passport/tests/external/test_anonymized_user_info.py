# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
import jwt
import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.psuid import parse_psuid
from passport.backend.oauth.core.test.base_test_data import (
    TEST_CIPHER_KEYS,
    TEST_FAKE_UUID,
    TEST_HOST,
)
from passport.backend.oauth.core.test.framework import BundleApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq


TEST_UID = 42
TEST_REDIRECT_URI = 'yandexta://ozon.ru'
TEST_JWT_TTL = 86400
TEST_EXPECTED_PSUID = '1.AAAAAQ.IOOV1ZVR5LaiSeMuES6_qQ.sRHhx_2Ug4C6BA97LgsbYA'


@override_settings(
    PSUID_DEFAULT_VERSION=1,
    PSUID_ENCRYPTION_KEYS=TEST_CIPHER_KEYS,
    PSUID_SIGNATURE_KEYS=TEST_CIPHER_KEYS,
    PSUID_JWT_TTL=TEST_JWT_TTL,
)
class TestAnonymizedUserInfo(BundleApiTestCase):
    default_url = reverse_lazy('api_anonymized_user_info')
    http_method = 'GET'

    def setUp(self):
        super(TestAnonymizedUserInfo, self).setUp()
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID, scope='test:xtoken'),
        )
        self.uuid_patch = mock.patch('uuid.uuid1', mock.Mock(return_value=TEST_FAKE_UUID))
        self.uuid_patch.start()

        self.patch_ydb()
        self.setup_ydb_response()

        with UPDATE(self.test_client) as client:
            client.display_id = 'a' * 32
            client._redirect_uris = [TEST_REDIRECT_URI]

    def tearDown(self):
        self.uuid_patch.stop()
        super(TestAnonymizedUserInfo, self).tearDown()

    def default_params(self):
        return {
            'consumer': 'dev',
            'client_id': self.test_client.display_id,
            'redirect_uri': TEST_REDIRECT_URI,
        }

    def default_headers(self):
        return dict(
            super(TestAnonymizedUserInfo, self).default_headers(),
            HTTP_AUTHORIZATION='OAuth token',
        )

    def setup_ydb_response(self, allow_psuid=True):
        rows = []
        if allow_psuid:
            rows.append({
                'host': 'test-host',
                'partner_id': 'test-partner-id',
                'allow_psuid': True,
            })
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet(rows)],
        )

    def test_ok(self):
        rv = self.make_request()
        eq_(
            set(rv.keys()),
            {'status', 'jwt', 'expires_in'},
        )
        eq_(rv['status'], 'ok')
        iter_eq(
            jwt.decode(rv['jwt'], self.test_client.secret, algorithms='HS256'),
            {
                'iat': TimeNow(),
                'jti': TEST_FAKE_UUID,
                'exp': TimeNow(offset=TEST_JWT_TTL),
                'iss': TEST_HOST,
                'psuid': TEST_EXPECTED_PSUID,
            },
        )
        eq_(rv['expires_in'], TEST_JWT_TTL)

        uid, seed, client = parse_psuid(TEST_EXPECTED_PSUID)
        eq_(uid, TEST_UID)
        eq_(seed, 0)
        eq_(client.display_id, self.test_client.display_id)

    def test_client_not_found_error(self):
        rv = self.make_request(client_id='b' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_redirect_uri_not_turboapp_error(self):
        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['https://yandex.ru']

        rv = self.make_request(redirect_uri='https://yandex.ru')
        self.assert_status_error(rv, ['redirect_uri.not_matched'])

    def test_redirect_uri_not_matched_error(self):
        rv = self.make_request(redirect_uri='yandexta://yandex.ru')
        self.assert_status_error(rv, ['redirect_uri.not_matched'])

    def test_psuid_not_allowed_by_ydb_error(self):
        self.setup_ydb_response(allow_psuid=False)
        rv = self.make_request()
        self.assert_status_error(rv, ['redirect_uri.not_matched'])

    def test_ydb_temporary_error(self):
        self.fake_ydb.set_execute_side_effect(YdbTemporaryError)
        rv = self.make_request()
        self.assert_status_error(rv, ['redirect_uri.not_matched'])

    def test_token_not_passed_error(self):
        rv = self.make_request(headers={'HTTP_AUTHORIZATION': 'foo'})
        self.assert_status_error(rv, ['authorization.invalid'])

    def token_invalid_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['authorization.invalid'])
