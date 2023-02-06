# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_EMAIL,
    TEST_HISTORYDB_API_URL,
    TEST_MASKED_EMAIL,
    TEST_MASKED_PUNICODE_EMAIL,
    TEST_PUNICODE_EMAIL,
)


class CommonCases(object):
    email = None
    masked_email = None

    def test_email_new_add(self):
        """Событие добавления почтового адреса в новом валидаторе"""
        events = self.make_historydb_events(
            {
                'action': 'validator',
                'email.369': 'created',
                'email.369.address': self.email,
                'email.369.created_at': '1461831768',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'email_add')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_add',
                    'email_bind': self.masked_email,
                },
            ],
        )

    def test_email_new_delete(self):
        """Событие отвязки почтового адреса в новом валидаторе"""
        events = self.make_historydb_events(
            {
                'action': 'validator',
                'email.369': 'deleted',
                'email.369.address': self.email,
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'email_remove')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_remove',
                    'email_unbind': self.masked_email,
                },
            ],
        )

    def test_email_old_add(self):
        events = self.make_historydb_events(
            {
                'email.unsafe': '{} safe'.format(self.email),
            },
            client_name='validator',
            user_agent=False,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'email_add')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_add',
                    'email_bind': self.masked_email,
                },
            ],
        )

    def test_email_old_delete(self):
        events = self.make_historydb_events(
            {
                'email.delete': self.email,
            },
            client_name='validator',
            user_agent=False,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'email_remove')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_remove',
                    'email_unbind': self.masked_email,
                },
            ],
        )


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryParseEmailTestCase(BaseHistoryParserTestCase, CommonCases):
    email = TEST_EMAIL
    masked_email = TEST_MASKED_EMAIL

    def test_email_old_delete_empty_email(self):
        # Я такого кейса не встречал, но на всякий случай подстраховался
        events = self.make_historydb_events(
            {
                'email.delete': ' aa bb cc ',
            },
            client_name='validator',
            user_agent=False,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 0)

    def test_email_old_delete_all(self):
        events = self.make_historydb_events(
            {
                'email.delete': '*',
            },
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'email_remove')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'email_remove_all',
                },
            ],
        )


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL
)
class HistoryParsePunycodeEmailTestCase(BaseHistoryParserTestCase, CommonCases):
    email = TEST_PUNICODE_EMAIL
    masked_email = TEST_MASKED_PUNICODE_EMAIL
