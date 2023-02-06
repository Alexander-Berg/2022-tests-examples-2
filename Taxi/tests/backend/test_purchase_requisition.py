import time
import uuid
from random import randrange
import logging
import datetime as dt
from unittest.mock import patch
from odoo.tests.common import Form
from common.client.wms import WMSConnector
from freezegun import freeze_time
from dateutil.relativedelta import relativedelta
from common.config import cfg
from odoo.tests import tagged
from odoo import exceptions
from odoo.fields import Datetime
from odoo.tests.common import SavepointCase, Form
from odoo.addons.lavka.tests.utils import read_json_data

_logger = logging.getLogger(__name__)
rnd = lambda x: f'{x}-{uuid.uuid4().hex}'
FIXTURES_PATH = 'purch_requisition_test'


def mocked_path(*args, **kwargs):
    return args[1]


def mocked_requests_post(*args, **kwargs):
    return kwargs.get('order'), None

@tagged('lavka', 'prices', 'oebs', 'search_lines')
class TestSearchLines(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': rnd('geo'),
            }
        )
        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': rnd('geo'),
            }
        )
        wh_tag3 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'size',
                'name': rnd('size'),
            }
        )
        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': rnd('wh'),
                'code': rnd('wh-code'),
                'warehouse_tag_ids': [cls.wh_tag1.id, wh_tag3.id],
            }
        )
        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': rnd('wh'),
                'code': rnd('wh-code'),
                'warehouse_tag_ids': [cls.wh_tag2.id, wh_tag3.id],
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': rnd('p'),
                'wms_id': 'p1',
            },

        )
        cls.p2 = cls.env['product.product'].create(
            {
                'name': rnd('p'),
                'wms_id': 'p2',
             },
        )

        cls.v1_vat = rnd('v1-vat')
        cls.v1 = cls.env['res.partner'].create(
            {
                'name': rnd('v'),
                'is_company': True,
                'vat': cls.v1_vat,
            }
        )

        cls.v2_vat = rnd('v2-vat')
        cls.v2 = cls.env['res.partner'].create(
            {
                'name': rnd('v'),
                'is_company': True,
                'vat': cls.v2_vat,
            }
        )

        cls.v1_contract = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'warehouse_tag_ids': [cls.wh_tag1.id, cls.wh_tag2.id],
                'state': 'ongoing',
            }
        )
        with freeze_time('2021-03-15 12:00:00'):
            new_lines = cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v1_contract.id,
                        'product_id': p.id,
                        'start_date': Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve_tax': True,
                        'active': True,
                        'approve_price': True,
                    }
                    for p in [cls.p1, cls.p2]
                ]
            )

            cls.v2_contract = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v2.id,
                    'warehouse_tag_ids': cls.wh_tag1,
                    'state': 'ongoing',
                }
            )
            new_lines += cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v2_contract.id,
                        'product_id': p.id,
                        'start_date': Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 400 + randrange(4, 7),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve_tax': True,
                        'active': True,
                        'approve_price': True,
                    }
                    for p in [cls.p1, cls.p2]
                ]
            )

            cls.draft_contract = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v2.id,
                    'warehouse_tag_ids': cls.wh_tag1,
                    'state': 'draft',
                }
            )

            new_lines += cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.draft_contract.id,
                        'product_id': p.id,
                        'start_date': Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 400 + randrange(4, 7),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve_tax': True,
                        'active': True,
                        'approve_price': True,
                    }
                    for p in [cls.p1, cls.p2]
                ]
            )

            for l in new_lines:
                l._compute_approve()

    def test_001_search_lines(self):
        from common.config import cfg

        cfg.set('oebs.contracts.skip_check', True)

        all_lines = self.env['purchase.requisition'].search_lines(self.wh1, self.p1)
        self.assertEqual(
            {(i.requisition_id, i.product_id) for i in all_lines},
            {
                (self.v1_contract, self.p1),
                (self.v2_contract, self.p1),
            },
            'прайсы по лавка-товар',
        )

        self.assertTrue(self.draft_contract.id not in [i.requisition_id.id for i in all_lines])

        lines_by_v1 = self.env['purchase.requisition'].search_lines(self.wh1, self.p1, vendor=self.v1)
        self.assertEqual(
            {(i.requisition_id, i.product_id) for i in lines_by_v1},
            {(self.v1_contract, self.p1)},
            'прайсы по лавка-товар-поставщик',
        )

        v2_contract_lines = self.env['purchase.requisition'].search_lines(self.wh1, self.p1, contract=self.v2_contract)
        self.assertEqual(
            {(i.requisition_id, i.product_id) for i in v2_contract_lines},
            {(self.v2_contract, self.p1)},
            'прайсы по лавка-товар-контракт',
        )

        cfg.set('oebs.contracts.skip_check', False)

        all_lines = self.env['purchase.requisition'].search_lines(self.wh1, self.p1)
        self.assertEqual(len(all_lines), 0, 'нет оебс контракта')

        v1_oebs_sup = {
            'OBJECT_ID': '300',
            'EXPORT_DATE': '300',
            'ORG_ID': '300',
            'ORG_NAME': '300',
            'VENDOR_ID': '300',
            'VENDOR_SITE_ID': '300',
            'VENDOR_SITE_CODE': '300',
            'FOREIGN_SUPPLIER': '300',
            'VENDOR_NAME': '300',
            'VENDOR_NAME_ALT': '300',
            'ADDRESS_LINE1': '300',
            'ADDRESS_LINE2': '300',
            'INN': self.v1_vat,
            'KPP': '',
            'PHONE': '300',
            'EMAIL_ADDRESS': '300',
            'SPAM': 'hello',
        }
        self.env['oebs.supplier']._sync_yt_row(
            self.env['oebs.supplier']._remap(v1_oebs_sup, self.env['oebs.supplier'].YT_MAPPING)
        )

        v1_oebs_contract = {
            'OBJECT_ID': '300',
            'EXPORT_DATE': '300',
            'ORG_ID': '300',
            'ORG_NAME': '300',
            'VENDOR_ID': '300',
            'VENDOR_SITE_ID': '300',
            'VENDOR_SITE_CODE': '300',
            'PO_HEADER_ID': '300',
            'PO': '300',
            'COORDINATOR': '300',
            'TERMS_ID': '300',
            'TERMS_NAME': '300',
            'CONTRACT_NUMBER': '300',
            'MVP': '300',
            'MVP_DESCRIPTION_RUS': '300',
            'MVP_DESCRIPTION_ENG': '300',
            'AGREEMENT_DATE': '1970-01-01 00:00:00',
            'START_DATE': '1970-01-02 00:00:00',
            'END_DATE': '2070-01-03 00:00:00',
            'CURRENCY': '300',
        }
        oebs_contract = self.env['oebs.contract']._sync_yt_row(
            self.env['oebs.contract']._remap(v1_oebs_contract, self.env['oebs.contract'].YT_MAPPING)
        )

        self.assertEqual(
            oebs_contract.oebs_supplier_id.id, self.v1.oebs_supplier_id.id,
        )

        self.v1_contract.write({'oebs_contract_id': oebs_contract.id})

        self.assertEqual(
            oebs_contract.id, self.v1_contract.oebs_contract_id.id,
        )

        self.v1_contract._compute_valid()
        self.assertTrue(self.v1_contract.valid, 'контракт ок')

        v1_oebs_contract['END_DATE'] = '1970-01-02 00:00:00'
        self.env['oebs.contract']._sync_yt_row(
            self.env['oebs.contract']._remap(v1_oebs_contract, self.env['oebs.contract'].YT_MAPPING)
        )

        self.v1_contract._compute_valid()
        self.assertFalse(self.v1_contract.valid, 'контракт протух')

        v1_oebs_contract['START_DATE'] = '2070-01-01 00:00:00'
        self.env['oebs.contract']._sync_yt_row(
            self.env['oebs.contract']._remap(v1_oebs_contract, self.env['oebs.contract'].YT_MAPPING)
        )

        self.v1_contract._compute_valid()
        self.assertFalse(self.v1_contract.valid, 'контракт еще не действует')
        cfg.set('oebs.contracts.skip_check', True)


