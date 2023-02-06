# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
from collections import defaultdict
from datetime import timedelta
from random import randrange, choice, sample, uniform
from unittest.mock import patch
from odoo.fields import datetime, Datetime
from odoo.tests import tagged
from odoo.tests.common import SavepointCase
from odoo.addons.lavka.tests.utils import get_products_from_csv

from .test_common import _logger

FIXTURES_PATH = 'common'
try:
    import pandas as pd
except ImportError:
    # pylint: disable=invalid-name
    pd = False


# pylint: disable=invalid-name,too-many-statements


@tagged('lavka', 'inventory', 'fast')
class TestStockInventoryCommon(SavepointCase):
    """
    Тест инвентаризации Самый главный тест для логистического лога товаров лавки
    """

    @classmethod
    def _calculate_veluations_product(cls):
        valuation_lines = cls.valuation_layer.search([
            '&',
            ('location_id', 'in', [cls.warehouse.lot_stock_id.id, cls.warehouse.wh_stock_diff.id]),
            ('product_id', 'in', [i.id for i in cls.products_all]),

        ])
        res = {}
        for i in valuation_lines:
            product_id = i.product_id.id
            if product_id in res:
                vals = res.get(product_id)
                quantity = vals.get('quantity')
                value = vals.get('value')
                vals.update({
                    'quantity': quantity + i.quantity,
                    'value': value + i.value
                })
            else:
                res.update({
                    i.product_id.id: {
                        'quantity': i.quantity,
                        'value': i.value,
                    }
                })
        return res

    @classmethod
    def _create_move(cls):
        picking_vals = []
        moves = []
        info = []
        for i, product in enumerate(cls.products[:10]):
            date_time = datetime.now() + timedelta(hours=3, minutes=i)
            location_id = choice([cls.warehouse.wh_stock_diff.id, cls.warehouse.lot_stock_id.id])
            if location_id == cls.warehouse.wh_stock_diff.id:
                location_dest_id = cls.warehouse.lot_stock_id.id
                lavka_type = 'recount_in'
            else:
                location_dest_id = cls.warehouse.wh_stock_diff.id
                lavka_type = 'recount_out'
            vals_pick = {
                'picking_type_id': cls.warehouse.int_type_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'date': date_time
            }
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
            picking_vals.append((vals_pick, vals_move))
            picking = cls.picking.create([vals_pick])
            vals_move.update({'picking_id': picking.id})
            move = cls.stock_move.create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()
            move.date = move.date.replace(microsecond=0)
            moves.append(move)
            info.append(move.id)
        _logger.debug(f'Recounts  {info} confirmed')
        # -=Между пересчетами делаем еще закупочки
        cls.purchase_order_ids_midle = [
            cls.env['purchase.order'].create({
                'partner_id': cls.partner.id,
                'picking_type_id': cls.warehouse.in_type_id.id,
                'requisition_id': cls.purchase_requsition.id,
                'date_order': datetime.now() + timedelta(hours=5, minutes=i)  # сейчас
            })
            for i in reversed(range(12, 24))
        ]
        info = []
        for po in cls.purchase_order_ids_midle:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': randrange(1, 100),
                    'product_init_qty': randrange(1, 100),
                    'order_id': po.id,
                    'price_unit': float(uniform(2.1, 10.9)),
                }
                for i in sample(cls.products, 20)
            ]
            cls.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()
            info.append(po.picking_ids.id)
        _logger.debug(f'Pickings midle {info} confirmed')
        # ------
        info = []
        for i, product in enumerate(cls.products[10:20]):
            date_time = datetime.now() + timedelta(hours=7, minutes=i)
            location_id = choice([cls.warehouse.wh_stock_diff.id, cls.warehouse.lot_stock_id.id])
            if location_id == cls.warehouse.wh_stock_diff.id:
                location_dest_id = cls.warehouse.lot_stock_id.id
                lavka_type = 'recount_in'
            else:
                location_dest_id = cls.warehouse.wh_stock_diff.id
                lavka_type = 'recount_out'
            vals_pick = {
                'picking_type_id': cls.warehouse.int_type_id.id,
                'location_dest_id': location_dest_id,
                'location_id': location_id,
                'date': date_time,
            }
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
            picking = cls.picking.create([vals_pick])
            vals_move.update({'picking_id': picking.id})
            move = cls.stock_move.create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()
            moves.append(move)
            info.append(move.id)
        _logger.debug(f'Recounts {info} confirmed')
        return moves

    @classmethod
    def setUpClass(cls):
        super(TestStockInventoryCommon, cls).setUpClass()
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
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'wms_id'
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
            'type': 'product',
            'wms_id': 'wms_id_tnis'
        })
        cls.products_all = cls.products + cls.product_not_in_stock
        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': datetime.now(),
            'price_unit': float(uniform(2.1, 10.9)),
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'product_qty': 9999,
            'approve_tax': True,
            'approve_price': True,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products_all]
        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')
        # """
        # -==Закупаем товары==-
        # """
        cls.purchase_order_ids = [
            cls.env['purchase.order'].create({
                'partner_id': cls.partner.id,
                'picking_type_id': cls.warehouse.in_type_id.id,
                'requisition_id': cls.purchase_requsition.id,
                'date_order': datetime.now() + timedelta(minutes=i)  # сейчас
            })
            for i in reversed(range(4, 8))
        ]
        info = []
        for po in cls.purchase_order_ids:
            po.date_order = po.date_order.replace(microsecond=0)
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': randrange(1, 100),
                    'product_init_qty': randrange(1, 100),
                    'order_id': po.id,
                    'price_unit': float(uniform(2.1, 10.9)),
                }
                for i in sample(cls.products, 10)
            ]

            cls.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()
            info.append(po.picking_ids.id)

        _logger.debug(f'Picking {info} confirmed')

        # ===Делаем пару рандомных продаж
        cls.sale_order_ids_rand = [
            cls.env['sale.order'].create({
                'partner_id': cls.partner.id,
                'warehouse_id': cls.warehouse.id,
                'date_order': datetime.now() + timedelta(hours=2, minutes=i, seconds=30, microseconds=0)
            })
            for i in range(1, 8)
        ]
        info = []
        for o in cls.sale_order_ids_rand:
            o.date_order = o.date_order.replace(microsecond=0)
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': randrange(1, 2),
                    'price_unit': float(uniform(1.0, 7.9)),
                    'order_id': o.id,
                }
                for i in sample(cls.products, 4)
            ]
            cls.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_lines:
                move.quantity_done = move.product_uom_qty
            o.picking_ids._action_done()
            info.append({o.id})
        _logger.debug(f'Sale rand order {info} confirmed')

        # -==Фактурируем товары==-
        info = []
        for po in cls.purchase_order_ids:
            with patch('odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
        for _order in (order for order in cls.purchase_order_ids):
            dt = Datetime.to_string(_order.date_order + timedelta(hours=3))
            setattr(_order.invoice_ids, 'payment_reference', dt)
            _order.invoice_ids.action_post(test_document_datetime=dt, force_post=True)
            info.append(_order.invoice_ids.id)
        _logger.debug(f'Invoices {info} confirmed')
        # -==Перемещаем туда сюда в DIFF что бы создать разницы в diff==-

        cls.diff_moves = cls._create_move()

        # -=Продаем товары==-
        cls.sale_order_ids = [
            cls.env['sale.order'].create({
                'partner_id': cls.partner.id,
                'warehouse_id': cls.warehouse.id,
                'date_order': datetime.now() + timedelta(hours=7, minutes=i, seconds=30)
            })
            for i in range(2, 24)
        ]
        info = []
        for o in cls.sale_order_ids:
            o.date_order = o.date_order.replace(microsecond=0)
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': randrange(1, 2),
                    'price_unit': float(uniform(1.0, 7.9)),
                    'order_id': o.id,
                }
                for i in sample(cls.products, 8)
            ]
            cls.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_lines:
                move.quantity_done = move.product_uom_qty
            o.picking_ids._action_done()
            info.append(o.id)
        _logger.debug(f'Sale Orders {info} confirmed')

        # -=Оцениваем то, что положили на склад=-

        cls.valuated_before = cls._calculate_veluations_product()

    def _create_invenotory_happy(self):
        """ Создаем инвентаризацию простенькую
        """
        _logger.debug('Create happy inventoty created')
        self.inventory_happy_id = self.inventory.create({
            'name': 'Test Inventory happy',
            'location_ids': (self.warehouse.lot_stock_id.id,)
        })
        self.inventory_happy_id.action_start()
        self.inventory_happy_id.post_inventory()
        return self.inventory_happy_id

    def _create_invenotory_not_annual(self):
        """ Создаем официальную инвентаризацию сложненькую
        """
        self.inventory_not_annual = self.inventory.create({
            'annual_inventory': False,
            'name': 'Test Inventory not_annual',
            'location_ids': [self.warehouse.lot_stock_id.id, ],
            'date': datetime.now() + timedelta(days=2)
        })
        self.inventory_not_annual.action_start()
        for line in self.inventory_not_annual.line_ids:
            random_wms_plan_qty = randrange(0, 1000)
            random_wms_fact_qty = randrange(0, 1000)

            line.write({'product_qty': random_wms_fact_qty, 'wms_qty': random_wms_plan_qty})
        self.inventory_not_annual._action_done()
        return self.inventory_not_annual

    def _create_invenotory_differenses(self):
        """ Создаем официальную инвентаризацию сложненькую
        """
        self.inventory_diff_id = self.inventory.create({
            'annual_inventory': True,
            'name': 'Test Inventory differenses',
            'location_ids': [self.warehouse.lot_stock_id.id, ],
            'date': datetime.now() + timedelta(days=2)
        })
        self.inventory_diff_id.action_start()
        self.env['stock.inventory.line'].create({
            'inventory_id': self.inventory_diff_id.id,
            'location_id': self.inventory_diff_id.location_ids[0].id,
            'product_id': self.product_not_in_stock.id,
            'product_qty': 10,
        })
        for line in self.inventory_diff_id.line_ids:
            random_wms_plan_qty = randrange(0, 1000)
            random_wms_fact_qty = randrange(0, 1000)

            line.write({'product_qty': random_wms_fact_qty, 'wms_qty': random_wms_plan_qty})
        self.inventory_diff_id._action_done()
        return self.inventory_diff_id


