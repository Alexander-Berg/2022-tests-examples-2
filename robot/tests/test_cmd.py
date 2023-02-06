#!/usr/bin/env python
from __future__ import print_function
import unittest
import tempfile
from concurrent.futures import ThreadPoolExecutor
from robot.library.yuppie.modules.asynchronous import Async, FutureWrap
from robot.library.yuppie.modules.cmd import Cmd


class TestCmd(unittest.TestCase):
    def test_async(self):
        pool = ThreadPoolExecutor(max_workers=3)
        o = Async(Cmd, ["sleep", "0.1"], pool=pool)
        o1 = Async(Cmd, ["sleep", "0.1"], pool=pool)

        self.assertEqual(type(o), FutureWrap)
        self.assertEqual(type(o1), FutureWrap)

        o2 = Cmd(["sleep", "0.1"])

        p = o.result()
        p1 = o1.result()
        p2 = o2

        self.assertEqual(p.process().returncode, 0)
        self.assertEqual(p1.process().returncode, 0)
        self.assertEqual(p2.process().returncode, 0)

    def test_big_file(self):
        _, f = tempfile.mkstemp()
        data = 's' * 1024 * 1024 * 10
        with open(f, 'w') as outf:
            print(data, file=outf)

        res = Cmd(['cat', f], timeout=30).stdout()
        self.assertTrue(res == data + '\n')

    @classmethod
    def test_big_file_to_stderr(cls):
        _, f = tempfile.mkstemp()
        with open(f, 'w') as outf:
            print('s' * 1024 * 1024 * 10, file=outf)
        Cmd("bash -c 'cat {} 1>&2'".format(f), timeout=30)

    def test_stdout_and_stderr(self):
        _, fout = tempfile.mkstemp()
        _, ferr = tempfile.mkstemp()
        p = Cmd(['echo', '123123'], stdout=fout, stderr=ferr, timeout=20)
        self.assertEqual(p.process().returncode, 0)

if __name__ == '__main__':
    unittest.main()
