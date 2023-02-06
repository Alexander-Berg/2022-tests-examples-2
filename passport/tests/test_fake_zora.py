# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.base.faker.fake_builder import FakeBuilderError
from passport.backend.core.builders.zora import (
    Zora,
    ZoraTemporaryError,
)
from passport.backend.core.builders.zora.faker.fake_zora import (
    FakeZora,
    zora_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_URL = 'https://smth'
TEST_OK_RESPONSE_RAW = b'SOME RAW BYTES'


@with_settings(
    ZORA_HOST='localhost',
    ZORA_PORT='666',
    ZORA_RETRIES=2,
    ZORA_TIMEOUT=1,
    ZORA_SOURCE='source',
)
class FakeZoraTestCase(TestCase):
    def setUp(self):
        self.faker = FakeZora()
        self.faker.start()
        self.zora = Zora()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_ok(self):
        self.faker.set_response_value(TEST_URL, zora_response(TEST_OK_RESPONSE_RAW))
        eq_(self.zora.get(TEST_URL), TEST_OK_RESPONSE_RAW)

    @raises(ZoraTemporaryError)
    def test_zora_error(self):
        self.faker.set_response_value(TEST_URL, zora_response(
            reason='zora',
        ))
        self.zora.get(TEST_URL)

    @raises(FakeBuilderError)
    def test_fake_builder_error(self):
        self.zora.get(TEST_URL)

    def test_response_for_any_url_ok(self):
        self.faker.set_response_value_without_method(zora_response(TEST_OK_RESPONSE_RAW))
        eq_(self.zora.get(TEST_URL), TEST_OK_RESPONSE_RAW)
