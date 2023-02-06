# -*- coding: utf-8 -*-

import json
import logging.config

import mock
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    AvatarsLoggerFaker,
    TskvLoggerFaker,
)
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker.app import (
    create_app,
    prepare_interprocess_environment,
    prepare_intraprocess_environment,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.broker.cookies import decrypt_cookie
from passport.backend.social.broker.logging_settings import logging_settings_deinit
from passport.backend.social.broker.misc import generate_retpath
from passport.backend.social.common.misc import PLACE_QUERY
from passport.backend.social.common.task import (
    load_task_from_redis,
    Task,
)
from passport.backend.social.common.test.consts import REQUEST_ID1
from passport.backend.social.common.test.fake_other import (
    FakeBuildRequestId,
    FakeGenerateTaskId,
)
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.fake_useragent import (
    FakeUseragent,
    FakeZoraUseragent,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import (
    RequestTestCaseMixin,
    ResponseTestCaseMixin,
    TestCase as _TestCase,
    TvmTestCaseMixin,
)
from werkzeug.http import parse_cookie
from werkzeug.routing import Map as RoutingMap
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


_STATBOX_TEMPLATES = {
    'base': {
        'tskv_format': 'social-broker-log',
        'unixtime': lambda: str(now.i()),
    },
}


class _BaseTestCase(
    TvmTestCaseMixin,
    RequestTestCaseMixin,
    _TestCase,
):
    def setUp(self):
        super(_BaseTestCase, self).setUp()

        self._fake_generate_task_id = FakeGenerateTaskId()
        self._fake_build_request_id = FakeBuildRequestId()

        self._fake_redis = FakeRedisClient()
        self._redis_patch = RedisPatch(self._fake_redis)

        self._fake_useragent = FakeUseragent()
        self._fake_zora_useragent = FakeZoraUseragent()
        self._fake_blackbox = FakeBlackbox()

        self._fake_grants_config = FakeGrantsConfig()
        self._fake_statbox = FakeStatboxLogger()
        self._fake_long_statbox = FakeLongStatboxLogger()
        self._fake_avatars_logger = AvatarsLoggerFaker()

        self.__patches = [
            self._fake_generate_task_id,
            self._fake_build_request_id,
            self._redis_patch,
            self._fake_useragent,
            self._fake_blackbox,
            self._fake_grants_config,
            self._fake_statbox,
            self._fake_long_statbox,
            self._fake_avatars_logger,
            self._fake_zora_useragent,
        ]
        for patch in self.__patches:
            patch.start()

        prepare_interprocess_environment()
        prepare_intraprocess_environment()
        self._app = create_app()
        self._client = Client(self._app, BaseResponse)

        logging.config.dictConfig(dict(
            version=1,
            disable_existing_loggers=False,
            root=dict(
                level='DEBUG',
                handlers=['root'],
            ),
            handlers={
                'root': {
                    'class': 'logging.StreamHandler',
                },
            },
        ))

    def tearDown(self):
        logging_settings_deinit()
        for patch in reversed(self.__patches):
            patch.stop()
        super(_BaseTestCase, self).tearDown()

    def _assert_task_equals(self, task_id, expected):
        task = load_task_from_redis(self._fake_redis, task_id)
        self.assertEqual(task.to_json_dict(), expected.to_json_dict())


class TestCase(ResponseTestCaseMixin, _BaseTestCase):
    """
    Базовый класс для ручек InternalBrokerHandlerV2.
    """


class InternalBrokerHandlerV1TestCase(_BaseTestCase):
    """
    Базовый класс для ручек Handler (старые внутренние ручки).
    """
    def _assert_response_burns_session(self, rv):
        rv = json.loads(rv.data)
        self.assertIn('cookies', rv)
        cookie = parse_cookie(rv['cookies'][0].encode('ascii'))
        self.assertIn('track', cookie)
        self.assertEqual(cookie['track'], '')

    def _assert_response_forwards_to_url(self, rv, url):
        check_url_equals(self._get_redirect_url_from_response(rv), url)

    def _get_redirect_url_from_response(self, rv):
        rv = json.loads(rv.data)
        self.assertIn('location', rv)
        return rv['location']

    def _build_ok_retpath(self, url, task_id):
        return generate_retpath(url, PLACE_QUERY, status='ok', task_id=task_id)

    def _assert_ok_response(self, rv, response=None, skip=None):
        response = response or dict()
        skip = skip or []

        self.assertEqual(rv.status_code, 200, (rv.status_code, rv.data))

        rv = json.loads(rv.data)
        response = {k: response[k] for k in response if k not in skip}
        rv = {k: rv[k] for k in rv if k not in skip}
        self.assertEqual(rv, response)

    def _assert_error_response(self, rv, errors, retpath, response=None, retpath_kwargs=None,
                               skip=None):
        response = response or dict()
        retpath_kwargs = retpath_kwargs or dict()
        skip = skip or list()

        rv = json.loads(rv.data)

        self.assertIn('error', rv)
        self.assertEqual(rv['error']['code'], errors[0])

        if retpath is not None:
            self.assertIn('retpath', rv)
            self.assertEqual(
                rv['retpath'],
                self._build_fail_retpath(retpath, **retpath_kwargs),
            )
        else:
            self.assertNotIn('retpath', rv)

        self.assertIn('request_id', rv)
        self.assertEqual(rv['request_id'], REQUEST_ID1)

        tested_args = ['error', 'retpath', 'request_id']
        rv = {k: rv[k] for k in rv if k not in tested_args}
        rv = {k: rv[k] for k in rv if k not in skip}
        response = {k: response[k] for k in response if k not in tested_args}
        response = {k: response[k] for k in response if k not in skip}

        self.assertEqual(rv, response)

    def _build_fail_retpath(self, url, additional_args=None):
        return generate_retpath(url, PLACE_QUERY, status='error', additional_args=additional_args)

    def _assert_response_contains_session(self, rv, expected):
        task = self._get_session_from_response(rv)
        self.assertEqual(task.to_json_dict(), expected.to_json_dict())

    def _get_session_from_response(self, rv):
        rv = json.loads(rv.data)
        self.assertIn('cookies', rv)
        cookie = parse_cookie(rv['cookies'][0].encode('ascii'))
        self.assertIn('track', cookie)
        track_json = decrypt_cookie(cookie['track'])
        task = Task()
        task.parse_session_data(track_json)
        return task


class FakeStatboxLogger(TskvLoggerFaker):
    logger_class_module = 'passport.backend.social.broker.statbox.StatboxLogger'
    templates = _STATBOX_TEMPLATES


class FakeLongStatboxLogger(TskvLoggerFaker):
    logger_class_module = 'passport.backend.social.broker.statbox.LongStatboxLogger'
    templates = _STATBOX_TEMPLATES


class FakeRoutes(object):
    def __init__(self, application):
        self._app = application
        self._url_map = RoutingMap()
        self._view_functions = dict()
        self._url_map_patch = mock.patch.object(self._app, 'url_map', self._url_map)
        self._view_functions_patch = mock.patch.object(self._app, 'view_functions', self._view_functions)

    def start(self):
        self._url_map_patch.start()
        self._view_functions_patch.start()
        return self

    def stop(self):
        self._view_functions_patch.stop()
        self._url_map_patch.stop()

    def add(self, method, endpoint, handler_class):
        self._app.add_url_rule(
            endpoint,
            methods=[method],
            view_func=handler_class.as_view(),
        )