@tagged('lavka', 'prices', 's_info')
class TestSupplierInfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # new
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=6)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.pos = cls.factory.create_purchase_order(cls.products, cls.purchase_requisition, cls.warehouses, qty=1)
        for po in cls.pos:
            po.write({'skip_check_before_invoicing': True})

        cls.factory.confirm_po(cls.pos)

    def test_requisition_constrait_in_form(self):

        partner = self.env['res.partner'].create({'name': 'Vendor'})
        purchase_requsition = self.env['purchase.requisition'].create([{
            'vendor_id': partner.id,
            'warehouse_tag_ids': self.warehouses.warehouse_tag_ids.ids,
            'state': 'ongoing',
        }])

        pr_form = Form(purchase_requsition)

        for product in self.products:
            with pr_form.line_ids.new() as line_form:
                line_form.product_id = product
                line_form.start_date = dt.datetime.now()
                line_form.price_unit = 4
                line_form.product_code = product.default_code
                line_form.qty_multiple = 1
                line_form.tax_id = product.supplier_taxes_id
        pr_form.save()

        # попробуем еще добавить дублей
        for product in self.products:
            with pr_form.line_ids.new() as line_form:
                line_form.product_id = product
                line_form.price_unit = 4
                line_form.product_code = product.default_code
                line_form.qty_multiple = 1
                line_form.tax_id = product.supplier_taxes_id
        with self.assertRaises(Exception):
            pr_form.save()


