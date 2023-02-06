# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.api.api.yandex_login.utils import (
    mask_token,
    parse_bool_str,
    sort_emails,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class SortEmailsTestCase(BaseTestCase):
    def test_1(self):
        emails = sort_emails([
            'aa@bb.cc',
            'aa2@bb2.cc2',
        ])
        eq_(emails, ['aa@bb.cc', 'aa2@bb2.cc2'])

    def test_2(self):
        emails = sort_emails([
            'aa2@bb.cc',
            'aa@bb2.cc2',
        ])
        eq_(emails, ['aa@bb2.cc2', 'aa2@bb.cc'])


class ParseBoolStrTestCase(BaseTestCase):
    def test_ok(self):
        for from_, to_ in (
            ('yes', True),
            ('YES', True),
            ('true', True),
            ('True', True),
            ('1', True),
            ('false', False),
            ('no', False),
            ('0', False),
            ('smth_other', False),
        ):
            eq_(parse_bool_str(from_), to_)


class MaskTokenTestCase(BaseTestCase):
    def test_ok(self):
        eq_(
            mask_token('a' * 32),
            'a' * 16 + '*' * 16,
        )

    def test_long(self):
        eq_(
            mask_token('a' * 48),
            'a' * 24 + '*' * 24,
        )

    def test_short(self):
        eq_(
            mask_token('a' * 18),
            'a' * 9 + '*' * 9,
        )

    def test_empty(self):
        eq_(
            mask_token(''),
            '',
        )
        eq_(
            mask_token(None),
            None,
        )
