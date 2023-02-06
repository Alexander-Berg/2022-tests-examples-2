# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.blackbox import (
    BLACKBOX_CHECK_SIGN_STATUS_EXPIRED,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_sign_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.undefined import Undefined

from .test_base import (
    BaseMda2Testcase,
    TEST_COOKIE_CHECK_VALUE,
    TEST_EXPECTED_MY_COOKIE_SLAVE,
    TEST_EXPECTED_YANDEX_GID_COOKIE_SLAVE,
    TEST_EXPECTED_YP_COOKIE_SLAVE,
    TEST_HOST,
    TEST_IP,
    TEST_MASTER_DOMAIN,
    TEST_MERGED_YS_COOKIE,
    TEST_PACKED_CONTAINER,
    TEST_RETPATH,
    TEST_SCRIPT_NONCE,
    TEST_SLAVE_DOMAIN,
    TEST_SLAVE_DOMAIN_USER_COOKIES,
    TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_MY,
    TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YP,
    TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YANDEX_GID,
    TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YS,
    TEST_TARGET_HOST,
    TEST_USER_AGENT,
    TEST_UUID,
    TEST_YANDEXUID_VALUE,
)


class BaseUseContainerTestcase(BaseMda2Testcase):
    default_url = '/1/bundle/mda2/container/use/'
    http_headers = dict(
        host=TEST_TARGET_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_SLAVE_DOMAIN_USER_COOKIES,
        user_ip=TEST_IP,
    )
    http_query_args = {
        'is_background': True,
        'process_uuid': TEST_UUID,
        'container': TEST_PACKED_CONTAINER,
    }
    rebuilt_cookies_for_slave = True

    def setUp(self):
        super(BaseUseContainerTestcase, self).setUp()
        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(json.dumps({
                'src_domain': TEST_MASTER_DOMAIN,
                'dst_domain': TEST_SLAVE_DOMAIN,
                'auth_cookie_valid': True,
                'cookies': self.get_expected_cookies_for_slave(),
                'cookie_check_value': str(TEST_COOKIE_CHECK_VALUE),
            })),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ttl=5,
            ),
        )

    def setup_statbox_templates(self, yandexuid=TEST_YANDEXUID_VALUE):
        self.env.statbox.bind_entry(
            'base',
            mode='mda2',
            action='use_container',
            status='ok',
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_VALUE,
            process_uuid=TEST_UUID,
            host=TEST_SLAVE_DOMAIN,
        )

    def expected_headers(self, with_script_nonce=True, domain=TEST_SLAVE_DOMAIN):
        csp_header = "default-src 'none'; frame-ancestors https://*.%s" % domain
        if with_script_nonce:
            csp_header += "; connect-src 'self'; script-src 'nonce-%s'" % TEST_SCRIPT_NONCE
        return {
            'Content-Security-Policy': csp_header,
            'Referrer-Policy': 'origin',
        }

    def assert_blackbox_called(self, requests_count=1):
        self.assertEqual(len(self.env.blackbox.requests), requests_count)
        self.env.blackbox.requests[0].assert_query_contains({
            'method': 'check_sign',
            'format': 'json',
        })
        if requests_count == 2:
            self.env.blackbox.requests[-1].assert_query_contains({
                'method': 'sessionid',
                'host': TEST_TARGET_HOST,
                'userip': TEST_IP,
                'sessionid': '0:old-session',
                'format': 'json',
            })

    def assert_statbox_ok(
        self, event, auth_status='auth', old_auth_status='auth',
        old_auth_bb_status='OK', with_check_cookies=False,
        **kwargs
    ):
        entries = []
        if with_check_cookies:
            entries.append(
                self.env.statbox.entry(
                    'check_cookies',
                    ['action', 'ip', 'process_uuid', 'status', 'user_agent', 'yandexuid'],
                    host='beta.kinopoisk.ru',
                    sessionid=mask_sessionid('0:old-session'),
                )
            )
        entries.append(
            self.env.statbox.entry(
                'base',
                event=event,
                auth_status=auth_status,
                old_auth_status=old_auth_status,
                old_auth_bb_status=old_auth_bb_status,
                **kwargs
            )
        )
        self.env.statbox.assert_has_written(entries)


