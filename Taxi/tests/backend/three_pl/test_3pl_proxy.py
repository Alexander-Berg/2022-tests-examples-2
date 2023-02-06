import datetime as dt
import json
import os
from unittest.mock import patch

from common.client.ftp_proxy import FTProxy
from odoo.addons.lavka.backend.models.three_pl.models import Provider
from odoo.tests.common import SavepointCase, tagged

from odoo.addons.queue_job.job import Job

FIXTURES_PATH = '/fixtures/three_pl/'


def read_json_data(filename):
    with open(f'{os.path.dirname(__file__)}{os.sep}{FIXTURES_PATH}{os.sep}{filename}.json',
              encoding='UTF-8') as wms_json:
        res_json = json.load(wms_json)
    return res_json


class Base3PLExchange(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(Base3PLExchange, cls).setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.wh_in, cls.wh_out = cls.factory.create_warehouses(qty=2)

        cls.wh_out.type = 'dc_external'
        cls.wh_out.address = 'address dc'
        cls.wh_in.address, cls.wh_in.name = 'address wh', 'name wh'

        _tpl = cls.env['three_pl.providers'].create([{
            'active': True,
            'warehouse': cls.wh_out.id,
            'partner_code': '0024',
            'url': 'infra.eda.yandex.net',
            'user_login': 'profresh',
            'user_password': 'PI6Lri6laiHX6WdtvUMcfmBF',
            'path_in': 'FromLogistic0024',
            'path_out': 'ToLogistic0024',
            'date_start': dt.datetime.utcnow(),
            's3_path': 'profresh_0024',
        }])

        cls.provider = Provider(
            user_login=_tpl.user_login,
            user_password=_tpl.user_password,
            url=_tpl.url,
            path_in=_tpl.path_in,
            path_out=_tpl.path_out,
            partner_code=_tpl.partner_code,
        )

        cls.products = cls.factory.create_products([cls.wh_in, cls.wh_out], qty=8)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.wh_in.warehouse_tag_ids
        )
        cls.purchased_products = cls.products[:5]

        cls.env['product.tag'].search([('type', 'in', ('storage_type', 'nonfood'))]).unlink()
        p_tag1 = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'dry',
            }
        )
        p_tag2 = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'refrigerator',
            }
        )
        p_tag3 = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'True',
            }
        )

        cls.purchased_products[:2].product_tag_ids = p_tag1 + p_tag3
        cls.purchased_products[2:].product_tag_ids = p_tag2

        cls.extra_products = cls.products[5:8]
        cls.po, cls.po2, cls.po3 = cls.factory.create_purchase_order(
            cls.purchased_products,
            cls.purchase_requisition,
            cls.wh_out,
            qty=3,
        )
        #todo: для теста  с pbl (distribuiton line)
        # cls.env['cross.dock.pbl'].create({
        #     'vendor_id': cls.vendor.id,
        #     'type_destination': 'warehouse',
        #     'destination_warehouse': cls.wh_in.id,
        #     'transit_warehouse': cls.wh_out.id,
        #     'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
        #     'delivery_type': 'dc_pbl',
        # })
        cls.vendor = cls.purchase_requisition.vendor_id

        # dc storage chains
        for pr in cls.purchased_products:
            cls.env['supply.chain'].create({
                'type_supplier': 'vendor',
                'vendor_id': cls.vendor.id,
                'type_destination': 'warehouse',
                'destination_warehouse': cls.wh_out.id,
                'product_id': pr.id,
                'changed': True,
            })

        cls.tr = cls.factory.create_transfer(
            cls.purchased_products,
            cls.wh_in,
            cls.wh_out,
        )
        cls.tr.button_approved()
        cls.tr.button_send_shipment() #  state 'sent'
        cls.tr2 = cls.factory.create_transfer(
            cls.purchased_products,
            cls.wh_in,
            cls.wh_out,
        )


@tagged("tpl")
class Test3PLProxy(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(Test3PLProxy, cls).setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)

        _tpl = cls.env['three_pl.providers'].create([{
            'active': True,
            'warehouse': cls.warehouses[0].id,
            'partner_code': '0024',
            'url': 'infra.eda.yandex.net',
            'user_login': 'profresh',
            'user_password': 'PI6Lri6laiHX6WdtvUMcfmBF',
            'path_in': 'FromLogistic0024',
            'path_out': 'ToLogistic0024',
            'date_start': dt.datetime.utcnow(),
            's3_path': 'profresh_0024',
        }])

        cls.provider = Provider(
            user_login=_tpl.user_login,
            user_password=_tpl.user_password,
            url=_tpl.url,
            path_in=_tpl.path_in,
            path_out=_tpl.path_out,
            partner_code=_tpl.partner_code,
        )

    def rem_test_get_files_list(self):
        conn = FTProxy(self.provider)
        file_names = conn.get_files_list(self.provider.path_in)
        self.assertTrue(len(file_names) > 0)
        res = 1

    def rem_test_get_file(self):
        conn = FTProxy(self.provider)
        file_data = conn.receive_file(self.provider.path_in, '0024_220713150138.json')
        self.assertIsNotNone(file_data)

    def rem_test_send_file(self):
        conn = FTProxy(self.provider)
        data = [
            {
                'test_str': 'ACC',
                'test_int': 2,
            }
        ]
        file_name = conn.send_file(self.provider.path_out, data)
        self.assertIsNotNone(file_name)
        file_data = conn.receive_file(self.provider.path_out, file_name)
        self.assertEqual(file_data[0]['test_str'], 'ACC')
        # удаляем созданный файл
        res = conn.delete_file(self.provider.path_out, file_name)
        self.assertTrue(res)


@tagged("tpl_po_send")
class Test3PLPOExchange(Base3PLExchange):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @staticmethod
    def prepare_file(pos, trs, template):
        # todo заполнить поля
        res = []
        for po in pos:
            for line in po.order_line:
                _t = template.copy()
                _t['TYPE'] = 'PST'
                _t['KOL'] = line.init_product_qty
                res.append(_t)

        for tr in trs:
            for line in tr.transfer_lines:
                _t = template.copy()
                _t['TYPE'] = 'REA'
                _t['KOL'] = line.qty_in_transfer
                res.append(_t)

        return res

    def rem_test_update_from_tpl(self):
        with patch('common.client.ftp_proxy .FTPrpoxy.get_files_list') as get_files_list:
            with patch('common.client.ftp_proxy .FTPrpoxy.receive_file') as receive_file:
                get_files_list.return_value = ['test_file_name']
                template = read_json_data('vygruzka.json')
                receive_file.return_value = self.prepare_file(self.po, self.tr, template)
                self.env['three_pl.updater'].update_from_tpl(self.provider)
                tasks = self.env['queue.job'].search([])
                # таски двух типов
                for task in tasks:
                    Job.load(self.env, task.uuid).perform()


@tagged("tpl_tr_send")
class Test3PLFRExchange(Base3PLExchange):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def rem_test_send_transfer_to_tpl(self):
        with patch('common.client.ftp_proxy .FTPrpoxy.send_file') as proxy_data:
            proxy_data.return_value = 'test_file_name'
            data = self.env['three_pl.sender'].send_po_to_3pl(self.provider, self.tr.ids)
