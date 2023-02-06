# -*- coding: utf-8 -*-

from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
)
from passport.backend.core.historydb.events import (
    ACTION_ACCOUNT_CREATE_PREFIX,
    EVENT_ACTION,
    EVENT_APP_KEY_INFO,
    EVENT_INFO_BIRTHDAY,
    EVENT_INFO_FIRSTNAME,
    EVENT_INFO_HINTA,
    EVENT_INFO_HINTQ,
    EVENT_INFO_LASTNAME,
    EVENT_INFO_PASSWORD,
    EVENT_USER_AGENT,
    EVENT_USERINFO_FT,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_IP,
    TEST_IP_2,
    TEST_USER_AGENT,
    TEST_USER_AGENT_2,
    TEST_VALUE,
    TEST_YANDEXUID,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class SimpleEventsAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_simple_info_events(self):
        response = []
        for event_name in (EVENT_INFO_FIRSTNAME, EVENT_INFO_LASTNAME, EVENT_INFO_HINTA):
            response.extend([
                event_item(name=event_name, value=TEST_VALUE),
                event_item(name=event_name, value=''),  # пустые значения
                event_item(name=event_name, value=TEST_VALUE),  # повторные значения не игнорируются
                event_item(name=event_name, value=None),  # нет поля value
                event_item(name=event_name, value=event_name),
            ])

        info = self.load_and_analyze_events(names=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            firstnames=[TEST_VALUE, TEST_VALUE, 'info.firstname'],
            lastnames=[TEST_VALUE, TEST_VALUE, 'info.lastname'],
            answers=[TEST_VALUE, TEST_VALUE, EVENT_INFO_HINTA],
        )

    def test_simple_info_with_registration_events_repair(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta='A', timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=1.2),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTA, value='A', timestamp=1.8),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
        ]
        info = self.load_and_analyze_events(names=True, answers=True, questions=True, events=response)
        self.assert_events_info_ok(
            info,
            firstnames=['A'],
            lastnames=['B'],
            questions=['99:Q', '99:Q2'],
            answers=['A'],
        )

    def test_userinfo_ft_events(self):
        response = []
        for field in ('firstname', 'lastname', 'hintq', 'hinta'):
            response.extend([
                event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, **{field: None}),
                event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, **{field: ''}),
                event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, **{field: TEST_VALUE}),
                event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, **{field: TEST_VALUE}),
                event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, **{field: field}),
            ])

        info = self.load_and_analyze_events(names=True, questions=True, answers=True, events=response)
        self.assert_events_info_ok(
            info,
            firstnames=[TEST_VALUE, TEST_VALUE, 'firstname'],
            lastnames=[TEST_VALUE, TEST_VALUE, 'lastname'],
            questions=[TEST_VALUE, TEST_VALUE, 'hintq'],
            answers=[TEST_VALUE, TEST_VALUE, 'hinta'],
        )

    def test_info_hintq_events(self):
        response = [
            event_item(hintq='2:abcd', name=EVENT_USERINFO_FT, timestamp=1),
            event_item(name=EVENT_INFO_HINTQ, value='1:abcd', timestamp=3),
            event_item(name=EVENT_INFO_HINTQ, value='1:abcd', timestamp=4),
            event_item(name=EVENT_INFO_HINTQ, value=u'0:не выбран', timestamp=5),
        ]

        info = self.load_and_analyze_events(questions=True, events=response)
        self.assert_events_info_ok(
            info,
            questions=['2:abcd', '1:abcd', '1:abcd', u'0:не выбран'],
        )

    def test_info_password_events(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, timestamp=1),
            event_item(name=EVENT_INFO_PASSWORD, value='*', timestamp=2),
            event_item(name=EVENT_INFO_PASSWORD, value='', timestamp=3),
            event_item(name=EVENT_INFO_PASSWORD, value='1:abcd', timestamp=4),
        ]

        info = self.load_and_analyze_events(password_hashes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_hashes=['*', '1:abcd'],
        )

    def test_app_key_info_events(self):
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta='A', timestamp=1),
            event_item(name=EVENT_APP_KEY_INFO, value='json1', timestamp=1.2),
            event_item(name=EVENT_APP_KEY_INFO, value='json2', timestamp=1.3),
            event_item(name=EVENT_APP_KEY_INFO, value='json1', timestamp=2.0),
        ]
        info = self.load_and_analyze_events(app_key_info=True, events=response)
        self.assert_events_info_ok(
            info,
            app_key_info=['json1', 'json2', 'json1'],
        )


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class BirthdayAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_info_birthday_events(self):
        response = [
            event_item(name=EVENT_INFO_BIRTHDAY, value='2010-10-10', timestamp=1, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_BIRTHDAY, value='2011-11-11', timestamp=2, user_ip=TEST_IP_2),
            # ручное удаление ДР
            event_item(name=EVENT_INFO_BIRTHDAY, value=None, timestamp=3, user_ip=TEST_IP_2),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT, timestamp=4, user_ip=TEST_IP),
            event_item(name=EVENT_ACTION, value='action', timestamp=4, yandexuid=TEST_YANDEXUID, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_BIRTHDAY, value='2010-10-10', timestamp=4, user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(birthdays=True, events=response)
        self.assert_events_info_ok(
            info,
            birthdays=[
                {
                    'value': '2010-10-10',
                    'interval': {
                        'start': events_info_interval_point(),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                    },
                },
                {
                    'value': '2011-11-11',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3),
                    },
                },
                {
                    'value': '2010-10-10',
                    'interval': {
                        'start': events_info_interval_point(
                            user_ip=TEST_IP,
                            timestamp=4,
                            user_agent=TEST_USER_AGENT,
                            yandexuid=TEST_YANDEXUID,
                        ),
                        'end': None,
                    },
                },
            ],
        )

    def test_info_birthday_events_with_last_delete(self):
        """Проверим работу в случае отсутствия текущего ДР из-за его удаления"""
        response = [
            event_item(name=EVENT_INFO_BIRTHDAY, value='2010-10-10', timestamp=1, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_BIRTHDAY, value='2011-11-11', timestamp=2, user_ip=TEST_IP_2),
            # ручное удаление ДР
            event_item(name=EVENT_INFO_BIRTHDAY, value=None, timestamp=3, user_ip=TEST_IP_2),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT, timestamp=3, user_ip=TEST_IP_2),
        ]

        info = self.load_and_analyze_events(birthdays=True, events=response)
        self.assert_events_info_ok(
            info,
            birthdays=[
                {
                    'value': '2010-10-10',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                    },
                },
                {
                    'value': '2011-11-11',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3, user_agent=TEST_USER_AGENT),
                    },
                },
            ],
        )

    def test_info_birthday_events_bad_order(self):
        """Дважды событие удаления ДР"""
        response = [
            event_item(name=EVENT_INFO_BIRTHDAY, value='2010-10-10', timestamp=1, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_BIRTHDAY, value=None, timestamp=2, user_ip=TEST_IP),
            event_item(name=EVENT_INFO_BIRTHDAY, value=None, timestamp=3, user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(birthdays=True, events=response)
        self.assert_events_info_ok(
            info,
            birthdays=[
                {
                    'value': '2010-10-10',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': events_info_interval_point(timestamp=2),
                    },
                },
            ],
        )

    def test_info_birthday_events_bad_value(self):
        """Игнорируем значения, не являющиеся валидными ДР"""
        response = [
            event_item(name=EVENT_INFO_BIRTHDAY, value='x'),
            event_item(name=EVENT_INFO_BIRTHDAY, value=u'1234-5'),
        ]

        info = self.load_and_analyze_events(birthdays=True, events=response)
        self.assert_events_info_ok(info)

    def test_info_birthday_events_missing_origin_info(self):
        """Не хватает информации об источнике изменений"""
        response = [
            event_item(name=EVENT_INFO_BIRTHDAY, value='2010-10-10', timestamp=1, user_ip=None, yandexuid=None),
            event_item(name=EVENT_INFO_BIRTHDAY, value=None, timestamp=2, user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(birthdays=True, events=response)
        self.assert_events_info_ok(
            info,
            birthdays=[
                {
                    'value': '2010-10-10',
                    'interval': {
                        'start': events_info_interval_point(timestamp=1, user_ip=None, yandexuid=None),
                        'end': events_info_interval_point(timestamp=2),
                    },
                },
            ],
        )


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class NamesAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_grouped_names_no_events(self):
        response = []

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[],
        )

    def test_grouped_names_single_event(self):
        response = [
            event_item(firstname=u'вася', name=EVENT_USERINFO_FT, user_ip=TEST_IP, timestamp=1),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(),
                        'end': None,
                    },
                },
            ],
        )

    def test_grouped_names_with_user_agent_event(self):
        response = [
            event_item(value=TEST_USER_AGENT, name=EVENT_USER_AGENT, timestamp=1),
            event_item(value=u'вася', name=EVENT_INFO_FIRSTNAME, user_ip=TEST_IP, timestamp=1),
            event_item(
                value=ACTION_ACCOUNT_CREATE_PREFIX,
                name=EVENT_ACTION,
                timestamp=1,
                yandexuid=TEST_YANDEXUID,
                user_ip=TEST_IP,
            ),
            event_item(value=u'pupkin', name=EVENT_INFO_LASTNAME, user_ip=TEST_IP, timestamp=2),
            event_item(value=TEST_USER_AGENT_2, name=EVENT_USER_AGENT, timestamp=2),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(
                            timestamp=1,
                            user_agent=TEST_USER_AGENT,
                            yandexuid=TEST_YANDEXUID,
                        ),
                        'end': events_info_interval_point(timestamp=2, user_agent=TEST_USER_AGENT_2),
                    },
                },
                {
                    'firstname': u'вася',
                    'lastname': u'pupkin',
                    'interval': {
                        'start': events_info_interval_point(timestamp=2, user_agent=TEST_USER_AGENT_2),
                        'end': None,
                    },
                },
            ],
        )

    def test_grouped_names_multiple_events_name_not_filled(self):
        response = [
            event_item(firstname=u'вася', name=EVENT_USERINFO_FT, user_ip=TEST_IP, timestamp=1),
            event_item(value=u'vasia', name=EVENT_INFO_FIRSTNAME, user_ip=TEST_IP, timestamp=3),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': events_info_interval_point(timestamp=3),
                    },
                },
                {
                    'firstname': u'vasia',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(timestamp=3),
                        'end': None,
                    },
                },
            ],
        )

    def test_grouped_names_multiple_events_registration_repaired(self):
        response = [
            event_item(firstname=u'вася', name=EVENT_USERINFO_FT, user_ip=TEST_IP, timestamp=1),
            event_item(value=u'вася', name=EVENT_INFO_FIRSTNAME, user_ip=TEST_IP, timestamp=1.1),
            event_item(value=u'hash', name=EVENT_INFO_PASSWORD, user_ip=TEST_IP, timestamp=1.1),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(timestamp=1),
                        'end': None,
                    },
                },
            ],
        )

    def test_grouped_names_multiple_events_names_filled(self):
        response = [
            event_item(firstname=u'вася', lastname=u'пупкин', name=EVENT_USERINFO_FT, user_ip=TEST_IP, timestamp=1),
            event_item(value=u'vasia', name=EVENT_INFO_FIRSTNAME, user_ip=TEST_IP, timestamp=3),
            event_item(value=u'pupkin', name=EVENT_INFO_LASTNAME, user_ip=TEST_IP, timestamp=4),
            event_item(value=u'маша', name=EVENT_INFO_FIRSTNAME, user_ip=TEST_IP_2, timestamp=5),
            event_item(value=TEST_USER_AGENT, name=EVENT_USER_AGENT, user_ip=TEST_IP_2, timestamp=5),
            event_item(value=u'иванова', name=EVENT_INFO_LASTNAME, user_ip=TEST_IP_2, timestamp=5),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': u'пупкин',
                    'interval': {
                        'start': events_info_interval_point(),
                        'end': events_info_interval_point(timestamp=3),
                    },
                },
                {
                    'firstname': u'vasia',
                    'lastname': u'пупкин',
                    'interval': {
                        'start': events_info_interval_point(timestamp=3),
                        'end': events_info_interval_point(timestamp=4),
                    },
                },
                {
                    'firstname': u'vasia',
                    'lastname': u'pupkin',
                    'interval': {
                        'start': events_info_interval_point(timestamp=4),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5, user_agent=TEST_USER_AGENT),
                    },
                },
                {
                    'firstname': u'маша',
                    'lastname': u'иванова',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5, user_agent=TEST_USER_AGENT),
                        'end': None,
                    },
                },
            ],
        )

    def test_grouped_names_with_missing_origin_info(self):
        response = [
            event_item(firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1, user_ip=None),
            event_item(value=u'vasia', name=EVENT_INFO_FIRSTNAME, timestamp=3, user_ip=None, yandexuid=None),
        ]

        info = self.load_and_analyze_events(grouped_names=True, events=response)
        self.assert_events_info_ok(
            info,
            names=[
                {
                    'firstname': u'вася',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(user_ip=None, timestamp=1),
                        'end': events_info_interval_point(user_ip=None, timestamp=3, yandexuid=None),
                    },
                },
                {
                    'firstname': u'vasia',
                    'lastname': None,
                    'interval': {
                        'start': events_info_interval_point(user_ip=None, timestamp=3, yandexuid=None),
                        'end': None,
                    },
                },
            ],
        )
