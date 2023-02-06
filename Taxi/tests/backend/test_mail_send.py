import logging
from datetime import datetime
from random import randrange
from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged
from odoo.tools.misc import format_date, format_amount

from .test_common import TestVeluationCommon

_logger = logging.getLogger(__name__)


@tagged('lavka', 'RFQ_send')
class TestPurchaseOrderRFQSend(TestVeluationCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()


        cls.mail_server = cls.env['ir.mail_server'].create(
            {
                'name': 'test_mail_server',
                'sending_type': 'email',
                'active': True,
                'smtp_host': 'test',
                'smtp_port': 777,
            }
        )

        cls.new_template = cls.env['mail.template'].create(
            {
                'name': 'test_template',
                'model_id': cls.env['ir.model'].search([
                    ('model', '=', 'purchase.order')
                ])[0].id,

            }
        )

        template_p = cls.env.ref('lavka.email_template_aeroo_lavka_mass').id
        template_p2 = cls.env.ref('lavka.email_template_aeroo_lavka').id

        cls.partner2 = cls.env['res.partner'].create({'name': 'Test Purchaser2', 'mail_template':  template_p2})
        cls.partner.update({'mail_template':  template_p})

        cls.subv_cnt = cls.env['res.partner'].create(
            {
                'name': 'Test Subv Contact',
                'company_type':  'person',
                'type':  'contact',
                'email': 'cnt@example.com'
            }
        )
        cls.subv_deliv = cls.env['res.partner'].create(
            {
                'name': 'Test Subv Delivery',
                'company_type':  'person',
                'type':  'delivery',
                'email': 'deliv@example.com'
            }
        )

        child_ids = (cls.subv_cnt.id, cls.subv_deliv.id)
        cls.partner2.update({'child_ids':child_ids})

        cls.purchase_requsition2 = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner2.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        with freeze_time('2021-03-15 12:00:00'):
            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 5.25,
                'start_date': fields.Datetime.today(),
                'product_uom_id': i.uom_id.id,
                'tax_id': i.supplier_taxes_id.id,
                'requisition_id': cls.purchase_requsition2.id,
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

        date_planned = datetime.today()

        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[0].name,
                    'product_id': cls.products[0].id,
                    'product_qty': 1.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 2.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po1.button_confirm()

        cls.po2 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[0].name,
                    'product_id': cls.products[0].id,
                    'product_qty': 1.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po2.button_confirm()

        cls.po3 = cls.env['purchase.order'].create({
            'partner_id': cls.partner2.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 3.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po3.button_confirm()

        cls.po4 = cls.env['purchase.order'].create({
            'partner_id': cls.partner2.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 3.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po4.button_confirm()


    def testSendRFQ(self):
        # set report out_format to .xlsx
        self.env.ref('lavka.email_template_aeroo_lavka').report_template.out_format = self.env[
            'report.mimetypes'].search([('code', '=', 'oo-xlsx')])
        # test for manual sending RFQ
        self.po1.action_rfq_send()

        self.assertEqual(
            self.new_template.conc_attach, 'many_one',
            f'''Send RFQ. Wrong default 'Attachment merge type' in new template'''
        )

        self.po1.action_rfq_send_lavka()
        last_message = self.env['mail.message'].search([], order='id desc')[0]
        self.assertEqual(
            last_message.subject,
            f'''Purchase Orders from {self.po1.company_id.name} - {format_date(self.env, datetime.today())}''',
            f'Send RFQ. Wrong subject of letter by several orders'
        )

        self.assertTrue(
            f'Dear {self.po1.partner_id.name}' in last_message.body,
            f'Send RFQ. Wrong partner'
        )

        self.partner.mail_template.update({'mail_server_id': self.mail_server})
        self.po1.action_rfq_send_lavka()
        last_message = self.env['mail.message'].search([], order='id desc')[0]
        self.assertEqual(
            last_message.message_type,
            'email',
            f'Send RFQ. Wrong type of mail message for one_many template'
        )

        orders = self.env['purchase.order']
        orders += self.po1
        orders += self.po2
        orders += self.po3
        orders += self.po4

        orders.action_rfq_send_lavka()
        last_message_po4 = self.env['mail.message'].search([], order='id desc')[0]
        last_message_po3 = self.env['mail.message'].search([], order='id desc')[1]

        self.assertTrue(
            self.po3.partner_id in last_message_po3.partner_ids,
            f'Send RFQ. No order partner in recipients'
        )
        self.assertTrue(
            self.subv_cnt in last_message_po3.partner_ids,
            f'Send RFQ. No order partner child with type contact is in recipients'
        )
        self.assertTrue(
            self.subv_deliv not in last_message_po3.partner_ids,
            f'Send RFQ. Order partner child with type delivery is in recipients'
        )

        self.assertEqual(
            self.po3.partner_id.name in last_message_po4.body,
            self.po4.partner_id.name in last_message_po3.body,
            f'Send RFQ. Wrong attachment merging algorithm for many_one partner template'
        )

        self.assertEqual(
            last_message_po3.subject,
            f'''{self.po3.company_id.name} Order (Ref {self.po3.name or 'n/a'})''',
            f'Send RFQ. Wrong subject of letter by alone order'
        )
        self.assertTrue(
            f'Dear {self.po3.partner_id.name}' in last_message_po3.body,
            f'Send RFQ. Wrong partner of letter by alone order'
        )

        last_message_po1 = self.env['mail.message'].search([], order='id desc')[2]
        self.assertEqual(
            last_message_po1.subject,
            f'''Purchase Orders from {self.po1.company_id.name} - {format_date(self.env, datetime.today())}''',
            f'Send RFQ. Wrong subject of letter by several orders'
        )
        self.assertTrue(
            f'Dear {self.po1.partner_id.name}' in last_message_po1.body,
            f'Send RFQ. Wrong partner of letter by several orders'
        )

        orders = self.env['purchase.order']
        orders += self.po1
        orders += self.po2

        amount_total = 0
        dates_planned = []
        for po in orders:
            amount_total += po.amount_total
            dates_planned.append(po.date_planned)

        currency_id = self.env.company.currency_id

        if len(set(dates_planned)) > 1:
            date_planned = ''
        else:
            date_planned = dates_planned[0]

        formatted_amount = format_amount(self.env, amount_total, currency_id)
        self.assertTrue(
            formatted_amount in last_message_po1.body,
            f'Send RFQ. Wrong amount_total of letter by several orders'
        )

        date_planned = format_date(self.env, date_planned)
        self.assertTrue(
            date_planned in last_message_po1.body,
            f'Send RFQ. Wrong date_planned of letter by several orders'
        )

        attachments = [at.name for at in self.env['ir.attachment'].search(
            [
                ['res_model', '=', 'mail.message'],
                ['res_id', '=', last_message_po1.id],
            ],
        )]

        for order in orders:
            self.assertFalse(
                f'PO_{order.name}.ods' in attachments,
                f'Send RFQ. Aeroo could not convert report to .xlsx. '
                'Check if LibreOffice is running.'
            )
            self.assertTrue(
                f'PO_{order.name}.xlsx' in attachments,
                f'Send RFQ. Attachment not found of letter by several orders'
            )


@tagged('lavka', 'RFQ_send')
class TestPurchaseOrderEDISend(TestVeluationCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        date_planned = datetime.today()

        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[0].name,
                    'product_id': cls.products[0].id,
                    'product_qty': 1.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 2.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po1.button_confirm()

        cls.po2 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_2.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[0].name,
                    'product_id': cls.products[0].id,
                    'product_qty': 1.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 2.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po2.button_confirm()

        cls.edi_mail_server = cls.env['ir.mail_server'].create(
            {
                'name': 'test_edi_mail_server',
                'sending_type': 'edi',
                'active': True,
                'smtp_host': 'test',
                'smtp_port': 777,
            }
        )

        cls.edi_receiver_mapping_line = cls.env['ir.mail.server.edi_receiver_mapping_line'].create(
            {
                'partner_id': cls.partner.id,
                'gln_code': '1111111',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_store_mapping_line = cls.env['ir.mail.server.edi_store_mapping_line'].create(
            {
                'store_id': cls.po1.picking_type_id.warehouse_id.id,
                'gln_code': '3333333',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_store_mapping_line2 = cls.env['ir.mail.server.edi_store_mapping_line'].create(
            {
                'store_id': cls.po2.picking_type_id.warehouse_id.id,
                'gln_code': '444444',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_pa_mapping_line = cls.env['ir.mail.server.edi_pa_mapping_line'].create(
            {
                'pa_id': cls.purchase_requsition.id,
                'gln_code': '4444444',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_report_view = cls.env['ir.ui.view'].create(
            {
                'name': 'test_edi_view',
                'model': 'purchase.order',
                'type': 'qweb',
                'arch_base': '''<?xml version="1.0"?>
                                 <t t-foreach="docs" t-as="o">&lt;?xml version="1.0"?&gt;
                                   <t t-if="docs._context['edi_type'] == 'edi'">
                                     <OrderXml>
                                       <Envelope>
                                         <Sender>7290058231072</Sender>
                                         <Receiver><t t-if="o.partner_id.parent_id"><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id.parent_id).mapped('gln_code')[0]"/></t><t t-else=""><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id).mapped('gln_code')[0]"/></t></Receiver>
                                         <DocType>MMORDMXML</DocType>
                                         <APRF>MMOR01</APRF>
                                         <SNRF>83959821</SNRF>
                                         <MessDate><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></MessDate>
                                         <MessTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%H%M')"/></MessTime>
                                         <Header>
                                           <OrderNo><t t-esc="o.name.replace('-','').replace('PO','')"/></OrderNo>
                                           <OrderType>105</OrderType>
                                           <OrderDate><t t-esc="o.create_date.strftime('%Y%m%d%H%M')"/></OrderDate>
                                           <SupplyDate><t t-esc="o.date_planned.strftime('%Y%m%d%H%M')"/></SupplyDate>
                                           <SupplierCode><t t-esc="o.partner_id.edi_template.mail_server_id.edi_pa_mapping_line.filtered(lambda r: r.pa_id == o.requisition_id).mapped('gln_code')[0]"/></SupplierCode>
                                           <StoreCode><t t-esc="o.partner_id.edi_template.mail_server_id.edi_store_mapping_line.filtered(lambda r: r.store_id == o.picking_type_id.warehouse_id).mapped('gln_code')[0]"/></StoreCode>
                                           <Details>
                                             <t t-set="total_lines" t-value="0"/>
                                             <t t-foreach="o.order_line" t-as="line">
                                               <t t-set="total_lines" t-value="total_lines + 1"/>
                                               <Line>
                                                 <LineNo><t t-esc="total_lines"/></LineNo>
                                                 <ItemBarcode><t t-esc="o.requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id).mapped('product_code')[0]"/></ItemBarcode>
                                                 <UnitsQty><t t-esc="line.product_init_qty"/></UnitsQty>
                                               </Line>
                                             </t>
                                           </Details>
                                           <Summary>
                                             <TotalQty><t t-esc="o.total_init_qty"/></TotalQty>
                                             <TotalLines><t t-esc="total_lines"/></TotalLines>
                                           </Summary>
                                           </Header>
                                       </Envelope>
                                     </OrderXml>
                                   </t>
                                   <t t-if="docs._context['edi_type'] == 'edi_response'">
                                     <ResponseSupplyXml>
                                       <Envelope>
                                         <Sender>7290058231072</Sender>
                                         <Receiver><t t-if="o.partner_id.parent_id"><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id.parent_id).mapped('gln_code')[0]"/></t><t t-else=""><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id).mapped('gln_code')[0]"/></t></Receiver>
                                         <DocType>MMORDMXML</DocType>
                                         <APRF>MMOR01</APRF>
                                         <MessDate><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></MessDate>
                                         <MessTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%H%M')"/></MessTime>
                                         <Header>
                                             <ResponseNo><t t-esc="o.name.replace('-','').replace('PO','')"/></ResponseNo>
                                             <ResponseCode>29</ResponseCode>
                                             <ResponseDateTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></ResponseDateTime>
                                             <DeliveryDateTime><t t-esc="o.date_planned.strftime('%Y%m%d%H%M')"/></DeliveryDateTime>
                                             <SupdesNo></SupdesNo>
                                             <SupdesDate></SupdesDate>
                                           <SupplierNo><t t-esc="o.partner_id.edi_template.mail_server_id.edi_pa_mapping_line.filtered(lambda r: r.pa_id == o.requisition_id).mapped('gln_code')[0]"/></SupplierNo>
                                           <StoreNo><t t-esc="o.partner_id.edi_template.mail_server_id.edi_store_mapping_line.filtered(lambda r: r.store_id == o.picking_type_id.warehouse_id).mapped('gln_code')[0]"/></StoreNo>
                                             <References>
                                                 <RefQual>ACE</RefQual>
                                                 <RefNo></RefNo>
                                                 <RefDate></RefDate>
                                             </References>
                                           <Details>
                                             <t t-set="total_lines" t-value="0"/>
                                             <t t-foreach="o.order_line" t-as="line">
                                               <t t-set="total_lines" t-value="total_lines + 1"/>
                                               <Line>
                                                 <LineNo><t t-esc="total_lines"/></LineNo>
                                                 <ItemBarcode><t t-esc="o.requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id).mapped('product_code')[0]"/></ItemBarcode>
                                                 <AmendQty><t t-esc="line.qty_received"/></AmendQty>
                                               </Line>
                                             </t>
                                           </Details>
                                         </Header>
                                       </Envelope>
                                     </ResponseSupplyXml>
                                   </t>
                                 </t>
                                 ''',
                'active': True
            }
        )

        cls.edi_report = cls.env['ir.actions.report'].create(
            {
                'name': 'test_edi_report',
                'model': 'purchase.order',
                'report_name': cls.edi_report_view.key,
                'print_report_name': '''(object.state in ('draft', 'sent') and 'Request for Quotation - %s' % (object.name) or 'Purchase Order - %s' % (object.name))''',
                'report_type': 'qweb-xml'
            }
        )

        cls.edi_template = cls.env['mail.template'].create(
            {
                'name': 'test_edi_template',
                'model_id': cls.env['ir.model'].search([
                    ('model', '=', 'purchase.order')
                ])[0].id,
                'subject': '''EDI-${object.company_id.name} Order (Ref ${object.name or 'n/a' })''',
                'mail_server_id': cls.edi_mail_server.id,
                'report_template': cls.edi_report.id,
                'report_name': '''PO_${(object.name or '').replace('/', '_')}''',
                'conc_attach': 'many_one',
            }
        )


    def testSendEDI(self):
        self.partner.update(
            {
                'edi_template': self.edi_template,
                'mail_template': None,
            }
        )

        self.assertEqual(
            self.edi_template.conc_attach, 'many_one',
            f'''Send EDI. Wrong default 'Attachment merge type' in new template'''
        )

        self.po1.action_rfq_send_lavka()
        last_message = self.env['mail.message'].search([], order='id desc')[0]

        self.assertEqual(
            last_message.subject,
            f'''ORD-EDI-{self.po1.company_id.name} Order (Ref {self.po1.name or 'n/a'})''',
            f'Send EDI. Wrong subject of edi message'
        )

        self.assertEqual(
            last_message.message_type,
            'edi',
            f'Send EDI. Wrong type of edi message'
        )

        self.assertEqual(
            last_message.mail_server_id,
            self.edi_mail_server,
            f'Send EDI. Wrong mail server of edi message'
        )

        last_mail = self.env['mail.mail'].search([], order='id desc')[0]
        attachment = last_mail.attachment_ids[0]

        self.assertEqual(
            attachment.name,
            f'''ORD-PO_{(self.po1.name or '').replace('/', '_')}.xml''',
            f'Send EDI. Wrong attachment name of edi message'
        )

        self.assertEqual(
            attachment.mimetype,
            'application/xml',
            f'Send EDI. Wrong attachment mimetype of edi message'
        )

        po_for_send = self.env['purchase.order']
        po_for_send += self.po1 + self.po2
        po_for_send.action_rfq_send_lavka()
        last_message = self.env['mail.message'].search([], order='id desc')[0]

        self.assertEqual(
            last_message.subject,
            f'''ORD-EDI-{self.po2.company_id.name} Order (Ref {self.po2.name or 'n/a'})''',
            f'Send EDI. Multy send. Wrong subject of edi message 1'
        )

        last_message = self.env['mail.message'].search([], order='id desc')[1]

        self.assertEqual(
            last_message.subject,
            f'''ORD-EDI-{self.po1.company_id.name} Order (Ref {self.po1.name or 'n/a'})''',
            f'Send EDI. Multy send. Wrong subject of edi message 2'
        )

        self.edi_store_mapping_line2.unlink()
        with self.assertRaises(exception=AssertionError):
            po_for_send.action_rfq_send_lavka()


@tagged('lavka', 'RFQ_send')
class TestPurchaseOrderEDIResponseSend(TestVeluationCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        date_planned = datetime.today()

        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id,
            'date_planned': date_planned,
            'picking_type_id': cls.warehouse_1.in_type_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'order_line': [
                (0, 0, {
                    'name': cls.products[0].name,
                    'product_id': cls.products[0].id,
                    'product_qty': 1.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
                (0, 0, {
                    'name': cls.products[1].name,
                    'product_id': cls.products[1].id,
                    'product_qty': 2.0,
                    'product_init_qty': 10,
                    'price_unit': 100.0,
                    'taxes_id': False,
                }),
            ],
        })
        cls.po1.button_confirm()

        cls.edi_mail_server = cls.env['ir.mail_server'].create(
            {
                'name': 'test_edi_mail_server',
                'sending_type': 'edi',
                'active': True,
                'smtp_host': 'test',
                'smtp_port': 777,
            }
        )

        cls.edi_receiver_mapping_line = cls.env['ir.mail.server.edi_receiver_mapping_line'].create(
            {
                'partner_id': cls.partner.id,
                'gln_code': '1111111',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_store_mapping_line = cls.env['ir.mail.server.edi_store_mapping_line'].create(
            {
                'store_id': cls.po1.picking_type_id.warehouse_id.id,
                'gln_code': '3333333',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_pa_mapping_line = cls.env['ir.mail.server.edi_pa_mapping_line'].create(
            {
                'pa_id': cls.purchase_requsition.id,
                'gln_code': '4444444',
                'server_id': cls.edi_mail_server.id,
            }
        )

        cls.edi_report_view = cls.env['ir.ui.view'].create(
            {
                'name': 'test_edi_view',
                'model': 'purchase.order',
                'type': 'qweb',
                'arch_base': '''<?xml version="1.0"?>
                                <t t-foreach="docs" t-as="o">&lt;?xml version="1.0"?&gt;
                                  <t t-if="docs._context['edi_type'] == 'edi'">
                                    <OrderXml>
                                      <Envelope>
                                        <Sender>7290058231072</Sender>
                                        <Receiver><t t-if="o.partner_id.parent_id"><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id.parent_id).mapped('gln_code')[0]"/></t><t t-else=""><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id).mapped('gln_code')[0]"/></t></Receiver>
                                        <DocType>MMORDMXML</DocType>
                                        <APRF>MMOR01</APRF>
                                        <SNRF>83959821</SNRF>
                                        <MessDate><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></MessDate>
                                        <MessTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%H%M')"/></MessTime>
                                        <Header>
                                          <OrderNo><t t-esc="o.name.replace('-','').replace('PO','')"/></OrderNo>
                                          <OrderType>105</OrderType>
                                          <OrderDate><t t-esc="o.create_date.strftime('%Y%m%d%H%M')"/></OrderDate>
                                          <SupplyDate><t t-esc="o.date_planned.strftime('%Y%m%d%H%M')"/></SupplyDate>
                                          <SupplierCode><t t-esc="o.partner_id.edi_template.mail_server_id.edi_pa_mapping_line.filtered(lambda r: r.pa_id == o.requisition_id).mapped('gln_code')[0]"/></SupplierCode>
                                          <StoreCode><t t-esc="o.partner_id.edi_template.mail_server_id.edi_store_mapping_line.filtered(lambda r: r.store_id == o.picking_type_id.warehouse_id).mapped('gln_code')[0]"/></StoreCode>
                                          <Details>
                                            <t t-set="total_lines" t-value="0"/>
                                            <t t-foreach="o.order_line" t-as="line">
                                              <t t-set="total_lines" t-value="total_lines + 1"/>
                                              <Line>
                                                <LineNo><t t-esc="total_lines"/></LineNo>
                                                <ItemBarcode><t t-esc="o.requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id).mapped('product_code')[0]"/></ItemBarcode>
                                                <UnitsQty><t t-esc="line.product_init_qty"/></UnitsQty>
                                              </Line>
                                            </t>
                                          </Details>
                                          <Summary>
                                            <TotalQty><t t-esc="o.total_init_qty"/></TotalQty>
                                            <TotalLines><t t-esc="total_lines"/></TotalLines>
                                          </Summary>
                                          </Header>
                                      </Envelope>
                                    </OrderXml>
                                  </t>
                                  <t t-if="docs._context['edi_type'] == 'edi_response'">
                                    <ResponseSupplyXml>
                                      <Envelope>
                                        <Sender>7290058231072</Sender>
                                        <Receiver><t t-if="o.partner_id.parent_id"><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id.parent_id).mapped('gln_code')[0]"/></t><t t-else=""><t t-esc="o.partner_id.edi_template.mail_server_id.edi_receiver_mapping_line.filtered(lambda r: r.partner_id == o.partner_id).mapped('gln_code')[0]"/></t></Receiver>
                                        <DocType>MMORDMXML</DocType>
                                        <APRF>MMOR01</APRF>
                                        <MessDate><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></MessDate>
                                        <MessTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%H%M')"/></MessTime>
                                        <Header>
                                            <ResponseNo><t t-esc="o.name.replace('-','').replace('PO','')"/></ResponseNo>
                                            <ResponseCode>29</ResponseCode>
                                            <ResponseDateTime><t t-esc="context_timestamp(datetime.datetime.now()).strftime('%y%m%d')"/></ResponseDateTime>
                                            <DeliveryDateTime><t t-esc="o.date_planned.strftime('%Y%m%d%H%M')"/></DeliveryDateTime>
                                            <SupdesNo></SupdesNo>
                                            <SupdesDate></SupdesDate>
                                          <SupplierNo><t t-esc="o.partner_id.edi_template.mail_server_id.edi_pa_mapping_line.filtered(lambda r: r.pa_id == o.requisition_id).mapped('gln_code')[0]"/></SupplierNo>
                                          <StoreNo><t t-esc="o.partner_id.edi_template.mail_server_id.edi_store_mapping_line.filtered(lambda r: r.store_id == o.picking_type_id.warehouse_id).mapped('gln_code')[0]"/></StoreNo>
                                            <References>
                                                <RefQual>ACE</RefQual>
                                                <RefNo></RefNo>
                                                <RefDate></RefDate>
                                            </References>
                                          <Details>
                                            <t t-set="total_lines" t-value="0"/>
                                            <t t-foreach="o.order_line" t-as="line">
                                              <t t-set="total_lines" t-value="total_lines + 1"/>
                                              <Line>
                                                <LineNo><t t-esc="total_lines"/></LineNo>
                                                <ItemBarcode><t t-esc="o.requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id).mapped('product_code')[0]"/></ItemBarcode>
                                                <AmendQty><t t-esc="line.qty_received"/></AmendQty>
                                              </Line>
                                            </t>
                                          </Details>
                                        </Header>
                                      </Envelope>
                                    </ResponseSupplyXml>
                                  </t>
                                </t>
                                ''',
                'active': True
            }
        )

        cls.edi_report = cls.env['ir.actions.report'].create(
            {
                'name': 'test_edi_report',
                'model': 'purchase.order',
                'report_name': cls.edi_report_view.key,
                'print_report_name': '''(object.state in ('draft', 'sent') and 'Request for Quotation - %s' % (object.name) or 'Purchase Order - %s' % (object.name))''',
                'report_type': 'qweb-xml'
            }
        )

        cls.edi_template = cls.env['mail.template'].create(
            {
                'name': 'test_edi_template',
                'model_id': cls.env['ir.model'].search([
                    ('model', '=', 'purchase.order')
                ])[0].id,
                'subject': '''EDI-${object.company_id.name} Order (Ref ${object.name or 'n/a' })''',
                'mail_server_id': cls.edi_mail_server.id,
                'report_template': cls.edi_report.id,
                'report_name': '''PO_${(object.name or '').replace('/', '_')}''',
                'conc_attach': 'many_one',
            }
        )


    def testSendEDIResponse(self):
        self.partner.update(
            {
                'edi_template': self.edi_template,
                'mail_template': None,
            }
        )

        self.assertEqual(
            self.edi_template.conc_attach, 'many_one',
            f'''Send EDI. Wrong default 'Attachment merge type' in new template'''
        )

        self.po1.action_rfq_send_lavka(edi_type='edi_response')
        last_message = self.env['mail.message'].search([], order='id desc')[0]

        self.assertEqual(
            last_message.subject,
            f'''RES-EDI-{self.po1.company_id.name} Order (Ref {self.po1.name or 'n/a'})''',
            f'Send EDI. Wrong subject of edi message'
        )

        self.assertEqual(
            last_message.message_type,
            'edi_response',
            f'Send EDI. Wrong type of edi message'
        )

        self.assertEqual(
            last_message.mail_server_id,
            self.edi_mail_server,
            f'Send EDI. Wrong mail server of edi message'
        )

        last_mail = self.env['mail.mail'].search([], order='id desc')[0]
        attachment = last_mail.attachment_ids[0]

        self.assertEqual(
            attachment.name,
            f'''RES-PO_{(self.po1.name or '').replace('/', '_')}.xml''',
            f'Send EDI. Wrong attachment name of edi message'
        )

        self.assertEqual(
            attachment.mimetype,
            'application/xml',
            f'Send EDI. Wrong attachment mimetype of edi message'
        )


