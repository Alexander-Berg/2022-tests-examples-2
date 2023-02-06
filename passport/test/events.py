# -*- coding: utf-8 -*-

from contextlib import contextmanager
from datetime import (
    datetime,
    timedelta,
)
from functools import partial
import re

import mock
from nose.tools import (
    assert_in,
    eq_,
    ok_,
)
from passport.backend.core.builders.historydb_api.faker import historydb_api
from passport.backend.core.historydb.account_history.account_history import AccountHistory
from passport.backend.core.historydb.converter import (
    EventEntryConverter,
    EventEntryTskvConverter,
)
from passport.backend.core.historydb.entry import (
    EventEntry,
    EventTskvEntry,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    single_entrant_patch,
)
from passport.backend.core.undefined import Undefined
from passport.backend.utils.time import (
    datetime_to_unixtime,
    switch_datetime_tz,
)
import pytz
from six import iteritems


_RFC_TIME_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2}).(\d{2}):(\d{2}):(\d{2})\.(\d{6})(?P<offset_sign>[+-])(?P<offset_hour>\d{2})$')


@single_entrant_patch
class EventLoggerFaker(object):
    def __init__(self):
        self._logger = mock.Mock(name='event_logger')
        self._handler = mock.Mock(name='event_log_handler')
        self._logger.debug = self._handler
        self._patch = mock.patch('passport.backend.core.serializers.logs.historydb.runner.event_log', self._logger)

    def assert_events_are_logged(self, names_values, in_order=False):
        """
        Проверит что только эти event-записи передавались в логгер.

        Входные параметры:
            names_values
                Словарь в котором каждый элемент это запись (можно задать
                только name и value).
                Или список словарей в котором каждый словарь это запись (можно
                задать name, value, uid,  action, comment).
            in_order
                Учитывать порядок
        """
        if not in_order and not isinstance(names_values, dict):
            all_records_have_not_uid = all(u'uid' not in r for r in names_values)
            all_records_have_uid = all(u'uid' in r for r in names_values)
            ok_(
                # Если указать uid только у части записей, то будет построен
                # например такой список [uid1, ANY], т.к. перед сравнением
                # мы сортируем списки, то невозможно заранее сказать в каком
                # порядке окажутся его элементы.
                all_records_have_not_uid or all_records_have_uid,
                u'Укажите uid у всех записей или не указывайте совсем',
            )

        actual_events = self._build_actual_events()
        if isinstance(names_values, dict):
            names_values = self._events_dict_to_events_list(names_values)
        expected_events = self._build_expected_events(names_values)

        if not in_order:
            actual_events = sorted(actual_events)
            expected_events = sorted(expected_events)
        iterdiff(eq_)(actual_events, expected_events)

    def assert_events_are_logged_with_order(self, names_values):
        """
        Проверит, что логгер вызывался со всеми переданными записями
        в указанном порядке.
        """
        self.assert_events_are_logged(names_values, in_order=True)

    def assert_event_is_logged(self, name, value):
        """
        Проверит что в логгер передавалась запись с указанным именем и значением.
        Без внимания к порядку передачи этой записи логгеру
        """
        events = self._build_actual_events()
        expected_event = (mock.ANY, name, value, mock.ANY, mock.ANY)
        assert_in(expected_event, events)

    def assert_contains(self, events):
        actual_events = self._build_actual_events()

        if isinstance(events, dict):
            events = self._events_dict_to_events_list(events)
        expected_events = self._build_expected_events(events)

        extra_events = []
        for event in expected_events:
            if event not in actual_events:
                extra_events.append(event)

        ok_(not extra_events, 'Items not found: %r ------------ %r' % (extra_events, actual_events))

    @property
    def events(self):
        events = []
        event_keys = set()
        for call_args in self._handler.call_args_list:
            args = call_args[0][0]
            log_field = partial(self._get_log_field, converter_cls=EventEntryConverter, log_msg=args)

            uid = log_field('uid')
            name = log_field('name')
            time = _parse_rfc_time(log_field('time'))
            event_key = (time, uid, name)
            if event_key not in event_keys:
                event_keys.add(event_key)
                events.append(
                    EventEntry(
                        uid=uid,
                        name=name,
                        value=log_field('value'),
                        admin=log_field('admin'),
                        comment=log_field('comment'),
                        time=time,
                        yandexuid=log_field('yandexuid'),
                        user_ip=log_field('ip_from'),
                        client_name=log_field('client_name'),
                    ),
                )
        return events

    def events_api_response(self, as_list='13238', geo_id='9999'):
        events = self.events
        response = []
        for event in events:
            api_event = historydb_api.event_item(
                client_name=event.client_name,
                host_id=event.host_id,
                name=event.name,
                value=event.value if event.value != '-' else None,
                timestamp=datetime_to_unixtime(event.time),
                user_ip=event.user_ip,
                ip_as_list=as_list,
                ip_geoid=str(geo_id),
            )
            response.append(api_event)
        return response

    def parse_events(self, as_list='13238', geo_id='9999'):
        account_history = AccountHistory(uid=123)
        groupped_events = list(account_history._group_events(self.events_api_response(as_list=as_list, geo_id=geo_id)))
        parsed_events = []
        for event in groupped_events:
            parsed_event = account_history._parse_event(event)
            if parsed_event:
                parsed_events.append(parsed_event)
        return parsed_events

    def _build_actual_events(self):
        return [(e.uid, e.name, e.value, e.admin, e.comment) for e in self.events]

    def _build_expected_events(self, names_values):
        expected_events = []
        for rec in names_values:
            expected_events.append((
                rec.get('uid', mock.ANY),
                rec['name'],
                rec['value'],
                rec.get('admin', '-'),
                rec.get('comment', '-'),
            ))
        return expected_events

    def _get_log_field(self, field_name, converter_cls, log_msg=''):
        # Получаем имена полей и соответствующие им значения для данного типа
        # записи.
        field_names = converter_cls.fields
        field_values = re.findall(r'(`.*?`|[^ ]+)', log_msg)

        for name, value in zip(field_names, field_values):
            if name == field_name:
                return value.strip('`')

    def _events_dict_to_events_list(self, events_dict):
        # В записи со значением поля name = action можно дополнительно
        # определить значения полей admin и comment, для это в словаре нужно
        # задать эти ключи и их значения.
        if 'action' in events_dict:
            action_admin = events_dict.pop('admin', '-')
            action_comment = events_dict.pop('comment', '-')
        events_list = []
        for name, value in iteritems(events_dict):
            event = {'name': name, 'value': value}
            if name == 'action':
                event['admin'] = action_admin
                event['comment'] = action_comment
            events_list.append(event)
        return events_list

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()


