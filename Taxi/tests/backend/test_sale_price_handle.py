import base64
import datetime
import uuid
import time
import random
import requests
from freezegun import freeze_time
from odoo.tests import tagged
from odoo.tests.common import HttpSavepointCase, get_db_name
import datetime as dt
from odoo.tools import config
from .test_common import TestVeluationCommon
from odoo.addons.lavka.tests.utils import get_products_from_csv


USER_DEMO = "base.user_admin"
USER_ADMIN = "base.user_root"

@tagged("lavka", "sale_price_list")
class TestSalePriceHandler(HttpSavepointCase, TestVeluationCommon):
    @classmethod
    def setUpClass(self):

        super(TestSalePriceHandler, self).setUpClass()
        self.external_id = 'external_id_test'

        self.wms_id = '6f087c7c54154702a9a569b89a53cb10000200020000'
        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'England Lavka Test',
            'code': '9321123123',
            'warehouse_tag_ids': self.tag,
            'wms_id': self.wms_id,
        })
        self.common_products_dict = get_products_from_csv(
            folder='stowages_test',
            filename='stw_products',
            # '../fixtures/stowages_test/stw_products.csv'
        )
        self.products = self.env['product.product'].create(
            self.common_products_dict)
        self.db_name = get_db_name()
        self.demo_user = self.env.ref(USER_DEMO)
        self.admin_user = self.env.ref(USER_ADMIN)

    def request_by_token(self, path, user, authorized=True, *args, **kwargs):
        token = f"{self.db_name}:{user.openapi_token}"
        _token = base64.b64encode(token.encode()).decode()
        headers = {}
        if authorized:
            headers = {
                'Authorization': f'Basic {_token}',
            }
        p = kwargs.get("params")
        port = config["http_port"]
        url = f'http://localhost:{port}{path}'
        self.opener = requests.Session()
        return self.opener.request(
            'POST', url, timeout=30, headers=headers, params=p
        )

    def test_get_warehouses(self):
        sale_price_list = self.env['sale_price_list.lavka'].create({
            'title': 'Sale Price List',
        })
        self.warehouse_1.write(
            {
                'name': '100',
                'price_list': sale_price_list.id,
            },
            approved=True
        )
        _cursor = self.warehouse_1.write_date.timestamp()
        new_write_date = self.warehouse_1.write_date + datetime.timedelta(minutes=10)
        query = f'''
                UPDATE stock_warehouse
                SET write_date = '{new_write_date}'
                WHERE id =  {self.warehouse_1.id}
                '''
        self.env.cr.execute(
            query,
        )
        data = {
            "cursor": f'{_cursor}',
            "limit": 100,
        }
        resp = self.request_by_token(
            path='/api/v1/warehouses',
            user=self.demo_user,
            params=data)
        self.assertEqual(resp.status_code, 200)
        rec_data = resp.json()
        cursor = rec_data['cursor']
        self.assertIsNotNone(cursor)
        warehouses = rec_data['warehouses']
        self.assertEqual(len(warehouses), 1)
        self.assertEqual(warehouses[0]['sale_price_list_id'], sale_price_list.id )

    def test_get_sale_price(self):
        sale_price_list = self.env['sale_price_list.lavka'].create({
            'title': 'Sale Price List TEST',
            'status': 'active',
        })
        data = {
            "sale_price_list_id": sale_price_list.id,
        }

        resp = self.request_by_token(
            path='/api/v1/sale_prices',
            user=self.demo_user,
            params=data)
        self.assertEqual(resp.status_code, 200)
        rec_data = resp.json()
        price_list_id = rec_data['price_list_id']
        self.assertEqual(price_list_id, sale_price_list.id)
        title = rec_data['title']
        self.assertEqual(title, sale_price_list.title)
        status = rec_data['status']
        self.assertEqual(status, sale_price_list.status)

    def test_get_sale_price_products(self):
        sale_price_list1 = self.env['sale_price_list.lavka'].create({
            'title': 'Sale Price List TEST',
            'status': 'active',
        })
        sale_price_list2 = self.env['sale_price_list.lavka'].create({
            'title': 'Sale Price List 2',
            'status': 'active',
        })

        store_price1 = random.randint(9, 100)
        markdown_price1 = random.randint(9, 100)
        self.env['sale_price_list.lavka.products'].create({
                    'sale_price_list_id': sale_price_list1.id,
                    'product_id': self.products[0].id,
                    'store_price': store_price1,
                    'markdown_price': markdown_price1,
                },)

        store_price2 = random.randint(9, 100)
        markdown_price2 = random.randint(9, 100)
        self.env['sale_price_list.lavka.products'].create({
            'sale_price_list_id': sale_price_list2.id,
            'product_id': self.products[1].id,
            'store_price': store_price2,
            'markdown_price': markdown_price2,
        }, )

        _cursor = (sale_price_list1.write_date - dt.timedelta(seconds=1)).timestamp()
        data = {
            "cursor": f'{_cursor}',
            "limit": 100,
        }
        resp = self.request_by_token(
            path='/api/v1/sale_price_products',
            user=self.demo_user,
            params=data)
        self.assertEqual(resp.status_code, 200)
        rec_data = resp.json()
        cursor = rec_data['cursor']
        self.assertIsNotNone(cursor)
        price_products = rec_data['price_products']
        self.assertEqual(len(price_products), 2)


