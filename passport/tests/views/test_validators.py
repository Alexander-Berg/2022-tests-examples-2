# coding: utf-8

from collections import namedtuple
import unittest

from passport.backend.vault.api.views.validators import GreatOrEqualZeroInt
from wtforms import validators as wtf_validators


class TestValidators(unittest.TestCase):
    def test_great_or_equal_zero_int_validator(self):
        validator = GreatOrEqualZeroInt()
        field_type = namedtuple('FieldType', 'data')

        bad_values = ['', '  ', '-1', '-500', 'test']
        for v in bad_values:
            with self.assertRaises(wtf_validators.ValidationError):
                validator(None, field_type(v))

        good_values = ['0', '100', '1000000000']
        for v in good_values:
            self.assertIsNone(validator(None, field_type(v)))
