import datetime as dt
import json
import os
from unittest.mock import patch


from odoo.addons.lavka.backend.models.purchase_requisition import TZ_DELTA
from odoo.tests.common import SavepointCase, tagged

from odoo.addons.lavka.tests.backend.three_pl.test_3pl_proxy import Base3PLExchange

@tagged("lavka", "tpl_po_send")
class Test3PLPOExchange(Base3PLExchange):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_send_po_manual_queue(self):
        self.assertEqual(self.po.state, 'draft')
        self.po.action_send_to_wms()
        count = self.env['exchange.queue'].search_count([
            ('res_model', '=', self.po._name),
            ('res_id', '=', self.po.id),
            ('dc', '=', self.wh_out.id),
        ]
        )
        self.assertEqual(count, 1)

        res_id = self.env['exchange.queue'].pop(self.po._name, self.wh_out)
        self.assertEqual(res_id, [self.po.id])

    def test_cron_add_po_to_send(self):
        begin_day = self.env['purchase.order'].begin_of_day(dt.datetime.now())
        (self.po + self.po2).date_planned = begin_day + dt.timedelta(hours=3)
        self.po3.date_planned = begin_day + dt.timedelta(days=1)
        (self.po + self.po2 + self.po3).state = 'sent'

        # today
        self.env['three_pl.providers'].push_orders_queue('today')

        res_ids = self.env['exchange.queue'].pop(self.po._name, self.wh_out)
        self.assertEqual(set(res_ids), {self.po.id, self.po2.id})

        count = self.env['exchange.queue'].search_count([
            ('res_model', '=', self.po._name),
            ('res_id', 'in', [self.po.id, self.po2.id]),
            ('dc', '=', self.wh_out.id),
        ]
        )
        self.assertEqual(count, 0)

        # tomorrow
        self.env['three_pl.providers'].push_orders_queue('tomorrow')

        res_id = self.env['exchange.queue'].pop(self.po3._name, self.wh_out)
        self.assertEqual(set(res_id), {self.po3.id})

        count = self.env['exchange.queue'].search_count([
            ('res_model', '=', self.po._name),
            ('res_id', '=', self.po3.id),
            ('dc', '=', self.wh_out.id),
        ]
        )
        self.assertEqual(count, 0)

    def test_send_po_to_tpl(self):
        with patch('common.client.ftp_proxy.FTProxy.send_file') as proxy_data:
            proxy_data.return_value = 'test_file_name'
            po_ids = self.po + self.po2
            data = self.env['three_pl.sender'].send_po_to_3pl(self.provider, po_ids.ids)
            self.assertEqual(len(data), len(po_ids.order_line))
            map_lines = {}
            for line in po_ids.order_line:
                map_lines[line.order_id.name + line.product_id.default_code] = line
            for line in data:
                #todo: проверять и вес, обновить фабрику для продуктов
                line_po = map_lines[line['NOMERDOK'] + line['TOVAR']]
                self.assertEqual(line['TOVAR'], line_po.product_id.default_code)
                self.assertEqual(line['TOVNAM'], line_po.product_id.name)
                self.assertEqual(line['ITOVNAM'], line_po.product_id.local_name)
                self.assertEqual(line['SL'], 0)
                self.assertEqual(line['KOLVO'], line_po.product_init_qty)
                self.assertEqual(line['UPAK'], 'kg' if line_po.product_id.type_accounting == 'weight' else 'unit')
                self.assertEqual(line['PRODUCER'], line_po.order_id.partner_id.name)
                self.assertEqual(line['VES'], '1' if line_po.product_id.type_accounting == 'weight' else '0')
                self.assertEqual(line['VES1'], line_po.product_id.weight)
                self.assertEqual(line['SLPROC'], 0)
                self.assertEqual(line['SLOSG'], line_po.product_id.write_off_before)
                self.assertEqual(line['KOLM'], line_po.qty_in_box)
                self.assertEqual(line['SHTRKOD'], line_po.product_id.barcode)
                self.assertEqual(line['NETTO'], line_po.product_id.weight_netto)
                self.assertEqual(line['BRUTTO'], line_po.product_id.weight_brutto)
                self.assertEqual(round(line['WEIGHT_K'], 2), round(line_po.product_id.weight_netto / 1000, 2))
                self.assertEqual(line['NONFOOD'], '1' if line_po.product_id.nonfood_tag else '0')
                self.assertEqual(line['STR_AREA'], line_po.storage_area)
                self.assertEqual(line['DLV_TYPE'], line_po.order_id.delivery_type)
                self.assertEqual(line['PRINTDOC'], '')
                self.assertEqual(line['NOMERDOK'], line_po.order_id.name)
                self.assertEqual(line['PRICE'], line_po.price_unit)
                self.assertEqual(line['SUP_INN'], line_po.order_id.partner_id.vat)
                self.assertEqual(line['DATADOK'], (line_po.order_id.date_planned - TZ_DELTA).strftime('%Y-%m-%dT%H:%M:%S'))

    def test_generate_file_interface(self):
        action = self.po.action_generate_json_3pl()
        wiz = self.env['save.file.wizard'].browse(action['res_id'])
        self.assertTrue(wiz.data)

        action = self.tr.action_generate_json_3pl()
        wiz = self.env['save.file.wizard'].browse(action['res_id'])
        self.assertTrue(wiz.data)
        self.assertTrue(wiz.data_header)


