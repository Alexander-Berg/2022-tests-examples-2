# coding: utf-8

from passport.backend.vault.api.models.external_record import ExternalType
from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestExternalRecord(BaseTestClass):
    fill_database = False

    def test_unknown_external_type(self):
        ext_dec = ExternalType()

        with self.assertRaises(ValueError) as e:
            ext_dec.process_bind_param('unknown', None)
        self.assertEqual(
            e.exception.message,
            '"unknown" is an unknown external type',
        )

        with self.assertRaises(ValueError) as e:
            ext_dec.process_result_value('unknown', None)
        self.assertEqual(
            e.exception.message,
            '"unknown" is an unknown external type',
        )
