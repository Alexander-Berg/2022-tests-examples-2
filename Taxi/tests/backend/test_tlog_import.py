# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error,bad-continuation
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated

from odoo.tests import tagged

from .test_common import _logger, TestVeluationCommon


@tagged('lavka', 'value', 'tlog')
class TesttlogImport(TestVeluationCommon):
    """
    price_unit = 5.25
    Метод в динамике проверяет себестоимость товара
    """

    @classmethod
    def setUpClass(cls):
        super(TesttlogImport, cls).setUpClass()

        tlog_transactions = [
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T19:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': 1,
                'product_id': '1',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'payment',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T18:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': 1,
                'product_id': '2',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'payment',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T11:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': 1,
                'product_id': '3',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'payment',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T20:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': 1,
                'product_id': '4',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'payment',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T20:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': 1,
                'product_id': '5',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'payment',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
            # скидка
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T11:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': -1,
                'product_id': '1',
                'vat': 0.1,
                'quantity': 0,
                'amount': 1,
                'transaction_type': 'refund',
                'orig_transaction_id': '9883338974',
                'detailed_product': 'discount'
            },
            # возврат
            {
                'place_id': 'TT1',
                'invoice_date': '2020-02-23T19:59:33.720000+00:00',
                'order_id': 'grossery_1',
                'aggregation_sign': -1,
                'product_id': '2',
                'vat': 0.9,
                'quantity': 1,
                'amount': 8,
                'transaction_type': 'refund',
                'orig_transaction_id': f'9883338971',
                'detailed_product': 'grocery_item_sale_vat_17'
            },
        ]
        cls.tlog = cls.env['tlog.transaction'].create(tlog_transactions)
    #
    # def save_xlsx_report(self, locations, report_name=None, ):
    #     # pylint: disable=import-outside-toplevel
    #     import pandas as pd
    #     res = []
    #     valuation_lines = self.env['stock.valuation.layer'].search([
    #         ('location_id', 'in', locations),
    #     ])
    #     for val in valuation_lines:
    #         try:
    #             cost_price = val.remaining_value / val.remaining_qty
    #         except ZeroDivisionError:
    #             cost_price = 0
    #         res.append({
    #             'PRICE_RULE': val.price_rule,
    #             'TRANSACTION_SYSTEM_NAME': val.transaction_system_name,
    #             'TRANS_SYSTEM_GROUP': val.trans_system_group,
    #             'TRANS_ID': val.trans_id,
    #             'PRODUCT_EXTERNAL_ID': val.product_id.default_code,
    #             'VIRT_WHS': val.location_id.name,
    #             'UNIT_COST': val.unit_cost,
    #             'QTY': val.quantity,
    #             'VALUE': val.value,
    #             'TAX_ID': val.tax_id.name,
    #             'TAX_SUM': val.tax_sum,
    #             'REMAINING-QTY': val.remaining_qty,
    #             'REMAINING-VALUE': val.remaining_value,
    #             'COST_PRICE': cost_price,
    #             'DESCRIPTION': val.description,
    #             'DOCUMENT_DATETIME': val.document_datetime,
    #             'DOCUMENT_DATE': val.document_date,
    #             'CREATE': val.create_date,
    #             'COMPANY_ID': val.company_id.id,
    #         })
    #     df = pd.DataFrame(res)
    #     writer = pd.ExcelWriter(f'{report_name}.xlsx')
    #     df.to_excel(writer, 'Sheet1')
    #     writer.save()
    #
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

    def test_tlog_import(self):
        # Приходуем товары по 5.25, на склад дожно прийти 25 товаров на сумму 131.25
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

            _logger.debug(f'Picking {po.picking_ids.id} confirmed')

        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_1.lot_stock_id)
        self.assertEqual(qty, 25)
        self.assertEqual(valuation_qty, 25)
        self.assertEqual(value, 131.25)
        self.assertEqual(rem_qty, 25)
        self.assertEqual(rem_value, 131.25)
        self.sale_order_ids_rand = [
            self.env['sale.order'].create({
                'partner_id': self.partner.id,
                'external_id': 'grossery_1',
                'warehouse_id': self.warehouse_1.id,
            })
            for _ in range(1)
        ]
        w = 1
        for i in self.products[:5]:
            i.wms_id = f'{w}'
            i.taxes_id = self.env['account.tax'].search([])[0]
            w += 1

        # Продаем 5 товаров по 5.25 и после продажи должно остаться 20 на сумму 105
        for i, product in enumerate(self.products[:5]):
            product.wms_id = str(i+1)

        for o in self.sale_order_ids_rand:
            so_lines = [
                {
                    'product_id': i.id,
                    'name': f'{i.name}: line',
                    'product_uom_qty': 1,
                    'price_unit': 10,
                    'order_id': o.id,
                }
                for i in self.products[:5]
            ]
            self.sale_order_line.create(so_lines)
            o.action_confirm()
            self.assertTrue(o.picking_ids.move_line_ids)
            for move in o.picking_ids.move_line_ids:
                move.qty_done = move.product_qty
            o.picking_ids._action_done()
            _logger.debug(f'Sale rand order {o.id} confirmed')
        qty, valuation_qty, value, rem_qty, rem_value = self.get_stock_loc(self.warehouse_1.lot_stock_id)
        self.assertEqual(qty, 20.0)
        self.assertEqual(valuation_qty, 20.0)
        self.assertEqual(value, 105.0)
        self.assertEqual(rem_qty, 20.0)
        self.assertEqual(rem_value, 105.0)

        self.tlog.processing_tlog()
