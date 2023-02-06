# -*- coding: utf-8 -*-
import json
import time

from passport.backend.logbroker_client.xiva.exceptions import (
    XivaPersistentError,
    XivaTemporaryError,
)
from passport.backend.logbroker_client.xiva.fake import FakeXiva
from passport.backend.logbroker_client.xiva.xiva import Xiva
import pytest


xiva_fake = FakeXiva()
xiva_fake.start()

xiva_client = Xiva('http://xiva', 'stoken', 'stoken_stream', 3)


@pytest.fixture
def fake_xiva(request):
    xiva_fake = FakeXiva()
    xiva_fake.start()

    def fin():
        xiva_fake.stop()
    request.addfinalizer(fin)
    return xiva_fake


def test_notify_valid(fake_xiva):
    fake_xiva.set_xiva_response_value('', 200)
    xiva_client.notify(125256075, 'glogout', int(time.time()))


def test_notify_valid_with_body(fake_xiva):
    data = json.dumps({'session': '1234567890qwerty'})
    fake_xiva.set_xiva_response_value('', 200)
    xiva_client.notify(125256075, 'glogout', int(time.time()), data)


def test_notify_persistent_error(fake_xiva):
    fake_xiva.set_xiva_response_value('auth_fail = 2', 400)
    with pytest.raises(XivaPersistentError):
        xiva_client.notify(125256075, 'glogout', int(time.time()))


def test_notify_temporary_error(fake_xiva):
    fake_xiva.set_xiva_response_value('', 500)
    with pytest.raises(XivaTemporaryError):
        xiva_client.notify(125256075, 'glogout', int(time.time()))


def test_stream_notify_valid(fake_xiva):
    fake_xiva.set_xiva_response_value('', 200)
    xiva_client.stream_notify('glogout', {})
