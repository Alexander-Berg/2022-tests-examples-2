import copy
import datetime as dt
import json
import logging
import os
import time
from uuid import uuid4
from unittest.mock import patch
from freezegun import freeze_time
import pytz

from odoo.exceptions import AccessError
from odoo.tests.common import tagged, SavepointCase, Form
from odoo import exceptions
from odoo import fields
from common.client.wms import WMSConnector
from common.config import cfg
from .test_common import TestVeluationCommon
from random import randint
from odoo.addons.lavka.tests.utils import get_products_from_csv, read_json_data


_logger = logging.getLogger(__name__)

FIXTURES_PATH = 'purchase_test'


def mocked_path(*args, **kwargs):
    return args[1]


def mocked_requests_post(*args, **kwargs):
    return kwargs.get('order'), None


@tagged('lavka', 'po')
class TestPurchaseOrderIntegration(TestVeluationCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wms_connector = WMSConnector()
        cls.picking = cls.env['stock.picking']
        cls.stock_move = cls.env['stock.move']
        cls.quant = cls.env['stock.quant']
        cls.purchase_order = cls.env['purchase.order']
        cls.purchase_order_line = cls.env['sale.order.line']
        cls.external_id = 'external_id_test'

        cls.product_qty_before_after = {
            cls.products[0].wms_id: {'before': 5, 'after': 4, 'price': 5.25, 'stowage': 5},
            cls.products[1].wms_id: {'before': 10, 'after': 8, 'price': 7.25, 'stowage': 9},
            cls.products[2].wms_id: {'before': 17, 'after': 15, 'price': 9.25, 'stowage': 15},
            cls.products[3].wms_id: {'before': 19, 'after': 21, 'price': 9.25, 'stowage': 20},
            cls.products[4].wms_id: {'before': 21, 'after': 20, 'price': 9.25, 'stowage': 22},
            cls.products[5].wms_id: {'before': 0, 'after': 0, 'price': 9.25, 'stowage': 1},
            cls.products[6].wms_id: {'before': 0, 'after': 0, 'price': 19.25, 'stowage': 100},
        }

        cls.acc_json_response = {
            "store_id": cls.warehouse_3.wms_id,
            "version": 1,
            "revision": 1,
            "serial": 1,
            "parent": [],
            "order_id": f'{cls.external_id}.test_mark_1',
            "external_id": f'{cls.external_id}.test_mark_1',
            "estatus": "done",
            "status": "complete",
            "vars": {
                "editable": True,
                "stowage_id": [
                    "stowage_id_0",
                    "stowage_id_1",
                    "stowage_id_2"
                ]
            },
            "updated": "2021-03-16T11:44:58+00:00",
            "type": "acceptance",
            "source": "dispatcher",
            "required": [
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[0].wms_id)['after'],
                    "product_id": cls.products[0].wms_id,
                    "price": str(cls.product_qty_before_after.get(cls.products[0].wms_id)['price']),
                    "count": cls.product_qty_before_after.get(cls.products[0].wms_id)['before'],
                },
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[1].wms_id)['after'],
                    "product_id": cls.products[1].wms_id,
                    "price": str(cls.product_qty_before_after.get(cls.products[1].wms_id)['price']),
                    "count": cls.product_qty_before_after.get(cls.products[1].wms_id)['before'],
                },
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[2].wms_id)['after'],
                    "product_id": cls.products[2].wms_id,
                    "price": 22,
                    "count": cls.product_qty_before_after.get(cls.products[2].wms_id)['before'],
                },
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[3].wms_id)['after'],
                    "product_id": cls.products[3].wms_id,
                    "price": 33,
                    "count": cls.product_qty_before_after.get(cls.products[3].wms_id)['before'],
                },
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[4].wms_id)['after'],
                    "product_id": cls.products[4].wms_id,
                    "price": 44,
                    "count": cls.product_qty_before_after.get(cls.products[4].wms_id)['before'],
                },
            ],
            "created": "2021-03-16T11:43:01+00:00",
            "attr": {
                "doc_date": "2021-03-16",
                "doc_number": "1111",
                "stat": {},
                "complete": {},
                "contractor": "поставщик"
            },
            "approved": "2021-03-16T11:43:01+00:00",
            "doc_date": "2021-03-16",
            "doc_number": "1111",
            "contractor": "поставщик",
        }

        cls.stowage_0_data = {
            "acks": [
                "3e2e1b976f2b4ef6967c1a42148ab964000100010001"
            ],
            "serial": 12,
            "attr": {
                "doc_date": "2021-06-17",
                "doc_number": "PO-210617-000012-1",
                "complete": {},
                "contractor": "поставщик"
            },
            "revision": 0,
            "vars": {},
            "company_id": "c643bfdbcedf4729bd58f3ba16fafeed000300010000",
            "created": "2021-06-17T19:25:17+00:00",
            "delivery_promise": "2021-06-17T19:25:17+00:00",
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "bb8e55591b9a477592473ddd9c4b2acf",
            "lsn": 652805015,
            "order_id": "stowage_0_id",
            "parent": [
                cls.acc_json_response.get('order_id')
            ],
            "problems": [],
            "required": [
                {
                    "count": cls.product_qty_before_after.get(cls.products[0].wms_id)['after'],
                    "product_id": cls.products[0].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[0].wms_id)['stowage'],
                },
                {
                    "count": cls.product_qty_before_after.get(cls.products[1].wms_id)['after'],
                    "product_id": cls.products[1].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[1].wms_id)['stowage'],
                },
            ],

            "source": "integration",
            "status": "complete",
            "store_id": cls.warehouse_3.wms_id,
            "target": "complete",
            "type": "sale_stowage",
            "updated": "2021-07-15T22:25:26+00:00",

            "version": 5,
            "doc_date": "2021-06-17",
            "doc_number": "PO-210617-000012-1",
            "contractor": "поставщик"
        }

        cls.stowage_1_data = {
            "acks": [
                "3e2e1b976f2b4ef6967c1a42148ab964000100010001"
            ],
            "serial": 12,
            "attr": {
                "doc_date": "2021-06-17",
                "doc_number": "PO-210617-000012-1",
                "complete": {},
                "contractor": "поставщик"
            },
            "company_id": "c643bfdbcedf4729bd58f3ba16fafeed000300010000",
            "created": "2021-06-17T19:25:17+00:00",
            "delivery_promise": "2021-06-17T19:25:17+00:00",
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "bb8e55591b9a477592473ddd9c4b2acf",
            "lsn": 652805015,
            "order_id": "stowage_1_id",
            "parent": [
                cls.acc_json_response.get('order_id')
            ],
            "problems": [],
            "required": [
                {
                    "count": cls.product_qty_before_after.get(cls.products[2].wms_id)['after'],
                    "product_id": cls.products[2].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[2].wms_id)['stowage'],
                },
                {
                    "count": cls.product_qty_before_after.get(cls.products[3].wms_id)['after'],
                    "product_id": cls.products[3].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[3].wms_id)['stowage'],
                },
            ],
            "vars": {},
            "source": "integration",
            "status": "complete",
            "store_id": cls.warehouse_3.wms_id,
            "target": "complete",
            "type": "sale_stowage",
            "updated": "2021-07-16T22:25:26+00:00",
            "revision": 0,
            "version": 5,
            "doc_date": "2021-06-17",
            "doc_number": "PO-210617-000012-1",
            "contractor": "поставщик"
        }

        cls.stowage_2_data = {
            "acks": [
                "3e2e1b976f2b4ef6967c1a42148ab964000100010001"
            ],
            "serial": 12,
            "revision": 0,
            "attr": {
                "doc_date": "2021-06-17",
                "doc_number": "PO-210617-000012-1",
                "complete": {},
                "contractor": "поставщик"
            },
            "vars": {},
            "company_id": "c643bfdbcedf4729bd58f3ba16fafeed000300010000",
            "created": "2021-06-17T19:25:17+00:00",
            "delivery_promise": "2021-06-17T19:25:17+00:00",
            "estatus": "done",
            "estatus_vars": {},
            "external_id": "bb8e55591b9a477592473ddd9c4b2acf",
            "lsn": 652805015,
            "order_id": "stowage_2_id",
            "parent": [
                cls.acc_json_response.get('order_id')
            ],
            "problems": [],
            "required": [
                {
                    "count": cls.product_qty_before_after.get(cls.products[4].wms_id)['after'],
                    "product_id": cls.products[4].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[4].wms_id)['stowage'],
                },
                # extra
                {
                    "count": 0,
                    "product_id": cls.products[5].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[5].wms_id)['stowage'],
                },
                {
                    "count": 0,
                    "product_id": cls.products[6].wms_id,
                    "result_count": cls.product_qty_before_after.get(cls.products[6].wms_id)['stowage'],
                },
            ],

            "source": "integration",
            "status": "complete",
            "store_id": cls.warehouse_3.wms_id,
            "target": "complete",
            "type": "sale_stowage",
            "updated": "2021-07-17T22:25:26+00:00",

            "version": 5,
            "doc_date": "2021-06-17",
            "doc_number": "PO-210617-000012-1",
            "contractor": "поставщик"
        }

        cls.first_batch_json_response = {
            "store_id": cls.warehouse_3.wms_id,
            "version": 1,
            "revision": 1,
            "serial": 1,
            "parent": [],
            "order_id": f'{cls.external_id}.test_mark_1',
            "external_id": f'{cls.external_id}.test_mark_1',
            "estatus": "done",
            "status": "complete",
            "vars": {
                "editable": True,
                "stowage_id": [
                ]
            },
            "updated": "2021-03-16T11:44:58+00:00",
            "type": "acceptance",
            "source": "dispatcher",
            "required": [
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[0].wms_id)['after'],
                    "product_id": cls.products[0].wms_id,
                    "price": str(cls.product_qty_before_after.get(cls.products[0].wms_id)['price']),
                    "count": cls.product_qty_before_after.get(cls.products[0].wms_id)['before'],
                },
            ],
            "created": "2021-03-16T11:43:01+00:00",
            "attr": {
                "doc_date": "2021-03-16",
                "doc_number": "1111",
                "stat": {},
                "complete": {},
                "contractor": "поставщик"
            },
            "approved": "2021-03-16T11:43:01+00:00",
            "doc_date": "2021-03-16",
            "doc_number": "1111",
            "contractor": "поставщик",
        }

        cls.second_batch_json_response = {
            "store_id": cls.warehouse_3.wms_id,
            "parent": [],
            "version": 1,
            "revision": 1,
            "serial": 1,
            "order_id": f'{cls.external_id}.test_mark_2',
            "external_id": f'{cls.external_id}.test_mark_2',
            "estatus": "done",
            "status": "complete",
            "vars": {
                "editable": True,
                "stowage_id": [
                ]
            },
            "updated": "2021-03-16T11:44:58+00:00",
            "type": "acceptance",
            "source": "dispatcher",
            "required": [
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[1].wms_id)['after'],
                    "product_id": cls.products[1].wms_id,
                    "price": str(cls.product_qty_before_after.get(cls.products[1].wms_id)['price']),
                    "count": cls.product_qty_before_after.get(cls.products[1].wms_id)['before'],
                },
            ],
            "created": "2021-03-16T11:43:01+00:00",
            "attr": {
                "doc_date": "2021-03-16",
                "doc_number": "1111",
                "stat": {},
                "complete": {},
                "contractor": "поставщик"
            },
            "approved": "2021-03-16T11:43:01+00:00",
            "doc_date": "2021-03-16",
            "doc_number": "1111",
            "contractor": "поставщик",
        }

        cls.third_batch_json_response = {
            "store_id": cls.warehouse_3.wms_id,
            "parent": [],
            "version": 1,
            "revision": 1,
            "serial": 1,
            "order_id": f'{cls.external_id}.test_mark_3',
            "external_id": f'{cls.external_id}.test_mark_3',
            "estatus": "done",
            "status": "complete",
            "vars": {
                "editable": True,
                "stowage_id": [
                ]
            },
            "updated": "2021-03-16T11:44:58+00:00",
            "type": "acceptance",
            "source": "dispatcher",
            "required": [
                {
                    "result_count": cls.product_qty_before_after.get(cls.products[2].wms_id)['after'],
                    "product_id": cls.products[2].wms_id,
                    "price": str(cls.product_qty_before_after.get(cls.products[2].wms_id)['price']),
                    "count": cls.product_qty_before_after.get(cls.products[2].wms_id)['before'],
                },
            ],
            "created": "2021-03-16T11:43:01+00:00",
            "attr": {
                "doc_date": "2021-03-16",
                "doc_number": "1111",
                "stat": {},
                "complete": {},
                "contractor": "поставщик"
            },
            "approved": "2021-03-16T11:43:01+00:00",
            "doc_date": "2021-03-16",
            "doc_number": "1111",
            "contractor": "поставщик",
        }

    def test_allowed_to_send(self):
        today = dt.datetime(year=2021, month=1, day=20)
        self.warehouse_3.open_from = '06:00'
        self.warehouse_3.timezone = 'Europe/Paris'

        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'external_id': self.external_id,
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_3.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]

        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_init_qty': self.product_qty_before_after.get(self.products[0].wms_id)['before'],
                    'order_id': po.id,
                    'price_unit': self.product_qty_before_after.get(self.products[0].wms_id)['price'],
                }
                for i in self.products[:1]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
            po = self.purchase_order_ids[0]
            # просто проверяем, что отправляется
            po.date_planned = today
            with freeze_time('2021-01-20 12:00:00'):
                res, err = po.allowed_to_send(po, False)
            self.assertTrue(res, f'this order {po.date_planned} must be sent!')

            self.warehouse_3.open_from = None
            po.date_planned = today
            with freeze_time('2021-01-20 12:00:00'):
                res, err = po.allowed_to_send(po, False)
            self.assertTrue(res, f'this order {po.date_planned} must be sent even the timetale did not set!')

    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    def test_trust_code(self, urls):
        po = self.env['purchase.order'].create({
            'external_id': self.external_id,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        purchase_line_vals = [
            {
                'product_id': i.id,
                'name': f'{i.name}: line',
                'product_init_qty': randint(1, 23),
                'order_id': po.id,
                'price_unit': randint(2, 78),
            }
            for i in self.products
        ]
        self.env['purchase.order.line'].create(purchase_line_vals)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = self.first_batch_json_response, None
            new_mark = uuid4().hex[:6]
            wms_order, data, _, _ = po.send_to_wms(po, new_mark, interactive=True)
        if po.partner_id.trust_acceptance:
            self.assertTrue(data.get('attr').get('trust_code'))
        else:
            self.assertFalse(data.get('attr').get('trust_code'))

        self.partner.write({'trust_acceptance': False})
        po2 = self.env['purchase.order'].create({
            'external_id': f'{self.external_id}-2',
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        purchase_line_vals = [
            {
                'product_id': i.id,
                'name': f'{i.name}: line',
                'product_init_qty': randint(1, 23),
                'order_id': po2.id,
                'price_unit': randint(2, 78),
            }
            for i in self.products
        ]
        self.env['purchase.order.line'].create(purchase_line_vals)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = self.first_batch_json_response, None
            new_mark = uuid4().hex[:6]
            wms_order, data2, _, _ = po2.send_to_wms(po2, new_mark, interactive=True)

        self.assertIsNone(data2.get('attr').get('trust_code'))

    def test_unlink_marked_lines(self):
        po = self.env['purchase.order'].create({
            'external_id': self.external_id,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        purchase_line_vals = [
            {
                'product_id': i.id,
                'mark': 'Some_mark',
                'name': f'{i.name}: line',
                'product_init_qty': randint(1, 23),
                'order_id': po.id,
                'price_unit': randint(2, 78),
            }
            for i in self.products
        ]
        lines = self.env['purchase.order.line'].create(purchase_line_vals)
        for line in lines:
            with self.assertRaises(exceptions.UserError):
                line.unlink()

    def test_cannot_be_changed_price_and_tax(self):
        po = self.env['purchase.order'].create({
            'external_id': self.external_id,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        other_tax = self.env['account.tax'].create({
            'type_tax_use': 'purchase',
            'name': '20%',
            'oebs_tax_code': 12345,
            'amount': 20
        })
        # price 5.25, tax = 15%
        purchase_line_vals = [
            {
                'product_id': i.id,
                'name': f'{i.name}: line',
                'product_init_qty': 10,
                'order_id': po.id,
            }
            for i in self.products[:1]
        ]
        self.env['purchase.order.line'].create(purchase_line_vals)

        po_form = Form(po)

        with po_form.order_line.edit(0) as line:
            line.product_init_qty = 777
            line.price_unit = 100
            line.taxes_id.clear()
            line.taxes_id.add(other_tax)
        po_form.save()

        line = po.order_line[0]
        self.assertEqual(line.product_init_qty, 777)
        self.assertNotEqual(line.price_unit, 100)
        self.assertNotEqual(line.taxes_id, other_tax)
        self.assertEqual(line.price_unit, 5.25)

    def test_weight_products(self):
        self.partner.trust_acceptance = True
        po_data = {
            'external_id': self.external_id,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        }
        po1 = self.env['purchase.order'].create(po_data)
        po_data['external_id'] = f'{self.external_id}-2'
        po2 = self.env['purchase.order'].create(po_data)
        self.purchase_order_ids = [po1, po2]
        self.products[0].type_accounting = 'weight'
        for num, po in enumerate(self.purchase_order_ids):
            # первый ро будет только с весовым товаром, второй – с двумя разными
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_init_qty': self.product_qty_before_after.get(self.products[0].wms_id)['before'],
                    'order_id': po.id,
                    'price_unit': self.product_qty_before_after.get(self.products[0].wms_id)['price'],
                }
                for i in self.products[:(num+1)]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = self.first_batch_json_response, None
            new_mark = uuid4().hex[:6]
            wms_order_u, data_u, wms_order_w, data_w = po1.send_to_wms(po1, new_mark, interactive=True)
            self.assertIsNone(wms_order_u or data_u, 'First PO should not have unit products')
            wms_order_u, data_u, wms_order_w, data_w = po2.send_to_wms(po2, new_mark, interactive=True)
            required_u = data_u['required'][0]
            required_w = data_w['required'][0]
            self.assertIsNotNone(wms_order_u or data_u, 'First PO should not have unit products')
            self.assertEqual(required_u['product_id'], self.products[1].code)
            self.assertTrue(data_u['external_id'].endswith('.U'))
            self.assertEqual(required_w['product_id'], self.products[0].code)
            self.assertEqual(required_w['weight'], 5000)
            self.assertEqual(required_u['count'], 5)
            self.assertTrue(data_w['external_id'].endswith('.W'))
            self.assertEqual(data_w['external_id'][:-2], data_u['external_id'][:-2])
            self.assertIsNone(data_w['attr'].get('trust_code'))
            self.assertIsNotNone(data_u['attr'].get('trust_code'))


@tagged('po_cancel')
class TestPurchaseOrderCancellaton(TestVeluationCommon):
    """
    Attention! This test used to be sending real date to TEST WMS!
    And has no lavka tag to avoid tests crashes while deploy
    You should run it separatley in your own machine
    Just set CS in ENV to 'true'
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wms_connector = WMSConnector()
        cls.picking = cls.env['stock.picking']
        cls.stock_move = cls.env['stock.move']
        cls.quant = cls.env['stock.quant']
        cls.purchase_order = cls.env['purchase.order']
        cls.purchase_order_line = cls.env['purchase.order.line']
        cls.external_id = 'external_id_test'
        for i, product in enumerate(cls.products):
            product.wms_id = f'wms_id{i}'
        cls.product_qty_before_after = {
            cls.products[0].wms_id: {'before': 5, 'after': 4, 'price': 5.25},
            cls.products[1].wms_id: {'before': 10, 'after': 8, 'price': 7.25},
            cls.products[2].wms_id: {'before': 17, 'after': 15, 'price': 9.25},
        }
        products = cls.env['product.product'].search([('wms_id', 'in', [
            '199a98512f934179b87f2fc3c4c99b5e000100020000',
            '939ebac9ec394245adfa28d08c18408b000200020000',
            '3fc8fcfa60474a2abe51696b3c248764000100020000',
            'c6918ab38f11428a89260fc1bac0c249000300020000',
        ])])
        prd_map = {i.wms_id: i for i in products}
        exsist_obj = list(prd_map.keys())

        if '199a98512f934179b87f2fc3c4c99b5e000100020000' not in exsist_obj:
            cls.real_product_0 = cls.env['product.product'].create(
                {'name': 'CHARLES HEIDSIECK Champagne Heidsieck Rosé Réserve',
                 'wms_id': '199a98512f934179b87f2fc3c4c99b5e000100020000',
                 'default_code': '37460e4d-b0f8-446e-a9fe-01b39e9b0f27'},
            )
        else:
            cls.real_product_0 = prd_map['199a98512f934179b87f2fc3c4c99b5e000100020000']

        cls.env['purchase.requisition.line'].create(
            {
                'requisition_id': cls.purchase_requsition.id,
                'start_date': dt.datetime.now(),
                'product_id': cls.real_product_0.id,
                'tax_id': cls.real_product_0.supplier_taxes_id.id,
                'product_uom_id': cls.real_product_0.uom_id.id,
                'price_unit': 50,
                'product_qty': 1,
                'product_code': f'code-{cls.real_product_0.default_code}',
                'product_name': f'name-{cls.real_product_0.default_code}',
                'qty_multiple': 1,
                'approve_price': True,
                'approve_tax': True,
                'approve': True,
                'active': True,
            }
        )

        if '939ebac9ec394245adfa28d08c18408b000200020000' not in exsist_obj:
            cls.real_product_1 = cls.env['product.product'].create(
                {'name': 'Булочки Бриошь с шоколадной начинкой «Смак»',
                 'wms_id': '939ebac9ec394245adfa28d08c18408b000200020000',
                 'default_code': '20868'}, )
        else:
            cls.real_product_1 = prd_map['939ebac9ec394245adfa28d08c18408b000200020000']

        cls.env['purchase.requisition.line'].create(
            {
                'requisition_id': cls.purchase_requsition.id,
                'start_date': dt.datetime.now(),
                'product_id': cls.real_product_1.id,
                'tax_id': cls.real_product_1.supplier_taxes_id.id,
                'product_uom_id': cls.real_product_1.uom_id.id,
                'price_unit': 50,
                'product_qty': 1,
                'product_code': f'code-{cls.real_product_1.default_code}',
                'product_name': f'name-{cls.real_product_1.default_code}',
                'qty_multiple': 1,
                'approve_price': True,
                'approve_tax': True,
                'approve': True,
                'active': True,
            }
        )

        if '3fc8fcfa60474a2abe51696b3c248764000100020000' not in exsist_obj:
            cls.real_product_2 = cls.env['product.product'].create(
                {'name': 'Носки St.Friday «Гори в аду» 38-41',
                 'wms_id': '3fc8fcfa60474a2abe51696b3c248764000100020000',
                 'default_code': '20781'},
            )
        else:
            cls.real_product_2 = prd_map['3fc8fcfa60474a2abe51696b3c248764000100020000']

        cls.env['purchase.requisition.line'].create(
            {
                'requisition_id': cls.purchase_requsition.id,
                'product_id': cls.real_product_2.id,
                'start_date': dt.datetime.now(),
                'tax_id': cls.real_product_1.supplier_taxes_id.id,
                'product_uom_id': cls.real_product_2.uom_id.id,
                'price_unit': 50,
                'product_qty': 1,
                'product_code': f'code-{cls.real_product_2.default_code}',
                'product_name': f'name-{cls.real_product_2.default_code}',
                'qty_multiple': 1,
                'approve_price': True,
                'approve_tax': True,
                'approve': True,
                'active': True,
            }
        )

        if 'c6918ab38f11428a89260fc1bac0c249000300020000' not in exsist_obj:
            cls.real_product_3 = cls.env['product.product'].create(
                {'name': 'CHARLES HEIDSIECK Champagne Heidsieck Rosé Réserve',
                 'wms_id': 'c6918ab38f11428a89260fc1bac0c249000300020000',
                 'default_code': 'Сок томатный Vi Nature с солью'},
            )
        else:
            cls.real_product_3 = prd_map['c6918ab38f11428a89260fc1bac0c249000300020000']

        cls.env['purchase.requisition.line'].create(
            {
                'requisition_id': cls.purchase_requsition.id,
                'product_id': cls.real_product_3.id,
                'start_date': dt.datetime.now(),
                'tax_id': cls.real_product_1.supplier_taxes_id.id,
                'product_uom_id': cls.real_product_3.uom_id.id,
                'price_unit': 50,
                'product_qty': 1,
                'product_code': f'code-{cls.real_product_3.default_code}',
                'product_name': f'name-{cls.real_product_3.default_code}',
                'qty_multiple': 1,
                'approve_price': True,
                'approve_tax': True,
                'approve': True,
                'active': True,
            }
        )

    def test_button_cancel_order_in_wms(self):
        if os.getenv('CS') != 'true':
            _logger.debug('skip no CS env')
            return
        cfg.set('wms.base_url', 'http://lavka-api-proxy.lavka.tst.yandex.net/')
        cfg.set('wms.wms_token', os.getenv('TEST_TOKEN'))

        self.warehouse_3.wms_id = '0fb2876b502d40d281fa074d21c40d28000300020001'

        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'external_id': self.external_id,
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_3.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]

        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': self.real_product_0.id,
                    'name': f'{self.real_product_0.name}: line',
                    'product_init_qty': 10,
                    'order_id': po.id,
                    'price_unit': 52.5,
                }
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)

        po = self.purchase_order_ids[0]
        new_mark = uuid4().hex[:6]
        wms_order_0, data, _, _ = po.send_to_wms(po, new_mark, interactive=True)
        time.sleep(10)
        # добавляем еще строку
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': self.real_product_1.id,
                    'name': f'{self.real_product_1.name}: line',
                    'product_init_qty': 15,
                    'order_id': po.id,
                    'price_unit': 41.2,
                }
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)

        # отправляем второй раз в WMS
        new_mark = uuid4().hex[:6]
        wms_order_1, data, _, _ = po.send_to_wms(po, new_mark, interactive=True)
        time.sleep(10)
        # отменяем кнопкой первый батч
        po.get_approve_from_wms(wms_order_0.get('external_id').split('.')[1], False)

        # ордер не должен полностью отмениться
        self.assertNotEqual(po.state, 'cancel')
        # должна отмениться только строка
        for line in po.order_line.filtered(lambda l: l.product_id == self.real_product_0):
            self.assertTrue(line.mark_state)
        for line in po.order_line.filtered(lambda l: l.product_id == self.real_product_1):
            self.assertFalse(line.mark_state)

        po.button_cancel()
        # order should be canceled completely
        self.assertEqual(po.state, 'cancel')
        # and all lines should be canceled too
        for line in po.order_line:
            self.assertEqual(line.mark_state, 'canceled')

    def test_canceled_all_batches_order_from_wms(self):
        if os.getenv('CS') != 'true':
            _logger.debug('skip no CS env')
            return
        cfg.set('wms.base_url', 'http://lavka-api-proxy.lavka.tst.yandex.net/')
        cfg.set('wms.wms_token', os.getenv('TEST_TOKEN'))

        self.warehouse_3.wms_id = '0fb2876b502d40d281fa074d21c40d28000300020001'

        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'external_id': self.external_id,
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_3.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]

        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': self.real_product_0.id,
                    'name': f'{self.real_product_0.name}: line',
                    'product_init_qty': 10,
                    'order_id': po.id,
                    'price_unit': 52.5,
                }
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)

        po = self.purchase_order_ids[0]
        new_mark = uuid4().hex[:6]
        wms_order_0, data, _, _ = po.send_to_wms(po, new_mark, interactive=True)
        time.sleep(10)
        # добавляем еще строку
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': self.real_product_1.id,
                    'name': f'{self.real_product_1.name}: line',
                    'product_init_qty': 15,
                    'order_id': po.id,
                    'price_unit': 41.2,
                }
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)

        # отправляем второй раз в WMS
        new_mark = uuid4().hex[:6]
        wms_order_1, data, _, _ = po.send_to_wms(po, new_mark, interactive=True)
        time.sleep(10)
        # отменяем кнопкой все батчи (не указываем в параметре)
        po.button_cancel()

        self.assertEqual(po.state, 'cancel')
        for line in po.order_line:
            self.assertEqual(line.mark_state, 'canceled')

    def test_canceled_only_old_orders(self):
        days_before = int(self.env['ir.config_parameter'].sudo()
                          .get_param('purchase_orders_days_to_cancel', cfg('purchase_orders.days_to_cancel')))
        po1 = self.env['purchase.order'].create({
            'external_id': 0,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'date_planned': dt.datetime.now() - dt.timedelta(days=days_before),
            'state': 'sent'
        })
        po2 = self.env['purchase.order'].create({
            'external_id': self.external_id,
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'date_planned': dt.datetime.now(),
            'state': 'sent'
        })

        self.env['purchase.order'].check_and_canceled_old_orders()

        self.assertEqual(po1.state, 'cancel')
        self.assertEqual(po2.state, 'sent')


@tagged('lavka', 'po_cancel')
class TestPostprocessingCancelled(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPostprocessingCancelled, cls).setUpClass()
        cls.wms_connector = WMSConnector()

        cls.orders = read_json_data(
            folder=FIXTURES_PATH,
            filename='orders',
        )

        prices = {i['product_id']: i['price'] for i in cls.orders[0].get('required')}

        cls.external_id = 'external_id_test'
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse_3 = cls.env['stock.warehouse'].create({
            'name': 'England Lavka Test',
            'code': '9321123123',
            'warehouse_tag_ids': cls.tag,
            'wms_id': cls.orders[0].get('store_id')
        })

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURES_PATH,
            filename='products',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'price_unit': float(prices.get(i.wms_id)),
            'start_date': dt.datetime.now(),
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products]

        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')

    def test_canceled_locked_order(self):

        po = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
                (0, 0, {
                    'name': 'test_product_1',
                    'product_id': self.products[1].id,
                    'product_init_qty': 13,
                    'product_qty': 13,
                    'product_uom': self.products[1].uom_id.id,
                    'price_unit': 54.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
            ],
        })
        po.button_done()
        po.button_confirm()
        po._create_picking()
        picks = self.env['stock.picking'].search([])
        for p in picks:
            p.purchase_id = po.id

        for picking in po.picking_ids:
            self.env['wms_integration.order'].complete_picking(picking, time.strftime('%Y-%m-%d'), po.wms_id)

        with self.assertRaises(exceptions.UserError):
            po.button_cancel()
            c = 1

    def test_send_cancelled_purchase_orders(self):
        template = self.env.ref('lavka.email_template_aeroo_cancel_po_lavka')
        po = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')})
            ]
        })
        today = dt.datetime.today()
        template.with_context({'orders': [po], 'current_date': today, 'days': 2}) \
            .send_mail(list(map(lambda x: x.id, [po])))
        last_message = self.env['mail.message'].search([], order='id desc', limit=1)
        self.assertEqual(
            last_message.subject,
            f'Cancelled Purchase Orders of {po.company_id.name} - {today.strftime("%m/%d/%Y")}'
        )
        self.assertEqual(last_message.partner_ids, po.user_id.partner_id)
        self.assertEqual(last_message.attachment_ids[0].name, f'PO_{po.name.replace("/", "_")}.ods')

@tagged('lavka', 'edi_delivery')
class TestLoadingEDIDelivery(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.orders = read_json_data(
            folder=FIXTURES_PATH,
            filename='orders',
        )

        prices = {i['product_id']: i['price'] for i in cls.orders[0].get('required')}

        cls.external_id = 'external_id_test'
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse_3 = cls.env['stock.warehouse'].create({
            'name': 'England Lavka Test',
            'code': '9321123123',
            'warehouse_tag_ids': cls.tag,
            'wms_id': cls.orders[0].get('store_id')
        })

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURES_PATH,
            filename='products',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'price_unit': float(prices.get(i.wms_id)),
            'start_date': dt.datetime.now(),
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': str(num),
            'product_name': f'vendor product name {num}',
            'qty_multiple': 1,
        }) for num, i in enumerate(cls.products)]

        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')

        cls.edi_mail_server = cls.env['ir.mail_server'].create(
            {
                'name': 'test_edi_mail_server',
                'sending_type': 'edi',
                'active': True,
                'smtp_host': 'test',
                'smtp_port': 777,
                'edi_path_delivery': 'addons/lavka/tests/fixtures/delivery',
            }
        )

    def test_load_supdesno_from_edi(self):

        po = self.env['purchase.order'].create({
            'name': 'PO-211115-999998',
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
                (0, 0, {
                    'name': 'test_product_1',
                    'product_id': self.products[1].id,
                    'product_init_qty': 13,
                    'product_qty': 13,
                    'product_uom': self.products[1].uom_id.id,
                    'price_unit': 54.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
            ],
        })
        po.button_done()
        po.button_confirm()

        po1 = self.env['purchase.order'].create({
            'name': 'PO-211115-999999',
            'date_order': fields.Date.from_string('2021-02-01'),
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
                (0, 0, {
                    'name': 'test_product_1',
                    'product_id': self.products[1].id,
                    'product_init_qty': 13,
                    'product_qty': 13,
                    'product_uom': self.products[1].uom_id.id,
                    'price_unit': 54.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
            ],
        })
        po1.button_done()
        po1.button_confirm()


        po2 = self.env['purchase.order'].create({
            'name': 'PO-201115-999999',
            'date_order': fields.Date.from_string('2020-02-01'),
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
                (0, 0, {
                    'name': 'test_product_1',
                    'product_id': self.products[1].id,
                    'product_init_qty': 13,
                    'product_qty': 13,
                    'product_uom': self.products[1].uom_id.id,
                    'price_unit': 54.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
            ],
        })
        po2.button_done()
        po2.button_confirm()

        po3 = self.env['purchase.order'].create({
            'name': 'PO-211116-999999',
            'date_order': fields.Date.from_string('2021-02-01'),
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_3.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': 'test_product_0',
                    'product_id': self.products[0].id,
                    'product_init_qty': 12,
                    'product_qty': 12,
                    'product_uom': self.products[0].uom_id.id,
                    'price_unit': 50.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
                (0, 0, {
                    'name': 'test_product_1',
                    'product_id': self.products[1].id,
                    'product_init_qty': 13,
                    'product_qty': 13,
                    'product_uom': self.products[1].uom_id.id,
                    'price_unit': 54.0,
                    'date_planned': time.strftime('%Y-%m-%d')}),
            ],
        })
        po3.button_done()
        po3.button_confirm()

        # все ро в статусе done, и их данные обновляться не должны,
        # меняем статус одного из них, чтобы проверить, что данные в нем обновятся
        po.state = 'sent'

        self.env['purchase.order'].update_orders_by_EDI_delivery(True)

        self.assertEqual(
            po3.order_line[1].product_qty,
            13,
            'Load EDI Delivery. Product qty in Locked Order has been updated'
        )

        self.assertEqual(
            self.edi_mail_server.edi_last_loaded_delivery,
            '000000011635101416',
            f'Load EDI Delivery. EDI server last loaded delivery is not set.'
        )

        self.assertEqual(
            po.supdes_no,
            '7114056285',
            f'Load EDI Delivery. PO long number "SupdesNo" is not set.'
        )

        self.assertEqual(
            po1.supdes_no,
            '7114056286',
            f'Load EDI Delivery. PO short number "SupdesNo" is not set.'
        )

        self.assertEqual(
            po2.supdes_no,
            False,
            f'Load EDI Delivery. Old PO short number "SupdesNo" is set.'
        )

        self.assertEqual(
            po3.supdes_no,
            '7114056288',
            f'Load EDI Delivery. PO very short number "SupdesNo" is not set.'
        )

        self.assertEqual(
            po.order_line[0].product_qty,
            40,
            'Load EDI Delivery. Product qty in order line has not been updated'
        )
        self.assertEqual(
            po.order_line[0].product_orig_qty,
            12,
            'Load EDI Delivery. product_orig_qty in order line has been updated'
        )
        self.assertEqual(
            po.order_line[1].product_qty,
            24,
            'Load EDI Delivery. Product qty in order line has not been updated'
        )
        self.assertEqual(
            po.order_line[1].product_orig_qty,
            13,
            'Load EDI Delivery. product_orig_qty in order line has been updated'
        )


@tagged('lavka', 'multiple')
class TestMultipleAdditionBill(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=5)
        cls.purchase_requsition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.purchase_order_ids = cls.factory.create_purchase_order(
            cls.products,
            cls.purchase_requsition,
            cls.warehouses,
            qty=1
        )
        for po in cls.purchase_order_ids:
            po.write({
                'skip_check_before_invoicing': True,
            })
            cls.factory.confirm_po(po)

        cls.move = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'date': dt.datetime.now().strftime('%Y-%m-%d'),
            'invoice_date': dt.datetime.now().strftime('%Y-%m-%d'),
            'partner_id': cls.purchase_requsition.vendor_id.id,
        })

        cls.user = cls.env['res.users'].create({
            'name': 'test_lead',
            'login': 'test_lead',
            'password': 'test_lead',
        })

    def test_add_multiple_invoice_lines(self):
        po = self.purchase_order_ids[0]
        po.with_context(bill_id=self.move.id).order_line[:-1].add_multiple_invoice_lines_for_bill()
        invoice_lines = self.move.invoice_line_ids
        self.assertEqual(len(invoice_lines), len(po.order_line) - 1)
        for po_line, invoice_line in zip(po.order_line[:-1], invoice_lines):
            self.assertEqual(po_line.product_id, invoice_line.product_id)
            self.assertEqual(po_line.qty_invoiced, invoice_line.quantity)
            self.assertEqual(po_line.taxes_id, invoice_line.tax_ids)
            self.assertEqual(round(po_line.price_unit, 2), round(invoice_line.price_unit, 2))
        self.assertTrue(po.order_line[-1].product_id not in invoice_lines.mapped('product_id'))

    def test_approve_another_acc(self):
        buhs = self.env.ref('lavka.group_accountant')
        buhs.users += self.user
        move = self.move

        move.with_user(self.user).date = dt.datetime.now()
        self.assertEqual(self.user, move.write_uid)

        error_string = 'Ask another accountant to confirm.'
        with self.assertRaises(AccessError) as context:
            move.with_user(self.user).approve()
        self.assertTrue(context.exception.args[0].startswith(error_string))

        other_acc = self.env.ref('base.user_admin')
        with self.assertRaises(Exception) as context:
            self.move.with_user(other_acc).approve()
        # another error
        self.assertNotEqual(error_string, context.exception.args[0])



@tagged('lavka', 'orders_from_yt')
class TestCreateOrdersFromYT(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=5)
        cls.products = cls.factory.create_products(cls.warehouses, qty=4)
        with freeze_time('2021-03-15 12:00:00'):
            cls.purchase_requisition = cls.factory.create_purchase_requisition(
                cls.products,
                geo_tag=cls.warehouses.mapped(
                    'warehouse_tag_ids')
            )

        cls.rows = [
            # normal
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[0].code,
                "supplier_id": cls.purchase_requisition.vendor_id.external_id,
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
            # wrong product
            {
                "lavka_id": cls.products[0].default_code + '1',
                "warehouse_id": cls.warehouses[0].code,
                "supplier_id": cls.purchase_requisition.vendor_id.external_id,
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
            # wrong warehouse
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[0].code + '1',
                "supplier_id": cls.purchase_requisition.vendor_id.external_id,
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
            # wrong supplier
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[0].code,
                "supplier_id": str(cls.purchase_requisition.vendor_id.external_id) + '1',
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
            # all wrong
            {
                "lavka_id": cls.products[0].default_code + '1',
                "warehouse_id": cls.warehouses[0].code + '1',
                "supplier_id": str(cls.purchase_requisition.vendor_id.external_id) + '1',
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
        ]

        cls.one_row = [
            # normal
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[0].code,
                "supplier_id": cls.purchase_requisition.vendor_id.external_id,
                "order_date": "17.03.2022",
                "supply_date": "22.03.2022",
                "date_of_delivery_to_dc": "",
                "autoorder_total": 2.0
            },
        ]

        tag_template = [
            {
                'type': 'geo',
                'name': 'test_tag1',
            },
            {
                'type': 'geo',
                'name': 'test_tag2',
            },
            {
                'type': 'geo',
                'name': 'test_tag3',
            },
        ]
        tags = cls.env['stock.warehouse.tag'].create(tag_template)

        cls.warehouses[1].type = 'dc_external'
        cls.warehouses[2].warehouse_tag_ids = tags[0]
        cls.warehouses[3].warehouse_tag_ids = tags[1]
        cls.warehouses[4].warehouse_tag_ids = tags[2]
        with freeze_time('2021-03-15 12:00:00'):
            cls.purchase_requisition_d = cls.factory.create_purchase_requisition(
                cls.products,
                geo_tag=tags.ids
            )

        supply_chain = cls.env['cross.dock.pbl'].create({
            'vendor_id': cls.purchase_requisition_d.vendor_id.id,
            'type_destination': 'geo',
            'destination_geo':cls.warehouses[2].warehouse_tag_ids.ids[0],
            'transit_warehouse': cls.warehouses[1].id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl'
        })
        supply_chain = cls.env['cross.dock.pbl'].create({
            'vendor_id': cls.purchase_requisition_d.vendor_id.id,
            'type_destination': 'geo',
            'destination_geo': cls.warehouses[3].warehouse_tag_ids.ids[0],
            'transit_warehouse': cls.warehouses[1].id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl'
        })
        supply_chain = cls.env['cross.dock.pbl'].create({
            'vendor_id': cls.purchase_requisition_d.vendor_id.id,
            'type_destination': 'geo',
            'destination_geo':cls.warehouses[4].warehouse_tag_ids.ids[0],
            'transit_warehouse': cls.warehouses[1].id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl'
        })

        dc_quants = cls.env['dc.quants'].create(
            [
                {
                    'product_id': cls.products[0].id,
                    'distribution_center_id': cls.warehouses[1].id,
                    'warehouse_tag_id': cls.warehouses[2].warehouse_tag_ids.ids[0],
                    'quant': 3,
                },
                {
                    'product_id': cls.products[0].id,
                    'distribution_center_id': cls.warehouses[1].id,
                    'warehouse_tag_id': cls.warehouses[3].warehouse_tag_ids.ids[0],
                    'quant': 4,
                },
                {
                    'product_id': cls.products[0].id,
                    'distribution_center_id': cls.warehouses[1].id,
                    'warehouse_tag_id': cls.warehouses[4].warehouse_tag_ids.ids[0],
                    'quant': 3,
                },
            ]
        )


        cls.rows_pbl = [
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[2].code,
                "supplier_id": cls.purchase_requisition_d.vendor_id.external_id,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 6.0
            },
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[4].code,
                "supplier_id": cls.purchase_requisition_d.vendor_id.external_id,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=2)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 3.0
            },
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[2].code,
                "supplier_id": cls.purchase_requisition_d.vendor_id.external_id,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=2)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 12.0
            },
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[3].code,
                "supplier_id": cls.purchase_requisition_d.vendor_id.external_id,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 4.0
            }
        ]


        product_tag_template = [
            {
                'type': 'nonfood',
                'name': 'nonfood',
            },
            {
                'type': 'nonfood',
                'name': 'food',
            },
            {
                'type': 'storage_type',
                'name': 'cold',
            },
            {
                'type': 'storage_type',
                'name': 'dry',
            },
            {
                'type': 'nonfood',
                'name': 'fresh',
            },
        ]
        product_tags = cls.env['product.tag'].create(product_tag_template)

        product_tag_group_template = [
            {
                'distrib_center_id': cls.warehouses[1].id,
                'product_tag_ids': (product_tags[0].id, product_tags[1].id),
            },
            {
                'distrib_center_id': cls.warehouses[1].id,
                'product_tag_ids': (product_tags[2].id, product_tags[3].id),
            },
        ]
        cls.product_tag_groups = cls.env['product.tag.group'].create(product_tag_group_template)

        cls.warehouses[1].update(
            {
                'product_tag_split_orders_ids': cls.product_tag_groups.ids
            }
        )

        cls.products[1].update(
            {
                'product_tag_ids': (product_tags[0].id, product_tags[1].id)
            }
        )

        cls.products[2].update(
            {
                'product_tag_ids': (product_tags[2].id, product_tags[3].id)
            }
        )

        cls.products[3].update(
            {
                'product_tag_ids': (product_tags[4].id,)
            }
        )

        cls.rows_transfers = [
            {
                "lavka_id": cls.products[1].default_code,
                "warehouse_id": cls.warehouses[3].code,
                "supplier_id": cls.warehouses[1].code,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 5.0
            },
            {
                "lavka_id": cls.products[0].default_code,
                "warehouse_id": cls.warehouses[3].code,
                "supplier_id": cls.warehouses[1].code,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 4.0
            },
            {
                "lavka_id": cls.products[2].default_code,
                "warehouse_id": cls.warehouses[3].code,
                "supplier_id": cls.warehouses[1].code,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 2.0
            },
            {
                "lavka_id": cls.products[3].default_code,
                "warehouse_id": cls.warehouses[3].code,
                "supplier_id": cls.warehouses[1].code,
                "order_date": fields.Date.today().strftime("%d.%m.%Y"),
                "supply_date": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "date_of_delivery_to_dc": (fields.Date.today() + dt.timedelta(days=1)).strftime("%d.%m.%Y"),
                "autoorder_total": 3.0
            },
        ]

    def test_create_orders_from_yt_pbl(self):
        self.env['purchase.order'].import_orders_from_yt_new(test_mode=True, rows=self.rows_pbl, in_queue=False)
        results = self.env['autoorder.result'].search([])

        po = self.env['purchase.order'].search([])
        self.assertEqual(po.source, 'autoorder')
        self.assertEqual(
            len(po),
            1,
            f'Create orders from YT pbl. PO not created.'
        )
        po = po[0]

        self.assertEqual(
            po.delivery_type,
            'dc_pbl',
            f'Create orders from YT pbl. PO delivery_type is not PBL.'
        )
        self.assertEqual(
            len(po.order_line),
            1,
            f'Create orders from YT pbl. PO product lines not equal 1.'
        )
        self.assertEqual(
            len(po.distribution_line),
            4,
            f'Create orders from YT pbl. PO distribution lines not equal 4.'
        )
        self.assertEqual(
            po.order_line[0].product_init_qty,
            25,
            f'Create orders from YT pbl. PO product line product_init_qty not equal 25.'
        )
        self.assertEqual(
            po.distribution_line[0].product_init_qty,
            6,
            f'Create orders from YT pbl. PO distribution line [0] product_init_qty not equal 6.'
        )
        self.assertEqual(
            po.distribution_line[1].product_init_qty,
            3,
            f'Create orders from YT pbl. PO distribution line [1] product_init_qty not equal 12.'
        )
        self.assertEqual(
            po.distribution_line[2].product_init_qty,
            12,
            f'Create orders from YT pbl. PO distribution line [1] product_init_qty not equal 12.'
        )
        self.assertEqual(
            po.distribution_line[3].product_init_qty,
            4,
            f'Create orders from YT pbl. PO distribution line [2] product_init_qty not equal 4.'
        )

        po.distribution_line[0].product_init_qty=16
        po.redistribute_pbl()
        self.assertEqual(
            po.order_line[0].product_init_qty,
            35,
            f'Create orders from YT pbl. PO product line wrong product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[0].product_init_qty,
            9,
            f'Create orders from YT pbl. PO distribution line[0] wrong product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[1].product_init_qty,
            6,
            f'Create orders from YT pbl. PO distribution line[1] wrong product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[2].product_init_qty,
            18,
            f'Create orders from YT pbl. PO distribution line[2] wrong product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[3].product_init_qty,
            2,
            f'Create orders from YT pbl. PO distribution line[3] wrong product_init_qty after redistribution.'
        )

        po.button_done()
        po.button_confirm()

        self.env['purchase.order'].import_orders_from_yt_new(test_mode=True, rows=self.rows_transfers, in_queue=False)
        results = self.env['autoorder.result'].search([])
        transfer = self.env['transfer.lavka'].search([])

        transfer_result = [
            (
                k.transfer_id,
                k.transfer_id.product_tag_group,
                k.transfer_id.warehouse_in,
                k.product_id,
                k.qty_plan
            ) for k in transfer.transfer_lines
        ]

        proper_result = [
            (transfer[0], self.product_tag_groups[0], self.warehouses[3], self.products[1], 5),
            (transfer[0], self.product_tag_groups[0], self.warehouses[3], self.products[0], 6),
            (transfer[1], self.product_tag_groups[1], self.warehouses[3], self.products[2], 2),
            (transfer[2], self.env['product.tag.group'], self.warehouses[3], self.products[3], 3),
            (transfer[3], self.product_tag_groups[0], self.warehouses[2], self.products[0], 9)
        ]

        self.assertEqual(
            transfer_result,
            proper_result,
            f'Create transfers from YT. Wrong transfers result.'
        )

        self.assertEqual(
            transfer[0].transfer_lines[1].purchase_distribution_line_ids[0],
            po.distribution_line[3],
            'Wrong purchase order distribution line id in TR 1 line 1'
        )
        self.assertEqual(
            transfer[3].transfer_lines[0].purchase_distribution_line_ids[0],
            po.distribution_line[0],
            'Wrong purchase order distribution line id in TR 2 line 1'
        )

        self.assertEqual(
            transfer[0].transfer_lines[1].purchase_order_ids[0],
            po,
            'Wrong purchase order id in TR 1'
        )
        self.assertEqual(
            transfer[0].purchase_order_count,
            1,
            'Wrong purchase order count in TR 1'
        )

        self.assertEqual(
            transfer[3].transfer_lines[0].purchase_order_ids[0],
            po,
            'Wrong purchase order id in TR 2'
        )
        self.assertEqual(
            transfer[3].purchase_order_count,
            1,
            'Wrong purchase order count in TR2'
        )


        self.assertEqual(
            po.distribution_line[0].transfer_lines[0],
            transfer[3].transfer_lines[0],
            'Wrong transfer line id in purchase order distribution line'
        )
        self.assertFalse(
            po.distribution_line[1].transfer_lines,
            'Not empty transfer line id in purchase order distribution line with future supply date'
        )
        self.assertEqual(
            po.distribution_line[3].transfer_lines[0],
            transfer[0].transfer_lines[1],
            'Wrong transfer line id in purchase order distribution line'
        )


        self.assertEqual(
            po.transfer_ids[0],
            transfer[3],
            'Wrong transfer id in purchase order'
        )
        self.assertEqual(
            po.transfer_ids[1],
            transfer[0],
            'Wrong transfer id in purchase order'
        )
        self.assertEqual(
            po.transfer_count,
            2,
            'Wrong transfer count in purchase order'
        )

        po.order_line[0].product_init_qty=24
        po.redistribute_pbl()

        self.assertEqual(
            po.distribution_line[0].product_init_qty,
            9,
            f'Create orders from YT pbl. PO distribution line [0] wrong product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[1].product_init_qty,
            3,
            f'Create orders from YT pbl. PO distribution line [1] product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[2].product_init_qty,
            10,
            f'Create orders from YT pbl. PO distribution line [2] product_init_qty after redistribution.'
        )
        self.assertEqual(
            po.distribution_line[3].product_init_qty,
            2,
            f'Create orders from YT pbl. PO distribution line [3] product_init_qty after redistribution.'
        )

    def test_create_orders_from_yt(self):
        self.env['purchase.order'].import_orders_from_yt_new(test_mode=True, rows=copy.deepcopy(self.rows))
        results = self.env['autoorder.result'].search([])
        jobs = self.env['queue.job'].search([])

        self.assertEqual(
            jobs[0].name,
            f'Creating PO for {self.purchase_requisition.vendor_id.name}_{self.warehouses[0].name}_{self.purchase_requisition.name}_2022-03-17_2022-03-22_direct',
            f'Create orders from YT. Queue job is not created.'
        )

        self.assertTrue(
            'Cannot find purchase requisition lines' in results[1].errors,
            f'Create orders from YT. No error for purchase requisition line not found.'
        )

        self.assertTrue(
            'Product with id' in results[1].errors,
            f'Create orders from YT. No error for product not found.'
        )

        self.assertTrue(
            'Cannot find warehouse' in results[2].errors,
            f'Create orders from YT. No error for warehouse not found.'
        )

        self.assertTrue(
            'Cannot find neither Vendor' in results[3].errors,
            f'Create orders from YT. No error for vendor not found.'
        )

        self.assertTrue(
            'Cannot find neither Vendor' in results[4].errors,
            f'Create orders from YT. No mass error for vendor not found.'
        )
        self.assertTrue(
            'Cannot find warehouse' in results[4].errors,
            f'Create orders from YT. No mass error for warehouse not found.'
        )
        self.assertTrue(
            'Product with id' in results[4].errors,
            f'Create orders from YT. No mass error for product not found.'
        )

        self.warehouses[0].update({'wms_id': False})
        self.env['purchase.order'].import_orders_from_yt_new(True, self.one_row)
        results = self.env['autoorder.result'].search([])
        self.assertTrue(
            'has no WMS id' in results[0].errors,
            f'Create orders from YT. No error for warehouse with empty wms_id.'
        )

    def test_create_orders_with_cancel_po(self):
        self.env['purchase.order'].import_orders_from_yt_new(test_mode=True, rows=copy.deepcopy(self.rows), in_queue=False)
        po = self.env['purchase.order'].search([])
        self.assertEqual(po.source, 'autoorder')
        po.button_cancel(test=True)
        self.assertEqual(po.state, 'cancel')

        self.env['purchase.order'].import_orders_from_yt_new(test_mode=True,  rows=copy.deepcopy(self.rows), in_queue=False)
        po2 = self.env['purchase.order'].search([('state', '=', 'draft')])
        self.assertEqual(po2.state, 'draft')

