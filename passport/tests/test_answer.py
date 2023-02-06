# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.core.types.answer import normalize_answer
import pytest


@pytest.mark.parametrize(
    ('actual', 'expected'),
    [
        ('foo     bar', 'foo bar'),
        ('   \t x\t\t  \t\t\n  y  \t\nz  ', 'x y z'),
        (u'А б  В Г  д \n Е \t Ё \n ж', u'а б в г д е ё ж'),
    ],
)
def test_normalize_answer(actual, expected):
    eq_(normalize_answer(actual), expected)
