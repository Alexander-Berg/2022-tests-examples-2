import logging
import os
import json
from unittest.mock import patch
from common.client.wms import WMSConnector
from odoo.tests.common import tagged
from csv import DictReader
from random import randrange
from collections import defaultdict
from freezegun import freeze_time

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)
from odoo.addons.lavka.tests.utils import get_products_from_csv, read_json_data

FIXTURE_PATH='kitchen_test'


def mocked_path(*args, **kwargs):
    return args[1]


def mocked_requests_post(*args, **kwargs):
    return kwargs.get('order'), None


@tagged('lavka', 'kt')
class TestKitchen(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestKitchen, cls).setUpClass()
        cls.wms_connector = WMSConnector()
        cls.external_id = 'external_id_test'
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 'test_tag',
            },
        ]
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'TEST LAVKA',
            'code': '103207',
            'warehouse_tag_ids': cls.tag,
            'wms_id': '42a184f0cbc94732b8aff4664b6121f9000200010001'
        })
        cls.partner = cls.env['res.partner'].create({'name': 'default vendor(lavka)'})
        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURE_PATH,
            filename='products',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)
        for product in cls.products:
            product.taxes_id = product.supplier_taxes_id

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 5.25,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products]
        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')
        cls.orders_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='orders_data'
        )
        cls.log_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='logs_data'
        )
        cls.wms_connector = WMSConnector()


    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    def test_kitchen(self, url):
        wms_ids = [i['order_id'] for i in self.orders_data.get('orders')]
        # создаем заказы клиентов
        for order_data in self.orders_data.get('orders'):
            with patch('common.client.wms.WMSConnector.get_wms_data') as log_response:
                log_response.return_value = self.log_data[order_data.get('order_id')], None
                with freeze_time('2021-03-15 12:00:00'):
                    self.env['wms_integration.order'].create_wms_order([order_data], self.wms_connector)
        # получаем данные из джсона по ингридиентам
        production_data = defaultdict(list)
        stock_log = self.log_data.values()
        for log in stock_log:
            for log_data in log:
                comp = log_data['vars'].get('components')
                if comp and log_data.get('delta_count') > 0:
                    production_data[log_data['order_id']] += [{
                        'product_id': log_data['product_id'],
                        'qty': log_data.get('delta_count'),
                        'spec': comp,
                    }]
        # ищем созданные wms доки
        wms_orders = {
            i.order_id: i for i in self.env['wms_integration.order'].search(
                [
                    ('order_id', 'in', wms_ids)
                ]
            )
        }

        # построцессим доки
        for order in wms_orders.values():
            order.order_post_processing(order)

        # получаем созданный заказы клиентов
        sale_orders = {
            i.wms_id: i for i in self.env['sale.order'].search(
                [
                    ('wms_id', 'in', wms_ids)
                ]
            )
        }
        self.assertEqual(len(sale_orders), 3)
        # собираем данные спеков для каждого заказа
        for wms_id, s_order in sale_orders.items():
            _logger.debug(f'============================SALE ORDER {s_order.name}=========================')
            # список изделий
            production = production_data.get(wms_id)
            mapped = {
                i['product_id']: i for i in production
            }
            self.assertIsNotNone(production)
            # ищем сборки изделий (пикинг производства)
            assemblings = self.env['stock.picking'].search(
                [
                    ('wms_id', '=', wms_id),
                    ('is_assembling', '=', True)
                ]
            )
            self.assertEqual(len(assemblings), len(production))

            # проверяем мувы сборки
            for assemble in assemblings:
                release_from_assemble = assemble.move_lines.filtered(lambda l: l.lavka_type =='prod_goods')
                data = mapped.get(release_from_assemble.product_id.wms_id)
                release_id = data['product_id']
                release_qty = data['qty']

                self.assertEqual(data['qty'], release_from_assemble.quantity_done)
                mapped_spec = {}
                for _line in data['spec']:
                    line = _line[0]
                    mapped_spec[line['product_id']] = (
                        round(float(line['portions']) * float(line['count']) / float(line['quants']), 3)
                    )
                mapped_moves_data = {
                    i.product_id.wms_id: i for i in assemble.move_lines
                }
                ingridients_lines = assemble.move_lines.filtered(lambda l: l.product_id.wms_id != release_id)
                _logger.debug(f'ingr lines in picking:{len(ingridients_lines)} spec:{len(mapped_spec)}')
                # проверяем что мувов столько же сколько строк в спеке
                self.assertEqual(len(ingridients_lines), len(mapped_spec))
                release_move_id = mapped_moves_data[release_id]
                # проверяем что есть строка изделия и она корректная
                self.assertIsNotNone(release_move_id)
                self.assertEqual(len(release_move_id), 1)
                self.assertEqual(release_qty, release_move_id.quantity_done)
                _logger.debug(f'Production {release_move_id.product_id.default_code} '
                             f'qty_move: {release_move_id.quantity_done} '
                             f'qty spec: {release_qty}')
                for move in assemble.move_lines:
                    if move.product_id.wms_id != release_id:
                        spec_qty = round(mapped_spec.get(move.product_id.wms_id), 4)
                        self.assertEqual(round(move.quantity_done, 4), spec_qty)
                        _logger.debug(f' --- > Ingridient {move.product_id.default_code} qty spec:{spec_qty} qty move:{move.quantity_done}')

