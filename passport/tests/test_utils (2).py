# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    get_alias,
    get_attribute,
)


class TestBlackboxUtils(unittest.TestCase):
    def setUp(self):
        super(TestBlackboxUtils, self).setUp()
        self.bb_response = {
            'attributes': {
                '1': 1,
                '4': 2,
            },
            'aliases': {
                '1': 'some_login',
                '10': 'phne-123',
            },
        }

    def test_get_attribute(self):
        eq_(get_attribute(self.bb_response, 'account.global_logout_datetime'), 2)
        ok_(get_attribute(self.bb_response, 'account.user_defined_login') is None)

    @raises(KeyError)
    def test_get_attribute_by_invalid_name(self):
        get_attribute(self.bb_response, 'unknown_attribute')

    def test_get_attributes_from_empty_response(self):
        ok_(get_attribute({}, 'account.user_defined_login') is None)

    def test_get_alias(self):
        eq_(get_alias(self.bb_response, 'phonish'), 'phne-123')
        ok_(get_alias(self.bb_response, 'yandexoid') is None)

    @raises(KeyError)
    def test_get_alias_by_invalid_name(self):
        get_alias(self.bb_response, 'unknown_alias')

    def test_get_alias_from_empty_response(self):
        ok_(get_alias({}, 'yandexoid') is None)
