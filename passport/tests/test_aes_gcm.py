# -*- coding: utf-8 -*-

from cryptography.exceptions import InvalidTag
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.crypto.aes_gcm import (
    decrypt,
    encrypt,
)
import six


TEST_KEY = b'KEYY' * 8

TEST_KEY_2 = b'1' * 32

TEST_SECRET = b'abcd'

TEST_ASSOCIATED_DATA = b'xxxyyyzzz'


def test_encrypt_decrypt_ok():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)

    value = decrypt(TEST_KEY, TEST_ASSOCIATED_DATA, iv, ciphertext, tag)

    eq_(value, TEST_SECRET)


def test_encrypt_decrypt_empty_data_ok():
    iv, ciphertext, tag = encrypt(TEST_KEY, b'', b'')

    value = decrypt(TEST_KEY, b'', iv, ciphertext, tag)

    eq_(value, b'')


def test_encrypt_invalid_key():
    for key in [TEST_KEY + b'2', b'']:
        with assert_raises(ValueError):
            encrypt(key, TEST_SECRET, TEST_ASSOCIATED_DATA)


def test_encrypt_invalid_encoding():
    with assert_raises(TypeError):
        encrypt(TEST_KEY, u'яблоко', TEST_ASSOCIATED_DATA)

    with assert_raises(TypeError):
        encrypt(TEST_KEY, TEST_SECRET, u'яблоко')


def test_decrypt_invalid_key():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)

    with assert_raises(ValueError):
        decrypt(TEST_KEY + b'1', TEST_ASSOCIATED_DATA, iv, ciphertext, tag)


def test_decrypt_incorrect_key():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)

    with assert_raises(InvalidTag):
        decrypt(TEST_KEY_2, TEST_ASSOCIATED_DATA, iv, ciphertext, tag)


def test_decrypt_incorrect_associated_data():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)

    with assert_raises(InvalidTag):
        decrypt(TEST_KEY, TEST_ASSOCIATED_DATA + b'bad', iv, ciphertext, tag)


def test_decrypt_incorrect_iv():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)
    if six.PY2:
        iv0 = ord(iv[0])
    else:
        iv0 = iv[0]
    tmp = chr(255 - iv0)
    if six.PY3:
        tmp = tmp.encode('latin1')
    iv = tmp + iv[1:]

    with assert_raises(InvalidTag):
        decrypt(TEST_KEY, TEST_ASSOCIATED_DATA, iv, ciphertext, tag)


def test_decrypt_incorrect_ciphertext():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)
    ciphertext = ciphertext[1:]

    with assert_raises(InvalidTag):
        decrypt(TEST_KEY, TEST_ASSOCIATED_DATA, iv, ciphertext, tag)


def test_decrypt_incorrect_tag():
    iv, ciphertext, tag = encrypt(TEST_KEY, TEST_SECRET, TEST_ASSOCIATED_DATA)
    if six.PY2:
        tag0 = ord(tag[0])
    else:
        tag0 = tag[0]

    tmp = chr(255 - tag0)
    if six.PY3:
        tmp = tmp.encode('latin1')
    tag = tmp + tag[1:]

    with assert_raises(InvalidTag):
        decrypt(TEST_KEY, TEST_ASSOCIATED_DATA, iv, ciphertext, tag)
