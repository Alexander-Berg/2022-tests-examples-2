import logging
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
_logger = logging.getLogger(__name__)

@tagged('lavka', 'serializers', 's_ship')
class TestShipmentSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.wh_in, cls.wh_out = cls.factory.create_warehouses(qty=2)
        cls.products = cls.factory.create_products(cls.wh_out, qty=8)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.wh_out.mapped(
                'warehouse_tag_ids')
        )
        cls.transfer = cls.factory.create_transfer(cls.products, cls.wh_in, cls.wh_out)

    def test_shipment_postprocessing(self):
        sh, sh_log = self.factory.get_shipment_and_stock_log(self.transfer)
        cls_wms_order = self.env['wms_integration.order']
        wms_doc = cls_wms_order.create(sh)
        self.transfer.shipment_id = wms_doc.order_id
        cls_wms_order.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(sh_log)

        self.assertEqual(self.transfer.state, 'in_transfer')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        transfer = self.env['transfer.lavka'].browse(self.transfer.id)
        moves = transfer.transfer_lines.mapped('moves')
        self.assertEqual(len(moves), len(sh_log))
        loc = transfer.warehouse_in.wh_stock_git
        for move in moves:
            qty = stocks.get((move.product_id, loc), 0)
            self.assertEqual(qty, move.quantity_done)

        for line in transfer.transfer_lines:
            self.assertTrue(line.qty_in_transfer > 0)

    def test_shipment_postprocessing_no_log(self):
        sh, sh_log = self.factory.get_shipment_and_stock_log(self.transfer)
        cls_wms_order = self.env['wms_integration.order']
        wms_doc = cls_wms_order.create(sh)
        self.transfer.shipment_id = wms_doc.order_id
        cls_wms_order.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs([])
        transfer = self.env['transfer.lavka'].browse(self.transfer.id)
        moves = transfer.transfer_lines.mapped('moves')
        self.assertFalse(moves)

    def test_acceptance_processing(self):
        # отгружаем
        sh, sh_log = self.factory.get_shipment_and_stock_log(self.transfer)
        cls_wms_order = self.env['wms_integration.order']
        wms_doc = cls_wms_order.create(sh)
        self.transfer.shipment_id = wms_doc.order_id
        cls_wms_order.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(sh_log)

        transfer = self.env['transfer.lavka'].browse(self.transfer.id)
        acc, stw, stw_log = self.factory.get_acc_stw_and_stock_log_of_transfer(transfer)
        acc_doc = cls_wms_order.create(acc)
        self.transfer.acceptance_id = acc_doc.order_id
        cls_wms_order.post_processing(acc_doc, 'TEST', test=True)
        stw_doc = cls_wms_order.create(stw)
        cls_wms_order.post_processing(stw_doc, 'TEST', test=True)
        self.factory.process_stock_logs(stw_log)
        c=1


@tagged('lavka', 'serializers', 'roll_back')
class TestShipmentSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.wh_in, cls.wh_out = cls.factory.create_warehouses(qty=2)
        cls.products = cls.factory.create_products(cls.wh_out, qty=8)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.wh_out.mapped(
                'warehouse_tag_ids')
        )
        cls.transfer = cls.factory.create_transfer(cls.products[:6], cls.wh_in, cls.wh_out)

    def test_shipment_postprocessing(self):
        sh, sh_log = self.factory.get_shipment_and_stock_log(self.transfer)
        cls_wms_order = self.env['wms_integration.order']
        wms_doc = cls_wms_order.create(sh)
        self.transfer.shipment_id = wms_doc.order_id
        cls_wms_order.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(sh_log)

        self.assertEqual(self.transfer.state, 'in_transfer')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        transfer = self.env['transfer.lavka'].browse(self.transfer.id)
        moves = transfer.transfer_lines.mapped('moves')
        self.assertEqual(len(moves), len(sh_log))
        loc = transfer.warehouse_in.wh_stock_git
        for move in moves:
            qty = stocks.get((move.product_id, loc), 0)
            self.assertEqual(qty, move.quantity_done)

        for line in transfer.transfer_lines:
            self.assertTrue(line.qty_in_transfer > 0)

        rollback, rb_log = self.factory.get_rollback_and_log(sh, sh_log, self.products[6:8])
        wms_doc_rb = cls_wms_order.create(rollback)
        cls_wms_order.post_processing(wms_doc_rb, 'TEST', test=True)
        self.factory.process_stock_logs(rb_log)
        pick = self.env['stock.picking'].search([
            ('wms_id', '=', wms_doc_rb.order_id)
        ])
        self.assertTrue(pick)
        moves = pick.move_lines
        self.assertEqual(len(moves), 4)
        self.assertEqual(len(transfer.transfer_lines), len(self.products))
        for move in moves:
            self.assertEqual(move.quantity_done, 2)
            self.assertEqual(move.state, 'done')
            self.assertEqual(move.location_dest_id, transfer.warehouse_out.lot_stock_id)
            self.assertEqual(move.location_id, transfer.warehouse_out.wh_stock_git)

        c=1






