# -*- coding: utf-8 -*-
import unittest

from passport.backend.logbroker_client.core.events.filters import BasicFilter
from passport.backend.logbroker_client.core.handlers.utils import MessageChunk
from passport.backend.logbroker_client.mail_unsubscriptions.events import (
    EmailConfirmedAddEvent,
    PortalAliasAddEvent,
    Sid2ChangeEvent,
    UnsubscribedFromMaillistsAttributeChangeEvent,
)


HEADER = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/statbox/statbox.log',
    'servier': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}


class TestEvents(unittest.TestCase):
    events_filter = BasicFilter([
        UnsubscribedFromMaillistsAttributeChangeEvent,
        Sid2ChangeEvent,
        EmailConfirmedAddEvent,
        PortalAliasAddEvent,
    ])

    def test_excess_events(self):
        log_data = (
            # без entity
            'tskv\tunixtime=139883646\tuid=10\toperation=updated\tsome_data=ccc\n'
            # неподходящий entity
            'tskv\tentity=wrong\tunixtime=139883646\tuid=11\toperation=added\tsome_data=ccc\n'
            + '\n'.join(  # без uid, странный uid (для каждого entity)
                'tskv\tentity={}\tunixtime=139883646\toperation={}\tsome_data=ccc\n'
                'tskv\tentity={}\tunixtime=139883646\tuid=wrong\toperation={}\tsome_data=ccc\n'.format(
                    f.ENTITY, f.OPERATIONS[0], f.ENTITY, f.OPERATIONS[0],
                ) for f in self.events_filter.events_classes
            )
            + '\n'.join(  # operation == 'wrong' (для каждого entity)
                'tskv\tentity={}\tunixtime=139883646\toperation=wrong\tuid=123\nsome_data=ccc\n'.format(
                    f.ENTITY,
                ) for f in self.events_filter.events_classes
            )
        )
        message = MessageChunk(HEADER, log_data)
        events_res = self.events_filter.filter(message)
        self.assertEqual(
            len(events_res), 0,
            'Excess events: {}'.format([event.__dict__ for event in events_res]),
        )

    def test_unsubscribed_from_maillists_change_event(self):
        log_data = (
            'tskv\tentity=account.unsubscribed_from_maillists\tunixtime=139883641\tuid=10\toperation=updated\tsome_data=ccc\n'
            'tskv\tentity=account.unsubscribed_from_maillists\tunixtime=139883642\tuid=11\toperation=added\tsome_data=ccc\n'
            'tskv\tentity=account.unsubscribed_from_maillists\tunixtime=139883643\tuid=12\toperation=created\tsome_data=ccc\n'
        )
        message = MessageChunk(HEADER, log_data)
        events_res = self.events_filter.filter(message)

        self.assertEqual(len(events_res), 3)
        self.assertIsInstance(events_res[0], UnsubscribedFromMaillistsAttributeChangeEvent)
        self.assertEqual(events_res[0].uid, 10)
        self.assertEqual(events_res[0].operation, 'updated')
        self.assertEqual(events_res[0].timestamp, 139883641)
        self.assertIsInstance(events_res[1], UnsubscribedFromMaillistsAttributeChangeEvent)
        self.assertEqual(events_res[1].uid, 11)
        self.assertEqual(events_res[1].operation, 'added')
        self.assertEqual(events_res[1].timestamp, 139883642)
        self.assertIsInstance(events_res[2], UnsubscribedFromMaillistsAttributeChangeEvent)
        self.assertEqual(events_res[2].uid, 12)
        self.assertEqual(events_res[2].operation, 'created')
        self.assertEqual(events_res[2].timestamp, 139883643)

    def test_sid2_change_event(self):
        log_data = (
            'tskv\tentity=subscriptions\tunixtime=139883641\tuid=10\toperation=added\tsid=2\tsome_data=bbb\n'
            'tskv\tentity=subscriptions\tunixtime=139883642\tuid=11\toperation=removed\tsid=2\tsome_data=bbb\n'
        )
        message = MessageChunk(HEADER, log_data)
        events_res = self.events_filter.filter(message)

        self.assertEqual(len(events_res), 2)
        self.assertIsInstance(events_res[0], Sid2ChangeEvent)
        self.assertEqual(events_res[0].uid, 10)
        self.assertEqual(events_res[0].operation, 'added')
        self.assertEqual(events_res[0].timestamp, 139883641)
        self.assertIsInstance(events_res[1], Sid2ChangeEvent)
        self.assertEqual(events_res[1].uid, 11)
        self.assertEqual(events_res[1].operation, 'removed')
        self.assertEqual(events_res[1].timestamp, 139883642)

    def test_email_confirmed_add_event(self):
        log_data = (
            'tskv\tentity=account.emails\tunixtime=139883641\tuid=10\tconfirmed_at=2021-01-28\toperation=added\temail_id=2\tsome_data=aaa\n'
            'tskv\tentity=account.emails\tunixtime=139883642\tuid=20\tconfirmed_at=2021-01-28\toperation=added\temail_id=aaa\tsome_data=aaa\n'
            'tskv\tentity=account.emails\tunixtime=139883643\tuid=21\toperation=added\temail_id=2\tsome_data=aaa\n'
        )
        message = MessageChunk(HEADER, log_data)
        events_res = self.events_filter.filter(message)

        self.assertEqual(len(events_res), 1)
        self.assertIsInstance(events_res[0], EmailConfirmedAddEvent)
        self.assertEqual(events_res[0].uid, 10)
        self.assertEqual(events_res[0].operation, 'added')
        self.assertEqual(events_res[0].timestamp, 139883641)
        self.assertTrue(events_res[0].email_id, 2)

    def test_portal_alias_add_event(self):
        log_data = (
            'tskv\tentity=aliases\tunixtime=139883645\tuid=456\toperation=added\ttype=2\tsome_data=aaa\n'
            'tskv\tentity=aliases\tunixtime=139883646\tuid=123\toperation=added\ttype=1\tsome_data=aaa\n'
        )
        message = MessageChunk(HEADER, log_data)
        events_res = self.events_filter.filter(message)

        self.assertEqual(len(events_res), 1)
        self.assertIsInstance(events_res[0], PortalAliasAddEvent)
        self.assertEqual(events_res[0].uid, 123)
        self.assertEqual(events_res[0].operation, 'added')
        self.assertEqual(events_res[0].timestamp, 139883646)
