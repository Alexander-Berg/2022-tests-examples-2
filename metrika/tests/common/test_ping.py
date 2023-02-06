import unittest.mock as um

import django.test

import metrika.admin.python.cms.frontend.tests.helper as helper


class TestPing(helper.CmsBaseTestCase, django.test.TestCase):
    success_response = 'OK'

    def test_app(self):
        response = self.client.get('/ping/app')
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )

    def test_db_read(self):
        response = self.client.get('/ping/db_read')
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )

    def test_db_read_error_handling(self):
        with um.patch('metrika.admin.python.cms.frontend.cms.ping.read_ping') as read_mock:
            read_mock.side_effect = Exception("Error mock message")
            response = self.client.get('/ping/db_read')
            self.assertEqual(
                response.status_code,
                500,
            )
            self.assertIn(
                'Failed to read from database: Error mock message',
                response.content.decode('utf-8'),
            )

    def test_db_write(self):
        response = self.client.get('/ping/db_write')
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )

    def test_db_write_error_handling(self):
        with um.patch('metrika.admin.python.cms.frontend.cms.ping.write_ping') as read_mock:
            read_mock.side_effect = Exception("Error mock message")
            response = self.client.get('/ping/db_write')
            self.assertEqual(
                response.status_code,
                500,
            )
            self.assertIn(
                'Failed to write to database: Error mock message',
                response.content.decode('utf-8'),
            )
