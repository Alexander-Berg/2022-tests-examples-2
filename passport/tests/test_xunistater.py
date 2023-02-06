# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from passport.backend.core.builders.xunistater import (
    get_xunistater,
    XunistaterPermanentError,
)
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_ERROR_RESPONSE,
    TEST_XUNISTATER_FAILED_RESPONSE,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    XUNISTATER_URL=u'http://local_xunistater/push',
    XUNISTATER_TIMEOUT=1,
    XUNISTATER_RETRIES=2,
)
class TestXunistater(TestCase):
    def _build_xunistater_request_data(self):
        return [{
            'metric_one_dmmm': {'value': 124},
            'tier=tag1;metric_two_dxxx': {'value': 0.24},
        }]

    def assert_xunistater_request_equal(self, request, request_data):
        request.assert_properties_equal(
            url='http://local_xunistater/push',
            method='POST',
            post_args=json.dumps(request_data, sort_keys=True),
        )

    def test_xunistater_ok(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
            request_data = self._build_xunistater_request_data()

            response = get_xunistater().push_metrics(request_data)
            self.assertDictEqual(
                response,
                TEST_XUNISTATER_OK_RESPONSE,
            )

            self.assertEqual(len(fake_xunistater.requests), 1)
            self.assert_xunistater_request_equal(fake_xunistater.requests[0], request_data)

    def test_xunistater_error(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_ERROR_RESPONSE), status=400)
            request_data = self._build_xunistater_request_data()

            with self.assertRaises(XunistaterPermanentError) as e:
                get_xunistater().push_metrics(request_data)

            self.assertEqual(
                str(e.exception),
                'Request failed with response={"status": "ERROR", "error": "Bad Xunistater request"} code=400',
            )

            self.assertEqual(len(fake_xunistater.requests), 1)
            self.assert_xunistater_request_equal(fake_xunistater.requests[0], request_data)

    def test_xunistater_failed(self):
        with FakeXunistater() as fake_xunistater:
            fake_xunistater.set_response_value('', TEST_XUNISTATER_FAILED_RESPONSE, status=500)
            request_data = self._build_xunistater_request_data()

            with self.assertRaises(XunistaterPermanentError) as e:
                get_xunistater().push_metrics(request_data)

            self.assertEqual(
                str(e.exception),
                'Xunistater is down. response=Failed to init code=500',
            )

            self.assertEqual(len(fake_xunistater.requests), 1)
            self.assert_xunistater_request_equal(fake_xunistater.requests[0], request_data)
