import django.test

import metrika.admin.python.clickhouse_rbac.frontend.rbac.management.commands.sync_permissions as sp


class ClickHouseRBACTestCase(django.test.TestCase):
    fixtures = ('metrika/admin/python/clickhouse_rbac/frontend/rbac/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()
        sp.Command().assign_permissions({})