@with_settings_hosts(
    CUSTOM_MDA_DOMAIN_CONFIGS={
        TEST_SLAVE_DOMAIN: {
            'cookies': {
                'Session_id': 'ya_sess_id',
            },
        },
    },
)
class UseContainerTestcase(BaseUseContainerTestcase):
    def test_host_invalid_error(self):
        resp = self.make_request(headers={'host': 'google.com'})
        self.assert_error_response(resp, ['host.invalid'])

    def test_container_invalid_error(self):
        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(status=BLACKBOX_CHECK_SIGN_STATUS_EXPIRED),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['container.invalid'],
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
        )

    def test_retpath_invalid_error(self):
        resp = self.make_request(query_args={'is_background': False, 'retpath': 'https://yandex.ru/'})
        self.assert_error_response(
            resp,
            ['retpath.invalid'],
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
        )

    def test_host_not_slave_error(self):
        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(json.dumps({
                'dst_domain': TEST_MASTER_DOMAIN,
                'cookies': self.get_expected_cookies_for_slave(),
                'cookie_check_value': str(TEST_COOKIE_CHECK_VALUE),
            })),
        )
        resp = self.make_request(
            headers={'host': TEST_HOST},
            query_args={'is_background': False, 'retpath': 'https://yandex.ru/'},
        )
        self.assert_error_response(
            resp,
            ['host.not_slave'],
            headers=self.expected_headers(domain=TEST_MASTER_DOMAIN),
            script_nonce=TEST_SCRIPT_NONCE,
        )

    def test_blackbox_temporary_error(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'check_sign',
            BlackboxTemporaryError,
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['backend.blackbox_failed'],
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
        )

    def test_inject_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok('inject', with_check_cookies=True)

    def test_inject_with_retpath_ok(self):
        resp = self.make_request(query_args={'retpath': TEST_RETPATH})
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            retpath=TEST_RETPATH,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok('inject', with_check_cookies=True)

    def test_install_ok(self):
        resp = self.make_request(query_args={'is_background': False, 'retpath': TEST_RETPATH})
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            retpath=TEST_RETPATH,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok('install', with_check_cookies=True)
        self.assert_blackbox_called(requests_count=2)

    def test_merge_ys_cookies(self):
        resp = self.make_request(
            headers={
                'cookie': TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YS,
            },
        )
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(ys_cookie=TEST_MERGED_YS_COOKIE),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok('inject', with_check_cookies=True)

    def test_no_session_cookie_ok(self):
        resp = self.make_request(
            query_args={'is_background': False, 'retpath': TEST_RETPATH},
            headers={'cookie': ''},
        )
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            retpath=TEST_RETPATH,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok(
            'install',
            old_auth_status='empty',
            old_auth_bb_status='None',
            _exclude=['yandexuid'],
        )
        self.assert_blackbox_called(requests_count=1)

    def test_invalid_session_cookie_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
                error='Error message',
            ),
        )
        resp = self.make_request(query_args={'is_background': False, 'retpath': TEST_RETPATH})
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            retpath=TEST_RETPATH,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok(
            'install',
            old_auth_status='noauth',
            old_auth_bb_status='Error message',
            with_check_cookies=True,
        )

    def test_same_site_issue29613(self):
        cookie = 'ya_sess_id=3:session_id; Domain=.%s; Path=/; SameSite=None' % TEST_SLAVE_DOMAIN

        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(json.dumps({
                'src_domain': TEST_MASTER_DOMAIN,
                'dst_domain': TEST_SLAVE_DOMAIN,
                'auth_cookie_valid': True,
                'cookies': [cookie],
                'cookie_check_value': str(TEST_COOKIE_CHECK_VALUE),
            })),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            cookies=[cookie],
            check_all=False,
            ignore_order_for=['cookies'],
        )


