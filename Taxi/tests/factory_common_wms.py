import json
import logging
import os
import random
import string
import datetime as dt
from unittest.mock import patch
from uuid import uuid4
from common.client.wms import WMSConnector

from freezegun import freeze_time
from odoo import fields, models
from odoo.tests.common import SavepointCase, tagged, Form
from odoo.addons.lavka.backend.models.wms.wms_order import INTEGRATION_KEY
from common.config import cfg

'''для изолированного тестирования необходимо создать фабрику.
Фабрика для тестов: Фабричный шаблон заключается в добавлении дополнительной абстракции между созданием объекта и тем, где он используется. Это дает нам дополнительные возможности, для дальнейшего расширения в будущем.
Фабричный метод − это шаблон проектирования, используемый для создания общего интерфейса.
В нашем случае есть “общее место” в коде, которое используют все тесты, код, который можно поддерживать отдельно от кода самих тестов.
Для удобной поддержки, повторного использования и упрощения кода будем использовать Фабрику.
В нашем случае мы разделяем процесс создания тестов и процесс подготовки данных от WMS, чтобы обеспечить отдельно поддержку кода тестов от кода данных, подверженных изменению как со стороны самих данных, так и их формата.

Что мы заменяем и на что:
Заменяем создание в def setUpClass():
Order, logs, parents, данные для acceptance и для sale_stowage, warehouse, partner:

Они будут создаваться в соответствии со спецификацией последней версии в необходимом количестве, источник данных - либо json, как сейчас, либо данные можно сгенерить.

Т. е. создается шаблон, куда можно будет подставить количество получаемых объектов и их суть - реальные данные
или же тестовые, полученные с помощью специальной библиотеки, отвечающие определенным условиям и похожие на реальные.
В коде появляется новый уровень абстракции, шаблон, помогающий избежать повторяемости и захардкоденных моментов.

созданные методы:
 create_products
 create_wms_sale_order
 create_warehouse
 get_or_create_partner
 create_purchase_requisition
 create_purchase_order
 create_purchase_order_lines
 create_purchase_requisition_lines
 create_acceptance
 create_sale_stowage

Использование:
 для создания склада делается вызов  cls.warehouses = cls.create_warehouses(qty=N)
 если нужно создать в локали, указать:  cls.warehouses = cls.create_warehouses(qty=1, geoTag='UK')
 создать N продуктов cls.products = cls.create_products(qty=N)'''

_logger = logging.getLogger(__name__)

FIXTURES_PATH = '/fixtures/factory_backend/'
get_first_logs_by_stores = 'odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores'


def get_date_in_wms_format():
    created = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    created = f'{created}+00:00'
    return created


