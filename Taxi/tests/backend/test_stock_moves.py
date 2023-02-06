# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import os
from random import randrange, choice, uniform
import datetime as dt

from freezegun import freeze_time
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase

from odoo.addons.lavka.tests.utils import get_products_from_csv
from .test_common import _logger

FIXTURES_PATH = 'common'
# pylint: disable=invalid-name


@tagged('lavka', 'lavka_stock', 'fast')
class TestStockMoveCommon(SavepointCase):
    """
    Тест Создания склада
    """

    @classmethod
    def setUpClass(cls):
        super(TestStockMoveCommon, cls).setUpClass()
        cls.move_comparison = (
            ('recount_in', 'RECOUNT_IN_OPER', 'RECOUNT_IN_DIFF'),
            ('recount_out', 'RECOUNT_OUT_OPER', 'RECOUNT_OUT_DIFF'),
        )
        cls.differenses = []
        cls.inventory = cls.env['stock.inventory']
        cls.picking = cls.env['stock.picking']
        cls.stock_move = cls.env['stock.move']
        cls.quant = cls.env['stock.quant']
        cls.sale_order = cls.env['sale.order']
        cls.sale_order_line = cls.env['sale.order.line']
        cls.valuation_layer = cls.env['stock.valuation.layer']
        cls.inventory_line = cls.env['stock.inventory.line']
        cls.tag = cls.env['stock.warehouse.tag'].create(
            [
                {
                    'type': 'geo',
                    'name': 'test_tag',
                },
            ]
        )
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse',
            'code': 'TT',
            'warehouse_tag_ids': cls.tag
        })
        _logger.debug(f'Warehouse {cls.warehouse.name} created')
        cls.partner = cls.env['res.partner'].create({'name': 'Test Purchaser'})
        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURES_PATH,
            filename='products_import',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)

        cls.product_not_in_stock = cls.env['product.product'].create({
            'name': 'Test not in stock',
            'default_code': '999999',
            'wms_id': '999999',
            'type': 'product'
        })
        cls.products_all = cls.products + cls.product_not_in_stock
        with freeze_time('2021-03-15 12:00:00'):
            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'start_date': fields.Datetime.today(),
                'price_unit': float(uniform(2.1, 10.9)),
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': cls.purchase_requsition.id,
                'product_qty': 9999,
                'product_code': '300',
                'approve_tax': True,
                'approve_price': True,
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products_all]
            for r in cls.requsition_lines:
                r._compute_approve()
            cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')


