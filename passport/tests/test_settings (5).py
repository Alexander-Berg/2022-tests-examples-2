# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from mock import Mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.common.settings import Settings


TEST_SETTINGS1 = Mock(foo='foo value', bar='bar value')
TEST_OPTIONS1 = {'spam': 'spam value'}


class TestSettings(TestCase):
    def test_dir(self):
        settings = Settings()
        eq_(dir(settings), dir(None))

        settings.configure(TEST_SETTINGS1, **TEST_OPTIONS1)
        ok_('foo' in dir(settings))
        ok_('bar' in dir(settings))
        ok_('spam' in dir(settings))

    def test_getattr(self):
        settings = Settings()
        settings.configure(TEST_SETTINGS1, **TEST_OPTIONS1)

        for key, value in {'foo': 'foo value', 'bar': 'bar value', 'spam': 'spam value'}.items():
            eq_(getattr(settings, key), value)