def read_json_data(filename):
    _logger.debug('reading json')
    with open(f'{os.path.dirname(__file__)}{os.sep}{FIXTURES_PATH}{os.sep}{filename}.json',
              encoding='UTF-8') as wms_json:
        res_json = json.load(wms_json)
    return res_json


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
    _name = 'factory_common_wms'
    _description = 'Factory for WMS test'
    wms_connector = WMSConnector()
    orders = read_json_data('orders')
    mapped_order_data = {i['type']: i for i in orders}

    acc = mapped_order_data.get('acceptance')
    stw = mapped_order_data.get('sale_stowage')
    stw.update({
        'created': dt.datetime.now(),
        'updated': dt.datetime.now(),
        'processing_info': INTEGRATION_KEY,
    })
    acc.update({
        'created': dt.datetime.now(),
        'updated': dt.datetime.now(),
        'processing_info': INTEGRATION_KEY,
    })
    logs = read_json_data('logs')
    for line in logs:
        line.update({
            'created': dt.datetime.now(),
        })

    order_template = read_json_data('check_product_on_shelf')
    order_template.update({
        'created': dt.datetime.now(),
        'updated': dt.datetime.now(),
        'processing_info': INTEGRATION_KEY,
    })
    parents = read_json_data('parents')

    def unlink_stess_test_param(self):
        p = self.env['ir.config_parameter'].search([
            ('key', '=', 'stress_test')
        ])
        if p:
            p.unlink()

    def confirm_po(self, pos):
        now = dt.datetime.now()
        mark = uuid4().hex[:6]
        for po in pos:
            for purchase_line in po.order_line:
                purchase_line.mark = mark
                purchase_line.product_qty = purchase_line.product_init_qty
                purchase_line.product_uom_qty = purchase_line.product_init_qty
                purchase_line.date_order = now

            po.state = 'purchase'
            pickings = po._create_picking_from_wms(po.order_line)
            for picking in pickings:
                picking.wms_id = po.wms_id
                self.env['wms_integration.order'].complete_picking(picking, now, po.wms_id)
            po.state = 'done'
        return pos

    def process_stock_logs(self, all_logs):
        log_data = self.prepare_logs(all_logs)
        logs = self.env['wms_stock_log'].create(log_data)
        for log_line in logs:
            with patch(get_first_logs_by_stores) as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)
                assert log_line.state == 'ok'
        return True

    def serialize(self, warehouses, obj, k, create_weight=False):
        assert warehouses, 'Warehouse looks empty'
        # создаем acceptance
        if isinstance(obj, self.env['purchase.order'].__class__):
            unit_required = []
            weight_required = []
            purchase_line_ids = []
            res_orders = []
            order = obj
            new_mark = uuid4().hex[:6]
            doc_number = f'{order.name}.{new_mark}'
            curr_external_id = f'{order.external_id}.{new_mark}'
            common_external_id = f'{order.external_id}'
            store_id = order.picking_type_id.warehouse_id.wms_id
            has_weight = 'weight' in order.order_line.mapped('product_id.type_accounting')
            for line in order.order_line.filtered(lambda l: not l.mark):
                assert line.product_id.wms_id, f'{line.product_id.default_code} has no WMS ID'
                unit_qty = line.product_id.uom_id._compute_quantity(
                    line.product_init_qty, self.env.ref('uom.product_uom_unit')
                )
                unit_price = line.product_id.uom_id._compute_price(
                    line.price_unit, self.env.ref('uom.product_uom_unit')
                )
                wmsline = {'product_id': line.product_id.wms_id,
                           'price': str(unit_price),
                           'vat': str(line.price_tax)}
                purchase_line_ids.append({'id': line.id, 'qty': line.product_init_qty})
                if line.product_id.type_accounting == 'unit':
                    wmsline['count'] = int(unit_qty)
                    unit_required.append(wmsline)
                    line.mark = f'{new_mark}.U'
                elif line.product_id.type_accounting == 'weight':
                    # переводим кг в граммы
                    wmsline['weight'] = int(unit_qty) * 1000
                    weight_required.append(wmsline)
                    line.mark = f'{new_mark}.W'
            if create_weight:
                reqs = [(weight_required, 'W'), (unit_required, 'U')]
            else:
                reqs = [(unit_required, 'U')]
            for req, acc_type in reqs:
                attr = {
                    'doc_date': order.date_planned.strftime('%Y-%m-%d'),
                    'contractor': order.partner_id.name,
                    'request_id': curr_external_id,
                    'contractor_id': f'{order.partner_id.external_id}',
                    'request_type': 'purchase_order',
                    'request_number': f'{order.name}-{acc_type}',
                    'doc_number': f'{doc_number}.{acc_type}'
                }
                _vars = {
                    'stowage_id': [
                        f'stw_id_{uuid4().hex}_{k}_{k}',
                        f'stw_id_{uuid4().hex}_{k}_{k + 1}'
                    ]
                }
                if order.partner_id.trust_acceptance and acc_type != 'W':
                    attr.update({'trust_code': f'{uuid4()}'})

                vals = {
                    'order_id': f'test_order_id_{uuid4().hex}_{k}.{acc_type}',
                    'store_id': order.picking_type_id.warehouse_id.wms_id,
                    'created': fields.datetime.now(),
                    'updated': fields.datetime.now(),
                    'approved': fields.datetime.now(),
                    'common_external_id': common_external_id,
                    'external_id': f'{curr_external_id}.{acc_type}',
                    'attr': json.dumps(attr),
                    'type': 'acceptance',
                    'source': 'integration',
                    'doc_number': f'{doc_number}.{acc_type}',
                    'status': 'complete',
                    'processing_status': 'new',
                    'odoo_wh': order.picking_type_id.warehouse_id.id,
                    'parent': [],
                    'required': json.dumps(req),
                    'request_type': 'purchase_order',
                    'vars': json.dumps(_vars),
                    'processing_info': INTEGRATION_KEY,
                }

                order.write({
                    'wms_id': vals.get('order_id'),
                    'state': 'purchase',
                })
                self.env['wms_integration.order'].create(vals)
                res_orders.append(order.wms_id)

            return self.env['wms_integration.order'].search([('order_id', 'in', res_orders)])
        elif isinstance(obj, self.env['wms_integration.order'].__class__):
            log_stowage = self.logs
            stw_template = self.stw
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
            stw_template.update(
                {
                    'order_id': f'order_id{rnd_mix(10)}--{k}',
                    'store_id': acc.store_id,
                    'parent': acc.order_id
                }
            )
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                get_wms_data_mock.return_value = log_list, None
                with freeze_time('2021-03-15 12:00:00'):
                    self.env['wms_integration.order'].create_wms_order([stw_template], self.wms_connector, 'cursor_1')

    def create_products(self, warehouses, qty, fields=False, fields_data=False, weight=False, **kw):
        _logger.debug('start creating product in factory')
        assert warehouses, 'Warehouse looks empty'
        products = self.env['product.product']
        tax = self.env['account.tax'].create({
            'name': 'Sale17',
            'amount': 17.0,
            'type_tax_use': 'sale',
            'oebs_tax_code': 'Sale17',

        })
        for i in range(qty):
            uid = uuid4().hex[:4]
            vals = {
                'name': f'test_product_{uid}',
                'default_code': f'default_code_{uid}',
                'type': 'product',
                'wms_id': f'wms_id_{uid}',
                'taxes_id': tax.id,
                'type_accounting': 'weight' if weight else 'unit',
                'barcode': f'barcode_{uid}',
            }
            if fields:
                for field in fields:
                    if fields_data:
                        data = fields_data.get(field)
                    else:
                        data = f'{field}_tst_data'
                    vals.update({field: data})
            products += self.env['product.product'].create(vals)
        _logger.debug('done')
        return products

    def create_products_with_parents(self, warehouses, qty, parent_qty, weight=False):
        _logger.debug('start creating product in factory')
        assert warehouses, 'Warehouse looks empty'
        assert parent_qty < qty, 'Parent qty > product qty'
        children = self.env['product.product']
        parents = self.env['product.product']
        tax = self.env['account.tax'].create([{
            'name': 'Sale17',
            'amount': 17.0,
            'type_tax_use': 'sale'

        }])
        for k in range(parent_qty):
            uid = uuid4().hex[:4]
            vals = {
                'name': f'test_parent_product_{uid}',
                'default_code': f'default_parent_code_{uid}',
                'type': 'product',
                'wms_id': f'parent_wms_id_{uid}',
                'taxes_id': tax.id,
                'type_accounting': 'weight' if weight else 'unit'
            }
            parents += self.env['product.product'].create(vals)
        p_list = [i for i in parents]
        pk = 0
        for i in range(1, qty + 1):
            uid = uuid4().hex[:4]
            vals = {
                'name': f'test_child_product_{uid}',
                'default_code': f'default_child_code_{uid}',
                'type': 'product',
                'wms_id': f'child_wms_id_{uid}',
                'taxes_id': tax.id,
                'type_accounting': 'weight' if weight else 'unit'
            }
            if pk > len(p_list) - 1:
                pk = 0
            parent = p_list[pk]
            vals.update({
                'wms_parent': parent.wms_id,
                'product_parent': parent.id,
            })
            if i % 2 == 0:
                pk += 1

            children += self.env['product.product'].create(vals)

        _logger.debug('done')
        return parents, children

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
            'name': 'test_tags',
        }, ]
        tag = self.env['stock.warehouse.tag'].search([('name', '=', 'test_tags')])
        if not tag:
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
                for field in fields:
                    if fields_data:
                        data = fields_data.get(field)
                    else:
                        data = f'{field}_tst_data'
                    vals.update({field: data})
            _code = f'code_{i}'
            w = self.env['stock.warehouse'].search([
                ('code', '=', _code)
            ])
            if not w:
                w = self.env['stock.warehouse'].create(vals)
            warehouses += w
        _logger.debug('done')
        return warehouses

    def add_parent(self, parent, *children):
        for child in children[0]:
            child[0].update({'wms_parent': parent[0].wms_id})
        return children[0]

    def get_or_create_partner(self, fields=False, fields_data=False):
        partner = self.env['res.partner'].search([
            ('name', '=', 'John Doe')
        ])
        if not partner:
            partner = self.env['res.partner'].create({'name': 'John Doe', 'vat': 'vat_123'})
        if fields:
            for field in fields:
                if fields_data:
                    data = fields_data.get(field)
                else:
                    data = f'{field}_tst_data'
                partner.update({field: data})
        return partner

    def create_bunch_purchase_requisition(self, products, geo_tag, create_parents=False):
        assert products, 'Products looks empty'
        partner = self.get_or_create_partner()
        purchase_requisitions = self.env['purchase.requisition']
        vals = []
        chunk = 100
        for i, product in enumerate(products):
            purchase_requisition = self.env['purchase.requisition'].create([{
                'vendor_id': partner.id,
                'warehouse_tag_ids': geo_tag,
                'state': 'ongoing'
            }])

            if product.wms_id != product.wms_parent:
                _logger.debug('skip childrens')
                continue

            vals.append({
                'product_id': product.id,
                'price_unit': rnd_float(),
                'product_uom_id': product.uom_id.id,
                'tax_id': product.supplier_taxes_id.id,
                'requisition_id': purchase_requisition.id,
                'approve_tax': True,
                'approve_price': True,
                'product_code': f'{product.default_code}_vendor',
                'product_name': f'{product.name}_vendor',
                'qty_multiple': 1,
            })
            if i % chunk == 0:
                self.env['purchase.requisition.line'].create(vals)
                vals = []
                _logger.debug(f'created: {i}')
                self.env['purchase.requisition.line'].create(vals)

                for r in purchase_requisition.line_ids:
                    r._compute_approve()
                purchase_requisitions += purchase_requisition

        self.env['purchase.requisition.line'].create(vals)
        purchase_requisitions += purchase_requisition

        _logger.debug('CREATED!')
        for r in purchase_requisition.line_ids:
            r._compute_approve()
        _logger.debug('APPROVED!')

        return purchase_requisitions

    def create_purchase_requisition(self, products, geo_tag, create_parents=False, force_create=False, taxes=False):
        assert products, 'Products looks empty'
        partner = self.get_or_create_partner()
        if not force_create:
            purchase_requisition = self.env['purchase.requisition'].search([
                ('vendor_id', '=', partner.id)
            ])
        else:
            purchase_requisition = None
        if not purchase_requisition:
            purchase_requisition = self.env['purchase.requisition'].create([{
                'vendor_id': partner.id,
                'warehouse_tag_ids': geo_tag,
                'state': 'ongoing',
                'name': uuid4().hex[:6]
            }])
        if taxes:
            taxes_id = taxes['purchase']
        else:
            taxes_id = self.env['account.tax'].search([
                ('type_tax_use', '=', 'purchase')
            ])[0]
        requisition_lines = []
        existing = {i.product_id: i for i in purchase_requisition.line_ids}
        vals = []
        chunk = 1000
        for i, product in enumerate(products):
            if product.id != product.product_parent.id:
                _logger.debug('skip childrens')
                continue
            if existing.get(product):
                continue

            vals.append({
                'product_id': product.id,
                'start_date': dt.datetime.now(),
                'price_unit': rnd_float(),
                'product_uom_id': product.uom_id.id,
                'tax_id': product.supplier_taxes_id.id if product.supplier_taxes_id else taxes_id.id,
                'requisition_id': purchase_requisition.id,
                'approve_tax': True,
                'approve_price': True,
                'product_code': f'{product.default_code}_vendor',
                'product_name': f'{product.name}_vendor',
                'qty_multiple': 1,
            })
            if i % chunk == 0:
                self.env['purchase.requisition.line'].create(vals)
                vals = []
                _logger.debug(f'created: {i}')
        self.env['purchase.requisition.line'].create(vals)
        _logger.debug('CREATED!')
        for r in purchase_requisition.line_ids:
            r._compute_approve()
        _logger.debug('APPROVED!')

        return purchase_requisition

    def create_purchase_order(self, products, purchase_requisition, warehouses, qty=1, fields=False, fields_data=False,
                              prd_qty=5):
        # создаем заказ поставщику
        assert purchase_requisition, 'Purchase requisition looks empty'
        if not products:
            products = [i.product_id for i in purchase_requisition.line_ids if i.approve][:prd_qty]
        assert products, 'Products looks empty'

        assert warehouses, 'Warehouse looks empty'
        orders = []
        for i in range(qty):
            po_res = {
                'external_id': uuid4().hex,
                'partner_id': purchase_requisition.vendor_id.id,
                'picking_type_id': random.choice(warehouses).in_type_id.id,
                'requisition_id': purchase_requisition.id,
            }
            if fields:
                for field in fields:
                    if fields_data:
                        data = fields_data.get(field)
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
                    'product_init_qty': random.randrange(1, 99),
                    'order_id': po.id,
                    # 'price_unit': rnd_float(),
                    'price_unit': req_line.price_unit,
                }
                purchase_line_vals.append(res_po_lines)
            self.env['purchase.order.line'].create(purchase_line_vals)
        return orders

    def create_acceptance_list(self, purchase_orders, warehouses, weight=False):
        acceptance_list = []
        for iterate, po in enumerate(purchase_orders):
            acceptance = self.serialize(warehouses, po, iterate, create_weight=weight)
            acceptance_list.extend(acceptance)
        return acceptance_list

    def create_tr_acceptance_list(self, purchase_orders, warehouses):
        acceptance_list = []
        for iterate, po in enumerate(purchase_orders):
            acceptance = self.serialize(warehouses, po, iterate)
            acceptance_list.extend(acceptance)
        return acceptance_list

    def create_sale_stowage_list(self, warehouses, acceptances, muliply=1):
        for k, acc in enumerate(acceptances):
            self.serialize(warehouses, acc, k)

    def get_sale_stowages_data_from_acceptance(self, acceptance, zero_qty=False):
        stw_wms_ids = json.loads(acceptance.vars)['stowage_id']
        assert stw_wms_ids, f'No stowage id in vars section of acceptance {acceptance.order}'
        # splt lines according stowages count
        req = json.loads(acceptance.required)
        chunk = len(req) // len(stw_wms_ids)
        counted_req = {}
        for i, line in enumerate(req):
            counted_req[i] = line
        stowages_data = []
        for k, stw_id in enumerate(stw_wms_ids):
            begin = k * chunk
            end = (k + 1) * chunk
            stw_template = self.stw.copy()
            log_stowage = self.logs

            log_list = []
            req = []
            for i in range(begin, end):
                if zero_qty:
                    continue
                log_template = log_stowage[0].copy()
                r = counted_req.get(i)
                if not r:
                    _logger.debug(f'Skip {i} line, no required line')

                log_weight = r.get('weight')
                if log_weight:
                    count = random.randint(1, 10)
                else:
                    count = r.get('count')

                req_extra_data = {
                    'product_id': r['product_id'],
                    'count': count,
                }
                if log_weight:
                    req_extra_data['weight'] = log_weight
                    log_template['order_type'] = 'weight_stowage'

                log_template.update(
                    {
                        'product_id': r['product_id'],
                        'store_id': acceptance.store_id,
                        'delta_count': count,
                        'vars': json.dumps({"weight": log_weight} if log_weight else {}),
                        'quants': 1,
                        'log_id': f'test_log_id_{acceptance.doc_number}_{uuid4().hex}',
                        'order_id': stw_id,
                        'shelf_type': 'store',
                        'created': get_date_in_wms_format(),
                    }
                )
                log_list.append(log_template)
                req.append(req_extra_data)
            stw_template.update(
                {
                    'order_id': stw_id,
                    'store_id': acceptance.store_id,
                    'parent': acceptance.order_id,
                    'required': json.dumps(req),
                    'processing_info': INTEGRATION_KEY,
                }
            )
            _line = (stw_template, log_list)
            stowages_data.append(_line)

        return stowages_data

    def prepare_logs(self, all_log_data):
        new_data = []
        for line in all_log_data:
            if line['delta_count'] == 0:
                continue
            new_data.append({
                'product_id': line['product_id'],
                'count': line['count'],
                'created': dt.datetime.now(),
                'delta_count': line['delta_count'],
                'log_id': line['log_id'],
                'type': line['type'],
                'order_id': line['order_id'],
                'order_type': line['order_type'],
                'quants': line['quants'],
                'shelf_id': line['shelf_id'],
                'shelf_type': line['shelf_type'],
                'store_id': line['store_id'],
                'vars': line['vars'],
            })
        return new_data

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

    def _create_stowage(self, vals, parent, count):

        template = read_json_data('sale_stowage')
        order_id = vals['order_id']
        doc_number = f'{parent.doc_number}-{count}'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        template.update({
            'order_id': order_id,
            'store_id': vals['store_id'],
            'external_id': f'{uuid4()}',
            'parent': json.dumps([parent.order_id]),
            'parent_id': parent.order_id,
            'attr': json.dumps(_attr),
            'type': 'sale_stowage',
            "doc_number": doc_number,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),

            'processing_status': 'new',
            'odoo_wh': self.env['stock.warehouse'].search([(
                'wms_id', '=', vals['store_id']
            )]).id,
            'required': vals['required'],
            'processing_info': INTEGRATION_KEY,

        })
        doc = self.env['wms_integration.order'].create([template])
        return doc

    def _create_weight_stowage(self, vals, parent, count):

        template = read_json_data('sale_stowage')
        order_id = vals['order_id']
        doc_number = f'{parent.doc_number}-{count}'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        template.update({
            'order_id': order_id,
            'store_id': vals['store_id'],
            'external_id': f'{uuid4()}',
            'parent': json.dumps([parent.order_id]),
            'parent_id': parent.order_id,
            'attr': json.dumps(_attr),
            'type': 'weight_stowage',
            "doc_number": doc_number,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),

            'processing_status': 'new',
            'odoo_wh': self.env['stock.warehouse'].search([(
                'wms_id', '=', vals['store_id']
            )]).id,
            'required': vals['required'],
            'processing_info': INTEGRATION_KEY,

        })
        doc = self.env['wms_integration.order'].create([template])
        parent_vars = json.loads(parent.vars)
        if not parent_vars or doc.order_id not in parent_vars.get('stowage_id', []):
            parent.vars = json.dumps(parent_vars.get('stowage_id', []).append(doc.order_id))
        return doc

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

    def get_docs_list(self):
        # вернет отдельно список доков acceptance и отдельно sale_stowage
        docs = {i.type: i for i in self.env['wms_integration.order'].search([])}
        docs_acc = docs.get('acceptance')
        docs_stw = docs.get('sale_stowage')
        return docs_acc, docs_stw

    def create_acceptance_from_po_lines(self, order_lines):
        required = []
        purchase_line_ids = []
        new_mark = uuid4().hex[:6]

        order = order_lines[0].order_id
        curr_external_id = f'{order.external_id}.{new_mark}'
        doc_number = f'{order.name}.{new_mark}'
        for line in order_lines:
            assert line.product_id.wms_id, f'{line.product_id.default_code} has no WMS ID'
            unit_qty = line.product_id.uom_id._compute_quantity(
                line.product_init_qty, self.env.ref('uom.product_uom_unit')
            )
            unit_price = line.product_id.uom_id._compute_price(
                line.price_unit, self.env.ref('uom.product_uom_unit')
            )
            wmsline = {'product_id': line.product_id.wms_id,
                       'count': int(unit_qty),
                       'price': str(unit_price),
                       'vat': str(line.price_tax)}
            purchase_line_ids.append({'id': line.id, 'qty': line.product_init_qty})
            required.append(wmsline)
            line.mark = new_mark
        attr = {
            'doc_date': order.date_planned.strftime('%Y-%m-%d'),
            'contractor': order.partner_id.name,
            'request_id': curr_external_id,
            'contractor_id': f'{order.partner_id.external_id}',
            'request_type': 'purchase_order',
            'request_number': order.name,
            'doc_number': doc_number
        }
        _vars = {
            'stowage_id': [f'stw_test_order_id_{new_mark}_1', f'stw_test_order_id_{new_mark}_2']
        }
        if order.partner_id.trust_acceptance:
            attr.update({'trust_code': f'{uuid4()}'})

        vals = {
            'order_id': f'acc_test_order_id_{new_mark}',
            'store_id': order.picking_type_id.warehouse_id.wms_id,
            'external_id': curr_external_id,
            'attr': json.dumps(attr),
            'type': 'acceptance',
            'doc_number': doc_number,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'processing_status': 'new',
            'odoo_wh': order.picking_type_id.warehouse_id.id,
            'parent': [],
            'source': 'integration',
            'required': json.dumps(required),
            'request_type': 'purchase_order',
            'vars': json.dumps(_vars),
            'processing_info': INTEGRATION_KEY,
        }
        wms_doc = self.env['wms_integration.order'].create([vals])
        for line in order_lines:
            line.mark = new_mark
        return wms_doc

    def create_stowage_from_data_set(self, stw_data_set, parent):
        j = 1
        wms_docs = []
        for stw_data, stw_log in stw_data_set:
            wms_doc = self._create_stowage(
                vals=stw_data,
                parent=parent,
                count=j
            )
            j += 1
            wms_docs.append((wms_doc, stw_log))

        return wms_docs

    def generate_stock_log(self, qty=100):
        log_list = []
        for i in range(qty):
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': uuid4().hex,
                    'store_id': uuid4().hex,
                    'delta_count': i,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': uuid4().hex,
                    'shelf_type': 'store',
                    'created': dt.datetime.now().isoformat()[:10],
                }
            )
            log_list.append(log_template)
        return log_list

    def get_get_checks_and_stock_log(self, wh, product, delta_count, dummy=False):
        """
        возвращает джсон для создания дока и стоклог
        """
        log_list = []
        log_template = self.logs[0].copy()
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f'check_{mark}'
        doc_number = f'doc_number_{mark}'
        order_type = 'check_product_on_shelf'
        store_id = wh.wms_id if not dummy else uuid4().hex
        wh_id = wh.id if not dummy else self.env['stock.warehouse'].search([]).id
        product_id = product.wms_id if not dummy else uuid4().hex

        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        template.update({
            'attr': json.dumps(_attr),
            'store_id': store_id,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh_id,
            'type': order_type,
            'required': [],
            'processing_info': INTEGRATION_KEY,
        })
        log_template.update(
            {
                'product_id': product_id,
                'store_id': store_id,
                'delta_count': delta_count,
                'quants': 1,
                'log_id': f'test_log_id_{uuid4().hex}',
                'order_id': order_id,
                'shelf_type': 'store',
                'order_type': order_type,
            }
        )
        log_list.append(log_template)
        return template, log_list

    def get_get_checks_on_order_and_stock_log(self, wh, product, acceptance, delta_count):
        """
        возвращает джсон для создания дока и стоклог с парентом
        """
        log_list = []
        parent = [acceptance.order_id]
        log_template = self.logs[0].copy()
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_type = 'check_product_on_shelf'
        order_id = f'check_{mark}'
        doc_number = f'doc_number_{mark}'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        template.update({
            'attr': json.dumps(_attr),
            'type': order_type,
            'store_id': wh.wms_id,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': [],
            'parent': json.dumps(parent),
            'processing_info': INTEGRATION_KEY,
        })
        log_template.update(
            {
                'product_id': product.wms_id,
                'store_id': wh.wms_id,
                'delta_count': delta_count,
                'quants': 1,
                'log_id': f'test_log_id_{uuid4().hex}',
                'order_id': order_id,
                'shelf_type': 'store',
                'order_type': order_type,
            }
        )
        log_list.append(log_template)
        return template, log_list

    def get_order_and_stock_log(self, wh, products, receipt, samples):
        """
        возвращает джсон для создания дока и стоклог с кухней и списанием
        """
        log_list = []

        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        order_type = 'order'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        req = []
        produced = receipt['product']
        for product in products:
            qty = random.randrange(1, 56)
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'order_type': order_type,
                    'store_id': wh.wms_id,
                    'delta_count': -1 * qty,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'store',
                    'created': get_date_in_wms_format(),
                    'type': 'sale',
                }
            )
            if product == produced:
                qty = -1
                log_template.update(
                    {
                        'delta_count': qty,
                        'shelf_type': 'kitchen_on_demand',
                    }
                )
            _pr = round(random.randrange(100, 9000) / 100, 2)
            _sum = _pr * qty
            ta = product.taxes_id.amount
            _vat = round(_sum * ta / 100, 2)
            req.append({
                'product_id': product.wms_id,
                'count': qty,
                'result_count': qty,
                'price': f'{_pr}',
                "price_type": "store",
                "price_unit": 1,
                "vat": f'{_vat}',
                "sum": f'{_sum}'
            })

            log_list.append(log_template)

        log_template = self.logs[0].copy()
        _vars = {'components': receipt['components']}
        log_template.update(
            {
                'product_id': produced.wms_id,
                'created': get_date_in_wms_format(),
                'order_type': order_type,
                'store_id': wh.wms_id,
                'delta_count': 1,
                'quants': 1,
                'log_id': f'test_log_id_{uuid4().hex}',
                'order_id': order_id,
                'shelf_type': 'kitchen_on_demand',
                'type': 'kitchen_produce',
                'vars': json.dumps(_vars),
            }
        )
        log_list.append(log_template)
        for ingr_list in receipt['components']:
            for ingr in ingr_list:
                log_template = self.logs[0].copy()
                log_template.update(
                    {
                        'product_id': ingr['product_id'],
                        'order_type': order_type,
                        'store_id': wh.wms_id,
                        'delta_count': -1 * ingr['count'],
                        'quants': ingr['quants'],
                        'log_id': f'test_log_id_{uuid4().hex}',
                        'order_id': order_id,
                        'shelf_type': 'kitchen_components',
                        'type': 'kitchen_consume',
                        'created': get_date_in_wms_format(),
                        'vars': {},
                    }
                )
                log_list.append(log_template)
        for sampl in samples:
            log_template = self.logs[0].copy()
            _vars = {
                "tags": [
                    "sampling"
                ],
            }
            log_template.update(
                {
                    'product_id': sampl.wms_id,
                    'order_type': order_type,
                    'store_id': wh.wms_id,
                    'delta_count': -1,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'store',
                    'type': 'sample',
                    'created': get_date_in_wms_format(),
                    'vars': json.dumps(_vars),
                }
            )
            log_list.append(log_template)

        template.update({
            'attr': json.dumps(_attr),
            'store_id': wh.wms_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': json.dumps(req),
            'processing_info': INTEGRATION_KEY,
        })

        return template, log_list

    def create_transfer(self, products, wh_in, wh_out):
        params = {
            'warehouse_out': wh_out.id,
            'warehouse_in': wh_in.id,
            'source': 'user',
            'date_planned': dt.datetime.now(),
            'external_id': uuid4().hex,
        }
        lines = []
        transfer = self.env['transfer.lavka'].create(params)
        for p in products:
            lines.append({
                'transfer_id': transfer.id,
                'product_id': p.id,
                'qty_plan': random.randrange(1, 150),
            })
        lines = self.env['transfer.lavka.line'].create(lines)
        return transfer

    def get_shipment_and_stock_log(self, transfer):
        log_list = []
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        store_id = transfer.warehouse_out.wms_id
        order_type = 'shipment'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {},
            'request_type': 'transfer',
            'request_number': transfer.name,
        }
        req = []

        for line in transfer.transfer_lines:
            product = line.product_id
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': store_id,
                    'count': line.qty_plan,
                    'delta_count': line.qty_plan,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'order_type': order_type,
                    'shelf_type': 'store',
                    'created': get_date_in_wms_format(),
                    'type': 'get',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': product.wms_id,
                'count': line.qty_plan,
                'result_count': line.qty_plan,
                'quants': 1,
            })

        template.update({
            'attr': json.dumps(_attr),
            'store_id': store_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': transfer.warehouse_out.id,
            'required': json.dumps(req),
            'parent': json.dumps([]),
            'processing_info': INTEGRATION_KEY,
        })
        return template, log_list

    def get_rollback_and_log(self, wms_doc, log, extra_products):
        log_list = []
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        store_id = wms_doc['store_id']
        order_type = 'shipment_rollback'
        parent = [wms_doc['order_id']]
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {},
            'request_type': 'transfer',
        }
        req = []

        for line in log[:2]:
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': line['product_id'],
                    'store_id': store_id,
                    'count': 2,
                    'delta_count': 2,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'order_type': order_type,
                    'shelf_type': 'store',
                    'created': get_date_in_wms_format(),
                    'type': 'put',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': line['product_id'],
                'count': 2,
                'result_count': 2,
                'quants': 1,
            })
        # добавляем экстра товар, которого не было в трансфере
        for prd in extra_products:
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': prd.wms_id,
                    'store_id': store_id,
                    'count': 2,
                    'delta_count': 2,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'order_type': order_type,
                    'shelf_type': 'store',
                    'created': get_date_in_wms_format(),
                    'type': 'put',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': prd.wms_id,
                'count': 2,
                'result_count': 2,
                'quants': 1,
            })

        template.update({
            'attr': json.dumps(_attr),
            'store_id': store_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wms_doc['odoo_wh'],
            'required': json.dumps(req),
            'parent': json.dumps(parent),
            'processing_info': INTEGRATION_KEY,
        })
        return template, log_list


    def get_acc_stw_and_stock_log_of_transfer(self, transfer):
        log_list = []
        mark1 = uuid4().hex
        mark2 = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        acc_order_id = f'order_{mark1}'
        stw_order_id = f'order_{mark2}'
        acc_doc_number = f'TR/{mark1}'
        stw_doc_number = f'TR/{mark2}'
        store_id = transfer.warehouse_out.wms_id
        acc_type = 'acceptance'
        stw_type = 'sale_stowage'

        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "complete": {},
            'request_type': 'transfer',
            'request_number': transfer.name,
        }
        acc_atr = _attr.copy()
        acc_atr["doc_number"] = acc_doc_number
        stw_atr = _attr.copy()
        stw_atr["doc_number"] = stw_doc_number
        req = []

        for line in transfer.transfer_lines:
            product = line.product_id
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': store_id,
                    'count': line.qty_plan,
                    'delta_count': line.qty_plan,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': stw_order_id,
                    'order_type': stw_type,
                    'shelf_type': 'store',
                    'type': 'pur',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': product.wms_id,
                'count': line.qty_plan,
                'result_count': line.qty_plan,
            })

        template.update({
            'attr': json.dumps(_attr),
            'store_id': store_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'processing_status': 'new',
            'odoo_wh': transfer.warehouse_out.id,
            'required': json.dumps(req),
            'parent': json.dumps([]),
            'processing_info': INTEGRATION_KEY,
        })
        acc_template = template.copy()
        acc_template.update({
            'type': acc_type,
            'order_id': acc_order_id,
            'external_id': f'ext_{acc_order_id}',
            'vars': json.dumps(
                {'stowage_id': [stw_order_id]}
            ),
            'doc_number': acc_doc_number,
            'attr': json.dumps(acc_atr),
            'processing_info': INTEGRATION_KEY,
        })
        stw_template = template.copy()
        stw_template.update({
            'type': stw_type,
            'order_id': stw_order_id,
            'external_id': f'ext_{stw_order_id}',
            'parent': json.dumps([acc_order_id]),
            'doc_number': stw_doc_number,
            'attr': json.dumps(stw_atr),
        })
        return acc_template, stw_template, log_list

    def get_refund_and_stock_log(self, wh, sale_order, excluded_products):
        log_list = []
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        order_type = 'part_refund'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        req = []

        for line in sale_order.order_line:
            product = line.product_id
            if product in excluded_products:
                continue
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'delta_count': line.product_uom_qty,
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'order_type': order_type,
                    'shelf_type': 'store',
                    'type': 'put',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': product.wms_id,
                'count': line.product_uom_qty,
                'result_count': line.product_uom_qty,
            })
        template.update({
            'attr': json.dumps(_attr),
            'store_id': wh.wms_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': json.dumps(req),
            'parent': json.dumps([sale_order.wms_id]),
            'processing_info': INTEGRATION_KEY,
        })
        return template, log_list

    def get_refund_and_stock_log_from_wms_order(self, wh, order, excluded_products):
        log_list = []
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        order_type = 'part_refund'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        req = []
        lines = json.loads(order.required)
        ids = [k['product_id'] for k in lines]
        prds = {i.wms_id: i for i in self.env['product.product'].search([
            ('wms_id', 'in', ids)
        ])}
        for line in json.loads(order.required):
            product = prds.get(line['product_id'])
            if product in excluded_products:
                continue
            log_template = self.logs[0].copy()
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'delta_count': line['count'],
                    'quants': 1,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'order_type': order_type,
                    'shelf_type': 'store',
                    'type': 'put',
                }
            )
            log_list.append(log_template)
            req.append({
                'product_id': product.wms_id,
                'count': line['count'],
                'result_count': line['result_count'],
            })
        template.update({
            'attr': json.dumps(_attr),
            'store_id': wh.wms_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': json.dumps(req),
            'parent': json.dumps([order.order_id]),
            'processing_info': INTEGRATION_KEY,
        })
        return template, log_list

    def get_writeoff_and_stock_log(self, wh, products):
        log_list = []
        mark = uuid4().hex
        template = read_json_data('check_product_on_shelf')
        order_id = f' order_{mark}'
        doc_number = f'doc_number_{mark}'
        order_type = 'writeoff'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        req = []

        for product in products:
            log_template = self.logs[0].copy()
            qty = random.randrange(1, 9)
            _vars = {
                "reasons": [
                    {
                        uuid4().hex: {
                            "count": 0,
                            "reason_code": "TRASH_DAMAGE",
                        }
                    }
                ],
                "write_off": [
                    {
                        uuid4().hex: [
                            {
                                "count": 2,
                                "reason_code": "TRASH_DAMAGE",
                                "order_id": f"some_{uuid4().hex}"
                            }
                        ]
                    },
                    {
                        uuid4().hex: [
                            {
                                "count": qty,
                                "reason_code": "TRASH_TTL",
                                "order_id": f"some_{uuid4().hex}"
                            }
                        ]
                    }
                ]
            }
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'delta_count': qty,
                    'quants': 10,
                    'log_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'kitchen_trash',
                    'type': 'write_off',
                    'order_type': order_type,
                    'vars': json.dumps(_vars),
                }
            )
            log_list.append(log_template)

        template.update({
            'attr': json.dumps(_attr),
            'store_id': wh.wms_id,
            'type': order_type,
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': json.dumps(req),
            'processing_info': INTEGRATION_KEY,
        })
        return template, log_list

    def get_inv_check_template(self, wh, parent_id, order_type='inventory_check_product_on_shelf'):

        template = self.order_template.copy()
        order_type = 'inventory_check_product_on_shelf'
        order_id = f'invcpos_{uuid4().hex}'
        doc_number = f'inv_check_{order_id}'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
            "complete": {}
        }
        template.update({
            'attr': json.dumps(_attr),
            'type': order_type,
            'store_id': wh.wms_id,
            'order_id': order_id,
            'created': fields.datetime.now() + dt.timedelta(hours=1),
            'updated': fields.datetime.now() + dt.timedelta(hours=1),
            'approved': fields.datetime.now() + dt.timedelta(hours=1),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': [],
            'parent': json.dumps([parent_id]),
            'parent_id': parent_id,
            'processing_info': INTEGRATION_KEY,
        })

        return template

    def get_inv_and_snapshots(self, wh, extra_products, stocks):
        snapshot_list = []
        mark = uuid4().hex
        template = self.order_template.copy()
        snapshot_template = read_json_data('snapshot')
        snapshot_template.update({
            'created': dt.datetime.now(),
            'updated': dt.datetime.now(),
        })
        order_id = f' inv_{mark}'
        doc_number = f'doc_number_{mark}'
        oder_type = 'inventory_check_product_on_shelf'
        _attr = {
            "doc_date": fields.datetime.now().strftime('%Y-%m-%d'),
            "doc_number": doc_number,
        }
        req = []

        inv_check_1 = self.get_inv_check_template(wh, order_id)
        inv_check_2 = self.get_inv_check_template(wh, order_id)
        inv_check_more_1 = self.get_inv_check_template(wh, order_id, order_type='inventory_check_more')
        inv_check_more_2 = self.get_inv_check_template(wh, order_id, order_type='inventory_check_more')
        inv_check_1_log = []
        inv_check_2_log = []
        k = 1
        for product, qty in stocks.items():
            log_template = self.logs[0].copy()
            _snapshot_template = snapshot_template.copy()
            _snapshot_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    # колво ПЛАН в wms  отличается от того, которое в вуди на 5 в большую
                    'count': qty + 5,  # 7
                    'quants': 1,
                    'record_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'store',
                    # колво ФАКТ на 2 меньше, (не достает 2 штук)
                    # эти две штуки с квантом в 1000 типа лежат в кухне
                    'result_count': qty + 3  # 5
                }
            )
            delta_count = 3 - 5
            log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'delta_count': delta_count,
                    'quants': 1,
                    'log_id': f'inv_check_log_id_{uuid4().hex}',
                    'shelf_type': 'store',
                    'order_type': oder_type,
                }
            )
            snapshot_list.append(_snapshot_template)

            # kitchen
            k_snapshot_template = snapshot_template.copy()
            k_log_template = self.logs[0].copy()
            k_snapshot_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'count': 2000,
                    'quants': 1000,
                    'record_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'kitchen_components',
                    # но часть куда-то дели
                    'result_count': 1806
                }
            )
            snapshot_list.append(k_snapshot_template)
            k_delta_count = 1806 - 2000
            k_log_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'delta_count': k_delta_count,
                    'quants': 1000,
                    'log_id': f'inv_check_log_id_{uuid4().hex}',
                    'shelf_type': 'kitchen_components',
                    'order_type': oder_type,
                }
            )
            if k < 5:
                log_template.update({
                    'order_id': inv_check_1['order_id'],
                })
                k_log_template.update({
                    'order_id': inv_check_1['order_id'],
                })
                inv_check_1_log.append(log_template)
                inv_check_1_log.append(k_log_template)
            else:
                log_template.update({
                    'order_id': inv_check_2['order_id'],
                })
                k_log_template.update({
                    'order_id': inv_check_2['order_id'],
                })
                inv_check_2_log.append(log_template)
                inv_check_2_log.append(k_log_template)

            k += 1
        # экстра продукты (нет в вуди)
        for product in extra_products:
            e_log_template = self.logs[0].copy()
            _snapshot_template = snapshot_template.copy()
            _snapshot_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'count': None,
                    'quants': 1,
                    'record_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'store',
                    'result_count': 50,
                }
            )
            snapshot_list.append(_snapshot_template)
            # добавим во второй чек
            e_log_template.update(
                {
                    'product_id': product.wms_id,
                    'order_id': inv_check_2['order_id'],
                    'store_id': wh.wms_id,
                    'delta_count': 50,
                    'quants': 1,
                    'log_id': f'inv_check_log_id_{uuid4().hex}',
                    'shelf_type': 'store',
                    'order_type': oder_type,
                }
            )
            inv_check_2_log.append(e_log_template)
            # kitchen
            k_snapshot_template = snapshot_template.copy()
            ek_log_template = self.logs[0].copy()
            k_snapshot_template.update(
                {
                    'product_id': product.wms_id,
                    'store_id': wh.wms_id,
                    'count': None,
                    'quants': 1500,
                    'record_id': f'test_log_id_{uuid4().hex}',
                    'order_id': order_id,
                    'shelf_type': 'kitchen_components',
                    'result_count': 2117,
                    'order_type': oder_type,
                }
            )
            snapshot_list.append(k_snapshot_template)
            # добавим в первый чек
            ek_log_template.update(
                {
                    'product_id': product.wms_id,
                    'order_id': inv_check_1['order_id'],
                    'store_id': wh.wms_id,
                    'delta_count': 2117,
                    'quants': 1500,
                    'log_id': f'inv_check_log_id_{uuid4().hex}',
                    'shelf_type': 'kitchen_components',
                    'order_type': 'inventory_check_product_on_shelf',
                }
            )
            inv_check_1_log.append(ek_log_template)

        _vars = {
            'shelf_types': ['store', 'markdown'],
            'child_orders': [
                inv_check_1['order_id'],
                inv_check_2['order_id'],
                # еще есть ids слепого пересчета, которые не создают логов
                inv_check_more_1['order_id'],
                inv_check_more_2['order_id'],
            ],
            'third_party_assistance': False,
        }

        template.update({
            'attr': json.dumps(_attr),
            'store_id': wh.wms_id,
            'type': 'inventory',
            'order_id': order_id,
            'created': fields.datetime.now(),
            'updated': fields.datetime.now(),
            'approved': fields.datetime.now(),
            'external_id': f'ext_{order_id}',
            'processing_status': 'new',
            'odoo_wh': wh.id,
            'required': json.dumps(req),
            'vars': json.dumps(_vars),
        })
        # в начальном снапшоте нет экстра товаров
        snapshot_plan = [i for i in snapshot_list if i['count']]
        checks_data = [
            (inv_check_1, inv_check_1_log),
            (inv_check_2, inv_check_2_log),
            (inv_check_more_1, []),
            (inv_check_more_2, []),
        ]
        return template, snapshot_plan, snapshot_list, checks_data

    def get_sale_stowages_data_with_children(self, acceptance, parents_p, children_p):
        stw_wms_ids = json.loads(acceptance.vars)['stowage_id']
        assert stw_wms_ids, f'No stowage id in vars section of acceptance {acceptance.order}'
        # splt lines according stowages count
        order_type = 'sale_stowage'
        stowages_data = []
        req = json.loads(acceptance.required)
        chunk = len(req) // len(stw_wms_ids)
        counted_req = {}
        for i, line in enumerate(req):
            counted_req[i] = line
        parent_with_childs = {}
        for p in parents_p:
            children_ids = []
            for c in children_p:
                if c.wms_parent == p.wms_id:
                    children_ids.append(c.wms_id)
            parent_with_childs[p.wms_id] = children_ids

        for k, stw_id in enumerate(stw_wms_ids):
            begin = k * chunk
            end = (k + 1) * chunk
            stw_template = self.stw.copy()
            log_stowage = self.logs

            log_list = []
            req = []
            for i in range(begin, end):
                r = counted_req.get(i)
                if not r:
                    _logger.debug(f'Skip {i} line, no required line')

                parent_weight = r.get('weight')
                child_weight = None
                if parent_weight:
                    child_weight = parent_weight / len(parent_with_childs[r['product_id']])
                    count = random.randint(1, 10)
                    while count == child_weight / 1000:
                        count = random.randint(1, 10)
                else:
                    count = round(r.get('count') // 2, 0)

                p_id = r['product_id']
                childs = parent_with_childs.get(p_id)
                for c_id in childs:
                    log_template = log_stowage[0].copy()

                    req_extra_data = {
                        'product_id': c_id,
                        'count': count,
                    }

                    log_template.update(
                        {
                            'product_id': c_id,
                            'store_id': acceptance.store_id,
                            'delta_count': count,
                            'vars': json.dumps({"weight": child_weight} if child_weight else {}),
                            'quants': 1,
                            'log_id': f'test_log_id_{acceptance.doc_number}_{uuid4().hex}',
                            'order_id': stw_id,
                            'shelf_type': 'store',
                            'order_type': order_type,
                            'created': get_date_in_wms_format(),
                        }
                    )

                    if child_weight:
                        req_extra_data['weight'] = child_weight
                        log_template['order_type'] = 'weight_stowage'

                    log_list.append(log_template)
                    req.append(req_extra_data)
            stw_template.update(
                {
                    'order_id': stw_id,
                    'type': order_type,
                    'store_id': acceptance.store_id,
                    'parent': acceptance.order_id,
                    'required': json.dumps(req),
                    'processing_info': INTEGRATION_KEY,
                }
            )
            _line = (stw_template, log_list)
            stowages_data.append(_line)

        return stowages_data

    def finalize_req(self, tax_sale, e_tag):
        all_products = self.env['product.product'].search([
            ('taxes_id', '=', False)
        ])
        for product in all_products:
            product.taxes_id = tax_sale[0]
            product.product_tmpl_id.sudo().tax_validate()
        for req in self.env['purchase.requisition'].search([]):
            req.warehouse_tag_ids += e_tag

    def prepare_tax_reqs_for_existing_products(self):

        tax_sale = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale')
        ])
        assert tax_sale
        tax_purchase = self.env['account.tax'].search([
            ('type_tax_use', '=', 'purchase')
        ])
        assert tax_purchase
        tag_template = [{
            'type': 'geo',
            'name': 'test',
        }]
        e_tag = self.env['stock.warehouse.tag'].search([
            ('name', '=', 'test')
        ])
        if not e_tag:
            e_tag = self.env['stock.warehouse.tag'].create(tag_template)
        _reqs = self.env['purchase.requisition.line'].search([
            ('approve', '=', True),
            ('requisition_id.state', '=', 'ongoing')
        ])
        p_with_prices = _reqs.mapped('product_id.id')

        products = self.env['product.product'].search([
            ('id', 'not in', p_with_prices)
        ], limit=3000)
        products.set_self_parent()
        self.env['product.product'].check_virtual_parent(products)

        if not products:
            self.finalize_req(tax_sale, e_tag)
            return
        taxes = {
            'sale': tax_sale[0],
            'purchase': tax_purchase[0]
        }
        reqs = self.create_purchase_requisition(
            products=products,
            geo_tag=e_tag,
            force_create=True,
            taxes=taxes,
        )
        for w in self.env['stock.warehouse'].search([]):
            w.warehouse_tag_ids = e_tag

        self.finalize_req(tax_sale, e_tag)
