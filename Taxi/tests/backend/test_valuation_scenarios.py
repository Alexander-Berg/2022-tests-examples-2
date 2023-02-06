# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error,bad-continuation
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import os
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import Form
from datetime import datetime as dt

from .test_common import _logger, TestVeluationCommon, SavepointCase
from odoo.addons.lavka.tests.utils import save_xlsx_report, get_stock_loc


# pylint: disable=invalid-name,too-many-statements
@tagged('lavka', 'value', 'direct')
class TestStockInventoryStandard(TestVeluationCommon):
    """
    price_unit = 5.25
    Метод в динамике проверяет себестоимость товара
    """

    def test_direct_scenario(self):
        # Приходуем товары по 5.25, на склад дожно прийти 25 товаров на сумму 131.25
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_1.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
                'wms_id': f'wms_id_{i}'
            })
            for i in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 5,
                    'product_init_qty': 5,
                    'order_id': po.id,
                    'price_unit': 5.25,
                }
                for i in self.products[:5]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

            for pl in po.order_line:
                moves = self.env['stock.move']
                moves += pl.change_target_received_qty(10)
                self.assertEqual(pl.qty_received, 10)
                moves += pl.change_target_received_qty(5)
                self.assertEqual(pl.qty_received, 5)
                moves += pl.change_target_received_qty(7)
                self.assertEqual(pl.qty_received, 7)
                moves += pl.change_target_received_qty(5)
                self.assertEqual(pl.qty_received, 5)

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id)
        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[self.warehouse_1.lot_stock_id.id, self.warehouse_1.wh_stock_diff.id],
                report_name='report_scenario',
            )
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)
        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'warehouse_id': self.warehouse_1.id,
            })
            for _ in range(1)
        ]
        # Продаем 5 товаров по 5.25 и после продажи должно остаться 20 на сумму 105
        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 1,
                    'price_unit': 5,# Кажется данная цена ни на что не влияет, т.к. берется средняя по остаткам
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 20.0)
        self.assertEqual(valuation_qty, 20.0)
        self.assertEqual(value, 105.0)
        self.assertEqual(rem_qty, 20.0)
        self.assertEqual(rem_value, 105.0)

        # Списывем 5шт по 5,25 и должно остаться на складе 15 на 78.75
        self.scrap = self.env['stock.scrap'].create({
            'location_id': self.warehouse_1.lot_stock_id.id,
            'date_done': fields.Date.today(),
            'scrap_location_id': self.env['stock.scrap']._get_default_scrap_location_id(),
        })
        vals_move = [{
            'scrap_id': self.scrap.id,
            'product_id': i.id,
            'product_uom_qty': 1,
            'product_uom': i.uom_id.id,
            'name': f'{i.name}',
            'lavka_type': 'write_off',
            'location_dest_id': self.scrap.scrap_location_id.id,
            'location_id': self.scrap.location_id.id
        } for i in self.products[:5]]
        self.env['stock.move'].create(vals_move)
        self.scrap.action_validate()
        account_line_ids = {
            i.product_id: i for i in self.scrap.account_move_id.line_ids.filtered(
                lambda l: l.account_internal_group == 'asset')
        }
        svls = {
            i.product_id: i for i in self.scrap.move_ids.mapped('stock_valuation_layer_ids').filtered(
                lambda svl: svl.transaction_system_name == 'WRITE_OFF'
            )
        }
        for key, acc_line in account_line_ids.items():
            svl = svls[key]
            self.assertEqual(acc_line.balance, svl.value)
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 15.0)
        self.assertEqual(valuation_qty, 15.0)
        self.assertEqual(value, 78.75)
        self.assertEqual(rem_qty, 15.0)
        self.assertEqual(rem_value, 78.75)

        # ФАКТУРИРУЕМ

        for po in self.purchase_order_ids:
            with patch(
                'odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'bla2313ds'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 1, тем самым недооцениваем
                        line_form.price_unit = 1
                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 15.0)
        self.assertEqual(valuation_qty, 15.0)
        self.assertEqual(value, 15)
        self.assertEqual(rem_qty, 15.0)
        self.assertEqual(rem_value, 15)
        # Далее мы делаем пересчет товара
        for product in self.products[:5]:
            vals_move = {
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'name': f'{product.name}',
                'wms_id': 'Some ID',
                'lavka_type': 'recount_out',
                'location_dest_id': self.warehouse_1.wh_stock_diff.id,
                'location_id': self.warehouse_1.lot_stock_id.id,
            }
            move = self.env['stock.move'].create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 10.0)
        self.assertEqual(valuation_qty, 10.0)
        self.assertEqual(value, 10)
        self.assertEqual(rem_qty, 10.0)
        self.assertEqual(rem_value, 10)
        # Смотрим, что на diff тоже сформировался запас
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.wh_stock_diff
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(value, 5)
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 5)
        # Теперь закупаем еще товаров  по большей стоимости
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_1.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 5,
                    'product_init_qty': 5,
                    'order_id': po.id,
                    'price_unit': 5.25,
                }
                for i in self.products[:5]
            ]
            self.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()
        # смотрим как изменилась себестоимость
        # была себестоимость 10(1*10шт), и мы приняли товар 25шт по 131,5(5.25 * 25шт)
        # ИТОГО ± 141.25
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 35.0)
        self.assertEqual(valuation_qty, 35.0)
        self.assertEqual(round(value, 2), round(141.25, 2))
        self.assertEqual(rem_qty, 35.0)
        self.assertEqual(round(rem_value, 2), round(141.25, 2))
        # Смотрим, что на diff все осталось так же
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.wh_stock_diff
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(value, 5)
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 5)

        # Вытаскиваем из DIFF 4 штуки товара, и смотрим что
        # прошлая себестоимость 1 прибавится к текущей
        # те ожидем что будет 141.25 + (1 *4) = 145.25
        for product in self.products[:4]:
            vals_move = {
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'name': f'{product.name}',
                'wms_id': 'Some ID',
                'lavka_type': 'recount_in',
                'location_dest_id': self.warehouse_1.lot_stock_id.id,
                'location_id': self.warehouse_1.wh_stock_diff.id,
            }
            move = self.env['stock.move'].create([vals_move])
            move.quantity_done = move.product_uom_qty
            move._action_done()

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 39.0)
        self.assertEqual(valuation_qty, 39.0)
        self.assertEqual(round(value, 2), round(145.25, 2))
        self.assertEqual(rem_qty, 39.0)
        self.assertEqual(round(rem_value, 2), round(145.25, 2))

        # проверем, что на DIFF останется 1 с оставшейся суммой 1
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.wh_stock_diff
        )
        self.assertEqual(qty, 1.0)
        self.assertEqual(valuation_qty, 1.0)
        self.assertEqual(value, 1)
        self.assertEqual(rem_qty, 1.0)
        self.assertEqual(rem_value, 1)

        # Теперь проводим инвентаризацию с условиями
        # что всех товаров 40( всех по 8 ), а значит, что 1 потерявшийся товар, должен вернутся
        # к 145.25 должна вернутся потеряшка и 1 +  145.25 = 146.25
        self.inventory_diff_id = self.inventory.create({
            'name': 'Test Inventory differenses',
            'location_ids': [self.warehouse_1.lot_stock_id.id, ],
            'date': datetime.now()
        })
        self.inventory_diff_id.action_start()
        for line in self.inventory_diff_id.line_ids:
            line.product_qty = 8
        self.inventory_diff_id._action_done()

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 40.0)
        self.assertEqual(valuation_qty, 40.0)
        self.assertEqual(round(value, 2), round(146.25, 2))
        self.assertEqual(rem_qty, 40.0)
        self.assertEqual(round(value, 2), round(146.25, 2))

        # DIFF должен быть пустой
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.wh_stock_diff
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertLessEqual(abs(round(value, 2) - round(0.0, 2)), 0.1)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(round(rem_value, 2), round(0.0, 2))

        # Продаем 5 товаров по 5.25 и после продажи должно остаться 20 на сумму 105
        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'warehouse_id': self.warehouse_1.id,
            })
            for _ in range(1)
        ]

        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 7,
                    'price_unit': 5,
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(round(value, 1), round(18.3, 1))
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 18.3)

        # Теперь фактурируем каждую по 7
        # значит 25 из 40 товаров должны переоценится
        # сейчас лежат 40 товаров на сумму 146.25
        # 15 из них по цене 1 = 15
        # 25шт по 5.25 = 131,25
        # после переоценки с 5.25 на 40 25ь товаров станут стоить 1000
        # Итого: 15 + 175 = 222,45
        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch(
                'odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'blad21312s'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 40, тем самым переоцениваем
                        line_form.price_unit = 40
                        line_form.quantity = 2
                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(value, 26.25)
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 26.25)

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'blaasdasdads'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                line_form.price_unit = 5.25
        move_form.save()
        reverse_move.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(round(value, 1), round(18.3, 1))
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(round(value, 1), 18.3)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[self.warehouse_1.lot_stock_id.id, self.warehouse_1.wh_stock_diff.id],
                report_name='report_scenario',
            )

    def test_invoice_for_zero(self):
        # Приходуем товары по 5.25, на склад дожно прийти 25 товаров на сумму 131.25
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_2.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 5,
                    'product_init_qty': 5,
                    'order_id': po.id,
                    'price_unit': 5.25,
                }
                for i in self.products[:5]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)

        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'warehouse_id': self.warehouse_2.id,
            })
            for _ in range(1)
        ]
        # Продаем все
        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 5,
                    'price_unit': 5,
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')
        # Убеждаемся что склад пустой
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertEqual(value, 0.0)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(rem_value, 0.0)

        # фактурируем
        for po in self.purchase_order_ids:
            with patch(
                'odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'bladsds'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        line_form.price_unit = 6
                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids

        # должно быть все еще 0, НО! это благодяря корректирующей транзакции PRICE_DIFF_CORR'
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertEqual(value, 0.0)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(rem_value, 0.0)

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'blaasdasdads'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                line_form.price_unit = 6
        move_form.save()
        reverse_move.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertEqual(value, 0.0)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(rem_value, 0.0)

        # приходуем по 1 что бы приклеить остаток прошлых
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_2.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
            })
            for _ in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 1,
                    'product_init_qty': 1,
                    'order_id': po.id,
                    'price_unit': 5.25,
                }
                for i in self.products[:5]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()

        # принимаем 5товаров п 5, значит 25, НО! благодаря PRICE_DIFF_CORR
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(value, 26.25)
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 26.25)

        # Фактурируем без изменения цены
        for po in self.purchase_order_ids:
            with patch(
                'odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_2.lot_stock_id
        )
        self.assertEqual(qty, 5.0)
        self.assertEqual(valuation_qty, 5.0)
        self.assertEqual(value, 26.25)
        self.assertEqual(rem_qty, 5.0)
        self.assertEqual(rem_value, 26.25)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[self.warehouse_2.lot_stock_id.id, self.warehouse_2.wh_stock_diff.id],
                report_name='report_zero'
            )

    def test_invoice_storno(self):
        # Приходуем товары по 5.25, на склад дожно прийти 25 товаров на сумму 131.25
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
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
                    'product_qty': 5,
                    'product_init_qty': 5,
                    'order_id': po.id,
                    'price_unit': 5.25,
                }
                for i in self.products[:5]
            ]

            self.env['purchase.order.line'].create(purchase_line_vals)
            po.button_confirm()
            for move in po.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            po.picking_ids._action_done()

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)

        # сначала мы приходуем, но чуть по другой цене, что бы создатьт расхождения в + COST_DIFF
        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch(
                'odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'bladasaads'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        line_form.price_unit = 6
                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 150.0)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 150.0)

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'blaasdasdads'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 5.25
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)

        # теперь финт ушами продаем все и фактурируем
        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'warehouse_id': self.warehouse_3.id,
            })
            for _ in range(1)
        ]
        # Продаем все
        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 5,
                    'price_unit': 5,
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertEqual(value, 0.0)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(rem_value, 0.0)

        # фактурируем  по зивышенной цене

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bladdasd5678sas'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 7
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 0.0)
        self.assertEqual(valuation_qty, 0.0)
        self.assertEqual(value, 0.0)
        self.assertEqual(rem_qty, 0.0)
        self.assertEqual(rem_value, 0.0)

        # Возвращаем остаток на склад
        sale_o = self.sale_order_ids_rand[0]
        pick = sale_o.picking_ids
        wizard = self.env['sale.order.cancel'].with_context({'order_id': sale_o.id}).create({
            'order_id': sale_o.id})
        wizard.action_cancel()
        stock_return_picking_form = Form(self.env['stock.return.picking']
                                         .with_context(active_ids=pick.ids, active_id=pick.sorted().ids[0],
                                                       active_model='stock.picking'))

        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity = 5.0  # Return only 2
        return_wiz.product_return_moves.to_refund = True  # Refund these 2
        res = return_wiz.create_returns()
        return_pick = self.env['stock.picking'].browse(res['res_id'])

        for i in return_pick.move_lines:
            i.quantity_done = 5
        return_pick.move_lines.write({'quantity_done': 5})
        return_pick.button_validate()

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 25.0)
        self.assertEqual(valuation_qty, 25.0)
        self.assertEqual(value, 175.0)
        self.assertEqual(rem_qty, 25.0)
        self.assertEqual(rem_value, 175.0)
        # списываем по 1
        self.scrap = self.env['stock.scrap'].create({
            'location_id': self.warehouse_3.lot_stock_id.id,
            'date_done': fields.Date.today(),
            'scrap_location_id': self.env['stock.scrap']._get_default_scrap_location_id(),
        })
        vals_move = [{
            'scrap_id': self.scrap.id,
            'product_id': i.id,
            'product_uom_qty': 1,
            'product_uom': i.uom_id.id,
            'name': f'{i.name}',
            'lavka_type': 'write_off',
            'location_dest_id': self.scrap.scrap_location_id.id,
            'location_id': self.scrap.location_id.id
        } for i in self.products[:5]]
        self.env['stock.move'].create(vals_move)
        self.scrap.action_validate()
        account_line_ids = {
            i.product_id: i for i in self.scrap.account_move_id.line_ids.filtered(
                lambda l: l.account_internal_group == 'asset')
        }
        svls = {
            i.product_id: i for i in self.scrap.move_ids.mapped('stock_valuation_layer_ids').filtered(
                lambda svl: svl.transaction_system_name == 'WRITE_OFF'
            )
        }
        for key, acc_line in account_line_ids.items():
            svl = svls[key]
            self.assertEqual(acc_line.balance, svl.value)
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 20.0)
        self.assertEqual(valuation_qty, 20.0)
        self.assertEqual(value, 140)
        self.assertEqual(rem_qty, 20.0)
        self.assertEqual(rem_value, 140)

        # фактурируем в 3р
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'blxcccccads'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 7
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 20.0)
        self.assertEqual(valuation_qty, 20.0)
        self.assertEqual(value, 140.0)
        self.assertEqual(rem_qty, 20.0)
        self.assertEqual(rem_value, 140.0)

        # Продаем по 1й
        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'warehouse_id': self.warehouse_3.id,
            })
            for _ in range(1)
        ]
        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 1,
                    'price_unit': 5,
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')

        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'blads12321312'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 7
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 15.0)
        self.assertEqual(valuation_qty, 15.0)
        self.assertEqual(round(value, 2), 105.0)
        self.assertEqual(rem_qty, 15.0)
        self.assertEqual(round(rem_value, 2), 105.0)

        # фактурируем снова по 6
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bladadasdsadsas'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 6
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_3.lot_stock_id
        )
        self.assertEqual(qty, 15.0)
        self.assertEqual(valuation_qty, 15.0)
        self.assertEqual(round(value, 2), 80)
        self.assertEqual(rem_qty, 15.0)
        self.assertEqual(round(rem_value, 2), 80)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[self.warehouse_3.lot_stock_id.id, self.warehouse_3.wh_stock_diff.id],
                report_name='report_storno'
            )


