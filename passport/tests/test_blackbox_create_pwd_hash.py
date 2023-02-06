# -*- coding: utf-8 -*-
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import with_settings
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCreatePwdHash(BaseBlackboxRequestTestCase):

    def test_create_pwd_hash_ok(self):
        self.set_blackbox_response_value(br'{"hash": "5:$1$5LZPAbej$n72mVDeSiIczF9Wkcz1y7\/"}')
        response = self.blackbox.create_pwd_hash(version='5', uid=12345, password='password')
        eq_(response, r'5:$1$5LZPAbej$n72mVDeSiIczF9Wkcz1y7/')


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestCreatePwdHashUrl(BaseBlackboxTestCase):

    def test_create_pwd_hash_url(self):
        request_info = Blackbox().build_create_pwd_hash_request(password='pass', version='1')
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

    def test_create_pwd_hash_request_via_password(self):
        request = Blackbox().build_create_pwd_hash_request(password='pass', version='3')

        eq_(
            request.post_args,
            {
                'format': 'json',
                'method': 'create_pwd_hash',
                'ver': '3',
                'password': 'pass',
            },
        )

    def test_create_pwd_hash_request_via_md5crypt_hash(self):
        request = Blackbox().build_create_pwd_hash_request(md5crypt_hash='md5crypt', version='6')

        eq_(
            request.post_args,
            {
                'format': 'json',
                'method': 'create_pwd_hash',
                'ver': '6',
                'md5crypt': 'md5crypt',
            },
        )

    def test_create_pwd_hash_request_via_raw_md5_hash(self):
        request = Blackbox().build_create_pwd_hash_request(rawmd5_hash='md5raw', version='7')

        eq_(
            request.post_args,
            {
                'format': 'json',
                'method': 'create_pwd_hash',
                'ver': '7',
                'rawmd5': 'md5raw',
            },
        )

    def test_create_pwd_hash_request_not_enough_params(self):
        with assert_raises(ValueError):
            Blackbox().build_create_pwd_hash_request(version='1')

    def test_create_pwd_hash_request_too_many_params(self):
        with assert_raises(ValueError):
            Blackbox().build_create_pwd_hash_request(password='pass', rawmd5_hash='md5raw', version='1')

    def test_create_pwd_hash_request_with_uid(self):
        request = Blackbox().build_create_pwd_hash_request(password='pass', version='5', uid=12345)

        eq_(
            request.post_args,
            {
                'format': 'json',
                'method': 'create_pwd_hash',
                'ver': '5',
                'password': 'pass',
                'uid': '12345',
            },
        )
