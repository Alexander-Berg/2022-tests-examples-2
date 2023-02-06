import datetime
import json
import logging
import os
import random
import string
from unittest.mock import patch
from uuid import uuid4
from common.client.wms import WMSConnector
from unittest import TestCase
from odoo import fields, models, exceptions
from collections import defaultdict
from freezegun import freeze_time
from odoo.tests import tagged

from odoo.addons.lavka.tests.backend.test_common import TestVeluationCommon
from odoo.addons.lavka.tests.backend.test_orders import Fixtures
from odoo.addons.lavka.tests.utils import save_xlsx_report, get_stock_loc
from odoo.tests.common import SavepointCase, tagged, Form

'''Для изолированного тестирования необходимо создать фабрику.
Фабрика для тестов: Фабричный шаблон заключается в добавлении дополнительной абстракции между созданием объекта и тем, где он используется. Это дает нам дополнительные возможности, для дальнейшего расширения в будущем.
Фабричный метод − это шаблон проектирования, используемый для создания общего интерфейса.
В нашем случае есть “общее место” в коде, которое используют все тесты, код, который можно поддерживать отдельно от кода самих тестов.
Для удобной поддержки, повторного использования и упрощения кода будем использовать Фабрику.
В нашем случае мы разделяем процесс создания тестов и процесс подготовки данных от WMS, чтобы обеспечить отдельно поддержку кода тестов от кода данных, подверженных изменению как со стороны самих данных, так и их формата.

Что мы заменяем и на что:
Заменяем создание в def setUpClass():
Order, logs, parents, данные для acceptance и для sale_stowage, warehouse, partner:

Они будут создаваться в соответствии со спецификацией последней версии в необходимом количестве, источник данных - либо json, как сейчас, либо данные можно сгенерить.

Т.е. создается шаблон, куда можно будет подставить количество получаемых объектов и их суть - реальные данные
или же тестовые, полученные с помощью специальной библиотеки, отвечающие определенным условиям и похожие на реальные.
В коде появляется новый уровень абстракции, шаблон, помогающий избежать повторяемости и захардкоденных моментов.

созданные методы:
 create_products
 create_wms_sale_order
 create_warehouse
 create_partner
 create_purchase_requisition
 create_purchase_order
 create_purchase_order_lines
 create_purchase_requisition_lines
 create_acceptance
 create_sale_stowage
 и тд

Использование:
 для создания склада делается вызов  cls.warehouses = cls.create_warehouses(qty=N)
 если нужно создать в локали, указать:  cls.warehouses = cls.create_warehouses(qty=1, geoTag='UK')
 создать N продуктов cls.products = cls.create_products(qty=N)

см. woody/addons/lavka/tests/fixtures/factory_backend/factory.about

как использовать
_________________
на примере acceptance

для самого теста создаются верхнеуровневые методы, создать_список_аксептансов
в этом методе в самой фабрике вызывается метод создания документа

template = self.create_doc_template('acceptance')[0]
и формируются и/или добавляются недостающие поля/атрибуты, например:

template.update(
 {
     'store_id': order.picking_type_id.warehouse_id.wms_id,
     'type': 'acceptance',
     'source': 'integration',
     'attr': attr,
     'required': required,
     'external_id': curr_external_id,
     'order_id': random.choice(warehouses).wms_id
 }
)

order.wms_id = template.get('order_id')
with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = {}, None
                with freeze_time('2021-03-15 12:00:00'):
                    self.env['wms_integration.order'].create_wms_order([template],
                     self.wms_connector, 'cursor_1')

именно добавлению и последующему корректному формированию полей необходимо уделить
 основное внимание, т к каждый документ возьмёт из джейсона только минимум полей,
 и, желательно, этот список сократить в будущем, формируя документ в фабрике
 на основании одного тимплейта. приемущество одного тимплейта в том, что при
 изменении api, нужно будет поменять/дополнить джейсон документа в одном месте
 для всех тестов.
'''

_logger = logging.getLogger(__name__)

FIXTURES_PATH = '/fixtures/factory_backend/'


def read_json_data(filename):
    _logger.debug('reading json')
    with open(f'{os.path.dirname(__file__)}{os.sep}{FIXTURES_PATH}{os.sep}{filename}.json',
              encoding='UTF-8') as wms_json:
        res_json = json.load(wms_json)
    return res_json


