# -*- coding: utf-8 -*-
from passport.backend.perimeter.auth_api.test import BaseTestCase
from passport.backend.perimeter.auth_api.utils.hash import (
    check_hashed_string,
    hash_string,
    truncated_hash,
)
import pytest


class TestHash(BaseTestCase):
    def test_check_hash_string(self):
        string = 'abcd'
        hashed_string = hash_string(string)
        assert check_hashed_string(string, hashed_string)
        assert not check_hashed_string('efgh', hashed_string)
        assert not check_hashed_string(string, '')

    def test_check_hash_string_nonascii(self):
        string = 'строка'
        hashed_string = hash_string(string)
        assert check_hashed_string(string, hashed_string)

    def test_unknown_hash_type(self):
        with pytest.raises(ValueError):
            check_hashed_string('abcd', '42$__$__')

    def test_simple_hash(self):
        assert truncated_hash('123') == 'a665a45920422f9d417e4867efdc4fb8a'
