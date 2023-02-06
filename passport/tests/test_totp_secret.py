# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.totp_secret import TotpSecret
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.totp_secret import TotpSecretType
from passport.backend.core.undefined import Undefined


class TestTotpSecret(unittest.TestCase):
    def test_set_secret(self):
        secret = TotpSecret()
        secret.set(TotpSecretType('secret'))
        ok_(secret.totp_secret is not None)
        eq_(secret.totp_secret.encrypted_pin_and_secret, 'secret')
        eq_(secret.update_datetime, DatetimeNow())


class TestTotpSecretParse(unittest.TestCase):
    def test_secret_is_set(self):
        acc = Account().parse({
            'login': 'test',
            '2fa_on': '1',
        })
        ok_(acc.totp_secret.is_set)

    def test_secret_is_not_set(self):
        acc = Account().parse({
            'login': 'test',
        })
        ok_(not acc.totp_secret.is_set)

    def test_failed_pin_checks_count(self):
        acc = Account().parse({
            'login': 'test',
            'totp.failed_pin_checks_count': 12,
        })
        eq_(acc.totp_secret.failed_pin_checks_count, 12)

    def test_undefined_update_datetime(self):
        acc = Account().parse({'login': 'test'})
        eq_(acc.totp_secret.update_datetime, Undefined)

        acc = Account().parse({'login': 'test', 'totp.update_datetime': ''})
        eq_(acc.totp_secret.update_datetime, Undefined)

    def test_update_datetime(self):
        ts = 12345678
        acc = Account().parse({'login': 'test', 'totp.update_datetime': str(ts)})
        eq_(acc.totp_secret.update_datetime, datetime.fromtimestamp(ts))

    def test_undefined_totp_secret_ids(self):
        acc = Account().parse({'login': 'test'})
        ok_(acc.totp_secret.secret_ids is Undefined)

    def test_secret_ids(self):
        acc = Account().parse({'login': 'test', 'totp.secret_ids': '0:0,1:100'})
        eq_(
            acc.totp_secret.secret_ids,
            {
                0: datetime.fromtimestamp(0),
                1: datetime.fromtimestamp(100),
            },
        )

    def test_device_ids(self):
        acc = Account().parse({'login': 'test', 'account.totp.yakey_device_ids': 'd1,d2'})
        eq_(
            acc.totp_secret.yakey_device_ids,
            ['d1', 'd2'],
        )

    def test_pin_length(self):
        acc = Account().parse({'login': 'test', 'totp.pin_length': 15})
        eq_(acc.totp_secret.pin_length, 15)
