# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error,bad-continuation
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import os

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import Form
from unittest.mock import patch
from .test_common import _logger, TestVeluationCommon


# pylint: disable=invalid-name,too-many-statements
@tagged('lavka', 'value', 'notes')
class TestNoteInventoryStandard(TestVeluationCommon):
    """
    price_unit = 5.25
    Метод в динамике проверяет себестоимость товара
    """

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

    def test_invoice_notes(self):
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

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)

        # сначала мы приходуем, но чуть по другой цене, что бы создатьт расхождения в + COST_DIFF
        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch('odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                for i, _ in enumerate(invoice.invoice_line_ids):
                    if i == 4:
                        move_form.invoice_line_ids.remove(i)
                        continue
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        line_form.price_unit = 6

                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        # Ожидаем, что 20 шт будут переоценены по 6р, НО! 5 штук из diff, должны быть по 5.25 из прошлого ACCR

        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 146.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 146.25)
        # Плюс не должен быть отрицательный остаток в DIFF
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        # Вводим кредит ноту на 1 по всем позициям
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': lastinvoice.date,
            'reason': 'no reason',
            'refund_method': 'refund',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bla_212312312'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.quantity = 1
                line_form.amount_currency = 5

        move_form.save()
        reverse_move.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)

        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 146.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 146.25)
        # Плюс должен быть отрицательный остаток в DIFF из за кредит-ноты
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, -4)
        self.assertEqual(valuation_qty, -4)
        self.assertEqual(value, -20)
        self.assertEqual(rem_qty, -4)
        self.assertEqual(rem_value, -20)

        # Вводим дебит ноту, и должно все выровниться
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'cancel',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bla_212312312'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.quantity = 1
                line_form.amount_currency = 5.25

        move_form.save()
        reverse_move.action_post(force_post=True)

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)

        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 146.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 146.25)
        # Плюс должен быть отрицательный остаток в DIFF
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            self.save_xlsx_report(
                locations=[self.warehouse_3.lot_stock_id.id, self.warehouse_3.wh_stock_diff.id],
                report_name='report_remove_from_invoice'
            )

@tagged('lavka', 'value', 'hardnotes')
class TestNoteInventoryStandard(TestNoteInventoryStandard):
    """
    price_unit = 5.25
    Метод в динамике проверяет себестоимость товара
    """
    def test_invoice_hard_notes(self):
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
            po.order_line[0].product_init_qty = 5
            po.button_confirm()
            for i, move in enumerate(po.picking_ids.move_lines):
                if i == 0:
                    po.order_line[0].product_qty = 0
                    move.product_uom_qty = 0
                    move.quantity_done = 0
                    continue
                move.quantity_done = move.product_qty
            po.picking_ids._action_done()

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 105)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 105)

        # self.test_move.write({
        #     'line_ids': [
        #         (1, lines[0].id, {'credit': lines[0].credit + 100.0}),
        #         (1, lines[2].id, {'debit': lines[2].debit + 100.0}),
        #     ],
        # })
        # Делаем очень кривой приход
        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch('odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'bla_1'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    if i == 4:
                        move_form.invoice_line_ids.remove(i)
                        continue
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        if i == 3:
                            line_form.quantity = 6
                            line_form.price_unit = 6
                            continue
                        if i == 0:
                            line_form.quantity = 5
                            line_form.price_unit = 6
                            continue
                        elif i == 2:
                            line_form.quantity = 3
                            line_form.price_unit = 6
                            continue
                        line_form.price_unit = 6

                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids
        # Позиция 0 одинакова
        # Позиция 1 пришло 5 по 5.25, но из инвойса удалили
        # Позиция 2 пришло 5, но в инвойсе ввели 3 по цене 6 = 18р
        # Позиция 3 пришло 5, но в инвойсе ввели 6
        # Позиция 4 не пришла, но в инвойсе ввели 5 по цене 6
        # ИТОГО, количество должно быть 25 штук принятых по инвойсу = по цене 6,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        # Ожидаем, что 20 шт будут переоценены по 6р, НО! 5 штук из diff, должны быть по 5.25 из прошлого ACCR
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 120.0)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 120.0)
        # Плюс должен быть отрицательный остаток в DIFF
        # Обьяснение -5 появилось из первой позиции, тк прихода небыло,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, -1)
        self.assertEqual(valuation_qty, -1)
        self.assertEqual(value, -6)
        self.assertEqual(rem_qty, -1)
        self.assertEqual(rem_value, -6)

        # Все сторнируем и вводим другие данные
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bla_2'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.price_unit = 7
        with move_form.invoice_line_ids.new() as new_line:
            new_line.account_id = self.env['account.account'].browse([26])
            new_line.product_id = po.order_line[0].product_id
            new_line.purchase_line_id = po.order_line[0]
            new_line.quantity = 7
            new_line.price_unit = 7


        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        # Ожидаем, что 20 шт будут переоценены по 6р, НО! 5 штук из diff, должны быть по 5.25 из прошлого ACCR
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 136.5)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 136.5)
        # Плюс должен быть отрицательный остаток в DIFF
        # Обьяснение -5 появилось из первой позиции, тк прихода небыло,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, 6)
        self.assertEqual(valuation_qty, 6)
        self.assertEqual(value, 45.5)
        self.assertEqual(rem_qty, 6)
        self.assertEqual(rem_value, 45.5)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            self.save_xlsx_report(
                locations=[self.warehouse_3.lot_stock_id.id, self.warehouse_3.wh_stock_diff.id],
                report_name='report_remove_hard_notes'
            )

