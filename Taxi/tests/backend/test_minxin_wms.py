import logging
from odoo.tests.common import SavepointCase, tagged, Form


_logger = logging.getLogger(__name__)

@tagged('lavka', 'link')
class TestWmsMixin(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # new
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=6)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.product = cls.products[0]
        cls.wh = cls.warehouses[0]
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.po = cls.factory.create_purchase_order(
            cls.products,
            cls.purchase_requisition,
            cls.warehouses,
            qty=1
        )[0]
        cls.acc = cls.factory.create_acceptance_list(cls.po, cls.warehouses)[0]

    def test_form_has_urls(self):

        self.acc._compute_request_type()
        self.env['wms_integration.order'].post_processing(self.acc, 'TEST', test=True)
        stw_data_set = self.factory.get_sale_stowages_data_from_acceptance(self.acc)
        j = 1
        all_logs = []
        for stw_data, stw_log in stw_data_set:
            all_logs += stw_log
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc,
                count=j
            )
            j += 1
            wms_doc.post_processing(wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(all_logs)

        po = self.env['purchase.order'].search([])
        po._compute_picking()
        po.skip_check_before_invoicing = True
        po_form = Form(po)
        product_form = Form(self.product)
        wh_form = Form(self.warehouses[0])
        picking = po.picking_ids[0]
        picking_form = Form(picking)
        move = picking.move_lines[0]
        move_form = Form(move)
        for f in [wh_form, product_form, po_form, picking_form, move_form]:
            self.assertIsNotNone(po_form._view['fields'].get('wms_url'))



