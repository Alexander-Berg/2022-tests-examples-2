import django.test

import metrika.admin.python.cms.frontend.tests.helper as helper


class TestUI(helper.CmsBaseTestCase, django.test.TestCase):
    def test_main_redirect(self):
        response = self.client.get(
            '/',
        )
        self.assertEqual(response.status_code, 302)

    def test_task(self):
        response = self.client.get(
            '/ui/tasks/production-3',
        )
        self.assertEqual(response.status_code, 200)

    def test_missing_task(self):
        response = self.client.get(
            '/ui/tasks/taks-missing-88',
        )
        self.assertEqual(response.status_code, 404)

    def test_tasks_list(self):
        response = self.client.get(
            '/ui/tasks',
        )
        self.assertEqual(response.status_code, 200)

    def test_ajax_tasks(self):
        response = self.client.get(
            '/ui/ajax/tasks',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['html'])
        self.assertNotIn(
            ' NO_TASKS_MATCHED_MARKER ',
            data['html'],
        )
        self.assertIn(
            ' TASKS_MATCHED_MARKER ',
            data['html'],
        )

    def test_ajax_tasks_not_match_filter(self):
        response = self.client.get(
            '/ui/ajax/tasks?walle_id=14532475',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['html'])
        self.assertIn(
            ' NO_TASKS_MATCHED_MARKER ',
            data['html'],
        )
        self.assertNotIn(
            ' TASKS_MATCHED_MARKER ',
            data['html'],
        )

    def test_ajax_task_part(self):
        response = self.client.get(
            '/ui/ajax/tasks/production-3',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['html'])
