# -*- coding: utf-8 -*-

import unittest

from passport.backend.core.types.account.account import uid_to_kpid


class TestUidToKpId(unittest.TestCase):
    def test_max(self):
        assert uid_to_kpid(1119999999999999) == 9999999999999

    def test_min(self):
        assert uid_to_kpid(1110000000000000) == 0

    def test_ok(self):
        assert uid_to_kpid(1110000012675389) == 12675389

    def test_too_large(self):
        self.assertRaises(ValueError, uid_to_kpid, 1120000000000000)

    def test_too_small(self):
        self.assertRaises(ValueError, uid_to_kpid, 1109999999999999)
