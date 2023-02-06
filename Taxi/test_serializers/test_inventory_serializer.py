import logging
from unittest.mock import patch
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged


_logger = logging.getLogger(__name__)


@tagged('lavka', 'serializers', 's_inventory')
class TestInventorySerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls._products = cls.factory.create_products(cls.warehouses, qty=13)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls._products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.products = cls._products[:10]
        cls.extra_products = cls._products[10:11]
        cls.wh = cls.warehouses[0]
        cls.po = cls.factory.create_purchase_order(
            cls.products,
            cls.purchase_requisition,
            cls.warehouses, qty=3
        )
        cls.acc = cls.factory.create_acceptance_list(cls.po, cls.warehouses)
        all_logs = []
        for _acc in cls.acc:
            _acc.post_processing(_acc, 'TEST', test=True)
            stw_data_set = cls.factory.get_sale_stowages_data_from_acceptance(_acc)
            j = 1
            wms_docs = []
            for stw_data, stw_log in stw_data_set:
                wms_doc = cls.factory._create_stowage(
                    vals=stw_data,
                    parent=_acc,
                    count=j
                )
                j += 1
                all_logs += stw_log
                wms_doc.post_processing(wms_doc, 'TEST', test=True)
                wms_docs.append((wms_doc, stw_log))
        cls.factory.process_stock_logs(all_logs)

    def base_process_inventory(self):
        """
        """
        self.env['ir.config_parameter'].set_param('check_qty_in_inventory', 'false')
        stocks = {
            i.product_id: i.quantity for i
            in self.env['stock.quant'].search([])
            if i.location_id == self.wh.lot_stock_id
        }
        inv_data, snapshot_plan, snapshot_fact, checks_data = self.factory.get_inv_and_snapshots(
            self.wh,
            self.extra_products,
            stocks=stocks
        )
        # проверяем что в плановом снапшоте нет экстра продуктов
        self.assertEqual(len(snapshot_plan), 2*len(stocks))
        self.assertEqual(len(snapshot_fact), 2*(len(stocks)+len(self.extra_products)))

        # сначала ровняем остатки
        inv_data.update({
            'status': 'processing',
        })
        wms_doc = self.env['wms_integration.order'].create(inv_data)
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = snapshot_plan, None
            wms_doc.post_processing(wms_doc, 'TEST')
        inv = self.env['stock.inventory'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertIsNotNone(inv)
        self.assertEqual(inv.state, 'confirm')
        self.assertEqual(len(inv.line_ids), len(stocks))
        arranged_stocks = {
            i.product_id: i.quantity for i
            in self.env['stock.quant'].search([])
            if i.location_id == self.wh.lot_stock_id
        }
        for line in inv.line_ids:
            wms_qty = line.wms_qty
            stock_qty_before = stocks.get(line.product_id, 0)
            stock_qty = arranged_stocks.get(line.product_id, 0)
            # плановые остатки из вмс +5 обычная полка
            # и +2000 с квантом 1000 (+2)
            self.assertEqual(stock_qty_before + 7, stock_qty)
            # остатки должны быть равны WMS
            self.assertEqual(wms_qty, stock_qty)
            c = 1
        # обрабатываем чексы
        all_logs = []
        for check_data, cp_log_data in checks_data:
            all_logs += cp_log_data
            ch_wms_doc = self.env['wms_integration.order'].create(check_data)
            ch_wms_doc.post_processing(ch_wms_doc, 'TEST', test=True)
        self.factory.process_stock_logs(all_logs)
        с = 1
        # потом завершаем инву
        wms_doc.status = 'complete'
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = snapshot_fact, None
            wms_doc.post_processing(wms_doc, 'TEST')
        inv_stocks = {
            i.product_id: i.quantity for i
            in self.env['stock.quant'].search([])
            if i.location_id == self.wh.lot_stock_id
        }
        self.assertEqual(inv.state, 'done')
        for line in inv.line_ids:
            fact_qty = round(line.product_qty, 2)
            stock_qty = round(inv_stocks.get(line.product_id, 0), 2)
            self.assertEqual(fact_qty, stock_qty)
        c = 1

    def test_inventory_happy(self):
        self.env['ir.config_parameter'].set_param('check_qty_in_inventory', 'false')
        self.base_process_inventory()

    def test_inventory_check_snapshot_after(self):
        """
         Делаем инву и потом проверяем с фактом из снапшота
        """
        self.env['ir.config_parameter'].set_param('check_qty_in_inventory', 'true')
        self.base_process_inventory()





