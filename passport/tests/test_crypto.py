# -*- coding: utf-8 -*-

import re
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.crypto.faker import FakeKeyStorage
from passport.backend.core.crypto.utils import DecryptionError
from passport.backend.core.historydb.crypto import (
    _key_storage,
    decrypt,
    encrypt,
)


TEST_UNICODE_VALUE = u'значение'

TEST_BYTE_VALUE = TEST_UNICODE_VALUE.encode('utf-8')[:-1] + b'tail'  # invalid continuation byte


class CryptoTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_key_storage = FakeKeyStorage(1, b'1' * 24)
        self.fake_key_storage.start()

    def tearDown(self):
        self.fake_key_storage.stop()

    def test_encrypt(self):
        encrypted = encrypt(TEST_UNICODE_VALUE)

        eq_(encrypted.count(b':'), 3)
        _, _, assoc_data, _ = encrypted.split(b':')
        eq_(
            assoc_data,
            b'key_number=%d' % _key_storage._get_key_number(),
        )

    def test_encrypt_unicode_string_decrypt_ok(self):
        encrypted = encrypt(TEST_UNICODE_VALUE)

        value = decrypt(encrypted)

        eq_(value.decode('utf-8'), TEST_UNICODE_VALUE)

    def test_encrypt_byte_string_decrypt_ok(self):
        encrypted = encrypt(TEST_BYTE_VALUE)

        value = decrypt(encrypted)

        eq_(value, TEST_BYTE_VALUE)

    @raises(DecryptionError)
    def test_decrypt_errors(self):
        test_encrypted_value = encrypt(TEST_UNICODE_VALUE)
        for encrypted in (
            b'::',
            b'1:2:3:4',
            test_encrypted_value.replace(b'key_number=', b'bla'),
            test_encrypted_value.replace(b'key_number=', b'key_number=b'),
            test_encrypted_value.replace(b'key_number=', b'key_number=9999999999999999999'),
            re.sub(b'key_number=\d+', b'key_number=684', test_encrypted_value),
        ):
            decrypt(encrypted)
