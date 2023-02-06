# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
    events_response,
    FakeHistoryDBApi,
)
from passport.backend.core.historydb.analyzer.events import (
    _repair_registration_events,
    DEFAULT_FROM_UNIXTIME,
    EVENTS_INFO_FIELDS,
    EventsAnalyzer,
)
from passport.backend.core.historydb.events import (
    ACTION_ACCOUNT_REGISTER_PREFIX,
    EVENT_ACTION,
    EVENT_INFO_BIRTHDAY,
    EVENT_INFO_FIRSTNAME,
    EVENT_INFO_HINTA,
    EVENT_INFO_HINTQ,
    EVENT_INFO_LASTNAME,
    EVENT_INFO_PASSWORD,
    EVENT_USER_AGENT,
    EVENT_USERINFO_FT,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .data import (
    TEST_DEFAULT_REGISTRATION_DATETIME,
    TEST_DEFAULT_REGISTRATION_TIMESTAMP,
    TEST_HISTORYDB_API_URL,
    TEST_IP,
    TEST_USER_AGENT,
    TranslationSettings,
)


class BaseEventsAnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_historydb = FakeHistoryDBApi()
        self.fake_historydb.start()
        self.fake_historydb.set_response_value('events', events_response(events=[]))
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(dbfields={'userinfo.reg_date.uid': TEST_DEFAULT_REGISTRATION_DATETIME}),
            ),
        )

    def tearDown(self):
        self.fake_historydb.stop()
        del self.fake_historydb

    def load_and_analyze_events(self, events=None, language=None, **kwargs):
        self.fake_historydb.set_response_value('events', events_response(events=events))
        return EventsAnalyzer(**kwargs).load_and_analyze_events(self.account, language=language)

    def assert_historydb_api_events_called(self, event_names, from_ts=TEST_DEFAULT_REGISTRATION_TIMESTAMP, **kwargs):
        eq_(len(self.fake_historydb.requests), 1)
        events_request = self.fake_historydb.requests[0]
        events_request.assert_url_starts_with('%s2/events/' % TEST_HISTORYDB_API_URL)
        events_request.assert_query_contains({
            'order_by': 'asc',
            'from_ts': str(from_ts),
            'to_ts': TimeNow(),
        })
        query = events_request.get_query_params()
        ok_('name' in query)
        eq_(sorted(query['name'][0].split(',')), sorted(event_names))

    def assert_events_info_ok(self, info, **params):
        for field in EVENTS_INFO_FIELDS:
            if field not in params:
                if field in ('emails', 'confirmed_emails', 'question_answer_mapping', 'registration_env'):
                    params[field] = {}
                else:
                    params[field] = []
        iterdiff(eq_)(info._asdict(), params)


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class EventsAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_with_empty_events(self):
        info = EventsAnalyzer().load_and_analyze_events(self.account)
        self.assert_events_info_ok(info)
        self.assert_historydb_api_events_called([''])

    def test_with_no_registration_datetime_on_account(self):
        analyzer = EventsAnalyzer(registration_env=True)
        response = events_response(events=[
            event_item(user_ip=TEST_IP, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT, timestamp=1.1),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя', timestamp=1.2),
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX, timestamp=1.2, user_ip=TEST_IP),
        ])
        self.fake_historydb.set_response_value('events', response)
        account = Account().parse(get_parsed_blackbox_response('userinfo', blackbox_userinfo_response()))

        info = analyzer.load_and_analyze_events(account)
        self.assert_events_info_ok(
            info,
            registration_env=events_info_interval_point(user_agent=TEST_USER_AGENT),
        )
        self.assert_historydb_api_events_called(
            [EVENT_ACTION, EVENT_USERINFO_FT, EVENT_USER_AGENT],
            from_ts=int(DEFAULT_FROM_UNIXTIME),
        )

    def test_with_limit_warning(self):
        analyzer = EventsAnalyzer(names=True, answers=True, questions=True)
        response = events_response(events=[
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta='A', timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=1.2),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTA, value='A', timestamp=1.8),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
        ])
        self.fake_historydb.set_response_value('events', response)

        info = analyzer.load_and_analyze_events(self.account, limit=10)
        self.assert_events_info_ok(
            info,
            firstnames=['A'],
            lastnames=['B'],
            questions=['99:Q', '99:Q2'],
            answers=['A'],
        )
        self.assert_historydb_api_events_called(
            [EVENT_INFO_HINTQ, EVENT_INFO_HINTA, EVENT_INFO_FIRSTNAME, EVENT_INFO_LASTNAME, EVENT_USERINFO_FT],
        )

    def test_with_uid(self):
        info = EventsAnalyzer().load_and_analyze_events(uid=self.account.uid)
        self.assert_events_info_ok(info)
        self.assert_historydb_api_events_called([''], from_ts=0)

    def test_fails_without_uid_and_account(self):
        with assert_raises(ValueError):
            EventsAnalyzer().load_and_analyze_events()

    def test_unknown_events_ignored(self):
        info = EventsAnalyzer()._analyze_events([event_item(name='unknown.event')])
        self.assert_events_info_ok(info)

    def test_unexpected_kwarg_raises_error(self):
        with assert_raises(ValueError):
            EventsAnalyzer(unexpected_kwarg=True)


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class RepairRegistrationEventsTestCase(BaseEventsAnalyzerTestCase):
    def test_repair_registration_events_nothing_to_repair(self):
        """С timestamp события userinfo_ft все в порядке"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=3.2),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=3.3),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=3.3),
            event_item(name=EVENT_INFO_HINTA, value='A2', timestamp=3.8),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=4.0),
        ]
        eq_(
            list(response),
            _repair_registration_events(response),
        )

    def test_repair_registration_events_no_userinfo_ft(self):
        """События userinfo_ft нет, ничего не нужно делать"""
        response = [
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=1.2),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=1.3),
            event_item(name=EVENT_INFO_HINTA, value='A2', timestamp=1.8),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
        ]
        eq_(
            list(response),
            _repair_registration_events(response),
        )

    def test_repair_registration_events_single_userinfo_ft_event(self):
        """Единственное событие userinfo_ft - ничего не делаем"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
        ]
        eq_(
            list(response),
            _repair_registration_events(response),
        )

    def test_repair_registration_events_personal_data_events_excluded(self):
        """Дублирующие события задания имени, фамилии, КВ, КО выбрасываются"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=2.2),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=2.3),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=2.3),
            event_item(name=EVENT_INFO_HINTA, value='A2', timestamp=2.8),  # значение отличается, запишется ворнинг
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=3.0),
        ]
        eq_(
            [
                event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
                event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=3.0),
            ],
            _repair_registration_events(response),
        )

    def test_repair_registration_events_userinfo_ft_timestamp_valid(self):
        """Округленное время userinfo_ft совпало с другими событиями"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=1.0),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=1.0),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=1.0),
            event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.0),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
        ]
        eq_(
            [
                event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
                event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1),
                event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
            ],
            _repair_registration_events(response),
        )

    def test_repair_registration_events_userinfo_ft_timestamp_valid_mixed_order(self):
        """Округленное время userinfo_ft совпало с другими событиями, userinfo_ft - не первое событие"""
        response = [
            event_item(name=EVENT_INFO_FIRSTNAME, value='A', timestamp=1.0),
            event_item(name=EVENT_INFO_LASTNAME, value='B', timestamp=1.0),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q', timestamp=1.0),
            event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.0),
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
        ]
        eq_(
            [
                event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
                event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1),
                event_item(name=EVENT_INFO_HINTQ, value='99:Q2', timestamp=2.0),
            ],
            _repair_registration_events(response),
        )

    def test_repair_registration_events_timestamp_updated(self):
        """У событий в пределах одной секунды timestamp приводится к одному значению"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.2),
            event_item(name=EVENT_INFO_BIRTHDAY, value='test', timestamp=1.3),
        ]
        eq_(
            [
                event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
                event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1),
                event_item(name=EVENT_INFO_BIRTHDAY, value='test', timestamp=1),
            ],
            _repair_registration_events(response),
        )

    def test_repair_registration_events_same_events_stay_intact(self):
        """При нахождении дубликатов событий в пределах одной секунды оставляем их в покое"""
        response = [
            event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
            event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.2),
            event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.3),
        ]
        eq_(
            [
                event_item(name=EVENT_USERINFO_FT, firstname='A', lastname='B', hintq='99:Q', hinta=None, timestamp=1),
                event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1),
                event_item(name=EVENT_INFO_PASSWORD, value='hash', timestamp=1.3),
            ],
            _repair_registration_events(response),
        )
