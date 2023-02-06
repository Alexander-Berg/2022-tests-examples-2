# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_UID1,
    TEST_USER_IP1,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidResponseError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_device_signature_response,
    blackbox_get_device_public_key_response,
)
from passport.backend.core.builders.drive_api.faker import (
    drive_api_find_drive_session_id_access_denied_response,
    drive_api_find_drive_session_id_found_response,
    drive_api_find_drive_session_id_not_found_response,
    FakeDriveApi,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.crypto.signing import SigningRegistry
from passport.backend.core.device_public_key import insert_device_public_key
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.device_public_key import DevicePublicKey
from passport.backend.core.models.drive import DriveSession
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.useragent.sync import RequestError
from passport.backend.core.ydb.faker.ydb_keyvalue import FakeYdbKeyValue
from passport.backend.core.ydb.processors.drive import (
    find_drive_session,
    save_drive_session,
)
import passport.backend.core.ydb_client as ydb


AUTHORIZATION_CODE1 = 'code1'
DRIVE_DEVICE_ID1 = '1' * 32
DRIVE_DEVICE_ID2 = '2' * 32
DRIVE_SANDBOX_DEVICE_ID1 = '3' * 32
DRIVE_SANDBOX_DEVICE_ID2 = '4' * 32
DRIVE_SESSION_ID1 = 'drive_session_id1'
DRIVE_SESSION_ID2 = 'drive_session_id2'
NONCE1 = 'nonce1'
OAUTH_CLIENT_ID1 = 'client_id1'
OAUTH_CLIENT_SECRET1 = 'client_secret1'
OAUTH_CLIENT_ID_XTOKEN = 'client_id_xtoken'
OAUTH_CLIENT_SECRET_XTOKEN = 'client_secret_xtoken'
OWNER1 = 'device_owner1'
OWNER2 = 'device_owner2'
PUBLIC_KEY1 = 'key1'
SIGNATURE1 = 'signature1'


class BaseTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/auth/forward_drive/issue_authorization_code/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    http_query_args = {
        'drive_device_id': DRIVE_DEVICE_ID1,
        'sandbox_device_id': DRIVE_SANDBOX_DEVICE_ID1,
        'nonce': NONCE1,
        'signature': SIGNATURE1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.fake_ydb_key_value = FakeYdbKeyValue()
        self.fake_drive_api = FakeDriveApi()

        self.__patches = [
            self.env,
            self.fake_ydb_key_value,
            self.fake_drive_api,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.env
        super(BaseTestCase, self).tearDown()

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forward_drive': ['issue_authorization_code'],
                    },
                ),
                'drive_device': dict(
                    networks=[TEST_USER_IP1],
                    grants={
                        'auth_forward_drive': ['public_access'],
                    },
                ),
            },
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='forward_auth_to_drive_device',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
        )
        self.env.statbox.bind_entry(
            'revoke_drive_device',
            action='revoke_drive_device',
            uid=str(TEST_UID1),
            device_id=DRIVE_SANDBOX_DEVICE_ID1,
        )
        self.env.statbox.bind_entry(
            'issue_authorization_code',
            action='issue_authorization_code',
            drive_device_id=DRIVE_DEVICE_ID1,
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'check_nonce',
            action='check_nonce',
            status='ok',
        )

    def setup_blackbox(
        self,
        check_device_signature_response=None,
        device_public_key=None,
    ):
        if check_device_signature_response is None:
            check_device_signature_response = blackbox_check_device_signature_response()
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                check_device_signature_response,
            ],
        )

        if device_public_key:
            response = blackbox_get_device_public_key_response(
                value=device_public_key.public_key,
                version=device_public_key.version,
                owner_id=device_public_key.owner_id,
            )
            self.save_device_public_key(device_public_key)
        else:
            response = blackbox_get_device_public_key_response(status=BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS.PUBLIC_KEY_NOT_FOUND)

        self.env.blackbox.set_response_side_effect('get_device_public_key', [response])

    def setup_oauth(self):
        self.env.oauth.set_response_side_effect(
            'issue_authorization_code',
            [
                oauth_bundle_successful_response(code=AUTHORIZATION_CODE1),
            ],
        )

    def setup_drive_api(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID1),
            ],
        )

    def setup_ydb(self, **kwargs):
        save_drive_session(self.build_drive_session(**kwargs))

    def build_drive_session(
        self,
        drive_device_id=DRIVE_DEVICE_ID1,
        sandbox_device_id=DRIVE_SANDBOX_DEVICE_ID1,
        drive_session_id=DRIVE_SESSION_ID1,
        uid=TEST_UID1,
    ):
        return DriveSession(
            drive_device_id=drive_device_id,
            sandbox_device_id=sandbox_device_id,
            drive_session_id=drive_session_id,
            uid=uid,
        )

    def assert_issue_authorization_code_ok_response(self, rv):
        self.assert_ok_response(
            rv,
            authorization_code=AUTHORIZATION_CODE1,
        )

    def assert_authorization_code_requested(self, request,
                                            client_id=OAUTH_CLIENT_ID_XTOKEN, client_secret=OAUTH_CLIENT_SECRET_XTOKEN):
        request.assert_url_starts_with('https://oauth/api/1/authorization_code/issue?')
        request.assert_properties_equal(
            method='POST',
            post_args={
                'by_uid': '1',
                'client_id': client_id,
                'client_secret': client_secret,
                'code_strength': 'long',
                'consumer': 'oauth_consumer',
                'uid': str(TEST_UID1),
                'require_activation': '0',
            },
        )
        request.assert_query_equals(
            {
                'user_ip': TEST_USER_IP1,
            },
        )

    def assert_check_device_signature_requested(self, request):
        request.assert_properties_equal(
            method='POST',
            url='https://blackbox/blackbox/',
            post_args={
                'method': 'check_device_signature',
                'format': 'json',
                'nonce': NONCE1,
                'nonce_sign_space': 'auto_head_unit',
                'device_id': DRIVE_DEVICE_ID1,
                'signature': SIGNATURE1,
            },
        )

    def assert_get_device_public_key_requested(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'get_device_public_key',
                'device_id': DRIVE_DEVICE_ID1,
            },
        )

    def assert_drive_session_saved(self, expected_drive_session=None):
        if expected_drive_session is None:
            expected_drive_session = self.build_drive_session()
        drive_session = find_drive_session(expected_drive_session.drive_device_id)
        self.assertEqual(drive_session, expected_drive_session)

    def assert_find_drive_session_id_requested(self, request):
        request.assert_url_starts_with('https://drive_api/api/staff/head/session?')
        request.assert_properties_equal(method='GET')
        request.assert_query_equals({'device_id': DRIVE_DEVICE_ID1})

    def save_device_public_key(self, key=None):
        if key is None:
            key = self.build_device_public_key()
        insert_device_public_key(key)

    def build_device_public_key(self, owner_id=1, device_id=DRIVE_DEVICE_ID1):
        return DevicePublicKey(
            public_key=PUBLIC_KEY1,
            owner_id=owner_id,
            version=1,
            device_id=device_id,
        )

    def setup_signing_registry(self):
        signing_registry_config = {
            'default_version_id': '1',
            'versions': [
                {
                    'id':   '1',
                    'algorithm': 'SHA256',
                    'salt_length': 32,
                    'secret': '0' * 32,
                },
            ],
        }
        signing_registry = SigningRegistry()
        signing_registry.add_from_dict(signing_registry_config)
        LazyLoader.register('SigningRegistry', lambda: signing_registry)


