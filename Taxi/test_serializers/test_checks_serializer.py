import logging
import json
import random
from collections import defaultdict
from unittest.mock import patch

from odoo import tools
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
from random import randrange

_logger = logging.getLogger(__name__)
stocklog_logger_name = 'odoo.addons.lavka.backend.models.wms.wms_stock_log'

@tagged('lavka', 'serializers', 's_checks')
class TestChecksProductOnShelfSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=1)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.product = cls.products[0]
        cls.wh = cls.warehouses[0]
        cls.env['ir.config_parameter'].set_param('sleep', 'false')

    def test_negative_delta_count(self):
        """
        проверка на полке в минус (товар с OPER на DIFF)
        """
        delta_count = -5
        check_data, check_log = self.factory.get_get_checks_and_stock_log(self.wh, self.product, delta_count)
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'ordinary')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.assertEqual(wms_doc.processing_status, 'ok')

        self.factory.process_stock_logs(check_log)

        _move = self.env['stock.move'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(_move.state, 'done')
        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(picking)
        self.assertEqual(picking.location_id.name, 'OPER')
        self.assertEqual(picking.location_dest_id.name, 'DIFF')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for move in picking.move_lines:
            # проверим, что заполнены ключевые поля
            self.assertEqual(move.origin, wms_doc.doc_number)
            self.assertEqual(check_log[0]['log_id'], move.log_id)
            # проверим правильные дестинейшены
            self.assertEqual(move.location_id.name, 'OPER')
            self.assertEqual(move.location_dest_id.name, 'DIFF')
            # и колво
            qty_at_oper = stocks.get((move.product_id, move.location_id))
            qty_at_diff = stocks.get((move.product_id, move.location_dest_id))
            self.assertEqual(qty_at_oper, delta_count)
            self.assertEqual(qty_at_diff, -delta_count)
        c=1

    def test_pozitive_delta_count(self):
        """
        проверка на полке в плюс (товар с DIFF на OPER)
        """
        delta_count = random.randrange(1, 99)
        check_data, check_log = self.factory.get_get_checks_and_stock_log(self.wh, self.product, delta_count)
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'ordinary')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(check_log)

        _move = self.env['stock.move'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(_move.state, 'done')
        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(picking)
        self.assertEqual(picking.location_id.name, 'DIFF')
        self.assertEqual(picking.location_dest_id.name, 'OPER')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for move in picking.move_lines:
            # проверим, что заполнены ключевые поля
            self.assertEqual(move.origin, wms_doc.doc_number)
            self.assertEqual(check_log[0]['log_id'], move.log_id)
            # проверим правильные дестинейшены
            self.assertEqual(move.location_id.name, 'DIFF')
            self.assertEqual(move.location_dest_id.name, 'OPER')
            # и колво
            qty_at_oper = stocks.get((move.product_id, move.location_id))
            qty_at_diff = stocks.get((move.product_id, move.location_dest_id))
            self.assertEqual(qty_at_oper, -delta_count)
            self.assertEqual(qty_at_diff, delta_count)
        c = 1

    def test_zero_delta_count(self):
        """
        проверка не выявила расхождений
        """
        delta_count = 0
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        check_data, check_log = self.factory.get_get_checks_and_stock_log(self.wh, self.product, delta_count)
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'ordinary')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(check_log)

        _move = self.env['stock.move'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(len(_move), 0)
        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        # пикинг все равно создан
        self.assertEqual(len(picking), 1)
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for key, qty in stocks_before.items():
            self.assertEqual(qty, stocks.get(key))
        for key, qty in stocks.items():
            self.assertEqual(qty, stocks_before.get(key))
        c = 1


@tagged('lavka', 'serializers', 's_checks_on_order')
class TestChecksProductOnShelfOnOrderSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.purchased_products = cls.products[:5]
        cls.extra_products = cls.products[5:8]
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.po = cls.factory.create_purchase_order(
            cls.purchased_products,
            cls.purchase_requisition,
            cls.warehouses,
            qty=1
        )[0]
        # обрабатываем документы вмс
        cls.acc = cls.factory.create_acceptance_list(cls.po, cls.warehouses)[0]
        cls.env['wms_integration.order'].post_processing(cls.acc, 'TEST', test=True)
        stw_data_set = cls.factory.get_sale_stowages_data_from_acceptance(cls.acc)
        j = 1
        all_logs = []
        for stw_data, stw_log in stw_data_set:
            wms_doc = cls.factory._create_stowage(
                vals=stw_data,
                parent=cls.acc,
                count=j
            )
            j += 1
            all_logs += stw_log

            wms_doc.post_processing(wms_doc, 'TEST', test=True)


        cls.factory.process_stock_logs(all_logs)

        cls.product = cls.products[0]
        cls.product_extra = cls.extra_products[0]
        cls.wh = cls.warehouses[0]


    def test_negative_delta_count_existing_product(self):
        """
        проверка на полке в минус (товар с OPER на Vendors)
        """
        delta_count = -5
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        check_data, check_log = self.factory.get_get_checks_on_order_and_stock_log(
            self.wh,
            self.product,
            self.acc,
            delta_count
        )
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'purchase_order')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)

        self.factory.process_stock_logs(check_log)

        _move = self.env['stock.move'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(_move.state, 'done')
        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(picking)
        self.assertEqual(picking.location_id.name, 'OPER')
        self.assertEqual(picking.location_dest_id.name, 'Vendors')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for move in picking.move_lines:
            # проверим, что заполнены ключевые поля
            self.assertEqual(move.origin, wms_doc.doc_number)
            self.assertEqual(check_log[0]['log_id'], move.log_id)
            # проверим правильные дестинейшены
            self.assertEqual(move.location_id.name, 'OPER')
            self.assertEqual(move.location_dest_id.name, 'Vendors')
            # и колво
            qty_at_oper = stocks.get((move.product_id, move.location_id))
            qty_at_oper_before = stocks_before.get((move.product_id, move.location_id))
            qty_at_diff = stocks.get((move.product_id, move.location_dest_id),0)
            self.assertEqual(qty_at_oper, qty_at_oper_before + delta_count)
            self.assertEqual(qty_at_diff, 0)
        c = 1

    def test_pozitive_delta_count_extra_product(self):
        """
        проверка на полке в плюс товара не было в заказе (товар с Vendors на OPER)
        """
        delta_count = random.randrange(1, 99)
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        check_data, check_log = self.factory.get_get_checks_on_order_and_stock_log(
            self.wh,
            self.product_extra,
            self.acc,
            delta_count
        )
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'purchase_order')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(check_log)

        _move = self.env['stock.move'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(_move.state, 'done')
        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(picking)
        self.assertEqual(picking.location_id.name, 'Vendors')
        self.assertEqual(picking.location_dest_id.name, 'OPER')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for move in picking.move_lines:
            # проверим, что заполнены ключевые поля
            self.assertEqual(move.origin, wms_doc.doc_number)
            self.assertEqual(check_log[0]['log_id'], move.log_id)
            # проверим правильные дестинейшены
            self.assertEqual(move.location_id.name, 'Vendors')
            self.assertEqual(move.location_dest_id.name, 'OPER')
            # и колво
            qty_at_oper = stocks.get((move.product_id, move.location_dest_id))
            qty_at_oper_before = stocks_before.get((move.product_id, move.location_dest_id), 0)
            qty_at_diff = stocks.get((move.product_id, move.location_dest_id))
            self.assertEqual(qty_at_oper, qty_at_oper_before + delta_count)
            self.assertEqual(qty_at_diff, delta_count)
        for line in self.po.order_line:
            if line.product_id == self.product_extra:
                self.assertTrue(line.is_extra_line)
        c = 1

    def test_negative_delta_count_extra_product(self):
        """
        проверка на полке в минус товара не было в заказе (надо падать)
        но потом меняем на обычный пересчет, и он должен отработаться нормально
        """
        delta_count = - 7
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        check_data, check_log = self.factory.get_get_checks_on_order_and_stock_log(
            self.wh,
            self.product_extra,
            self.acc,
            delta_count
        )
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'purchase_order')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        with self.assertRaises(AssertionError):
            with tools.mute_logger(stocklog_logger_name):
                self.factory.process_stock_logs(check_log)

        picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(picking)
        # не изменились локейшены из-за исключения
        self.assertEqual(picking.location_id.name, 'Vendors')
        self.assertEqual(picking.location_dest_id.name, 'OPER')

        # далее убираем парента, и обрабатываем как обычный пересчет
        wms_doc.parent = []
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'ordinary')
        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        # проверим, что локейшены поменялись
        self.assertEqual(picking.location_id.name, 'OPER')
        self.assertEqual(picking.location_dest_id.name, 'DIFF')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for move in picking.move_lines:
            # проверим, что заполнены ключевые поля
            self.assertEqual(move.origin, wms_doc.doc_number)
            self.assertEqual(check_log[0]['log_id'], move.log_id)
            # проверим правильные дестинейшены
            self.assertEqual(move.location_id.name, 'OPER')
            self.assertEqual(move.location_dest_id.name, 'DIFF')
            # и колво
            qty_at_oper = stocks.get((move.product_id, move.location_dest_id))
            qty_at_oper_before = stocks_before.get((move.product_id, move.location_dest_id), 0)
            qty_at_diff = stocks.get((move.product_id, move.location_dest_id))
            self.assertEqual(qty_at_oper, qty_at_oper_before - delta_count)
            self.assertEqual(qty_at_diff, -delta_count)

        c = 1



