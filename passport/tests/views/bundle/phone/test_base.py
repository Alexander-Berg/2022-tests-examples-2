# -*- coding: utf-8 -*-

import unittest

from nose.tools import raises
from passport.backend.api.views.bundle.phone.base import BasePhoneBundleView


class BasePhoneBundleViewTestCase(unittest.TestCase):

    @raises(NotImplementedError)
    def test_process(self):
        BasePhoneBundleView().process()

    @raises(NotImplementedError)
    def test_internal_process(self):
        BasePhoneBundleView()._process()
