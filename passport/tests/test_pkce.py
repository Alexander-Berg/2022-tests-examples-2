# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.utils.pkce import (
    CODE_CHALLENGE_METHOD_PLAIN,
    CODE_CHALLENGE_METHOD_SHA256,
    is_pkce_valid,
    make_code_challenge_s256,
)


TEST_CODE_VERIFIER = 'foo'
TEST_CODE_CHALLENGE = 'LCa0a2j_xo_5m0U8HTBBNBNCLXBkg7-g-YpeiGJm564'


class TestPkce(unittest.TestCase):
    def test_make_code_challenge_s256(self):
        eq_(make_code_challenge_s256(TEST_CODE_VERIFIER), TEST_CODE_CHALLENGE)

    def test_is_pkce_valid__plain(self):
        ok_(is_pkce_valid(
            challenge=TEST_CODE_VERIFIER,
            challenge_method=CODE_CHALLENGE_METHOD_PLAIN,
            verifier=TEST_CODE_VERIFIER,
        ))

    def test_is_pkce_valid__s256(self):
        ok_(is_pkce_valid(
            challenge=TEST_CODE_CHALLENGE,
            challenge_method=CODE_CHALLENGE_METHOD_SHA256,
            verifier=TEST_CODE_VERIFIER,
        ))

    def test_is_pkce_valid__not_required(self):
        ok_(is_pkce_valid(
            challenge=None,
            challenge_method=None,
            verifier=None,
        ))

    def test_not_is_pkce_valid__plain(self):
        ok_(not is_pkce_valid(
            challenge=TEST_CODE_VERIFIER,
            challenge_method=CODE_CHALLENGE_METHOD_PLAIN,
            verifier='bar',
        ))

    def test_not_is_pkce_valid__s256(self):
        ok_(not is_pkce_valid(
            challenge=TEST_CODE_VERIFIER,
            challenge_method=CODE_CHALLENGE_METHOD_SHA256,
            verifier='bar',
        ))

    def test_not_is_pkce_valid__not_required_but_passed(self):
        ok_(not is_pkce_valid(
            challenge=None,
            challenge_method=None,
            verifier=TEST_CODE_VERIFIER,
        ))
