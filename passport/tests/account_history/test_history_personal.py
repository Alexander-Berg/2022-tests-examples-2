# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_HISTORYDB_API_URL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryParsePersonalTestCase(BaseHistoryParserTestCase):
    def test_remove_birthday_fields(self):
        events = self.make_historydb_events(
            {
                'info.birthday': None,
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'personal_data',
                    'birthday': None,
                    'changed_fields': [
                        'birthday',
                    ],
                },
            ],
        )

    def test_personal_only_lang_field(self):
        events = self.make_historydb_events(
            {
                'action': 'person',
                'info.lang': 'en',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 0)

    def test_all_personal_fields(self):
        events = self.make_historydb_events(
            {
                'info.country': 'UA',
                'info.firstname': 'Василий',
                'info.lastname': 'Петрович',
                'info.birthday': '1987-08-12',
                'info.city': 'Киев',
                'info.tz': 'Europe/Moscow',
                'info.display_name': 'Display Name',
                'info.sex': '1',
                'info.lang': 'en',  # пропускаем это поле, оно нам не интересно
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'personal_data',
                    'country': 'UA',
                    'firstname': u'Василий',
                    'lastname': u'Петрович',
                    'city': u'Киев',
                    'birthday': '1987-08-12',
                    'sex': '1',
                    'display_name': 'Display Name',
                    'display_name_format': 'unknown',
                    'tz': 'Europe/Moscow',
                    'changed_fields': sorted([
                        'country',
                        'firstname',
                        'lastname',
                        'birthday',
                        'city',
                        'tz',
                        'display_name',
                        'sex',
                    ]),
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'personal_data')

    def test_parse_display_name_social(self):
        events = self.make_historydb_events(
            {
                'info.display_name': u's:102600:tw:ЛСДУ3 ЙФЯУ9',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'personal_data',
                    'display_name': u'ЛСДУ3 ЙФЯУ9',
                    'display_name_format': 'social',
                    'changed_fields': ['display_name'],
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'personal_data')

    def test_parse_display_name_template(self):
        events = self.make_historydb_events(
            {
                'info.display_name': 't:%pdd_username%@%pdd_domain%',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'personal_data',
                    'display_name': '%pdd_username%@%pdd_domain%',
                    'display_name_format': 'template',
                    'changed_fields': ['display_name'],
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'personal_data')

    def test_parse_display_name_bad_prefix(self):
        events = self.make_historydb_events(
            {
                'info.display_name': u'bad_prefix:ЛСДУ3 ЙФЯУ9',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'personal_data',
                    'display_name': u'bad_prefix:ЛСДУ3 ЙФЯУ9',
                    'display_name_format': 'unknown',
                    'changed_fields': ['display_name'],
                },
            ],
        )

    def test_parse_complete_pdd(self):
        """При дорегистрации ПДД-пользователя ему проставляются персональные данные."""
        events = self.make_historydb_events(
            {
                'action': 'complete_pdd',
                'info.glogout': '1467204322',
                'info.password': '$1$v6MPXuvB$lAG928p/S/x5c080ToOAw.',
                'info.password_quality': '65',
                'info.password_update_time': '1467204322',
                'info.birthday': '2001-12-09',
                'info.country': 'us',
                'info.firstname': 'Test',
                'info.hinta': 'asdf',
                'info.hintq': u"12:Your favorite musician's surname",
                'info.lang': 'en',  # пропускаем это поле, оно нам не интересно
                'info.lastname': 'Test',
                'info.sex': '1',
                'sid.add': '102',
                'sid.rm': '100|yandex-team.passchangepdd@xaker.ru',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'personal_data')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'personal_data',
                    'firstname': 'Test',
                    'lastname': 'Test',
                    'sex': '1',
                    'country': 'us',
                    'birthday': '2001-12-09',
                    'changed_fields': sorted(
                        [
                            'firstname',
                            'lastname',
                            'sex',
                            'country',
                            'birthday',
                        ],
                    ),
                },
                {
                    'type': 'questions_change',
                },
            ],
        )
