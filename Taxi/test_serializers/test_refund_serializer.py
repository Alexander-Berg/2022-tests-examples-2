import logging
from unittest.mock import patch
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged('lavka', 'serializers', 's_refund')
class TestRefundfSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls._products = cls.factory.create_products(cls.warehouses, qty=10)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls._products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.products = cls._products[:5]
        cls.ingr = cls._products[5:8]
        cls.samples = cls._products[8:10]
        cls.wh = cls.warehouses[0]
        cls.receipt = {
            'product': cls.products[0],
            'components': [
                [{
                    "count": 120,
                    "quants": 2000,
                    "portions": 1,
                    "product_id": cls.ingr[0].wms_id
                }],
                [{
                    "count": 1,
                    "quants": 1,
                    "portions": 1,
                    "product_id": cls.ingr[1].wms_id
                }],
                [{
                    "count": 977,
                    "quants": 1500,
                    "portions": 1,
                    "product_id": cls.ingr[2].wms_id
                }]
            ]
        }

    def test_refund(self):
        """
        """
        order_data, order_log = self.factory.get_order_and_stock_log(
            self.wh,
            self.products,
            self.receipt,
            self.samples,
        )
        wms_doc = self.env['wms_integration.order'].create(order_data)
        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        # забираем стоклог не по ручке, а из таблички
        self.env['ir.config_parameter'].set_param('stress_testing', 'true')
        self.factory.process_stock_logs(order_log)
        self.factory.unlink_stess_test_param()
        so = self.env['wms_order_serializer'].get_or_create_sale_order(wms_doc)
        excluded = []
        excluded.append(self.receipt['product'])
        refund_data, refund_log = self.factory.get_refund_and_stock_log(
            self.wh,
            so,
            excluded
        )
        refund_doc = self.env['wms_integration.order'].create(refund_data)
        refund_doc.post_processing(refund_doc, 'TEST', test=True)
        self.factory.process_stock_logs(refund_log)

        r_picking = self.env['stock.picking'].search([
            ('wms_id', '=', refund_doc.order_id)
        ])
        self.assertTrue(r_picking)

        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}

        oper_loc = so.warehouse_id.lot_stock_id
        produced = [i for i in self.receipt['product']]
        # проверяем что в ноль схлопнулся
        for r_line in r_picking.move_lines:
            self.assertEqual(r_line.state, 'done')
            self.assertTrue(r_line.quantity_done > 0)
            product = r_line.product_id
            qty_on_stock = stocks.get(
                (r_line.product_id, oper_loc), 0
            )
            if product in produced:
                self.assertEqual(qty_on_stock, 0)
            else:
                self.assertEqual(qty_on_stock, 0)
        components = [i for i in self.receipt['components']]
        ingr = {i.wms_id: i for i in self.ingr}
        for r in components:
            wms_id = r[0]['product_id']
            prd = ingr[wms_id]
            qty = stocks.get(
                (prd, oper_loc), 0
            )
            self.assertEqual(round(-qty, 2), round(r[0]['count'] / r[0]['quants'], 2))
        c = 1

