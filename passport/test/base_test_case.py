# coding: utf-8

import unittest

from passport.backend.vault.api.test.arcadia_mock import ArcadiaMock


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.arcadia_mock = ArcadiaMock()
        self.arcadia_mock.start()

    def tearDown(self):
        self.arcadia_mock.stop()