@with_settings_hosts(
    CUSTOM_MDA_DOMAIN_CONFIGS={
        TEST_SLAVE_DOMAIN: {
            'cookies': {
                'Session_id': 'ya_sess_id',
                'ys': 'ys',
            },
        },
    },
)
class UseContainerWithYSCookieTestcase(BaseUseContainerTestcase):
    def test_skip_merge_ys_cookies(self):
        resp = self.make_request(
            headers={
                'cookie': TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YS,
            },
        )
        self.assert_ok_response(
            resp,
            origin=TEST_MASTER_DOMAIN,
            current_domain=TEST_SLAVE_DOMAIN,
            auth_cookie_valid=True,
            cookie_check_value=str(TEST_COOKIE_CHECK_VALUE),
            cookies=self.get_expected_cookies_for_slave(),
            headers=self.expected_headers(),
            script_nonce=TEST_SCRIPT_NONCE,
            ignore_order_for=['cookies'],
        )
        self.assert_statbox_ok('inject', with_check_cookies=True)


class TestUseContainerYp(BaseUseContainerTestcase):
    http_headers = dict(
        BaseUseContainerTestcase.http_headers,
        cookie=TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YP,
    )

    def get_expected_cookies_for_slave(self, yp_cookie=Undefined, **kwargs):
        if yp_cookie is Undefined:
            yp_cookie = TEST_EXPECTED_YP_COOKIE_SLAVE
        return super(TestUseContainerYp, self).get_expected_cookies_for_slave(yp_cookie=yp_cookie, **kwargs)

    def test_not_configured(self):
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(yp_cookie=None),
            ignore_order_for=['cookies'],
        )

    def test_configured(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                TEST_SLAVE_DOMAIN: {'cookies': {'yp': 'yp'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(),
            ignore_order_for=['cookies'],
        )


class TestUseContainerMy(BaseUseContainerTestcase):
    http_headers = dict(
        BaseUseContainerTestcase.http_headers,
        cookie=TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_MY,
    )

    def get_expected_cookies_for_slave(self, my_cookie=Undefined, **kwargs):
        if my_cookie is Undefined:
            my_cookie = TEST_EXPECTED_MY_COOKIE_SLAVE
        return super(TestUseContainerMy, self).get_expected_cookies_for_slave(my_cookie=my_cookie, **kwargs)

    def test_not_configured(self):
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(my_cookie=None),
            ignore_order_for=['cookies'],
        )

    def test_configured(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                TEST_SLAVE_DOMAIN: {'cookies': {'my': 'my'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(),
            ignore_order_for=['cookies'],
        )


class TestUseContainerYandexGid(BaseUseContainerTestcase):
    http_headers = dict(
        BaseUseContainerTestcase.http_headers,
        cookie=TEST_SLAVE_DOMAIN_USER_COOKIES_WITH_CUSTOM_YANDEX_GID,
    )

    def get_expected_cookies_for_slave(self, yandex_gid_cookie=Undefined, **kwargs):
        if yandex_gid_cookie is Undefined:
            yandex_gid_cookie = TEST_EXPECTED_YANDEX_GID_COOKIE_SLAVE
        return super(TestUseContainerYandexGid, self).get_expected_cookies_for_slave(
            yandex_gid_cookie=yandex_gid_cookie,
            **kwargs
        )

    def test_not_configured(self):
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(yandex_gid_cookie=None),
            ignore_order_for=['cookies'],
        )

    def test_configured(self):
        with settings_context(
            inherit_all_existing=True,
            CUSTOM_MDA_DOMAIN_CONFIGS={
                TEST_SLAVE_DOMAIN: {'cookies': {'yandex_gid': 'yandex_gid'}},
            },
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            check_all=False,
            auth_cookie_valid=True,
            cookies=self.get_expected_cookies_for_slave(),
            ignore_order_for=['cookies'],
        )
