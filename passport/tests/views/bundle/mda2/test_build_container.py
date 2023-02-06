# -*- coding: utf-8 -*-
import json
import random

import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox import (
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_sign_response,
)
from passport.backend.core.cookies import (
    cookie_lah,
    cookie_y,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
)

from .test_base import (
    BaseMda2Testcase,
    EXPECTED_MDA2_BEACON_COOKIE_WITH_EXPIRES,
    EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
    EXPECTED_SLAVE_MDA2_BEACON_COOKIE_WITH_EXPIRES,
    MDA2_BEACON_VALUE,
    TEST_COOKIE_CHECK_VALUE,
    TEST_COOKIE_LAH_VALUE,
    TEST_COOKIE_YP_VALUE,
    TEST_COOKIE_YS_VALUE,
    TEST_EXPECTED_ERASER_MY_COOKIE_SLAVE,
    TEST_EXPECTED_I_SLAVE,
    TEST_EXPECTED_MDA2_DOMAINS_MASTER,
    TEST_EXPECTED_MY_COOKIE_SLAVE,
    TEST_EXPECTED_NOAUTH_SESSIONID_COOKIE_SLAVE,
    TEST_EXPECTED_NOAUTH_YANDEX_LOGIN_SLAVE,
    TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
    TEST_EXPECTED_YANDEX_GID_COOKIE_SLAVE,
    TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
    TEST_EXPECTED_YANDEXUID_SLAVE,
    TEST_EXPECTED_YP_COOKIE_SLAVE,
    TEST_EXPECTED_YS_COOKIE_MASTER,
    TEST_EXPECTED_YS_COOKIE_SLAVE,
    TEST_HOST,
    TEST_IP,
    TEST_MASTER_DOMAIN,
    TEST_MDA2_DOMAINS_TEMPLATE,
    TEST_MDA2_DOMAINS_VALUE,
    TEST_PACKED_CONTAINER,
    TEST_SCRIPT_NONCE,
    TEST_SLAVE_DOMAIN,
    TEST_TARGET_HOST,
    TEST_TIME_NOW,
    TEST_USER_AGENT,
    TEST_USER_AGENT_WITH_SAMESITE_SUPPORT,
    TEST_USER_COOKIES,
    TEST_UUID,
    TEST_YANDEXUID_VALUE,
)


