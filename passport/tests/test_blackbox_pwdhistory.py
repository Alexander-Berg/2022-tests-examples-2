# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import with_settings
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestPwdHistory(BaseBlackboxRequestTestCase):

    def test_pwdhistory_found(self):
        self.set_blackbox_response_value(b'''{"password_history_result":"found"}''')
        response = self.blackbox.pwdhistory(1, 'password', 0)
        eq_(response['found_in_history'], True)

    def test_pwd_history_not_found(self):
        self.set_blackbox_response_value(b'''{"password_history_result":"not_found"}''')
        response = self.blackbox.pwdhistory(1, 'password', 0)
        eq_(response['found_in_history'], False)


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestPwdHistoryUrl(BaseBlackboxTestCase):

    def test_pwdhistory_url(self):
        request_info = Blackbox().build_pwdhistory_request(uid=42, password='pass', depth=1)
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')

    def test_pwdhistory_request(self):
        request = Blackbox().build_pwdhistory_request(uid=42, password='pass', depth=1)

        eq_(request.post_args['method'], 'pwdhistory')
        eq_(request.post_args['uid'], 42)
        eq_(request.post_args['depth'], 1)
        eq_(request.post_args['password'], 'pass')
        ok_('reason' not in request.post_args)

    def test_pwdhistory_request_with_reason_specified(self):
        request = Blackbox().build_pwdhistory_request(uid=42, password='pass', depth=1, reason=[1, 2, 3])

        eq_(request.post_args['method'], 'pwdhistory')
        eq_(request.post_args['uid'], 42)
        eq_(request.post_args['depth'], 1)
        eq_(request.post_args['password'], 'pass')
        eq_(request.post_args['reason'], '1,2,3')
