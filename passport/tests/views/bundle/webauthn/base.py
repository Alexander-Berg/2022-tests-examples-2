# -*- coding: utf-8 -*-
import base64
from binascii import hexlify
from datetime import datetime

from fido2 import cbor
from fido2.cose import ES256
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_HOST,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.utils.common import deep_merge
from soft_webauthn import SoftWebauthnDevice


TEST_ORIGIN = '127.0.0.1:1234'
TEST_DEVICE_NAME = 'Android Chrome'
TEST_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; LG-H818 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.95 Mobile Safari/537.36'
TEST_BROWSER_ID = 83  # соответствует юзерагенту
TEST_OS_FAMILY_ID = 433  # соответствует юзерагенту

TEST_RP_ID = 'passport-test.yandex.ru'

TEST_UNIXTIME = 100500
TEST_DATETIME = datetime.fromtimestamp(TEST_UNIXTIME)

TEST_CHALLENGE_RANDOM_BYTES = b'1' * 32
TEST_CHALLENGE_BASE64 = base64.urlsafe_b64encode(TEST_CHALLENGE_RANDOM_BYTES).decode().rstrip('=')

TEST_EXPECTED_MAKE_CREDENTIAL_OPTIONS = {
    'attestation': 'direct',
    'authenticatorSelection': {
        'userVerification': 'preferred',
        'authenticatorAttachment': 'platform',
    },
    'challenge': TEST_CHALLENGE_BASE64,
    'excludeCredentials': [],
    'extensions': {
        'webauthn.loc': True,
    },
    'pubKeyCredParams': [
        {
            'alg': -7,
            'type': 'public-key',
        },
        {
            'alg': -257,
            'type': 'public-key',
        },
        {
            'alg': -37,
            'type': 'public-key',
        },
    ],
    'rp': {
        'id': TEST_RP_ID,
        'name': 'Yandex',
    },
    'timeout': 60000,
    'user': {
        'id': str(TEST_UID),
        'name': TEST_LOGIN,
        'displayName': TEST_DISPLAY_NAME,
        'icon': 'https://localhost/get-yapic/0/0-0/normal',
    },
}

fake_webauthn = SoftWebauthnDevice()
rv_create = fake_webauthn.create(
    {
        'publicKey': dict(
            TEST_EXPECTED_MAKE_CREDENTIAL_OPTIONS,
            attestation='none',
            challenge=TEST_CHALLENGE_RANDOM_BYTES,
        ),
    },
    TEST_ORIGIN,
)

TEST_CREDENTIAL_PUBLIC_KEY = base64.urlsafe_b64encode(
    cbor.encode(
        ES256.from_cryptography_key(fake_webauthn.private_key.public_key()),
    ),
).decode().rstrip('=')
TEST_CREDENTIAL_EXTERNAL_ID = rv_create['id'].decode().rstrip('=')

TEST_ATTESTATION_OBJECT = rv_create['response']['attestationObject']
TEST_ATTESTATION_OBJECT_BASE64 = base64.b64encode(TEST_ATTESTATION_OBJECT).decode()

TEST_CLIENT_DATA_CREATE = rv_create['response']['clientDataJSON']
TEST_CLIENT_DATA_CREATE_BASE64 = base64.b64encode(TEST_CLIENT_DATA_CREATE).decode()

TEST_EXPECTED_ASSERTION_OPTIONS = {
    'allowCredentials': [
        {
            'id': TEST_CREDENTIAL_EXTERNAL_ID,
            'transports': [
                'usb',
                'nfc',
                'ble',
                'internal',
            ],
            'type': 'public-key',
        },
    ],
    'challenge': TEST_CHALLENGE_BASE64,
    'rpId': TEST_RP_ID,
    'timeout': 60000,
    'userVerification': 'required',
}

rv_get = fake_webauthn.get(
    {
        'publicKey': dict(
            TEST_EXPECTED_ASSERTION_OPTIONS,
            challenge=TEST_CHALLENGE_RANDOM_BYTES,
        ),
    },
    TEST_ORIGIN,
)

TEST_CLIENT_DATA_GET = rv_get['response']['clientDataJSON']
TEST_CLIENT_DATA_GET_BASE64 = base64.b64encode(TEST_CLIENT_DATA_GET).decode()

TEST_AUTH_DATA = rv_get['response']['authenticatorData']
TEST_AUTH_DATA_BASE64 = base64.b64encode(TEST_AUTH_DATA).decode()

TEST_SIGNATURE = rv_get['response']['signature']
TEST_SIGNATURE_HEX = hexlify(TEST_SIGNATURE).decode()


class BaseWebauthnTestCase(BaseBundleTestViews):
    http_method = 'POST'
    http_headers = {
        'host': TEST_HOST,
        'cookie': 'Session_id=foo',
        'user_ip': TEST_USER_IP,
        'user_agent': TEST_USER_AGENT,
    }
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={'webauthn': ['manage', 'verify']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('universal')
        self.http_query_args.update(track_id=self.track_id)
        with self.track_transaction(self.track_id) as track:
            track.uid = TEST_UID
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        self.setup_blackbox_responses()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()

    def setup_blackbox_responses(self, has_secure_phone=True, has_webauthn_credentials=False, webautn_cred_kwargs=None):
        bb_kwargs = {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'display_name': TEST_DISPLAY_NAME_DATA,
        }

        if has_secure_phone:
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )
            bb_kwargs = deep_merge(bb_kwargs, phone_secured)

        if has_webauthn_credentials:
            cred = {
                'id': 1,
                'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'public_key': '1:%s' % TEST_CREDENTIAL_PUBLIC_KEY,
                'sign_count': 0,
                'device_name': TEST_DEVICE_NAME,
                'os_family_id': TEST_OS_FAMILY_ID,
                'browser_id': TEST_BROWSER_ID,
                'is_device_mobile': '1',
                'relying_party_id': TEST_HOST,
                'created': TEST_DATETIME,
            }
            if webautn_cred_kwargs:
                for param, value in webautn_cred_kwargs.items():
                    if value is None:
                        del cred[param]
                    else:
                        cred[param] = value
            bb_kwargs.update(
                webauthn_credentials=[cred]
            )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**bb_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**bb_kwargs),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_USER_IP,
            track_id=self.track_id,
            mode='webauthn',
            consumer='dev',
            uid=str(TEST_UID),
            user_agent=TEST_USER_AGENT,
        )