# use as example
@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPrices(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем прайсы
        # нормальный активный
        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        # first
        cls.purchase_requsition_active_with_tag = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'cancel',
        })

        _logger.debug(f'Partner {cls.partner.name} created')

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'price_unit': 11.1,
            'start_date': dt.datetime.now(),
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_active_with_tag.id,
            'approve_tax': True,
            'active': True,
            'approve_price': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products.values()]

        for r in cls.requsition_lines:
            r._compute_approve()
        # cls.purchase_requsition_active_with_tag.action_in_progress()
        _logger.debug(f'Normal Active Purchase requsition  {cls.purchase_requsition_active_with_tag.id} confirmed')

        # нормальный Не активные строки
        cls.purchase_requsition_NOT_ACTIVE_with_tag = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        time.sleep(1)

        cls.not_active_requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 22.2,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_NOT_ACTIVE_with_tag.id,
            'active': True,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products.values()]

        for r in cls.not_active_requsition_lines:
            r._compute_approve()
        cls.purchase_requsition_NOT_ACTIVE_with_tag.action_in_progress()
        _logger.debug(
            f'Normal NOT Active Purchase requsition  {cls.purchase_requsition_NOT_ACTIVE_with_tag.id} confirmed')

        # ОТМЕНЕННЫЙ Не активные строки
        cls.canceled_purchase_requsition_NOT_ACTIVE_with_tag = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'cancel',
        })

        cls.canceled_not_active_requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 33.3,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.canceled_purchase_requsition_NOT_ACTIVE_with_tag.id,
            'active': False,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products.values()]

        for r in cls.canceled_not_active_requsition_lines:
            r._compute_approve()

        # нормальный без тега активные строки
        cls.no_tag_purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'state': 'ongoing',
        })

        cls.no_tag_active_requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 44.4,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.no_tag_purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products.values()]

        for r in cls.no_tag_active_requsition_lines:
            r._compute_approve()
        cls.no_tag_purchase_requsition.action_in_progress()
        _logger.debug(f'Normal NOT Active Purchase requsition  {cls.no_tag_purchase_requsition.id} confirmed')

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 22.2)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPricesCanceled(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем отменнные прайсы

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.reqs = []
        for k in range(4):
            req = cls.env['purchase.requisition'].create({
                'name': f'req_{k}',
                'vendor_id': cls.partner.id,
                'warehouse_tag_ids': cls.tag,
                'state': 'cancel',
            })

            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 1 + k,
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': req.id,
                'approve_tax': True,
                'active': True,
                'approve_price': True,
                'product_qty': 1,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products.values()]
            for r in cls.requsition_lines:
                r._compute_approve()
            cls.reqs.append(req)

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 1.0)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPricesNoTag(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag']
        for q in range(2):
            tag = cls.env['stock.warehouse.tag'].create([
                {
                    'type': 'geo',
                    'name': f't_{q}',
                },
            ]
            )
            cls.tag += tag

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем некоторые прайсы без тега

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.reqs = []
        for k in range(4):
            if k < 3:
                tags = None
            else:
                tags = cls.tag
            req = cls.env['purchase.requisition'].create({
                'name': f'req_{k}',
                'vendor_id': cls.partner.id,
                'warehouse_tag_ids': tags,
                'state': 'ongoing',
            })

            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 1 + k,
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': req.id,
                'approve_tax': True,
                'active': True,
                'approve_price': True,
                'product_qty': 1,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products.values()]
            for r in cls.requsition_lines:
                r._compute_approve()
            req.action_in_progress()
            cls.reqs.append(req)

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 4.0)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPricesNoActive(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag']
        for q in range(2):
            tag = cls.env['stock.warehouse.tag'].create([
                {
                    'type': 'geo',
                    'name': f't_{q}',
                },
            ]
            )
            cls.tag += tag

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем прайсы

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.reqs = []
        for k in range(4):

            req = cls.env['purchase.requisition'].create({
                'name': f'req_{k}',
                'vendor_id': cls.partner.id,
                'warehouse_tag_ids': cls.tag,
                'state': 'ongoing',
            })
            if k < 3:
                active = False
            else:
                active = True
            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 1 + k,
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': req.id,
                'approve_tax': True,
                'active': active,
                'approve_price': True,
                'product_qty': 1,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products.values()]
            for r in cls.requsition_lines:
                r._compute_approve()
            req.action_in_progress()
            cls.reqs.append(req)

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 4.0)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPricesNoActiveNoTag(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag']
        for q in range(2):
            tag = cls.env['stock.warehouse.tag'].create([
                {
                    'type': 'geo',
                    'name': f't_{q}',
                },
            ]
            )
            cls.tag += tag

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем прайсы

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.reqs = []
        # активные строки тока у агримента без тего
        for k in range(4):
            if k < 3:
                tags = cls.tag
            else:
                tags = None
            req = cls.env['purchase.requisition'].create({
                'name': f'req_{k}',
                'vendor_id': cls.partner.id,
                'warehouse_tag_ids': tags,
                'state': 'ongoing',
            })
            if k < 3:
                active = False
            else:
                active = True
            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 1 + k,
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': req.id,
                'approve_tax': True,
                'active': active,
                'approve_price': True,
                'product_qty': 1,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products.values()]
            for r in cls.requsition_lines:
                r._compute_approve()
            req.action_in_progress()
            cls.reqs.append(req)

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 1.0)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'look_prices')
class TestLookUpAllPricesNoTagAtALL(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wms_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='checks',
        )
        log_data = read_json_data(
            folder=FIXTURES_PATH,
            filename='logs',
        )
        cls.wms_connector = WMSConnector()
        cls.tag = cls.env['stock.warehouse.tag']
        for q in range(2):
            tag = cls.env['stock.warehouse.tag'].create([
                {
                    'type': 'geo',
                    'name': f't_{q}',
                },
            ]
            )
            cls.tag += tag

        c = 0
        mapped_products = {}
        mapped_wh = {}
        doc_ids = []
        for order in wms_data:
            # создаем склады
            store_id = order['store_id']
            order_id = order['order_id']
            doc_ids.append(order_id)
            if not mapped_wh.get(store_id):
                wh = cls.env['stock.warehouse'].create({
                    'name': f'test_wh_{c}',
                    'code': f'{c}',
                    'warehouse_tag_ids': cls.tag,
                    'wms_id': store_id
                })
                mapped_wh[store_id] = wh

            req = order.get('required')
            # создаем товары
            for prd_data in req:
                wms_id = prd_data['product_id']
                if not mapped_products.get(wms_id):
                    res = cls.env['product.product'].create(
                        {
                            'name': f'test_product_{c}',
                            'default_code': f'{c}',
                            'type': 'product',
                            'wms_id': wms_id,
                            'taxes_id': 1,

                        }
                    )
                    mapped_products[wms_id] = res
                    c += 1
            # создаем доки wms
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_data, None
                with freeze_time('2021-03-15 12:00:00'):
                    cls.env['wms_integration.order'].create_wms_order([order], cls.wms_connector, 'cursor_1')

        cls.docs = {i.order_id: i for i in cls.env['wms_integration.order'].search([
            ('order_id', 'in', doc_ids)
        ])}
        cls.products = mapped_products
        cls.warehouses = mapped_wh

        # создаем некоторые прайсы без тега

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.reqs = []
        for k in range(4):

            req = cls.env['purchase.requisition'].create({
                'name': f'req_{k}',
                'vendor_id': cls.partner.id,
                'state': 'ongoing',
            })

            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 1 + k,
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': req.id,
                'approve_tax': True,
                'active': True,
                'approve_price': True,
                'product_qty': 1,
                'product_code': '300',
                'product_name': 'vendor product name',
                'qty_multiple': 1,
            }) for i in cls.products.values()]
            for r in cls.requsition_lines:
                r._compute_approve()
            req.action_in_progress()
            cls.reqs.append(req)

    def _test_lookup_prices(self):
        pr = self.env['purchase.requisition.line']
        self.env['ir.config_parameter'].set_param('lookup_all_prices', 'true')
        for product in self.products.values():
            price = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0],
                only_price=True)
            self.assertTrue(price == 1.0)
            req_line = pr.get_last_req_line(
                product,
                list(self.warehouses.values())[0])
            self.assertIsNotNone(req_line)

        for wms_doc in self.docs.values():
            if wms_doc.type in ['order', 'check_product_on_shelf']:
                res = wms_doc.post_processing(wms_doc)
                self.assertEqual(res.value, 'ok')


