# -*- coding: utf-8 -*-

from passport.backend.vault.api.utils.secrets import (
    InvalidSignedString,
    parse_signed_string,
    sign_string,
)
import pytest


def test_sign_string():
    test = (
        ('', '.1.9ae16a3b2f90404f'),
        ('ololo-hash', 'ololo-hash.1.1ad613cf56489198'),
        (u'хешик с русскими буковками', u'хешик с русскими буковками.1.b9d7702dff1762fd'),
        ('one.two.three. .', 'one.two.three. ..1.a01e4c9da8890889'),
    )
    for t in test:
        assert sign_string(t[0]) == t[1]


def test_parse_signed_string():
    test = (
        ('.1.9ae16a3b2f90404f', ''),
        ('.1.9AE16A3B2F90404F', ''),
        ('ololo-hash.1.1ad613cf56489198', 'ololo-hash'),
        (u'хешик с русскими буковками.1.b9d7702dff1762fd', u'хешик с русскими буковками'),
        ('one.two.three. ..1.a01e4c9da8890889', 'one.two.three. .'),
    )
    for t in test:
        assert parse_signed_string(t[0]) == t[1]


def test_parse_invalid_signed_string():
    test = (
        '',
        '.1.9ae16a3b2f904000',
        '.1.9ae16a3b2f90404f.abce',
        '.....1.9ae16a3b2f90404f',
        'one.two.three....1.a01e4c9da8890889'
        '.9ae16a3b2f90404f',
        '1.9ae16a3b2f90404f',
        'ololo-hash.1.1ad613cf53389198',
    )
    for t in test:
        with pytest.raises(InvalidSignedString):
            assert parse_signed_string(t)
