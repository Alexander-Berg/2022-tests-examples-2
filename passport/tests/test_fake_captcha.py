# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.builders.captcha.faker import FakeCaptcha


class FakeCaptchaTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_captcha = FakeCaptcha()
        self.fake_captcha.start()

    def tearDown(self):
        self.fake_captcha.stop()
        del self.fake_captcha

    def test_getattr(self):
        eq_(self.fake_captcha._mock.foo, self.fake_captcha.foo)