@tagged('lavka', 'prices', 'new_taxes')
class TestTaxesInRequisitions(TestLookUpAllPrices):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purch_tax = cls.env['account.tax'].search(
            [
                ('type_tax_use', '=', 'purchase'),
            ]
        )[0]
        cls.new_purch_tax = cls.purch_tax.copy()
        cls.new_purch_tax.amount += 1
        cls.new_sale_tax = cls.new_purch_tax.copy()
        cls.new_sale_tax.type_tax_use = 'sale'
        cls.new_purch_tax_2 = cls.purch_tax.copy()
        cls.new_purch_tax_2.amount += 2

        cls.new_sale_tax_2 = cls.new_sale_tax.copy()
        cls.new_sale_tax_2.amount += 3

        cls.admin_user = cls.env.ref("base.user_root")
        # создаем пользователя, который может аппрувить налог
        buhs = cls.env.ref('account.group_account_manager')
        buhs.users += cls.admin_user

    def test_correct_taxes(self):

        product = self.env['product.product'].create({
            'name': 'test_p',
            'type': 'product',
            'default_code': '12',
            'wms_id': '12',
        })

        purchase_requsition = self.env['purchase.requisition'].create({
            'vendor_id': self.partner.id,
            'warehouse_tag_ids': self.tag,
            'state': 'ongoing',
        })

        req_line_data = {
            'product_id': product.id,
            'price_unit': 11.1,
            'start_date': dt.datetime.now(),
            'product_uom_id': product.uom_id.id,
            'tax_id': self.purch_tax.id,
            'requisition_id': purchase_requsition.id,
            'approve_tax': True,
            'active': True,
            'approve_price': True,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }

        requsition_lines = self.env['purchase.requisition.line'].create(req_line_data)

        for r in requsition_lines:
            r._compute_approve()

        req_line_data['tax_id'] = self.new_purch_tax.id
        # создаем новый лайн с другим налогом на тот же продукт
        self.env['purchase.requisition.line'].create(req_line_data)

        self.assertTrue(product.new_taxes_id.amount == self.new_purch_tax.amount)
        self.assertTrue(product.new_taxes_id.type_tax_use == 'sale')
        self.env.ref('account.group_account_manager').users += self.admin_user
        self.assertTrue(self.admin_user.has_group('account.group_account_manager'))
        product.product_tmpl_id.with_user(self.admin_user).tax_validate()
        self.assertTrue(not product.new_taxes_id)
        self.assertTrue(product.taxes_id.type_tax_use == 'sale')
        # повторно с тем же налогом но другой ценой
        req_line_data['price_unit'] = 22.2
        self.env['purchase.requisition.line'].create(req_line_data)

        self.assertTrue(not product.new_taxes_id)
        self.assertTrue(product.taxes_id.type_tax_use == 'sale')

        # ставим налог, у котрого нет брата с типом sale
        with self.assertRaises(AssertionError):
            req_line_data['tax_id'] = self.new_purch_tax_2.id
            self.env['purchase.requisition.line'].create(req_line_data)

        # ставим налог с типом sale вместо purchase
        with self.assertRaises(AssertionError):
            req_line_data['tax_id'] = self.new_sale_tax_2.id
            self.env['purchase.requisition.line'].create(req_line_data)

    def test_diff_percente(self):
        diff_percente = self.env['purchase.requisition.line'].diff_percente

        old_price, new_price = 100, 120
        diff = new_price - old_price
        perc = diff_percente(diff, old_price)
        self.assertEqual(perc, 20)

        old_price, new_price = 100, 70
        diff = new_price - old_price
        perc = diff_percente(diff, old_price)
        self.assertEqual(perc, 30)

        old_price, new_price = 100, 100
        diff = new_price - old_price
        perc = diff_percente(diff, old_price)
        self.assertEqual(perc, 0)


