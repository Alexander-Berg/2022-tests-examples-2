import unittest.mock

import django_idm_api.exceptions as idm_exceptions

import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper
import metrika.admin.python.clickhouse_rbac.frontend.rbac.idm.permissions as rbac_permissions
import metrika.admin.python.clickhouse_rbac.frontend.rbac.idm.hooks as rbac_hooks


class TestHooks(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(rbac_permissions, 'get_idm_info', new=unittest.mock.Mock().method())
    def test_info(self):
        rbac_hooks.Hooks().info()
        rbac_permissions.get_idm_info.assert_called()

    @unittest.mock.patch.object(rbac_permissions, 'get_all_roles', new=unittest.mock.Mock().method())
    def test_all_roles(self):
        rbac_hooks.Hooks().get_all_roles()
        rbac_permissions.get_all_roles.assert_called()

    @unittest.mock.patch.object(rbac_permissions, 'add_role', new=unittest.mock.Mock().method())
    def test_add_role_impl_normal(self):
        rbac_hooks.Hooks().add_role_impl('vova', 'administrator', 'some fields')
        rbac_permissions.add_role.assert_called_with('vova', 'administrator')

    @unittest.mock.patch.object(rbac_permissions, 'add_role', new=unittest.mock.Mock().method())
    def test_add_role_impl_no_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_hooks.Hooks().add_role_impl('vova', None, 'some fields')
        rbac_permissions.add_role.assert_not_called()

    @unittest.mock.patch.object(rbac_permissions, 'remove_role', new=unittest.mock.Mock().method())
    def test_remove_role_impl_normal(self):
        rbac_hooks.Hooks().remove_role_impl('vova', 'administrator', 'data', 'is_fired')
        rbac_permissions.remove_role.assert_called_with('vova', 'administrator')

    @unittest.mock.patch.object(rbac_permissions, 'remove_role', new=unittest.mock.Mock().method())
    def test_remove_role_impl_no_role(self):
        with self.assertRaises(idm_exceptions.RoleNotFound):
            rbac_hooks.Hooks().remove_role_impl('vova', None, 'data', 'is_fired')
        rbac_permissions.remove_role.assert_not_called()
