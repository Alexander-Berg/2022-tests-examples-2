# coding: utf-8

from passport.backend.utils.file import (
    get_gid,
    get_uid,
    parse_owner,
)


def test_parse_owner():
    assert parse_owner('user') == ('user', None)
    assert parse_owner('user:group') == ('user', 'group')
    assert parse_owner(':group') == (None, 'group')
    assert parse_owner('100') == ('100', None)
    assert parse_owner('100:101') == ('100', '101')
    assert parse_owner(':101') == (None, '101')


def test_get_gid():
    assert get_gid('root') == 0
    assert get_gid('0') == 0
    assert get_gid('-1') is None


def test_get_uid():
    assert get_uid('root') == 0
    assert get_uid('0') == 0
    assert get_uid('-1') is None
