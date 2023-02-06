# -*- coding: utf-8 -*-
import unittest

from nose.tools import raises
from passport.backend.core.serializers.runner import BaseSerializeActionRunner


class TestBaseActionRunner(unittest.TestCase):
    @raises(NotImplementedError)
    def test_serialize(self):
        BaseSerializeActionRunner().serialize(None, None)

    @raises(NotImplementedError)
    def test_invalid_execute(self):
        BaseSerializeActionRunner().execute()
