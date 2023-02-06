# -*- coding: utf-8 -*-
import json
import logging
import re
import unittest

import mock
from nose.tools import eq_
from passport.backend.adm_api.app import create_app
from passport.backend.adm_api.test.client import FlaskTestClient
from passport.backend.adm_api.test.grants import FakeGrantsLoader
from passport.backend.adm_api.test.mock_objects import (
    mock_grants,
    mock_headers,
)
from passport.backend.adm_api.test.statbox import AdmStatboxLoggerFaker
from passport.backend.adm_api.test.yt_dt import FakeYtDt
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.historydb_api.faker.historydb_api import FakeHistoryDBApi
from passport.backend.core.builders.meltingpot_api.faker.fake_meltingpot_api import FakeMeltingpotApi
from passport.backend.core.builders.passport.faker.fake_passport import FakePassport
from passport.backend.core.builders.ufo_api.faker import FakeUfoApi
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.historydb.converter import EventEntryConverter
from passport.backend.core.services import SERVICES
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


log = logging.getLogger('passport_adm_api.tests.views')

eq_ = iterdiff(eq_)


TEST_COOKIE = 'Session_id=3:1408711252.5.0.1408710928000:vGUJJQ:7e.0|1.0.2|66585.705413.3SNybpx2D_aCv5wrBHfJs48odcY'
TEST_HOST = 'yandex-team.ru'
TEST_IP = '127.0.0.1'


class BaseViewTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP):
        return mock_headers(cookie=cookie, host=host, user_ip=ip)

    def make_request(self, method, path, params=None, data=None, headers=None):
        if params is None:
            params = {}

        params['consumer'] = 'dev'

        if method == 'GET':
            return self.env.client.get(
                path,
                query_string=params,
                headers=headers,
            )
        elif method == 'POST':
            return self.env.client.post(
                path,
                query_string=params,
                data=data,
                headers=headers,
            )

    def _check_response(self, resp, **response_values):
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        for field, value in response_values.items():
            eq_(resp[field], value)

    def check_response_ok(self, resp, **response_values):
        self._check_response(resp, status='ok', **response_values)

    def check_response_error(self, resp, error_list):
        self._check_response(resp, status='error', errors=error_list)

    def _get_log_field(self, field_name, log_type='event', log_msg=''):
        converter_cls = EventEntryConverter

        for value, name in zip(re.findall(r'(`.*?`|[^ ]+)', log_msg), converter_cls.fields):
            if name == field_name:
                return value.strip('`')

    def assert_events_are_empty(self, logger_handler_mock):
        """Проверить что event-лог не использовался"""
        eq_(logger_handler_mock.call_count, 0, 'Not empty call list: %s' % logger_handler_mock.call_args_list)

    def assert_events_are_logged(self, logger_handler_mock, names_values):
        """Проверить что только эти event-записи передавались в логгер"""
        admin = names_values.pop('admin', '-')
        comment = names_values.pop('comment', '-')
        eq_(len(names_values), logger_handler_mock.call_count, [names_values, logger_handler_mock.call_args_list])
        for call_arg in logger_handler_mock.call_args_list:
            name = self._get_log_field('name', 'event', call_arg[0][0])
            value = self._get_log_field('value', 'event', call_arg[0][0])

            # сравниваем значения из set, поэтому приходится сортировать
            if name == 'alias.old_public_id.rm':
                value = ','.join(sorted(value.split(',')))

            self.assertIn(name, names_values)
            eq_(value, names_values[name])
            if name == 'action' and (comment or admin):
                actual_admin = self._get_log_field('admin', 'event', call_arg[0][0])
                eq_(actual_admin, admin)
                actual_comment = self._get_log_field('comment', 'event', call_arg[0][0])
                eq_(actual_comment, comment)


class ViewsTestEnvironment(object):

    TEST_UID = 1
    TEST_PDD_UID = 1130000000000001

    def __init__(self, mock_dbm=False, mock_redis=False):
        # создаем тестовый клиент
        app = create_app()
        app.test_client_class = FlaskTestClient
        app.testing = True
        self.client = app.test_client()

        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.blackbox = FakeBlackbox()
        self.db = FakeDB()
        self.historydb_api = FakeHistoryDBApi()
        self.meltingpot_api = FakeMeltingpotApi()
        self.passport = FakePassport()
        self.grants_loader = FakeGrantsLoader()
        self.ufo_api = FakeUfoApi()
        self.yt_dt = FakeYtDt()

        # mock-аем и патчим логи historydb
        self.event_handle_mock = mock.Mock()
        self._event_logger = mock.Mock()
        self._event_logger.debug = self.event_handle_mock

        self.adm_statbox_logger = AdmStatboxLoggerFaker()

        self.patches = [
            mock.patch('passport.backend.core.serializers.logs.historydb.runner.event_log', self._event_logger),
            self.adm_statbox_logger,
            self.blackbox,
            self.db,
            self.grants_loader,
            self.historydb_api,
            self.meltingpot_api,
            self.passport,
            self.tvm_credentials_manager,
            self.ufo_api,
            self.yt_dt,
        ]

    def start(self):
        for patch in self.patches:
            patch.start()
        SERVICES['dev'].sid = 100400
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    '2': {
                        'alias': 'blackbox_intranet',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()
        SERVICES['dev'].sid = ''
