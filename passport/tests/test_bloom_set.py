# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    assert_raises,
    ok_,
)
from passport.backend.core.bloom_set import BaseBloomSet
import yatest.common as yc


class TestBloomSet(TestCase):
    def setUp(self):
        self.bloom = BaseBloomSet(
            filename=yc.source_path('passport/backend/core/bloom_set/tests/example_file.txt'),
            max_error=10 ** -8,
        )

    def test_load(self):
        ok_(self.bloom.config is None)
        self.bloom.load()
        ok_(self.bloom.config is not None)

    def test_has_item(self):
        self.bloom.load()

        ok_(self.bloom.has_item('item1'))
        ok_('item2' in self.bloom)
        ok_('item3' not in self.bloom)

    def test_not_loaded_error(self):
        with assert_raises(RuntimeError):
            self.bloom.has_item('item1')
