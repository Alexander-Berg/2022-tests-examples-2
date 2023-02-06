import logging
from unittest.mock import patch
from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged

from common.config import cfg

_logger = logging.getLogger(__name__)


@tagged('lavka', 'serializers', 's_orders')
class TestOrderfSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls._products = cls.factory.create_products(cls.warehouses, qty=11)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls._products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.products = cls._products[:5]
        cls.ingr = cls._products[5:9]
        cls.samples = cls._products[9:11]
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
                },
                    {
                        "count": 977,
                        "quants": 1500,
                        "portions": 1,
                        "product_id": cls.ingr[3].wms_id
                    }]
            ]
        }

    def test_full_house_order(self):
        """
        """
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        order_data, order_log = self.factory.get_order_and_stock_log(
            self.wh,
            self.products,
            self.receipt,
            self.samples,
        )
        # создаем документ
        wms_doc = self.env['wms_integration.order'].create(order_data)
        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        # забираем стоклог не по ручке, а из таблички
        self.env['ir.config_parameter'].set_param('stress_testing', 'true')
        self.factory.process_stock_logs(order_log)
        self.factory.unlink_stess_test_param()
        so = self.env['sale.order'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(so.state, 'done')
        self.env['ir.config_parameter'].set_param('stress_testing', 'true')


        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        oper_loc = so.warehouse_id.lot_stock_id
        produced = [i for i in self.receipt['product']]
        for order_line in so.order_line:
            product = order_line.product_id
            qty_on_stock = stocks.get(
                (order_line.product_id, oper_loc), 0
            )
            if product in produced:
                self.assertEqual(qty_on_stock, 0)
            else:
                self.assertEqual(-qty_on_stock, order_line.qty_delivered)

        for samp in self.samples:
            qty_on_stock = stocks.get(
                (samp, oper_loc), 0
            )
            self.assertTrue(qty_on_stock < 0)
        components = [i for i in self.receipt['components']]
        ingr = {i.wms_id: i for i in self.ingr}
        for r_list in components:
            for r in r_list:
                wms_id = r['product_id']
                prd = ingr[wms_id]
                qty = stocks.get(
                    (prd, oper_loc), 0
                )
                self.assertEqual(round(-qty, 2), round(r['count']/r['quants'],2))

    def test_full_house_order_no_svl(self):
        """
        """
        stocks_before = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        order_data, order_log = self.factory.get_order_and_stock_log(
            self.wh,
            self.products,
            self.receipt,
            self.samples,
        )
        # убираем svl
        self.env['ir.config_parameter'].set_param(key='svl.disabled', value='True')
        # создаем документ
        wms_doc = self.env['wms_integration.order'].create(order_data)
        wms_doc.post_processing(wms_doc, 'TEST', test=True)
        # забираем стоклог не по ручке, а из таблички
        self.env['ir.config_parameter'].set_param('stress_testing', 'true')
        self.factory.process_stock_logs(order_log)
        self.factory.unlink_stess_test_param()

        _param = self.env['ir.config_parameter'].search([
            ('key', '=', 'svl.disabled')
        ])
        if _param:
            _param.unlink()

        so = self.env['sale.order'].search([
            ('wms_id', '=', wms_doc.order_id)
        ])
        self.assertEqual(so.state, 'done')
        self.env['ir.config_parameter'].set_param('stress_testing', 'true')


        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        oper_loc = so.warehouse_id.lot_stock_id
        produced = [i for i in self.receipt['product']]
        for order_line in so.order_line:
            product = order_line.product_id
            qty_on_stock = stocks.get(
                (order_line.product_id, oper_loc), 0
            )
            if product in produced:
                self.assertEqual(qty_on_stock, 0)
            else:
                self.assertEqual(-qty_on_stock, order_line.qty_delivered)

        for samp in self.samples:
            qty_on_stock = stocks.get(
                (samp, oper_loc), 0
            )
            self.assertTrue(qty_on_stock < 0)
        components = [i for i in self.receipt['components']]
        ingr = {i.wms_id: i for i in self.ingr}
        for r_list in components:
            for r in r_list:
                wms_id = r['product_id']
                prd = ingr[wms_id]
                qty = stocks.get(
                    (prd, oper_loc), 0
                )
                self.assertEqual(round(-qty, 2), round(r['count']/r['quants'],2))

    def test_canceled_no_log_order(self):
        """
        """
        order_data, order_log = self.factory.get_order_and_stock_log(
            self.wh,
            self.products,
            self.receipt,
            self.samples,
        )
        order_data.update({
            'status': 'canceled',
        })
        wms_doc = self.env['wms_integration.order'].create(order_data)
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = [], None
            wms_doc.post_processing(wms_doc, 'TEST')