@tagged('lavka', 'prices', 'new_req_lines')
class TestNewRequisitionLines(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=5)
        assert cls.warehouses, 'Warehouses look empty'
        cls.products = cls.factory.create_products(cls.warehouses, qty=10)
        assert cls.products, 'Products look empty'
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )

    def test_insert_req_lines(self):
        # добавим регулярных цен на сегодня
        self.factory.create_requisition_lines(
            self.products[:8],
            self.purchase_requisition,
        )
        # добавим регулярных цен на будущее
        self.factory.create_requisition_lines(
            self.products[:5],
            self.purchase_requisition,
            start_date=Datetime.today() + dt.timedelta(days=2),
        )
        # добавим промо цену на сегодня:
        self.factory.create_requisition_lines(
            self.products[:5],
            self.purchase_requisition,
            end_date=Datetime.today() + dt.timedelta(days=3),
        )
        # добавим промо цену на будущее:
        self.factory.create_requisition_lines(
            self.products[:6],
            self.purchase_requisition,
            start_date=Datetime.today() + dt.timedelta(days=2),
            end_date=Datetime.today() + dt.timedelta(days=4),
        )

        all_lines = self.env['purchase.requisition.line'].search(
            [],
            order="start_date",
        )

        # проверим что все цены идут по порядку
        for product in self.products:
            lines = all_lines.filtered_domain([
                ('product_id', '=', product.id),
                ('requisition_id', '=', self.purchase_requisition.id),
            ])
            if len(lines) > 1:
                for i in range(1, len(lines)):
                    self.assertEqual(
                        lines[i - 1].actual_end_date + dt.timedelta(seconds=1),
                        lines[i].start_date
                    )

    def test_change_activity(self):
        some_product = self.products[0]
        some_product_lines = self.env['purchase.requisition.line'].search([
            ('requisition_id', '=', self.purchase_requisition.id),
            ('product_id', '=', some_product.id),
        ])
        some_product_lines[0]._change_activity(False)
        for line in some_product_lines:
            self.assertFalse(line.active)
        some_product_lines[0]._change_activity(True)
        for line in some_product_lines:
            self.assertTrue(line.active)


class TestPrCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.requisition_lines = []
        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=5)
        assert cls.warehouses, 'Warehouses look empty'
        cls.products = cls.factory.create_products(cls.warehouses, qty=10)
        assert cls.products, 'Products look empty'
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'
            ),
            add_lines=False,
        )


# первое добавление с первой ценой: цена с концом
# нег: не должно добавиться
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase1(TestPrCommon):

    def test_create_wrong_prices(self):
        with self.assertRaises(exceptions.UserError) as context:
            self.requsition_lines = self.factory.create_requisition_lines(
                self.products,
                self.purchase_requisition,
                start_date=Datetime.today(),
                end_date=Datetime.today() + dt.timedelta(days=10),
            )
        self.assertTrue(
            'First requisition line should not have an end date' in
            str(context.exception)
        )


# первое добавление с первой ценой: цена без конца (ок)
# проверить непрерывность цен (ok)
# отсортировать по start_date и проверить, что последовательно
# line[i].actual_end_date + relativedelta(seconds=1) == line[i+1].start_date,
# до тех пор пока у очередной цены не будет actual_end_date == None
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase2(TestPrCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for k in range(4):
            cls.requisition_lines += cls.factory.create_requisition_lines(
                cls.products,
                cls.purchase_requisition,
                start_date=Datetime.today() + dt.timedelta(days=k),
            )

    def test_prices_order(self):
        all_lines = self.env['purchase.requisition.line'].search(
            [],
            order="start_date",
        )

        # проверим что все цены идут по порядку
        for product in self.products:
            lines = all_lines.filtered_domain([
                ('product_id', '=', product.id),
                ('requisition_id', '=', self.purchase_requisition.id),
            ])
            if len(lines) > 1:
                for i in range(1, len(lines)):
                    self.assertEqual(
                        lines[i - 1].actual_end_date + dt.timedelta(seconds=1),
                        lines[i].start_date
                    )


# добавление одинаковых цен на одинаковый промежуток (ok)
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase3(TestPrCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for k in range(4):
            cls.requisition_lines += cls.factory.create_requisition_lines(
                cls.products,
                cls.purchase_requisition,
                start_date=Datetime.today() + dt.timedelta(days=1),
            )

    def test_replace_prices(self):
        the_only_prices = self.factory.create_requisition_lines(
                self.products,
                self.purchase_requisition,
                start_date=Datetime.today() + dt.timedelta(days=1),
            )
        self.assertEqual(len(self.products), len(the_only_prices), 'Wrong number of prices')
        all_lines = self.env['purchase.requisition.line'].search(
            [('product_id', 'in', [product.id for product in self.products])],
            order="start_date",
        )
        self.assertEqual(set(the_only_prices), set(all_lines) - set(self.requisition_lines), 'There is wrong prices')


# добавление цены с поздним концом, проверить,
# что на новый промежуток времени изменилась цена (ok)
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase4(TestPrCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'
            ),
            add_lines=True,
        )

    def test_actual_end_date(self):
        lines = self.env['purchase.requisition.line'].search([('requisition_id', '=', self.purchase_requisition.id)])
        new_start_date = Datetime.today() + dt.timedelta(days=10)
        self.factory.create_requisition_lines(
            self.products,
            self.purchase_requisition,
            start_date=new_start_date,
        )
        for line in lines:
            self.assertEqual(
                line.actual_end_date,
                new_start_date - dt.timedelta(seconds=1)
            )


# добавление обычной цены в период промо цены, проверить
# обычная цена не добавилась (ok)
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase5(TestPrCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'
            ),
            add_lines=True,
        )

    def test_promo_prices(self):
        start_date = Datetime.today() + dt.timedelta(days=2)
        end_date = Datetime.today() + dt.timedelta(days=4)
        promo_lines = self.factory.create_requisition_lines(
            self.products,
            self.purchase_requisition,
            start_date=start_date,
            end_date=end_date
        )
        regular_lines = self.factory.create_requisition_lines(
            self.products,
            self.purchase_requisition,
            start_date=start_date,
        )
        for i in range(len(promo_lines)):
            # мы считаем, что цена заканчивается в конце дня, указанного, как
            # end_date, поэтому при проверке actual_end_date делаем замену
            self.assertEqual(
                promo_lines[i].actual_end_date,
                dt.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            )
            self.assertEqual(
                regular_lines[i].start_date,
                promo_lines[i].end_date + dt.timedelta(seconds=1)
            )


