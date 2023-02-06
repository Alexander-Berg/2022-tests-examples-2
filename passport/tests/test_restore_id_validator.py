# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.types.restore_id import RestoreId
from passport.backend.core.validators import (
    Invalid,
    RestoreIdValidator,
)


class RestoreIdValidatorTestCase(TestCase):

    def setUp(self):
        self.v = RestoreIdValidator()

    def test_invalid(self):
        with assert_raises(Invalid):
            self.v.to_python('restore_id')

    def test_not_a_string(self):
        with assert_raises(Invalid):
            self.v.to_python(23)

    def test_empty(self):
        with assert_raises(Invalid):
            self.v.to_python('')

    def test_invalid_uid(self):
        with assert_raises(Invalid):
            self.v.to_python('host_id,pid,timestamp,uid,track_id')

    def test_valid(self):
        eq_(RestoreId.from_string('1,2,3,4,5'), self.v.to_python('1,2,3,4,5'))
