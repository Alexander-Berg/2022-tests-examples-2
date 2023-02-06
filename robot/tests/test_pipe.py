#!/usr/bin/env python

import unittest
from robot.library.yuppie.modules.cmd import CmdPipe, PipeEnd


class TestPipe(unittest.TestCase):
    def test_pipe(self):
        p = CmdPipe(["echo", "123", "345"]) | CmdPipe(["awk", "{{print $1}}"]) | PipeEnd()
        self.assertEqual(p.stdout().strip(), "123")


if __name__ == '__main__':
    unittest.main()
