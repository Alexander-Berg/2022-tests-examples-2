import logging
from odoo.tests.common import SavepointCase, tagged

_logger = logging.getLogger(__name__)


@tagged('lavka', 'bananas')
class TestBananasStowage(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBananasStowage, cls).setUpClass()
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.parents_p, cls.children_p = cls.factory.create_products_with_parents(cls.warehouses, qty=10, parent_qty=4)

        cls.parents_ids = [i.wms_id for i in cls.parents_p]
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.parents_p,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.po = cls.factory.create_purchase_order(cls.parents_p, cls.purchase_requisition, cls.warehouses)[0]
        cls.acc = cls.factory.create_acceptance_list(cls.po, cls.warehouses)[0]
        cls.stw_data_set = cls.factory.get_sale_stowages_data_with_children(cls.acc, cls.parents_p, cls.children_p)

    def test_banana_stowage(self):

        self.env['wms_integration.order'].post_processing(self.acc, 'TEST', test=True)
        all_logs = []
        j = 1
        for stw_data, stw_log in self.stw_data_set:
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc,
                count=j
            )
            j += 1
            self.env['wms_integration.order'].post_processing(wms_doc, 'TEST', test=True)
            all_logs += stw_log
        self.factory.process_stock_logs(all_logs)


        extra_po_lines = [i for i in self.po.order_line if i.product_id in self.children_p]
        for line in extra_po_lines:
            self.assertTrue(line.parent_line_id.id > 0)
            _logger.debug(
                f'=============== > Parent {line.parent_line_id.product_id.name} - {line.parent_line_id.product_qty} '
                f'converted to {line.product_id.name} - {line.qty_received}')

        # создаем invoice для каждой order_line из extra_po_lines
        self.po.skip_check_before_invoicing = True
        invoice_id = self.po.action_create_invoice().get("res_id")
        invoice = self.env["account.move"].browse(invoice_id)
        # строчки инвойса содержат бананы-потомки:
        for line in invoice.invoice_line_ids:
            self.assertTrue(line.purchase_line_id.product_id in self.children_p)
