# coding: utf-8

from passport.backend.vault.utils.roles import RoleAction

from .base import (
    BaseCLICommandRSATestCaseMixin,
    BaseCLICommandTestCase,
)


class TestCLIVaultClient(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    def test_get_abc_id_by_name(self):
        test_cases = [
            ('passp', '14',),
            ('passport', None),
            ('', None,),
        ]

        for t in test_cases:
            self.assertEqual(self.client.get_abc_id_by_name(t[0]), t[1])

    def test_get_staff_id_by_name(self):
        test_cases = [
            ('yandex_personal_com_aux_sec', '2864',),
            ('yandex_personal_com_aux', None),
            ('', None,),
        ]

        for t in test_cases:
            self.assertEqual(self.client.get_staff_id_by_name(t[0]), t[1])

    def test_resolve_services_ok(self):
        valid_test_cases = [
            (
                '+reader:abc:14:development',
                {'abc_id': '14', 'abc_scope': 'development'},
            ),
            (
                '+reader:abc:999999:development',
                {'abc_id': '999999', 'abc_scope': 'development'},
            ),
            (
                '+reader:abc:passp:development',
                {'abc_id': '14', 'abc_scope': 'development'},
            ),
            (
                '+reader:staff:2864',
                {'staff_id': '2864'},
            ),
            (
                '+reader:staff:999999',
                {'staff_id': '999999'},
            ),
            (
                '+reader:staff:yandex_personal_com_aux_sec:development',
                {'staff_id': '2864'},
            ),
        ]

        for t in valid_test_cases:
            self.assertDictEqual(
                self.client.resolve_services(
                    RoleAction.from_string(t[0]).as_method_params(),
                ),
                t[1],
            )

    def test_resolve_services_fail(self):
        invalid_test_cases = [
            (
                '+reader:abc:unknown:unknown',
                '"unknown" is an unknown ABC service name',
            ),
            (
                '+reader:staff:unknown',
                '"unknown" is an unknown Staff service name',
            ),
        ]

        for t in invalid_test_cases:
            with self.assertRaises(self.client.ClientError) as e:
                self.client.resolve_services(
                    RoleAction.from_string(t[0]).as_method_params(),
                )
            self.assertEqual(
                e.exception.kwargs['message'],
                t[1],
            )
