import logging
from odoo.tests.common import SavepointCase, tagged

_logger = logging.getLogger(__name__)


FIXTURES_PATH = 'checks_test'


@tagged('lavka', 'rev')
class TestReverseMove(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # new
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=1)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.product = cls.products[0]
        cls.wh = cls.warehouses[0]
        cls.env['ir.config_parameter'].set_param('sleep', 'false')

    def test_reverse_move_for_stock_move(self):

        delta_count = 15
        check_data, check_log = self.factory.get_get_checks_and_stock_log(self.wh, self.product, delta_count)
        wms_doc = self.env['wms_integration.order'].create(check_data)
        wms_doc._compute_request_type()
        self.assertEqual(wms_doc.request_type, 'ordinary')

        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(check_log)
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}

        # процессим
        moves_before = self.env['stock.move'].search([])

        # откатываем движения и стираем wms_id
        storno_moves = self.env['stock.move.line'].reverse_move(model_name='stock.move',
                                                       wms_id=wms_doc.order_id,
                                                       wipe_wms_id=True)

        # проверяем что движений нет
        for move in moves_before:
            self.assertEqual(move.state, 'storned')
        for move in storno_moves:
            self.assertEqual(move.state, 'done')

        # проверим что остаток нулевой
        for product in self.products:
            q = self.env['stock.quant'].search(
                [
                    ('product_id', '=', product.id),
                    ('location_id', '=', self.wh.lot_stock_id.id)
                ]
            ).quantity
            self.assertEqual(q, 0)
        _moves = self.env['stock.move']
        for m in _moves:
            self.assertFalse(m.log_id)
