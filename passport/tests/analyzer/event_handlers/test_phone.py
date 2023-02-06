# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    phone_event_item,
)
from passport.backend.core.historydb.analyzer.event_handlers.phone import flatten_phones_mapping
from passport.backend.core.historydb.events import (
    EVENT_ACTION,
    EVENT_OLD_YASMS_PHONE_ACTION,
    EVENT_OLD_YASMS_PHONE_NUMBER,
    EVENT_OLD_YASMS_PHONE_STATUS,
    EVENT_USER_AGENT,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_IP,
    TEST_IP_2,
    TEST_USER_AGENT,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class PhoneAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_phone_events_add_and_remove_secure_phone(self):
        response = [
            # secure_phone_bind_submit
            event_item(timestamp=1, name=EVENT_ACTION, value='secure_phone_bind_submit', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.started', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.finished', value='10', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='created', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='action', value='created', user_ip=TEST_IP),
            # secure_phone_bind_commit
            event_item(timestamp=2, name=EVENT_ACTION, value='secure_phone_bind_commit', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=2, name='phone.add', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='secured', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='confirmed', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='bound', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            # secure_phone_remove_submit
            event_item(timestamp=3, name=EVENT_ACTION, value='secure_phone_remove_submit', user_ip=TEST_IP),
            event_item(timestamp=3, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.type', value='remove', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.started', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.security_identity', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.finished', value='13', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            # secure_phone_remove_commit
            event_item(timestamp=4, name=EVENT_ACTION, value='secure_phone_remove_commit', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=4, name='phone.rm', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.type', value='remove', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='action', value='deleted', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        confirmed_phones = [
            {
                'value': '79111234567',
                'intervals': [
                    {
                        'start': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=2),
                        'end': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=4),
                    },
                ],
            },
        ]
        self.assert_events_info_ok(
            info,
            confirmed_phones=confirmed_phones,
        )

    def test_phone_events_add_and_remove_multiple_phones(self):
        response = [
            # привязка первого телефона
            event_item(timestamp=2, name=EVENT_ACTION, value='secure_phone_bind_commit', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=2, name='phone.add', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='secured', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='confirmed', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='bound', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            # привязка второго телефона
            event_item(timestamp=3, name=EVENT_ACTION, value='phone_bind_commit', user_ip=TEST_IP),
            event_item(timestamp=3, name='phone.add', value='+7 922 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='operation.1.security_identity', value='79221234567', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='number', value='+79221234567', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='confirmed', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='bound', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=2, attribute='action', value='changed', user_ip=TEST_IP),
            # удаление сразу двух телефонов
            event_item(timestamp=4, name=EVENT_ACTION, value='remove_all_phones', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=4, name='phone.rm', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.type', value='remove', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=2, attribute='operation.1.type', value='remove', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=2, attribute='operation.1.security_identity', value='79221234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=2, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=2, attribute='number', value='+79221234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=2, attribute='action', value='deleted', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        confirmed_phones = [
            {
                'value': '79111234567',
                'intervals': [
                    {
                        'start': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=2),
                        'end': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=4),
                    },
                ],
            },
            {
                'value': '79221234567',
                'intervals': [
                    {
                        'start': events_info_interval_point(timestamp=3),
                        'end': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=4),
                    },
                ],
            },
        ]
        self.assert_events_info_ok(
            info,
            confirmed_phones=confirmed_phones,
        )

    def test_phone_events_add_and_remove_by_binding_limit(self):
        response = [
            # secure_phone_bind_submit
            event_item(timestamp=1, name=EVENT_ACTION, value='secure_phone_bind_submit', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.started', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.finished', value='10', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='created', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='action', value='created', user_ip=TEST_IP),
            # secure_phone_bind_commit
            event_item(timestamp=2, name=EVENT_ACTION, value='secure_phone_bind_commit', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=2, name='phone.add', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='secured', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='confirmed', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='bound', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            # acquire_phone
            event_item(timestamp=3, name=EVENT_ACTION, value='acquire_phone', user_ip=TEST_IP),
            event_item(timestamp=3, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.type', value='mark', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.started', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.finished', value='13', user_ip=TEST_IP),
            # unbind_phone_from_account
            event_item(timestamp=4, name=EVENT_ACTION, value='unbind_phone_from_account', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='bound', value='0', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.type', value='mark', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        confirmed_phones = [
            {
                'value': '79111234567',
                'intervals': [
                    {
                        'start': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=2),
                        'end': events_info_interval_point(user_agent=TEST_USER_AGENT, timestamp=4),
                    },
                ],
            },
        ]
        self.assert_events_info_ok(
            info,
            confirmed_phones=confirmed_phones,
        )

    def test_phone_events_no_number_or_invalid_number(self):
        response = [
            # secure_phone_bind_submit
            event_item(timestamp=1, name=EVENT_ACTION, value='secure_phone_bind_submit', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.started', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.finished', value='10', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='number', value='invalid', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='created', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=1, phone_id=1, attribute='action', value='created', user_ip=TEST_IP),
            # secure_phone_bind_commit
            event_item(timestamp=2, name=EVENT_ACTION, value='secure_phone_bind_commit', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            event_item(timestamp=2, name='phone.add', value='+7 911 123-45-67', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='secured', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.type', value='bind', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='confirmed', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='bound', value='2', user_ip=TEST_IP),
            phone_event_item(timestamp=2, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            # acquire_phone
            event_item(timestamp=3, name=EVENT_ACTION, value='acquire_phone', user_ip=TEST_IP),
            event_item(timestamp=3, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.action', value='created', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.type', value='mark', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.started', value='3', user_ip=TEST_IP),
            phone_event_item(timestamp=3, phone_id=1, attribute='operation.1.finished', value='13', user_ip=TEST_IP),
            # unbind_phone_from_account
            event_item(timestamp=4, name=EVENT_ACTION, value='unbind_phone_from_account', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_USER_AGENT, value=TEST_USER_AGENT, user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='action', value='changed', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='number', value='+79111234567', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='bound', value='0', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.type', value='mark', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.security_identity', value='1', user_ip=TEST_IP),
            phone_event_item(timestamp=4, phone_id=1, attribute='operation.1.action', value='deleted', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_phones=[],
        )

    def test_phone_old_yasms_events_valid(self):
        response = [
            event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79111234567', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321'),
            event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_ACTION, value='add'),
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP_2),
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP_2),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_ACTION, value='add'),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654333'),
            event_item(timestamp=5, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP_2),
            event_item(timestamp=5, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP_2),
            event_item(timestamp=6, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
            event_item(timestamp=6, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        confirmed_phones = [
            {
                'value': '79111234567',
                'intervals': [
                    {'start': events_info_interval_point(), 'end': None},
                ],
            },
            {
                'value': '79117654321',
                'intervals': [
                    {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5),
                    },
                    {
                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                        'end': None,
                    },
                ],
            },
        ]
        self.assert_events_info_ok(
            info,
            confirmed_phones=confirmed_phones,
        )
        eq_(
            flatten_phones_mapping(confirmed_phones),
            [
                {
                    'value': '79111234567',
                    'interval': {'start': events_info_interval_point(), 'end': None},
                },
                {
                    'value': '79117654321',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=5),
                    },
                },
                {
                    'value': '79117654321',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                        'end': None,
                    },
                },
            ],
        )

    def test_phone_old_yasms_events_invalid(self):
        response = [
            event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save'),  # одинокое событие
            event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321'),  # одинокое событие
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='phone'),  # некорректное значение телефона
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid'),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete'),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='111234567'),  # некорректное значение телефона
            event_item(timestamp=5, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete'),
            event_item(timestamp=5, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321'),  # удаление неизвестного номера
            event_item(timestamp=6, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save'),
            event_item(timestamp=6, name=EVENT_OLD_YASMS_PHONE_NUMBER, value=None),  # отсутствующее значение телефона
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_phones=[],
        )
        eq_(
            flatten_phones_mapping([]),
            [],
        )

    def test_phone_old_yasms_events_duplicates(self):
        response = [
            event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_ACTION, value='save', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
            event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP_2),
            event_item(timestamp=2, name=EVENT_OLD_YASMS_PHONE_STATUS, value='valid', user_ip=TEST_IP_2),
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP_2),
            event_item(timestamp=3, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP_2),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_ACTION, value='delete', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_OLD_YASMS_PHONE_NUMBER, value='+79117654321', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(confirmed_phones=True, events=response)
        self.assert_events_info_ok(
            info,
            confirmed_phones=[
                {
                    'value': '79117654321',
                    'intervals': [
                        {
                            'start': events_info_interval_point(),
                            'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=3),
                        },
                    ],
                },
            ],
        )
