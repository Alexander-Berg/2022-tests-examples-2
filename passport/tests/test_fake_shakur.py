# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.shakur import Shakur
from passport.backend.core.builders.shakur.faker.fake_shakur import (
    FakeShakur,
    shakur_check_password,
)
from passport.backend.core.test.test_utils import with_settings


TEST_SHA_PREFIX = '11111111'


@with_settings(
    SHAKUR_LIMIT=100,
    SHAKUR_URL='http://localhost/',
    SHAKUR_RETRIES=2,
    SHAKUR_TIMEOUT=3,
    SHAKUR_USE_TVM=False,
    IS_SHAKUR_CHECK_DISABLED=False,
)
class FakeShakurTestCase(TestCase):
    def setUp(self):
        self.faker = FakeShakur()
        self.faker.start()
        self.shakur = Shakur()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_check_password(self):
        self.faker.set_response_value(
            'check_password',
            json.dumps(shakur_check_password(TEST_SHA_PREFIX)),
        )
        eq_(
            self.shakur.check_password(TEST_SHA_PREFIX),
            shakur_check_password(TEST_SHA_PREFIX),
        )
