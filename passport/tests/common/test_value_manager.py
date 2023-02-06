# -*- coding: utf-8 -*-

from passport.backend.vault.api.errors import DecryptionError
from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.test_data import TEST_KEYS
from passport.backend.vault.api.value_manager import (
    ValueManager,
    ValueType,
)


class TestValueManager(BaseTestCase):
    def test_value_manager(self):
        value_manager = ValueManager(None, TEST_KEYS)
        index, algorithm, encoded_value = value_manager.encode('123')
        decoded_value = value_manager.decode(index, algorithm, encoded_value)
        self.assertEqual(decoded_value, '123')

    def test_compressed_aes(self):
        value_manager = ValueManager(None, TEST_KEYS)
        value = '123' * 1000
        index, algorithm, encoded_value = value_manager.encode(value)
        decoded_value = value_manager.decode(index, algorithm, encoded_value)
        self.assertEqual(decoded_value, value)
        self.assertEqual(algorithm, ValueType.COMPRESSED_AES)

    def test_exceptions(self):
        value_manager = ValueManager(None, TEST_KEYS)
        index, algorithm, encoded_value = value_manager.encode('123')
        with self.assertRaises(DecryptionError):
            value_manager.decode(index, algorithm, '123')
        with self.assertRaises(DecryptionError):
            value_manager.decode(index, algorithm, '1.1.1.1')
        with self.assertRaises(DecryptionError):
            value_manager.decode('201801', algorithm, encoded_value)