@tagged("lavka","tpl_tr_send")
class Test3PLTRExchange(Base3PLExchange):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_cron_add_tr_to_send(self):
        self.env['three_pl.providers'].push_transfers_queue()

        res_id = self.env['exchange.queue'].pop(self.tr._name, self.wh_out)
        self.assertEqual(res_id, [self.tr.id])

        count = self.env['exchange.queue'].search_count([
            ('res_model', '=', self.po._name),
            ('res_id', '=', self.tr.id),
            ('dc', '=', self.wh_out.id),
        ]
        )
        self.assertEqual(count, 0)

    def test_send_tr_to_tpl(self):
        with patch('common.client.ftp_proxy.FTProxy.send_file') as proxy_data:
            proxy_data.return_value = 'test_file_name'
            #storage type + nonfood


            data = self.env['three_pl.sender'].send_tr_to_3pl(self.provider,
                                                              [self.tr.id],
                                                              self.env['three_pl.providers'].get_company_params()
                                                              )
            header, lines = data['HEADERS'][0], data['LINES']

            #  company properties (system parameters)
            self.assertEqual(header['KONTRA'], self.env.ref('lavka.company_code_param').value)
            self.assertEqual(header['KONTRANAME'], self.env.ref('lavka.company_name_param').value)
            self.assertEqual(header['KINN'], self.env.ref('lavka.company_vat_param').value)
            self.assertEqual(header['MADR'], self.env.ref('lavka.company_addr_param').value)

            self.assertEqual(header['ZAKAZ'], self.tr.name)
            self.assertEqual(header['ADR'], self.tr.warehouse_in.address)
            self.assertEqual(header['MARKET'], self.tr.warehouse_in.code)
            self.assertEqual(header['MARKETNAME'], self.tr.warehouse_in.name)
            self.assertEqual(header['ZAKAZID'], self.tr.name)
            self.assertEqual(header['STATUSZ'], '0')
            self.assertEqual(header['MOROZ'], '1' if self.tr.is_freezer else '0')
            self.assertEqual(header['VS'], '0')
            self.assertEqual(header['DATA'], (self.tr.date_planned - TZ_DELTA).strftime('%Y-%m-%dT%H:%M:%S'))
            self.assertEqual(header['DATADOK'], (self.tr.create_date - TZ_DELTA).strftime('%Y-%m-%dT%H:%M:%S'))

            self.assertEqual(len(lines), len(self.tr.transfer_lines))
            map_lines = {}
            for line in self.tr.transfer_lines:
                map_lines[line.transfer_id.name + line.product_id.default_code] = line
            for line in lines:
                line_tr = map_lines[line['ZAKAZ'] + line['TOVAR']]
                self.assertEqual(line['TOVAR'], line_tr.product_id.default_code)
                self.assertEqual(line['TOVNAM'], line_tr.product_id.name)
                self.assertEqual(line['ITOVNAM'], line_tr.product_id.local_name)
                self.assertEqual(line['SL'], 0)
                self.assertEqual(line['KOLVO'], line_tr.qty_plan)
                self.assertEqual(line['UPAK'], 'kg' if line_tr.product_id.type_accounting == 'weight' else 'unit')
                self.assertEqual(line['PRODUCER'], '')
                self.assertEqual(line['VES'], '1' if line_tr.product_id.type_accounting == 'weight' else '0')
                self.assertEqual(line['VES1'], line_tr.product_id.weight)
                self.assertEqual(line['SLPROC'], 0)
                self.assertEqual(line['SLOSG'], line_tr.product_id.write_off_before)
                self.assertEqual(line['KOLM'], line_tr.qty_in_box)
                self.assertEqual(line['SHTRKOD'], line_tr.product_id.barcode)
                self.assertEqual(line['NETTO'], line_tr.product_id.weight_netto)
                self.assertEqual(line['BRUTTO'], line_tr.product_id.weight_brutto)
                self.assertEqual(round(line['WEIGHT_K'], 2), round(line_tr.product_id.weight_netto / 1000, 2))
                self.assertEqual(line['NONFOOD'], '1' if line_tr.product_id.nonfood_tag else '0')
                self.assertEqual(line['STR_AREA'], line_tr.storage_area)
                self.assertEqual(line['DLV_TYPE'], line_tr.delivery_type)
                self.assertEqual(line['ZAKAZ'], line_tr.transfer_id.name)
                self.assertEqual(line['TMRKID'], '')
                self.assertEqual(line['NOVSD'], '0')
                #не требуется, в шапке есть
                # self.assertEqual(line['DATADOK'],line_tr.transfer_id.date_planned)
