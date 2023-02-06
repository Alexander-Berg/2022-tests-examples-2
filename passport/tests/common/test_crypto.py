# -*- coding: utf-8 -*-
from cryptography.exceptions import InvalidTag
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.common.crypto import (
    decrypt,
    decrypt_aes_gcm,
    DecryptFailedError,
    encrypt,
    encrypt_aes_gcm,
    UnsupportedVersionError,
)
from passport.backend.oauth.core.common.utils import int_to_bytes
from passport.backend.oauth.core.test.framework import BaseTestCase


TEST_MESSAGE = b'Very important message'
TEST_UNICODE_MESSAGE = 'Очень важное сообщение'
TEST_KEY = b'1' * 16
TEST_KEYS = {
    1: TEST_KEY,
}


class TestCryptoLowLevel(BaseTestCase):
    def test_encrypt_decrypt(self):
        iv, encrypted, tag = encrypt_aes_gcm(TEST_KEY, TEST_MESSAGE)
        decrypted = decrypt_aes_gcm(TEST_KEY, iv, encrypted, tag)
        eq_(decrypted, TEST_MESSAGE)

    @raises(ValueError)
    def test_bad_ecryption_key_length(self):
        encrypt_aes_gcm('1' * 15, TEST_MESSAGE)

    @raises(InvalidTag)
    def test_decrypt_failed_bad_key(self):
        iv, encrypted, tag = encrypt_aes_gcm(TEST_KEY, TEST_MESSAGE)
        decrypt_aes_gcm(b'*' + TEST_KEY[1:], iv, encrypted, tag)

    @raises(InvalidTag)
    def test_decrypt_failed_bad_iv(self):
        iv, encrypted, tag = encrypt_aes_gcm(TEST_KEY, TEST_MESSAGE)
        decrypt_aes_gcm(TEST_KEY, iv[1:], encrypted, tag)

    @raises(InvalidTag)
    def test_decrypt_failed_bad_message(self):
        iv, encrypted, tag = encrypt_aes_gcm(TEST_KEY, TEST_MESSAGE)
        decrypt_aes_gcm(TEST_KEY, iv, encrypted[1:], tag)

    @raises(InvalidTag)
    def test_decrypt_failed_bad_tag(self):
        iv, encrypted, tag = encrypt_aes_gcm(TEST_KEY, TEST_MESSAGE)
        # xor-им первый байт tag с единицей, чтобы гарантированно изменить в нём один бит
        bad_tag = int_to_bytes(tag[0] ^ 1, byte_count=1) + tag[1:]
        ok_(bad_tag != tag)
        decrypt_aes_gcm(TEST_KEY, iv, encrypted, bad_tag)


class TestCryptoHighLevel(BaseTestCase):
    def test_encrypt_decrypt(self):
        encrypted = encrypt(TEST_KEYS, TEST_MESSAGE)
        version, decrypted = decrypt(TEST_KEYS, encrypted)
        eq_(version, 1)
        eq_(decrypted, TEST_MESSAGE)

    def test_encrypt_decrypt_unicode(self):
        encrypted = encrypt(TEST_KEYS, TEST_UNICODE_MESSAGE)
        version, decrypted = decrypt(TEST_KEYS, encrypted)
        eq_(version, 1)
        eq_(decrypted, TEST_UNICODE_MESSAGE.encode())

    @raises(UnsupportedVersionError)
    def test_decrypt_version_missing(self):
        decrypt(TEST_KEYS, 'something')

    @raises(UnsupportedVersionError)
    def test_decrypt_unknown_version(self):
        decrypt(TEST_KEYS, '42:something')

    @raises(DecryptFailedError)
    def test_decrypt_failed_corrupt_message(self):
        encrypted = encrypt(TEST_KEYS, TEST_MESSAGE)
        decrypt(TEST_KEYS, encrypted + b'1')

    @raises(DecryptFailedError)
    def test_decrypt_failed_malformed_message(self):
        decrypt(TEST_KEYS, '1:something')
