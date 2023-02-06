# -*- coding: utf-8 -*-

import inspect
import json
from os import path
from unittest import TestCase as _TestCase
from unittest.util import safe_repr

from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.utils import pseudo_diff
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    FakeTvmTicketChecker,
)
from passport.backend.social.common.application import Application
from passport.backend.social.common.context import request_ctx
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.session import Session
from passport.backend.social.common.social_config import social_config
from passport.backend.social.common.test import conf
from passport.backend.social.common.test.conf import settings_context
from passport.backend.social.common.test.db import FakeDb
from passport.backend.social.common.test.fake_chrono import FakeChronoManager
from passport.backend.social.common.test.fake_useragent import FakeRequest
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.useragent import Request


class TestCase(_TestCase):
    maxDiff = None
    longMessage = True

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.addTypeEqualityFunc(Application, self.assertApplicationEqual)
        self.addTypeEqualityFunc(FakeRequest, self.assertFakeRequestEqual)
        self.addTypeEqualityFunc(RefreshToken, self.assertRefreshTokenEqual)
        self.addTypeEqualityFunc(Request, self.assertRequestEqual)
        self.addTypeEqualityFunc(Token, self.assertTokenEqual)

    def setUp(self):
        settings_dict = self.build_settings()

        self._fake_db = FakeDb()
        self._fake_db.start()

        self._fake_settings = conf.FakeSettings(
            self._fake_db,
            settings_dict['providers'],
            settings_dict['applications'],
            settings_dict['social_config']
        )
        self._fake_settings.start()

        self.fake_chrono = FakeChronoManager()
        self.fake_chrono.start()

        social_config.init()

        self.request_ctx = request_ctx
        self.request_ctx.clear()

    def tearDown(self):
        self.request_ctx.clear()
        LazyLoader.flush()
        self.fake_chrono.stop()
        self._fake_settings.stop()
        self._fake_db.stop()

    def shortDescription(self):
        module_path = path.relpath(inspect.getsourcefile(type(self)))
        _, class_name, method_name = self.id().rsplit('.', 2)
        return '%s:%s.%s' % (module_path, class_name, method_name)

    def build_settings(self):
        return dict(
            providers=list(conf.DEFAULT_PROVIDERS),
            applications=list(conf.DEFAULT_APPLICATIONS),
            social_config=dict(conf.DEFAULT_SOCIAL_CONFIG),
        )

    def settings_context(self, settings):
        return settings_context(
            applications=settings['applications'],
            fake_db=self._fake_db,
            providers=settings['providers'],
            social_config=settings['social_config'],
        )

    def assertRequestEqual(self, request1, request2, msg=None):
        self.assertIsInstance(request1, Request, 'First argument is not a Request')
        self.assertIsInstance(request2, Request, 'Second argument is not a Request')
        self.assertDictEqual(request1.to_dict(), request2.to_dict())

    def assertApplicationEqual(self, app1, app2, msg=None):
        self.assertIsInstance(app1, Application, 'First argument is not a Application')
        self.assertIsInstance(app2, Application, 'Second argument is not a Application')
        self.assertDictEqual(dict(app1), dict(app2))

    def assertTokenEqual(self, token1, token2, msg=None):
        self.assertIsInstance(token1, Token, 'First argument is not a Token')
        self.assertIsInstance(token2, Token, 'Second argument is not a Token')
        self.assertDictEqual(token1.to_dict(), token2.to_dict())

    def assertRefreshTokenEqual(self, token1, token2, msg=None):
        self.assertIsInstance(token1, RefreshToken, 'First argument is not a RefreshToken')
        self.assertIsInstance(token2, RefreshToken, 'Second argument is not a RefreshToken')
        self.assertDictEqual(token1.to_dict(), token2.to_dict())

    def assertDictEqual(self, d1, d2, msg=None):
        self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')

        if d1 != d2:
            standardMsg = '%s != %s' % (safe_repr(d1, True), safe_repr(d2, True))
            diff = pseudo_diff(d1, d2)
            standardMsg += '\n' + diff
            self.fail(self._formatMessage(msg, standardMsg))

    def assertFakeRequestEqual(self, request1, request2, msg=None):
        self.assertIsInstance(request1, FakeRequest, 'First argument is not a FakeRequest')
        self.assertIsInstance(request2, FakeRequest, 'Second argument is not a FakeRequest')
        self.assertDictEqual(request1.to_dict(), request2.to_dict())

    def _build_session(self):
        return Session(write_conn=self._fake_db.get_engine())


class RequestTestCaseMixin(object):
    REQUEST_HTTP_METHOD = None
    REQUEST_URL = None
    REQUEST_HEADERS = None
    REQUEST_QUERY = None
    REQUEST_DATA = None

    def _make_request(self, http_method=None, url=None, headers=None,
                      exclude_headers=None, query=None, exclude_query=None,
                      data=None, exclude_data=None):
        http_method = http_method or self.REQUEST_HTTP_METHOD
        url = url or self.REQUEST_URL
        headers = build_dict_from_standard(self.REQUEST_HEADERS, headers, exclude_headers)
        query = build_dict_from_standard(self.REQUEST_QUERY, query, exclude_query)
        data = build_dict_from_standard(self._get_default_request_data(), data, exclude_data)
        return self._client.open(
            method=http_method,
            path=url,
            headers=headers,
            query_string=query,
            data=data,
        )

    def _get_default_request_data(self):
        return self.REQUEST_DATA


class ResponseTestCaseMixin(object):
    def _assert_ok_response(self, rv, response=None):
        response = response or dict()
        self.assertEqual(rv.status_code, 200)
        rv = json.loads(rv.data)
        self.assertEqual(rv, dict(response, status='ok'))

    def _assert_error_response(self, rv, errors, description=None):
        self.assertEqual(rv.status_code, 200)
        rv = json.loads(rv.data)
        self.assertEqual(rv['status'], 'error')
        self.assertEqual(sorted(rv['errors']), sorted(errors))
        if description is not None:
            self.assertEqual(rv['description'],  description)


class TvmTestCaseMixin(object):
    def setUp(self):
        super(TvmTestCaseMixin, self).setUp()

        self.tvm_credentials_config = dict(conf.DEFAULT_TVM_CREDENTIALS_CONFIG)

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(self.build_tvm_credentials_config())
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_ticket_checker = FakeTvmTicketChecker()
        self.fake_tvm_ticket_checker.start()

    def tearDown(self):
        self.fake_tvm_ticket_checker.stop()
        self.fake_tvm_credentials_manager.stop()
        super(TvmTestCaseMixin, self).tearDown()

    def build_tvm_credentials_config(self):
        return fake_tvm_credentials_data(ticket_data=self._ticket_data)

    def get_ticket_from_tvm_alias(self, tvm_alias):
        return self.tvm_credentials_config.get(tvm_alias, dict()).get('ticket')

    @property
    def _ticket_data(self):
        ticket_data = dict()
        for alias in self.tvm_credentials_config:
            client_id = self.tvm_credentials_config[alias]['client_id']
            ticket_data[client_id] = dict(
                alias=alias,
                ticket=self.tvm_credentials_config[alias]['ticket']
            )
        return ticket_data
