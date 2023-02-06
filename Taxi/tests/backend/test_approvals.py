import logging
import time
from random import randrange
from unittest.mock import patch

from common.client.wms import WMSConnector
from freezegun import freeze_time
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase, tagged, Form
from odoo.addons.lavka.tests.utils import get_products_from_csv, read_json_data

_logger = logging.getLogger(__name__)


@tagged('lavka', 'appr')
class TestApprovals(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestApprovals, cls).setUpClass()

        cls.team_lead = cls.env['res.users'].create({
            'name': 'test_lead',
            'login': 'test_lead',
            'password': 'test_lead',
        })

        cls.team = cls.env['crm.team'].create({
            'name': 'test_team',
            'company_id': False,
            'user_id': cls.team_lead.id
        })

    #   новый
        cls.env['ir.config_parameter'].set_param('sleep', 'false')
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=6)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.partner = cls.env['res.partner'].create({'name': 'Vendor', 'team_id': cls.team.id})
        cls.purchase_requisition.vendor_id = cls.partner

        cls.pos = cls.factory.create_purchase_order(cls.products, cls.purchase_requisition, cls.warehouses, qty=1)
        for po in cls.pos:
            po.write({'skip_check_before_invoicing': True})

        # no team
        cls.partner_no_team = cls.env['res.partner'].create({'name': 'Vendor_no_team'})


        cls.factory.confirm_po(cls.pos)

    def test_approvals_belongs_to_its_masters(self):

        po = self.pos[0]
        po.skip_check_before_invoicing = True
        po.action_create_invoice()
        acc_moves = self.env['account.move'].search([])
        acc_moves._compute_purchase_orders_ids()
        for invoice in acc_moves:
            move_form = Form(invoice)
            move_form.ref = 'bla2313ds'
            move_form.invoice_date = fields.Date.today()
            for i, _ in enumerate(invoice.invoice_line_ids):
                line_form = move_form.invoice_line_ids.edit(i)
                line_form.price_unit += 5
                line_form.save()
            move_form.save()
            invoice.approve(force_post=True)
            self.assertEqual(invoice.state, 'to_approve')

        approvals = self.env['approval.line'].search([])
        for ap in approvals:

            self.assertEqual(ap.res_model, invoice._name)
            self.assertIsNotNone(invoice.approval_ids)
            self.assertEqual(len(po.approval_ids), 0)
            ap.approval_user = self.env.user
            # проходит локально, но в тимсити падает
            # app_form = Form(ap)
            # app_form.approval_user = self.env.user
            # app_form.to_approve = True
            # app_form.save()
            ap.to_approve = True

        for invoice in acc_moves:
            self.assertEqual(invoice.state, 'to_approve')
            task = self.env['queue.job'].search([])
            self.assertEqual(task[0].identity_key, f'{invoice.partner_id}_{invoice.id}')
            self.assertTrue(len(invoice.mapped('stock_valuation_layer_ids')) == 0)

        c = 1
    #
    # def test_approvals_price_difference_01(self):
    #
    #     po = self.pos[0]
    #     po.skip_check_before_invoicing = True
    #     po.action_create_invoice()
    #
    #     acc_moves = self.env['account.move'].search([])
    #     for invoice in acc_moves:
    #         move_form = Form(invoice)
    #         move_form.ref = 'bla2313ds2'
    #         move_form.invoice_date = fields.Date.today()
    #         for i, _ in enumerate(invoice.invoice_line_ids):
    #             line_form = move_form.invoice_line_ids.edit(i)
    #             line_form.price_unit = line_form.price_unit * 1.005
    #             line_form.save()
    #         move_form.save()
    #         invoice.purchase_order_ids += invoice.purchase_order_id
    #         invoice.approve(force_post=True)
    #
    #     approvals = self.env['approval.line'].search([])
    #     for ap in approvals:
    #         self.assertEqual(ap.approval_reason, 'price_0.1')
    #     c = 1
    #
    # def test_approvals_price_difference_1(self):
    #
    #     po = self.pos[0]
    #     po.action_create_invoice()
    #     acc_moves = self.env['account.move'].search([])
    #     for invoice in acc_moves:
    #         move_form = Form(invoice)
    #         move_form.ref = 'bla2313ds'
    #         move_form.invoice_date = fields.Date.today()
    #         for i, _ in enumerate(invoice.invoice_line_ids):
    #             line_form = move_form.invoice_line_ids.edit(i)
    #             line_form.price_unit = line_form.price_unit * 1.2
    #             line_form.quantity += 1
    #             line_form.save()
    #         move_form.save()
    #         invoice.purchase_order_ids += invoice.purchase_order_id
    #         _logger.info(f'WHEEE - {invoice.purchase_order_ids}')
    #         invoice.approve()
    #
    #     approvals = self.env['approval.line'].search([])
    #     reasons = {i.approval_reason: i for i in approvals}
    #
    #     self.assertIsNotNone(reasons['price_1.0'])
    #     self.assertIsNotNone(reasons['quantity'])
    #
    #     for i in approvals:
    #         i.with_user(self.team_lead).approve_line()
    #         self.assertEqual(i.state, 'approved')
    #
    #     # check msg from bot
    #     bot = self.env.ref('odoo_debrand.bot_approver')
    #     channel_name = '%s, %s' % (self.team_lead.name, bot.name)
    #     channel = self.env['mail.channel'].search([('name', 'like', channel_name)])
    #     self.assertTrue(channel.id != False)
    #     msg = (
    #                 f'<p>Your confirmation is required in the document \n'
    #                 f'You can follow the link '
    #                 f'<b> <a href="{i.share_link.replace("&", "&amp;")}">Vendor: {self.partner.name} {acc_moves.ref}</a></b></p>'
    #             )
    #     self.assertTrue(msg in channel.message_ids.mapped('body'))
    #
    def test_check_approval_team_lead(self):
        self.purchase_requisition.vendor_id = self.partner_no_team
        po = self.factory.create_purchase_order(self.products, self.purchase_requisition, self.warehouses, qty=1)[0]
        self.factory.confirm_po([po])
        po.skip_check_before_invoicing = True
        po.action_create_invoice()
        acc_moves = self.env['account.move'].search([])
        # self.partner.update({'team_id': None})
        err = f'The purchase from supplier {self.partner_no_team.name} team is not filled in'
        for invoice in acc_moves:
            move_form = Form(invoice)
            move_form.ref = 'bla2313ds'
            move_form.invoice_date = fields.Date.today()
            for i, _ in enumerate(invoice.invoice_line_ids):
                line_form = move_form.invoice_line_ids.edit(i)
                line_form.price_unit = line_form.price_unit * 1.2
                line_form.quantity += 1
                line_form.save()
            move_form.save()
            with self.assertRaises(UserError) as context:
                invoice.approve(force_post=True)
            self.assertEqual(err, context.exception.args[0])
            self.purchase_requisition.vendor_id = self.partner
