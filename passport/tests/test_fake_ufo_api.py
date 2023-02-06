# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.ufo_api import UfoApi
from passport.backend.core.builders.ufo_api.faker import FakeUfoApi
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = 1
TEST_PHONE = PhoneNumber.parse('+79091234567')


@with_settings(
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=2,
    UFO_API_TIMEOUT=1,
    UFO_API_USE_RC=False,
)
class FakeUfoApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeUfoApi()
        self.faker.start()
        self.ufo_api = UfoApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_known_methods(self):
        response = {'a': 'b'}
        for method, args in [
                (
                    'profile',
                    (
                        TEST_UID,
                    ),
                ),
                (
                    'phones_stats',
                    (
                        TEST_PHONE,
                    ),
                ),
        ]:
            self.faker.set_response_value(
                method,
                json.dumps(response),
            )
            eq_(
                getattr(self.ufo_api, method)(*args),
                response,
            )

    def test_unknown_methods(self):
        for method in ['acb', 'profiles']:
            for response_setter in [
                    'set_response_value',
                    'set_response_side_effect',
            ]:
                with assert_raises(ValueError):
                    getattr(self.faker, response_setter)(
                        method,
                        None,
                    )

    def test_set_side_effect(self):
        self.faker.set_response_side_effect(
            'profile',
            ValueError,
        )
        with assert_raises(ValueError):
            self.ufo_api.profile(TEST_UID)
