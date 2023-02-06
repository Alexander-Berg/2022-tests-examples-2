# -*- coding: utf-8 -*-
from nose.tools import (
    ok_,
    raises,
)
from passport.backend.core.crypto.md5crypt import md5crypt
from passport.backend.core.crypto.utils import (
    check_hashed_string,
    dumb_hash_string,
    hash_string,
)
from passport.backend.core.test.test_utils import PassportTestCase


class TestUtils(PassportTestCase):

    def test_check_hash_string(self):
        string = 'abcd'
        hashed_string = hash_string(string)
        ok_(check_hashed_string(string, hashed_string))
        ok_(not check_hashed_string('efgh', hashed_string))

    def test_check_dumb_hash_string(self):
        string = 'test1234'
        hashed_string = dumb_hash_string(string)
        ok_(check_hashed_string(string, hashed_string))
        ok_(not check_hashed_string('efgh', hashed_string))

    @raises(ValueError)
    def test_check_hash_string_error(self):
        string = 'abcd'
        hashed_string = md5crypt(string, magic=b'$2$')
        ok_(check_hashed_string(string, hashed_string))

    def test_check_hash_string_unicode(self):
        string = u'строка'
        hashed_string = hash_string(string)
        ok_(check_hashed_string(string, hashed_string))

    def test_check_hashed_string_raw_md5(self):
        string = 'test1234'
        hashed_string = '16d7a4fca7442dda3ad93c9a726597e4'
        ok_(check_hashed_string(string, hashed_string))

    def test_check_hashed_string_unicode_raw_md5(self):
        string = u'абырвалг'
        hashed_string = '8db606ee2ca7db5c1ee6db13d727dd64'
        ok_(check_hashed_string(string, hashed_string))

    def test_check_hash_string_empty_hash(self):
        ok_(not check_hashed_string('test', ''))
