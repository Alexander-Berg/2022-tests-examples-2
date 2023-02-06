#!/usr/bin/env python
# coding: utf-8

import unittest
from morda.singleton import Singleton


class SingletonTest(Singleton):

    def __init__(self):
        self.x = id(self)


class TestSingleton(unittest.TestCase):

    def test_same_object(self):
        a = SingletonTest()
        b = SingletonTest()
        self.assertEqual(id(a), id(b))
        self.assertEqual(a.x, b.x)

    def test_isinstance(self):
        a = SingletonTest()
        isinstance(a, Singleton)