# pylint: disable=abstract-class-instantiated
@tagged('lavka', 'lavka_stock')
class TestStockInventoryStandard(TestStockMoveCommon):
    def test_create_warehouse(self):
        self.assertEqual(self.warehouse.wh_stock_diff.name, 'DIFF')
        self.assertEqual(self.warehouse.lot_stock_id.name, 'OPER')
        self.assertEqual(self.warehouse.wh_stock_git.name, 'GIT')

    @classmethod
    def create_move_recounts(cls):
        moves = []
        for product in cls.products[5:10]:
            location_id = choice([cls.warehouse.wh_stock_diff.id, cls.warehouse.lot_stock_id.id])
            if location_id == cls.warehouse.wh_stock_diff.id:
                location_dest_id = cls.warehouse.lot_stock_id.id
                lavka_type = 'recount_in'
            else:
                location_dest_id = cls.warehouse.wh_stock_diff.id
                lavka_type = 'recount_out'
            vals_move = {
                'product_id': product.id,
                'product_uom_qty': randrange(1, 20),
                'product_uom': product.uom_id.id,
                'name': f'{product.name}',
                'wms_id': 'Some ID',
                'lavka_type': lavka_type,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            }
            move = cls.stock_move.create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()
            moves.append(move)
            _logger.debug(f'Recount  {move.id} confirmed')
        # ------
        for product in cls.products[:5]:
            location_id = choice([cls.warehouse.wh_stock_diff.id, cls.warehouse.lot_stock_id.id])
            if location_id == cls.warehouse.wh_stock_diff.id:
                location_dest_id = cls.warehouse.lot_stock_id.id
                lavka_type = 'recount_in'
            else:
                location_dest_id = cls.warehouse.wh_stock_diff.id
                lavka_type = 'recount_out'
            vals_move = {
                'product_id': product.id,
                'product_uom_qty': randrange(1, 20),
                'product_uom': product.uom_id.id,
                'name': f'{product.name}',
                'wms_id': 'Some ID',
                'lavka_type': lavka_type,
                'location_dest_id': location_dest_id,
                'location_id': location_id,
            }
            move = cls.stock_move.create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()
            moves.append(move)
            _logger.debug(f'Recount {move.id} confirmed')
        return moves

    # Проверяем, что движения создают ровно такой остаток, какой нужен
    def test_stock_move(self):
        moves = self.create_move_recounts()
        quant = self.env['stock.quant']
        oper_qty_in_moves = 0.0
        diff_qty_in_moves = 0.0
        for m in moves:
            if m.location_dest_id.name == 'OPER':
                oper_qty_in_moves += m.quantity_done
                diff_qty_in_moves -= m.quantity_done
            if m.location_dest_id.name == 'DIFF':
                diff_qty_in_moves += m.quantity_done
                oper_qty_in_moves -= m.quantity_done
        oper_qty = sum([
            i.quantity for i in quant.search([
                ('location_id', '=', self.warehouse.lot_stock_id.id)
            ])
        ])
        diff_qty = sum([
            i.quantity for i in quant.search([
                ('location_id', '=', self.warehouse.wh_stock_diff.id)
            ])
        ])
        self.assertEqual(oper_qty_in_moves, oper_qty)
        self.assertEqual(diff_qty_in_moves, diff_qty)
        for i in moves:
            value_sum = sum([s.value for s in i.stock_valuation_layer_ids])
            self.assertEqual(value_sum, 0.0)
            self.assertEqual(len(i.stock_valuation_layer_ids), 2)



@tagged('lavka', 'kitchen')
class TestStockKitchen(TestStockMoveCommon):

    def get_stock_loc(self, loc):
        quant_obj = self.env['stock.quant']
        value_obj = self.env['stock.valuation.layer']
        qty = sum([
            i.quantity for i in quant_obj.search([
                ('location_id', '=', loc.id)
            ])
        ])
        valuation_qty = sum([
            i.quantity for i in value_obj.search([
                ('location_id', '=', loc.id)
            ])
        ])
        value = sum([
            i.value for i in value_obj.search([
                ('location_id', '=', loc.id)
            ])
        ])
        rem_qty = 0.0
        rem_value = 0.0
        for prod in self.products[:5]:
            svl = value_obj._sequential_formula(prod, loc)
            if svl:
                rem_qty += svl.remaining_qty
                rem_value += svl.remaining_value

        return qty, valuation_qty, value, rem_qty, rem_value


    def save_xlsx_report(self, locations, report_name=None, ):
        # pylint: disable=import-outside-toplevel
        import pandas as pd
        res = []
        valuation_lines = self.env['stock.valuation.layer'].search([
            ('location_id', 'in', locations),
        ])
        for val in valuation_lines:
            try:
                cost_price = val.remaining_value / val.remaining_qty
            except ZeroDivisionError:
                cost_price = 0
            res.append({
                'PRICE_RULE': val.price_rule,
                'TRANSACTION_SYSTEM_NAME': val.transaction_system_name,
                'TRANS_SYSTEM_GROUP': val.trans_system_group,
                'TRANS_ID': val.trans_id,
                'PRODUCT_EXTERNAL_ID': val.product_id.default_code,
                'VIRT_WHS': val.location_id.name,
                'UNIT_COST': val.unit_cost,
                'QTY': val.quantity,
                'VALUE': val.value,
                'TAX_ID': val.tax_id.name,
                'TAX_SUM': val.tax_sum,
                'REMAINING-QTY': val.remaining_qty,
                'REMAINING-VALUE': val.remaining_value,
                'COST_PRICE': cost_price,
                'DESCRIPTION': val.description,
                'DOCUMENT_DATETIME': val.document_datetime,
                'DOCUMENT_DATE': val.document_date,
                'CREATE': val.create_date,
                'COMPANY_ID': val.company_id.id,
            })
        df = pd.DataFrame(res)
        writer = pd.ExcelWriter(f'{report_name}.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()

