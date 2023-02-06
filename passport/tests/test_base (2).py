# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.cache.backend.base import BaseCache


class TestBaseCache(unittest.TestCase):
    def setUp(self):
        self.c = BaseCache()

    def test_make_key(self):
        self.assertRaises(NotImplementedError, self.c.make_key, 'key')

    def test_validate_key(self):
        self.assertRaises(NotImplementedError, self.c.validate_key, 'key')

    def test_get(self):
        self.assertRaises(NotImplementedError, self.c.get, 'key')

    def test_set(self):
        self.assertRaises(NotImplementedError, self.c.set, 'key', 'value')

    def test_delete(self):
        self.assertRaises(NotImplementedError, self.c.delete, 'key')

    def test_has_key(self):
        # Здесь есть проблема с тем, что flake8 автоматом считает
        # .has_key() как deprecated-метод dict'a из-за коллизии
        # имен в проверке. Поэтому пометим эту строчку как исключение :)
        self.assertRaises(NotImplementedError, self.c.has_key, 'key')  # noqa

    def test_clear(self):
        self.assertRaises(NotImplementedError, self.c.clear)
