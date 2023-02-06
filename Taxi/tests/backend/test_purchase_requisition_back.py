# import time
# import uuid
# from random import randrange
# import logging
# import datetime as dt
# from unittest.mock import patch
# from odoo.fields import Datetime
# from odoo.tests.common import Form
# from common.client.wms import WMSConnector
# from freezegun import freeze_time
# from common.config import cfg
# from odoo.tests import tagged
# from odoo import exceptions
# from odoo.tests.common import SavepointCase, Form
# from odoo.addons.lavka.tests.utils import read_json_data
# from dateutil.relativedelta import relativedelta
#
# _logger = logging.getLogger(__name__)
# rnd = lambda x: f'{x}-{uuid.uuid4().hex}'
# FIXTURES_PATH = 'purch_requisition_test'
#
#
# def mocked_path(*args, **kwargs):
#     return args[1]
#
#
# def mocked_requests_post(*args, **kwargs):
#     return kwargs.get('order'), None
#
#
# # первое добавление с первой ценой: цена с концом
# # нег: не должно добавиться
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase1(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_1_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test563_1_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_test_563_1_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(1):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1+k,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300',
#                 'product_name': 'test563_1_vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today(),
#                 'end_date': Datetime.today() + dt.timedelta(days=10),
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             self.assertIsNotNone(price)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
#
# #первое добавление с первой ценой: цена без конца (ок)
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase2(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_2_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test563_2_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_test563_2_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(4):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1+k,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300',
#                 'product_name': 'test563_2 vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today() + dt.timedelta(days=1+k),
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
#
# # проверить непрерывность цен (ok)
# # отсортировать по start_date и проверить, что последовательно
# # line[i].actual_end_date + relativedelta(seconds=1) == line[i+1].start_date,
# # до тех пор пока у очередной цены не будет actual_end_date == None
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase3(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_3_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test563_3_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(4):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300_test563_3',
#                 'product_name': 'test563_3 vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today() + dt.timedelta(days=1),
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
#
#         prices = self.env["purchase.requisition.line"].search(
#             order="actual_start_date",
#         )
#         prices = iter(prices)
#         prv = None
#         cur = next(prices)
#         try:
#             while cur.actual_end_date is not None:
#                 nxt = next(prices)
#                 yield prv, cur, nxt
#                 prv = cur
#                 cur = nxt
#                 self.assertEqual(prv.actual_end_date + relativedelta(seconds=1), cur.start_date)
#         except StopIteration:
#             yield prv, cur, None
#
# # добавление одинаковых цен на одинаковый промежуток (ok)
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase4(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_4_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test563_4_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(4):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300_test563_4',
#                 'product_name': 'test563_4 vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today() + dt.timedelta(days=1),
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
#
# # добавление цены с поздним концом, проверить,
# # что на новый промежуток времени изменилась цена (ok)
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase5(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_5_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test563_5_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(1):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300_test563_5',
#                 'product_name': 'test563_5 vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today() + dt.timedelta(days=1),
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
#
#         prices = self.env["purchase.requisition.line"].search(
#             order="actual_start_date",
#         )
#         prices = iter(prices)
#         prv = None
#         cur = next(prices)
#         try:
#             while cur.actual_end_date is not None:
#                 nxt = next(prices)
#                 yield prv, cur, nxt
#                 prv = cur
#                 cur = nxt
#         except StopIteration:
#             yield prv, cur, None
#             if cur.actual_end_date is not None:
#                 self.requsition_lines = [self.env['purchase.requisition.line'].create({
#                     'product_id': i.id,
#                     'price_unit': 1,
#                     'product_uom_id': i.uom_id.id,
#                     'tax_id': i.supplier_taxes_id.id,
#                     'requisition_id': self.req.id,
#                     'approve_tax': True,
#                     'active': True,
#                     'approve_price': True,
#                     'product_qty': 1,
#                     'product_code': '300_test563_5',
#                     'product_name': 'test563_5 vendor product name',
#                     'qty_multiple': 1,
#                     'start_date': Datetime.today(),
#                     'end_date': cur.actual_end_date + relativedelta(seconds=1),
#                 }) for i in self.products.values()[:1]]
#                 for r in self.requsition_lines:
#                     r._compute_approve()
#                 self.action_in_progress()
#                 self.reqs.append(self.req)
#             else:
#                 # добавить с actual_end_date = cur.start_date + dt.timedelta(days=1)
#                 self.requsition_lines = [self.env['purchase.requisition.line'].create({
#                     'product_id': i.id,
#                     'price_unit': 1,
#                     'product_uom_id': i.uom_id.id,
#                     'tax_id': i.supplier_taxes_id.id,
#                     'requisition_id': self.req.id,
#                     'approve_tax': True,
#                     'active': True,
#                     'approve_price': True,
#                     'product_qty': 1,
#                     'product_code': '300_test563_5',
#                     'product_name': 'test563_5 vendor product name',
#                     'qty_multiple': 1,
#                     'start_date': Datetime.today(),
#                     'end_date': cur.start_date + dt.timedelta(days=1),
#                 }) for i in self.products.values()[:1]]
#                 for r in self.requsition_lines:
#                     r._compute_approve()
#                 self.action_in_progress()
#                 self.reqs.append(self.req)
#             # проверить, что на новый промежуток времени изменилась цена
#             self.assertEqual(cur.actual_end_date + relativedelta(seconds=1), cur.actual_end_date)
#
# # проверять лог действий - skipped, can do on front testing <!
#
# # создаем на один период разные цены, промо и не промо
# # с разной позицией в графе, проверить изменение
# @tagged('lavka', 'test_pr_prices')
# class TestPrCase7(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         wms_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='checks',
#         )
#         log_data = read_json_data(
#             folder=FIXTURES_PATH,
#             filename='logs',
#         )
#         cls.wms_connector = WMSConnector()
#         cls.tag = cls.env['stock.warehouse.tag']
#         for q in range(2):
#             tag = cls.env['stock.warehouse.tag'].create([
#                 {
#                     'type': 'geo',
#                     'name': f'test563_7_{q}',
#                 },
#             ]
#             )
#             cls.tag += tag
#
#         c = 0
#         mapped_products = {}
#         mapped_wh = {}
#         doc_ids = []
#         for order in wms_data:
#             # создаем склады
#             store_id = order['store_id']
#             order_id = order['order_id']
#             doc_ids.append(order_id)
#             if not mapped_wh.get(store_id):
#                 wh = cls.env['stock.warehouse'].create({
#                     'name': f'test_wh_test563_7_{c}',
#                     'code': f'{c}',
#                     'warehouse_tag_ids': cls.tag,
#                     'wms_id': store_id
#                 })
#                 mapped_wh[store_id] = wh
#
#             req = order.get('required')
#             # создаем товары
#             for prd_data in req:
#                 wms_id = prd_data['product_id']
#                 if not mapped_products.get(wms_id):
#                     res = cls.env['product.product'].create(
#                         {
#                             'name': f'test_product_test563_7_{c}',
#                             'default_code': f'{c}',
#                             'type': 'product',
#                             'wms_id': wms_id,
#                             'taxes_id': 1,
#
#                         }
#                     )
#                     mapped_products[wms_id] = res
#                     c += 1
#             # создаем доки wms
#             with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
#                 get_wms_data_mock.return_value = log_data, None
#                 with freeze_time('2021-03-15 12:00:00'):
#                     cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')
#
#         cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
#             ('order_id', 'in', doc_ids)
#         ])}
#         cls.products = mapped_products
#         cls.warehouses = mapped_wh
#
#         # создаем прайсы
#
#         cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
#         _logger.info(f'Partner {cls.partner.name} created')
#         cls.reqs = []
#         for k in range(10):
#
#             req = cls.env['purchase.requisition'].create({
#                 'name': f'req_{k}',
#                 'vendor_id': cls.partner.id,
#                 'state': 'ongoing',
#             })
#
#             cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
#                 'product_id': i.id,
#                 'price_unit': 1 + k,
#                 'product_uom_id': i.uom_id.id,
#                 'tax_id': i.supplier_taxes_id.id,
#                 'requisition_id': req.id,
#                 'approve_tax': True,
#                 'active': True,
#                 'approve_price': True,
#                 'product_qty': 1,
#                 'product_code': '300_test563_7_',
#                 'product_name': 'vendor product name',
#                 'qty_multiple': 1,
#                 'start_date': Datetime.today(),
#                 'end_date': Datetime.today() + dt.timedelta(days=1 + 2 * k) if not k & 1 else None
#             }) for i in cls.products.values()]
#             for r in cls.requsition_lines:
#                 r._compute_approve()
#             req.action_in_progress()
#             cls.reqs.append(req)
#
#     def test_lookup_prices(self):
#         pr = self.env['purchase.requisition.line']
#         self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
#         for product in self.products.values():
#             price = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0],
#                 only_price=True)
#             req_line = pr.get_last_req_line(
#                 product,
#                 list(self.warehouses.values())[0])
#             self.assertIsNotNone(req_line)
#
#         for wms_doc in self.docs.values():
#             if wms_doc.type in ['order', 'check_product_on_shelf']:
#                 res = wms_doc.post_processing(wms_doc)
#                 self.assertEqual(res.value, 'ok')