class EventCompositor(object):
    def __init__(self, prefix=None, uid=None):
        self._lines = list()

        # Общий префикс для всех названий событий
        self._prefix = prefix

        self._uid = uid

    def add_line(self, name, value):
        if self._prefix:
            name = self._prefix + name

        line = dict(
            name=name,
            value=value,
        )

        if self._uid is not None:
            line.update(uid=self._uid)

        self._lines.append(line)
        return self

    __call__ = add_line

    @contextmanager
    def context(self, prefix=None, uid=Undefined):
        old_prefix = self._prefix
        old_uid = self._uid

        if prefix:
            self._prefix = prefix if self._prefix is None else self._prefix + prefix

        if uid is not Undefined:
            self._uid = uid

        yield

        self._prefix = old_prefix
        self._uid = old_uid

    def to_lines(self):
        return self._lines

    def prefix(self, prefix):
        return self.context(prefix=prefix)

    def uid(self, uid):
        return self.context(uid=uid)

    def add_dict(self, events):
        for key in events:
            value = events[key]
            if isinstance(value, dict):
                with self.prefix(key):
                    self.add_dict(value)
            else:
                self.add_line(key, value)
        return self


def _parse_rfc_time(datetime_string):
    """
    Преобразует время из формы RFC 3339 в объект datetime в московском часовом
    поясе.

    Формат: 2012-06-05T12:33:58.407453+04

    Возвращается нативный объект datetime.
    """
    match = _RFC_TIME_RE.match(datetime_string)
    offset_hour = int(match.group('offset_hour'))
    if match.group('offset_sign') == '+':
        offset_hour = -offset_hour

    utc_time = datetime(*map(int, match.groups()[:-2])) + timedelta(hours=offset_hour)
    utc_time = pytz.utc.localize(utc_time)
    local_time = switch_datetime_tz(utc_time, pytz.timezone('Europe/Moscow'))

    # По всему Паспорту используются наивные объекты datetime
    return local_time.replace(tzinfo=None)


