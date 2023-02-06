# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.mock_objects import TimeNow
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.events.controllers import (
    ACCOUNT_HISTORY_BASIC_GRANT,
    ACCOUNT_HISTORY_HISTORY_BY_UID_GRANT,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_response,
)
from passport.backend.core.historydb.account_history.account_history import (
    HALF_A_YEAR_AGO,
    HISTORYDB_API_QEURY_LIMIT,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 123
TEST_SESSIONID = 'sessionid'
TEST_COOKIE = 'Session_id=%s' % TEST_SESSIONID
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_IP = '3.3.3.3'
TEST_YANDEXUID = '1230'

ACCOUNT_EVENTS_DEFAULT_LIMIT = 543


def parsed_events_response(events=None, timestamp=3600, from_timestamp=None):
    if events is None:
        events = [parsed_event([personal_action()], 'personal_data', timestamp=timestamp)]
    return {
        'status': 'ok',
        'events': events,
        'next_from_timestamp': from_timestamp,
    }


def personal_action():
    return {
        'changed_fields': ['firstname'],
        'firstname': 'firstname',
        'type': 'personal_data',
    }


def parsed_event(actions, event_type, timestamp):
    return {
        'event_type': event_type,
        'actions': actions,
        'browser': {
            'name': None,
            'version': None,
        },
        'ip': {
            'AS': None,
            'geoid': None,
            'ip': TEST_USER_IP,
        },
        'os': {
            'name': None,
            'version': None,
        },
        'timestamp': timestamp,
    }


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
    ACCOUNT_EVENTS_DEFAULT_LIMIT=ACCOUNT_EVENTS_DEFAULT_LIMIT,
)
class TestEventsView(BaseBundleTestViews):

    default_url = '/1/bundle/account/events/'
    http_query_args = dict(consumer='dev')
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_COOKIE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()

    def tearDown(self):
        self.env.stop()
        del self.env

    def set_grants(self, by_uid=False):
        grants = {}
        for grant in (ACCOUNT_HISTORY_BASIC_GRANT,):
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)
        if by_uid:
            prefix, suffix = ACCOUNT_HISTORY_HISTORY_BY_UID_GRANT.split('.')
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def default_userinfo_response(self, uid=TEST_UID, enabled=True, attributes=None):
        return blackbox_userinfo_response(
            uid=uid,
            enabled=enabled,
            attributes=attributes,
        )

    def default_sessionid_response(self, uid=TEST_UID):
        return blackbox_sessionid_multi_response(uid=uid)

    def set_historydb_api_events(self, uid=TEST_UID, events=None):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(uid, events=events),
        )

    def assert_historydb_called(self,
                                uid=TEST_UID,
                                to_ts=None,
                                from_ts=None):
        eq_(len(self.env.historydb_api.requests), 1)
        request = self.env.historydb_api.requests[0]

        request.assert_url_starts_with('http://localhost/2/events/')

        if to_ts is None:
            to_ts = TimeNow()
        if from_ts is None:
            from_ts = TimeNow(offset=-HALF_A_YEAR_AGO)

        params = {
            'consumer': 'passport',
            'limit': str(HISTORYDB_API_QEURY_LIMIT),
            'uid': str(uid),
            'from_ts': from_ts,
            'to_ts': to_ts,
        }

        request.assert_query_equals(params)

    def test_no_uid_and_session_fails(self):
        """
        Если не передан uid и Session_id, то отвечаем
        ошибкой request.uid_or_session_expected
        """
        resp = self.make_request(headers=dict(cookie=None))
        self.assert_error_response(resp, ['request.credentials_all_missing'])

    def test_both_uid_sessionid_fails(self):
        """
        Если передан uid и Session_id, то отвечаем
        ошибкой request.uid_session_both_present
        """
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie='Session_id='),
        )
        self.assert_error_response(resp, ['request.credentials_several_present'])

    def test_unknown_uid_fails(self):
        """
        Если передали неизвестный uid, то отвечаем
        ошибкой account.not_found
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie=None),
        )
        self.assert_error_response(resp, ['account.not_found'])

    def test_by_uid_no_grant_fails(self):
        """
        Для запроса по uid необходимо иметь дополнительный грант
        """
        self.set_grants(by_uid=False)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie=None),
        )
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_disabled_uid_account_fails(self):
        """
        Запрос по uid.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie=None),
        )
        self.assert_error_response(resp, ['account.disabled'])

    def test_disabled_on_deletion_uid_account_fails(self):
        """
        Запрос по uid.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        self.set_grants(by_uid=True)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie=None),
        )
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_invalid_sessionid_fails(self):
        """
        Если сессия невалидная, то отвечаем
        ошибкой sessionid.invalid
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request(headers=dict(cookie='Session_id='))
        self.assert_error_response(resp, ['sessionid.invalid'])

    def test_disabled_sessionid_account_fails(self):
        """
        Запрос по Session_id.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_disabled_on_deletion_sessionid_account_fails(self):
        """
        Запрос по Session_id.
        Если пользователь заблокирован, то отвечаем
        ошибкой account.disabled
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_by_uid_ok(self):
        """
        Запрос по uid.
        В ответе в поле events события пользователя
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_grants(by_uid=True)
        self.set_historydb_api_events(events=[event_item(user_ip=TEST_USER_IP)])
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            headers=dict(cookie=None),
        )
        self.assert_ok_response(
            resp,
            **parsed_events_response()
        )
        self.assert_historydb_called()

    def test_by_sessionid_ok(self):
        """
        Запрос по Session_id.
        В ответе в поле events события пользователя
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_events(events=[event_item(user_ip=TEST_USER_IP)])
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **parsed_events_response()
        )
        self.assert_historydb_called()

    def test_with_optional_params(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_events()
        resp = self.make_request(
            query_args=dict(
                limit=555,
                from_timestamp=42,
            ),
        )
        self.assert_ok_response(
            resp,
            events=[],
            next_from_timestamp=None,
        )
        self.assert_historydb_called(to_ts='42')

    def test_sorting(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        e1 = event_item(user_ip=TEST_USER_IP, timestamp=1)
        e2 = event_item(user_ip=TEST_USER_IP, timestamp=2)
        e3 = event_item(user_ip=TEST_USER_IP, timestamp=3)

        events = [e1, e2, e3]

        self.set_historydb_api_events(events=events)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            events=[
                parsed_event([personal_action()], 'personal_data', timestamp=3),
                parsed_event([personal_action()], 'personal_data', timestamp=2),
                parsed_event([personal_action()], 'personal_data', timestamp=1),
            ],
            next_from_timestamp=None,
        )

    def test_pagination(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        e1 = event_item(user_ip=TEST_USER_IP, timestamp=1)
        e2 = event_item(user_ip=TEST_USER_IP, timestamp=2)
        e3 = event_item(user_ip=TEST_USER_IP, timestamp=3)
        e4 = event_item(user_ip=TEST_USER_IP, timestamp=4)
        e5 = event_item(user_ip=TEST_USER_IP, timestamp=5)

        events = [e1, e2, e3, e4, e5]

        self.set_historydb_api_events(events=events)

        resp = self.make_request(
            query_args=dict(limit=2),
        )
        self.assert_ok_response(
            resp,
            events=[
                parsed_event([personal_action()], 'personal_data', timestamp=5),
                parsed_event([personal_action()], 'personal_data', timestamp=4),
            ],
            next_from_timestamp=3,
        )

        resp = self.make_request(
            query_args=dict(
                from_timestamp=3,
                limit=2,
            ),
        )
        self.assert_ok_response(
            resp,
            events=[
                parsed_event([personal_action()], 'personal_data', timestamp=3),
                parsed_event([personal_action()], 'personal_data', timestamp=2),
            ],
            next_from_timestamp=1,
        )

        self.set_historydb_api_events(events=events[:3])

        resp = self.make_request(
            query_args=dict(
                from_timestamp=1,
                limit=2,
            ),
        )
        self.assert_ok_response(
            resp,
            events=[
                parsed_event([personal_action()], 'personal_data', timestamp=1),
            ],
            next_from_timestamp=None,
        )

    def test_hours_limit(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_events(events=[event_item(user_ip=TEST_USER_IP)])
        resp = self.make_request(query_args=dict(hours_limit=5))
        self.assert_ok_response(
            resp,
            events=[
                parsed_event([personal_action()], 'personal_data', timestamp=3600),
            ],
            next_from_timestamp=None,
        )
        self.assert_historydb_called(
            from_ts=TimeNow(offset=-5 * 3600),
        )
