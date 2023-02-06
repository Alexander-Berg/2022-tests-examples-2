# -*- coding: utf-8 -*-
import json

from django.test import (
    Client,
    TestCase,
)
from django.test.utils import override_settings
from django_idm_api.constants import (
    IDM_CERT_ISSUERS,
    IDM_CERT_SUBJECTS,
)
from nose.tools import eq_
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
    TEST_INVALID_TICKET,
    TEST_TICKET,
)
import pytest


@pytest.mark.django_db
@override_settings(IDM_TVM_CLIENT_ID=TEST_CLIENT_ID_2)
class BaseViewsTestCase(TestCase):
    default_url = None
    http_method = 'GET'
    http_query_args = None
    http_headers = None

    def setUp(self):
        super(BaseViewsTestCase, self).setUp()
        self.client = Client()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={},
        ))
        self.fake_tvm_credentials_manager.start()

    def idm_cert_headers(self, is_valid=True):
        return {
            'HTTP_X_QLOUD_SSL_VERIFIED': 'SUCCESS' if is_valid else 'NONE',
            'HTTP_X_QLOUD_SSL_SUBJECT': IDM_CERT_SUBJECTS[-1],
            'HTTP_X_QLOUD_SSL_ISSUER': IDM_CERT_ISSUERS[-1],
        }

    def tvm_headers(self, is_valid=True):
        return {
            'HTTP_X_YA_SERVICE_TICKET': TEST_TICKET if is_valid else TEST_INVALID_TICKET,
        }

    def make_request(self, url=None, method=None, query_args=None, headers=None):
        url = url or self.default_url
        method = method or self.http_method
        method = method.lower()
        query_args = dict(self.http_query_args or {}, **(query_args or {}))
        headers = dict(self.http_headers or {}, **(headers or self.tvm_headers()))

        return getattr(self.client, method)(
            url,
            data=query_args,
            **headers
        )

    def assert_response_ok(self, response, expected_response_values, decode_response=True):
        eq_(response.status_code, 200, response)
        rv = json.loads(response.content) if decode_response else response.content
        eq_(
            rv,
            expected_response_values,
        )


class IDMAuthTests(object):
    def test_idm_cert_not_accepted(self):
        response = self.make_request(
            headers=self.idm_cert_headers(),
        )
        eq_(response.status_code, 403, response)

    def test_tvm_ticket_invalid(self):
        response = self.make_request(
            headers=self.tvm_headers(is_valid=False),
        )
        eq_(response.status_code, 403, response)
