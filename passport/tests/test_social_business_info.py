# -*- coding: utf-8 -*-
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.social_business_info import BusinessInfo


class TestSocialBusinessInfo(PassportTestCase):

    def test_simple_ok(self):
        info = BusinessInfo(1, 'abc')
        eq_(info.id, 1)
        eq_(info.token, 'abc')

    def test_from_dict(self):
        info = BusinessInfo.from_dict({'id': 1, 'token': 'abc', 'other': 'data'})
        eq_(info.id, 1)
        eq_(info.token, 'abc')

        eq_(BusinessInfo.from_dict(None), None)
        eq_(BusinessInfo.from_dict({}), None)

        with assert_raises(ValueError):
            BusinessInfo.from_dict({'id': 1})

        with assert_raises(ValueError):
            BusinessInfo.from_dict({'token': 'abc'})

    def test_is_hashable(self):
        info = BusinessInfo(1, 'abc')
        eq_(list({info}), [info])
