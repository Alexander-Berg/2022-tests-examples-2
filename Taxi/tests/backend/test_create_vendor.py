# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import logging

from odoo.tests.common import SavepointCase, tagged, Form

_logger = logging.getLogger(__name__)


@tagged('lavka', 'form', 'vendor')
class TestVendorForm(SavepointCase):

    def test_vendor_create(self):
        vendor_form = Form(self.env['res.partner'])
        self.assertIsNot(vendor_form, 'vendor_form created')

    def test_vendor_create_same_tax_id(self):

        self.v1_vat = 'v1-vat'
        self.v1 = self.env['res.partner'].create(
            {
                'name': 'v-001: assort_base',
                'is_company': True,
                'supplier_rank': 1,
                'vat': self.v1_vat,
            }
        )

        error_string = f'Partner with Tax ID "{self.v1_vat}" already exists.'
        with self.assertRaises(Exception) as context:
            self.v1 = self.env['res.partner'].create(
                {
                    'name': 'v-001: assort_base',
                    'is_company': True,
                    'supplier_rank': 1,
                    'vat': self.v1_vat,
                }
            )

        self.assertTrue(error_string == context.exception.args[0])
