import datetime as dt
import json
import logging
import os
from csv import DictReader
from random import randrange
from unittest.mock import patch

from common.client.wms import WMSConnector
from common.config import cfg
from freezegun import freeze_time
from odoo import exceptions
from odoo.tests.common import SavepointCase, tagged
from odoo.addons.lavka.tests.utils import get_products_from_csv, read_json_data

_logger = logging.getLogger(__name__)

FIXTURES_PATH = 'autocreate_po'


@tagged('lavka', 'auto_c')
class TestLookupAllPrices(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestLookupAllPrices, cls).setUpClass()
        cls.wms_connector = WMSConnector()
        cls.acceptance = read_json_data(
            folder=FIXTURES_PATH,
            filename='acceptance',
        )
        cls.stowage = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage',
        )
        cls.stowage_log = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage_log',
        )
        cls.checks = read_json_data(
            folder=FIXTURES_PATH,
            filename='check',
        )
        cls.checkslog = read_json_data(
            folder=FIXTURES_PATH,
            filename='check_log',
        )

        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Test',
            'code': '9321123123',
            'warehouse_tag_ids': cls.tag,
            'wms_id': cls.acceptance[0].get('store_id')
        })

        cls.partner = cls.env['res.partner'].create({'name': 'Jafora Tabori LTD'})
        cls.partner_zoho = cls.env['res.partner'].create({'name': 'Zoho'})
        cls.partner_some = cls.env['res.partner'].create({'name': 'Some vendor'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')

        cls.purchase_requsition_zoho = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_zoho.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.purchase_requsition_2 = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_some.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.req1 = cls.acceptance[0].get('required')
        cls.req2 = cls.stowage[0].get('required')
        cls.req3 = cls.checks[0].get('required')
        req = cls.req1 + cls.req2 + cls.req3
        c = 0
        mapped_products = {}

        extra_ids = [i['product_id'] for i in cls.req2 if i.get('count') == 0]
        extra_ids.append('b690a9dc94504037b377596c24ba5c77000300010002')
        for line in req:
            wms_id = line['product_id']

            if not mapped_products.get(wms_id):
                res = cls.env['product.product'].create(
                    {
                        'name': f'test_product_{c}',
                        'default_code': f'{c}',
                        'type': 'product',
                        'wms_id': wms_id,
                    }
                )
                mapped_products[wms_id] = res
                c += 1
        cls.products = mapped_products

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 1.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for wms_id, i in cls.products.items() if wms_id not in extra_ids]

        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        # часть есть в зохо
        cls.requsition_lines_zoho = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 5.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_zoho.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for wms_id, i in cls.products.items() if wms_id in extra_ids]
        for r in cls.requsition_lines_zoho:
            r._compute_approve()
        cls.purchase_requsition_zoho.action_in_progress()

        #     делаем неактивную строку для checks
        check_product = cls.products.get('b690a9dc94504037b377596c24ba5c77000300010002')
        res = cls.env['purchase.requisition.line'].create({
            'product_id': check_product.id,
            'start_date': dt.datetime.now(),
            'price_unit': 5.11,
            'product_uom_id': check_product.uom_id.id,
            'tax_id': check_product.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_2.id,
            'approve_tax': True,
            'approve_price': True,
            'active': False,
            'approve': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        })
        cls.purchase_requsition_2.action_in_progress()

        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')


