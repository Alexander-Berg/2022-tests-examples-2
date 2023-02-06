# -*- coding: utf-8 -*-

from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.api.views.bundle.device_public_key.forms import PublicKeyValidator
from passport.backend.core import validators
from passport.backend.core.test.test_utils.utils import PassportTestCase


class TestPublicKeyValidator(PassportTestCase):
    @parameterized.expand(
        [
            ('0', '0',),
            ('z!1', 'z!1',),
            ('0' * 60000, '0' * 60000),
            ('  000  ', '000'),
        ],
    )
    def test_valid(self, _in, out):
        eq_(PublicKeyValidator().to_python(_in), out)

    @parameterized.expand(
        [
            (None,),
            ('',),
            ('a\0b',),
            ('0' * 60001,),
        ],
    )
    def test_invalid(self, _in):
        with assert_raises(validators.Invalid):
            PublicKeyValidator().to_python(_in)
