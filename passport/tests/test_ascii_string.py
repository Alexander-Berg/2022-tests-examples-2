# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import ASCIIString
import pytest


MAX_ASCII_STRING_LENGTH = 255


@pytest.mark.parametrize('valid_param', [
    'a' * MAX_ASCII_STRING_LENGTH,
    '123',
    '!#$%`{}|~"{:><?&\'*+-/=?^',
    ])
def test_ok(valid_param):
    check_equality(ASCIIString(), (valid_param, valid_param.strip()))


@pytest.mark.parametrize('invalid_param', [
    ' ' * MAX_ASCII_STRING_LENGTH,
    'a' * (MAX_ASCII_STRING_LENGTH + 1),
    'foo\nbar',
    'foo\x0D\x0Abar',
    'foo\x0Abar',
    u'бэкап',
    123,
    '',
    None,
    ])
def test_not_ok(invalid_param):
    check_raise_error(ASCIIString(), invalid_param)


@pytest.mark.parametrize('valid_param', [
    'foo\nbar',
    'foo\x0D\x0Abar',
    'foo\x0Abar',
    ])
def test_new_lines_allowed(valid_param):
    check_equality(ASCIIString(allow_new_lines=True), (valid_param, valid_param.strip()))
