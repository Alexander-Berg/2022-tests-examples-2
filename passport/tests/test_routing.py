# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import (
    datetime,
    timedelta,
)
import json
from unittest import TestCase

from flask.testing import FlaskClient
from nose.tools import eq_
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings,
)
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import datetime_to_integer_unixtime
from passport.infra.daemons.yasmsapi.api.app import create_app
from passport.infra.daemons.yasmsapi.api.exceptions import (
    BaseError,
    InternalError,
    NoNumberOrRouteError,
    NoRights,
    NoSender,
)
from passport.infra.daemons.yasmsapi.api.grants import (
    get_grant_name_for_action,
    get_name_for_checking_grants,
)
from passport.infra.daemons.yasmsapi.api.views.base import (
    INTERNAL_ERROR_CODE,
    INTERNAL_ERROR_MESSAGE,
)
from passport.infra.daemons.yasmsapi.db import queries
from passport.infra.daemons.yasmsapi.db.connection import DBError

from .fake_db import FakeYasmsDB
from .test_data import (
    INITIAL_TEST_DB_DATA,
    TEST_CACHED_ROUTES,
    TEST_CONSUMER_IP,
    TEST_DEFAULT_ROUTE,
    TEST_DUMP_ACTION,
    TEST_PHONE,
    TEST_ROUTE,
    TEST_ROUTE_ACTION,
    TEST_SENDER,
)


_host = namedtuple('host', 'name id dc')