@with_settings_hosts(
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DRIVE_API_RETRIES=1,
    DRIVE_API_TIMEOUT=1,
    DRIVE_API_URL='https://drive_api/',
    DRIVE_AUTH_FORWARDING_API_ENABLED=True,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    DRIVE_PRODUCTION_PUBLIC_KEY_OWNER_ID=1,
    DRIVE_VIRTUAL_PUBLIC_KEY_OWNER_ID=2,
    OAUTH_APPLICATION_AM_XTOKEN={
        'client_id': OAUTH_CLIENT_ID_XTOKEN,
        'client_secret': OAUTH_CLIENT_SECRET_XTOKEN,
    },
    OAUTH_CONSUMER='oauth_consumer',
    OAUTH_RETRIES=1,
    OAUTH_URL='https://oauth',
    UNKNOWN_DRIVE_SESSIONS_ALLOWED=False,
    ALLOW_DRIVE_SANDBOX_IDS=True,
    YDB_DRIVE_DATABASE='drive_database',
    YDB_DRIVE_ENABLED=True,
    YDB_RETRIES=1,
)
class TestIssueAuthorizationCodeView(BaseTestCase):
    def setUp(self):
        super(TestIssueAuthorizationCodeView, self).setUp()

        self.setup_signing_registry()
        self.setup_grants()
        self.setup_statbox_templates()
        self.setup_blackbox(device_public_key=self.build_device_public_key())
        self.setup_oauth()
        self.setup_ydb()
        self.setup_drive_api()

    def test_ok(self):
        rv = self.make_request()

        self.assert_issue_authorization_code_ok_response(rv)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_nonce'),
                self.env.statbox.entry('issue_authorization_code'),
            ],
        )
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.assert_authorization_code_requested(self.env.oauth.requests[0])
        self.assertEqual(len(self.env.blackbox.requests), 2)
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[0])
        self.assert_check_device_signature_requested(self.env.blackbox.requests[1])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.fake_drive_api.requests), 1)
        self.assert_find_drive_session_id_requested(self.fake_drive_api.requests[0])

    def test_ok_without_sandbox_device_id(self):
        self.setup_ydb(sandbox_device_id=Undefined)

        rv = self.make_request(exclude_args=['sandbox_device_id'])

        self.assert_issue_authorization_code_ok_response(rv)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_nonce'),
                self.env.statbox.entry('issue_authorization_code'),
            ],
        )
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.assert_authorization_code_requested(self.env.oauth.requests[0])
        self.assertEqual(len(self.env.blackbox.requests), 2)
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[0])
        self.assert_check_device_signature_requested(self.env.blackbox.requests[1])
        self.assert_drive_session_saved(expected_drive_session=self.build_drive_session(sandbox_device_id=Undefined))
        self.assertEqual(len(self.fake_drive_api.requests), 1)
        self.assert_find_drive_session_id_requested(self.fake_drive_api.requests[0])

    def test_ok_sandbox_device_id_changed(self):
        self.setup_ydb(sandbox_device_id=DRIVE_SANDBOX_DEVICE_ID2)

        rv = self.make_request()

        self.assert_issue_authorization_code_ok_response(rv)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_nonce'),
                self.env.statbox.entry('revoke_drive_device', device_id=DRIVE_SANDBOX_DEVICE_ID2),
                self.env.statbox.entry('issue_authorization_code'),
            ],
        )
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.assert_authorization_code_requested(self.env.oauth.requests[0])
        self.assertEqual(len(self.env.blackbox.requests), 2)
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[0])
        self.assert_check_device_signature_requested(self.env.blackbox.requests[1])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.fake_drive_api.requests), 1)
        self.assert_find_drive_session_id_requested(self.fake_drive_api.requests[0])

    def test_ok_custom_oauth_credentials(self):
        rv = self.make_request(
            query_args={
                'oauth_client_id': OAUTH_CLIENT_ID1,
                'oauth_client_secret': OAUTH_CLIENT_SECRET1,
            },
        )

        self.assert_issue_authorization_code_ok_response(rv)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('check_nonce'),
                self.env.statbox.entry('issue_authorization_code'),
            ],
        )
        self.assertEqual(len(self.env.oauth.requests), 1)
        self.assert_authorization_code_requested(
            self.env.oauth.requests[0],
            client_id=OAUTH_CLIENT_ID1,
            client_secret=OAUTH_CLIENT_SECRET1,
        )
        self.assertEqual(len(self.env.blackbox.requests), 2)
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[0])
        self.assert_check_device_signature_requested(self.env.blackbox.requests[1])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.fake_drive_api.requests), 1)
        self.assert_find_drive_session_id_requested(self.fake_drive_api.requests[0])

    def test_ydb_did_not_find_drive_session(self):
        rv = self.make_request(query_args={'drive_device_id': DRIVE_DEVICE_ID2})

        self.assert_error_response(rv, ['drive_session.not_found'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_ydb_timeout(self):
        self.fake_ydb_key_value.set_response_side_effect([ydb.Timeout('timeout')])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_invalid_signature(self):
        check_device_signature_response = blackbox_check_device_signature_response(
            status='SIGNATURE.INVALID',
            error='your password',
        )
        self.setup_blackbox(check_device_signature_response=check_device_signature_response)

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['internal.permanent'],
            # Не игнорим описание ошибки, чтобы быть уверенными, что секретное
            # описание отказа из ЧЯ не попадает в ответ ручки.
            ignore_error_message=False,
        )
        self.env.statbox.assert_equals([
            self.env.statbox.entry(
                'check_nonce',
                status='signature.invalid',
            ),
        ])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_public_key_not_found(self):
        check_device_signature_response = blackbox_check_device_signature_response(
            status='PUBLIC_KEY.NOT_FOUND',
            error='your password',
        )
        self.setup_blackbox(check_device_signature_response=check_device_signature_response)

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['public_key.not_found'],
            # Не игнорим описание ошибки, чтобы быть уверенными, что секретное
            # описание отказа из ЧЯ не попадает в ответ ручки.
            ignore_error_message=False,
        )
        self.env.statbox.assert_equals([
            self.env.statbox.entry(
                'check_nonce',
                status='public_key.not_found',
            ),
        ])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_blackbox_invalid_response(self):
        self.env.blackbox.set_response_side_effect('check_device_signature', [])

    def test_blackbox_check_device_signature_invalid_response(self):
        self.env.blackbox.set_response_side_effect('check_device_signature', [BlackboxInvalidResponseError()])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry(
                'check_nonce',
                status='invalid_response',
            ),
        ])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_blackbox_get_device_public_key_timeout(self):
        self.env.blackbox.set_response_side_effect('get_device_public_key', [RequestError()])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([])
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_oauth_timeout(self):
        self.env.oauth.set_response_side_effect('issue_authorization_code', [RequestError()])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])

    def test_invalid_client_id(self):
        self.env.oauth.set_response_side_effect(
            'issue_authorization_code',
            [
                oauth_bundle_error_response('client.not_found'),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['oauth_client_id.invalid'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])

    def test_invalid_client_secret(self):
        self.env.oauth.set_response_side_effect(
            'issue_authorization_code',
            [
                oauth_bundle_error_response('client_secret.not_matched'),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['oauth_client_secret.invalid'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])

    def test_drive_does_not_find_session(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_not_found_response(),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_drive_access_denied(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_access_denied_response(),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])

    def test_drive_finds_other_session(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID2),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_drive_timeout(self):
        self.fake_drive_api.set_response_side_effect('find_drive_session_id', [RequestError()])

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([
            self.env.statbox.entry('check_nonce'),
        ])
        self.assert_drive_session_saved()
        self.assertEqual(len(self.env.oauth.requests), 0)

    def test_test_drive_session_id(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID2),
            ],
        )

        rv = self.make_request(query_args={'test_drive_session_id': DRIVE_SESSION_ID1})

        self.assert_error_response(rv, ['internal.permanent'])

    def test_check_drive_session__non_virtual_headunit(self):
        rv = self.make_request(query_args={
            'check_drive_session': 'false',
            'drive_device_id': DRIVE_DEVICE_ID1,
        })
        assert self.fake_drive_api.requests == []
        self.assert_error_response(rv, ['internal.permanent'])

    def test_check_drive_session__virtual_headunit(self):
        device_public_key = self.build_device_public_key(owner_id=2, device_id=DRIVE_DEVICE_ID2)
        self.setup_blackbox(device_public_key=device_public_key)
        self.setup_ydb(drive_device_id=DRIVE_DEVICE_ID2)
        rv = self.make_request(query_args={
            'check_drive_session': 'false',
            'drive_device_id': DRIVE_DEVICE_ID2,
        })
        assert self.fake_drive_api.requests == []
        self.assert_issue_authorization_code_ok_response(rv)

    def test_forbidden_user_ip(self):
        rv = self.make_request(headers={'user_ip': TEST_CONSUMER_IP1})
        self.assert_error_response(rv, ['access.denied'], status_code=403)


