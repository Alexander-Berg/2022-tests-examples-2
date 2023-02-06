# -*- coding: utf-8 -*-

from collections import namedtuple
import socket

from mock import patch
from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.host.host import get_current_host
from passport.backend.core.test.test_utils import with_settings
import yenv


_host = namedtuple('host', 'name id dc')


def check_host_id(id):
    eq_(get_current_host().get_id(), id)


def check_raise_error(id):
    for env_type in ('testing', 'production'):
        with patch.object(yenv, 'type', env_type):
            with assert_raises(RuntimeError):
                get_current_host().get_id()


@with_settings(HOSTS=[_host(name='localhost', id=0x7F, dc='myt'), _host(name='unknown.addr', id=0x8F, dc='f')])
def check_defaults_on_testing(id):
    with patch.object(yenv, 'type', 'development'):
        eq_(get_current_host().get_id(), id)


@with_settings(HOSTS=[_host(name=socket.getfqdn(), id=0x7F, dc='myt')])
def test_real_address():
    check_host_id(127)


@with_settings(HOSTS=[_host(name='unknown.addr', id=0x7F, dc='myt')])
def test_unknown_address():
    check_raise_error(127)


@with_settings(HOSTS=[_host(name=socket.getfqdn(), id=0x7F, dc='myt')])
def test_get_dc():
    eq_(get_current_host().get_dc(), 'myt')


@with_settings(HOSTS=[])
@raises(RuntimeError)
def test_get_dc_misconfigured():
    get_current_host().get_dc()
