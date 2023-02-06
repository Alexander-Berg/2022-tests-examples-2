# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.oauth.core.test.framework import ApiTestCase


class CheckInTestCase(ApiTestCase):
    http_method = 'GET'
    default_url = reverse_lazy('check_in')

    def default_params(self):
        return {
            'access_token': 'not_used',
        }

    def test_ok(self):
        rv = self.make_request()
        eq_(rv['status'], 'ok')
