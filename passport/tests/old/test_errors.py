# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.api.api.old.views import (
    error_404,
    error_500,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class ErrorHandlersTestCase(BaseTestCase):

    def test_404(self):
        resp = error_404(request=None)
        eq_(resp.status_code, 404)
        eq_(resp.content.decode(), 'Unknown url')

    def test_500(self):
        resp = error_500(request=None)
        eq_(resp.status_code, 500)
        eq_(resp.content.decode(), 'Server error')
