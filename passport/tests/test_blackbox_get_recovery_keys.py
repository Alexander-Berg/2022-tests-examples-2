# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_recovery_keys_response
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_UID = 1
TEST_KEY_ID = 'id'
TEST_RECOVERY_KEY = 'key'


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestGetRecoveryKeysParse(BaseBlackboxRequestTestCase):
    def test_parse_exists(self):
        self.set_blackbox_response_value(blackbox_get_recovery_keys_response(TEST_RECOVERY_KEY))
        response = self.blackbox.get_recovery_keys(TEST_UID, TEST_KEY_ID)
        eq_(response, TEST_RECOVERY_KEY)

    def test_parse_not_found(self):
        self.set_blackbox_response_value(blackbox_get_recovery_keys_response(None))
        response = self.blackbox.get_recovery_keys(TEST_UID, TEST_KEY_ID)
        ok_(response is None)


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestGetRecoveryKeysUrl(BaseBlackboxTestCase):
    def test_get_recovery_keys_url(self):
        request_info = Blackbox().build_get_recovery_keys_request(TEST_UID, TEST_KEY_ID)
        check_all_url_params_match(
            request_info.url,
            {
                'uid': str(TEST_UID),
                'method': 'get_recovery_keys',
                'key_id': TEST_KEY_ID,
                'format': 'json',
            },
        )
