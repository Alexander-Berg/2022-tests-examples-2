# -*- coding: utf-8 -*-
# pylint: disable=import-error
from unittest.mock import patch
from odoo.addons.hire.tests.dataset import MainDataset
from odoo.tests import tagged


@tagged('hire', 'store')
class TestStore(MainDataset):
    def test_create_dataset(self):
        name = 'New store'
        kwargs = {
            'name': name,
        }
        store = self.store(save=True, **kwargs)
        stores = self.env['res.partner'].search(
            [('store_wid', '=', store['store_wid'])]
        )
        self.assertEqual(len(stores), 1, 'found 1 company')
        store = stores[0]
        self.assertEqual(store['name'], name, 'name')
        self.assertIsNotNone(store['city'], 'cluster')

        # add timetable

        self.env['hire.timetable.wms'].create(
            {
                'begin': '07:00:00',
                'end': '23:00:00',
                'type': 'everyday',
                'store_id': store['id']
            }
        )

        stores = self.env['res.partner'].search(
            [('store_wid', '=', store['store_wid'])]
        )
        store = stores[0]

        self.assertEqual(store.timetable_ids[0].type, 'everyday', 'type is ok')

    def test_create_from_wms(self):
        company = self.company(save=True)
        store_id = '12345'
        store_random = self.store()
        store_param = {
            'store_id': store_id,
            "address": "3 Almond Road, SE16 3LR, London",
            "attr": {
                "telephone": "+447599109379"
            },
            "cluster": "Лондон",
            "company_id": company['company_wid'],
            "currency": "GBP",
            "timetable": [
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "everyday"
                },
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "monday"
                }
            ],
            "title": store_random['name'],
            "tz": "Europe/London",
        }

        with patch('common.client.wms.WMSConnector.get_wms_data') \
                as get_wms_data_mock:
            stores = [store_param]
            get_wms_data_mock.return_value = stores, None
            self.env['res.partner'].import_from_wms()

        stores = self.env['res.partner'].search(
            [('store_wid', '=', store_id)]
        )

        self.assertEqual(len(stores), 1, 'store created')
        store = stores[0]
        self.assertEqual(store.name, store_random['name'], 'name ok')
        self.assertEqual(len(store.timetable_ids), 2, '2 timetable')
        self.assertEqual(
            store.phone,
            store_param['attr']['telephone'],
            'phone ok'
        )
        self.assertEqual(
            store.company_id.id,
            company['id'],
            'company odoo link'
        )

        self.assertEqual(
            store.tz,
            store_param['tz'],
            'tz ok'
        )

    def test_update_from_wms(self):
        company = self.company(save=True)
        store = self.store(
            save=True,
            company_id=company['id'],
            company_wid=company['company_wid']
        )

        store_param = {
            'store_id': store['store_wid'],
            "address": "3 Almond Road, SE16 3LR, London",
            "attr": {
                "telephone": "+447599109379"
            },
            "cluster": "Лондон",
            "company_id": company['company_wid'],
            "currency": "GBP",
            "timetable": [
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "everyday"
                },
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "monday"
                }
            ],
            "title": "3 Almond Road",
            "tz": "Europe/London",
        }

        with patch('common.client.wms.WMSConnector.get_wms_data') \
                as get_wms_data_mock:
            stores = [store_param]
            get_wms_data_mock.return_value = stores, None
            self.env['res.partner'].import_from_wms()

        stores = self.env['res.partner'].search(
            [('store_wid', '=', store['store_wid'])]
        )

        self.assertEqual(len(stores), 1, 'store created')
        store = stores[0]
        self.assertEqual(store.name, store_param['title'], 'name ok')
        self.assertEqual(len(store.timetable_ids), 2, '2 timetable')
        self.assertEqual(
            store.phone,
            store_param['attr']['telephone'],
            'phone ok'
        )
        self.assertEqual(
            store.company_id.id,
            company['id'],
            'company odoo link'
        )

        self.assertEqual(
            store.tz,
            store_param['tz'],
            'tz ok'
        )

        self.assertIsNotNone(
            store.resource_id,
            'resource_id ok'
        )

    def test_update_timetable(self):
        company = self.company(save=True)
        store = self.store(
            save=True,
            company_id=company['id'],
            company_wid=company['company_wid']
        )

        self.env['hire.timetable.wms'].create(
            {
                'begin': '07:00:00',
                'end': '23:00:00',
                'type': 'everyday',
                'store_id': store['id']
            }
        )

        store_param = {
            'store_id': store['store_wid'],
            "address": "3 Almond Road, SE16 3LR, London",
            "attr": {
                "telephone": "+447599109379"
            },
            "cluster": "Лондон",
            "company_id": company['company_wid'],
            "currency": "GBP",
            "timetable": [
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "everyday"
                },
                {
                    "begin": "07:00:00",
                    "end": "23:00:00",
                    "type": "monday"
                }
            ],
            "title": "3 Almond Road",
            "tz": "Europe/London",
        }

        with patch('common.client.wms.WMSConnector.get_wms_data') \
                as get_wms_data_mock:
            stores = [store_param]
            get_wms_data_mock.return_value = stores, None
            self.env['res.partner'].import_from_wms()

        stores = self.env['res.partner'].search(
            [('store_wid', '=', store['store_wid'])]
        )

        self.assertEqual(len(stores), 1, 'store created')
        store = stores[0]
        self.assertEqual(store.name, store_param['title'], 'name ok')
        self.assertEqual(len(store.timetable_ids), 2, '2 timetable')
        self.assertEqual(
            store.phone,
            store_param['attr']['telephone'],
            'phone ok'
        )
        self.assertEqual(
            store.company_id.id,
            company['id'],
            'company odoo link'
        )

        self.assertEqual(
            store.tz,
            store_param['tz'],
            'tz ok'
        )
