#!/usr/bin/env python

import unittest
from robot.jupiter.library.python.jupiter_util import macro_replacement


class TestMacro(unittest.TestCase):
    def test_macro(self):
        src = "{{k1}} {{k2}}\n{{k3}}\n{{k1}}"
        res = macro_replacement(src, k1=1, k2=2, k3=3)

        self.assertEqual(res, "1 2\n3\n1")


if __name__ == '__main__':
    unittest.main()
