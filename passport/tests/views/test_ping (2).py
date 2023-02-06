# -*- coding: utf-8 -*-
from passport.backend.perimeter.auth_api.test.utils import settings_context
from passport.backend.perimeter.tests.views.base import BaseViewTestCase
import yatest


class TestPing(BaseViewTestCase):
    def test_ok(self):
        ping_file_path = yatest.common.source_path('passport/backend/perimeter/deb/debian/ping.html')
        with settings_context(PING_TEST_FILE=ping_file_path):
            resp = self.client.get('/ping')
        assert resp.status_code == 200
        assert resp.data == b'Pong\n'

    def test_file_not_accessible(self):
        with settings_context(PING_TEST_FILE='not_existing_file.html'):
            resp = self.client.get('/ping')
        assert resp.status_code == 503