@with_settings_hosts(
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DRIVE_API_RETRIES=1,
    DRIVE_API_TIMEOUT=1,
    DRIVE_API_URL='https://drive_api/',
    DRIVE_AUTH_FORWARDING_API_ENABLED=True,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    DRIVE_PRODUCTION_PUBLIC_KEY_OWNER_ID=1,
    DRIVE_VIRTUAL_PUBLIC_KEY_OWNER_ID=2,
    OAUTH_APPLICATION_AM_XTOKEN={
        'client_id': OAUTH_CLIENT_ID_XTOKEN,
        'client_secret': OAUTH_CLIENT_SECRET_XTOKEN,
    },
    OAUTH_CONSUMER='oauth_consumer',
    OAUTH_RETRIES=1,
    OAUTH_URL='https://oauth',
    UNKNOWN_DRIVE_SESSIONS_ALLOWED=True,
    YDB_DRIVE_DATABASE='drive_database',
    YDB_DRIVE_ENABLED=True,
    YDB_RETRIES=1,
)
class TestIssueAuthorizationCodeViewTestDriveSessionId(BaseTestCase):
    def setUp(self):
        super(TestIssueAuthorizationCodeViewTestDriveSessionId, self).setUp()

        self.setup_signing_registry()
        self.setup_grants()
        self.setup_statbox_templates()
        self.setup_blackbox(device_public_key=self.build_device_public_key())
        self.setup_oauth()
        self.setup_ydb()

    def test_test_drive_session_id(self):
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(DRIVE_SESSION_ID2),
            ],
        )

        rv = self.make_request(query_args={'test_drive_session_id': DRIVE_SESSION_ID1})

        self.assert_issue_authorization_code_ok_response(rv)


