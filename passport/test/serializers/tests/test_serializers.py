# -*- coding: utf-8 -*-

import unittest

from passport.backend.core.test.serializers.serializers import (
    bool_to_yesno,
    number_to_str,
)


class TestSerializers(unittest.TestCase):
    def test_bool_to_yesno(self):
        assert bool_to_yesno(True) == u'yes'
        assert bool_to_yesno(False) == u'no'
        assert bool_to_yesno(None) == u''
        self.assertRaises(TypeError, bool_to_yesno, u'yes')
        self.assertRaises(TypeError, bool_to_yesno, u'no')
        self.assertRaises(TypeError, bool_to_yesno, u'')
        self.assertRaises(TypeError, bool_to_yesno, 0)
        self.assertRaises(TypeError, bool_to_yesno, 1)

    def test_number_to_str(self):
        assert number_to_str(13) == u'13'
        assert number_to_str(None) == u''
        self.assertRaises(TypeError, number_to_str, u'13')
        self.assertRaises(TypeError, number_to_str, u'0xd')
