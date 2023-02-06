# coding: utf-8

from passport.backend.vault.api.models.user_role import UserRole
from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestUserRole(BaseTestClass):
    fill_database = False

    def test_empty_not_nulled_columns(self):
        with self.app.app_context():
            with self.assertRaises(ValueError) as e:
                UserRole()
            self.assertEqual(
                e.exception.message,
                'only_one: [\'uid\', \'abc_id\', \'staff_id\'], presents: []',
            )
