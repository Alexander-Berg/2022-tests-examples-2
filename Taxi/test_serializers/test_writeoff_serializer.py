import logging
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged('lavka', 'serializers', 's_writeoff')
class TestWriteoffSerializer(SavepointCase):
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
        cls.products = cls._products

    def test_writeoff(self):
        """
        """
        order_data, wrt_log = self.factory.get_writeoff_and_stock_log(
            self.warehouses[0],
            self.products,
        )
        wms_doc = self.env['wms_integration.order'].create(order_data)
        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(wrt_log)

        w_picking = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertTrue(w_picking)
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}

        oper_loc = w_picking.warehouse_id.lot_stock_id
        for r in w_picking.move_lines:
            self.assertEqual(r.state, 'done')
            self.assertTrue(r.quantity_done > 0)
            qty_on_stock = stocks.get(
                (r.product_id, oper_loc), 0
            )
            self.assertEqual(round(-qty_on_stock, 2), round(r.quantity_done, 2))
            self.assertTrue(r.scrap_reason)
        c = 1
