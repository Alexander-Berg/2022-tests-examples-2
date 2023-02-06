# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.perimeter_api.tests.views.base import BaseViewsTestCase


class TestGetMdmPass(BaseViewsTestCase):
    http_method = 'GET'
    fixtures = ['default.json']

    def test_ok(self):
        response = self.make_request(
            url='/provisioning/get-mdm-pass/vasya',
        )
        self.assert_response_ok(
            response,
            b'mdmpass_1',
            decode_response=False,
        )

    def test_not_exists(self):
        response = self.make_request(
            url='/provisioning/get-mdm-pass/petya',
        )
        eq_(response.status_code, 404)
