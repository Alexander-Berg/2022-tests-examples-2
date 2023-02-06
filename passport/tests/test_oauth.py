# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.oauth import (
    OAuth,
    OAuthDeviceCodeNotAccepted,
    OAuthDeviceCodeNotFound,
    OAuthPermanentError,
    OAuthTemporaryError,
)
from passport.backend.core.builders.oauth.faker import (
    check_device_code_response,
    FakeOAuth,
    issue_device_code_response,
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.core.useragent.sync import RequestError


TEST_UID = 1
TEST_USER_IP = '1.2.3.4'
TEST_CLIENT_ID = 'test_client_id'
TEST_CLIENT_HOST = 'yandex.ru'
TEST_CLIENT_SECRET = 'test_client_secret'
TEST_CA_CERT = '/etc/ssl/certs/some-ca-certificates.crt'

TEST_TVM_TICKET = '3:test:test'


@with_settings(
    OAUTH_URL='http://localhost/',
    OAUTH_CONSUMER='passport',
    SSL_CA_CERT=TEST_CA_CERT,
)
class TestOAuth(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'oauth',
                        'ticket': TEST_TVM_TICKET,
                    },
                },
            )
        )
        self.fake_tvm_credentials_manager.start()

        self.fake_oauth = FakeOAuth()
        self.fake_oauth.start()

        self.oauth = OAuth()

    def tearDown(self):
        self.fake_oauth.stop()
        del self.fake_oauth
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def oauth_retries(self, exc, retries_count=None):
        token_by_uid_call = (
            self.oauth.token_by_uid,
            [
                'client_id',
                'client_secret',
                'uid',
                'user_ip',
            ],
        )
        token_by_sessionid_call = (
            self.oauth.token_by_sessionid,
            [
                'client_id',
                'client_secret',
                'session_id',
                'host',
                'user_ip',
            ],
        )

        for i, (method, args) in enumerate(
            [
                token_by_uid_call,
                token_by_sessionid_call,
            ]
        ):
            with assert_raises(exc):
                method(*args)
        eq_(len(self.fake_oauth.requests), (retries_count or 10) * (i + 1))

    def test_oauth_retries_response_503(self):
        self.oauth.retries = 10
        self.fake_oauth.set_response_value(
            '_token',
            b'Service temporarily unavailable',
            503,
        )
        self.oauth_retries(OAuthTemporaryError)

    def test_oauth_retries_response_500(self):
        self.oauth.retries = 10
        self.fake_oauth.set_response_value(
            '_token',
            b'Server error',
            500,
        )
        self.oauth_retries(OAuthPermanentError, retries_count=1)

    def test_oauth_retries_request_error(self):
        self.oauth.retries = 10
        self.fake_oauth.set_response_side_effect('_token', RequestError)
        self.oauth_retries(OAuthTemporaryError)

    def test_token_by_sessionid(self):
        self.fake_oauth.set_response_value('_token', b'{}', 200)

        self.oauth.token_by_sessionid(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            'test_sessionid',
            'yandex.com',
            TEST_USER_IP,
            device_id='foo',
        )

        eq_(len(self.fake_oauth.requests), 1)
        req = self.fake_oauth.requests[0]
        req.assert_url_starts_with('http://localhost/token?')
        req.assert_properties_equal(
            method='POST',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'grant_type': 'sessionid',
                'sessionid': 'test_sessionid',
                'host': 'yandex.com',
            },
        )
        req.assert_query_equals(
            {
                'user_ip': TEST_USER_IP,
                'device_id': 'foo',
            }
        )

    def test_token_by_sessionid_invalid_json(self):
        self.oauth.retries = 10
        self.fake_oauth.set_response_value(
            '_token',
            u'плохой json'.encode('utf-8'),
            200,
        )

        with assert_raises(OAuthPermanentError):
            self.oauth.token_by_sessionid(
                TEST_CLIENT_ID,
                TEST_CLIENT_SECRET,
                'test_sessionid',
                'yandex.com',
                TEST_USER_IP,
            )
        eq_(len(self.fake_oauth.requests), 1)

    def test_token_by_x_token(self):
        self.fake_oauth.set_response_value('_token', b'{}', 200)

        self.oauth.token_by_x_token(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            'test_xtoken',
            TEST_USER_IP,
            device_id='foo',
        )

        eq_(len(self.fake_oauth.requests), 1)
        req = self.fake_oauth.requests[0]
        req.assert_url_starts_with('http://localhost/token?')
        req.assert_properties_equal(
            method='POST',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'grant_type': 'x-token',
                'access_token': 'test_xtoken',
            },
        )
        req.assert_query_equals(
            {
                'user_ip': TEST_USER_IP,
                'device_id': 'foo',
            }
        )

    def test_oauth_not_available(self):
        self.oauth.retries = 10
        self.fake_oauth.set_response_value(
            '_token',
            u'Сервер недоступен'.encode('utf-8'),
            503,
        )

        with assert_raises(OAuthTemporaryError):
            self.oauth.token_by_sessionid(
                TEST_CLIENT_ID,
                TEST_CLIENT_SECRET,
                'test_sessionid',
                'yandex.com',
                TEST_USER_IP,
            )
        eq_(len(self.fake_oauth.requests), 10)

    def test_token_by_uid(self):
        self.fake_oauth.set_response_value('_token', b'{}', 200)

        self.oauth.token_by_uid(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            '123456789',
            TEST_USER_IP,
            device_id='foo',
            password_passed=True,
        )

        eq_(len(self.fake_oauth.requests), 1)
        req = self.fake_oauth.requests[0]
        req.assert_url_starts_with('http://localhost/token?')
        req.assert_properties_equal(
            method='POST',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'grant_type': 'passport_assertion',
                'assertion': '123456789',
                'password_passed': True,
            },
        )
        req.assert_query_equals(
            {
                'user_ip': TEST_USER_IP,
                'device_id': 'foo',
            }
        )

    def test_issue_authorization_code(self):
        self.fake_oauth.set_response_value('issue_authorization_code', b'{}', 200)

        self.oauth.issue_authorization_code(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            {
                'Cookie': 'foo=bar',
                'Host': 'google.com',
                'Ya-Consumer-Real-Ip': TEST_USER_IP,
            },
            ttl=59,
            uid=1,
        )

        eq_(len(self.fake_oauth.requests), 1)
        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/1/authorization_code/issue',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'ttl': 59,
                'uid': '1',
                'consumer': 'passport',
            },
            headers={
                'Host': 'localhost',
                'Cookie': 'foo=bar',
                'Ya-Consumer-Real-Ip': TEST_USER_IP,
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
        )

    def test_issue_authorization_code_skip_tvm_ticket(self):
        self.fake_oauth.set_response_value('issue_authorization_code', b'{}', 200)

        self.oauth.issue_authorization_code(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            {
                'Cookie': 'foo=bar',
                'Host': 'google.com',
                'Ya-Consumer-Real-Ip': TEST_USER_IP,
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
            ttl=59,
            uid=1,
        )

        eq_(len(self.fake_oauth.requests), 1)
        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/1/authorization_code/issue',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'ttl': 59,
                'uid': '1',
                'consumer': 'passport',
            },
            headers={
                'Host': 'localhost',
                'Cookie': 'foo=bar',
                'Ya-Consumer-Real-Ip': TEST_USER_IP,
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
        )

    def test_issue_authorization_code_without_consumer_real_ip_header(self):
        self.fake_oauth.set_response_value('issue_authorization_code', b'{}', 200)

        self.oauth.issue_authorization_code(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            {
                'Cookie': 'foo=bar',
                'Host': 'google.com',
            },
            ttl=59,
            uid=1,
        )

        eq_(len(self.fake_oauth.requests), 1)
        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/1/authorization_code/issue',
            post_args={
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'ttl': 59,
                'uid': '1',
                'consumer': 'passport',
            },
            headers={
                'Host': 'localhost',
                'Cookie': 'foo=bar',
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
        )

    def test_device_status(self):
        self.fake_oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='device-id', device_name='model-name'),
        )

        rv = self.oauth.device_status(
            uid=1,
            deviceid='device-id',
            model='model-name',
        )
        eq_(
            rv,
            {
                'status': 'ok',
                'has_auth_on_device': True,
                'device_id': 'device-id',
                'device_name': 'model-name',
            },
        )

        eq_(len(self.fake_oauth.requests), 1)
        self.fake_oauth.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/1/device/status?uid=1&deviceid=device-id&model=model-name&consumer=passport',
        )

    def test_oauth_default_initialization(self):
        """
        Проверим, что оаус по дефолту инициализируется useragent-ом
        и урлом из настроек
        """
        oauth = OAuth()
        ok_(oauth.useragent is not None)
        eq_(oauth.url, 'http://localhost/')
        eq_(oauth.ca_cert, TEST_CA_CERT)

    def test_revoke_device(self):
        self.fake_oauth.set_response_value(
            'revoke_device',
            oauth_bundle_successful_response(),
        )

        rv = self.oauth.revoke_device(
            uid=1,
            device_id='device-id',
        )

        eq_(rv, {'status': 'ok'})

        eq_(len(self.fake_oauth.requests), 1)
        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/api/1/device/revoke',
            post_args={
                'consumer': 'passport',
                'device_id': 'device-id',
                'uid': '1',
            },
        )

    def test_issue_device_code(self):
        self.fake_oauth.set_response_value(
            'issue_device_code',
            issue_device_code_response(),
        )

        rv = self.oauth.issue_device_code(
            client_id=TEST_CLIENT_ID,
            code_strength='medium_with_crc',
            client_bound=True,
            device_id='device-id',
            device_name='device-name',
        )
        eq_(
            rv,
            {
                'device_code': 'device-code',
                'user_code': 'user-code',
                'verification_url': 'ver-url',
                'expires_in': 30,
            },
        )
        eq_(len(self.fake_oauth.requests), 1)
        expected_url = ''.join(
            [
                'http://localhost/api/1/device_code/issue',
                '?code_strength=medium_with_crc',
                '&client_bound=True',
                '&device_name=device-name',
                '&client_id={}'.format(TEST_CLIENT_ID),
                '&consumer=passport',
                '&device_id=device-id',
            ]
        )

        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url=expected_url,
        )

    def test_check_device_code_ok(self):
        self.fake_oauth.set_response_value(
            'check_device_code',
            check_device_code_response(),
        )
        rv = self.oauth.check_device_code('device-code')
        eq_(
            rv,
            {
                'uid': 1,
                'scopes': ['scope-1', 'scope-2'],
            },
        )
        eq_(len(self.fake_oauth.requests), 1)
        expected_url = ''.join(
            [
                'http://localhost/api/1/device_code/check',
                '?consumer=passport',
                '&device_code=device-code',
            ]
        )

        self.fake_oauth.requests[0].assert_properties_equal(
            method='GET',
            url=expected_url,
        )

    def test_check_device_code_not_found(self):
        self.fake_oauth.set_response_value(
            'check_device_code',
            oauth_bundle_error_response('code.not_found'),
        )
        with assert_raises(OAuthDeviceCodeNotFound):
            self.oauth.check_device_code('device-code')

    def test_check_device_code_not_accepted(self):
        self.fake_oauth.set_response_value(
            'check_device_code',
            oauth_bundle_error_response('code.not_accepted'),
        )
        with assert_raises(OAuthDeviceCodeNotAccepted):
            self.oauth.check_device_code('device-code')

    @parameterized.expand(
        [
            (TEST_UID,),
            (None,),
        ]
    )
    def test_device_authorize_submit(self, uid):
        self.fake_oauth.set_response_value(
            'device_authorize_submit',
            oauth_bundle_successful_response(),
        )
        self.oauth.device_authorize_submit(
            language='ru',
            code='123',
            client_id=TEST_CLIENT_ID,
            client_host=TEST_CLIENT_HOST,
            uid=uid,
            cookie='cookie',
            authorization='authorization',
            # опциональные для АМ
            device_id='device-id',
        )

        eq_(len(self.fake_oauth.requests), 1)

        expected_url = ''.join(
            [
                'http://localhost/iface_api/1/device/authorize/submit',
                '?consumer=passport',
                '&language=ru',
                '&client_id={}'.format(TEST_CLIENT_ID),
                '&device_id=device-id',
            ]
        )
        if uid is not None:
            expected_url += '&uid={}'.format(TEST_UID)

        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url=expected_url,
            headers={
                'Ya-Client-Cookie': 'cookie',
                'Ya-Client-Host': TEST_CLIENT_HOST,
                'Ya-Consumer-Authorization': 'authorization',
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
            post_args={
                'code': '123',
            },
        )

    @parameterized.expand(
        [
            (TEST_UID,),
            (None,),
        ]
    )
    def test_device_authorize_commit(self, uid):
        self.fake_oauth.set_response_value(
            'device_authorize_commit',
            oauth_bundle_successful_response(),
        )
        self.oauth.device_authorize_commit(
            language='ru',
            code='123',
            client_id=TEST_CLIENT_ID,
            client_host=TEST_CLIENT_HOST,
            uid=uid,
            cookie='cookie',
            authorization='authorization',
            # опциональные для АМ
            device_id='device-id',
        )

        eq_(len(self.fake_oauth.requests), 1)

        expected_url = ''.join(
            [
                'http://localhost/iface_api/1/device/authorize/commit',
                '?consumer=passport',
                '&language=ru',
                '&client_id={}'.format(TEST_CLIENT_ID),
                '&device_id=device-id',
            ]
        )
        if uid is not None:
            expected_url += '&uid={}'.format(TEST_UID)

        self.fake_oauth.requests[0].assert_properties_equal(
            method='POST',
            url=expected_url,
            headers={
                'Ya-Client-Cookie': 'cookie',
                'Ya-Client-Host': TEST_CLIENT_HOST,
                'Ya-Consumer-Authorization': 'authorization',
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
            },
            post_args={
                'code': '123',
            },
        )
