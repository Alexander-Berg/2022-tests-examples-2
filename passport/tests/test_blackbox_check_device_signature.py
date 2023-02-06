# -*- coding: utf-8 -*-

from datetime import datetime

from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidDeviceSignature
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_device_signature_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.utils.common import noneless_dict

from .test_blackbox import BaseBlackboxTestCase


DEVICE_ID1 = 'device_id1'
NONCE1 = 'nonce1'
NONCE_SIGN_SPACE1 = 'nonce_sign_space1'
PUBLIC_KEY1 = 'public_key1'
SIGNATURE1 = 'signature1'
TIMESTAMP1 = 1565879349
VERSION1 = 'version1'


@with_settings_hosts(
    BLACKBOX_URL='https://blackbox'
)
class TestRequest(BaseBlackboxTestCase):
    def setUp(self):
        super(TestRequest, self).setUp()
        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()
        self.blackbox = Blackbox()
        self.fake_blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(),
            ],
        )

    def tearDown(self):
        self.fake_blackbox.stop()
        del self.blackbox
        del self.fake_blackbox
        super(TestRequest, self).tearDown()

    def assert_check_device_signature_requested(
        self,
        nonce=NONCE1,
        nonce_sign_space=NONCE_SIGN_SPACE1,
        device_id=DEVICE_ID1,
        signature=SIGNATURE1,
        timestamp=None,
        public_key=None,
        version=None,
    ):
        self.assertEqual(len(self.fake_blackbox.requests), 1)
        post_args = {
            'method': 'check_device_signature',
            'format': 'json',
            'nonce': nonce,
            'nonce_sign_space': nonce_sign_space,
            'device_id': device_id,
            'signature': signature,
            'timestamp': timestamp,
            'public_key': public_key,
            'version': version,
        }
        post_args = noneless_dict(post_args)
        self.fake_blackbox.requests[0].assert_properties_equal(
            method='POST',
            url='https://blackbox/blackbox/',
            post_args=post_args,
        )

    def check_device_signature(
        self,
        nonce=NONCE1,
        nonce_sign_space=NONCE_SIGN_SPACE1,
        device_id=DEVICE_ID1,
        signature=SIGNATURE1,
        timestamp=None,
        public_key=None,
        version=None,
    ):
        kwargs = dict(
            nonce=nonce,
            nonce_sign_space=nonce_sign_space,
            device_id=device_id,
            signature=signature,
            timestamp=timestamp,
            public_key=public_key,
            version=version,
        )
        kwargs = noneless_dict(kwargs)
        self.blackbox.check_device_signature(**kwargs)

    @parameterized.expand(
        [
            ('nonce', NONCE1),
            ('nonce_sign_space', NONCE_SIGN_SPACE1),
            ('device_id', DEVICE_ID1),
            ('signature', SIGNATURE1),
            ('timestamp', TIMESTAMP1, str(TIMESTAMP1)),
            ('timestamp', TIMESTAMP1 + 0.3, str(TIMESTAMP1)),
            ('timestamp', datetime.fromtimestamp(TIMESTAMP1), str(TIMESTAMP1)),
            ('timestamp', str(TIMESTAMP1)),
            ('public_key', PUBLIC_KEY1),
            ('version', VERSION1),
        ],
    )
    def test(self, arg_name, arg_value, request_value=None):
        if request_value is None:
            request_value = arg_value
        self.check_device_signature(**{arg_name: arg_value})
        self.assert_check_device_signature_requested(**{arg_name: request_value})


@with_settings_hosts(
    BLACKBOX_URL='https://blackbox'
)
class TestResponse(BaseBlackboxTestCase):
    def setUp(self):
        super(TestResponse, self).setUp()
        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()
        self.blackbox = Blackbox()
        self.setup_response()

    def tearDown(self):
        self.fake_blackbox.stop()
        del self.blackbox
        del self.fake_blackbox
        super(TestResponse, self).tearDown()

    def check_device_signature(self):
        self.blackbox.check_device_signature(
            nonce=NONCE1,
            nonce_sign_space=NONCE_SIGN_SPACE1,
            device_id=DEVICE_ID1,
            signature=SIGNATURE1,
        )

    def setup_response(self, **kwargs):
        self.fake_blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(**kwargs),
            ],
        )

    def test_ok(self):
        rv = self.check_device_signature()
        self.assertIsNone(rv)

    def test_fail(self):
        self.setup_response(status='YET_ANOTHER_FAIL', error='your password')

        with self.assertRaises(BlackboxInvalidDeviceSignature) as assertion:
            self.check_device_signature()

        self.assertEqual(
            str(assertion.exception),
            'Invalid device signature: YET_ANOTHER_FAIL',
        )
        self.assertEqual(assertion.exception.security_info, 'your password')
