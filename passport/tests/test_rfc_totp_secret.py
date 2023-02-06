# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.rfc_totp_secret import RfcTotpSecret
from passport.backend.core.types.rfc_totp_secret import RfcTotpSecretType


class TestRfcTotpSecret(unittest.TestCase):
    def test_set_secret(self):
        secret = RfcTotpSecret()
        secret.set(RfcTotpSecretType('secret'))
        eq_(secret.totp_secret.binary_secret, 'secret')
        ok_(secret.is_set)


class TestRfcTotpSecretParse(unittest.TestCase):
    def test_secret_is_set(self):
        acc = Account().parse({
            'login': 'test',
            'account.rfc_2fa_on': '1',
        })
        ok_(acc.rfc_totp_secret.is_set)

    def test_secret_is_not_set(self):
        acc = Account().parse({
            'login': 'test',
        })
        ok_(not acc.rfc_totp_secret.is_set)
