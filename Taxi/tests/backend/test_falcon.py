import base64
import uuid

import requests
from freezegun import freeze_time
from odoo.tests import tagged
from odoo.tests.common import HttpSavepointCase, get_db_name
import datetime as dt
from odoo.tools import config

@tagged("lavka", "falcon")
class TestFalcon(HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=5)
        with freeze_time(dt.datetime.now() - dt.timedelta(days=1)):
            cls.purchase_requisition = cls.factory.create_purchase_requisition(
                cls.products,
                geo_tag=cls.warehouses.mapped(
                    'warehouse_tag_ids')
            )

        tax = cls.factory.create_tax(
            ['amount', 'type_tax_use'],
            [20, 'purchase']
        )
        cls.admin_user = cls.env.ref('base.user_root')
        buhs = cls.env.ref('account.group_account_manager')
        cat = cls.env.ref('lavka.group_approve_price')

        buhs.users += cls.admin_user
        cat.users += cls.admin_user
        # поставим коды поставщиков
        for line in cls.purchase_requisition.line_ids:
            line.sudo().write({
                'tax_id': tax.id,
            })
            line.with_user(cls.admin_user).set_approve_tax()
            line.sudo()._compute_approve()

        cls.pos = cls.factory.create_purchase_order(cls.products, cls.purchase_requisition, cls.warehouses, qty=4)
        for i, po in enumerate(cls.pos):
            _mark = f'mark{i}'
            po.state = 'purchase'
            for line in po.order_line:
                line.mark = _mark

            pickings = po._create_picking_from_wms(po.order_line)
            cls.env['wms_integration.order'].complete_picking(pickings[0], dt.datetime.now(), 'some_order_id')
            po.state = 'done'
            po.skip_check_before_invoicing = True

            po.wms_id = f'{uuid.uuid4()}'

            cls.wms_acc = cls.env['wms_integration.order'].create([{
                'external_id': f'{po.external_id}.qeqwe{i}',
                'common_external_id': po.external_id,
                'order_id': po.wms_id,
                'created': dt.datetime.now(),
                'updated': dt.datetime.now(),
                'approved': dt.datetime.now(),
                'status': 'ok',
                'type': 'acceptance',
                'stowage_count': 1,
                'processing_status': 'ok',
            }])

        cls.demo_user = cls.env.ref('base.user_admin')
        cls.db_name = get_db_name()

    def request_by_token(self, user, authorized=True, *args, **kwargs):
        token = f"{self.db_name}:{user.openapi_token}"
        _token = base64.b64encode(token.encode()).decode()
        headers = {}
        if authorized:
            headers = {
                'Authorization': f'Basic {_token}',
            }
        p = kwargs.get("params")
        port = config["http_port"]
        url = f'http://localhost:{port}/api/v1/falcon/docs'
        self.opener = requests.Session()
        return self.opener.request(
            'GET', url, timeout=30, headers=headers, params=p
        )

    def test_get_falcon(self):
        cursor = '0'
        data = {
            "store_id": self.warehouses[0].wms_id,
            "cursor": cursor,
            "limit": 200,
        }
        resp = self.request_by_token(self.demo_user, params=data)
        self.assertEqual(resp.status_code, 200)
        rec_data = resp.json()
        cursor = rec_data['cursor']
        self.assertIsNotNone(cursor)
        orders = rec_data['orders']
        self.assertEqual(len(orders), 4)
        for order in orders:
            items = order['items']
            self.assertEqual(len(items), 5)
        resp = self.request_by_token(self.demo_user, authorized=False, params=data)
        self.assertEqual(resp.status_code, 401)

    def test_get_falcon_no_store_id(self):
        cursor = '0'
        data = {
            "cursor": cursor,
            "limit": 2,
        }
        resp = self.request_by_token(self.demo_user, params=data)
        self.assertEqual(resp.status_code, 200)
        rec_data = resp.json()
        cursor = rec_data['cursor']
        self.assertIsNotNone(cursor)
        orders = rec_data['orders']
        self.assertEqual(len(orders), 2)
        for order in orders:
            items = order['items']
            self.assertEqual(len(items), 5)

        resp = self.request_by_token(self.demo_user, authorized=False, params=data)
        self.assertEqual(resp.status_code, 401)
        # пустые параметры
        resp = self.request_by_token(self.demo_user, params={})
        rec_data = resp.json()
        cursor = rec_data['cursor']
        self.assertIsNotNone(cursor)
        orders = rec_data['orders']
        self.assertEqual(len(orders), 4)
