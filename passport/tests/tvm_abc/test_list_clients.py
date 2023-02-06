# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.urls import reverse_lazy
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient
from passport.backend.oauth.tvm_api.tvm_api.tvm_abc.utils import client_to_response

from .base import (
    BaseTvmAbcTestcase,
    TEST_ABC_REQUEST_ID,
    TEST_ABC_SERVICE_ID,
    TEST_UID,
)


class ListClientsTestcase(BaseTvmAbcTestcase):
    default_url = reverse_lazy('tvm_abc_list_clients')
    http_method = 'GET'

    def setUp(self):
        super(ListClientsTestcase, self).setUp()

        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test Client 2',
        )) as client:
            client.abc_service_id = TEST_ABC_SERVICE_ID + 1
            client.abc_request_id = TEST_ABC_REQUEST_ID + 1
            self.test_client_2 = client

        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test Client without ABC',
        )):
            pass

        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test Client Deleted',
        )) as client:
            client.deleted = datetime.now() - timedelta(seconds=10)

        with CREATE(TVMClient.create(
                creator_uid=TEST_UID,
                name='Test Client 3',
        )) as client:
            client.abc_service_id = TEST_ABC_SERVICE_ID + 2
            client.abc_request_id = TEST_ABC_REQUEST_ID + 2
            self.test_client_3 = client

    def default_params(self):
        return {
            'consumer': 'dev',
        }

    def default_headers(self):
        return {}

    def expected_response(self, clients=None, next_page=None):
        return {
            'status': 'ok',
            'content': [
                client_to_response(client, full_info=False)
                for client in (clients or [])
            ],
            'meta': {
                'next_page': next_page,
            },
        }

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client, self.test_client_2, self.test_client_3]),
        )

    def test_paginated_ok(self):
        rv = self.make_request(page=1, page_size=4)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client, self.test_client_2], next_page=2),
        )

        rv = self.make_request(page=2, page_size=4)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client_3]),
        )

    def test_paginated_extra_empty_pages(self):
        rv = self.make_request(page=1, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client], next_page=2),
        )

        rv = self.make_request(page=2, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client_2], next_page=3),
        )

        rv = self.make_request(page=3, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([], next_page=4),  # здесь мы не стали выводить приложение без abc_service_id
        )

        rv = self.make_request(page=4, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([], next_page=5),  # здесь мы не стали выводить удалённое приложение
        )

        rv = self.make_request(page=5, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([self.test_client_3], next_page=6),
        )

        rv = self.make_request(page=6, page_size=1)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response([]),  # предыдущая страница была полностью заполнена, поэтому появилась эта
        )
