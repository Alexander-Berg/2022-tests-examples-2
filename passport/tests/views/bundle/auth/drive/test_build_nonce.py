# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_USER_IP1,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_device_public_key_response,
    blackbox_sign_response,
)
from passport.backend.core.device_public_key import insert_device_public_key
from passport.backend.core.models.device_public_key import DevicePublicKey
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.useragent.sync import RequestError


DRIVE_DEVICE_ID1 = '1' * 32
NONCE1 = 'nonce1'
OWNER1 = 'device_owner1'
OWNER2 = 'device_owner2'
PUBLIC_KEY1 = 'key1'
TTL1 = 11


@with_settings_hosts(
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DRIVE_AUTH_FORWARDING_NONCE_TTL=TTL1,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    DRIVE_PRODUCTION_PUBLIC_KEY_OWNER_ID=1,
)
class TestBuildNonceView(BaseBundleTestViews):
    default_url = '/1/bundle/auth/forward_drive/build_nonce/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP1,
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    http_query_args = {
        'drive_device_id': DRIVE_DEVICE_ID1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestBuildNonceView, self).setUp()
        self.env = ViewsTestEnvironment()

        self.__patches = [
            self.env,
        ]
        for patch in self.__patches:
            patch.start()

        self.setup_grants()
        self.setup_statbox_templates()
        self.setup_blackbox()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.env
        super(TestBuildNonceView, self).tearDown()

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'auth_forward_drive': ['build_nonce'],
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
        self.env.statbox.bind_entry(
            'build_nonce',
            action='build_nonce',
            mode='forward_auth_to_drive_device',
            drive_device_id=DRIVE_DEVICE_ID1,
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
        )

    def setup_blackbox(self, device_public_key=None):
        self.env.blackbox.set_response_side_effect(
            'sign',
            [blackbox_sign_response(NONCE1)],
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

    def assert_build_nonce_ok_response(self, rv):
        self.assert_ok_response(rv, nonce=NONCE1)

    def assert_blackbox_sign_request_ok(self, request):
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'sign',
                'sign_space': 'auto_head_unit',
                'ttl': str(TTL1),
                'value': DRIVE_DEVICE_ID1,
            },
        )

    def assert_blackbox_get_device_public_key_request_ok(self, request):
        request.assert_query_equals(
            {
                'format': 'json',
                'method': 'get_device_public_key',
                'device_id': DRIVE_DEVICE_ID1,
            },
        )

    def save_device_public_key(self, key=None):
        if key is None:
            key = self.build_device_public_key()
        insert_device_public_key(key)

    def build_device_public_key(self, owner_id=1):
        return DevicePublicKey(
            public_key=PUBLIC_KEY1,
            owner_id=owner_id,
            version=1,
            device_id=DRIVE_DEVICE_ID1,
        )

    def test_ok(self):
        self.setup_blackbox(
            device_public_key=self.build_device_public_key(),
        )

        rv = self.make_request()

        self.assert_build_nonce_ok_response(rv)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('build_nonce'),
            ],
        )
        self.assert_blackbox_get_device_public_key_request_ok(self.env.blackbox.requests[0])
        self.assert_blackbox_sign_request_ok(self.env.blackbox.requests[1])

    def test_blackbox_sign_failed(self):
        self.setup_blackbox(
            device_public_key=self.build_device_public_key(),
        )

        self.env.blackbox.set_response_side_effect('sign', RequestError())

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([])

    def test_blackbox_get_device_public_key_failed(self):
        self.env.blackbox.set_response_side_effect('get_device_public_key', RequestError())

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.env.statbox.assert_equals([])

    def test_forbidden_user_ip(self):
        self.setup_blackbox(
            device_public_key=self.build_device_public_key(),
        )

        rv = self.make_request(headers={'user_ip': TEST_CONSUMER_IP1})

        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def test_not_restricted_owner_and_forbidden_user_ip(self):
        key = self.build_device_public_key(owner_id=2)
        self.setup_blackbox(device_public_key=key)

        rv = self.make_request(headers={'user_ip': TEST_CONSUMER_IP1})

        self.assert_build_nonce_ok_response(rv)
