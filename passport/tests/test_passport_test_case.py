# -*- coding: utf-8 -*-

from os.path import relpath

from nose.tools import eq_
from passport.backend.core.test.test_utils import PassportTestCase


class TestShortDescription(PassportTestCase):
    def test(self):
        eq_(
            self.shortDescription(),
            '%s:TestShortDescription.test' % relpath(__file__),
        )
