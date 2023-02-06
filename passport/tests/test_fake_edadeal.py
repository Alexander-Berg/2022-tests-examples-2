# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    ok_,
    raises,
)
from passport.backend.core.builders.edadeal import (
    EdadealApi,
    EdadealPermanentError,
)
from passport.backend.core.builders.edadeal.faker import FakeEdadealApi
from passport.backend.core.test.test_utils import with_settings


TEST_EDADEAL_TOKEN = '123-qwe'
TEST_UID = 1


@with_settings(
    EDADEAL_URL='http://localhost',
    EDADEAL_TIMEOUT=1,
    EDADEAL_RETRIES=1,
    EDADEAL_TOKEN=TEST_EDADEAL_TOKEN,
)
class FakeEdadealTestCase(TestCase):
    def setUp(self):
        self.faker = FakeEdadealApi()
        self.faker.start()
        self.edadeal = EdadealApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_update_plus_ok(self):
        self.faker.set_response_value('update_plus_status', b'')
        ok_(not self.edadeal.update_plus_status(TEST_UID, is_active=True))

    @raises(EdadealPermanentError)
    def test_create_session_error(self):
        self.faker.set_response_side_effect('update_plus_status', EdadealPermanentError)
        self.edadeal.update_plus_status(TEST_UID, is_active=False)
