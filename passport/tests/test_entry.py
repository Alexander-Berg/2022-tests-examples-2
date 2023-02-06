# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.historydb.entry import (
    AuthChallengeEntry,
    EventEntry,
    LogEntry,
    LoyaltyEntry,
    RestoreEntry,
)
from passport.backend.core.test.test_utils import settings_context
import six


class TestEntry(unittest.TestCase):
    def setUp(self):
        super(TestEntry, self).setUp()

    def test_LogEntry(self):
        entry = LogEntry(uid=123, user_ip='127.0.0.1', comment='der_comment')
        eq_(entry.uid, 123)
        eq_(entry.ip_from, '127.0.0.1')
        eq_(entry.comment, 'der_comment')

    @raises(NotImplementedError)
    def test_LogEntry_str(self):
        str(LogEntry())

    @raises(NotImplementedError)
    def test_LogEntry_unicode(self):
        six.text_type(LogEntry())

    def test_LogEntry_ipv4_mapped(self):
        entry = LogEntry(uid=123, user_ip='::ffff:127.0.0.1')
        eq_(entry.uid, 123)
        eq_(entry.ip_from, '127.0.0.1')

    def test_LogEntry_ipv6(self):
        entry = LogEntry(uid=123, user_ip='2a02:6b8::24')
        eq_(entry.uid, 123)
        eq_(entry.ip_from, '2a02:6b8::24')

    def test_LogEntry_empty_ip(self):
        entry = LogEntry(uid=123)
        eq_(entry.uid, 123)
        eq_(entry.ip_from, None)
        eq_(entry.ip_prox, None)

    def test_EventEntry(self):
        entry = EventEntry(name='name', value='value', comment='the_comment', admin='the_admin')
        eq_(entry.name, 'name')
        eq_(entry.value, 'value')
        eq_(entry.comment, 'the_comment')
        eq_(entry.admin, 'the_admin')
        eq_(entry.sensitive_fields, set())

        entry = EventEntry(name=['a', 'b'], value=['c', 'd'])
        eq_(entry.name, ['a', 'b'])
        eq_(entry.value, ['c', 'd'])

        entry = EventEntry(name='info.password', value='')
        eq_(entry.sensitive_fields, set())
        with settings_context(HISTORYDB_LOG_ENCRYPTION_ENABLED=True):
            entry = EventEntry(name='info.password', value='')
            eq_(entry.sensitive_fields, {'value'})

            entry = EventEntry(name='info.hinta', value='hinta')
            eq_(entry.sensitive_fields, {'value'})

    def test_LoyaltyEntry(self):
        entry = LoyaltyEntry(
            123.123456,
            'email',
            'foo@okna.ru',
            '8.8.8.8',
            'maps',
            'action name',
            {'foo': 'bar'},
        )
        eq_(entry.timestamp, 123.123456)
        eq_(entry.user_id_type, 'email')
        eq_(entry.user_id, 'foo@okna.ru')
        eq_(entry.user_ip, '8.8.8.8')
        eq_(entry.domain, 'maps')
        eq_(entry.name, 'action name')
        eq_(entry.meta, {'foo': 'bar'})
        eq_(entry.meta_json, '{"foo": "bar"}')
        eq_(entry.timestamp_str, '123.123456')

    def test_RestoreEntry(self):
        entry = RestoreEntry(
            'restore',
            1,
            '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f',
            {'a': 'b'},
        )
        eq_(entry.action, 'restore')
        eq_(entry.uid, 1)
        eq_(entry.restore_id, '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f')
        eq_(entry.data, {'a': 'b'})
        eq_(entry.data_json, '{"a": "b"}')
        eq_(entry.sensitive_fields, set())

        with settings_context(HISTORYDB_LOG_ENCRYPTION_ENABLED=True):
            entry = RestoreEntry(
                'restore',
                1,
                '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f',
                {'a': 'b'},
            )
            eq_(entry.sensitive_fields, {'data_json'})

    def test_AuthChallengeEntry(self):
        env = {
            'yandexuid': '123',
            'UserAgent': 'curl',
            'user_ip': '123',
        }

        entry = AuthChallengeEntry(
            'some-action',
            123,
            '5972577a-8208-11e5-9f79-843a4bcee9c4',
            env,
            'comment',
        )
        eq_(entry.action, 'some-action')
        eq_(entry.uid, 123)
        eq_(entry.env_profile_id, '5972577a-8208-11e5-9f79-843a4bcee9c4')
        eq_(
            entry.env_profile_pb2_base64,
            '-',
        )
        eq_(entry.env, env)
        eq_(entry.env_json, json.dumps(env))
        eq_(entry.comment, 'comment')
