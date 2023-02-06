# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.rfc_totp_secret import (
    RfcTotpSecretType,
    TOTP_SECRET_LENGTH,
)
import six


class TestRfcTotpSecretType(PassportTestCase):
    def test_generate(self):
        if six.PY2:
            random_secret = 'ffffffff'.decode('hex')
        else:
            random_secret = bytes.fromhex('ffffffff')
        urandom_mock = mock.Mock(return_value=random_secret)

        with mock.patch('os.urandom', urandom_mock):
            secret = RfcTotpSecretType.generate()

        urandom_mock.assert_called_once_with(TOTP_SECRET_LENGTH)
        eq_(secret.binary_secret, b'\xff\xff\xff\xff')
        eq_(secret.human_readable_secret, '777777Y')
        eq_(secret.serialized_secret, b'1://///w')
