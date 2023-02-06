# -*- coding: utf-8 -*-
import json

from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.session import UseSessGuardContainerView
from passport.backend.core.builders.blackbox import BLACKBOX_CHECK_SIGN_STATUS_BROKEN
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_check_sign_response
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants


TEST_DST_DOMAIN_L3 = 'mail.yandex.ru'
TEST_RETPATH_L3 = 'https://mail.yandex.ru/some/path'
TEST_DST_DOMAIN_L3_2 = 'mail1.yandex.ru'
TEST_DST_DOMAIN_L4 = '1.mail.yandex.ru'
TEST_DST_DOMAIN_L4_2 = '1.mail.yandex.ru'
TEST_RETPATH_L4 = 'https://1.mail.yandex.ru/some/path'
TEST_SESSGUARD_COOKIE_TMPL = 'sessguard=1.sessguard; Path=/; Domain=.%s; Secure; HttpOnly'
TEST_CONTAINER = '123.abc' * 100

TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIE = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_USER_IP = '127.0.0.1'


class TestExtractMeaningfulLevel3Host(PassportTestCase):
    @parameterized.expand(
        [
            # L2
            ('yandex.ru', 'yandex.ru'),
            ('yandex.su', 'yandex.su'),
            ('yandex.com', 'yandex.com'),
            ('yandex.avia', 'yandex.avia'),
            ('yandex.com.tr', 'yandex.com.tr'),
            ('yandex.msk.ru', 'yandex.msk.ru'),
            # L3
            ('mail.yandex.ru', 'mail.yandex.ru'),
            ('mail.yandex.su', 'mail.yandex.su'),
            ('mail.yandex.com', 'mail.yandex.com'),
            ('mail.yandex.avia', 'mail.yandex.avia'),
            ('mail.yandex.com.tr', 'mail.yandex.com.tr'),
            ('mail.yandex.msk.ru', 'yandex.msk.ru'),
            # L4
            ('black.mail.yandex.ru', 'mail.yandex.ru'),
            ('black.mail.yandex.su', 'mail.yandex.su'),
            ('black.mail.yandex.com', 'mail.yandex.com'),
            ('black.mail.yandex.avia', 'mail.yandex.avia'),
            ('black.mail.yandex.com.tr', 'mail.yandex.com.tr'),
            ('black.mail.yandex.msk.ru', 'yandex.msk.ru'),
            # LXXX
            ('some.thing.at.black.mail.yandex.ru', 'mail.yandex.ru'),
            ('some.thing.at.black.mail.yandex.su', 'mail.yandex.su'),
            ('some.thing.at.black.mail.yandex.com', 'mail.yandex.com'),
            ('some.thing.at.black.mail.yandex.avia', 'mail.yandex.avia'),
            ('some.thing.at.black.mail.yandex.com.tr', 'mail.yandex.com.tr'),
            ('some.thing.at.black.mail.yandex.msk.ru', 'yandex.msk.ru'),
        ],
    )
    def test_extract_meaningful_level3_host(self, hostname, expected):
        result = UseSessGuardContainerView._extract_meaningful_level3_host(hostname)
        self.assertEqual(result, expected)


@with_settings_hosts
class TestUseSessGuardContainer(BaseBundleTestViews):
    default_url = '/1/bundle/session/sessguard_container/use/'
    http_method = 'post'
    consumer = 'dev'
    http_headers = dict(
        host=TEST_DST_DOMAIN_L3,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self, track_type='authorize'):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'session': ['use_sessguard_container']}))
        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'use_sessguard_container',
            mode='any_auth',
            yandexuid=TEST_YANDEXUID_COOKIE,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            event='use_sessguard_container',
            action='use_sessguard_container',
        )

    def setup_blackbox(self, sign_ok=True, sessguard_cookie_host=TEST_DST_DOMAIN_L3, retpath=TEST_RETPATH_L3):
        sessguard = TEST_SESSGUARD_COOKIE_TMPL % sessguard_cookie_host
        if sign_ok:
            value = json.dumps(
                {
                    'cookies': [sessguard],
                    'retpath': retpath,
                },
            )
            response = blackbox_check_sign_response(value=value)
        else:
            response = blackbox_check_sign_response(status=BLACKBOX_CHECK_SIGN_STATUS_BROKEN)
        self.env.blackbox.set_blackbox_response_value('check_sign', response)

    def test_unpack__ok(self):
        """ Распаковка проходит при совпадающих хостах """
        self.setup_blackbox()

        resp = self.make_request(
            query_args=dict(container=TEST_CONTAINER),
            headers=dict(host=TEST_DST_DOMAIN_L4_2),
        )

        self.assert_ok_response(
            resp,
            cookies=[TEST_SESSGUARD_COOKIE_TMPL % TEST_DST_DOMAIN_L3],
            retpath=TEST_RETPATH_L3,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'use_sessguard_container',
                retpath=TEST_RETPATH_L3,
                status='ok',
            ),
        ])

    def test_unpack__ok_different_l4(self):
        """ Распаковка проходит при совпадающих l3-хостах, разных l4 """
        self.setup_blackbox(sessguard_cookie_host=TEST_DST_DOMAIN_L4, retpath=TEST_RETPATH_L4)

        resp = self.make_request(query_args=dict(container=TEST_CONTAINER))

        self.assert_ok_response(
            resp,
            cookies=[TEST_SESSGUARD_COOKIE_TMPL % TEST_DST_DOMAIN_L4],
            retpath=TEST_RETPATH_L4,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'use_sessguard_container',
                retpath=TEST_RETPATH_L4,
                status='ok',
            ),
        ])

    def test_unpack__invalid_signature(self):
        """ Распаковка не проходит из-за неверной подписи """
        self.setup_blackbox(sign_ok=False)
        resp = self.make_request(query_args=dict(container=TEST_CONTAINER))

        self.assert_error_response(resp, error_codes=['container.invalid_signature'])
        self.assert_events_are_empty(None)

    def test_unpack__invalid_host(self):
        """ Распаковка не проходит из-за несовпадающего l3-домена """
        self.setup_blackbox()
        resp = self.make_request(
            query_args=dict(container=TEST_CONTAINER),
            headers=dict(host=TEST_DST_DOMAIN_L3_2),
        )

        self.assert_error_response(resp, error_codes=['container.invalid_host'])
        self.assert_events_are_empty(None)
