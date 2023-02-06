# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.cache.backend.locmem import LocalMemoryCache


class TestLocalMemoryCache(unittest.TestCase):
    def test_make_key(self):
        c = LocalMemoryCache()
        assert c.make_key('key') == 'key'

    def test_validate_key(self):
        c = LocalMemoryCache()
        assert c.validate_key('key')

    def test_set_get(self):
        c = LocalMemoryCache()
        c.set('key', 'value')
        assert c.get('key') == 'value'
        assert len(c._cache) == 1
        assert len(c._expire_info) == 1

    def test_delete(self):
        c = LocalMemoryCache()
        c.set('key', 'value')
        c.delete('key')
        assert len(c._cache) == 0
        assert len(c._expire_info) == 0

    def test_has_key(self):
        c = LocalMemoryCache()
        c.set('key', 'value')
        assert c.has_key('key')  # noqa

    def test_clear(self):
        c = LocalMemoryCache()
        for x in range(10):
            c.set('key%s' % x, 'value')
        assert len(c._cache) == 10
        assert len(c._expire_info) == 10
        c.clear()
        assert len(c._cache) == 0
        assert len(c._expire_info) == 0

    def test_ttl(self):
        c = LocalMemoryCache(ttl=0)
        c.set('key', 'value')
        assert c.get('key') is None
        assert len(c._cache) == 0
        assert len(c._expire_info) == 0

    def test_max_entries(self):
        c = LocalMemoryCache(max_entries=10)
        for x in range(100):
            c.set('key%s' % x, 'value')
        assert len(c._cache) == 10
        assert len(c._expire_info) == 10

    def test_cull_frequency_zero(self):
        c = LocalMemoryCache(cull_frequency=0, max_entries=10)
        for x in range(11):
            c.set('key%s' % x, 'value')
        assert len(c._cache) == 1
        assert len(c._expire_info) == 1

    def test_cull_frequency(self):
        c = LocalMemoryCache(cull_frequency=2, max_entries=10)
        for x in range(11):
            c.set('key%s' % x, 'value')
        assert len(c._cache) == 6
        assert len(c._expire_info) == 6
