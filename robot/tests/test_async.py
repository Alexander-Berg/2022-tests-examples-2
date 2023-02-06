#!/usr/bin/env python

import unittest

import time
import logging

from concurrent.futures import ThreadPoolExecutor
from robot.library.yuppie.modules.asynchronous import Async


class TestAsync(unittest.TestCase):
    def test_async_main(self):
        class TestAsyncInternal(object):

            def __init__(self):
                self.param = 5

            def simplemethod(self, blah, blah2):
                logging.info("Going to sleep")
                time.sleep(0.1)
                self.param = 10
                return "foo"

            @classmethod
            def clmethod(cls, v):
                logging.info("Going to sleep clsm")
                time.sleep(0.1)
                return v

        inst = TestAsyncInternal()
        with ThreadPoolExecutor(5) as pool:
            out1 = Async(inst.simplemethod, 1, "a", pool=pool)
            Async(inst.simplemethod, 2, "b", pool=pool)
            Async(inst.simplemethod, 3, "c", pool=pool)
            Async(inst.simplemethod, 4, "d", pool=pool)
            out5 = Async(TestAsyncInternal.clmethod, 8, pool=pool)

        self.assertEqual(out1.result(), "foo")
        self.assertEqual(out5.result(), 8)
        self.assertEqual(inst.param, 10)


if __name__ == '__main__':
    unittest.main()
