# -*- coding: utf-8 -*-

from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_device_public_key_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import with_settings_hosts

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
            'get_device_public_key',
            [
                blackbox_get_device_public_key_response(),
            ],
        )

    def tearDown(self):
        self.fake_blackbox.stop()
        del self.blackbox
        del self.fake_blackbox
        super(TestRequest, self).tearDown()

    def test(self):
        self.blackbox.get_device_public_key(DEVICE_ID1)

        request = self.fake_blackbox.requests[0]
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_equals(
            {
                'method': 'get_device_public_key',
                'format': 'json',
                'device_id': DEVICE_ID1,
            },
        )
