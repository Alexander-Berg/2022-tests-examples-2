# -*- coding: utf-8 -*-
import os
import unittest

from passport.backend.utils.warnings import enable_strict_bytes_mode


class TestEnableStrictBytesModeFunction(unittest.TestCase):
    def setUp(self):
        # Сбросим значение переменной, выставленное в ya.make
        os.environ['Y_PYTHON_BYTES_WARNING'] = '0'

    def test_env(self):
        enable_strict_bytes_mode()
        assert os.environ['Y_PYTHON_BYTES_WARNING'] == '2'
