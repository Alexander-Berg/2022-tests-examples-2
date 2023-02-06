import unittest.mock

import django.contrib.auth.models as auth_models
import django.core.exceptions as dce

import django_idm_api.exceptions as idm_exceptions

import metrika.admin.python.clickhouse_rbac.frontend.rbac.utils as rbac_utils
import metrika.admin.python.clickhouse_rbac.frontend.rbac.models as rbac_models
import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper
import metrika.admin.python.clickhouse_rbac.frontend.rbac.idm.permissions as rbac_permissions


class TestGetAllRoles(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        rbac_permissions.get_all_roles()


class TestGetClustersRoles(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        roles = rbac_permissions.get_clusters_roles()
        self.assertTrue(isinstance(roles, dict))


class TestGetIdmInfo(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        info = rbac_permissions.get_idm_info()
        self.assertTrue(isinstance(info, dict))


class TestCheckKnownAccessRole(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        for name in rbac_permissions.ACCESS_ROLES:
            rbac_permissions.check_known_access_role(name)

    def test_invalid(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.check_known_access_role('missing value')


class TestCheckKnownUiRole(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        for name in rbac_permissions.UI_ROLES:
            rbac_permissions.check_known_ui_role(name)

    def test_invalid(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.check_known_ui_role('missing value')


class TestCheckKnownCluster(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        for name in rbac_permissions.CLUSTERS:
            rbac_permissions.check_known_cluster(name)

    def test_invalid(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.check_known_cluster('missing value')


class TestGetGroupUsernames(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        rbac_permissions.get_group_usernames('ui_admins')

    def test_missing(self):
        with self.assertRaises(dce.ObjectDoesNotExist):
            rbac_permissions.get_group_usernames('missing group')


class TestAddRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'add_ui_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'add_cluster_role', new=unittest.mock.Mock(return_value=[None, None, None, None, 'uuid']))
    @unittest.mock.patch.object(rbac_permissions, 'check_known_access_role', new=unittest.mock.Mock().method())
    def test_ui_normal(self):
        role = {
            'access': 'ui',
            'role': 'role_name',
        }
        rbac_permissions.add_role('some_login', role)
        rbac_permissions.add_ui_role.assert_called_with('some_login', 'role_name')
        rbac_permissions.add_cluster_role.assert_not_called()
        rbac_permissions.check_known_access_role.asslert_called_with('ui')

    @unittest.mock.patch.object(rbac_permissions, 'add_ui_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'add_cluster_role', new=unittest.mock.Mock(return_value=[None, None, None, None, 'uuid']))
    @unittest.mock.patch.object(rbac_permissions, 'check_known_access_role', new=unittest.mock.Mock().method())
    def test_cluster_normal(self):
        role = {
            'access': 'clusters',
            'cluster': 'cluster_name',
        }
        rbac_permissions.add_role('some_login', role)
        rbac_permissions.add_ui_role.assert_not_called()
        rbac_permissions.add_cluster_role.assert_called_with('some_login', 'cluster_name')
        rbac_permissions.check_known_access_role.asslert_called_with('clusters')

    def test_no_access_in_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.add_role('some_login', 'somerole')


class TestRemoveRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'remove_ui_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'remove_cluster_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'check_known_access_role', new=unittest.mock.Mock().method())
    def test_ui_normal(self):
        role = {
            'access': 'ui',
            'role': 'role_name',
        }
        rbac_permissions.remove_role('some_login', role)
        rbac_permissions.remove_ui_role.assert_called_with('some_login', 'role_name')
        rbac_permissions.remove_cluster_role.assert_not_called()
        rbac_permissions.check_known_access_role.asslert_called_with('ui')

    @unittest.mock.patch.object(rbac_permissions, 'remove_ui_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'remove_cluster_role', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_permissions, 'check_known_access_role', new=unittest.mock.Mock().method())
    def test_cluster_normal(self):
        role = {
            'access': 'clusters',
            'cluster': 'cluster_name',
        }
        rbac_permissions.remove_role('some_login', role)
        rbac_permissions.remove_ui_role.assert_not_called()
        rbac_permissions.remove_cluster_role.assert_called_with('some_login', 'cluster_name')
        rbac_permissions.check_known_access_role.asslert_called_with('clusters')

    def test_no_access_in_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.remove_role('some_login', 'somerole')


class TestAddUiRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'check_known_ui_role', new=unittest.mock.Mock().method())
    def test_normal(self):
        user, created = rbac_permissions.add_ui_role('petya', 'administrator')
        self.assertTrue(isinstance(user, auth_models.User))
        self.assertTrue(created)
        self.assertTrue(user.has_perm('rbac.ui_admin'))
        rbac_permissions.check_known_ui_role.assert_called_with('administrator')

        user, created = rbac_permissions.add_ui_role('petya', 'administrator')
        self.assertTrue(isinstance(user, auth_models.User))
        self.assertFalse(created)

    def test_ivanlid_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.add_ui_role('petya', 'superadmin')


class TestRemoveUiRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'check_known_ui_role', new=unittest.mock.Mock().method())
    def test_normal(self):
        user = auth_models.User.objects.get(username='vova')
        self.assertTrue(user.has_perm('rbac.ui_admin'))

        result = rbac_permissions.remove_ui_role('vova', 'administrator')
        self.assertTrue(result)
        user = auth_models.User.objects.get(username='vova')
        self.assertFalse(user.has_perm('rbac.ui_admin'))
        rbac_permissions.check_known_ui_role.assert_called_with('administrator')

    def test_invalid_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.remove_ui_role('vova', 'superadmin')

    @unittest.mock.patch.object(rbac_permissions, 'check_known_ui_role', new=unittest.mock.Mock().method())
    def test_false_when_no_user(self):
        result = rbac_permissions.remove_ui_role('username does not exist', 'administrator')
        rbac_permissions.check_known_ui_role.assert_not_called()
        self.assertFalse(result)


class TestAddClusterRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'check_known_cluster', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(rbac_utils, 'store_password_to_yav', new=unittest.mock.Mock(return_value='secret_uuid'))
    def test_normal(self):
        user, user_created, access, access_created, secret_uuid = rbac_permissions.add_cluster_role(
            'petya', rbac_permissions.METRIKA_CLUSTER
        )
        self.assertTrue(isinstance(user, rbac_models.ClickHouseUser))
        self.assertTrue(isinstance(access, rbac_models.Access))
        self.assertTrue(user_created)
        self.assertTrue(access_created)
        self.assertEqual(user.source, 'idm')
        self.assertEqual(secret_uuid, 'secret_uuid')
        rbac_permissions.check_known_cluster.assert_called_with(rbac_permissions.METRIKA_CLUSTER)

        user, user_created, access, access_created, secret_uuid = rbac_permissions.add_cluster_role(
            'petya', rbac_permissions.METRIKA_CLUSTER
        )
        self.assertTrue(isinstance(user, rbac_models.ClickHouseUser))
        self.assertTrue(isinstance(access, rbac_models.Access))
        self.assertFalse(user_created)
        self.assertFalse(access_created)
        self.assertIsNone(secret_uuid)

    def test_invalid_cluster(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.add_cluster_role('petya', 'missing cluster')


class TestRemoveClusterRole(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'check_known_cluster', new=unittest.mock.Mock().method())
    def test_normal(self):
        result = rbac_permissions.remove_cluster_role('vova', rbac_permissions.METRIKA_CLUSTER)
        self.assertTrue(result)
        rbac_permissions.check_known_cluster.assert_called_with(rbac_permissions.METRIKA_CLUSTER)

        user = rbac_models.ClickHouseUser.objects.get(name='vova')
        with self.assertRaises(dce.ObjectDoesNotExist):
            rbac_models.Access.objects.get(user=user, cluster=rbac_permissions.METRIKA_CLUSTER)

        result = rbac_permissions.remove_cluster_role('vova', rbac_permissions.METRIKA_CLUSTER)
        self.assertFalse(result)

    def test_invalid_cluster(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_permissions.remove_cluster_role('vova', 'missing cluster')
