# -*- coding: utf-8 -*-
from collections import namedtuple
import time

from passport.backend.logbroker_client.account_events.exceptions import (
    BaseNotifyError,
    NotifyRequestError,
)
from passport.backend.logbroker_client.account_events.notify import NotifyClient
from passport.backend.logbroker_client.account_events.test.fake import FakeNotify
import pytest


notify_client = NotifyClient('fotki', 'http://fotki')


@pytest.fixture
def fake_notify(request):
    notify_fake = FakeNotify()
    notify_fake.start()

    def fin():
        notify_fake.stop()
    request.addfinalizer(fin)
    return notify_fake


def test_notify_valid(fake_notify):
    fake_notify.set_notify_response_value('{"status": "ok"}', 200)
    notify_client.notify(namedtuple('Event', ['uid', 'name', 'timestamp'])(125256075, 'glogout', int(time.time())))


def test_notify_valid_with_body(fake_notify):
    fake_notify.set_notify_response_value('{"status": "ok"}', 200)
    notify_client.notify(namedtuple('Event', ['uid', 'name', 'timestamp'])(125256075, 'glogout', int(time.time())))


def test_notify_parser_error(fake_notify):
    fake_notify.set_notify_response_value('auth_fail = 2', 200)
    with pytest.raises(NotifyRequestError):
        notify_client.notify(namedtuple('Event', ['uid', 'name', 'timestamp'])(125256075, 'glogout', int(time.time())))


def test_notify_invalid_response_error(fake_notify):
    fake_notify.set_notify_response_value('{"status": "error"}', 400)
    with pytest.raises(BaseNotifyError):
        notify_client.notify(namedtuple('Event', ['uid', 'name', 'timestamp'])(125256075, 'glogout', int(time.time())))


def test_notify_temporary_error(fake_notify):
    fake_notify.set_notify_response_value('{"status": "error"}', 500)
    with pytest.raises(BaseNotifyError):
        notify_client.notify(namedtuple('Event', ['uid', 'name', 'timestamp'])(125256075, 'glogout', int(time.time())))