@tagged('lavka', 'diffs')
class TestCostPriceCorr(TestVeluationCommon):
    def test_diffs(self):
        # Приходуем товары по 5, на склад дожно прийти 100 товаров на сумму 500
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_1.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
                'wms_id': f'wms_id_{i}'
            })
            for i in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 100,
                    'product_init_qty': 100,
                    'order_id': po.id,
                    'price_unit': 5,
                }
                for i in self.products[:1]
            ]
        self.env['purchase.order.line'].create(purchase_line_vals)
        po.button_confirm()
        for move in po.picking_ids.move_line_ids:
            move.qty_done = move.product_qty
        po.picking_ids._action_done()

        _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        c = 1
        self.purchase_order_ids = [
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'picking_type_id': self.warehouse_1.in_type_id.id,
                'requisition_id': self.purchase_requsition.id,
                'wms_id': f'wms_id_{i}'
            })
            for i in range(1)
        ]
        for po in self.purchase_order_ids:
            purchase_line_vals = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_qty': 1,
                    'product_init_qty': 1,
                    'order_id': po.id,
                    'price_unit': 1,
                }
                for i in self.products[:1]
            ]
        self.env['purchase.order.line'].create(purchase_line_vals)
        po.button_confirm()
        for move in po.picking_ids.move_line_ids:
            move.qty_done = move.product_qty
        po.picking_ids._action_done()

        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.warehouse_1.lot_stock_id
        )
        c =1