@with_settings(
    CURRENT_FQDN='yasms-dev.passport.yandex.net',
    HOSTS=[_host(name='yasms-dev.passport.yandex.net', id=0x7F, dc='i')],
)
class RoutingViewTestCase(TestCase):
    url = '/routing'

    def setUp(self):
        # создаем тестовый клиент
        app = create_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()

        self.patches = []

        self.grants = FakeGrants()
        self.patches.append(self.grants)

        self.db = FakeYasmsDB()
        self.patches.append(self.db)

        for patch in self.patches:
            patch.start()

        self.db.load_initial_data()
        self.setup_grants()
        self.clear_cache()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.clear_cache()

    def clear_cache(self):
        queries.ROUTES_CACHE = []
        queries.ROUTES_CACHE_UPDATED = 0

    def fill_cache(self):
        queries.ROUTES_CACHE = TEST_CACHED_ROUTES

    def set_cache_upd(self, dt):
        queries.ROUTES_CACHE_UPDATED = datetime_to_integer_unixtime(dt)

    @property
    def all_grants(self):
        return [
            get_grant_name_for_action('Routing'),
        ]

    @property
    def default_params(self):
        return {
            'sender': TEST_SENDER,
            'number': TEST_PHONE,
            'action': TEST_ROUTE_ACTION,
            'route': TEST_DEFAULT_ROUTE,
        }

    def setup_grants(self, grants_list=None):
        grants_list = self.all_grants if grants_list is None else grants_list
        self.grants.set_grants_return_value(
            {
                get_name_for_checking_grants(TEST_SENDER): {
                    u'grants': dict((grant.split('.') for grant in grants_list)),
                    u'networks': ['127.0.0.1'],
                },
            }
        )

    def assert_headers(self, resp):
        eq_(resp.headers.get('Content-Type'), 'application/json')
        eq_(resp.headers.get('Pragma'), 'no-cache')
        eq_(resp.headers.get('Cache-control'), 'private, max-age=0, no-cache, no-store, must-revalidate')
        eq_(resp.headers.get('Expires'), 'Thu, 01 Jan 1970 00:00:00 GMT')

    def assert_ok_response(self, resp, expected):
        eq_(resp.status_code, 200)
        expected.update(status='ok')
        data = json.loads(resp.data)
        iterdiff(eq_(data, expected))
        self.assert_headers(resp)

    def assert_error_response(self, resp, error_cls, status_code=200):
        eq_(resp.status_code, status_code)
        data = json.loads(resp.data)
        if issubclass(error_cls, BaseError):
            err_code = error_cls.code
            err_message = error_cls.message
        else:
            err_code = INTERNAL_ERROR_CODE
            err_message = INTERNAL_ERROR_MESSAGE
        expected = {
            'status': 'error',
            'error': err_code,
            'message': err_message,
        }
        iterdiff(eq_(data, expected))
        self.assert_headers(resp)

    def make_request(self, url=None, query_string=None, exclude_from_query=None, remote_addr=TEST_CONSUMER_IP):
        url = url or self.url
        query_string = merge_dicts(
            self.default_params,
            query_string or {},
        )
        exclude = exclude_from_query or []
        for key in exclude:
            query_string.pop(key, None)
        kwargs = {
            'query_string': query_string,
            'environ_base': {'REMOTE_ADDR': remote_addr},
        }
        return self.client.get(url, **kwargs)

    def test_empty_action__ok(self):
        query = {
            'action': '',
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, {})

    def test_form_invalid__error(self):
        resp = self.make_request(exclude_from_query=['sender'])
        self.assert_error_response(resp, NoSender)

    def test_no_grants__error(self):
        self.setup_grants(grants_list=[])
        resp = self.make_request()
        self.assert_error_response(resp, NoRights)

    def test_route_action__ok(self):
        resp = self.make_request()
        expected = {
            'number': TEST_PHONE,
            'route': TEST_DEFAULT_ROUTE,
            'possible_gates': [1, 7],
        }
        self.assert_ok_response(resp, expected)

    def test_route_action_not_enough_params__error(self):
        resp = self.make_request(exclude_from_query=['route'])
        self.assert_error_response(resp, NoNumberOrRouteError)

    def test_route_action_no_possible_gates__error(self):
        self.db.drop_tables(['smsrt'])
        query = {
            'route': TEST_ROUTE,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, InternalError)

    def test_dump_action__ok(self):
        query = {
            'action': TEST_DUMP_ACTION,
        }
        resp = self.make_request(query_string=query)
        expected = {
            'gates': INITIAL_TEST_DB_DATA['smsgates'],
            'routes': INITIAL_TEST_DB_DATA['smsrt'],
        }
        self.assert_ok_response(resp, expected)

    def test_dump_action_no_gates__error(self):
        self.db.drop_tables(['smsgates'])
        query = {
            'action': TEST_DUMP_ACTION,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, InternalError)

    def test_dump_action_no_routes__error(self):
        self.db.drop_tables(['smsrt'])
        query = {
            'action': TEST_DUMP_ACTION,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, InternalError)

    def test_route_action_from_cache__ok(self):
        self.fill_cache()
        self.set_cache_upd(datetime.now() + timedelta(days=2))

        resp = self.make_request()
        expected = {
            'number': TEST_PHONE,
            'route': TEST_DEFAULT_ROUTE,
            'possible_gates': [1, 7],
        }
        self.assert_ok_response(resp, expected)
        self.db.assert_not_called()

    def test_route_action_cache_expired__ok(self):
        self.fill_cache()
        self.set_cache_upd(datetime(2016, 1, 1, 0, 30))

        resp = self.make_request()
        expected = {
            'number': TEST_PHONE,
            'route': TEST_DEFAULT_ROUTE,
            'possible_gates': [1, 7],
        }
        self.assert_ok_response(resp, expected)
        self.db.assert_called()

    def test_dump_action_db_failed__error(self):
        """
        Получаем все гейты и роуты, бд недоступна.
        Ожидаемые вызовы к бд:
            1. Получение гейтов
            2. Получение роутов
        """
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result(INITIAL_TEST_DB_DATA['smsgates']),
                DBError(),
            ]
        )
        query = {
            'action': TEST_DUMP_ACTION,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, InternalError)

    def test_unhandled_exception(self):
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result(INITIAL_TEST_DB_DATA['smsgates']),
                ValueError('Test'),
            ]
        )
        query = {
            'action': TEST_DUMP_ACTION,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, ValueError, status_code=500)