@with_settings_hosts(
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DRIVE_API_RETRIES=1,
    DRIVE_API_TIMEOUT=1,
    DRIVE_API_URL='https://drive_api/',
    DRIVE_AUTH_FORWARDING_API_ENABLED=True,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    DRIVE_PRODUCTION_PUBLIC_KEY_OWNER_ID=1,
    DRIVE_VIRTUAL_PUBLIC_KEY_OWNER_ID=2,
    OAUTH_APPLICATION_AM_XTOKEN={
        'client_id': OAUTH_CLIENT_ID_XTOKEN,
        'client_secret': OAUTH_CLIENT_SECRET_XTOKEN,
    },
    OAUTH_CONSUMER='oauth_consumer',
    OAUTH_RETRIES=1,
    OAUTH_URL='https://oauth',
    UNKNOWN_DRIVE_SESSIONS_ALLOWED=False,
    YDB_DRIVE_DATABASE='drive_database',
    YDB_DRIVE_ENABLED=True,
    YDB_RETRIES=1,
)
class TestIssueAuthorizationCodeViewNotRestrictedOwnerAndForbiddenUserIp(BaseTestCase):
    def setUp(self):
        super(TestIssueAuthorizationCodeViewNotRestrictedOwnerAndForbiddenUserIp, self).setUp()

        self.setup_signing_registry()
        self.setup_grants()
        self.setup_statbox_templates()
        self.setup_blackbox()
        self.setup_oauth()
        self.setup_ydb()
        self.setup_drive_api()

    def test(self):
        device_public_key = self.build_device_public_key(owner_id=2)
        self.setup_blackbox(device_public_key=device_public_key)

        rv = self.make_request(headers={'user_ip': TEST_CONSUMER_IP1})

        self.assert_issue_authorization_code_ok_response(rv)
