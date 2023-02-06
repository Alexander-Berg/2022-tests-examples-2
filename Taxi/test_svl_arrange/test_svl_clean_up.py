import datetime
import logging

from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged('lavka', 'svl_clean_up')
class TestSVLCleanUp(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=1)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )

        cls.p_orders = cls.factory.create_purchase_order(cls.products, cls.purchase_requisition, cls.warehouses, qty=1)
        for po in cls.p_orders:
            po.write({
                'date_planned': datetime.datetime.today(),
                'skip_check_before_invoicing': True,
            })
            cls.factory.confirm_po(po)

    def test_svl_clean_up_and_recalculate(self):
        moves = self.env['stock.move'].search([])
        _logger.info(f'order price - {moves[0].purchase_line_id.price_unit}')
        _logger.info(f'move price - {moves[0].price_unit}')
        self.assertEqual(len(moves), len(self.products) * len(self.p_orders))
        quants = self.env['stock.quant'].search([])
        self.assertEqual(len(quants), len(self.products))
        pickings = self.env['stock.picking'].search([])
        self.assertEqual(len(self.p_orders), len(pickings))

        svls_before = self.env['stock.valuation.layer'].search([])
        sum_before = sum(svls_before.mapped('remaining_value'))
        qty_before = sum(svls_before.mapped('remaining_qty'))

        svl_arr = self.env['svl.arranging']

        svl_arr.svl_truncate()
        svls = self.env['stock.valuation.layer'].search([])
        self.assertFalse(svls)

        svl_arr.recalculate_svl(test=True)
        svls_after = self.env['stock.valuation.layer'].search([])
        self.assertTrue(len(svls_after) > 0)
        moves_after = self.env['stock.move'].search([])
        _logger.info(f'order price after- {moves_after[0].purchase_line_id.price_unit}')
        _logger.info(f'move price after- {moves_after[0].price_unit}')
        sum_after = sum(svls_after.mapped('remaining_value'))
        qty_after = sum(svls_after.mapped('remaining_qty'))

        self.assertEqual(sum_before, sum_after)
        self.assertEqual(qty_before, qty_after)