# pylint: disable=abstract-class-instantiated
@tagged('lavka', 'inventory2')
class TestStockInventoryStandard(TestStockInventoryCommon):
    def save_xlsx_report(self, file_name):
        res = []
        valuation_lines = self.valuation_layer.search([
            ('location_id', 'in', [self.warehouse.lot_stock_id.id, self.warehouse.wh_stock_diff.id]),
        ], order='id desc')
        for val in valuation_lines:
            valuated_after = self.valuated_after.get(val.product_id.id)
            if valuated_after:
                value_value_after = valuated_after.get('value')
                value_qty_after = valuated_after.get('quantity')
            else:
                value_value_after = 0
                value_qty_after = 0
            valuated_before = self.valuated_before.get(val.product_id.id)
            if valuated_before:
                value_value_before = valuated_before.get('value')
                value_qty_before = valuated_before.get('quantity')
            else:
                value_value_before = 0
                value_qty_before = 0
            try:
                cost_price = val.remaining_value / val.remaining_qty
            except ZeroDivisionError:
                cost_price = 0
            res.append({
                'PRICE_RULE': val.price_rule,
                'QTY_BEFORE_INV_OPER': self.qty_oper_before.get(val.product_id.id) or 0,
                'QTY_BEFORE_INV_DIFF': self.qty_diff_before.get(val.product_id.id) or 0,
                'VALUE_BEFORE_INV': value_value_before or 0,
                'VALUE_QTY_BEFORE_INV': value_qty_before or 0,
                'VALUE_AFTER_INV': value_value_after or 0,
                'VALUE_QTY_AFTER_INV': value_qty_after or 0,
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

        writer = pd.ExcelWriter(f'{file_name}.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()

    def _merge_results(self):
        res = {}
        for item in self.products_all:
            valuated_after = self.valuated_after.get(item.id)
            if valuated_after:
                value_value_after = valuated_after.get('value')
                value_qty_after = valuated_after.get('quantity')
            else:
                value_value_after = 0
                value_qty_after = 0
            valuated_before = self.valuated_before.get(item.id)
            if valuated_before:
                value_value_before = valuated_before.get('value')
                value_qty_before = valuated_before.get('quantity')
            else:
                value_value_before = 0
                value_qty_before = 0
            vals = {
                'products': item.default_code,
                'oper_before': self.qty_oper_before.get(item.id) or 0,
                'oper_after': self.qty_oper_after.get(item.id) or 0,
                'diff_before': self.qty_diff_before.get(item.id) or 0,
                'diff_after': self.qty_diff_after.get(item.id) or 0,
                'value_value_before': value_value_before or 0,
                'value_qty_before': value_qty_before or 0,
                'value_value_after': value_value_after or 0,
                'value_qty_after': value_qty_after or 0,
            }
            res.update({item.id: vals})
        for key, value in res.items():
            oper_svl_qty = 0
            oper_svl_money = 0
            diff_svl_qty = 0
            diff_svl_money = 0
            diff_svl_result_qty = 0
            diff_svl_result_money = 0
            move_qty = 0
            move_result = 0
            for move in self.inventory_diff_id.move_ids:
                if move.product_id.id == key and move.lavka_type in ['stocktake_writeoff_out',
                                                                     'stocktake_suplus_in',
                                                                     'stocktake_suplus_out',
                                                                     'stocktake_writeoff_in']:
                    for svl in move.stock_valuation_layer_ids:
                        if svl.transaction_system_name == 'COST_PRICE_CORR':
                            continue
                        if self.warehouse.lot_stock_id == svl.location_id:
                            oper_svl_qty += svl.quantity
                            oper_svl_money += svl.value
                        elif self.warehouse.wh_stock_diff == svl.location_id:
                            diff_svl_qty += svl.quantity
                            diff_svl_money += svl.value

                    if move.location_id == self.warehouse.lot_stock_id:
                        move_qty -= move.quantity_done
                    else:
                        move_qty += move.quantity_done
                elif move.product_id.id == key:
                    for svl in move.stock_valuation_layer_ids:
                        if svl.transaction_system_name == 'COST_PRICE_CORR':
                            continue
                        if self.warehouse.wh_stock_diff == svl.location_id:
                            diff_svl_result_qty += svl.quantity
                            diff_svl_result_money += svl.value

                    if move.location_id == self.warehouse.wh_stock_diff:
                        move_result -= move.quantity_done
                    else:
                        move_result += move.quantity_done
            value.update({
                'oper_svl_qty': oper_svl_qty or 0,
                'oper_svl_money': oper_svl_money or 0,
                'diff_svl_qty': diff_svl_qty or 0,
                'diff_svl_money': diff_svl_money or 0,
                'diff_svl_result_qty': diff_svl_result_qty or 0,
                'diff_svl_result_money': diff_svl_result_money or 0,
                'move_qty': move_qty or 0,
                'move_result': move_result or 0
            })
        return res

    def test_inventory_not_annual(self):
        self.qty_oper_before = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.lot_stock_id.quant_ids
        }
        self.qty_diff_before = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.wh_stock_diff.quant_ids
        }
        self.inventory_not_annual = self._create_invenotory_not_annual()
        self.valuated_after = self._calculate_veluations_product()
        self.qty_diff_after = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.wh_stock_diff.quant_ids
        }
        self.qty_oper_after = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.lot_stock_id.quant_ids
        }
        for line in self.inventory_not_annual.line_ids:
            oper_quant = self.qty_oper_after[line.product_id.id]
            self.assertEqual(oper_quant, line.product_qty)
        if pd:
            self.save_xlsx_report('inventory_not_annual')

        self.assertFalse(bool(self.inventory.account_move_id))

    def test_inventory_differenses(self):
        self.qty_oper_before = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.lot_stock_id.quant_ids
        }
        self.qty_diff_before = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.wh_stock_diff.quant_ids
        }

        self.inventory = self._create_invenotory_differenses()
        self.valuated_after = self._calculate_veluations_product()
        self.qty_diff_after = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.wh_stock_diff.quant_ids
        }
        self.qty_oper_after = {
            i.product_id.id: i.quantity or 0
            for i in self.warehouse.lot_stock_id.quant_ids
        }

        merged = self._merge_results()
        if pd:
            self.save_xlsx_report('inventory_annual')
        for vals in merged.values():
            oper_before = vals.get('oper_before')
            oper_after = vals.get('oper_after')
            diff_before = vals.get('diff_before')
            diff_after = vals.get('diff_after')
            value_value_before = round(vals.get('value_value_before'), 4)
            value_qty_before = vals.get('value_qty_before')
            value_qty_after = vals.get('value_qty_after')
            diff_svl_result_money = round(vals.get('diff_svl_result_money'), 4)
            value_value_after = round(vals.get('value_value_after'), 4)
            move_result = vals.get('move_result')
            as_qty_value_before = value_qty_before - (oper_before + diff_before)
            as_qty_value_after = value_qty_after - (oper_after + diff_after)
            as_value_before_diff = value_value_after - (diff_svl_result_money + value_value_before)
            as_qty_result = (oper_after - move_result) - (oper_before + diff_before)
            self.assertEqual(as_qty_value_before, 0)
            self.assertEqual(as_qty_value_after, 0)
            try:
                self.assertLess(abs(as_value_before_diff), 1, vals)
            except:
                _logger.info(vals)
            self.assertLess(abs(as_value_before_diff), 1)
            self.assertEqual(as_qty_result, 0)
        self.assertTrue(bool(self.inventory.account_move_id))
        lines = defaultdict(list)
        svls = defaultdict(list)
        for line in self.inventory.account_move_id.line_ids.filtered(lambda a: a.account_internal_group == 'expense'):
            lines[line.product_id] += line
        for svl in self.inventory.account_move_id.stock_valuation_layer_ids:
            svls[svl.product_id] += svl
        for svl_inv in self.inventory.mapped('move_ids.stock_valuation_layer_ids').filtered(
                lambda s: s.transaction_system_name in ['STOCKTAKE_SURPLUS_RESULT', 'STOCKTAKE_WRITEOFF_RESULT']
          ):
            acc_lines = lines[svl_inv.product_id]
            for i in acc_lines:
                if svl_inv.value > 0:
                    self.assertEqual(round(-svl_inv.value, 2), round(i.balance, 2))
                else:
                    self.assertEqual(round(svl_inv.value, 2), round(-i.balance, 2))
        self.assertEqual(sum(i for i in self.qty_diff_after.values()), 0)
        self.assertEqual(self.inventory.state, 'done')
        # Проверяем лавка тайп в мувах
        inventory_loc = (
            ('DIFF', 'OPER'),
            ('OPER', 'DIFF'),
        )
        for i in self.inventory.move_ids:
            before_qty = self.qty_diff_before.get(i.product_id.id, 0) + self.qty_oper_before.get(i.product_id.id, 0)
            for inv_line in self.inventory.line_ids:
                if i.product_id == inv_line.product_id:
                    self.assertEqual(i.date, self.inventory.date)
                    for svl in i.stock_valuation_layer_ids:
                        self.assertEqual(i.inventory_id.date, svl.document_datetime)
                        self.assertEqual(i.date, svl.document_datetime)
                    if inv_line.product_qty >= before_qty:
                        if (i.location_id.name, i.location_dest_id.name) not in inventory_loc:
                            self.assertEqual(i.lavka_type, 'stocktake_suplus_result')
                            continue
                        if inv_line.product_qty < self.qty_oper_before.get(i.product_id.id, 0):
                            self.assertEqual(i.lavka_type, 'stocktake_suplus_out')
                        elif inv_line.product_qty >= self.qty_oper_before.get(i.product_id.id, 0):
                            self.assertEqual(i.lavka_type, 'stocktake_suplus_in')
                        else:
                            raise Exception('Что то очень странное')
                    if inv_line.product_qty < before_qty:
                        if (i.location_id.name, i.location_dest_id.name) not in inventory_loc:
                            self.assertEqual(i.lavka_type, 'stocktake_writeoff_result')
                            continue
                        if inv_line.product_qty >= self.qty_oper_before.get(i.product_id.id, 0):
                            self.assertEqual(i.lavka_type, 'stocktake_writeoff_in')
                        elif inv_line.product_qty < self.qty_oper_before.get(i.product_id.id, 0):
                            self.assertEqual(i.lavka_type, 'stocktake_writeoff_out')
                        else:
                            raise Exception('Что то очень странное')



        # self.assertEqual(len(inventory.line_ids), 99) #TODO: Почему то не проходит иногда

    def test_veluations_diff(self):
        for move in self.diff_moves:
            if move.location_id.name == 'DIFF' and move.location_dest_id.name == 'OPER':
                try:
                    self.assertEqual(len(move.stock_valuation_layer_ids), 2)
                except AssertionError:
                    self.assertEqual(len(move.stock_valuation_layer_ids), 3)
                for svl in move.stock_valuation_layer_ids:
                    # self.assertEqual(move.picking_id.date, svl.document_datetime)
                    # self.assertEqual(move.date, svl.document_datetime)
                    if svl.location_id.name == 'DIFF':
                        self.assertEqual(svl.transaction_system_name, 'RECOUNT_IN_DIFF')
                    else:
                        self.assertEqual(svl.transaction_system_name, 'RECOUNT_IN_OPER')
            if move.location_id.name == 'OPER' and move.location_dest_id.name == 'DIFF':
                try:
                    self.assertEqual(len(move.stock_valuation_layer_ids), 2)
                except AssertionError:
                    self.assertEqual(len(move.stock_valuation_layer_ids), 3)
                for svl in move.stock_valuation_layer_ids:
                    # self.assertEqual(move.picking_id.date, svl.document_datetime)
                    # self.assertEqual(move.date, svl.document_datetime)
                    if svl.location_id.name == 'OPER':
                        self.assertEqual(svl.transaction_system_name, 'RECOUNT_OUT_OPER')
                    else:
                        try:
                            self.assertEqual(svl.transaction_system_name, 'RECOUNT_OUT_DIFF')
                        except AssertionError:
                            self.assertEqual(svl.transaction_system_name, 'PRICE_DIFF_CORR')

    def test_lavka_type(self):
        moves = self.diff_moves
        for o in self.sale_order_ids:
            for ol in o.order_line:
                moves += ol.move_ids
        for o in self.purchase_order_ids:
            for ol in o.order_line:
                moves += ol.move_ids
        for i in moves:
            if i.location_id.name == 'OPER' and i.location_id.name == 'DIFF':
                self.assertEqual(i.lavka_type, 'recount_out')
                self.assertEqual(len(i.stock_valuation_layer_ids), 2)
                for svl in i.stock_valuation_layer_ids:
                    self.assertEqual(i.date, svl.document_datetime)
                    self.assertEqual(i.picking_id.date, svl.document_datetime)
            if i.location_id.name == 'DIFF' and i.location_id.name == 'OPER':
                self.assertEqual(i.lavka_type, 'recount_in')
                self.assertEqual(len(i.stock_valuation_layer_ids), 2)
                for svl in i.stock_valuation_layer_ids:
                    self.assertEqual(i.date, svl.document_datetime)
                    self.assertEqual(i.picking_id.date, svl.document_datetime)
            if i.location_id.name == 'OPER' and i.location_dest_id.name == 'Customers':
                self.assertEqual(i.lavka_type, 'sale')
                self.assertEqual(len(i.stock_valuation_layer_ids), 1)
                for svl in i.stock_valuation_layer_ids:
                    self.assertEqual(i.sale_line_id.order_id.date_order, svl.document_datetime)
                    self.assertEqual(i.picking_id.date, svl.document_datetime)
                    self.assertEqual(i.date, svl.document_datetime)
            if i.location_dest_id.name == 'OPER' and i.location_id.name == 'Vendors':
                self.assertIn(i.lavka_type, ['inbound', 'invoice'])
                self.assertEqual(len(i.stock_valuation_layer_ids.filtered(
                    lambda l: l.transaction_system_name != 'COST_PRICE_CORR')), 1)
                for svl in i.stock_valuation_layer_ids:
                    if svl.transaction_system_name == 'P_ACCR':
                        self.assertEqual(i.purchase_line_id.order_id.date_order, svl.document_datetime)
                        self.assertEqual(i.picking_id.date, svl.document_datetime)
                        self.assertEqual(i.date, svl.document_datetime)

    # pylint: disable=too-many-nested-blocks
    def test_valuation_invoiced(self):
        for o in self.purchase_order_ids:
            for ol in o.order_line:
                if ol.state == 'purchase':
                    self.assertIn(len(ol.stock_valuation_layer_ids), list(range(8)))
                    self.assertEqual(len(ol.invoice_lines), 2)
                for svl in ol.stock_valuation_layer_ids:
                    if svl.transaction_system_name == 'P_ACCR':
                        self.assertEqual(ol.order_id.date_order, svl.document_datetime)
                    elif svl.transaction_system_name in ['P_INVOICE', 'ST_ACCR']:
                        for line in ol.invoice_lines:
                            if not line.exclude_from_invoice_tab:
                                self.assertEqual(line.date, svl.document_date)
                                # self.assertEqual(line.move_id.payment_reference, Datetime.to_string(
                                #     svl.document_datetime))
