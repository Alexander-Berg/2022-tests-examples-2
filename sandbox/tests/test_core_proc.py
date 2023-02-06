#!/usr/bin/env python
# coding: utf-8

import os
import sys
import unittest
import yatest.common as tc

from sandbox.sdk2.helpers import coredump_filter

_GDB_STACKS = [
    "stack1",
    "stack2_1",
    "stack2_2",
]

_LLDB_STACKS = [
    "stack3_1",
    "stack3_2",

    "stack4_1",
    "stack4_2",
]

_SDC_ASSERT_STACKS = [
    "stack5_1",
    "stack5_2",
]


def _write_file(file_name, contents):
    with open(file_name, "w") as f:
        f.write(contents)


class TestStack(unittest.TestCase):

    def setUp(self):
        self.data_dir = tc.source_path('sandbox/sdk2/helpers/coredump_filter/tests/data')

        source_root = coredump_filter.SourceRoot()
        self.stacks = {}

        for current_stacks in [_GDB_STACKS, _LLDB_STACKS, _SDC_ASSERT_STACKS]:
            for test_name in current_stacks:
                self.stacks[test_name] = coredump_filter.GDBStack(
                    lines=self._read_lines(test_name),
                    source_root=source_root,
                    stream=sys.stdout,
                )
                self.stacks[test_name].parse()

        self.maxDiff = None

    def test_count_frames_in_stack(self):
        self.assertEqual(len(self.stacks["stack1"].frames), 65, "Invalid frame count")

    def test_cropped_source(self):
        source = self.stacks["stack1"].frames[10].cropped_source()
        self.assertEqual(source, "$S/search/cache/reqcacher.cpp", "Invalid cropped source")

    def test_gdb_fingerprints(self):
        # See CORES-179
        fp1 = self.stacks["stack2_1"].fingerprint()
        fp2 = self.stacks["stack2_2"].fingerprint()
        self.assertEqual(fp1, fp2)

    def test_lldb_fingerprints(self):
        # See CORES-180
        # CORES-180 description
        # Case 3: CORES-180 description
        # Case 4: https://st.yandex-team.ru/CORES-180#62068f85fe8cf974a1ab8423
        for n in ["3", "4"]:
            fp1 = self.stacks["stack{}_1".format(n)].fingerprint()
            fp2 = self.stacks["stack{}_2".format(n)].fingerprint()
            # _write_file("/tmp/x1", fp1)
            # _write_file("/tmp/x2", fp2)
            self.assertEqual(fp1, fp2)

    def test_sdcassert_fingerprints(self):
        fp1 = self.stacks["stack5_1"].fingerprint()
        fp2 = self.stacks["stack5_2"].fingerprint()
        self.assertEqual(fp1, fp2)

    def _read_lines(self, test_name):
        stack_lines = []
        with open(os.path.join(self.data_dir, "{}.txt".format(test_name))) as f:
            stack_lines = f.readlines()
        return stack_lines
