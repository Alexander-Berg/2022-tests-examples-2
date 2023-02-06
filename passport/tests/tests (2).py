# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.library.packaging import format_commit


TEST_PACKAGE_NAME = 'package-name'


class TestPackagingUtils(unittest.TestCase):
    def test_format_commit(self):
        for message, expected_result in (
            ('Cool commit', 'Cool commit'),
            ('Cool commit\n\nFeature1\nFeature2', 'Cool commit\n    Feature1\n    Feature2'),
            ('Cool commit [mergeto:passport_api:25]', 'Cool commit'),
            ('Cool commit\n\nREVIEW:123', 'Cool commit'),
            ('release foo 0.0.1, %s 0.0.2' % TEST_PACKAGE_NAME, ''),
        ):
            eq_(
                format_commit(message=message, package_name=TEST_PACKAGE_NAME),
                expected_result,
            )
