# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.exceptions import BaseCoreError


class TestBaseCoreError(unittest.TestCase):

    def test_str(self):
        eq_(str(BaseCoreError()), 'BaseCoreError')
        eq_(str(BaseCoreError('my message')), 'my message')
        eq_(str(BaseCoreError({'foo': 'bar'})), str({'foo': 'bar'}))
        eq_(str(BaseCoreError({'foo': u'раз'})), str({'foo': u'раз'}))
        eq_(str(BaseCoreError(u'раз')), 'раз')
        eq_(str(BaseCoreError(u'раз', u'два')), str((u'раз', u'два')))
