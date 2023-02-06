import datetime
import uuid

from odoo.tests import tagged
from odoo.tests.common import SavepointCase

rnd = lambda x: f'{x}-{uuid.uuid4().hex}'


@tagged('lavka', 'oebs')
class TestOEBSSync(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.v1_vat = rnd('v1-vat')
        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-001: assort_base',
                'is_company': True,
                'supplier_rank': 1,
                'vat': cls.v1_vat,
            }
        )

        cls.v2_vat = rnd('v2-vat')
        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-002',
                'is_company': True,
                'supplier_rank': 1,
                'vat': cls.v2_vat,
            }
        )

        cls.v3_vat = rnd('v3-vat')
        cls.v3 = cls.env['res.partner'].create(
            {
                'name': 'v-003',
                'is_company': True,
                'supplier_rank': 1,
                'vat': cls.v3_vat,
            }
        )

    def test_001_supplier_remap(self):
        yt_row = {
            'OBJECT_ID': '300',
            'EXPORT_DATE': '300',
            'ORG_ID': '300',
            'ORG_NAME': '300',
            'VENDOR_ID': '300',
            'VENDOR_SITE_ID': '300',
            'VENDOR_SITE_CODE': '300',
            'FOREIGN_SUPPLIER': '300',
            'VENDOR_NAME': '300',
            'VENDOR_NAME_ALT': '300',
            'ADDRESS_LINE1': '300',
            'ADDRESS_LINE2': '300',
            'INN': '300',
            'KPP': '300',
            'PHONE': '300',
            'EMAIL_ADDRESS': '300',
            'SPAM': 'hello',
        }
        mapping = self.env['oebs.supplier'].YT_MAPPING

        self.assertEqual(
            self.env['oebs.supplier']._remap(yt_row, mapping),
            {
                'object_id': '300',
                'export_date': datetime.date(1970, 1, 1),
                'org_id': '300',
                'org_name': '300',
                'vendor_id': '300',
                'vendor_site_id': '300',
                'vendor_site_code': '300',
                'foreign_supplier': '300',
                'vendor_name': '300',
                'vendor_name_alt': '300',
                'address_line1': '300',
                'address_line2': '300',
                'inn': '300',
                'kpp': '300',
                'phone': '300',
                'email_address': '300',
            }
        )

    def test_002_supplier_sync_yt_row(self):
        yt_rows = [
            {
                'OBJECT_ID': '300',
                'EXPORT_DATE': '300',
                'ORG_ID': '300',
                'ORG_NAME': '300',
                'VENDOR_ID': '300',
                'VENDOR_SITE_ID': '300',
                'VENDOR_SITE_CODE': '300',
                'FOREIGN_SUPPLIER': '300',
                'VENDOR_NAME': '300',
                'VENDOR_NAME_ALT': '300',
                'ADDRESS_LINE1': '300',
                'ADDRESS_LINE2': '300',
                'INN': self.v1_vat,
                'KPP': '',
                'PHONE': '300',
                'EMAIL_ADDRESS': '300',
                'SPAM': 'hello',
            },
            {
                'OBJECT_ID': '301',
                'EXPORT_DATE': '301',
                'ORG_ID': '301',
                'ORG_NAME': '301',
                'VENDOR_ID': '301',
                'VENDOR_SITE_ID': '301',
                'VENDOR_SITE_CODE': '301',
                'FOREIGN_SUPPLIER': '301',
                'VENDOR_NAME': '301',
                'VENDOR_NAME_ALT': '301',
                'ADDRESS_LINE1': '301',
                'ADDRESS_LINE2': '301',
                'INN': '',
                'KPP': self.v2_vat,
                'PHONE': '301',
                'EMAIL_ADDRESS': '301',
                'SPAM': 'hello',
            },
            {
                'OBJECT_ID': '302',
                'EXPORT_DATE': '302',
                'ORG_ID': '302',
                'ORG_NAME': '302',
                'VENDOR_ID': '302',
                'VENDOR_SITE_ID': '302',
                'VENDOR_SITE_CODE': '302',
                'FOREIGN_SUPPLIER': '302',
                'VENDOR_NAME': '302',
                'VENDOR_NAME_ALT': '302',
                'ADDRESS_LINE1': '302',
                'ADDRESS_LINE2': '302',
                'INN': self.v3_vat,
                'KPP': self.v3_vat,
                'PHONE': '302',
                'EMAIL_ADDRESS': '302',
                'SPAM': 'hello',
            },
            {
                'OBJECT_ID': '303',
                'EXPORT_DATE': '303',
                'ORG_ID': '303',
                'ORG_NAME': '303',
                'VENDOR_ID': '303',
                'VENDOR_SITE_ID': '303',
                'VENDOR_SITE_CODE': '303',
                'FOREIGN_SUPPLIER': '303',
                'VENDOR_NAME': '303',
                'VENDOR_NAME_ALT': '303',
                'ADDRESS_LINE1': '303',
                'ADDRESS_LINE2': '303',
                'INN': rnd('vat-x'),
                'KPP': rnd('vat-y'),
                'PHONE': '303',
                'EMAIL_ADDRESS': '303',
                'SPAM': 'hello',
            },
        ]

        for yt_row in yt_rows:
            yt_row = self.env['oebs.supplier']._remap(
                yt_row,
                self.env['oebs.supplier'].YT_MAPPING,
            )
            self.env['oebs.supplier']._sync_yt_row(yt_row)

        oebs_sups = self.env['oebs.supplier'].search([])
        self.assertEqual(
            len(oebs_sups), 3, 'из оебса засосали 3',
        )

        our_sups = self.env['res.partner'].search(
            [
                ('vat', 'in', [self.v1_vat, self.v2_vat, self.v3_vat]),
            ]
        )
        self.assertEqual(
            len(our_sups), 3, '3 поставщика в бд с ватами',
        )

        for our_sup in our_sups:
            self.assertIn(
                our_sup.vat,
                [our_sup.oebs_supplier_id.inn, our_sup.oebs_supplier_id.kpp],
                'залинковали по вату',
            )

    def test_003_contract_remap(self):
        yt_row = {
            'OBJECT_ID': '300',
            'EXPORT_DATE': '300',
            'ORG_ID': '300',
            'ORG_NAME': '300',
            'VENDOR_ID': '300',
            'VENDOR_SITE_ID': '300',
            'VENDOR_SITE_CODE': '300',
            'PO_HEADER_ID': '300',
            'PO': '300',
            'COORDINATOR': '300',
            'TERMS_ID': '300',
            'TERMS_NAME': '300',
            'CONTRACT_NUMBER': '300',
            'MVP': '300',
            'MVP_DESCRIPTION_RUS': '300',
            'MVP_DESCRIPTION_ENG': '300',
            'AGREEMENT_DATE': '1970-01-01 00:00:00',
            'START_DATE': '1970-01-02 00:00:00',
            'END_DATE': '1970-01-03 00:00:00',
            'CURRENCY': '300',
        }
        mapping = self.env['oebs.contract'].YT_MAPPING

        self.assertEqual(
            self.env['oebs.contract']._remap(yt_row, mapping),
            {
                'object_id': '300',
                'export_date': datetime.date(1970, 1, 1),
                'org_id': '300',
                'org_name': '300',
                'vendor_id': '300',
                'vendor_site_id': '300',
                'po_header_id': '300',
                'po': '300',
                'coordinator': '300',
                'vendor_site_code': '300',
                'terms_id': '300',
                'terms_name': '300',
                'contract_number': '300',
                'mvp': '300',
                'mvp_description_rus': '300',
                'mvp_description_eng': '300',
                'agreement_date': datetime.date(1970, 1, 1),
                'start_date': datetime.date(1970, 1, 2),
                'end_date': datetime.date(1970, 1, 3),
                'currency': '300',

            }
        )

    def test_004_contract_sync_yt_row(self):
        sup_yt_rows = [
            {
                'OBJECT_ID': '300',
                'EXPORT_DATE': '300',
                'ORG_ID': '300',
                'ORG_NAME': '300',
                'VENDOR_ID': '300',
                'VENDOR_SITE_ID': '300',
                'VENDOR_SITE_CODE': '300',
                'FOREIGN_SUPPLIER': '300',
                'VENDOR_NAME': '300',
                'VENDOR_NAME_ALT': '300',
                'ADDRESS_LINE1': '300',
                'ADDRESS_LINE2': '300',
                'INN': self.v1_vat,
                'KPP': '',
                'PHONE': '300',
                'EMAIL_ADDRESS': '300',
                'SPAM': 'hello',
            },
            {
                'OBJECT_ID': '301',
                'EXPORT_DATE': '301',
                'ORG_ID': '301',
                'ORG_NAME': '301',
                'VENDOR_ID': '301',
                'VENDOR_SITE_ID': '301',
                'VENDOR_SITE_CODE': '301',
                'FOREIGN_SUPPLIER': '301',
                'VENDOR_NAME': '301',
                'VENDOR_NAME_ALT': '301',
                'ADDRESS_LINE1': '301',
                'ADDRESS_LINE2': '301',
                'INN': '',
                'KPP': self.v2_vat,
                'PHONE': '301',
                'EMAIL_ADDRESS': '301',
                'SPAM': 'hello',
            },
        ]

        for yt_row in sup_yt_rows:
            yt_row = self.env['oebs.supplier']._remap(
                yt_row,
                self.env['oebs.supplier'].YT_MAPPING,
            )
            self.env['oebs.supplier']._sync_yt_row(yt_row)

        oebs_sups = self.env['oebs.supplier'].search([])
        self.assertEqual(
            len(oebs_sups), 2, 'из оебса засосали 2',
        )

        contract_yt_rows = [
            {
                'OBJECT_ID': '300',
                'EXPORT_DATE': '300',
                'ORG_ID': '300',
                'ORG_NAME': '300',
                'VENDOR_ID': '300',
                'VENDOR_SITE_ID': '300',
                'VENDOR_SITE_CODE': '300',
                'PO_HEADER_ID': '300',
                'PO': '300',
                'COORDINATOR': '300',
                'TERMS_ID': '300',
                'TERMS_NAME': '300',
                'CONTRACT_NUMBER': '300',
                'MVP': '300',
                'MVP_DESCRIPTION_RUS': '300',
                'MVP_DESCRIPTION_ENG': '300',
                'AGREEMENT_DATE': '1970-01-01 00:00:00',
                'START_DATE': '1970-01-02 00:00:00',
                'END_DATE': '1970-01-03 00:00:00',
                'CURRENCY': '300',
            },
            {
                'OBJECT_ID': '500',
                'EXPORT_DATE': '500',
                'ORG_ID': '500',
                'ORG_NAME': '500',
                'VENDOR_ID': '500',
                'VENDOR_SITE_ID': '500',
                'VENDOR_SITE_CODE': '500',
                'PO_HEADER_ID': '500',
                'PO': '500',
                'COORDINATOR': '500',
                'TERMS_ID': '500',
                'TERMS_NAME': '500',
                'CONTRACT_NUMBER': '500',
                'MVP': '500',
                'MVP_DESCRIPTION_RUS': '500',
                'MVP_DESCRIPTION_ENG': '500',
                'AGREEMENT_DATE': '1970-01-01 00:00:00',
                'START_DATE': '1970-01-02 00:00:00',
                'END_DATE': '1970-01-03 00:00:00',
                'CURRENCY': '500',
            }
        ]

        for yt_row in contract_yt_rows:
            yt_row = self.env['oebs.contract']._remap(
                yt_row,
                self.env['oebs.contract'].YT_MAPPING,
            )
            self.env['oebs.contract']._sync_yt_row(yt_row)

        oebs_contracts = self.env['oebs.contract'].search([])
        self.assertEqual(
            len(oebs_contracts), 1, 'из оебса засосали 1',
        )

        self.assertEqual(
            oebs_contracts.oebs_supplier_id.id,
            self.v1.oebs_supplier_id.id,
            'контракт для корректного поставщика',
        )
