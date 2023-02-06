# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.common.misc import (
    ApplicationMapper,
    rebuild_scope_string,
    split_scope_string,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_NAME1,
    APPLICATION_NAME2,
)


_PROVIDER_CODE1 = 'pc1'

_APPLICATION1 = Mock()
_APPLICATION1.engine_id = APPLICATION_NAME1

_APPLICATION2 = Mock()
_APPLICATION2.engine_id = APPLICATION_NAME2


class TestMisc(TestCase):
    def test_split_scope_string(self):
        eq_(split_scope_string('a,b,c'), ['a', 'b', 'c'])
        eq_(split_scope_string('a b c'), ['a', 'b', 'c'])
        eq_(split_scope_string('a,b c'), ['a', 'b', 'c'])
        eq_(split_scope_string(',  a b,  c ,, '), ['a', 'b', 'c'])

    def test_rebuild_scope_string(self):
        eq_(rebuild_scope_string(', a,b  c,,,  d', ','), 'a,b,c,d')
        eq_(rebuild_scope_string(None, ' '), '')
        eq_(rebuild_scope_string('   ,,,  ', ' '), '')


class TestApplicationMapper(TestCase):
    def setUp(self):
        self._mapper = ApplicationMapper()

    def test_empty(self):
        with self.assertRaises(KeyError):
            self._mapper.map_application(_PROVIDER_CODE1, _APPLICATION1)

        ok_(not self._mapper.has_provider(_PROVIDER_CODE1))

    def test_default(self):
        self._mapper.add_mapping(_PROVIDER_CODE1, _APPLICATION1)

        val = self._mapper.map_application(_PROVIDER_CODE1, _APPLICATION1)

        ok_(val is _APPLICATION1)
        ok_(self._mapper.has_provider(_PROVIDER_CODE1))

    def test_custom_mapping(self):
        self._mapper.add_mapping(
            _PROVIDER_CODE1,
            _APPLICATION1,
            mapping={APPLICATION_NAME2: _APPLICATION2},
        )

        val1 = self._mapper.map_application(_PROVIDER_CODE1, _APPLICATION1)
        val2 = self._mapper.map_application(_PROVIDER_CODE1, _APPLICATION2)

        ok_(val1 is _APPLICATION1)
        ok_(val2 is _APPLICATION2)
        ok_(self._mapper.has_provider(_PROVIDER_CODE1))

    def test_getitem(self):
        map_application = Mock(name='map_application')
        with patch.object(self._mapper, 'map_application', map_application):
            retval = self._mapper[(_PROVIDER_CODE1, _APPLICATION1)]

        map_application.assert_called_with(_PROVIDER_CODE1, _APPLICATION1)
        ok_(retval is map_application.return_value)
