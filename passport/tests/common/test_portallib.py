# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.common.portallib import (
    get_net,
    InvalidIpHeaderError,
    is_yandex_ip,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class TestIpReg(BaseTestCase):
    def setUp(self):
        super(TestIpReg, self).setUp()
        self.headers = {
            'HTTP_ACCEPT_LANGUAGE': 'ru',
            'HTTP_COOKIE': 'foo=bar',
            'HTTP_X_REAL_IP': '1.1.1.1',
        }

    def test_get_net(self):
        actual = get_net('8.8.8.8', self.headers)
        eq_(actual['real_ip'], '8.8.8.8')

        # текущий ip passport-dev
        actual = get_net('87.250.235.4', self.headers)
        eq_(actual['real_ip'], '87.250.235.4')

    @raises(InvalidIpHeaderError)
    def test_get_net_invalid_header(self):
        get_net('8.8.8.8, 1.2.3.4', self.headers)

    def test_is_yandex_ip(self):
        ok_(not is_yandex_ip('8.8.8.8'))
