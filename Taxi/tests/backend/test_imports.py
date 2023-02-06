import base64
import random
from io import BytesIO

import openpyxl
from freezegun import freeze_time
from random import randrange
from uuid import uuid4

from odoo import fields
from odoo.modules.module import get_resource_path
from odoo.tests import tagged
from odoo.tests.common import HttpSavepointCase, SavepointCase
from odoo.tools import file_open
import datetime as dt


@tagged('lavka', 'autoorder', 'autoorder_imports')
class TestImports(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_assortment.xls'), 'rb'
        ) as f:
            cls.assort_file = base64.b64encode(f.read())

        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_purchase_orders.xls'), 'rb'
        ) as f:
            cls.pur_orders_file = base64.b64encode(f.read())

        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_requisition_lines.xlsx'), 'rb'
        ) as f:
            cls.req_lines_file = base64.b64encode(f.read())

        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_requisition_lines_common.xlsx'), 'rb'
        ) as f:
            cls.req_lines_file_common = base64.b64encode(f.read())

        cls.p_tag1 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'assort_1',
            }
        )
        cls.p_tag2 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'assort_2',
            }
        )
        cls.p_tag3 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'assort_tag_1',
            }
        )
        cls.p_tag4 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'assort_tag_2',
            }
        )
        cls.p_tag5 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'assor_tag_3',
            }
        )

        cls.assort_tags_pre = [cls.p_tag1.id, cls.p_tag2.id, cls.p_tag3.id]
        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'geo-1',
            }
        )

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'geo-2',
            }
        )
        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': 'a-001',
                'code': 'a-001',
                'warehouse_tag_ids': [cls.wh_tag1.id, cls.wh_tag2.id],
            }
        )
        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'a-002',
                'code': 'a-002',
                'warehouse_tag_ids': [cls.wh_tag2.id, cls.wh_tag2.id],
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {'name': 'p-001',
             'default_code': '3866',
             'product_tag_ids': [(6, 0, cls.assort_tags_pre)],
             'wms_id': '3866',
             },
        )
        cls.p2 = cls.env['product.product'].create(
            {'name': 'p-002',
             'default_code': '2987',
             'product_tag_ids': [(6, 0, cls.assort_tags_pre)],
             'wms_id': '2987',
             },
        )
        cls.p3 = cls.env['product.product'].create(
            {'name': 'p-003',
             'default_code': '118751',
             'wms_id': '118751',
             },
        )
        cls.p4 = cls.env['product.product'].create(
            {'name': 'p-004',
             'default_code': '31192',
             'wms_id': '31192',
             },
        )
        cls.p5 = cls.env['product.product'].create(
            {'name': 'p-005',
             'default_code': '6295477',
             'wms_id': '6295477',
             'product_tag_ids': [(6, 0, cls.assort_tags_pre)]
             },
        )
        cls.p6 = cls.env['product.product'].create(
            {'name': 'p-006',
             'default_code': '6295488',
             'wms_id': '6295488',
             },
        )
        cls.p7 = cls.env['product.product'].create(
            {'name': 'p-007',
             'default_code': '6283549',
             'wms_id': '6283549',
             },
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-001',
                'is_company': True,
            }
        )
        cls.v1.external_id = 123454321

        cls.pr_v1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'warehouse_tag_ids': [cls.wh_tag1.id, cls.wh_tag2.id],
                'state': 'ongoing',
            }
        )
        cls.env['purchase.requisition.line'].create(
            [
                {
                    'requisition_id': cls.pr_v1.id,
                    'product_id': p.id,
                    'start_date': fields.Datetime.today(),
                    'tax_id': p.supplier_taxes_id.id,
                    'product_uom_id': p.uom_id.id,
                    'price_unit': 300 + randrange(1, 3),
                    'product_qty': 1,
                    'product_code': f'code-{p.id}',
                    'product_name': 'vendor product name',
                    'qty_multiple': 1,
                }
                for p in [cls.p1, cls.p2]
            ]
        )

    def test_import_assortment(self):
        assort_import = self.env['purchase.assortment.import'].create({'file': self.assort_file})
        assort_import.load_lines()
        for i in self.p1.product_tag_ids:
            self.assertIn(i.name, ['assort_1', 'assor_tag_3', 'assort_tag_1'])
            self.assertNotIn(i, [self.p_tag2, ])
        for i in self.p2.product_tag_ids:
            self.assertIn(i.name, ['assort_2', 'assor_tag_3', 'assort_tag_1'])
            self.assertNotIn(i, [self.p_tag1])
        self.assertEqual(len(self.p3.product_tag_ids), 0)
        for i in self.p4.product_tag_ids:
            self.assertIn(i.name, ['assort_tag_1', 'assort_tag_2', 'assor_tag_3', 'assort_tag_1'])

    def test_import_price_list(self):
        with freeze_time('2021-03-15 12:00:00'):
            price_import = self.env['purchase.requisition.import_lines'].with_context(active_id=self.pr_v1.id).create(
                {'file': self.req_lines_file})
            price_import.load_lines()
        self.assertEqual(len(self.pr_v1.line_ids), 5)

    def test_import_common_price_list(self):
        with freeze_time('2021-03-15 12:00:00'):
            price_import = self.env['purchase.requisition.import_lines.common'].create(
                {'file': self.req_lines_file_common})
            price_import.load_lines()
        self.assertEqual(len(self.pr_v1.line_ids), 5)


