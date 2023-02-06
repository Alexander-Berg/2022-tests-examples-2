# -*- coding: utf-8 -*-
# pylint: disable=import-error
from unittest.mock import patch
from odoo.addons.hire.tests.dataset import MainDataset
from odoo.tests import tagged


@tagged('hire', 'company')
class TestCompany(MainDataset):

    def test_create_dataset(self):
        name = 'New company'
        ownership = 'yandex'
        vat = '12345'
        kwargs = {
            'name': name,
            'ownership': ownership,
            'vat': vat,
        }
        company = self.company(save=True, **kwargs)
        companies = self.env['res.company'].search(
            [('company_wid', '=', company['company_wid'])]
        )
        self.assertEqual(len(companies), 1, 'found 1 company')
        company = companies[0]

        self.assertEqual(company['name'], name, 'name')
        self.assertEqual(company['ownership'], ownership, 'ownership')
        self.assertEqual(company['vat'], vat, 'tax id equal')

    def test_import_wms(self):
        exist_company = self.company(save=True)
        replace_data = self.company(save=False)

        name = 'New company'
        ownership = 'yandex'
        vat = '12345'
        new_company = {
            'company_id': '654321',
            'fullname': name,
            'ownership': ownership,
            'tin': vat,
        }
        with patch('common.client.wms.WMSConnector.get_wms_data') \
                as get_wms_data_mock:
            companies = [
                {
                    'company_id': exist_company['company_wid'],
                    'fullname': replace_data['name'],
                    'tin': replace_data['vat'],
                },
                new_company
            ]
            get_wms_data_mock.return_value = companies, None
            self.env['res.company'].import_from_wms()

        exist_companies = self.env['res.company'].search(
            [('company_wid', '=', exist_company['company_wid'])])

        self.assertEqual(exist_companies[0]['name'],
                         replace_data['name'],
                         'name changed')
        self.assertEqual(exist_companies[0]['vat'],
                         replace_data['vat'],
                         'vat changed')
        new_companies = self.env['res.company'].search(
            [('company_wid', '=', new_company['company_id'])])

        self.assertEqual(
            new_companies[0]['name'],
            name,
            'name created company ok')
        self.assertEqual(
            new_companies[0]['ownership'],
            ownership,
            'ownership created company ok')
        self.assertEqual(
            new_companies[0]['vat'],
            vat,
            'tax id equal'
        )
