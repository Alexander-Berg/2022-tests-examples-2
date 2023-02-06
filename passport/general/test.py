# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.logging_utils.faker.fake_tskv_logger import TskvLoggerFaker
from passport.backend.social.api.app import (
    create_app,
    prepare_interprocess_environment,
    prepare_intraprocess_environment,
)
from passport.backend.social.api.logging_settings import logging_settings_deinit
from passport.backend.social.common.chrono import now
from passport.backend.social.common.test.fake_other import FakeBuildRequestId
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import (
    RequestTestCaseMixin,
    ResponseTestCaseMixin,
    TestCase as _TestCase,
    TvmTestCaseMixin,
)


_STATBOX_TEMPLATES = {
    'base': {
        'tskv_format': 'social-api-log',
        'unixtime': lambda: str(now.i()),
    },
}


class _BaseTestCase(
    TvmTestCaseMixin,
    RequestTestCaseMixin,
    _TestCase,
):
    def _build_app(self):
        prepare_interprocess_environment()
        prepare_intraprocess_environment()
        return create_app()

    def setUp(self):
        super(_BaseTestCase, self).setUp()

        self._fake_redis = FakeRedisClient()
        redis_patch = RedisPatch(self._fake_redis)

        self._fake_grants_config = FakeGrantsConfig()

        self._fake_useragent = FakeUseragent()
        self._fake_blackbox = FakeBlackbox()
        self._fake_kolmogor = FakeKolmogor()
        self._fake_request_id = FakeBuildRequestId()
        self._fake_statbox = FakeStatboxLogger()

        self.__patches = [
            redis_patch,
            self._fake_useragent,
            self._fake_grants_config,
            self._fake_blackbox,
            self._fake_kolmogor,
            self._fake_request_id,
            self._fake_statbox,
        ]
        for patch in self.__patches:
            patch.start()

        self._app = self._build_app()
        self._client = self._app.test_client()
        self._session = self._build_session()

    def tearDown(self):
        logging_settings_deinit()
        for patch in reversed(self.__patches):
            patch.stop()
        super(_BaseTestCase, self).tearDown()


class ApiV2TestCase(_BaseTestCase):
    def _assert_ok_response(self, rv, expected, status_code=200):
        self.assertEqual(rv.status_code, status_code)
        rv = json.loads(rv.data)
        self.assertEqual(rv, expected)

    def _assert_error_response(self, rv, error_name, status_code=200, description=Undefined):
        self.assertEqual(rv.status_code, status_code)
        rv = json.loads(rv.data)
        self.assertIn('error', rv)
        self.assertEqual(rv['error']['name'], error_name)
        if description is not Undefined:
            self.assertEqual(rv['error']['description'], description)


class ApiV3TestCase(ResponseTestCaseMixin, _BaseTestCase):
    pass


class FakeStatboxLogger(TskvLoggerFaker):
    logger_class_module = 'passport.backend.social.api.statbox.StatboxLogger'
    templates = _STATBOX_TEMPLATES
