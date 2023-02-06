# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.oauth.core.test.framework import ApiTestCase


class PingTestCase(ApiTestCase):
    default_url = reverse_lazy('ping', args=['production'])

    def default_params(self):
        return {}

    @override_settings(YAUTH_TEST_USER=False)
    def test_ok(self):
        rv = self.make_request(decode_response=False)
        eq_(rv, 'Pong\n')
