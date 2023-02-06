# -*- coding: utf-8 -*-
import json
from time import time

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.history.controllers import (
    ACCOUNT_HISTORY_BASIC_GRANT,
    ACCOUNT_HISTORY_HISTORY_BY_UID_GRANT,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_aggregated_item,
    auth_aggregated_item_old,
    auth_failed_item,
    auths_aggregated_response,
    auths_aggregated_response_old,
    auths_failed_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 123
TEST_SESSIONID = 'sessionid'
TEST_COOKIE = 'Session_id=%s' % TEST_SESSIONID
TEST_HOST = 'passport-test.yandex.ru'
TEST_USER_IP = '3.3.3.3'
TEST_YANDEXUID = '1230'

ACCOUNT_HISTORY_DEFAULT_LIMIT = 543


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
    ACCOUNT_HISTORY_DEFAULT_LIMIT=ACCOUNT_HISTORY_DEFAULT_LIMIT,
)
class TestHistoryViewOld(BaseBundleTestViews):

    default_url = '/1/bundle/account/history/'
    http_method = 'get'
    http_query_args = dict(consumer='dev')
    http_headers = dict(
        user_ip=TEST_USER_IP,
        cookie=TEST_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()
        self.mock_method_name = 'auths_aggregated_old'
        self.historydb_api_url = 'http://localhost/2/auths/aggregated/'

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

    def make_auth_aggregated_response(self, uid, auths=None, next=None):
        return auths_aggregated_response_old(uid=uid, auths=auths, next=next)

    def simple_history_response(self, uid=TEST_UID, next_auth_row='bla'):
        return {
            'status': 'ok',
            'next_auth_row': next_auth_row,
            'events': json.loads(self.make_auth_aggregated_response(uid=uid))['auths'],
        }

    def set_historydb_api_auths_aggregated(self, uid=TEST_UID, auths=None, next='bla'):
        self.env.historydb_api.set_response_value(
            self.mock_method_name,
            self.make_auth_aggregated_response(uid=uid, auths=auths, next=next),
        )

    def assert_historydb_called(self,
                                uid=TEST_UID,
                                limit=ACCOUNT_HISTORY_DEFAULT_LIMIT,
                                hours_limit=None,
                                from_auth_row=None,
                                next_row_in_response='bla',
                                password_auths=None):
        eq_(len(self.env.historydb_api.requests), 2)
        request = self.env.historydb_api.requests[0]

        params = {
            'consumer': 'passport',
            'limit': str(limit),
            'uid': str(uid),
        }

        if hours_limit is not None:
            params['hours_limit'] = str(hours_limit)

        if from_auth_row is not None:
            params['from'] = from_auth_row

        if password_auths is not None:
            params['password_auths'] = str(password_auths).lower()

        request.assert_query_equals(params)
        request.assert_url_starts_with(self.historydb_api_url)

        request = self.env.historydb_api.requests[1]

        params = {
            'consumer': 'passport',
            'limit': '1',
            'uid': str(uid),
            'from': next_row_in_response,
        }
        if hours_limit is not None:
            params['hours_limit'] = str(hours_limit)

        request.assert_query_equals(params)
        request.assert_url_starts_with(self.historydb_api_url)

    def test_no_uid_and_session_fails(self):
        """
        Если не передан uid и Session_id, то отвечаем
        ошибкой request.uid_or_session_expected
        """
        resp = self.make_request(exclude_headers=['cookie'])
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
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.not_found'])

    def test_by_uid_no_grant_fails(self):
        """
        Для запроса по uid необходимо иметь дополнительный грант
        """
        self.set_grants(by_uid=False)
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
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
            exclude_headers=['cookie'],
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
            exclude_headers=['cookie'],
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
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=['cookie'],
        )
        self.assert_ok_response(
            resp,
            **self.simple_history_response()
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
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.simple_history_response()
        )
        self.assert_historydb_called()

    def test_by_sessionid_ok_with_password_auths(self):
        """
        Запрос по Session_id.
        В ответе в поле events события пользователя
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request(
            query_args=dict(password_auths=True),
        )
        self.assert_ok_response(
            resp,
            **self.simple_history_response()
        )
        self.assert_historydb_called(password_auths=True)

    def test_with_optional_params(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_auths_aggregated()
        resp = self.make_request(
            query_args=dict(
                limit=555,
                hours_limit=100,
                from_auth_row='bla',
            ),
        )
        self.assert_ok_response(
            resp,
            **self.simple_history_response()
        )
        self.assert_historydb_called(limit=555, hours_limit=100, from_auth_row='bla')

    def test_nullify_next_auth_row(self):
        """
        Обнуляем next_auth_row, если при перезапросе не нашли данных
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.env.historydb_api.set_response_side_effect(
            self.mock_method_name,
            [
                self.make_auth_aggregated_response(uid=TEST_UID, next='bla'),
                self.make_auth_aggregated_response(uid=TEST_UID, auths=[], next=None),
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.simple_history_response(next_auth_row=None)
        )
        self.assert_historydb_called()

    def test_empty_next_auth_row_in_first_response(self):
        """
        Не делаем дополнительный запрос в historydb,
        если данных нет точно
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        self.set_historydb_api_auths_aggregated(next=None)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.simple_history_response(next_auth_row=None)
        )
        eq_(len(self.env.historydb_api.requests), 1)

    def test_sorting(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        # Тут неправильный порядок в рамках 1 часа
        a1 = auth_aggregated_item_old(
            1,
            'web',
        )
        a2 = auth_aggregated_item_old(
            2,
            'web',
        )
        a3 = auth_aggregated_item_old(
            3,
            'web',
        )

        auths = [a1, a2, a3]

        self.set_historydb_api_auths_aggregated(auths=auths)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            events=json.loads(
                self.make_auth_aggregated_response(uid=TEST_UID, auths=[a3, a2, a1]),
            )['auths'],
            next_auth_row='bla',
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
    ACCOUNT_HISTORY_DEFAULT_LIMIT=ACCOUNT_HISTORY_DEFAULT_LIMIT,
)
class TestHistoryView(TestHistoryViewOld):
    def setUp(self):
        super(TestHistoryView, self).setUp()
        self.mock_method_name = 'auths_aggregated'
        self.default_url = '/2/bundle/account/history/'
        self.historydb_api_url = 'http://localhost/3/auths/aggregated/'

    def set_historydb_api_auths_aggregated(self, uid=TEST_UID, auths=None, next='bla'):
        self.env.historydb_api.set_response_value(
            self.mock_method_name,
            auths_aggregated_response(uid=uid, auths=auths, next=next),
        )

    def make_auth_aggregated_response(self, uid, auths=None, next=None):
        return auths_aggregated_response(uid=uid, auths=auths, next=next)

    def simple_history_response(self, uid=TEST_UID, next_auth_row='bla'):
        return {
            'status': 'ok',
            'next_auth_row': next_auth_row,
            'events': json.loads(auths_aggregated_response(uid=uid))['auths'],
        }

    def test_sorting(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            self.default_sessionid_response(),
        )
        # Тут неправильный порядок в рамках 1 часа
        a1 = auth_aggregated_item(
            1,
            'web',
        )
        a2 = auth_aggregated_item(
            2,
            'web',
        )
        a3 = auth_aggregated_item(
            3,
            'web',
        )

        auths = [a1, a2, a3]

        self.set_historydb_api_auths_aggregated(auths=auths)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            events=json.loads(
                self.make_auth_aggregated_response(uid=TEST_UID, auths=[a3, a2, a1]),
            )['auths'],
            next_auth_row='bla',
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HISTORYDB_API_URL='http://localhost/',
    CHALLENGE_HISTORY_LIMIT=10,
    CHALLENGE_HISTORY_THRESHOLD=0.001,
)
class TestChallengeView(BaseBundleTestViews):

    default_url = '/1/bundle/account/history/challenge/'
    http_method = 'get'
    http_query_args = dict(consumer='dev')
    http_headers = dict(
        user_ip=TEST_USER_IP,
        cookie=TEST_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.base_time = int(time()) - 0.5
        self.http_query_args.update(challenge_time=self.base_time)

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'history': ['base']}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID),
        )
        self.setup_historydb_response([
            auth_failed_item(timestamp=self.base_time + 0.4),
            auth_failed_item(timestamp=self.base_time),
        ])

    def tearDown(self):
        self.env.stop()

    def setup_historydb_response(self, auths):
        self.env.historydb_api.set_response_value(
            'auths_failed',
            auths_failed_response(
                uid=TEST_UID,
                auths=auths,
            ),
        )

    def assert_historydb_not_called(self):
        eq_(len(self.env.historydb_api.requests), 0)

    def assert_historydb_called(self):
        eq_(len(self.env.historydb_api.requests), 1)
        request = self.env.historydb_api.requests[0]
        request.assert_url_starts_with('http://localhost/2/auths/failed/')
        request.assert_query_equals({
            'consumer': 'passport',
            'uid': str(TEST_UID),
            'from_ts': str(int(self.base_time)),
            'to_ts': str(int(self.base_time + 1)),
            'limit': '10',
            'status': 'challenge_shown',
        })


    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            challenge=auth_failed_item(timestamp=self.base_time),
        )
        self.assert_historydb_called()

    def test_ok_with_threshold(self):
        resp = self.make_request(query_args={'challenge_time': self.base_time + 0.00001})
        self.assert_ok_response(
            resp,
            challenge=auth_failed_item(timestamp=self.base_time),
        )
        self.assert_historydb_called()

    def test_ts_mismatch(self):
        resp = self.make_request(query_args={'challenge_time': self.base_time + 0.1})
        self.assert_error_response(resp, ['challenge.not_found'])
        self.assert_historydb_called()

    def test_nothing_found(self):
        self.setup_historydb_response([])
        resp = self.make_request()
        self.assert_error_response(resp, ['challenge.not_found'])
        self.assert_historydb_called()

    def test_ts_too_new(self):
        resp = self.make_request(query_args={'challenge_time': int(time()) + 3600})
        self.assert_error_response(resp, ['challenge_time.invalid'])
        self.assert_historydb_not_called()

    def test_ts_too_old(self):
        resp = self.make_request(query_args={'challenge_time': 42})
        self.assert_error_response(resp, ['challenge_time.invalid'])
        self.assert_historydb_not_called()
