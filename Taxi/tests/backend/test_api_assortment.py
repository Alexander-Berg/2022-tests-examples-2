import datetime as dt
import logging
import random
from random import randrange
import requests
from odoo import fields
from odoo.addons.openapi.controllers import pinguin
from odoo.tests.common import HttpSavepointCase, get_db_name, tagged
from odoo.tools import config

from odoo.addons.lavka.tests.utils import get_products_from_csv

_logger = logging.getLogger(__name__)

USER_DEMO = "base.user_admin"
USER_ADMIN = "base.user_root"
MESSAGE = "message is posted from API"


@tagged("lavka", "api_ass")
class TestAssortment(HttpSavepointCase):
    @classmethod
    def setUpClass(self):
        super(TestAssortment, self).setUpClass()
        self.external_id = 'external_id_test'
        self.wms_id = '6f087c7c54154702a9a569b89a53cb10000200020000'
        self.partner = self.env['res.partner'].create(
            {
                'name': 'default vendor(lavka)',
             }
        )
        self.tag = self.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 'test_tag',
            },
        ]
        )
        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'England Lavka Test',
            'code': '9321123123',
            'warehouse_tag_ids': self.tag,
            'wms_id': self.wms_id,
        })

        self.purchase_requisition = self.env['purchase.requisition'].create({
            'vendor_id': self.partner.id,
            'warehouse_tag_ids': self.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {self.partner.name} created')
        self.common_products_dict = get_products_from_csv(
            folder='stowages_test',
            filename='stw_products',
            # '../fixtures/stowages_test/stw_products.csv'
        )
        self.products = self.env['product.product'].create(self.common_products_dict)
        with self.env.cr.savepoint():
            self.requisition_lines = [self.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'start_date': fields.Datetime.today(),
                'price_unit': randrange(1, 17),
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': self.purchase_requisition.id,
                'approve_tax': True,
                'approve_price': True,
                'product_qty': 9999,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in self.products]
            for r in self.requisition_lines:
                r._compute_approve()
            self.purchase_requisition.action_in_progress()
        _logger.debug(f'Purchase requisition  {self.purchase_requisition.id} confirmed')

        self.db_name = get_db_name()
        self.demo_user = self.env.ref(USER_DEMO)
        self.admin_user = self.env.ref(USER_ADMIN)
        self.model_name = "purchase.requisition"

        # создаем пользователя, который может аппрувить налог
        buhs = self.env.ref('account.group_account_manager')
        buhs.users += self.admin_user

    def request(self, method, url, auth=None, **kwargs):
        kwargs.setdefault("model", self.model_name)
        kwargs.setdefault("namespace", "vendor_assortment")
        url = (
            "http://localhost:%d/api/v1/vendor.assortment" % config["http_port"] + url
        ).format(**kwargs)
        self.opener = requests.Session()
        return self.opener.request(
            method, url, timeout=30, auth=auth, json=kwargs.get("data_json")
        )

    def request_from_user(self, user, *args, **kwargs):
        kwargs["auth"] = requests.auth.HTTPBasicAuth(self.db_name, user.openapi_token)
        return self.request(*args, **kwargs)

    def request_from_not_auth_user(self, *args, **kwargs):
        kwargs["auth"] = requests.auth.HTTPBasicAuth(self.db_name, 'some token')
        return self.request(*args, **kwargs)

    def test_get_assortment(self):

        cursor = None
        data = {
            "store_id": self.wms_id,
            "contractor_id": self.partner.external_id,
            "cursor": cursor,
            "namespace": "vendor_assortment"
        }
        resp = self.request_from_user(self.demo_user, "POST", "", data_json=data)

        # happy flow 200
        self.assertEqual(resp.status_code, pinguin.CODE__success)
        resp_data = resp.json()
        assortment = resp_data.get('products')
        first_line = assortment[0]

        self.assertTrue('price' in first_line)
        self.assertTrue('active' in first_line)
        self.assertTrue('product_id' in first_line)

        cursor = resp_data.get('cursor')
        self.assertEqual(len(assortment), len(self.products))
        # update 10 lines, must get only 10 with cursor
        count = 10
        for i in range(count):
            line = self.purchase_requisition.line_ids[i]
            new_time = line.write_date + dt.timedelta(minutes=20)
            line.with_user(self.admin_user).write({'write_date': new_time,
                        'approve_tax': True,
                        'approve_price': True,
                        })

        data.update({'cursor': cursor})
        cursor_date = dt.datetime.utcfromtimestamp(float(cursor))
        contract_lines = self.env['purchase.requisition.line'].search(
                [
                    ('requisition_id', 'in', [self.purchase_requisition.id]),
                    ('active', 'in', (False, True)),
                    ('approve', '=', True),
                    ('write_date', '>', cursor_date),
                ])
        resp1 = self.request_from_user(self.demo_user, 'POST', '', data_json=data)
        resp1_data = resp1.json()
        self.assertEqual(len(resp1_data.get('products')), count)
        # new cursor must differ from new
        cursor_2 = resp1_data.get('cursor')
        self.assertNotEqual(cursor, cursor_2)

        data.update({'cursor': cursor_2})
        resp2 = self.request_from_user(self.demo_user, 'POST', '', data_json=data)
        resp2_data = resp2.json()
        # all data empty new cursor must be equal the old one
        self.assertEqual(resp2_data.get('cursor'), cursor_2)

        # check 404
        data404 = {
            "store_id": 'some id',
            "contractor_id": self.partner.external_id,
            "cursor": cursor,
            "namespace": "vendor_assortment"
        }
        resp = self.request_from_user(self.demo_user, "POST", "", data_json=data404)

        self.assertEqual(resp.status_code, 404)
        data404 = {
            "store_id": self.wms_id,
            "contractor_id": str(random.randint(999, 5666)),
            "cursor": cursor,
            "namespace": "vendor_assortment"
        }
        resp = self.request_from_user(self.demo_user, "POST", '', data_json=data404)
        self.assertEqual(resp.status_code, 404)

        resp = self.request_from_not_auth_user("POST", '', data_json=data)
        self.assertEqual(resp.status_code, 401)
        _logger.debug('Done')
