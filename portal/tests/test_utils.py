#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
from morda import utils


class TestUnicodeUtils(unittest.TestCase):

    def test_is_unicode(self):
        self.assertTrue(utils.is_unicode(u'ыы'))
        if sys.version_info[0] < 3:
            self.assertFalse(utils.is_unicode(bytes('ыы')))
            self.assertFalse(utils.is_unicode(bytearray('ыы')))
        else:
            self.assertFalse(utils.is_unicode(bytes('ыы'.encode('utf-8'))))
            self.assertFalse(utils.is_unicode(bytearray('ыы'.encode('utf-8'))))

    def test_any_to_unicode(self):
        expected = u'ыыы'
        tests = [
            u'ыыы',
            'ыыы' if sys.version_info[0] < 3 else bytes('ыыы'.encode('utf-8')),
        ]
        for t in tests:
            self.assertEqual(utils.any_to_unicode(t), expected)

    def test_any_to_bytes(self):
        expected = 'ыыы' if sys.version_info[
            0] < 3 else bytes('ыыы'.encode('utf-8'))
        tests = [
            u'ыыы',
            'ыыы' if sys.version_info[0] < 3 else bytes('ыыы'.encode('utf-8')),
        ]
        for t in tests:
            self.assertEqual(utils.any_to_bytes(t), expected)