@tagged('lavka', 'auto_c')
class TestLookupAllPrices3(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestLookupAllPrices3, cls).setUpClass()
        cls.wms_connector = WMSConnector()
        cls.acceptance = read_json_data(
            folder=FIXTURES_PATH,
            filename='acceptance',
        )
        cls.stowage = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage',
        )
        cls.stowage_log = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage_log',
        )
        cls.checks = read_json_data(
            folder=FIXTURES_PATH,
            filename='check',
        )
        cls.checkslog = read_json_data(
            folder=FIXTURES_PATH,
            filename='check_log',
        )

        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Test',
            'code': '9321123123',
            'warehouse_tag_ids': cls.tag,
            'wms_id': cls.acceptance[0].get('store_id')
        })

        cls.partner = cls.env['res.partner'].create({'name': 'Jafora Tabori LTD'})
        cls.partner_zoho = cls.env['res.partner'].create({'name': 'Zoho'})
        cls.partner_some = cls.env['res.partner'].create({'name': 'Some vendor'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')

        cls.purchase_requsition_zoho = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_zoho.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.purchase_requsition_2 = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_some.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.req1 = cls.acceptance[0].get('required')
        cls.req2 = cls.stowage[0].get('required')
        cls.req3 = cls.checks[0].get('required')
        req = cls.req1 + cls.req2 + cls.req3
        c = 0
        mapped_products = {}

        extra_ids = [i['product_id'] for i in cls.req2 if i.get('count') == 0]
        extra_ids.append('b690a9dc94504037b377596c24ba5c77000300010002')
        cls.extra = extra_ids
        for line in req:
            wms_id = line['product_id']

            if not mapped_products.get(wms_id):
                res = cls.env['product.product'].create(
                    {
                        'name': f'test_product_{c}',
                        'default_code': f'{c}',
                        'type': 'product',
                        'wms_id': wms_id,
                    }
                )
                mapped_products[wms_id] = res
                c += 1
        cls.products = mapped_products

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 1.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for wms_id, i in cls.products.items() if wms_id not in extra_ids]

        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        # экстра лайны есть в зохо
        cls.requsition_lines_zoho = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 5.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_zoho.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for wms_id, i in cls.products.items() if wms_id in extra_ids]
        for r in cls.requsition_lines_zoho:
            r._compute_approve()
        cls.purchase_requsition_zoho.action_in_progress()

        #   и они есть неактивные в другом
        cls.requsition_lines_2 = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 5.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_2.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for wms_id, i in cls.products.items() if wms_id in extra_ids]
        for r in cls.requsition_lines_2:
            r._compute_approve()
        for r in cls.requsition_lines_2:
            r.active = False
        cls.purchase_requsition_2.action_in_progress()

    def test_lookup_all_prices_no_sale_many_extra(self):
        self.env['ir.config_parameter'].set_param('lookup_all_prices', True)

        # создаем заказ поставщику
        po = self.env['purchase.order'].create({
            'external_id': self.acceptance[0].get('external_id').split('.')[0],
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_1.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        purchase_line_vals = []
        for line in self.req1:
            i = self.products.get(line.get('product_id'))
            purchase_line_vals.append(
                {
                    'product_id': i.id,
                    'name': f'{i.name}',
                    'product_init_qty': int(line.get('count')),
                    'order_id': po.id,
                    'price_unit': float(line.get('price')),
                    'mark': self.acceptance[0].get('external_id').split('.')[1],
                }
            )

        self.env['purchase.order.line'].create(purchase_line_vals)

        # создаем acceptance
        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = {}, None
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order([self.acceptance[0]], self.wms_connector,
                                                                   'cursor_1')
        # создаем stowage
        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = self.stowage_log, None
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order([self.stowage[0]], self.wms_connector,
                                                                   'cursor_1')

        docs = {i.type: i for i in self.env['wms_integration.order'].search([])}
        doc_acc = docs.get('acceptance')
        doc_stw = docs.get('sale_stowage')

        doc_acc.post_processing(doc_acc)
        self.assertEqual(po.state, 'purchase')
        doc_acc.processing_status = 'ok'
        doc_stw.post_processing(doc_stw)
        self.assertEqual(po.state, 'done')

    def test_compute_requisition_line(self):
        """
        тестирование создания лайнов в множественном self
        надо убедиться, что нельзя передать лайны из разных агриментов в один ордер
        """
        self.env['ir.config_parameter'].set_param('lookup_all_prices', True)

        # создаем заказ поставщику
        po = self.env['purchase.order'].create({
            'external_id': self.acceptance[0].get('external_id').split('.')[0],
            'partner_id': self.partner.id,
            'picking_type_id': self.warehouse_1.in_type_id.id,
            'requisition_id': self.purchase_requsition.id,
        })

        purchase_line_vals = []
        # добавим им экстра строки из стоваджа
        for line in self.req1:
            i = self.products.get(line.get('product_id'))
            purchase_line_vals.append(
                {
                    'product_id': i.id,
                    'name': f'{i.name}',
                    'product_init_qty': int(line.get('count')) if line.get('count') else 22,
                    'order_id': po.id,
                    'price_unit': float(line.get('price')) if line.get('price') else 2,
                    'mark': self.acceptance[0].get('external_id').split('.')[1],
                }
            )
        for line in self.req2:
            if line.get('product_id') not in self.extra:
                continue
            i = self.products.get(line.get('product_id'))

            purchase_line_vals.append(
                {
                    'product_id': i.id,
                    'name': f'{i.name}',
                    'product_init_qty': int(line.get('count')) if line.get('count') else 22,
                    'order_id': po.id,
                    'price_unit': float(line.get('price')) if line.get('price') else 2,
                    'mark': self.acceptance[0].get('external_id').split('.')[1],
                }
            )

        with self.assertRaises(exceptions.UserError):
            self.env['purchase.order.line'].create(purchase_line_vals)

@tagged('lavka', 'qv')
class TestQuantValuationTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestQuantValuationTest, cls).setUpClass()
        cls.wms_connector = WMSConnector()
        cls.acceptance = read_json_data(
            folder=FIXTURES_PATH,
            filename='acceptance',
        )
        cls.stowage = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage',
        )
        cls.stowage_log = read_json_data(
            folder=FIXTURES_PATH,
            filename='stowage_log',
        )
        cls.checks = read_json_data(
            folder=FIXTURES_PATH,
            filename='check',
        )
        cls.checkslog = read_json_data(
            folder=FIXTURES_PATH,
            filename='check_log',
        )

        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Test',
            'code': f'{randrange(1, 9999999)}',
            'warehouse_tag_ids': cls.tag,
            'wms_id': cls.acceptance[0].get('store_id')
        })

        cls.partner = cls.env['res.partner'].create({'name': 'Jafora Tabori LTD'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')

        cls.req1 = cls.acceptance[0].get('required')
        cls.req2 = cls.stowage[0].get('required')
        cls.req3 = cls.checks[0].get('required')
        req = cls.req1 + cls.req2 + cls.req3
        c = 0
        mapped_products = {}

        extra_ids = [i['product_id'] for i in cls.req2 if i.get('count') == 0]
        extra_ids.append('b690a9dc94504037b377596c24ba5c77000300010002')
        cls.extra = extra_ids
        for line in req:
            wms_id = line['product_id']

            if not mapped_products.get(wms_id):
                res = cls.env['product.product'].create(
                    {
                        'name': f'test_product_{c}',
                        'default_code': f'{c}',
                        'type': 'product',
                        'wms_id': wms_id,
                    }
                )
                mapped_products[wms_id] = res
                c += 1
        cls.products = mapped_products

        cls.requsition_lines = cls.env['purchase.requisition.line']

        uniques = {}

        for line in req:
            if not uniques.get(line.get('product_id')):
                i =  mapped_products.get(line.get('product_id'))
                res = cls.env['purchase.requisition.line'].create({
                    'product_id': i.id,
                    'start_date': dt.datetime.now(),
                    'price_unit': 1.25,
                    'product_uom_id': i.uom_id.id,
                    'tax_id': i.supplier_taxes_id.id,
                    'requisition_id': cls.purchase_requsition.id,
                    'approve_tax': True,
                    'approve_price': True,
                    # 'product_qty': 9999,
                    'product_code': '300',
                    'product_name': 'vendor product name',
                    'qty_multiple': 1,
                })
            uniques[line.get('product_id')] = res
            cls.requsition_lines += res


        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()

    def test_quant_valuation(self):
        self.env['ir.config_parameter'].set_param('compute quant value from svl', True)

        # создаем заказ поставщику
        q = 1
        for k in range(q):
            ex = self.acceptance[0].get('external_id').split('.')[0]
            mark = self.acceptance[0].get('external_id').split('.')[1]
            po = self.env['purchase.order'].create({
                'external_id': f'{k}_{ex}',
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_1.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            purchase_line_vals = []
            for line in self.req1:
                i = self.products.get(line.get('product_id'))
                if int(line.get('count')) == 0:
                    continue
                purchase_line_vals.append(
                    {
                        'product_id': i.id,
                        'name': f'{i.name}',
                        'product_init_qty': int(line.get('count')),
                        'order_id': po.id,
                        'price_unit': 1.25,
                        'mark': f'{k}_{mark}',
                    }
                )

            self.env['purchase.order.line'].create(purchase_line_vals)
            for purchase_line in po.order_line:
                uom_qty = purchase_line.product_init_qty
                purchase_line.product_qty = purchase_line.product_init_qty
                purchase_line.product_uom_qty = uom_qty

            po.button_done()
            po = po.with_company(po.company_id)
            pickings = po._create_picking_from_wms(po.order_line)
            for picking in pickings:
                self.env['wms_integration.order'].complete_picking(picking, po.date_order, po.wms_id)
            _logger.debug(f'Created {po.name}')

        _logger.debug('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        location_id = po.picking_ids.location_dest_id.id
        for line in po.order_line:
            product = line.product_id
            b = dt.datetime.now()
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', location_id),
            ])
            _logger.debug(f'{product} qty {quant.quantity} value {quant.value} t {dt.datetime.now() - b}')
            self.assertAlmostEqual(quant.value, q * line.product_init_qty * line.price_unit, 2)
