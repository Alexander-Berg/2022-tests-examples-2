# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.authtypes import authtypes
from passport.backend.core.historydb.entry import (
    AuthEntry,
    EventEntry,
)
from passport.backend.core.historydb.statuses import SESSION_CREATE


class TestUtils(unittest.TestCase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_entry_to_str(self):
        entries = []
        for n, v in [('another', 'one'), ('bites', 'the dust')]:
            entry = EventEntry(
                host_id=0x5,
                client_name='name',
                uid=123,
                user_ip='127.0.0.1',
                name=n,
                value=v,
            )

            entries.append(entry)

        logs = [str(e) for e in entries]
        eq_(len(logs), 2)
        ok_('another one' in logs[0])
        ok_('bites `the dust`' in logs[1])

    def test_auth_entry_to_str(self):
        entry = AuthEntry(
            host_id=0x7F,
            client_name='name',
            uid=123,
            user_ip='127.0.0.1',
            comment='hinta=asdf115prmode=key128',
            status=SESSION_CREATE,
            type=authtypes.AUTH_TYPE_WEB,
        )

        log = str(entry)
        ok_('hinta=asdf115prmode=key128' in log)
