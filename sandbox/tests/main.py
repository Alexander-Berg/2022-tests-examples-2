#!/usr/bin/env python

"""
    base_search_quality unit-tests.
"""

import sys
import unittest

from optparse import OptionParser


parser = OptionParser()
parser.add_option("-y", "--sandbox_dir", dest="sandbox_dir")
parser.add_option("-p", "--tasks_dir", dest="tasks_dir")
parser.add_option("-t", "--temp_dir", dest="temp_dir")

options, args = parser.parse_args()

sys.path.append(options.sandbox_dir)
sys.path.append(options.tasks_dir)

# from base_search_quality_tests import init_tests

# init_tests(options.temp_dir)

if __name__ == "__main__":
    del sys.argv[1:]  # hack
    unittest.main()
