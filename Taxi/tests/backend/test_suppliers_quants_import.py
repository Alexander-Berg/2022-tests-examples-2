from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged('lavka', 'autoorder', 'autoorder_imports', 'suppliers_quants_import')
class TestSafetyStockImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 1',
            }
        )

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 2',
            }
        )

        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-1',
                'code': '1',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-2',
                'code': '2',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag2.id],
            }
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-1',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-2',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'p-1',
                'default_code': '1',
                'wms_id': '1',
            }
        )

        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'p-2',
                'default_code': '2',
                'wms_id': '2',
            }
        )

        cls.pr1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.pr2 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v2.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag2.id],
            }
        )

        products_lines_data = (
            (cls.pr1, cls.p1, 100, 1, 1, True, True, True, True,),
            (cls.pr2, cls.p2, 200, 2, 2, True, True, True, True,),
        )

        cls.env['purchase.requisition.line'].create(
            [
                {
                    'requisition_id': pr.id,
                    'product_id': p.id,
                    'start_date': fields.Datetime.today(),
                    'tax_id': p.supplier_taxes_id.id,
                    'product_uom_id': p.uom_id.id,
                    'price_unit': price,
                    'product_qty': qty,
                    'product_code': f'code-{p.id}',
                    'product_name': 'vendor product name',
                    'qty_multiple': qty_multiple,
                    'approve_price': approve_price,
                    'approve_tax': approve_tax,
                    'approve': approve,
                    'active': active,
                }
                for (pr, p, price, qty, qty_multiple,
                     approve_price, approve_tax, approve, active)
                in products_lines_data
            ]
        )

    def test_suppliers_quants_import(self):
        sqi = self.env['autoorder.supplier.quant.import']
        serialized_data = [
            {
                'default_code': self.p1.id,
                'vendor_external_id': self.v1.id,
                'warehouse_tag_id': self.wh_tag1.id,
                'qty_multiple': 5
            },
            {
                'default_code': self.p1.id,
                'vendor_external_id': self.v2.id,
                'warehouse_tag_id': self.wh_tag1.id,
                'qty_multiple': 6
            },
            {
                'default_code': self.p2.id,
                'vendor_external_id': self.v2.id,
                'warehouse_tag_id': self.wh_tag2.id,
                'qty_multiple': 7
            }
        ]

        items, errors = sqi.post_process(serialized_data)
        sqi.save(items)

        self.assertEqual(len(errors), 1)

        prl1 = self.env['purchase.requisition.line'].search([
            ('requisition_id', '=', self.pr1.id),
            ('product_id', '=', self.p1.id),
        ])

        self.assertEqual(prl1.qty_multiple, 5)

        prl2 = self.env['purchase.requisition.line'].search([
            ('requisition_id', '=', self.pr2.id),
            ('product_id', '=', self.p2.id),
        ])

        self.assertEqual(prl2.qty_multiple, 7)