@tagged('lavka', 'excel_imp')
class TestImportBillLines(HttpSavepointCase):

    def create_bill_from_several_po(self, qty=2):
        po_ids = self.env['purchase.order']
        pos = self.factory.create_purchase_order(
            self.products,
            self.purchase_requisition,
            self.warehouses,
            qty
        )

        for po in pos:
            _mark = uuid4().hex[:6]
            po.state = 'purchase'
            for line in po.order_line:
                _code, _qty, _price, f_price = self.mapped_vendors_code.get(line.product_id.wms_id)
                line.mark = _mark
                line.product_init_qty = _qty
                line.product_qty = _qty

            pickings = po._create_picking_from_wms(po.order_line)
            self.env['wms_integration.order'].complete_picking(pickings[0], dt.datetime.now(), f'some_order_id_{_mark}')
            po.state = 'done'
            po.skip_check_before_invoicing = True
            po_ids += po
        res = po_ids.task_create_invoice()
        invoice_id = res['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        return invoice, po_ids

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_bill_lines.xls'), 'rb'
        ) as f:
            cls.excel_file = base64.b64encode(f.read())

        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_bill_lines_2.xls'), 'rb'
        ) as f:
            cls.excel_file_2 = base64.b64encode(f.read())

        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        _products = cls.factory.create_products(cls.warehouses, qty=6)
        cls.products = _products[:5]
        cls.extra_p = _products[5:6]
        with freeze_time(dt.datetime.now() - dt.timedelta(days=1)):
            cls.purchase_requisition = cls.factory.create_purchase_requisition(
                cls.products,
                geo_tag=cls.warehouses.mapped(
                    'warehouse_tag_ids')
            )
        wms_ids = [i.wms_id for i in cls.products]

        vendor_codes = [
            ('SA127BNV', 6, 7.7, 7.675),
            ('AZ107B19', 6, 5.90, 5.89833333333333),
            ('CF302B19', 6, 6.98, 6.98166666666667),
            ('FR306B18', 6, 11.4, 11.3983333333333),
            ('GV104B20', 6, 5.62, 5.615),
        ]

        cls.mapped_vendors_code = dict(zip(wms_ids, vendor_codes))
        tax = cls.factory.create_tax(
            ['amount', 'type_tax_use'],
            [20, 'purchase']
        )
        cls.admin_user = cls.env.ref('base.user_root')
        admins = cls.env.ref('lavka.group_admin')
        admins.users += cls.admin_user
        # поставим коды поставщиков

        for line in cls.purchase_requisition.line_ids:
            v_code, qty, price_req, price_file = cls.mapped_vendors_code.get(line.product_id.wms_id)
            line.sudo().write({
                'product_code': v_code,
                'tax_id': tax.id,
                'price_unit': price_req
            })
            line.with_user(cls.admin_user).set_approve_tax()
            line.with_user(cls.admin_user).set_approve_price()
            line.sudo()._compute_approve()

        cls.po = cls.factory.create_purchase_order(cls.products, cls.purchase_requisition, cls.warehouses, qty=1)[0]
        _mark = 'mark'
        cls.po.state = 'purchase'
        for line in cls.po.order_line:
            _code, _qty, _price, f_price = cls.mapped_vendors_code.get(line.product_id.wms_id)
            line.mark = _mark
            line.product_init_qty = _qty
            line.product_qty = _qty

        pickings = cls.po._create_picking_from_wms(cls.po.order_line)
        cls.env['wms_integration.order'].complete_picking(pickings[0], dt.datetime.now(), 'some_order_id')
        cls.po.state = 'done'
        cls.po.skip_check_before_invoicing = True
        # создаем еще одно активное соглашение
        cls.purchase_requisition_dupl = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        # поставим коды поставщиков
        for line in cls.purchase_requisition_dupl.line_ids:
            v_code, qty, price_req, price_file = cls.mapped_vendors_code.get(line.product_id.wms_id)
            line.sudo().write({
                'product_code': v_code,
                'tax_id': tax.id,
                'price_unit': price_req
            })
            line.with_user(cls.admin_user).set_approve_tax()
            line.with_user(cls.admin_user).set_approve_price()
            line.sudo()._compute_approve()

        cls.test_user = cls.env['res.users'].create([{
            'login': 'test',
            'password': 'test',
            'partner_id': cls.env['res.partner'].create([{
                'name': 'Test'
            }]).id,
            'groups_id': (4, cls.env.ref('lavka.group_accountant').id),
        }])

    def test_read_bill_lines(self):
        res = self.po.task_create_invoice()
        invoice_id = res['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        bill_lines_import = self.env['bill_lines.import'].create([{
            'file': self.excel_file,
            'account_move_id': invoice_id,
            'file_name': 'some_file.xlsx',
        }])

        bill_lines_import.load_lines()
        self.assertEqual(len(bill_lines_import.file_lines_ids.purchase_line_ids), len(self.po.order_line))
        bill_lines_import.compute_lines_count()
        bill_lines_import.update_lines()

        tax_sum_file = sum(bill_lines_import.file_lines_ids.mapped('vat_sum'))
        untaxed_sum_files = sum(bill_lines_import.file_lines_ids.mapped('sum_no_vat'))
        tax_sum_doc = sum(invoice.invoice_line_ids.mapped('wo_vat_sum'))
        untaxed_sum_doc = sum(invoice.invoice_line_ids.mapped('amount_currency'))

        self.assertEqual(tax_sum_file, tax_sum_doc)
        self.assertEqual(untaxed_sum_files, untaxed_sum_doc)

    def test_multiple_po(self):
        invoice, po_ids = self.create_bill_from_several_po()
        bill_lines_import = self.env['bill_lines.import'].create([{
            'file': self.excel_file_2,
            'account_move_id': invoice.id,
            'file_name': 'some_file.xlsx',
        }])

        bill_lines_import.load_lines()
        # в одной строке кол-во только на 1 строк заказа
        self.assertEqual(len(bill_lines_import.file_lines_ids.purchase_line_ids), len(po_ids.mapped('order_line'))-1)
        bill_lines_import.compute_lines_count()
        bill_lines_import.update_lines()

        tax_sum_file = sum(bill_lines_import.file_lines_ids.mapped('vat_sum'))
        untaxed_sum_files = sum(bill_lines_import.file_lines_ids.mapped('sum_no_vat'))
        tax_sum_doc = sum(invoice.invoice_line_ids.mapped('wo_vat_sum'))
        untaxed_sum_doc = sum(invoice.invoice_line_ids.mapped('amount_currency'))

        self.assertEqual(tax_sum_file, tax_sum_doc)
        self.assertEqual(untaxed_sum_files, untaxed_sum_doc)

    def test_read_bill_lines_duplicate_vendor_code(self):
        # добавим левый товар, но с тем же vendor_code
        dupl_product = self.extra_p[0]
        example_vcode = self.purchase_requisition.line_ids[0].product_code
        line = self.env['purchase.requisition.line'].create(
            {
                'product_id': dupl_product.id,
                'price_unit': random.randrange(1, 100),
                'product_uom_id': dupl_product.uom_id.id,
                'requisition_id': self.purchase_requisition.id,
                'start_date': dt.datetime.now(),
                'tax_id': dupl_product.supplier_taxes_id.id,
                'approve_tax': True,
                'approve_price': True,
                'product_code': example_vcode,
                'product_name': f'{dupl_product.name}_vendor',
                'qty_multiple': 1,
            },
        )
        line.with_user(self.admin_user).set_approve_tax()
        line.with_user(self.admin_user).set_approve_price()
        line.sudo()._compute_approve()

        res = self.po.task_create_invoice()
        invoice_id = res['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        bill_lines_import = self.env['bill_lines.import'].create([{
            'file': self.excel_file,
            'account_move_id': invoice_id,
            'file_name': 'some_file.xlsx',
        }])

        bill_lines_import.load_lines()
        self.assertEqual(len(bill_lines_import.file_lines_ids.purchase_line_ids), len(self.po.order_line))
        bill_lines_import.compute_lines_count()
        bill_lines_import.update_lines()

        tax_sum_file = sum(bill_lines_import.file_lines_ids.mapped('vat_sum'))
        untaxed_sum_files = sum(bill_lines_import.file_lines_ids.mapped('sum_no_vat'))
        tax_sum_doc = sum(invoice.invoice_line_ids.mapped('wo_vat_sum'))
        untaxed_sum_doc = sum(invoice.invoice_line_ids.mapped('amount_currency'))

        self.assertEqual(tax_sum_file, tax_sum_doc)
        self.assertEqual(untaxed_sum_files, untaxed_sum_doc)

    def test_duplicate_vendor_code_two_req(self):
        po2 = self.factory.create_purchase_order(self.products, self.purchase_requisition_dupl, self.warehouses, qty=1)[0]
        _mark = 'mark2'
        po2.state = 'purchase'
        for line in po2.order_line:
            _code, _qty, _price, f_price = self.mapped_vendors_code.get(line.product_id.wms_id)
            line.mark = _mark
            line.product_init_qty = _qty
            line.product_qty = _qty

        pickings = po2._create_picking_from_wms(po2.order_line)
        self.env['wms_integration.order'].complete_picking(pickings[0], dt.datetime.now(), 'some_order_id')
        po2.state = 'done'
        po2.skip_check_before_invoicing = True
        po_ids = self.env['purchase.order']
        po_ids += self.po
        po_ids += po2

        res = po_ids.task_create_invoice()
        invoice_id = res['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        bill_lines_import = self.env['bill_lines.import'].create([{
            'file': self.excel_file_2,
            'file_name': 'some_file.xlsx',
            'account_move_id': invoice_id,
        }])

        bill_lines_import.load_lines()
        # в одной строке кол-во только на 1 строк заказа
        self.assertEqual(len(bill_lines_import.file_lines_ids.purchase_line_ids), len(po_ids.mapped('order_line')) - 1)
        bill_lines_import.compute_lines_count()
        bill_lines_import.update_lines()

        tax_sum_file = sum(bill_lines_import.file_lines_ids.mapped('vat_sum'))
        untaxed_sum_files = sum(bill_lines_import.file_lines_ids.mapped('sum_no_vat'))
        tax_sum_doc = sum(invoice.invoice_line_ids.mapped('wo_vat_sum'))
        untaxed_sum_doc = sum(invoice.invoice_line_ids.mapped('amount_currency'))

        self.assertEqual(tax_sum_file, tax_sum_doc)
        self.assertEqual(untaxed_sum_files, untaxed_sum_doc)

    def test_export_lines_to_excel(self):
        invoice, po_ids = self.create_bill_from_several_po()
        bill_lines_import = self.env['bill_lines.import'].create([{
            'file': self.excel_file_2,
            'account_move_id': invoice.id,
        }])

        session = self.authenticate('test', 'test')
        response = self.url_open(
            '/web/download/bill_lines?req_id=%s' % invoice.id,
            headers={'session_id': session['session_token']},
        )
        self.assertEqual(response.status_code, 200)
        xlsx_file = BytesIO(response.content)
        wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)
        sheet = wb_obj.active
        # проверка, что заголовки создались корректно
        file_headers = bill_lines_import.check_columns_template(sheet[1])
        products = po_ids.order_line.mapped('product_id')
        # кол-во строк долдно быть равно ко-ву товаров
        rows = list(sheet.iter_rows(min_row=2))
        self.assertEqual(len(rows), len(products))


