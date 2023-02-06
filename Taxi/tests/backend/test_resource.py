# -*- coding: utf-8 -*-
# pylint: disable=import-error
from unittest.mock import patch
from odoo.addons.hire.tests.dataset import MainDataset
from odoo.tests import tagged


@tagged('hire', 'resource')
class TestResource(MainDataset):

    def test_create_resource(self):
        store = self.store(save=True)

        res = self.env['resource.resource'].create(
            {
                'name': 'Resource',
                'resource_type': 'store',
                'store_id': store['id'],
                'tz': 'Europe/London',
            }
        )

        self.assertIsNotNone(res, 'resource is ok')

    def test_create_resource_2(self):
        store = self.store(save=True)

        store = self.env['res.partner'].search(
            [('store_wid', '=', store['store_wid'])]
        )

        store[0].resource_id = [
            (0, 0, {
                'name': 'Resource',
                'resource_type': 'store',
                'tz': 'UTC',
            }
             )
        ]

        res = store.resource_id
        self.assertIsNotNone(res, 'resource is ok')