# добавление первой цены с началом в будущем, проверить,
# что дата начала изменилась на сегодня (ok)
@tagged('lavka', 'prices', 'test_pr_prices')
class TestPrCase6(TestPrCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_prices = cls.factory.create_requisition_lines(
            cls.products,
            cls.purchase_requisition,
            start_date=Datetime.today() + dt.timedelta(days=1),
        )

    def test_first_future_price(self):
        for line in self.first_prices:
            self.assertEqual(line.start_date, Datetime.today())

    # добавление второй цены задним числом
    # проверяем что конец новой цены подтягивается к началу первой существующей,
    # не перекрывая ее, без end_date и флага промо
    def test_past_prices(self):
        past_prices = self.factory.create_requisition_lines(
                self.products,
                self.purchase_requisition,
                start_date=Datetime.today() - dt.timedelta(days=10),
            )
        for line in past_prices:
            self.assertEqual(line.actual_end_date, Datetime.today() - relativedelta(seconds=1))
            self.assertFalse(line.promo)
            self.assertFalse(line.end_date)

        # проверяем, что не получится создать цену в прошлом, если на эту дату уже есть цена
        with self.assertRaises(exceptions.UserError) as context:
            self.requsition_lines = self.factory.create_requisition_lines(
                self.products,
                self.purchase_requisition,
                start_date=Datetime.today() - dt.timedelta(days=2),
            )
        self.assertTrue(
            'Start date can\'t be earlier than today if price for today already exists' in
            str(context.exception)
        )

