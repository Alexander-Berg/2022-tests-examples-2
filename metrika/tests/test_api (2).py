import json
import django.test

import metrika.admin.python.duty.frontend.tests.helper as helper


class TestUI(helper.DutyBaseTestCase, django.test.TestCase):
    def _assert(self, url, code=200, result=True):
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            code,
        )
        if result:
            self.assertTrue(
                response.json()['result'],
                result,
            )
        else:
            self.assertFalse(
                response.json()['result'],
                result,
            )

    def test_duty_group(self):
        self._assert('/api/v1/project/awesome/duty_group/production-group/')

    def test_missing_duty_group(self):
        self._assert(
            '/api/v1/project/awesome/duty_group/missinggroup/',
            code=404,
            result=False,
        )

    def test_switch_duty(self):
        response = self.client.post(
            '/api/v1/project/awesome/duty_group/production-group/switch_duty/',
            json.dumps({"username": "frenz"}),
            content_type='application/json',
        )
        self.assertEqual(
            response.status_code,
            200,
        )
