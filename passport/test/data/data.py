# -*- coding: utf-8 -*-
from collections import namedtuple

from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON


password_info = namedtuple('password_info', 'password salt quality encrypted')
TEST_PASSWORD = password_info('kasdlsdf', 'salt', 24, '$1$salt$ZjqOeku9hOwYcRRqwMdCc.')

TEST_PASSWORD_HASH = 'c4ca4238a0b923820dcc509a6f75849b'
TEST_PASSWORD_HASH_MD5_CRYPT_ARGON = '1:1:2048:md5salt:argonsalt:hash'
TEST_PASSWORD_HASH_RAW_MD5_ARGON = '1:1:2048:argonsalt:hash'
TEST_SERIALIZED_PASSWORD = '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON, TEST_PASSWORD_HASH_MD5_CRYPT_ARGON)
TEST_IMPOSSIBLE_PASSWORD = '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON, '-')
