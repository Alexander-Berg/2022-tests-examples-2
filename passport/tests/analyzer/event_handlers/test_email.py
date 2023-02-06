# -*- coding: utf-8 -*-

from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
)
from passport.backend.core.historydb.events import (
    ACTION_DELETE_ENTITIES_BY_SUPPORT_LINK_PERL,
    ACTION_DELETE_ENTITIES_BY_SUPPORT_LINK_WITH_PHONES_PERL,
    EVENT_ACTION,
    EVENT_EMAIL_CONFIRM,
    EVENT_EMAIL_DELETE,
    EVENT_EMAIL_RPOP,
    EVENT_INFO_FLUSHED_ENTITIES,
    EVENT_USER_AGENT,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_IP,
    TEST_IP_2,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class EmailAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_confirmed_email_old_events(self):
        response = [
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 12345678', user_ip=TEST_IP, timestamp=1),
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_3@ya.ru 12345678', user_ip=TEST_IP_2, timestamp=2),
            event_item(name=EVENT_EMAIL_RPOP, value=u'ва@силий@xn--80atjc.xn--p1ai added', user_ip=TEST_IP_2, timestamp=3),
            event_item(name=EVENT_EMAIL_DELETE, value=u'email_2@ya.ru', user_ip=TEST_IP_2, timestamp=4),
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'ва@силий@xn--80atjc.xn--p1ai 12345678', user_ip=TEST_IP_2, timestamp=5),
            event_item(name=EVENT_EMAIL_RPOP, value=u'email_5@.рф added', user_ip=TEST_IP, timestamp=6),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=4),
                        },
                    ],
                },
                {
                    'value': u'email_3@ya.ru',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2), 'end': None}],
                },
                {
                    'value': u'ва@силий@xn--80atjc.xn--p1ai',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3), 'end': None}],
                },
                {
                    'value': u'email_5@.рф',
                    'intervals': [{'start': events_info_interval_point(timestamp=6), 'end': None}],
                },
            ],
        )

    def test_confirmed_email_multiple_interval_old_events(self):
        response = [
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 12345678', user_ip=TEST_IP, timestamp=1),
            event_item(name=EVENT_EMAIL_DELETE, value=u'email_2@ya.ru', user_ip=TEST_IP_2, timestamp=4),
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 444', user_ip=TEST_IP, timestamp=5),
            event_item(name=EVENT_EMAIL_RPOP, value=u'email_2@ya.ru added', user_ip=TEST_IP, timestamp=5),
            # новое событие подтверждения, при удалении сборщика не была записано информация об удалении
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 555', user_ip=TEST_IP, timestamp=6),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=4),
                        },
                        {
                            'start': events_info_interval_point(timestamp=5),
                            'end': None,
                        },
                    ],
                },
            ],
        )

    def test_confirmed_email_unexpected_events(self):
        response = [
            event_item(name=EVENT_EMAIL_DELETE, value=u'email_2@ya.ru', user_ip=TEST_IP_2, timestamp=4),
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 444', user_ip=TEST_IP, timestamp=5),
            event_item(name=EVENT_EMAIL_DELETE, value=u'email_2@ya.ru', user_ip=TEST_IP_2, timestamp=6),
            event_item(name=EVENT_EMAIL_DELETE, value=u'email_2@ya.ru', user_ip=TEST_IP_2, timestamp=7),
            event_item(name=EVENT_EMAIL_DELETE, value=None, user_ip=TEST_IP_2, timestamp=8),
            # Событие в новом валидаторе, без записи значения адреса
            event_item(name='email.1', value='deleted', user_ip=TEST_IP, timestamp=9),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=5),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=6),
                        },
                    ],
                },
            ],
        )

    def test_confirmed_email_old_to_new_events_transition(self):
        response = [
            event_item(name=EVENT_EMAIL_CONFIRM, value=u'email_2@ya.ru 12345678', user_ip=TEST_IP, timestamp=1),
            event_item(name='email.1', value='deleted', user_ip=TEST_IP_2, timestamp=20),
            event_item(name='email.1.address', value='email_2@ya.ru', user_ip=TEST_IP, timestamp=20),
            event_item(name=EVENT_ACTION, value='email_deleted', user_ip=TEST_IP_2, timestamp=20),
            event_item(name=EVENT_USER_AGENT, value='curl', user_ip=TEST_IP_2, timestamp=20),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=1),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=20, user_agent='curl'),
                        },
                    ],
                },
            ],
        )

    def test_confirmed_email_new_events_multiple_intervals(self):
        response = [
            event_item(name='email.1', value='created', user_ip=TEST_IP, timestamp=10),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP, timestamp=10),
            event_item(name='email.1.is_unsafe', value='0', user_ip=TEST_IP, timestamp=10),
            event_item(name='email.1.created_at', value='10', user_ip=TEST_IP, timestamp=10),
            event_item(name='email.1.confirmed_at', value='20', user_ip=TEST_IP_2, timestamp=20),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=20),
            # Признак подтвержденности сбрасывается
            event_item(name='email.1.confirmed_at', value='', user_ip=TEST_IP_2, timestamp=30),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=30),
            event_item(name='email.1.confirmed_at', value='40', user_ip=TEST_IP_2, timestamp=40),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=40),
            event_item(name='email.1', value='deleted', user_ip=TEST_IP_2, timestamp=50),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=50),
            # Тот же адрес привязывается заново с другим ID
            event_item(name='email.2', value='created', user_ip=TEST_IP, timestamp=60),
            event_item(name='email.2.address', value='email_1@ya.ru', user_ip=TEST_IP, timestamp=60),
            event_item(name='email.2.created_at', value='60', user_ip=TEST_IP, timestamp=60),
            event_item(name='email.2.confirmed_at', value='70', user_ip=TEST_IP_2, timestamp=70),
            event_item(name='email.2.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=70),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_1@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=20, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=30, user_ip=TEST_IP_2),
                        },
                        {
                            'start': events_info_interval_point(timestamp=40, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=50, user_ip=TEST_IP_2),
                        },
                        {
                            'start': events_info_interval_point(timestamp=70, user_ip=TEST_IP_2),
                            'end': None,
                        },
                    ],
                },
            ],
        )

    def test_confirmed_email_global_delete_cases(self):
        response = [
            event_item(name='email.1.confirmed_at', value='20', user_ip=TEST_IP_2, timestamp=20),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=20),
            event_item(name='email.2.confirmed_at', value='30', user_ip=TEST_IP_2, timestamp=30),
            event_item(name='email.2.address', value='email_2@ya.ru', user_ip=TEST_IP_2, timestamp=30),
            # Отдельное событие удаление всего
            event_item(name=EVENT_ACTION, value=ACTION_DELETE_ENTITIES_BY_SUPPORT_LINK_PERL, timestamp=40, user_ip=TEST_IP_2),
            # Отдельное событие удаление всего - при условии что адресов нет
            event_item(name=EVENT_ACTION, value=ACTION_DELETE_ENTITIES_BY_SUPPORT_LINK_WITH_PHONES_PERL, timestamp=50, user_ip=TEST_IP_2),
            event_item(name='email.1.confirmed_at', value='60', user_ip=TEST_IP_2, timestamp=60),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=60),
            # Глобальное удаление, не относящееся к email-ам
            event_item(name=EVENT_INFO_FLUSHED_ENTITIES, value='phones,social_profiles', timestamp=65, user_ip=TEST_IP_2),
            event_item(name='email.2.confirmed_at', value='70', user_ip=TEST_IP_2, timestamp=70),
            event_item(name='email.2.address', value='email_2@ya.ru', user_ip=TEST_IP_2, timestamp=70),

            # Глобальное удаление вместе с записью событий удаления
            event_item(name=EVENT_INFO_FLUSHED_ENTITIES, value='emails,phones,social_profiles', timestamp=80, user_ip=TEST_IP_2),
            event_item(name='email.1', value='deleted', user_ip=TEST_IP_2, timestamp=80),
            event_item(name='email.1.address', value='email_1@ya.ru', user_ip=TEST_IP_2, timestamp=80),
            event_item(name='email.2', value='deleted', user_ip=TEST_IP_2, timestamp=80),
            event_item(name='email.2.address', value='email_2@ya.ru', user_ip=TEST_IP_2, timestamp=80),
        ]

        info = self.load_and_analyze_events(confirmed_emails=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_emails=[
                {
                    'value': u'email_1@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=20, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=40, user_ip=TEST_IP_2),
                        },
                        {
                            'start': events_info_interval_point(timestamp=60, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=80, user_ip=TEST_IP_2),
                        },
                    ],
                },
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [
                        {
                            'start': events_info_interval_point(timestamp=30, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=40, user_ip=TEST_IP_2),
                        },
                        {
                            'start': events_info_interval_point(timestamp=70, user_ip=TEST_IP_2),
                            'end': events_info_interval_point(timestamp=80, user_ip=TEST_IP_2),
                        },
                    ],
                },
            ],
        )