@tagged('lavka', 'value', 'one_po')
class TestNoteInventoryStandardNew(TestNoteInventoryStandard):
    """
    price_unit = 5.25
    Метод в динамике проверяет себестоимость товара
    """
    def test_invoice_two_bills_for_one_po(self):
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
            po.order_line[0].product_init_qty = 5
            po.button_confirm()
            for i, move in enumerate(po.picking_ids.move_line_ids):
                if i == 0:
                    po.order_line[0].product_qty = 0
                    move.qty_done = 0
                    continue
                move.qty_done = move.product_qty
            po.picking_ids._action_done()

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 105)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 105)

        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch('odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids:
                move_form = Form(invoice)
                move_form.ref = 'bla_1'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    if i == 4:
                        move_form.invoice_line_ids.remove(i)
                        continue
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        if i == 3: # 3 позиция +1 по количеству
                            line_form.quantity = 6
                            line_form.price_unit = 6
                            continue
                        if i == 0:
                            line_form.quantity = 5
                            line_form.price_unit = 6
                            continue
                        elif i == 2:
                            line_form.quantity = 3
                            line_form.price_unit = 6
                            continue
                        line_form.price_unit = 6

                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.action_post(force_post=True)
            lastinvoice = _order.invoice_ids
        # Позиция 0 одинакова
        # Позиция 1 пришло 5 по 5.25, но из инвойса удалили
        # Позиция 2 пришло 5, но в инвойсе ввели 3 по цене 6 = 18р
        # Позиция 3 пришло 5, но в инвойсе ввели 6
        # Позиция 4 не пришла, но в инвойсе ввели 5 по цене 6
        # ИТОГО, количество должно быть 25 штук принятых по инвойсу = по цене 6,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        # Ожидаем, что 20 шт будут переоценены по 6р, НО! 5 штук из diff, должны быть по 5.25 из прошлого ACCR
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 120.0)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 120.0)
        # Плюс должен быть отрицательный остаток в DIFF
        # Обьяснение -5 появилось из первой позиции, тк прихода небыло,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, -1)
        self.assertEqual(valuation_qty, -1)
        self.assertEqual(value, -6)
        self.assertEqual(rem_qty, -1)
        self.assertEqual(rem_value, -6)

        lastinvoice = None
        for po in self.purchase_order_ids:
            with patch('odoo.addons.lavka.backend.models.purchase_order.PurchaseOrder.date_in_safe_period') as safe_period:
                safe_period.return_value = True, 'ok'
                po.action_create_invoice()
            for invoice in po.invoice_ids.filtered(lambda inoice: inoice.state == 'draft'):
                lastinvoice = invoice
                move_form = Form(invoice)
                move_form.ref = 'bla_3'
                move_form.invoice_date = fields.Date.today()
                for i, _ in enumerate(invoice.invoice_line_ids):
                    if i == 4:
                        move_form.invoice_line_ids.remove(i)
                        continue
                    with move_form.invoice_line_ids.edit(i) as line_form:
                        # Ставим всем цену 6, тем самым переоцениваем
                        if i == 3: # 3 позиция +1 по количеству
                            line_form.quantity = 1
                            line_form.price_unit = 6
                            continue
                        elif i == 2:
                            line_form.quantity = 2
                            line_form.price_unit = 6
                            continue
                        line_form.price_unit = 6

                move_form.save()
        for _order in (order for order in self.purchase_order_ids):
            _order.invoice_ids.filtered(lambda inoice: inoice.state == 'draft').action_post(force_post=True)


        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        # Ожидаем, что 20 шт будут переоценены по 6р, НО! 5 штук из diff, должны быть по 5.25 из прошлого ACCR
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 120.0)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 120.0)
        # Плюс должен быть отрицательный остаток в DIFF
        # Обьяснение -5 появилось из первой позиции, тк прихода небыло,
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, 1)
        self.assertEqual(valuation_qty, 1)
        self.assertEqual(value, 6)
        self.assertEqual(rem_qty, 1)
        self.assertEqual(rem_value, 6)

        # Все сторнируем и вводим другие данные
        move_reversal = self.env['account.move.reversal'].with_context(active_model="account.move",
                                                                       active_ids=lastinvoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'refund_method': 'modify',
        })
        reversal = move_reversal.reverse_moves()
        reverse_move = self.env['account.move'].browse(reversal['res_id'])
        move_form = Form(reverse_move)
        move_form.ref = 'bla_6'
        move_form.invoice_date = fields.Date.today()
        for i, _ in enumerate(reverse_move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                # Ставим всем цену 6, тем самым переоцениваем
                line_form.quantity = 1
        move_form.save()
        reverse_move.action_post(force_post=True)
        lastinvoice = reverse_move

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.lot_stock_id)
        #
        self.assertEqual(qty, 20)
        self.assertEqual(valuation_qty, 20)
        self.assertEqual(value, 120.0)
        self.assertEqual(rem_qty, 20)
        self.assertEqual(rem_value, 120)
        # На Дифе должно быть по налям, тк выровняли все
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_3.wh_stock_diff)
        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)
        if os.environ.get('EXPORT_TEST_TO_XLS'):
            self.save_xlsx_report(
                locations=[self.warehouse_3.lot_stock_id.id, self.warehouse_3.wh_stock_diff.id],
                report_name='report_remove_hard_notes_one_po'
            )
