# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANTS_CONFIG,
    TEST_INTERNAL_HOST,
    TEST_TVM_TICKET,
)
from passport.backend.oauth.core.test.framework.testcases.api_testcase import ApiTestCase


class BundleApiTestCase(ApiTestCase):
    require_grants = True
    require_consumer = True

    def setUp(self):
        super(BundleApiTestCase, self).setUp()
        if not self.require_grants:
            self.fake_grants.set_data({})

    def assert_status_ok(self, rv):
        eq_(rv['status'], 'ok', msg=rv)

    def assert_response_ok(self, rv, **kwargs):
        eq_(
            rv,
            dict(status='ok', **kwargs),
        )

    def assert_status_error(self, rv, errors=None):
        eq_(rv['status'], 'error', msg=rv)
        if errors is not None:
            eq_(
                sorted(rv['errors']),
                sorted(errors),
            )

    def test_method_not_allowed(self):
        if self.default_url is None:
            return
        if self.http_method == 'POST':
            response = self.client.get(self.default_url)
        elif self.http_method == 'GET':
            response = self.client.post('%s' % self.default_url)
        eq_(response.status_code, 200)
        eq_(
            json.loads(response.content),
            {
                'status': 'error',
                'errors': ['method.not_allowed'],
            },
        )

    def test_no_grants(self):
        if self.default_url is None or not self.require_grants:
            return
        self.fake_grants.set_data({})
        rv = self.make_request(url=self.default_url)
        self.assert_status_error(rv, ['grants.missing'])

    def test_consumer_missing(self):
        if self.default_url is None or not self.require_consumer:
            return
        rv = self.make_request(url=self.default_url, exclude=['consumer'])
        self.assert_status_error(rv, ['consumer.missing'])

    def test_unknown_consumer(self):
        if self.default_url is None or not self.require_grants:
            return
        rv = self.make_request(url=self.default_url, consumer='unknown')
        self.assert_status_error(rv, ['grants.missing'])

    def test_ok_with_tvm_ticket(self):
        if self.default_url is None:
            return
        self.fake_grants.set_data(TEST_GRANTS_CONFIG)
        rv = self.make_request(
            url=self.default_url,
            consumer='tvm_dev',
            headers=dict(
                self.default_headers(),
                HTTP_HOST=TEST_INTERNAL_HOST,
                HTTP_X_YA_SERVICE_TICKET=TEST_TVM_TICKET,
            ),
        )
        # В некоторые ручки нужно передавать дополнительные параметры (например, token_id).
        # Поэтому тут не можем гарантировать отсутствие любых ошибок при вызове ручки.
        ok_('grants.missing' not in rv.get('errors', []))

    def test_tvm_ticket_invalid(self):
        if self.default_url is None or not self.require_grants:
            return
        self.fake_grants.set_data(TEST_GRANTS_CONFIG)
        rv = self.make_request(
            url=self.default_url,
            consumer='tvm_dev',
            headers=dict(self.default_headers(), HTTP_HOST=TEST_INTERNAL_HOST, HTTP_X_YA_SERVICE_TICKET='foo'),
        )
        self.assert_status_error(rv, ['tvm_ticket.invalid'])

    def test_tvm_ticket_missing(self):
        if self.default_url is None or not self.require_grants:
            return
        self.fake_grants.set_data(TEST_GRANTS_CONFIG)
        rv = self.make_request(
            url=self.default_url,
            consumer='tvm_dev',
            headers=dict(self.default_headers(), HTTP_HOST=TEST_INTERNAL_HOST),
        )
        self.assert_status_error(rv, ['grants.missing'])

    def test_tvm_ticket_invalid_src(self):
        if self.default_url is None or not self.require_grants:
            return
        self.fake_grants.set_data(TEST_GRANTS_CONFIG)
        rv = self.make_request(
            url=self.default_url,
            consumer='tvm_dev_2',
            headers=dict(
                self.default_headers(),
                HTTP_HOST=TEST_INTERNAL_HOST,
                HTTP_X_YA_SERVICE_TICKET=TEST_TVM_TICKET,
            ),
        )
        self.assert_status_error(rv, ['grants.missing'])
