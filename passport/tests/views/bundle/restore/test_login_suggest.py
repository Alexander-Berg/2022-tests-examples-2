# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_RESTORE
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.tests.views.bundle.restore.test.test_base import RestoreTestUtilsMixin
from passport.backend.core.builders.blackbox import (
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NEED_RESET_STATUS,
    BLACKBOX_SESSIONID_VALID_STATUS,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_sessionid_response,
    blackbox_userinfo_response,
)
from passport.backend.core.cookies.cookie_l import CookieLUnpackError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


def blackbox_sessionid_multi_append_unknown_uid(sessionid, item_id):
    sessionid = blackbox_sessionid_multi_append_user(
        sessionid,
        uid=None,
        item_id=item_id,
    )
    parsed_sessionid = json.loads(sessionid)
    parsed_sessionid['users'][-1]['uid'] = {}
    sessionid = json.dumps(parsed_sessionid)
    return sessionid


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    BLACKBOX_RETRIES=1,
)
class RestoreLoginSuggestTestCase(BaseBundleTestViews, RestoreTestUtilsMixin):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'restore': ['base']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(login=TEST_DEFAULT_LOGIN, display_login=TEST_USER_ENTERED_LOGIN),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self._cookie_l = mock.Mock()
        self._cookie_l.unpack = mock.Mock(return_value=TEST_COOKIE_L_INFO)

        self.patches = [
            mock.patch(
                'passport.backend.api.views.bundle.restore.controllers.CookieL',
                mock.Mock(side_effect=[self._cookie_l]),
            ),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches
        del self._cookie_l
        del self.orig_track

    def make_request(self, headers=None):
        return self.env.client.post(
            '/2/bundle/restore/login_suggest/?consumer=dev',
            data={'track_id': self.track_id},
            headers=headers,
        )

    def test_suggest_with_L_cookie(self):
        """Саджест на основе куки L"""
        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': TEST_USER_ENTERED_LOGIN,
                    'suggest_name': TEST_USER_ENTERED_LOGIN,
                },
            ],
        )
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_suggest_works_within_restore_process(self):
        """Саджест работает в рамках процесса восстановления"""
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = PROCESS_RESTORE

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': TEST_USER_ENTERED_LOGIN,
                    'suggest_name': TEST_USER_ENTERED_LOGIN,
                },
            ],
        )

    def test_suggest_with_L_cookie_empty_login(self):
        """В куке L нет логина"""
        self._cookie_l.unpack = mock.Mock(return_value={'uid': TEST_DEFAULT_UID, 'login': ''})
        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )

    def test_suggest_with_no_cookies(self):
        """Нет кук для саджеста"""
        self._cookie_l.unpack = mock.Mock(side_effect=CookieLUnpackError)
        resp = self.make_request(headers=self.get_headers(cookie=''))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )
        self.assert_track_updated(
            suggested_logins=[],
            suggest_login_first_call=TimeNow(),
            suggest_login_last_call=TimeNow(),
            suggest_login_count=1,
        )
        eq_(len(self.env.blackbox.requests), 0)

    def test_suggest_with_yandex_login_cookie(self):
        """Саджест на основе куки yandex_login не работает"""
        self._cookie_l.unpack = mock.Mock(side_effect=CookieLUnpackError)
        resp = self.make_request(headers=self.get_headers(cookie='yandex_login=%s;' % TEST_PDD_LOGIN))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )

    def test_suggest_works_when_blackbox_sessionid_fails(self):
        """Саджест работает, даже если происходит сбой метода sessionid ЧЯ"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': TEST_USER_ENTERED_LOGIN,
                    'suggest_name': TEST_USER_ENTERED_LOGIN,
                },
            ],
        )
        eq_(len(self.env.blackbox.requests), 2)
        self.env.blackbox.requests[0].assert_query_contains({
            'method': 'sessionid',
            # наличие флага гарантирует, что вся информация о пользователе будет в ответе, даже если статус
            # пользователя в куке - невалидный или заблокированный
            'full_info': 'yes',
            'sessionid': TEST_SESSIONID,
            'multisession': 'yes',
        })

    def test_suggest_works_when_blackbox_userinfo_fails(self):
        """Саджест работает, даже если происходит сбой метода userinfo ЧЯ"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )
        eq_(len(self.env.blackbox.requests), 2)
        self.env.blackbox.requests[1].assert_post_data_contains(
            {
                'method': 'userinfo',
                'login': TEST_DEFAULT_LOGIN,
            },
        )

    def test_suggest_with_various_users_in_session(self):
        """В куке есть несколько разных пользователей"""
        # вся кука со статусом NEED RESET, дефолтный пользователь валидный
        sessionid = blackbox_sessionid_multi_response(
            uid=1,
            login='other-login',
            display_login='OTHER.LOGIN',
            status=BLACKBOX_SESSIONID_NEED_RESET_STATUS,
            default_user_status=BLACKBOX_SESSIONID_VALID_STATUS,
        )
        # социальный пользователь - не выводим в саджесте
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=2,
            login='',
            aliases={
                'social': TEST_SOCIAL_LOGIN,
            },
        )
        # пользователь с тем же логином, что и в куке L
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=3,
            login=TEST_DEFAULT_LOGIN,
        )
        # ПДД-пользователь с невалидным статусом
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
            default_avatar_key=TEST_AVATAR_KEY,
        )
        # заблокированный пользователь
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=4,
            login='disabled-login',
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            default_avatar_key=TEST_AVATAR_KEY,
        )
        # невалидный (удаленный) пользователь
        sessionid = blackbox_sessionid_multi_append_invalid_session(
            sessionid,
            item_id=100,
        )
        # пустой uid
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=None,
            item_id=200,
        )
        # unknown uid
        sessionid = blackbox_sessionid_multi_append_unknown_uid(
            sessionid,
            item_id=300,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': 'OTHER.LOGIN',
                    'suggest_name': 'OTHER.LOGIN',
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'login': 'disabled-login',
                    'suggest_name': 'disabled-login',
                },
                {
                    'login': TEST_DEFAULT_LOGIN,
                    'suggest_name': TEST_DEFAULT_LOGIN,
                },
                {
                    'default_avatar': TEST_AVATAR_KEY,
                    'login': TEST_PDD_LOGIN,
                    'suggest_name': TEST_PDD_LOGIN,
                },
            ],
        )

    def test_suggest_with_invalid_session(self):
        """Кука невалидная"""
        sessionid = blackbox_sessionid_response(
            uid=None,
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': TEST_USER_ENTERED_LOGIN,
                    'suggest_name': TEST_USER_ENTERED_LOGIN,
                },
            ],
        )

    def test_suggest_for_social_user(self):
        """Саджест на основе куки L, соц. пользователю показываем display name"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                display_name=TEST_SOCIAL_DISPLAY_NAME,
            ),
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[
                {
                    'login': TEST_SOCIAL_LOGIN,
                    'suggest_name': TEST_SOCIAL_NAME,
                },
            ],
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    BLACKBOX_RETRIES=1,
)
class RestoreLoginSuggestTestCaseV1(BaseBundleTestViews, RestoreTestUtilsMixin):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'restore': ['base']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            self.orig_track = track.snapshot()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self._cookie_l = mock.Mock()
        self._cookie_l.unpack = mock.Mock(return_value=TEST_COOKIE_L_INFO)

        self.patches = [
            mock.patch(
                'passport.backend.api.views.bundle.restore.controllers.CookieL',
                mock.Mock(side_effect=[self._cookie_l]),
            ),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.patches
        del self._cookie_l
        del self.orig_track

    def make_request(self, headers=None):
        return self.env.client.post(
            '/1/bundle/restore/login_suggest/?consumer=dev',
            data={'track_id': self.track_id},
            headers=headers,
        )

    def test_suggest_with_L_cookie(self):
        """Саджест на основе куки L"""
        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[TEST_DEFAULT_LOGIN],
        )

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_suggest_works_within_restore_process(self):
        """Саджест работает в рамках процесса восстановления"""
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = PROCESS_RESTORE

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[TEST_DEFAULT_LOGIN],
        )

    def test_suggest_with_L_cookie_empty_login(self):
        """В куке L нет логина"""
        self._cookie_l.unpack = mock.Mock(return_value={'uid': TEST_DEFAULT_UID, 'login': ''})
        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )

    def test_suggest_with_no_cookies(self):
        """Нет кук для саджеста"""
        self._cookie_l.unpack = mock.Mock(side_effect=CookieLUnpackError)
        resp = self.make_request(headers=self.get_headers(cookie=''))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )
        self.assert_track_updated(
            suggested_logins=[],
            suggest_login_first_call=TimeNow(),
            suggest_login_last_call=TimeNow(),
            suggest_login_count=1,
        )
        eq_(len(self.env.blackbox.requests), 0)

    def test_suggest_with_yandex_login_cookie(self):
        """Саджест на основе куки yandex_login не работает - см. PASSP-12573"""
        self._cookie_l.unpack = mock.Mock(side_effect=CookieLUnpackError)
        resp = self.make_request(headers=self.get_headers(cookie='yandex_login=%s;' % TEST_PDD_LOGIN))

        self.assert_ok_response(
            resp,
            suggested_logins=[],
        )

    def test_suggest_works_when_blackbox_sessionid_fails(self):
        """Саджест работает, даже если происходит сбой метода sessionid ЧЯ"""
        self.env.blackbox.set_blackbox_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[TEST_DEFAULT_LOGIN],
        )
        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_query_contains({
            'method': 'sessionid',
            # наличие флага гарантирует, что вся информация о пользователе будет в ответе, даже если статус
            # пользователя в куке - невалидный или заблокированный
            'full_info': 'yes',
            'sessionid': TEST_SESSIONID,
            'multisession': 'yes',
        })

    def test_suggest_with_various_users_in_session(self):
        """В куке есть несколько разных пользователей"""
        # вся кука со статусом NEED RESET, дефолтный пользователь валидный
        sessionid = blackbox_sessionid_multi_response(
            uid=1,
            login='other_login',
            display_login='OTHER_LOGIN',
            status=BLACKBOX_SESSIONID_NEED_RESET_STATUS,
            default_user_status=BLACKBOX_SESSIONID_VALID_STATUS,
        )
        # социальный пользователь - не выводим в саджесте
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=2,
            login='',
            aliases={
                'social': TEST_SOCIAL_LOGIN,
            },
        )
        # пользователь с тем же логином, что и в куке L
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=3,
            login=TEST_DEFAULT_LOGIN,
        )
        # ПДД-пользователь с невалидным статусом
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
        )
        # заблокированный пользователь
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=4,
            login='disabled-login',
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
        )
        # невалидный (удаленный) пользователь
        sessionid = blackbox_sessionid_multi_append_invalid_session(
            sessionid,
            item_id=100,
        )
        # пустой uid
        sessionid = blackbox_sessionid_multi_append_user(
            sessionid,
            uid=None,
            item_id=200,
        )
        # unknown uid
        sessionid = blackbox_sessionid_multi_append_unknown_uid(
            sessionid,
            item_id=300,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[TEST_DEFAULT_LOGIN, 'OTHER_LOGIN', 'disabled-login', TEST_PDD_LOGIN],
        )

    def test_suggest_with_invalid_session(self):
        """Кука невалидная"""
        sessionid = blackbox_sessionid_response(
            uid=None,
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid,
        )

        resp = self.make_request(headers=self.get_headers(cookie=TEST_USER_COOKIES))

        self.assert_ok_response(
            resp,
            suggested_logins=[TEST_DEFAULT_LOGIN],
        )
