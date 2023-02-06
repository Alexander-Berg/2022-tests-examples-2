# -*- coding: utf-8 -*-
from unittest import TestCase

from nose_parameterized import parameterized
from passport.backend.core.utils.version import is_version_left_gte_right


class VersionComparisonTestCase(TestCase):
    @parameterized.expand(
        [
            # перечислять в порядке левое >= правое
            ('1.0.0', ''),
            ('5.22.1', '5.22'),
            ('5.22.1', '5.22(12345)'),
            ('7.5.1(705010244)', '7.0.0'),
            ('6.0', '5.22.1'),
        ],
    )
    def test_left_as_new_as_right(self, left, right):
        assert is_version_left_gte_right(left, right)
        assert not is_version_left_gte_right(right, left)

    @parameterized.expand(
        [
            ('7.5.1(705010244)', '7.5.1(9999999999999)'),
        ]
    )
    def test_left_as_new_as_right__equal(self, left, right):
        assert is_version_left_gte_right(left, right)
        assert is_version_left_gte_right(right, left)
