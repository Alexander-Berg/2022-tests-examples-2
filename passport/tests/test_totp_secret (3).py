# -*- coding: utf-8 -*-
import base64
import random
import unittest

import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.totp_secret import (
    APP_SECRET_LENGTH,
    get_zero_padded_pin,
    InvalidPinError,
    MAX_DEFAULT_PIN,
    parse_pin_as_string,
    TotpSecretType,
)
from passport.backend.core.utils.crc import bytes_to_long
import six


class TestFunctions(PassportTestCase):
    @raises(InvalidPinError)
    def test_parse_pin_negative_error(self):
        parse_pin_as_string(-1)

    @raises(InvalidPinError)
    def test_parse_pin_extra_symbols_error(self):
        parse_pin_as_string('+1')

    @raises(InvalidPinError)
    def test_parse_pin_too_big(self):
        parse_pin_as_string(10 ** 17)

    def test_parse_pin(self):
        eq_(parse_pin_as_string(9999), '9999')
        eq_(parse_pin_as_string('123'), '123')
        eq_(parse_pin_as_string('0001'), '0001')

    def test_get_zero_padded_pin_invalid_pin(self):
        with assert_raises(ValueError):
            get_zero_padded_pin(10 ** 17)
        with assert_raises(ValueError):
            get_zero_padded_pin(10001, length=4)

    def test_get_zero_padded_pin_ok(self):
        eq_(get_zero_padded_pin(11, length=4), '0011')
        eq_(get_zero_padded_pin(1145, length=4), '1145')
        eq_(get_zero_padded_pin(1145), '0' * 12 + '1145')


class TestTotpSecretType(unittest.TestCase):

    def test_create_from_encrypted(self):
        secret = TotpSecretType('encrypted-pin-and-secret')
        eq_(secret.encrypted_pin_and_secret, 'encrypted-pin-and-secret')
        assert_is_none(secret.app_secret)
        assert_is_none(secret.pin)

    def test_create_from_raw(self):
        secret = TotpSecretType(app_secret='secret', pin='pin')
        assert_is_none(secret.encrypted_pin_and_secret)
        eq_(secret.app_secret, 'secret')
        eq_(secret.pin, 'pin')

    @raises(ValueError)
    def test_create_invalid_args(self):
        TotpSecretType()

    def test_generate(self):
        if six.PY2:
            random_secret = 'ffffffff'.decode('hex')
        else:
            random_secret = bytes.fromhex('ffffffff')
        random_pin = 42
        urandom_mock = mock.Mock(return_value=random_secret)
        system_random_mock = mock.Mock(return_value=random_pin)
        with mock.patch('os.urandom', urandom_mock):
            with mock.patch.object(random.SystemRandom, 'uniform', system_random_mock):
                secret = TotpSecretType.generate()
                urandom_mock.assert_called_once_with(APP_SECRET_LENGTH)
                system_random_mock.assert_called_once_with(0, MAX_DEFAULT_PIN)
                assert_is_none(secret.encrypted_pin_and_secret)
                eq_(secret.pin, '0042')
                eq_(secret.app_secret, b'\xff\xff\xff\xff')
                eq_(secret.human_readable_app_secret, '777777Y')
                eq_(
                    base64.urlsafe_b64decode(
                        secret.base64_secret.encode() + b'=' * (4 - len(secret.base64_secret) % 4),
                    ),
                    random_secret,
                )

    @raises(ValueError)
    def test_build_app_secret_too_long_error(self):
        """
        Пытаемся сделать секрет, передав более длинный усеченный секрет
        """
        bad_app_secret = base64.b32encode(b'a' * (APP_SECRET_LENGTH + 1)).rstrip(b'=')
        TotpSecretType.build(bad_app_secret, 123)

    def test_correct_build_with_padding(self):
        """
        Проверим, что мы корректно строим секрет и восстанавливаем паддинг
        """
        app_secret_unpadded = 'AAAND6G4J2HJLNDGMVOYXBYXD4'
        pin = '7315'
        secret = TotpSecretType.build(app_secret_unpadded, pin)
        eq_(secret.app_secret, base64.b32decode(app_secret_unpadded + '======'))
        eq_(secret.pin, pin)

    def test_correct_rebuild(self):
        """
        Проверим, что корректно работает преобразование:
        генерация секрета и восстановление того же секрета из усеченного и пина
        """
        secret = TotpSecretType.generate()
        new_secret = TotpSecretType.build(secret.human_readable_app_secret, secret.pin)
        eq_(new_secret.app_secret, secret.app_secret)
        eq_(new_secret.pin, secret.pin)

    def test_eq_ne(self):
        secret1 = TotpSecretType('secret')
        secret2 = TotpSecretType('secret')

        ok_(secret1 == secret2)
        ok_(not secret1 == '1234')
        ok_(not secret1 == TotpSecretType('secret2'))
        ok_(not secret1 != secret2)

    def test_build_container_for_yakey(self):
        app_secret = base64.b32encode(b'\xff' * 16)
        pin = 7315
        secret = TotpSecretType.build(app_secret, pin)
        container = secret.build_container_for_yakey(uid=42)

        message_bytes = bytes_to_long(base64.b32decode(container.encode() + b'=' * (-len(container) % 8)))
        eq_(
            (message_bytes >> 12) % (2 ** 4),
            3,  # длина пина минус 1
        )
        eq_(
            (message_bytes >> (12 + 4)) % (2 ** 64),
            42,  # uid
        )
        eq_(
            (message_bytes >> (12 + 4 + 64)) % (2 ** 128),
            2 ** 128 - 1,  # secret
        )
