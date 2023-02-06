# -*- coding: utf-8 -*-
import unittest

from nose.tools import assert_raises
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
    PASSWORD_ENCODING_VERSION_MD5_HEX,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
)
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators.password.password import PasswordHash


TEST_MD5_CRYPT_HASH = '$1$aaaaaaaa$lWxWtPmiNjS/cwJnGm6fe0'
TEST_MD5_RAW_HASH = 'ab' * 16


class TestPasswordHash(unittest.TestCase):
    def test_md5crypt_ok(self):
        validator = PasswordHash(allowed_hash_versions=[PASSWORD_ENCODING_VERSION_MD5_CRYPT])
        check_equality(
            validator,
            (
                TEST_MD5_CRYPT_HASH,
                (PASSWORD_ENCODING_VERSION_MD5_CRYPT, TEST_MD5_CRYPT_HASH),
            ),
        )

    def test_raw_md5_ok(self):
        validator = PasswordHash(allowed_hash_versions=[PASSWORD_ENCODING_VERSION_MD5_HEX])
        check_equality(
            validator,
            (
                TEST_MD5_RAW_HASH,
                (PASSWORD_ENCODING_VERSION_MD5_HEX, TEST_MD5_RAW_HASH),
            ),
        )

    def test_select_by_priority(self):
        """По формату подходят обе версии, но у Аргона приоритет выше"""
        validator = PasswordHash(
            allowed_hash_versions=[PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON, PASSWORD_ENCODING_VERSION_MD5_HEX],
        )
        check_equality(
            validator,
            (
                TEST_MD5_RAW_HASH,
                (PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON, TEST_MD5_RAW_HASH),
            ),
        )

    def test_invalid_hash(self):
        invalid_hashes = [
            ':',
            '123',
            u'Привет, мир',
            'a' * 31,
            'a' * 33,
        ]
        validator = PasswordHash(
            allowed_hash_versions=[
                PASSWORD_ENCODING_VERSION_MD5_CRYPT,
                PASSWORD_ENCODING_VERSION_MD5_HEX,
                PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
                PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
            ],
        )
        for invalid_hashes in invalid_hashes:
            check_raise_error(validator, invalid_hashes)

    def test_forbidden_hash_version(self):
        validator = PasswordHash(
            allowed_hash_versions=[PASSWORD_ENCODING_VERSION_MD5_CRYPT],
        )
        check_raise_error(validator, TEST_MD5_RAW_HASH)

    def test_unsupported_hash_version(self):
        with assert_raises(NotImplementedError):
            PasswordHash(allowed_hash_versions=[0])
