# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.kolmogor import Kolmogor
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.test.test_utils import with_settings


TEST_SPACE = 'keyspace'
TEST_KEYS = ['key1', 'key2']


@with_settings(
    KOLMOGOR_URL='http://localhost/',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=2,
)
class FakeKolmogorTestCase(TestCase):
    def setUp(self):
        self.faker = FakeKolmogor()
        self.faker.start()
        self.kolmogor = Kolmogor()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_get(self):
        self.faker.set_response_value('get', '0,1')
        eq_(self.kolmogor.get(TEST_SPACE, TEST_KEYS), {'key1': 0, 'key2': 1})

    def test_inc(self):
        self.faker.set_response_value('inc', 'OK')
        ok_(self.kolmogor.inc(TEST_SPACE, TEST_KEYS) is None)
