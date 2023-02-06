# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.gender import Gender


class TestGender(PassportTestCase):
    def test_from_char(self):
        TEST_TABLE = [
            ('m', Gender.Male),
            ('f', Gender.Female),
            ('u', Gender.Unknown),
            ('', Gender.Unknown),
        ]
        for char, gender in TEST_TABLE:
            ok_(Gender.from_char(char.lower()) is gender)
            ok_(Gender.from_char(char.upper()) is gender)

        ok_(Gender.from_char(None) is Gender.Unknown)

    def test_to_char(self):
        TEST_TABLE = [
            ('m', Gender.Male),
            ('f', Gender.Female),
            (None, Gender.Unknown),
        ]
        for char, gender in TEST_TABLE:
            eq_(Gender.to_char(gender), char)
