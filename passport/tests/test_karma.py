# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.models.karma import Karma


class TestKarma(unittest.TestCase):

    def test_karma_parsed(self):
        karma = Karma().parse({'karma': 99})
        eq_(karma.prefix, 0)
        eq_(karma.suffix, 99)
        ok_(not karma.activation_datetime)
        ok_(not karma.is_empty())
        ok_(not karma.is_washed())
        eq_(karma.value, 99)
        ok_(not karma.parent)

    def test_washed_karma_parsed(self):
        karma = Karma().parse({'karma': 6099})
        eq_(karma.prefix, 6)
        eq_(karma.suffix, 99)
        ok_(not karma.activation_datetime)
        ok_(not karma.is_empty())
        ok_(karma.is_washed())
        eq_(karma.value, 6099)
        ok_(not karma.parent)

    def test_zero_karma_parsed(self):
        karma = Karma().parse({'karma': 0})
        eq_(karma.prefix, 0)
        eq_(karma.suffix, 0)
        ok_(not karma.activation_datetime)
        ok_(not karma.is_empty())
        ok_(not karma.is_washed())
        eq_(karma.value, 0)
        ok_(not karma.parent)

    def test_empty_karma_parsed(self):
        karma = Karma().parse({'karma': None})
        ok_(not karma.prefix)
        ok_(not karma.suffix)
        ok_(not karma.activation_datetime)
        ok_(karma.is_empty())
        ok_(not karma.is_washed())
        ok_(not karma.value)
        ok_(not karma.parent)

    def test_wtf_karma_not_parsed(self):
        with assert_raises(TypeError):
            Karma().parse({'karma': ''})
