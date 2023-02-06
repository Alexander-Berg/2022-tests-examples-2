#!/usr/bin/env python
# coding: utf-8

import unittest
import tempfile
import shutil
from morda.lock import FileLock, LOCK_EXCEPTION


class TestFileLock(unittest.TestCase):

    def test_resource_unavailable(self):
        run_dir = tempfile.mkdtemp()
        lockname = 'TestFileLock'
        with FileLock(lockname, run_dir):
            with self.assertRaises(LOCK_EXCEPTION) as cm:
                with FileLock(lockname, run_dir):
                    pass
        the_exception = cm.exception
        self.assertEqual(the_exception.errno, 11)
        shutil.rmtree(run_dir)