@single_entrant_patch
class EventLoggerTskvFaker(object):
    def __init__(self):
        self._logger = mock.Mock(name='event_logger')
        self._handler = mock.Mock(name='event_log_handler')
        self._logger.debug = self._handler
        self._patch = mock.patch('passport.backend.core.serializers.logs.historydb.runner.event_tskv_log', self._logger)

    def assert_events_are_logged(self, names_values, in_order=False):
        """
        Проверит что только эти event-записи передавались в логгер.

        Входные параметры:
            names_values
                Словарь в котором каждый элемент это запись (можно задать
                только name и value).
                Или список словарей в котором каждый словарь это запись (можно
                задать name, value, uid,  action, comment).
            in_order
                Учитывать порядок
        """
        if not in_order and not isinstance(names_values, dict):
            all_records_have_not_uid = all(u'uid' not in r for r in names_values)
            all_records_have_uid = all(u'uid' in r for r in names_values)
            ok_(
                # Если указать uid только у части записей, то будет построен
                # например такой список [uid1, ANY], т.к. перед сравнением
                # мы сортируем списки, то невозможно заранее сказать в каком
                # порядке окажутся его элементы.
                all_records_have_not_uid or all_records_have_uid,
                u'Укажите uid у всех записей или не указывайте совсем',
            )
        actual_events = self._build_actual_events()
        if isinstance(names_values, dict):
            names_values = self._events_dict_to_events_list(names_values)
        expected_events = self._build_expected_events(names_values)

        iterdiff(eq_)(actual_events, expected_events)

    @property
    def events(self):
        events = []
        for call_args in self._handler.call_args_list:
            args = call_args[0][0]
            log_field = partial(self._get_log_field, log_msg=args)
            event_field = partial(self._get_event_field, converter_cls=EventEntryTskvConverter, log_msg=args)

            data = dict()

            for field_name in EventEntryTskvConverter.fields:
                field_data = log_field(field_name)
                if field_data is not None:
                    data[field_name] = field_data
            events.append(EventTskvEntry(events=event_field(), **data))
        return events

    def _build_actual_events(self):
        event_entry_list = self.events
        result = []
        for event_entry in event_entry_list:
            def __only_with_keys(d, keys):
                return {x: d[x] for x in d if x in keys}
            # Динамическое KV для event_name=event_value забираем из entry отдельным полем
            item = __only_with_keys(event_entry.data.copy(), ['uid', 'admin', 'comment'], )
            item.update(event_entry.events)
            result.append(item)

        return result

    def _build_expected_events(self, names_values):
        # В TSKV формате у атомарной операции есть серия событий которая записывается в строчку c общим uid
        # Пример: uid=3324324 info.domain_name=test-domain.ru info.domain_id=123
        # Но так же может быть залогированны две атомарные операции одна за другой и для этого они разделяются по uid
        # Пример: uid=3324324 info.domain_name=test-domain.ru
        #         uid=3324325 info.domain_id=123
        events_by_uid = dict()

        for rec in names_values:
            # Проверяем что uid передан явно
            test_uid = rec.get('uid')
            # Если передан то фиксируем его как новый если uid уже зафиксирован то ничего не делаем
            # Если uid не передан то фиксируем с ключем None и складываем все эвенты без uid туда
            item = events_by_uid.get(test_uid)
            if events_by_uid.get(test_uid) is None:
                item = dict()
                events_by_uid[test_uid] = item

            item[rec['name']] = rec['value'] if rec['value'] != '-' else ''

            admin = rec.get('admin')
            if admin is not None:
                item['admin'] = admin
            comment = rec.get('comment')
            if comment is not None:
                item['comment'] = comment

        for k, v in events_by_uid.items():
            v['uid'] = mock.ANY if k is None else k

        return list(events_by_uid.values())

    def _get_log_field(self, field_name, log_msg=''):
        data = log_msg.split('\t')
        d = dict(map(lambda x: x.split('=', 1), data))

        if field_name in d:
            return d[field_name]

    def _get_event_field(self, converter_cls, log_msg=''):
        field_names = converter_cls.fields
        data = log_msg.split('\t')
        d = dict(map(lambda x: x.split('=', 1), data))

        def __get_event(event, event_name):
            return event_name, event[event_name]
        events_name = list(set(d.keys()).difference(field_names))
        return dict(map(lambda x: __get_event(d, x), events_name))

    def _events_dict_to_events_list(self, events_dict):
        # В записи со значением поля name = action можно дополнительно
        # определить значения полей admin и comment, для это в словаре нужно
        # задать эти ключи и их значения.
        if 'action' in events_dict:
            action_admin = events_dict.pop('admin', '-')
            action_comment = events_dict.pop('comment', '-')
        events_list = []
        for name, value in iteritems(events_dict):
            event = {'name': name, 'value': value}
            if name == 'action':
                event['admin'] = action_admin
                event['comment'] = action_comment
            events_list.append(event)
        return events_list

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()
