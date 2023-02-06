import unittest

import numpy as np
from passport.backend.library.yalearn.structures import UInt64StlSet


class TestStlSet(unittest.TestCase):
    def test_add(self):
        stl_set = UInt64StlSet()
        stl_set.add(1)
        stl_set.add(2)
        stl_set.add(3)
        self.assertTrue(stl_set.has(1))
        self.assertTrue(stl_set.has(2))
        self.assertTrue(stl_set.has(3))

    def test_file(self):
        np.array([123, 456, 789]).astype(np.uint64).tofile('tfile.bin')
        stl_set = UInt64StlSet('tfile.bin')
        self.assertTrue(stl_set.has(123))
        self.assertTrue(stl_set.has(456))
        self.assertTrue(stl_set.has(789))
        self.assertFalse(stl_set.has(10))
