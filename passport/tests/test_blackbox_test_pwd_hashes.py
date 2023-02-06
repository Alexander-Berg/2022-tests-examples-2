# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import with_settings
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestTestPwdHashes(BaseBlackboxRequestTestCase):

    def test_test_pwd_hashes_ok(self):
        self.set_blackbox_response_value('''{"hashes": {"hash1": true, "hash2": false}}''')
        response = self.blackbox.test_pwd_hashes('password', ['hash1', 'hash2'])
        eq_(response, {'hash1': True, 'hash2': False})


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestTestPwdHashesUrl(BaseBlackboxTestCase):

    def test_test_pwd_hashes_url(self):
        request_info = Blackbox().build_test_pwd_hashes_request(password='pass', hashes=['hash'])
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

    def test_test_pwd_hashes_request(self):
        request = Blackbox().build_test_pwd_hashes_request(password='pass', hashes=['hash1', 'hash2'])

        eq_(request.post_args['method'], 'test_pwd_hashes')
        eq_(request.post_args['password'], 'pass')
        eq_(request.post_args['hashes'], 'hash1,hash2')

    def test_test_pwd_hashes_request_with_uid(self):
        request = Blackbox().build_test_pwd_hashes_request(password='pass', hashes=['hash1', 'hash2'], uid=123)

        eq_(request.post_args['method'], 'test_pwd_hashes')
        eq_(request.post_args['password'], 'pass')
        eq_(request.post_args['hashes'], 'hash1,hash2')
        eq_(request.post_args['uid'], 123)
