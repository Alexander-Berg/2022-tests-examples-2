# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import eq_
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.env import Environment
from passport.backend.oauth.core.test.base_test_data import (
    TEST_HOST,
    TEST_REMOTE_ADDR,
    TEST_REQUEST_ID,
)
from passport.backend.oauth.core.test.framework import YandexAwareClient
from passport.backend.oauth.core.test.framework.testcases.db_testcase import DBTestCase
from passport.backend.oauth.core.test.framework.testcases.mixins import PatchesMixin
from passport.backend.oauth.core.test.utils import (
    check_tskv_log_entries,
    check_tskv_log_entry,
)


TEST_UID = 1


class ApiTestCase(DBTestCase, PatchesMixin):
    default_url = None
    http_method = 'GET'

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.patch_environment()

        self.client = YandexAwareClient(
            HTTP_X_REAL_SCHEME='https',
            HTTP_X_REQUEST_ID=TEST_REQUEST_ID,
            SERVER_NAME=TEST_HOST,
        )

        self.env = Environment(
            user_ip=TEST_REMOTE_ADDR,
            consumer_ip=TEST_REMOTE_ADDR,
            user_agent=None,
            raw_cookies='',
            cookies={},
            host=TEST_HOST,
            request_id=TEST_REQUEST_ID,
            authorization=None,
            service_ticket=None,
            user_ticket=None,
        )

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            redirect_uris=['https://callback'],
            default_title='Тестовое приложение',
            icon='http://icon',
            icon_id='gid/client_id-abc',
            homepage='http://homepage',
            default_description='Test client',
        )) as client:
            self.test_client = client
            client.created = client.modified = datetime.now() - timedelta(hours=1)

    def tearDown(self):
        self.stop_patches()

    def make_request(self, url=None, http_method=None, decode_response=True, expected_status=200,
                     expected_content_type=None, headers=None, exclude=None, **kwargs):
        params = dict(self.default_params(), **kwargs)
        for param in (exclude or []):
            params.pop(param, None)
        request_args = dict(
            path=url or self.default_url,
            data=params,
            **(headers or self.default_headers())
        )
        http_method = http_method or self.http_method
        if http_method == 'POST':
            response = self.client.post(**request_args)
        elif http_method == 'GET':
            response = self.client.get(**request_args)
        else:
            raise ValueError('Unhandled HTTP method')  # pragma: no cover
        eq_(response.status_code, expected_status, msg=(response.status_code, response.content))
        if expected_content_type is None:
            expected_content_type = 'application/json' if decode_response else 'text/html; charset=utf-8'
        eq_(response['Content-Type'], expected_content_type)
        if decode_response:
            return json.loads(response.content)
        else:
            return response.content.decode()

    def default_headers(self):
        return {
            'HTTP_HOST': 'oauth.yandex.ru',
            'HTTP_USER_AGENT': 'curl',
        }

    def default_params(self):
        raise NotImplementedError()  # pragma: no cover

    @property
    def base_historydb_entry(self):
        return {
            'timestamp': TimeNow(),
        }

    def check_historydb_event_entries(self, entries):
        combined_entries = [
            dict(self.base_historydb_entry, **entry)
            for entry in entries
        ]
        check_tskv_log_entries(
            self.event_log_handle_mock,
            combined_entries,
        )

    def check_historydb_event_entry(self, entry, entry_index=-1):
        check_tskv_log_entry(
            self.event_log_handle_mock,
            dict(self.base_historydb_entry, **entry),
            entry_index=entry_index,
        )
