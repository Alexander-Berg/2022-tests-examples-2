# -*- coding: utf-8 -*-
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.oauth.api.api.yandex_login.utils import parse_auth_header
from passport.backend.oauth.core.test.framework import BaseTestCase


class ParseAuthHeaderTestCase(BaseTestCase):
    def test_oauth(self):
        eq_(
            parse_auth_header('OAuth foo'),
            'foo',
        )

    def test_oauth_mixed_case(self):
        eq_(
            parse_auth_header('oAuTh fOO'),
            'fOO',
        )

    def test_bearer(self):
        eq_(
            parse_auth_header('Bearer foo'),
            'foo',
        )

    def test_bearer_mixed_case(self):
        eq_(
            parse_auth_header('bEaReR fOO'),
            'fOO',
        )

    def test_unknown_scheme(self):
        assert_is_none(
            parse_auth_header('basic foo'),
        )

    def test_empty_header(self):
        assert_is_none(
            parse_auth_header(''),
        )

    def test_missingheader(self):
        assert_is_none(
            parse_auth_header(None),
        )
