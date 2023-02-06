# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.services import (
    _sids_internal_subscribe,
    _sids_renewable,
    _sids_requires_login,
    _sids_requires_password,
    _sids_stores_not_uid_in_login,
    get_service,
)


def test_sids_stores_not_uid_in_login():
    for sid in _sids_stores_not_uid_in_login:
        eq_(get_service(sid=sid).stores_not_uid_in_login, True)


def test_sids_requires_login():
    for sid in _sids_requires_login:
        eq_(get_service(sid=sid).requires_login, True)


def test_sids_requires_password():
    for sid in _sids_requires_password:
        eq_(get_service(sid=sid).requires_password, True)


def test_sids_internal_subscribe():
    for sid in _sids_internal_subscribe:
        eq_(get_service(sid=sid).internal_subscribe, True)


def test_sids_renewable():
    for sid in _sids_renewable:
        eq_(get_service(sid=sid).is_renewable, True)


def test_service_hash():
    mail = get_service(slug='mail')
    money = get_service(slug='money')
    service_set = set([mail, mail])
    eq_(len(service_set), 1)
    ok_(mail in service_set)
    ok_(money not in service_set)


def test_service_repr():
    actual = repr(get_service(slug='mail'))
    expected = "<%s: %r>" % ('Service', get_service(slug='mail').__dict__)
    assert actual == expected
