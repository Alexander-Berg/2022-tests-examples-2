#!/usr/bin/env python

import unittest
from robot.library.yuppie.modules.apply_cmd import ApplyCmd


class TestApply(unittest.TestCase):
    @classmethod
    def test_apply(cls):
        command = "{sleep_cmd} {how_much}"

        args = {"sleep_cmd": "sleep", "how_much": [0.05]*10}

        ApplyCmd(command, args=args, jobs=5, tick=0.01)

if __name__ == '__main__':
    unittest.main()
