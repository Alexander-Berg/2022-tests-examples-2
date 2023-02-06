# -*- coding: utf-8 -*-

from operator import itemgetter
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.serializers.logs.statbox.getters import build_getter
from passport.backend.core.undefined import Undefined


class TestBuildGetter(TestCase):
    def setUp(self):
        self._model = {
            'foo': 'bar',
            'spam': None,
            'doh': Undefined,
        }

    def test_ok(self):
        get = build_getter(itemgetter('foo'))
        eq_(get(self._model), 'bar')

    def test_no_value(self):
        get = build_getter(itemgetter('foo'))
        ok_(get(None) is None)

        get = build_getter(itemgetter('spam'))
        ok_(get(self._model) is None)

        get = build_getter(itemgetter('doh'))
        ok_(get(self._model) is None)
