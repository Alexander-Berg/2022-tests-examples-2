import mock

import django.test
import metrika.admin.python.bishop.config_api.config_api.ping as ping


class TestPingHandler(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

    def test_app(self):
        response = self.client.get('/ping/app')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'OK')

    def test_database(self):
        response = self.client.get('/ping/database')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'OK')

    def test_database_error(self):
        exception_text = "test error"
        expected_code = 500
        expected_message = f"Failed to read from database: {exception_text}\n"

        with mock.patch.object(ping, 'read_from_db') as mock_func:
            mock_func.side_effect = Exception(exception_text)

            response = self.client.get('/ping/database')
            self.assertEqual(response.status_code, expected_code)
            self.assertEqual(response.content.decode('utf-8'), expected_message)