@tagged("lavka", "svl_wh")
class TestSVL(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=1, create_parents=False)[0]
        tax = cls.env['account.tax'].search([('type_tax_use', '=', 'purchase')])[0]
        if not tax:
            tax = cls.factory.create_tax(
                ['amount', 'type_tax_use'],
                [1.2, 'purchase']
            )

        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'),
            tax_id=tax.id

        )

    def test_sad(self):
        product_obj = self.products[0]
        delta_count = 5
        curr_location_id = self.warehouses[0].lot_stock_id.id
        location_dest_id = self.warehouses[0].wh_stock_diff.id

        vals_move = {
            'product_id': product_obj.id,
            'product_uom_qty': delta_count,
            'quantity_done': delta_count,
            'product_uom': product_obj.uom_id.id,
            'description_picking': 'recount',
            'name': product_obj.name,
            'location_id': curr_location_id,
            'location_dest_id': location_dest_id,
            'wms_id': uuid4().hex,
            'origin': 'test_origin',
            'date': dt.now(),
            'picking_code': 'internal',
            'lavka_type': 'recount_in',
        }
        m = self.env['stock.move'].create([vals_move])
        svl_obj = self.env['stock.valuation.layer']
        invoice_vals = svl_obj._pre_create_svl_by_move(m)
        for val in invoice_vals:
            val.update({
                'warehouse_id': None
            })
        svl = svl_obj.create(invoice_vals)
        self.assertTrue(svl)
