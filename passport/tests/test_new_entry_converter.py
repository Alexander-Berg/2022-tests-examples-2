# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.historydb.converter import EntryConverter
from passport.backend.core.historydb.entry import LogEntry


class TestEntryConverter(unittest.TestCase):
    def setUp(self):
        self.converter = EntryConverter()

    def test_escape(self):
        value = 'play\n the\r game'
        eq_(self.converter.escape(value), 'play\\n the\\r game')

    def test_quote(self):
        value = r'Flash - Ah - Saviour` of the universe'
        quoted_value = self.converter.quote(value)
        eq_(quoted_value, r'`Flash - Ah - Saviour`` of the universe`')

        eq_(self.converter.quote('first last'), '`first last`')
        eq_(self.converter.quote('first`last'), '`first``last`')
        eq_(self.converter.quote('firstlast'), 'firstlast')
        eq_(self.converter.quote('-'), '`-`')

    def test_nullify(self):
        eq_(self.converter.nullify(''), '-')
        eq_(self.converter.nullify(None), '-')

    def test_escape_quote(self):
        # first`\rlast -> `first``\\rlast`

        value = "Flash\n - Ah -\rHe`ll save every one of us"
        self.converter.escape_fields = set(['fake'])
        self.converter.quote_fields = set(['fake'])
        prepared_value = self.converter.convert_field('fake', value)
        eq_(prepared_value, "`Flash\\n - Ah -\\rHe``ll save every one of us`")

        value = "first`\rlast"
        prepared_value = self.converter.convert_field('fake', value)
        eq_(prepared_value, "`first``\\rlast`")

    def test_datetime_field(self):
        # YYYY-MM-DDTHH:MM:SS.mmmmmm
        self.converter.datetime_fields = set(['dt_field'])
        dt = datetime.now()
        eq_(self.converter.convert_field('dt_field', dt),
            dt.strftime("%Y-%m-%dT%H:%M:%S.%f+03"))

        with assert_raises(AttributeError):
            self.converter.convert_field('dt_field', 'fake')

    def test_convert(self):
        entry = LogEntry()
        eq_('', self.converter.convert(entry))
        ok_(self.converter.convert(entry).startswith(''))

    def test_prepare_value(self):
        eq_('value', self.converter.convert_field('fake', 'value'))

        self.converter.datetime_fields = set(['dt_field'])

        self.converter.convert_field('dt_field', datetime(2012, 3, 1))

    def test_replace(self):
        old = 'vasya pupkin'
        new = self.converter.replace(['ya', 'pu'], ['ily', 'Pu'], old)
        eq_(new, 'vasily Pupkin')
