#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import tempfile
import unittest
import yatest.common

from concurrent.futures import ThreadPoolExecutor
from library.python.testing.deprecated import setup_environment
from robot.library.yuppie.modules.cm import Cm


class TestCm(unittest.TestCase):
    CM_POOL = ThreadPoolExecutor(max_workers=3)

    def setUp(self):
        setup_environment.setup_bin_dir()
        self.wd = tempfile.mkdtemp()
        self.test_file = os.path.join(self.wd, 'test_file')
        cm_sh = os.path.join(self.wd, 'cm.sh')
        with open(cm_sh, 'w') as outf:
            print("""
                _scenario() {{
                    MAIN = localhost
                    MAIN good_target:
                }}

                target_good_target() {{
                    echo done > {test_file}
                }}

                target_$1
            """.format(test_file=self.test_file), file=outf)
        self.cm = Cm.up(
            bin_dir=yatest.common.binary_path('bin'),
            cm_sh=cm_sh,
            generate_hostlist=True,
            pool=TestCm.CM_POOL,
            working_dir=self.wd,
        )

    def tearDown(self):
        self.cm.down()
        TestCm.CM_POOL.shutdown()

    def test_check_call_target(self):
        self.cm.check_call_target('good_target')
        with open(self.test_file) as inf:
            self.assertEqual(inf.read(), "done\n")


if __name__ == '__main__':
    unittest.main()
