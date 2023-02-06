# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_sign_response,
    blackbox_sign_response,
)
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    iterdiff,
    with_settings_hosts,
)
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


eq_ = iterdiff(eq_)

TEST_SIGNED_VALUE = '1234567890.1555.AAAA.BBBBBBBB.CCCCC'
TEST_SIGN_SPACE = 'that_goodies'
TEST_TTL = 1000
TEST_VALUE = 'alohomora'


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestSignParse(BaseBlackboxRequestTestCase):
    def test_sign_ok(self):
        self.set_blackbox_response_value(blackbox_sign_response(TEST_SIGNED_VALUE))

        response = self.blackbox.sign(
            value=TEST_VALUE,
            ttl=TEST_TTL,
            sign_space=TEST_SIGN_SPACE,
        )
        eq_(
            response,
            dict(
                signed_value=TEST_SIGNED_VALUE,
            ),
        )

    def test_check_sign_ok(self):
        original_value = json.dumps({
            'uid': 123,
            'ttl': 600,
            'otp_counter': 0,
        })
        self.set_blackbox_response_value(blackbox_check_sign_response(original_value))

        response = self.blackbox.check_sign(
            signed_value=TEST_SIGNED_VALUE,
            sign_space=TEST_SIGN_SPACE,
        )
        eq_(
            response,
            dict(
                status='OK',
                value=original_value,
            ),
        )

    def test_check_sign_not_ok(self):
        original_value = json.dumps({
            'uid': 1,
            'ttl': 600,
            'otp_counter': 0,
        })
        self.set_blackbox_response_value(blackbox_check_sign_response(original_value, status='EXPIRED'))

        response = self.blackbox.check_sign(
            signed_value=TEST_SIGNED_VALUE,
            sign_space=TEST_SIGN_SPACE,
        )
        eq_(
            response,
            dict(
                status='EXPIRED',
            ),
        )


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestSignRequest(BaseBlackboxTestCase):
    def test_sign_ok(self):
        request_info = Blackbox().build_sign_request(
            value=TEST_VALUE,
            ttl=TEST_TTL,
            sign_space=TEST_SIGN_SPACE,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'format': 'json',
                'method': 'sign',
                'value': TEST_VALUE,
                'ttl': str(TEST_TTL),
                'sign_space': TEST_SIGN_SPACE,
            },
        )

    def test_check_sign_ok(self):
        request_info = Blackbox().build_check_sign_request(
            signed_value=TEST_SIGNED_VALUE,
            sign_space=TEST_SIGN_SPACE,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'format': 'json',
                'method': 'check_sign',
                'signed_value': TEST_SIGNED_VALUE,
                'sign_space': TEST_SIGN_SPACE,
            },
        )
