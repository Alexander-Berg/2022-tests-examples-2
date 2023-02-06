# -*- coding: utf-8 -*-
import json

from flask.testing import FlaskClient
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.perimeter.auth_api.app import execute_app
from passport.backend.perimeter.auth_api.test import BaseTestCase


class BaseViewTestCase(BaseTestCase):
    def setUp(self):
        app = execute_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()

        LazyLoader.flush()

    def check_response(self, response, expected_values):
        assert response.status_code == 200
        actual_values = json.loads(response.data)
        assert actual_values == expected_values, '%r != %r' % (actual_values, expected_values)
