from django.test.utils import override_settings

import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper


class TestPings(tests_helper.ClickHouseRBACTestCase):
    def test_ping(self):
        response = self.client.get('/ping/app')
        self.assertEqual(response.status_code, 200)

    def test_db_read(self):
        response = self.client.get('/ping/db_read')
        self.assertEqual(response.status_code, 200)
