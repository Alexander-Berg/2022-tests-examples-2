import django.test

import metrika.admin.python.duty.frontend.tests.helper as helper


class TestUI(helper.DutyBaseTestCase, django.test.TestCase):
    def _assert(self, url, code=200, contains=None):
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            code,
        )
        if contains is not None:
            self.assertIn(
                contains,
                response.content.decode('utf-8'),
            )

    def test_main(self):
        self._assert('/')

    def test_duty_groups(self):
        self._assert('/project/awesome/')

    def test_duty_groups_part(self):
        self._assert('/project/awesome/parts/duty_groups/')

    def test_missing_project(self):
        self._assert('/project/notexist/')

    def test_missing_project_duty_groups(self):
        self._assert(
            '/project/notexist/parts/duty_groups/',
            contains='Project notexist does not exist',
        )

    def test_get_switch_duty_form(self):
        self._assert('/project/awesome/forms/duty_group/2/switch/')

    def test_get_add_group_form(self):
        self._assert('/project/awesome/forms/duty_group/add/')

    def test_get_change_group_form(self):
        self._assert('/project/awesome/forms/duty_group/2/change/')

    def test_stats(self):
        self._assert('/project/awesome/stats?group_api_key=production-group')

    def test_stats_part(self):
        self._assert('/project/awesome/parts/duty_groups/2/stats/')

    def test_audit(self):
        self._assert('/project/awesome/audit/')

    def test_audit_part(self):
        self._assert('/project/awesome/parts/audit/')

    def test_group_delete(self):
        response = self.client.post('/project/another/duty_group/3/delete/')
        self.assertEqual(
            response.status_code,
            200,
        )