class BuildContainerTestcase(BaseMda2Testcase):
    default_url = '/1/bundle/mda2/container/build/'
    http_query_args = {
        'is_background': True,
        'process_uuid': TEST_UUID,
        'target_host': TEST_TARGET_HOST,
    }

    def setUp(self):
        super(BuildContainerTestcase, self).setUp()

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ttl=5,
                prolong_cookies=True,
                resign_for_domains=[TEST_TARGET_HOST],
            ),
        )
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_PACKED_CONTAINER),
        )

        self._time_mock = mock.Mock(return_value=TEST_TIME_NOW)  # для куки yandexuid
        self._system_random_mock = mock.Mock(return_value=TEST_COOKIE_CHECK_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=TEST_COOKIE_YS_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=TEST_COOKIE_LAH_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=TEST_COOKIE_YP_VALUE)

        patches = [
            mock.patch(
                'passport.backend.api.common.authorization.time.time',
                self._time_mock,
            ),
            mock.patch.object(
                random.SystemRandom,
                'randint',
                self._system_random_mock,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
        ]
        for patch in patches:
            patch.start()
        self._patches += patches

    def tearDown(self):
        del self._time_mock
        del self._system_random_mock
        del self._cookie_ys_pack
        del self._cookie_lah_pack
        super(BuildContainerTestcase, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            mode='mda2',
            action='build_container',
            status='ok',
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_VALUE,
            process_uuid=TEST_UUID,
            host=TEST_SLAVE_DOMAIN,
        )

    def get_csp_headers(self):
        return {
            'Content-Security-Policy': "default-src 'none'; frame-ancestors https://*.kinopoisk.ru; connect-src 'self'; script-src 'nonce-%s'" % TEST_SCRIPT_NONCE,
        }

    def assert_blackbox_called(self, requests_count=2):
        eq_(len(self.env.blackbox.requests), requests_count)
        if requests_count == 2:
            self.env.blackbox.requests[0].assert_query_contains({
                'method': 'sessionid',
                'host': TEST_HOST,
                'userip': TEST_IP,
                'sessionid': '0:old-session',
                'resign': 'yes',
                'resign_for_domains': TEST_TARGET_HOST,
                'format': 'json',
            })
        self.env.blackbox.requests[-1].assert_query_contains({
            'method': 'sign',
            'format': 'json',
        })

    def assert_container_ok(self, auth_cookie_valid=True, expected_cookies=None):
        container_data_raw = self.env.blackbox.requests[-1].get_query_params()['value'][0]
        container_data = json.loads(container_data_raw)
        eq_(
            set(container_data.keys()),
            {'src_domain', 'dst_domain', 'auth_cookie_valid', 'cookies', 'cookie_check_value'},
        )
        eq_(container_data['src_domain'], TEST_MASTER_DOMAIN)
        eq_(container_data['dst_domain'], TEST_SLAVE_DOMAIN)
        eq_(container_data['auth_cookie_valid'], auth_cookie_valid)
        iterdiff(eq_)(
            sorted(container_data['cookies']),
            sorted(expected_cookies or self.get_expected_cookies_for_slave()),
        )
        eq_(container_data['cookie_check_value'], str(TEST_COOKIE_CHECK_VALUE))

    def assert_statbox_ok(self, event, auth_status='auth', with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(
                self.env.statbox.entry(
                    'check_cookies',
                    ['action', 'ip', 'process_uuid', 'status', 'user_agent', 'yandexuid'],
                    sessionid=mask_sessionid('0:old-session')
                )
            )
        entries.append(
            self.env.statbox.entry(
                'base',
                event=event,
                auth_status=auth_status,
                **kwargs
            )
        )
        self.env.statbox.assert_has_written(entries)

    def test_host_invalid_error(self):
        resp = self.make_request(headers={'host': 'google.com'})
        self.assert_error_response(resp, ['host.invalid'])

    def test_target_host_not_slave_error(self):
        resp = self.make_request(query_args={'target_host': 'yandex.ru'})
        self.assert_error_response(resp, ['target_host.not_slave'])

    def test_blackbox_temporary_error(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['backend.blackbox_failed'],
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
        )

    def test_pull_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            auth_status='auth',
            container=TEST_PACKED_CONTAINER,
            cookies=self.get_expected_cookies_for_master(),
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_blackbox_called()
        self.assert_container_ok()
        self.assert_statbox_ok('pull', with_check_cookies=True)

    def test_push_ok(self):
        resp = self.make_request(query_args={'is_background': False})
        self.assert_ok_response(
            resp,
            auth_status='auth',
            container=TEST_PACKED_CONTAINER,
            cookies=self.get_expected_cookies_for_master(),
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_blackbox_called()
        self.assert_container_ok()
        self.assert_statbox_ok('push', with_check_cookies=True)

    def test_no_cookies_ok(self):
        resp = self.make_request(query_args={'is_background': False}, headers={'cookie': ''})
        self.assert_ok_response(
            resp,
            auth_status='empty',
            container=TEST_PACKED_CONTAINER,
            cookies=[
                TEST_EXPECTED_YS_COOKIE_MASTER,
                TEST_MDA2_DOMAINS_TEMPLATE % (TEST_SLAVE_DOMAIN, TEST_MASTER_DOMAIN),
                EXPECTED_MDA2_BEACON_COOKIE_WITH_EXPIRES,
            ],
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_blackbox_called(requests_count=1)
        self.assert_container_ok(
            auth_cookie_valid=False,
            expected_cookies=[
                TEST_EXPECTED_NOAUTH_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_NOAUTH_YANDEX_LOGIN_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE_WITH_EXPIRES,
            ],
        )
        self.assert_statbox_ok('push', auth_status='empty', _exclude=['yandexuid'])

    def test_cookies_need_no_refresh_ok(self):
        """
        Куки на мастер-домене свежие: поэтому фронту подновлённые авторизационные куки не отдадим,
        но в контейнер положим полный набор кук
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ttl=5,
                prolong_cookies=False,
                resign_for_domains=[TEST_TARGET_HOST],
            ),
        )
        resp = self.make_request(query_args={'is_background': False})
        self.assert_ok_response(
            resp,
            auth_status='auth',
            container=TEST_PACKED_CONTAINER,
            cookies=[
                TEST_EXPECTED_YS_COOKIE_MASTER,
                TEST_MDA2_DOMAINS_TEMPLATE % (TEST_MDA2_DOMAINS_VALUE, TEST_MASTER_DOMAIN),
            ],
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_blackbox_called()
        self.assert_container_ok()
        self.assert_statbox_ok('push', with_check_cookies=True)

    def test_cookies_with_samesite_ok(self):
        resp = self.make_request(
            query_args={'is_background': False},
            headers={
                'cookie': '',
                'user_agent': TEST_USER_AGENT_WITH_SAMESITE_SUPPORT,
            }
        )
        self.assert_ok_response(
            resp,
            auth_status='empty',
            container=TEST_PACKED_CONTAINER,
            cookies=[
                TEST_EXPECTED_YS_COOKIE_MASTER + '; SameSite=None',
                TEST_MDA2_DOMAINS_TEMPLATE % (TEST_SLAVE_DOMAIN, TEST_MASTER_DOMAIN),
                EXPECTED_MDA2_BEACON_COOKIE_WITH_EXPIRES + '; SameSite=None',
            ],
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )

    def test_cookies_invalid_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request(query_args={'is_background': False})
        self.assert_ok_response(
            resp,
            auth_status='noauth',
            container=TEST_PACKED_CONTAINER,
            cookies=[
                TEST_EXPECTED_YS_COOKIE_MASTER,
                TEST_EXPECTED_MDA2_DOMAINS_MASTER,
                EXPECTED_MDA2_BEACON_COOKIE_WITH_EXPIRES,
            ],
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_blackbox_called()
        self.assert_container_ok(
            auth_cookie_valid=False,
            expected_cookies=[
                TEST_EXPECTED_NOAUTH_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_NOAUTH_YANDEX_LOGIN_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
                TEST_EXPECTED_YANDEXUID_SLAVE,
                TEST_EXPECTED_I_SLAVE,
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE_WITH_EXPIRES,
            ],
        )
        self.assert_statbox_ok('push', auth_status='noauth', with_check_cookies=True)

    def test_custom_slave_domain_settings_ok(self):
        with settings_context(
            PASSPORT_SUBDOMAIN='passport-test',
            MDA2_SLAVE_DOMAINS=['kinopoisk.ru'],
            CUSTOM_MDA_DOMAIN_CONFIGS={
                'kinopoisk.ru': {
                    'cookies': {
                        'Session_id': 'ya_sess_id',  # эту куку надо переименовать
                        'yandexuid': '',  # эту куку надо выкинуть
                        'i': None,  # эту куку надо выкинуть
                    },
                },
            },
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            auth_status='auth',
            container=TEST_PACKED_CONTAINER,
            cookies=self.get_expected_cookies_for_master(),
            headers=self.get_csp_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_container_ok(
            expected_cookies=[
                TEST_EXPECTED_SESSIONID_COOKIE_SLAVE.replace('Session_id=', 'ya_sess_id='),
                TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
            ],
        )

    def test_cookie_yp(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                'kinopoisk.ru': {'cookies': {'yp': 'yp'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            auth_status='auth',
            check_all=False,
            cookies=self.get_expected_cookies_for_master(),
            ignore_order_for=['cookies'],
        )
        self.assert_container_ok(
            expected_cookies=[
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
                TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
                TEST_EXPECTED_YP_COOKIE_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
            ],
        )

    def test_cookie_my(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                'kinopoisk.ru': {'cookies': {'my': 'my'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            auth_status='auth',
            check_all=False,
            cookies=self.get_expected_cookies_for_master(),
            ignore_order_for=['cookies'],
        )
        self.assert_container_ok(
            expected_cookies=[
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
                TEST_EXPECTED_MY_COOKIE_SLAVE,
                TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
            ],
        )

    def test_no_cookie_my(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                'kinopoisk.ru': {'cookies': {'my': 'my'}},
            },
        ):
            resp = self.make_request(
                headers=dict(
                    cookie='; '.join(c for c in TEST_USER_COOKIES.split('; ') if not c.startswith('my='))
                ),
            )

        self.assert_ok_response(
            resp,
            auth_status='auth',
            check_all=False,
            cookies=self.get_expected_cookies_for_master(),
            ignore_order_for=['cookies'],
        )
        self.assert_container_ok(
            expected_cookies=[
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
                TEST_EXPECTED_ERASER_MY_COOKIE_SLAVE,
                TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
            ],
        )

    def test_cookie_yandex_gid(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                'kinopoisk.ru': {'cookies': {'yandex_gid': 'yandex_gid'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            auth_status='auth',
            check_all=False,
            cookies=self.get_expected_cookies_for_master(),
            ignore_order_for=['cookies'],
        )
        self.assert_container_ok(
            expected_cookies=[
                EXPECTED_SLAVE_MDA2_BEACON_COOKIE,
                TEST_EXPECTED_YANDEX_GID_COOKIE_SLAVE,
                TEST_EXPECTED_SESSIONID_COOKIE_SLAVE,
                TEST_EXPECTED_YANDEX_LOGIN_COOKIE_SLAVE,
                TEST_EXPECTED_YS_COOKIE_SLAVE,
            ],
        )
