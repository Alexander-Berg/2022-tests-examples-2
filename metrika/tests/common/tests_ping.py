import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestPing(tests_helper.BishopTestCase):
    success_response = 'OK'

    def test_app(self):
        response = self.client.get('/ping/app')
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )

    def test_db_read(self):
        response = self.client.get('/ping/db_read')
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )

    def test_db_write(self):
        response = self.client.get('/ping/db_write')
        self.assertEqual(
            response.content.decode('utf-8'),
            self.success_response,
        )
