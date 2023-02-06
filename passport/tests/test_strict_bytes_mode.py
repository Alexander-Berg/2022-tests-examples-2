# -*- coding: utf-8 -*-
import os
import unittest

from nose.tools import assert_raises
import six


class TestStrictBytesMode(unittest.TestCase):
    """
    Проверяем, что выставление переменной окружения Y_PYTHON_BYTES_WARNING=2 эквивалентно ключу -bb неаркадийного питона
    """
    def setUp(self):
        assert os.environ['Y_PYTHON_BYTES_WARNING'] == '2'  # значение выставляется в ya.make

    def test_compare_error(self):
        if not six.PY3:
            return

        with assert_raises(BytesWarning):
            b'1' == '1'

    def test_convert_error(self):
        if not six.PY3:
            return

        with assert_raises(BytesWarning):
            str(b'1')
