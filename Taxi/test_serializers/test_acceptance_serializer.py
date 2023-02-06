import logging
import json
import random
from collections import defaultdict
from unittest.mock import patch
from uuid import uuid4

from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
from odoo.tests.common import Form
from common.config import cfg
from random import randrange
_logger = logging.getLogger(__name__)


@tagged('lavka', 'serializers', 's_acc')
class TestAcceptanceSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.weight_parent_products, cls.weight_products = cls.factory.create_products_with_parents(
            cls.warehouses, qty=4, parent_qty=2, weight=True
        )
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products + cls.weight_parent_products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.purchased_products = cls.products[:5]
        cls.extra_products = cls.products[5:8]
        cls.po = cls.factory.create_purchase_order(cls.purchased_products, cls.purchase_requisition, cls.warehouses, qty=4)
        cls.weight_po = cls.factory.create_purchase_order(cls.weight_parent_products, cls.purchase_requisition, cls.warehouses, qty=2)
        cls.acc = cls.factory.create_acceptance_list(cls.po, cls.warehouses)
        cls.weight_accs = cls.factory.create_acceptance_list(cls.weight_po, cls.warehouses, weight=True)
        cls.weight_acc = [i for i in cls.weight_accs if i.order_id.endswith('.W')][0]
        # отмененный в вмс ацептанс
        cls.canceled_acc = cls.acc[0]
        cls.canceled_acc.status = 'canceled'
        zqa = cls.acc[1]
        # обычный ацептанс
        cls.normal_acc = cls.acc[2]
        # принято с нулевым колвом
        zero_qty_acc_req = json.loads(cls.acc[1].required)
        new_req = []
        for line in zero_qty_acc_req:
            line.update({
                'result_count': 0
            })
            new_req.append(line)
        _vars = json.loads(zqa.vars)
        del _vars['stowage_id']
        cls.zqa = zqa
        cls.zqa.required = json.dumps(new_req)
        cls.zqa.vars = json.dumps(_vars)
        cls.env['ir.config_parameter'].set_param('sleep', 'false')

        # cls.stws = cls.factory.create_sale_stowage_list(cls.warehouses, [cls.normal_acc])

    def test_acceptance_canceled_serialize(self):
        """
        обработка отмененного ацептанса
        должна создасться таска на отмену
        """
        self.env['wms_integration.order'].post_processing(self.canceled_acc, 'TEST')
        po = self.env['purchase.order'].search([('external_id', '=', self.canceled_acc.common_external_id)])
        task = self.env['queue.job'].search([
            ('identity_key', '!=', 'reborn_jobs')
        ])
        self.assertEqual(po.state, 'cancel')

    def test_acceptance_zero_qty_serialize(self):
        """
        Если при приемке ацептанса проставили в result_count нулевое колво,
        то стоваджи не сгенерятся, надо переводить заказ поставщика в статус done,
        что, конечно, суперлогично (с)
        """
        self.env['wms_integration.order'].post_processing(self.zqa, 'TEST', test=True)
        for po in self.po:
            if po.external_id == self.zqa.common_external_id:
                self.assertEqual(po.state, 'done')
        # повторно
        self.env['wms_integration.order'].post_processing(self.zqa, 'TEST', test=True)
        for po in self.po:
            if po.external_id == self.zqa.common_external_id:
                self.assertEqual(po.state, 'done')

    def test_acceptance_complete_before_stw_serialize(self):
        """
        нормальный флоу, когда обрабатывается ацептанс до стоваджей,
        должен измениться статус заказа поставщику с драфта на purchase
        и должны сгенериться пикинги для каждого стоваджа
        """
        self.env['wms_integration.order'].post_processing(self.normal_acc, 'TEST', test=True)
        for po in self.po:
            if po.external_id == self.normal_acc.common_external_id:
                self.assertEqual(po.state, 'purchase')
                stowage_ids = json.loads(self.normal_acc.vars)['stowage_id']
                pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
                self.assertEqual(len(pickings), len(json.loads(self.normal_acc.vars).get('stowage_id')))
                self.assertEqual(po.state, 'purchase')

    def test_weight_stowage_diffs(self):
        self.env['wms_integration.order'].post_processing(self.weight_acc, 'TEST', test=True)
        po = [po for po in self.weight_po if self.weight_acc.common_external_id.startswith(po.external_id)][0]
        self.assertEqual(po.state, 'purchase')
        stw_data_set = self.factory.get_sale_stowages_data_with_children(
            self.weight_acc, self.weight_parent_products, self.weight_products
        )
        stowage_ids = json.loads(self.weight_acc.vars)['stowage_id']
        pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(len(stw_data_set), len(stowage_ids))
        j = 1
        wms_docs = []
        all_logs = []
        for stw_data, stw_log in stw_data_set:
            all_logs += stw_log
            wms_doc = self.factory._create_weight_stowage(
                vals=stw_data,
                parent=self.weight_acc,
                count=j
            )
            j += 1

            wms_doc.post_processing(wms_doc, 'TEST', test=True)
            wms_docs.append((wms_doc, stw_log))
        self.factory.process_stock_logs(all_logs)
        for po_line in po.order_line:
            po_line.product_init_qty += 2
            po_line.product_orig_qty += 2

        po.set_skip_checks()
        po.action_create_invoice()

        bill = po.invoice_ids
        bill.payment_reference = '123'
        bill_form = Form(bill)
        # меняем quantity через форму, чтобы корректно пересчитался итог
        for i, _ in enumerate(bill.invoice_line_ids):
            with bill_form.invoice_line_ids.edit(i) as line_form:
                line_form.quantity = line_form.qty_purchase_received
                line_form.save()
        bill_form.save()
        bill.action_post()

        parent_svl = self.env['stock.valuation.layer'].search([
            ('product_id', 'in', self.weight_parent_products.ids)
        ])
        children_svl = self.env['stock.valuation.layer'].search([
            ('product_id', 'in', self.weight_products.ids)
        ])
        invoiced_by_parents = defaultdict(float)
        for child in self.weight_products:
            c_svls = children_svl.filtered(lambda i: i.product_id.id == child.id)
            self.assertEqual(len(c_svls), 6)
            invoice_svl = c_svls.filtered(
                lambda i: i.transaction_system_name == 'RECLASS_IN_INVOICE_OPER'
            )
            st_svl = c_svls.filtered(
                lambda i: i.transaction_system_name == 'ST_RECLASS_IN_PROD'
            )
            accr_svl = c_svls.filtered(
                lambda i: i.transaction_system_name == 'RECLASS_IN_ACCR_OPER'
            )
            self.assertEqual(round(st_svl.value, 2), round(accr_svl.value, 2))
            self.assertTrue(invoice_svl.value > accr_svl.value)
            invoiced_by_parents[child.product_parent] += round(invoice_svl.value, 2)
        for parent in self.weight_parent_products:
            # svls = parent_svl.filtered(lambda i: i.product_id.id == parent.id)
            p_agg_svls = self.env['stock.valuation.layer'].read_group(
                [('product_id', 'in', parent.ids)],
                ['quantity:sum', 'value:sum', 'unit_cost:min'],
                ['transaction_system_name']
            )
            p_mapped_svls = {i['transaction_system_name']: i for i in p_agg_svls}
            quantity_sum = sum([i['quantity'] for i in p_agg_svls])
            self.assertEqual(quantity_sum, abs(p_agg_svls[0]['quantity']))
            self.assertEqual(
                p_mapped_svls['P_INVOICE']['value'],
                p_mapped_svls['RECLASS_OUT_INVOICE_PROD']['value']
            )
            self.assertEqual(
                sum([
                    p_mapped_svls['P_ACCR']['value'],
                    p_mapped_svls['RECLASS_OUT_ACCR_OPER']['value'],
                ]),
                sum([
                    p_mapped_svls['ST_ACCR']['value'],
                    p_mapped_svls['ST_RECLASS_OUT_OPER']['value'],
                ]),
            )
            self.assertEqual(
                sum([
                    p_mapped_svls['RECLASS_OUT_ACCR_PROD']['value'],
                    p_mapped_svls['RECLASS_OUT_ACCR_OPER']['value'],
                ]),
                0
            )
            self.assertEqual(
                sum([
                    p_mapped_svls['ST_RECLASS_OUT_PROD']['value'],
                    p_mapped_svls['ST_RECLASS_OUT_OPER']['value'],
                ]),
                0
            )
            self.assertEqual(
                sum([
                    p_mapped_svls['RECLASS_OUT_ACCR_PROD']['value'],
                    p_mapped_svls['RECLASS_OUT_ACCR_OPER']['value'],
                ]),
                0
            )
            self.assertEqual(
                invoiced_by_parents.get(parent),
                p_mapped_svls['P_INVOICE']['value']
            )

    def test_weight_stowage(self):
        self.env['wms_integration.order'].post_processing(self.weight_acc, 'TEST', test=True)
        po = [po for po in self.weight_po if self.weight_acc.common_external_id.startswith(po.external_id)][0]
        self.assertEqual(po.state, 'purchase')
        stw_data_set = self.factory.get_sale_stowages_data_with_children(
            self.weight_acc, self.weight_parent_products, self.weight_products
        )
        stowage_ids = json.loads(self.weight_acc.vars)['stowage_id']
        pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(len(stw_data_set), len(stowage_ids))
        j = 1
        wms_docs = []
        all_logs = []
        for stw_data, stw_log in stw_data_set:
            all_logs += stw_log
            wms_doc = self.factory._create_weight_stowage(
                vals=stw_data,
                parent=self.weight_acc,
                count=j
            )
            j += 1

            wms_doc.post_processing(wms_doc, 'TEST', test=True)
            wms_docs.append((wms_doc, stw_log))
        self.factory.process_stock_logs(all_logs)
        mapped_moves = defaultdict(dict)
        for picking in pickings:
            for move in picking.move_lines:
                if move.log_id.endswith('_in'):
                    mapped_moves[move.log_id[:-3]]['in'] = move
                elif move.log_id.endswith('_prod'):
                    mapped_moves[move.log_id[:-5]]['to_prod'] = move
                else:
                    mapped_moves[move.log_id]['to_oper'] = move
        for moves in mapped_moves.values():
            _in = moves['in']
            to_prod = moves['to_prod']
            to_oper = moves['to_oper']
            self.assertEqual(_in.product_qty, to_prod.product_qty)
            self.assertAlmostEqual(
                round(_in.price_unit, 2),
                round(to_prod.price_unit, 2),
                delta=0.02,
            )
            self.assertEqual(_in.note, to_prod.note)
            note_in = json.loads(_in.note)
            note_to_oper = json.loads(to_oper.note)
            delta_count = note_in.get('delta_count')
            child_wms_id = note_in.get('child_wms_id')
            weight = note_to_oper.get('weight')
            self.assertEqual(_in.product_qty, to_prod.product_qty)
            self.assertAlmostEqual(
                to_prod.product_qty,
                weight / 1000,
                delta=0.001
            )
            self.assertTrue(_in.product_id == to_prod.product_id == to_oper.product_id.product_parent)
            self.assertEqual(to_oper.product_qty, delta_count)
            self.assertEqual(to_oper.product_id.wms_id, child_wms_id)
            self.assertAlmostEqual(
                round(_in.product_qty * _in.price_unit, 2),
                round(to_prod.product_qty * to_prod.price_unit, 2),
                delta=0.02,
            )
            self.assertAlmostEqual(
                round(_in.product_qty * _in.price_unit, 2),
                round(to_oper.product_qty * to_oper.price_unit, 2),
                delta=0.02,
            )
        self.assertEqual(po.state, 'done')
        for line in po.order_line:
            self.assertNotEqual(line.qty_received, 0)

    def test_stowages_happy(self):
        """
        обрабатываем ацептанс happy
        в нем 5 строк, в стоваджах по 2 (4) таким образом не должно обработаться 1 строка
        но статус должен перейти в done
        """
        self.env['wms_integration.order'].post_processing(self.normal_acc, 'TEST', test=True)

        po = [po for po in self.po if po.external_id == self.normal_acc.common_external_id][0]

        self.assertEqual(po.state, 'purchase')
        stowage_ids = json.loads(self.normal_acc.vars)['stowage_id']
        pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
        self.assertEqual(len(pickings), len(json.loads(self.normal_acc.vars).get('stowage_id')))
        self.assertEqual(po.state, 'purchase')
        stw_data_set = self.factory.get_sale_stowages_data_from_acceptance(self.normal_acc)
        self.assertEqual(len(stw_data_set), len(stowage_ids))
        j = 1
        wms_docs = []
        all_logs = []
        for stw_data, stw_log in stw_data_set:
            all_logs += stw_log
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.normal_acc,
                count=j
            )
            j += 1

            wms_doc.post_processing(wms_doc, 'TEST', test=True)
            wms_docs.append((wms_doc, stw_log))
        self.factory.process_stock_logs(all_logs)

        self.assertEqual(po.state, 'done')
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        for line in po.order_line:
            qty_on_stock = stocks.get(
                (line.product_id, line.order_id.picking_type_id.warehouse_id.lot_stock_id),
                0
            )
            self.assertEqual(line.qty_received, qty_on_stock)

    def test_stowages_with_extra_lines(self):
        """
        обрабатываем стовадж с экстра строками
        """
        self.env['wms_integration.order'].post_processing(self.normal_acc, 'TEST', test=True)
        for po in self.po:
            if po.external_id == self.normal_acc.common_external_id:
                self.assertEqual(po.state, 'purchase')
                stowage_ids = json.loads(self.normal_acc.vars)['stowage_id']
                pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
                self.assertEqual(len(pickings), len(json.loads(self.normal_acc.vars).get('stowage_id')))
                self.assertEqual(po.state, 'purchase')
                stw_data_set = self.factory.get_sale_stowages_data_from_acceptance(self.normal_acc)
                self.assertEqual(len(stw_data_set), len(stowage_ids))
                j = 1
                purchased_products_fact = []
                all_logs = []
                for stw_data, stw_log in stw_data_set:

                    # добавим в каждый стовадж экстра строки
                    for product in self.extra_products:
                        extra_log_line = stw_log[0].copy()
                        extra_log_line.update({
                            'product_id': product.wms_id,
                            'delta_count': random.randrange(1, 45),
                            'log_id': f'extra_log_id_{j}_{uuid4()}',
                        })
                        stw_log.append(extra_log_line)

                    for line in stw_log:
                        purchased_products_fact.append(line['product_id'])
                    all_logs += stw_log
                    wms_doc = self.factory._create_stowage(
                        vals=stw_data,
                        parent=self.normal_acc,
                        count=j
                    )
                    j += 1
                    wms_doc.post_processing(wms_doc, 'TEST', test=True)

                new_log = self.factory.prepare_logs(all_logs)
                logs = self.env['wms_stock_log'].create(new_log)
                for log_line in logs:
                    with patch(
                            'odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                        log_data.return_value = [log_line]
                        self.env['wms_stock_log'].stock_log_jobs(test=True)
                        self.assertEqual(log_line.state, 'ok')

                not_purchased = [i for i in self.purchased_products if i.wms_id not in purchased_products_fact]
                mapped_prices = {i.product_id: i for i in self.purchase_requisition.line_ids}
                self.assertEqual(po.state, 'done')
                # проверим что добавились три экстра строки
                self.assertEqual(len(po.order_line), len(self.purchased_products) + len(self.extra_products))

                stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}

                for order_line in po.order_line:
                    price_line = mapped_prices.get(order_line.product_id)
                    # проверим, что не принятый товар реально не принят))
                    if order_line.product_id in not_purchased:
                        self.assertEqual(order_line.qty_received, 0)
                    # проверим цены для всех строк
                    self.assertAlmostEqual(order_line.price_unit, price_line.price_unit, 2)
                    qty_on_stock = stocks.get(
                        (order_line.product_id, order_line.order_id.picking_type_id.warehouse_id.lot_stock_id),
                        0
                    )
                    # проверим остаток на складе
                    self.assertEqual(order_line.qty_received, qty_on_stock)

                # проверим, что в свл сумма равна сумме прайсе
                for svl in po.order_line.mapped('move_ids.stock_valuation_layer_ids'):
                    req_line = mapped_prices.get(svl.product_id)
                    self.assertAlmostEqual(svl.value, svl.quantity * req_line.price_unit, 2)

    def test_zero_qty_stowage(self):
        """
          обрабатываем ацептанс, когда кто-то умный во всех стоваджах
          поставил нулевое кол-во
          тогда стоваджи прилетят без стоклога, но заказ должен перейти в done
        """
        self.env['wms_integration.order'].post_processing(self.normal_acc, 'TEST', test=True)
        for po in self.po:
            if po.external_id == self.normal_acc.common_external_id:
                self.assertEqual(po.state, 'purchase')
                stowage_ids = json.loads(self.normal_acc.vars)['stowage_id']
                pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
                self.assertEqual(len(pickings), len(json.loads(self.normal_acc.vars).get('stowage_id')))
                self.assertEqual(po.state, 'purchase')
                stw_data_set = self.factory.get_sale_stowages_data_from_acceptance(self.normal_acc, zero_qty=True)
                self.assertEqual(len(stw_data_set), len(stowage_ids))
                j = 1
                all_logs = []
                for stw_data, stw_log in stw_data_set:

                    wms_doc = self.factory._create_stowage(
                        vals=stw_data,
                        parent=self.normal_acc,
                        count=j
                    )
                    j += 1
                    all_logs += stw_log
                    wms_doc.post_processing(wms_doc, 'TEST', test=True)

                new_log = self.factory.prepare_logs(all_logs)
                logs = self.env['wms_stock_log'].create(new_log)
                for log_line in logs:
                    with patch(
                            'odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                        log_data.return_value = [log_line]
                        self.env['wms_stock_log'].stock_log_jobs(test=True)
                        self.assertEqual(log_line.state, 'ok')

                self.assertEqual(po.state, 'done')

    def test_stowage_before_acceptance(self):
        """
        случай, когда стоваджи лежат раньше, чем ацептанс при сортировке по полю updated
        это не должно никак влиять на обработку
        """
        self.env['ir.config_parameter'].set_param('sleep', 'false')
        po = [po for po in self.po if po.external_id == self.normal_acc.common_external_id][0]
        self.assertEqual(po.state, 'purchase')
        stowage_ids = json.loads(self.normal_acc.vars)['stowage_id']

        stw_data_set = self.factory.get_sale_stowages_data_from_acceptance(self.normal_acc)
        self.assertEqual(len(stw_data_set), len(stowage_ids))
        j = 1
        all_log_data = []
        for stw_data, stw_log in stw_data_set:
            all_log_data += stw_log
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.normal_acc,
                count=j
            )
            j += 1
            # обрабатываем стовадж
            wms_doc.post_processing(wms_doc, 'TEST', test=True)
            wms_doc.processing_status = 'ok'
        #  подготавливаем стоклог
        log_data = self.factory.prepare_logs(all_log_data)
        logs = self.env['wms_stock_log'].create(log_data)
        for log_line in logs:
            with patch('odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)

        pickings = self.env['stock.picking'].search([('wms_id', 'in', stowage_ids)])
        self.assertEqual(len(pickings), len(json.loads(self.normal_acc.vars).get('stowage_id')))
        self.assertEqual(po.state, 'done')
        # а теперь процессим ацептанс
        self.env['wms_integration.order'].post_processing(self.normal_acc, 'TEST', test=True)
        self.assertEqual(po.state, 'purchase')


@tagged('lavka', 'serializers', 's_acc_multi')
class TestAcceptanceMultiSerializer(SavepointCase):
    """
    тест цепочки
    ацептанс1 - ацептанс2 - ацептанс3
    стоваджи1 - стоваджи2 - стоваджи3
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.purchased_products = cls.products[:5]
        cls.extra_products = cls.products[5:8]
        cls.po = cls.factory.create_purchase_order(
            cls.purchased_products,
            cls.purchase_requisition,
            cls.warehouses, qty=1
        )[0]
        cls.acc_1 = cls.factory.create_acceptance_list(cls.po, cls.warehouses)[0]
        cls.stw_data_set_1 = cls.factory.get_sale_stowages_data_from_acceptance(cls.acc_1)

        purchase_line_vals = []
        # добавляем новый батч c существующимим в заказе товарами
        for product in cls.products[:4]:
            purchase_line_vals.append({
                'product_id': product.id,
                'name': product.name,
                'product_init_qty': random.randrange(1, 99),
                'order_id': cls.po.id,
                'price_unit': round(randrange(100, 999)/100, 2),
            })
        po_lines_2 = cls.env['purchase.order.line'].create(purchase_line_vals)
        cls.acc_2 = cls.factory.create_acceptance_from_po_lines(po_lines_2)
        cls.stw_data_set_2 = cls.factory.get_sale_stowages_data_from_acceptance(cls.acc_2)

        purchase_line_vals = []
        # добавляем новый батч c новыми товарами
        for product in cls.extra_products:
            purchase_line_vals.append({
                'product_id': product.id,
                'name': product.name,
                'product_init_qty': random.randrange(1, 99),
                'order_id': cls.po.id,
                'price_unit': round(randrange(100, 999)/100, 2),
            })
        po_lines_3 = cls.env['purchase.order.line'].create(purchase_line_vals)
        cls.acc_3 = cls.factory.create_acceptance_from_po_lines(po_lines_3)
        cls.stw_data_set_3 = cls.factory.get_sale_stowages_data_from_acceptance(cls.acc_3)
        cls.env['ir.config_parameter'].set_param('sleep', 'false')

    def test_acc_multi_sending_1(self):
        purchased_products_fact = []
        self.env['wms_integration.order'].post_processing(self.acc_1, 'TEST', test=True)
        j = 1
        all_logs = []
        for stw_data, stw_log in self.stw_data_set_1:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc_1,
                count=j
            )
            j += 1
            all_logs += stw_log
            wms_doc.post_processing(wms_doc, 'TEST',test=True)
        #  обрабатываем стоклог
        log_data = self.factory.prepare_logs(all_logs)
        logs = self.env['wms_stock_log'].create(log_data)
        for log_line in logs:
            with patch(
                    'odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)
                self.assertEqual(log_line.state, 'ok')

        # обработка второго ацептанса
        self.env['wms_integration.order'].post_processing(self.acc_2, 'TEST', test=True)
        j = 1
        all_logs_2 = []
        for stw_data, stw_log in self.stw_data_set_2:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc_2,
                count=j
            )
            j += 1
            all_logs_2 += stw_log
            wms_doc.post_processing(wms_doc, 'TEST', test=True)

        log_data_2 = self.factory.prepare_logs(all_logs_2)
        logs_2 = self.env['wms_stock_log'].create(log_data_2)
        for log_line in logs_2:
            with patch('odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)
                self.assertEqual(log_line.state, 'ok')

        # обработка третьего ацептанса
        self.env['wms_integration.order'].post_processing(self.acc_3, 'TEST', test=True)
        j = 1
        all_logs_3 = []
        for stw_data, stw_log in self.stw_data_set_3:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc_3,
                count=j
            )
            j += 1
            all_logs_3 += stw_log

            wms_doc.post_processing(wms_doc, 'TEST', test=True)

        log_data_3 = self.factory.prepare_logs(all_logs_3)
        logs_3 = self.env['wms_stock_log'].create(log_data_3)
        for log_line in logs_3:
            with patch('odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)
                self.assertEqual(log_line.state, 'ok')

        not_purchased = [i for i in self.purchased_products if i.wms_id not in purchased_products_fact]
        mapped_prices = {i.product_id: i for i in self.purchase_requisition.line_ids}
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        total_purchase_qty = defaultdict(int)
        for order_line in self.po.order_line:
            price_line = mapped_prices.get(order_line.product_id)
            # проверим, что не принятый товар реально не принят))
            if order_line.product_id in not_purchased:
                self.assertEqual(order_line.qty_received, 0)
            # проверим цены для всех строк
            self.assertAlmostEqual(order_line.price_unit, price_line.price_unit, 2)
            total_purchase_qty[
                (order_line.product_id, order_line.order_id.picking_type_id.warehouse_id.lot_stock_id)
            ] += order_line.qty_received

        for key, qty in total_purchase_qty.items():
            qty_on_stock = stocks.get(key, 0)
            # проверим остаток на складе
            self.assertEqual(qty, qty_on_stock)

        # проверим, что в свл сумма равна сумме прайсе
        for svl in self.po.order_line.mapped('move_ids.stock_valuation_layer_ids'):
            req_line = mapped_prices.get(svl.product_id)
            self.assertAlmostEqual(svl.value, svl.quantity * req_line.price_unit, 2)

        self.assertEqual(self.po.state, 'done')
        c = 1


@tagged('lavka', 'serializers', 's_acc_multi')
class TestAcceptanceMultiDistributedSerializer(SavepointCase):
    """
    тест цепочки
    ацептанс1 - стоваджи1
    ацептанс2 - стоваджи2
    ацептанс3 - стоваджи3
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.purchased_products = cls.products[:5]
        cls.extra_products = cls.products[5:8]
        cls.po = cls.factory.create_purchase_order(
            cls.purchased_products,
            cls.purchase_requisition,
            cls.warehouses, qty=1
        )[0]
        cls.acc_1 = cls.factory.create_acceptance_list(cls.po, cls.warehouses)[0]
        cls.stw_data_set_1 = cls.factory.get_sale_stowages_data_from_acceptance(cls.acc_1)

        purchase_line_vals = []
        # добавляем новый батч c существующимим в заказе товарами
        for product in cls.products[:4]:
            purchase_line_vals.append({
                'product_id': product.id,
                'name': product.name,
                'product_init_qty': random.randrange(1, 99),
                'order_id': cls.po.id,
                'price_unit': round(randrange(100, 999)/100, 2),
            })
        cls.po_lines_2 = cls.env['purchase.order.line'].create(purchase_line_vals)

        purchase_line_vals = []
        # добавляем новый батч c новыми товарами
        for product in cls.extra_products:
            purchase_line_vals.append({
                'product_id': product.id,
                'name': product.name,
                'product_init_qty': random.randrange(1, 99),
                'order_id': cls.po.id,
                'price_unit': round(randrange(100, 999)/100, 2),
            })
        cls.po_lines_3 = cls.env['purchase.order.line'].create(purchase_line_vals)
        cls.env['ir.config_parameter'].set_param('sleep', 'false')

    def test_acc_multi_sending_2(self):
        purchased_products_fact = []
        # обрабатываем первый ацептанс
        self.env['wms_integration.order'].post_processing(self.acc_1, 'TEST', test=True)
        j = 1
        all_logs = []
        for stw_data, stw_log in self.stw_data_set_1:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=self.acc_1,
                count=j
            )
            j += 1
            all_logs += stw_log
            wms_doc.post_processing(wms_doc, 'TEST', test=True)

        # обработка второго ацептанса после того, как первый полностью обработан
        acc_2 = self.factory.create_acceptance_from_po_lines(self.po_lines_2)
        stw_data_set_2 = self.factory.get_sale_stowages_data_from_acceptance(acc_2)
        self.env['wms_integration.order'].post_processing(acc_2, 'TEST', test=True)
        j = 1
        for stw_data, stw_log in stw_data_set_2:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=acc_2,
                count=j
            )
            j += 1
            all_logs += stw_log

            wms_doc.post_processing(wms_doc, 'TEST', test=True)

        # обработка третьего ацептанса после того, как первый и второй обработан
        acc_3 = self.factory.create_acceptance_from_po_lines(self.po_lines_3)
        stw_data_set_3 = self.factory.get_sale_stowages_data_from_acceptance(acc_3)

        self.env['wms_integration.order'].post_processing(acc_3, 'TEST', test=True)
        j = 1

        for stw_data, stw_log in stw_data_set_3:
            for line in stw_log:
                purchased_products_fact.append(line['product_id'])
            wms_doc = self.factory._create_stowage(
                vals=stw_data,
                parent=acc_3,
                count=j
            )
            j += 1
            all_logs += stw_log
            wms_doc.post_processing(wms_doc, 'TEST', test=True)
        # обработка логов после всех стооваджей
        log_data = self.factory.prepare_logs(all_logs)
        logs = self.env['wms_stock_log'].create(log_data)
        for log_line in logs:
            with patch('odoo.addons.lavka.backend.models.wms.wms_stock_log.WMSStockLog.get_first_logs_by_stores') as log_data:
                log_data.return_value = [log_line]
                self.env['wms_stock_log'].stock_log_jobs(test=True)
                self.assertEqual(log_line.state, 'ok')

        not_purchased = [i for i in self.purchased_products if i.wms_id not in purchased_products_fact]
        mapped_prices = {i.product_id: i for i in self.purchase_requisition.line_ids}
        stocks = {(i.product_id, i.location_id): i.quantity for i in self.env['stock.quant'].search([])}
        total_purchase_qty = defaultdict(int)
        for order_line in self.po.order_line:
            price_line = mapped_prices.get(order_line.product_id)
            # проверим, что не принятый товар реально не принят))
            if order_line.product_id in not_purchased:
                self.assertEqual(order_line.qty_received, 0)
            # проверим цены для всех строк
            self.assertAlmostEqual(order_line.price_unit, price_line.price_unit, 2)
            total_purchase_qty[
                (order_line.product_id, order_line.order_id.picking_type_id.warehouse_id.lot_stock_id)
            ] += order_line.qty_received

        for key, qty in total_purchase_qty.items():
            qty_on_stock = stocks.get(key, 0)
            # проверим остаток на складе
            self.assertEqual(qty, qty_on_stock)

        # проверим, что в свл сумма равна сумме прайсе
        for svl in self.po.order_line.mapped('move_ids.stock_valuation_layer_ids'):
            req_line = mapped_prices.get(svl.product_id)
            self.assertAlmostEqual(svl.value, svl.quantity * req_line.price_unit, 2)

        self.assertEqual(self.po.state, 'done')
        c = 1

