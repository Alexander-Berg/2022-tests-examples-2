# -*- coding: utf-8 -*-

from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.core import validators
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.validators import DriveDeviceIdValidator


DEVICE_ID1 = '0123456789abcdefABCDEF0123456789'


class TestDriveDeviceIdValidator(PassportTestCase):
    @parameterized.expand(
        [
            (DEVICE_ID1, DEVICE_ID1),
            ('f' * 32, 'f' * 32),
            ('F' * 32, 'F' * 32),
            (' a ', 'a'),
            ('  ' + DEVICE_ID1 + '  ', DEVICE_ID1),
        ],
    )
    def test_valid(self, _in, out):
        eq_(DriveDeviceIdValidator().to_python(_in), out)

    @parameterized.expand(
        [
            (None,),
            ('',),
            ('0' * 33,),
        ],
    )
    def test_invalid(self, _in):
        with assert_raises(validators.Invalid):
            DriveDeviceIdValidator().to_python(_in)
