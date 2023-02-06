import django.core.exceptions as dce

import metrika.admin.python.clickhouse_rbac.frontend.rbac.models as rbac_models
import metrika.admin.python.clickhouse_rbac.frontend.rbac.idm.permissions as rbac_permissions

import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper


class TestClickHouseUser(tests_helper.ClickHouseRBACTestCase):
    def test_get_or_create_normal(self):
        user, created = rbac_models.ClickHouseUser.get_or_create(
            name='petya',
            source='local',
        )
        self.assertTrue(created)
        self.assertTrue(isinstance(user, rbac_models.ClickHouseUser))
        self.assertEqual(user.source, 'local')

    def test_get_or_create_exists(self):
        user, created = rbac_models.ClickHouseUser.get_or_create(
            name='vova',
            source='idm',
        )
        self.assertFalse(created)
        self.assertTrue(isinstance(user, rbac_models.ClickHouseUser))


class TestAccess(tests_helper.ClickHouseRBACTestCase):
    def test_get_or_create_normal(self):
        user = rbac_models.ClickHouseUser.objects.get(name='misha')
        access, created = rbac_models.Access.get_or_create(
            user=user,
            profile='analytics',
            quota='analytics',
            cluster=rbac_permissions.METRIKA_CLUSTER,
        )
        self.assertTrue(created)
        self.assertTrue(isinstance(access, rbac_models.Access))
        self.assertEqual(access.user, user)
        self.assertEqual(access.cluster, rbac_permissions.METRIKA_CLUSTER)

    def test_get_or_create_exists(self):
        user = rbac_models.ClickHouseUser.objects.get(name='vova')
        access, created = rbac_models.Access.get_or_create(
            user=user,
            profile='analytics',
            quota='analytics',
            cluster=rbac_permissions.METRIKA_CLUSTER,
        )
        self.assertFalse(created)
        self.assertTrue(isinstance(access, rbac_models.Access))
        self.assertEqual(access.user, user)
        self.assertEqual(access.cluster, rbac_permissions.METRIKA_CLUSTER)

    def test_delete_if_exists_normal(self):
        result = rbac_models.Access.delete_if_exists('vova', rbac_permissions.METRIKA_CLUSTER)
        self.assertTrue(result)

        with self.assertRaises(dce.ObjectDoesNotExist):
            rbac_models.Access.objects.get(user__name='vova', cluster=rbac_permissions.METRIKA_CLUSTER)

    def test_delete_if_exists_missing(self):
        with self.assertRaises(dce.ObjectDoesNotExist):
            rbac_models.Access.objects.get(user__name='misha', cluster=rbac_permissions.METRIKA_CLUSTER)

        result = rbac_models.Access.delete_if_exists('misha', rbac_permissions.METRIKA_CLUSTER)
        self.assertFalse(result)
