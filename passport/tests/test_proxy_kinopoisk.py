# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose.tools import raises
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    FakeBlackbox,
)
from passport.backend.social.common.application import Application
from passport.backend.social.common.builders.blackbox import (
    BlackboxInvalidResponseError,
    BlackboxTemporaryError,
    BlackboxUnknownError,
)
from passport.backend.social.common.exception import (
    InternalProxylibError,
    InvalidTokenProxylibError,
    ProviderTemporaryUnavailableProxylibError,
)
from passport.backend.social.common.providers.Kinopoisk import Kinopoisk
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    EXTERNAL_APPLICATION_ID1,
    UID1,
    USER_IP2,
)
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test.test_case import TestCase


class KinopoiskTestCase(TestCase):
    def setUp(self):
        super(KinopoiskTestCase, self).setUp()
        passport.backend.social.proxylib.init()

        self._p = get_proxy(
            Kinopoisk.code,
            {'value': APPLICATION_TOKEN1},
            Application(
                id=EXTERNAL_APPLICATION_ID1,
                secret=APPLICATION_SECRET1,
            ),
        )

        self._fake_blackbox = FakeBlackbox()
        self._fake_blackbox.start()
        self._p.r.aux_data['user_ip'] = USER_IP2

    def tearDown(self):
        self._fake_blackbox.stop()
        super(KinopoiskTestCase, self).tearDown()

    def _set_blackbox_response(self, response=blackbox_sessionid_response(uid=UID1)):
        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                response,
            ],
        )


class TestGetProfile(KinopoiskTestCase):
    def test_basic(self):
        self._set_blackbox_response()
        rv = self._p.get_profile()
        self.assertEqual(
            rv,
            {
                'userid': UID1,
            },
        )
        requests = self._fake_blackbox.requests
        self.assertEqual(len(requests), 1)
        requests[0].assert_query_equals({
            'method': 'sessionid',
            'host': 'kinopoisk.ru',
            'sessionid': APPLICATION_TOKEN1,
            'userip': USER_IP2,
            'regname': 'yes',
            'full_info': 'yes',
            'format': 'json',
            'authid': 'yes',
            'aliases': 'all',
            'is_display_name_empty': 'yes',
        })

    @raises(InvalidTokenProxylibError)
    def test_blackbox_invalid_session_id_error(self):
        self._set_blackbox_response(blackbox_sessionid_response(status=BLACKBOX_SESSIONID_INVALID_STATUS))
        self._p.get_profile()

    @raises(ProviderTemporaryUnavailableProxylibError)
    def test_blackbox_temporary_error(self):
        self._set_blackbox_response(BlackboxTemporaryError)
        self._p.get_profile()

    @raises(InternalProxylibError)
    def test_bllackbox_invalid_response_error(self):
        self._set_blackbox_response(BlackboxInvalidResponseError)
        self._p.get_profile()

    @raises(InternalProxylibError)
    def test_blackbox_unknown_error(self):
        self._set_blackbox_response(BlackboxUnknownError)
        self._p.get_profile()
