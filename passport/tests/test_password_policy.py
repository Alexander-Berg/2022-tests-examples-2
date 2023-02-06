# -*- coding: utf-8 -*-

import re
from unittest import TestCase

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.password import policy


class PasswordPolicyTest(TestCase):

    def test_successful_object_creation(self):
        p = policy.Policy(
            max_length=20,
            min_length=10,
            min_quality=50,
            middle_quality=70,
            prohibited_symbols_re=re.compile(r'[^abc]'),
            search_depth=1,
            reason=None,
        )
        eq_(p.max_length, 20)
        eq_(p.min_length, 10)
        eq_(p.min_quality, 50)
        eq_(p.middle_quality, 70)
        eq_(p.prohibited_symbols_re.pattern, r'[^abc]')
        eq_(p.search_depth, 1)
        assert_is_none(p.reason)

    def test_predefined_policies_must_be_copies(self):
        basic1 = policy.basic()
        basic1.min_length = 100
        basic2 = policy.basic()
        basic2.min_length = 200
        ok_(basic1.min_length != basic2.min_length)
