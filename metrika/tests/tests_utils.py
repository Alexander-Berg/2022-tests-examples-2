import unittest.mock

from django.conf import settings

import library.python.vault_client as vc

import metrika.pylib.auth
import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper
import metrika.admin.python.clickhouse_rbac.frontend.rbac.utils as rbac_utils


class TestGeneratePassword(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        pwd, sha256 = rbac_utils.generate_password()
        self.assertTrue(isinstance(pwd, str))
        self.assertTrue(isinstance(sha256, str))


class TestStorePasswordToYav(tests_helper.ClickHouseRBACTestCase):
    @unittest.mock.patch.object(metrika.pylib.auth, 'get_robot_oauth_token', new=unittest.mock.Mock(return_value='toktoken'))
    @unittest.mock.patch.object(vc.VaultClient, 'create_secret', new=unittest.mock.Mock(return_value='pwd_uuid'))
    @unittest.mock.patch.object(vc.VaultClient, 'create_secret_version', new=unittest.mock.Mock(return_value='ver_uuid'))
    @unittest.mock.patch.object(vc.VaultClient, 'add_user_role_to_secret', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(vc.VaultClient, 'delete_user_role_from_secret', new=unittest.mock.Mock().method())
    def test_normal(self):
        robot_name = settings.CONFIG.robot_name
        uuid = rbac_utils.store_password_to_yav('vova', 'password_text')
        self.assertEqual(uuid, 'pwd_uuid')
        vc.VaultClient.create_secret.assert_called()
        vc.VaultClient.create_secret_version.assert_called_with('pwd_uuid', {'password': 'password_text'})
        vc.VaultClient.add_user_role_to_secret.assert_called_with('pwd_uuid', 'OWNER', login='vova')
        vc.VaultClient.delete_user_role_from_secret.assert_called_with('pwd_uuid', 'OWNER', login=robot_name)