def _create_delta(transfer_lines, shipment_required):
    shipment_delta = defaultdict(int)
    for required in shipment_required:
        shipment_delta[required['product_id']] = required['result_count']
    return shipment_delta


def mocked_requests_for_order(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    fixtures = Fixtures()
    path = args[0].rsplit('/', 1)[1]
    if path == 'log':
        return MockResponse({"stocks_log": fixtures.order_log_data}, 200)
    return MockResponse(None, 404)


def mocked_path(*args, **kwargs):
    return args[1]


def rnd_str(string_length=1):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))


def rnd_mix(string_length=1):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(string_length))


def rnd_int(string_length=1):
    letters = string.digits
    return int(''.join(random.choice(letters) for _ in range(string_length)))


def rnd_float(maxn=1000):
    int_num = random.choice(range(100, maxn * 100))
    return round(float(int_num / 100), 2)


class FactoryCommon(models.AbstractModel):
    _name = 'factory_common'
    _description = 'Factory for WMS test'
    wms_connector = WMSConnector()
    data = read_json_data('data')
    data_by_type = {i['type']: i for i in data}
    logs = read_json_data('logs')

    def create_default_doc_template(self):
        return read_json_data('default')

    def create_doc_template(self, doc_type, fields=False, fields_data=False):
        template = self.create_default_doc_template()
        try:
            doc = self.data_by_type.get(doc_type)
        except:
            _logger.exception(msg="Document type is not defined.")
        template[0].update(
            {
                'type': doc_type,
                'approved': doc['approved'] if 'approved' in doc else None,
                'external_id': doc['external_id'] if 'external_id' in doc else rnd_mix(32),
                'order_id': doc['order_id'] if 'order_id' in doc else None,
                'signals': doc['signals'] if 'signals' in doc else None,
                'store_id': doc['store_id'] if 'store_id' in doc else None,
                'user_done': doc['user_done'] if 'user_done' in doc else None,
                'vars': doc['vars'] if 'vars' in doc else None,
                'doc_number': doc['doc_number'] if 'doc_number' in doc else None,
                'contractor': doc['contractor'] if 'contractor' in doc else None,
                'required': doc['required'] if 'required' in doc else None
            }
        )
        if fields:
            for field in fields:
                if fields_data:
                    data = fields_data.get(field)
                else:
                    data = f'{field}_tst_data'
                template[0].update({field: data})
        return template

    # orders.py transfer order: po->shipment(wh A)->acceptance(wh B)
    def create_acceptance_sample(self, obj, warehouses):
        required = []
        purchase_line_ids = []
        order = obj
        new_mark = uuid4().hex[:6]
        curr_external_id = f'{order.external_id}.{new_mark}'
        for line in order.order_line.filtered(lambda l: not l.mark):
            assert line.product_id.wms_id, f'{line.product_id.default_code} has no WMS ID'
            line.mark = new_mark
        for line in order.order_line:
            unit_qty = line.product_id.uom_id._compute_quantity(
                line.product_init_qty, self.env.ref('uom.product_uom_unit')
            )
            unit_price = line.product_id.uom_id._compute_price(
                line.price_unit, self.env.ref('uom.product_uom_unit')
            )
            wmsline = {'product_id': line.product_id.wms_id,
                       'count': int(unit_qty),
                       'result_count': int(unit_qty),
                       'price': str(unit_price),
                       'vat': str(line.price_tax)}
            purchase_line_ids.append({'id': line.id, 'qty': line.product_init_qty})
            required.append(wmsline)
        attr = {
            'doc_date': order.date_planned.strftime('%Y-%m-%d'),
            'contractor': order.partner_id.name,
            'request_id': curr_external_id,
            'contractor_id': f'{order.partner_id.external_id}',
            'request_type': 'purchase_order',
            'request_number': order.name,
            'doc_number': order.name
        }
        if order.partner_id.trust_acceptance:
            attr.update({'trust_code': f'{uuid4()}'})
        template = self.create_doc_template('acceptance')[0]
        template.update(
            {
                'store_id': order.picking_type_id.warehouse_id.wms_id,
                'type': 'acceptance',
                'source': 'integration',
                'attr': attr,
                'required': required,
                'external_id': curr_external_id,
                'order_id': random.choice(warehouses).wms_id
            }
        )
        order.wms_id = template.get('order_id')
        return order, template

    def create_sale_stowage_sample(self, obj):
        log_stowage = self.logs
        stw_template = self.create_doc_template('sale_stowage')[0]
        log_template = log_stowage[0]
        acc = obj
        log_list = []
        req = json.loads(acc.required)
        for r in req:
            log_template.update(
                {
                    'product_id': r['product_id'],
                    'delta_count': r['count'],
                    'quants': 1,
                    'shelf_type': 'store'
                }
            )
            log_list.append(log_template)
        acc_attr = json.loads(acc.attr)
        attr = {
            'doc_date': acc_attr['doc_date'],
            'contractor': acc_attr['contractor'],
            'complete': {},
            'doc_number': stw_template['doc_number'],
        }
        stw_template.update(
            {
                'order_id': f'order_id{rnd_mix(12)}',
                'store_id': acc.store_id,
                'parent': acc.order_id,
                'parent_id': acc.order_id,
                'type': 'sale_stowage',
                'attr': attr,
                'required': req,
            }
        )
        return log_list, stw_template

    def serialize(self, warehouses, obj, k):
        assert warehouses, 'Warehouse looks empty'
        if isinstance(obj, self.env['purchase.order'].__class__):
            order, acceptance_sample = self.create_acceptance_sample(obj, warehouses)
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = {}, None
                with freeze_time('2021-03-15 12:00:00'):
                    self.env['wms_integration.order'].create_wms_order([acceptance_sample], self.wms_connector,
                                                                       'cursor_1')
            return self.env['wms_integration.order'].search([('order_id', '=', order.wms_id)])
        elif isinstance(obj, self.env['wms_integration.order'].__class__):
            log_list, stw_template = self.create_sale_stowage_sample(obj)
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_list, None
                with freeze_time('2021-03-15 12:00:00'):
                    self.env['wms_integration.order'].create_wms_order([stw_template], self.wms_connector,
                                                                       cursor='cursor_1')

    def create_products(self, warehouses, qty, create_parents=False, fields=False, fields_data=False):
        _logger.debug('start creating product in factory')
        assert warehouses, 'Warehouse looks empty'
        products = []
        mapped_products = {}
        for i in range(qty):
            wms_id = f'{rnd_mix(20)}{i}'
            vals = {
                'name': f'test_product_{i}',
                'default_code': f'default_code_{i}',
                'type': 'product',
                'wms_id': wms_id,
                'wms_parent': wms_id,
            }
            if fields:
                for field in fields:
                    if fields_data:
                        data = fields_data.get(field)
                    else:
                        data = f'{field}_tst_data'
                    vals.update({field: data})
            mapped_products[wms_id] = vals
        if create_parents:
            prod_list = list(mapped_products.values())
            parent_rnd = random.choice(prod_list)
            children_rndlist = random.choices(prod_list, k=random.randrange(len(prod_list) - 1) + 1)
            products_with_parent = self.add_parent(parent_rnd, children_rndlist)
        for item in mapped_products.values():
            products += self.env['product.product'].create(item)
        _logger.debug('done')
        return products

    def create_wms_sale_order(self, qty, req_qty):
        products = self.create_products(req_qty)
        order_template = {
            'count': 6,
            'price': '2.00',
            'price_type': 'store',
            'price_unit': 1,
            'product_id': '',
            'result_count': 6,
            'sum': '12.00'
        }
        sale_docs = self.env['wms_integration.order']
        for i in range(qty):
            order_template.update(
                {
                    'store_id': f'test_store_id_{i}',
                    'order_id': f'test_order_id_{i}'
                }
            )
            req = order_template.get('required')
            for k in products:
                line = req
                line.update({'product_id': k.wms_id})
            self.env['wms_integration.order'].create_wms_order(order_template)
            sale_docs += sale_docs.search([('order_id', '=', order_template['order_id'])])
        return sale_docs

    def create_warehouses(self, qty, geoTag=False, fields=False, fields_data=False):
        """when GeoTag selected False we will produce Test Tag, otherwise will use passed for all warehouses"""
        _logger.debug('creating warehouse in factory')
        tag_template = [{
            'type': 'geo',
            'name': rnd_str(string_length=3),
        }, ]
        tag = self.env['stock.warehouse.tag'].create(tag_template)
        if geoTag:
            tag.update({'name': geoTag})
        warehouses = self.env['stock.warehouse']
        for i in range(qty):
            vals = {
                'name': f'test_warehouse_{i}',
                'code': f'code_{i}',
                'warehouse_tag_ids': tag,
                'wms_id': f'wms_id_{i}'
            }
            if fields:
                for j in range(len(fields)):
                    field = fields[j]
                    if fields_data:
                        data = fields_data[j]
                    else:
                        data = f'{field}_tst_data'
                    vals.update({field: data})
            warehouses += self.env['stock.warehouse'].create(vals)
        _logger.debug('done')
        return warehouses

    def add_parent(self, parent, *children):
        for child in children[0]:
            child.update({'wms_parent': parent['wms_id']})
        return children[0]

    def create_partner(self, fields=False, fields_data=False):
        partner = self.env['res.partner'].search([
            ('name', '=', 'Test Banana Republic')

        ])
        if not partner:
            partner = self.env['res.partner'].create({'name': 'Test Banana Republic'})
        if fields:
            for j in range(len(fields)):
                field = fields[j]
                if fields_data:
                    data = fields_data[j]
                else:
                    data = f'{field}_tst_data'
                partner.update({field: data})
        return partner

    def create_purchase_requisition(self, products, geo_tag, part_fields=False,
                                    part_fields_data=False, tax_id=False,
                                    add_lines=True):
        assert products, 'Products looks empty'
        partner = self.create_partner(fields=part_fields, fields_data=part_fields_data)
        purchase_requisition = self.env['purchase.requisition'].create(
            {
                'vendor_id': partner.id,
                'warehouse_tag_ids': geo_tag,
                'state': 'ongoing',
            }
        )
        if add_lines:
            self.create_requisition_lines(products, purchase_requisition, tax_id)
            purchase_requisition.action_in_progress()
        return purchase_requisition

    def create_requisition_lines(self, products, purchase_requisition, tax_id=None,
                                 start_date=None, end_date=None):
        requisition_lines = []
        if not start_date:
            # какая-то магия при использовании freeze_time в тестах,
            # если start_date присваивать значение по умаолчанию
            # то freee_time не работает
            start_date = fields.Datetime.today()
        for product in products:
            res = self.env['purchase.requisition.line'].create(
                {
                    'product_id': product.id,
                    'price_unit': rnd_float(),
                    'product_uom_id': product.uom_id.id,
                    'requisition_id': purchase_requisition.id,
                    'start_date': start_date,
                    'actual_end_date': end_date,
                    'tax_id': tax_id if tax_id else product.supplier_taxes_id.id,
                    'approve_tax': True,
                    'approve_price': True,
                    'active': True,
                    'product_code': f'{product.default_code}_vendor',
                    'product_name': f'{product.name}_vendor',
                    'qty_multiple': 1,
                },
            )
            existed_lines = self.env['purchase.requisition.line'].search([
                ('product_id', '=', product.id),
                ('requisition_id', '=', purchase_requisition.id),
                ],
                order='start_date'
            )
            # тут лайн создается под правами суперюзера, поэтому end_date приходится вставлять вручную
            if not existed_lines or start_date >= fields.Datetime.today():
                res.end_date = res.actual_end_date
            res._compute_approve()
            requisition_lines.append(res)
        return requisition_lines

    def create_purchase_order(self, products, purchase_requisition, warehouses, qty=1, fields=False, fields_data=False):
        # создаем заказ поставщику
        assert products, 'Products looks empty'
        assert purchase_requisition, 'Purchase requisition looks empty'
        assert warehouses, 'Warehouse looks empty'
        orders = []
        for i in range(qty):
            po_res = {
                'external_id': rnd_mix(10),
                'partner_id': purchase_requisition.vendor_id.id,
                'picking_type_id': random.choice(warehouses).in_type_id.id,
                'requisition_id': purchase_requisition.id,
            }
            if fields:
                for j in range(len(fields)):
                    field = fields[j]
                    if fields_data:
                        data = fields_data[j]
                    else:
                        data = f'{field}_tst_data'
                    po_res.update({field: data})
            po = self.env['purchase.order'].create(po_res)
            orders.append(po)
            purchase_line_vals = []
            req_lines = {i.product_id: i for i in purchase_requisition.line_ids}
            for product in products:
                req_line = req_lines[product]
                res_po_lines = {
                    'product_id': product.id,
                    'name': product.name,
                    'product_init_qty': rnd_int(2),
                    'product_qty': rnd_int(2),
                    'order_id': po.id,
                    'price_unit': req_line.price_unit,
                }
                purchase_line_vals.append(res_po_lines)
            self.env['purchase.order.line'].create(purchase_line_vals)
        return orders

    def _create_stocklog_based_order(self, tmpl_file_name, products, warehouses):

        docs = []

        template = read_json_data(tmpl_file_name)

        for i, wh in enumerate(warehouses):
            order_id = f'{wh.wms_id}_writeoff_{i}'
            doc_number = f'test_doc_number_{i}'
            _attr = {
                "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
                "doc_number": doc_number,
                "complete": {}
            }
            template.update({
                'attr': json.dumps(_attr),
                'store_id': wh.wms_id,
                'order_id': order_id,
                'created': fields.datetime.now(),
                'updated': fields.datetime.now(),
                'approved': fields.datetime.now(),
                'external_id': f'ext_{order_id}',
                'processing_status': 'new',
                'odoo_wh': wh.id,

            })
            new_req = []
            for prd in products:
                req_line = template.get('required')[0]
                delta_count = random.randrange(1, 20)
                _vars = req_line.get('vars')
                if tmpl_file_name == 'writeoff':
                    _reas = [
                        {
                            "c6bf1a4315424a6398bebcc438575405000200010001": {
                                "count": delta_count,
                                "reason_code": "TRASH_TTL"
                            }
                        }
                    ]
                    _wrt_of = [
                        {
                            order_id: [
                                {
                                    "count": delta_count,
                                    "order_id": "c6bf1a4315424a6398bebcc438575405000200010001",
                                    "reason_code": "TRASH_TTL"
                                }
                            ]
                        }
                    ]

                    _vars.update({
                        'reasons': _reas,
                        'write_off': _wrt_of,
                    })

                req_line.update({
                    'product_id': prd.wms_id,
                    'name': prd.name,
                    'odoo_product_id': prd.id,
                    'order_id': order_id,
                    'store_id': wh.wms_id,
                    'delta_count': delta_count,
                    'vars': _vars,
                })
                new_req.append(req_line)
            template.update({'required': json.dumps(new_req)})
            docs.append(self.env['wms_integration.order'].create(template))

            return docs

    def create_writeoff_list(self, products, warehouses):
        """
        создает по одному доку writeoff на каждвй склад,
        переданный в параметре
        """
        return self._create_stocklog_based_order(
            tmpl_file_name='writeoff',
            products=products,
            warehouses=warehouses
        )

    def create_check_product_on_shelf_list(self, products, warehouses):
        """
        создает простой check_product_on_shelf
        """
        return self._create_stocklog_based_order(
            tmpl_file_name='check_product_on_shelf',
            products=products,
            warehouses=warehouses
        )

    def create_acceptance_list(self, purchase_orders, warehouses):
        acceptance_list = []
        for iterate, po in enumerate(purchase_orders):
            acceptance = self.serialize(warehouses, po, iterate)
            acceptance_list.append(acceptance)
        return acceptance_list

    def create_sale_stowage_list(self, warehouses, acceptances, muliply=1):
        for k, acc in enumerate(acceptances):
            self.serialize(warehouses, acc, k)

    def get_docs_processing_list(self, doc_type):
        # вернет отдельно список переданного типа доков
        docs = {i.type: i for i in self.env['wms_integration.order'].search([])}
        doc_list = docs.get(doc_type)
        # обрабатываем док
        for doc_ in doc_list:
            doc_.post_processing(doc_)
        return doc_list

    def set_ok_doc_status(self, docs):
        for doc in docs:
            doc.processing_status = 'ok'
        return docs

    def create_tax(self, fields=False, fields_data=False):
        val = {
            'name': f'VAT 10 perc {rnd_str(string_length=3)}',
            'amount_type': 'percent',
            'amount': 10.0,
            # 'price_include': True,
            'oebs_tax_code': f'VAT_{rnd_str(string_length=5)}',
            'type_tax_use': 'sale'
        }
        if fields:
            for j in range(len(fields)):
                field = fields[j]
                if fields_data:
                    data = fields_data[j]
                else:
                    data = f'{field}_tst_data'
                val.update({field: data})
        tax = self.env['account.tax'].create(val)
        return tax

    def _create_transfer(self, params):
        self.transfer = self.env['transfer.lavka'].create(params)
        return self.transfer.id

    def _create_lines(self, products, transfer_id=None):
        if transfer_id is None:
            transfer_id = self.transfer.id
        lines = [
            {
                'transfer_id': transfer_id,
                'product_id': products[0].id,
                'qty_plan': 5,
            },
            {
                'transfer_id': transfer_id,
                'product_id': products[1].id,
                'qty_plan': 10,
            },
        ]
        self.env['transfer.lavka.line'].create(lines)

    def test_transfer_create_lines(self, warehouse_in, warehouse_out, products):
        params = {
            'warehouse_out': warehouse_out.id,
            'warehouse_in': warehouse_in.id,
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines(products)
        self.assertEqual(len(self.transfer.transfer_lines), 2, 'Длина совпала')

    def test_import_stocks_for_line(self, warehouse_in, warehouse_out, products):
        params = {
            'warehouse_out': warehouse_out.id,
            'warehouse_in': warehouse_in.id,
            'state': 'draft',
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines(products)

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = read_json_data(
                'fixtures/transfer_test/stocks.json'), None
            self.transfer.check_transfer_lines(self.transfer.state)

        self.assertEqual(len(self.transfer.transfer_lines), 2,
                         'Длина не изменилась')

        result_dict = {
            products[0].id: 5,
            products[1].id: 7,
        }

        from_transfer_lines = {
            line.product_id.id: line.qty_plan
            for line in self.transfer.transfer_lines
        }

        self.assertEqual(
            from_transfer_lines, result_dict,
            'значения изменились'
        )

    def test_import_stocks_all(self, warehouse_in, warehouse_out):
        params = {
            'warehouse_out': warehouse_out.id,
            'warehouse_in': warehouse_in.id,
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self.assertEqual(len(self.transfer.transfer_lines), 0,
                         'Линий нет')

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = _import_json(
                'fixtures/transfer_test/stocks.json'), None
            self.transfer.fill_transfer_lines_from_wms(self.transfer.state)

        self.assertEqual(len(self.transfer.transfer_lines), 4,
                         'Длина изменилась')

    def test_approve(self, warehouse_in, warehouse_out, products):
        params = {
            'warehouse_out': warehouse_out.id,
            'warehouse_in': warehouse_in.id,
            'source': 'user',
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines(products)

        self.assertEqual(self.transfer.source, 'user',
                         'source есть')
        self.assertEqual(self.transfer.state, 'draft',
                         'статус draft')

        self.transfer.button_approved()
        self.assertEqual(self.transfer.state, 'approved',
                         'статус approved')
        self.assertEqual(
            self.transfer.user_approved,
            self.env.user,
            'юзер проставлен'
        )

    def test_shipment(self, warehouse_in, warehouse_out, products):
        params = {
            'warehouse_out': warehouse_out.id,
            'warehouse_in': warehouse_in.id,
            'source': 'user',
            'date_planned': datetime.now(),
            'external_id': 'transf2343',
            'state': 'draft',
        }
        self._create_transfer(params)
        self._create_lines(products)

        with self.assertRaises(exceptions.UserError):
            self.transfer.button_send_shipment()

        self.transfer.state = 'approved'

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = {}
            get_wms_data_mock.return_value = data, None
            with self.assertRaises(exceptions.UserError):
                self.transfer.button_send_shipment()
        with patch('odoo.addons.lavka.models.backend.transfer.transfer.Transfer._get_products_by_stock') as _get_products_by_stock_mock:
            _get_products_by_stock_mock.return_value = {'126903': 10, '11909': 12}, \
                                                       {('126903', 'store'): 10, ('11909', 'store'): 12}
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                data = {'order_id': 'dd3bc1144ce545c48c104bf6646976b6000200010001'}
                get_wms_data_mock.return_value = data, None
                self.transfer.button_send_shipment()

        self.assertEqual(self.transfer.state, 'sent', 'статус изменился')
        self.assertEqual(self.transfer.shipment_id, data['order_id'],
                         'shipment_id появился')
