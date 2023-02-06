import base64
import logging
from datetime import datetime
from io import BytesIO

import openpyxl
from odoo.exceptions import UserError
from odoo.modules import get_resource_path
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
from random import randrange

from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def create_or_load_xls(filename):
    with file_open(filename, 'rb') as f:
        excel_file = base64.b64encode(f.read())
        return excel_file


@tagged('lavka', 'in_b')
class TestInputBalance(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.res = cls.factory.create_purchase_requisition(cls.products, cls.warehouses.warehouse_tag_ids)
        cls.ordinary_user = cls.env['res.users'].create([{
            'name': 'John Doe',
            'login': 'john_doe',
            'password': 'pass',
        }])
        cls.auth_user = cls.env['res.users'].create([{
            'name': 'John Doe 2',
            'login': 'john_doe 2',
            'password': 'pass2',
        }])

        cls.auth_user_final = cls.env['res.users'].create([{
            'name': 'John Doe 3',
            'login': 'john_doe 3',
            'password': 'pass3',
        }])

        cls.env.ref('lavka.group_approve_input_balance').users += cls.auth_user
        cls.env.ref('lavka.group_final_approve_input_balance').users += cls.auth_user_final
        cls.env.ref('lavka.group_admin').users += cls.auth_user
        cls.env.ref('lavka.group_admin').users += cls.auth_user_final

        cls.filename = get_resource_path('lavka', 'tests/backend/test_input_balance/test_openpyxl.xlsx.test')
        cls.import_file = create_or_load_xls(cls.filename)
        decoded = base64.b64decode(cls.import_file)
        xlsx_file = BytesIO(decoded)
        wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)
        sheet = wb_obj.active
        for i in range(2, 5):
            addr = f'A{i}'
            sheet[addr] = cls.products[i].default_code
        wb_obj.save(filename=cls.filename)

    def test_create_input_balance(self):
        doc = self.env['input.balance'].create([{
            'warehouse': self.warehouses[0].id,
            'date_input': datetime.now(),
        }])
        in_lines = []
        for prd in self.products:
            qty = randrange(1, 200)
            price = randrange(1, 100) / 100
            t_sum = price * qty
            in_lines.append({
                'input_balance_id': doc.id,
                'product_id': prd.id,
                'qty': qty,
                'invoice_quantity': qty - randrange(197, 200),
                'unit_price': price,
                'row_total_sum': t_sum,

            })
        self.env['input.balance.line'].create(in_lines)
        self.assertTrue(doc.name)
        self.assertTrue(doc.state == 'draft')
        self.assertTrue(doc.company_id)

        with self.assertRaises(UserError):
            doc.with_user(self.ordinary_user).button_approve()

        with self.assertRaises(UserError):
            doc.button_done()

        doc.with_user(self.auth_user).button_approve()
        self.assertEqual(doc.state, 'approving')
        doc.with_user(self.auth_user_final).button_final_approve()
        self.assertEqual(doc.state, 'approving_final')

        doc.with_user(self.auth_user).button_done()
        quants = {i.product_id: i for i in self.env['stock.quant'].search([
            ('location_id', '=', doc.warehouse.lot_stock_id.id)
        ])}
        self.assertEqual(doc.state, 'done')
        total_svl_sum = sum(doc.input_lines.moves.mapped('stock_valuation_layer_ids.remaining_value'))
        total_svl_qty = sum(doc.input_lines.moves.mapped('stock_valuation_layer_ids.remaining_qty'))
        self.assertEqual(round(total_svl_sum, 2), round(doc.total_sum, 2))
        self.assertEqual(round(total_svl_qty, 3), round(doc.total_qty, 3))
        for line in doc.input_lines:
            self.assertTrue(line.moves)
            mv = line.moves
            svl = mv.stock_valuation_layer_ids
            stock_qty = quants[line.product_id]
            self.assertEqual(line.unit_price, mv.price_unit)
            self.assertEqual(round(svl.unit_cost, 2), mv.price_unit)
            self.assertEqual(round(svl.value, 3), round(line.row_total_sum, 3))
            self.assertEqual(line.qty, stock_qty.quantity)

        with self.assertRaises(UserError):
            doc.unlink()

        with self.assertRaises(UserError):
            doc.input_lines.unlink()

        with self.assertRaises(UserError):
            doc.button_approve()

    def test_import_input_balance(self):

        input_balance = self.env['input.balance'].create([{
            'warehouse': self.warehouses[0].id,
            'date_input': datetime.now(),
        }])
        xls = create_or_load_xls(self.filename)
        bi_lines_import = self.env['input_balance_lines.import'].create([{
            'file': xls,
            'input_balance_id': input_balance,
        }])
        bi_lines_import.load_lines()
        bi_lines_import.update_lines()

        doc_lines = input_balance.input_lines
        self.assertEqual(len(doc_lines), 3)
