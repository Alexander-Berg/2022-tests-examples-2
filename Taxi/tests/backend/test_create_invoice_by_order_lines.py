from collections import defaultdict
from datetime import datetime, timedelta
import logging

from odoo.exceptions import AccessError
from odoo.tests import Form, tagged, SavepointCase
from odoo.addons.lavka.tests.utils import assertEqualFloat


_logger = logging.getLogger(__name__)


@tagged('lavka', 'CreateInvoice')
class TestCreateInvoiceBySeveralOrders(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=2)
        cls.purchase_requsition2 = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'),
            force_create=True,
        )
        cls.partner = cls.purchase_requsition2.vendor_id
        cls.partner2 = cls.env['res.partner'].create({'name': 'John Doe 2'})
        cls.purchase_requsition2_with_oebs = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids'),
            force_create=True,
        )
        cls.purchase_requsition2_with_oebs.write({
            'vendor_id': cls.partner2.id,
            'oebs_contract_id': cls.env['oebs.contract'].create({}).id,
        })
        cls.po1 = cls.factory.create_purchase_order(cls.products, cls.purchase_requsition2, cls.warehouses, qty=1)[0]
        cls.po2 = cls.factory.create_purchase_order(cls.products[:1], cls.purchase_requsition2_with_oebs, cls.warehouses, qty=1)[0]
        for po in (cls.po1, cls.po2):
            po.write({
                'date_planned': datetime.today(),
                'delivery_type': 'direct',
                'skip_check_before_invoicing': True,
            })
            cls.factory.confirm_po(po)

    def testCreateInvoice(self):

        invoices = self.po1.order_line[0].action_create_invoice_multi()

        self.assertTrue(
            invoices['res_id'] in self.po1.invoice_ids.ids,
            f'Create Invoice. No Invoice created.'
        )

        self.assertTrue(
            len(self.po1.invoice_ids[0].invoice_line_ids) == 1,
            f'Create Invoice. Wrong lines quantity in created Invoice.'
        )

        self.assertTrue(
            self.po1.invoice_ids[0].invoice_line_ids[0].quantity == self.po1.order_line[0].product_qty,
            f'Create Invoice. In invoice qty != qty in PO.'
        )

        self.assertTrue(
            self.po1.invoice_ids[0].invoice_line_ids[0].qty_diff == 0,
            f'Create Invoice. In draft invoice wrong qty_diff.'
        )

        self.env['ir.config_parameter'].set_param('auto_send_bill_to_oebs', True)
        self.po1.invoice_ids[0].action_post(force_post=True)

        self.assertTrue(
            self.po1.invoice_ids[0].invoice_line_ids[0].qty_diff == 0,
            f'Create Invoice. In posted invoice wrong qty_diff.'
        )

        invoices = self.po1.order_line[0].action_create_invoice_multi()
        confirmation = self.env['invoice.create.confirmation'].browse(invoices['res_id'])
        invoices = confirmation.action_confirm()


        tasks = self.env['queue.job'].search([('identity_key', 'like', 'BILL-to-OEBS')])
        self.assertTrue(len(tasks) == 1,
             f'Task for sending posted bill to OEBS was not created.'
         )

        self.assertTrue(
            invoices['res_id'] in self.po1.invoice_ids.ids,
            f'Create Invoice. No double Invoice created.'
        )

        self.assertTrue(
            len(self.po1.invoice_ids[1].invoice_line_ids) == 1,
            f'Create Invoice. Wrong lines quantity in created double Invoice.'
        )

        self.assertTrue(
            self.po1.invoice_ids[1].invoice_line_ids[0].quantity == 0,
            f'Create Invoice. In double invoice qty != 0.'
        )

        self.po1.update({'invoice_ids': self.env['account.move']})
        self.po2.update({'invoice_ids': self.env['account.move']})

        # several partners
        order_lines = self.po1.order_line + self.po2.order_line
        error_string = 'You have choose order lines for different partners, it\'s possible to create invoice only for one partner at a time.'
        with self.assertRaises(Exception) as context:
            invoices = order_lines.action_create_invoice_multi()
        self.assertEqual(
            error_string,
            context.exception.args[0],
            f'Create Invoice.. Create invoice with different partners raise wrong exception.'
        )

        for oline in order_lines:
            oline.update({'invoice_lines': self.env['account.move.line']})

        self.partner2.update({'parent_id': self.partner.id})
        invoices = order_lines.action_create_invoice_multi()
        self.assertTrue(
            isinstance(invoices['res_id'], int),
            f'Create Invoice. Invoice for subvendor and parent lines not created.'
        )

        invoice = self.env['account.move'].browse(invoices['res_id'])
        self.assertTrue(
            invoice.partner_id == self.partner,
            f'Create Invoice. Wrong invoice partner for subvendor PO.'
        )

        invoice = self.env['account.move'].browse(invoices['res_id'])
        product = self.env['product.product'].create({
            'wms_id': '1', 'name': 'test'
        })
        invoice.invoice_line_ids[0].update({
            'product_id': product,
            'tax_ids': False
        })
        error_string = f"The Taxes field is not filled in '{product.name}'. Confirm is not possible"
        with self.assertRaises(Exception) as context:
            invoice.approve()

        self.assertTrue(error_string == context.exception.args[0])

        # check compute_selected_contract
        pids = invoice.purchase_order_ids
        invoice.purchase_order_ids = self.env['purchase.order']
        invoice._compute_selected_contract()
        self.assertFalse(invoice.selected_contract)

        invoice.purchase_order_ids = pids
        invoice.purchase_order_ids[0].requisition_id = self.purchase_requsition2_with_oebs
        invoice.purchase_order_ids[1].requisition_id = self.purchase_requsition2
        self.assertTrue(invoice.purchase_order_ids[0].requisition_id.oebs_contract_id.id != False)
        self.assertFalse(invoice.purchase_order_ids[1].requisition_id.oebs_contract_id.id)
        invoice._compute_selected_contract()
        self.assertFalse(invoice.selected_contract)

        invoice.purchase_order_ids[1].requisition_id = self.purchase_requsition2_with_oebs
        self.assertTrue(invoice.purchase_order_ids[1].requisition_id.oebs_contract_id.id != False)
        invoice._compute_selected_contract()
        self.assertTrue(invoice.selected_contract)

@tagged('lavka', 'CombineBills')
class TestCombineBills(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=8)
        cls.purchase_requsition2 = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        p_orders = cls.factory.create_purchase_order(cls.products, cls.purchase_requsition2, cls.warehouses, qty=2)
        for po in p_orders:
            po.write({
                'date_planned': datetime.today(),
                'skip_check_before_invoicing': True,
            })
            cls.factory.confirm_po(po)
        cls.po1, cls.po2 = p_orders
        partner = cls.env['res.partner'].create({'name': 'John Doe 2'})
        cls.purchase_requsition3 = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )
        cls.purchase_requsition3.vendor_id = partner
        cls.po3 = cls.factory.create_purchase_order(cls.products, cls.purchase_requsition3, cls.warehouses,
                                                    qty=1)[0]
        cls.po3.write({
            'date_planned': datetime.today(),
            'skip_check_before_invoicing': True,
        })
        cls.factory.confirm_po(cls.po3)
        c = 1

    def test_combine_bills(self):
        self.po1.action_create_invoice()
        self.po2.action_create_invoice()

        source_bills = self.env['account.move'].search([('move_type', '=', 'in_invoice')])
        source_bills_line_names = [x.name for x in source_bills[0].line_ids + source_bills[1].line_ids]
        source_bills_PO_ids = [x.purchase_order_ids for x in source_bills]
        source_bills.action_combine_bills()
        new_bill = self.env['account.move'].search([('move_type', '=', 'in_invoice')])

        for _ in new_bill.line_ids:
            self.assertTrue(
                _.name in source_bills_line_names,
                f'Combine bills. Not all lines combined.'
            )

        for _ in new_bill.purchase_order_ids:
            self.assertTrue(
            _ in source_bills_PO_ids,
            f'Combine bills. Not all PO combined.'
        )

    def test_error_combine_bills_for_different_partners(self):
        self.po1.action_create_invoice()
        self.po2.action_create_invoice()
        self.po3.action_create_invoice()

        source_bills = self.env['account.move'].search([('move_type', '=', 'in_invoice')])

        error_string = 'You have choose bills for different partners, it\'s possible to combine bills only for one partner.'
        with self.assertRaises(Exception) as context:
            source_bills.action_combine_bills()
        self.assertEqual(
            error_string,
            context.exception.args[0],
            f'Combine bills. Combine bills with different partners raise wrong exception.'
        )

@tagged('lavka', 'GroupLine')
class TestGroupLine(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.assertEqualFloat = assertEqualFloat

        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=5)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )

        cls.admin_user = cls.env.ref('base.user_root')

        for line in cls.purchase_requisition.line_ids:
            line.with_user(cls.admin_user).set_approve_tax()
            line.with_user(cls.admin_user).set_approve_price()
            line.sudo()._compute_approve()

        cls.po1 = cls.factory.create_purchase_order(cls.products[:5], cls.purchase_requisition, cls.warehouses, qty=1)[0]
        cls.po2 = cls.factory.create_purchase_order(cls.products[3:5], cls.purchase_requisition, cls.warehouses, qty=1)[0]
        cls.count_lines = len(cls.po1.order_line) + len(cls.po2.order_line)
        cls.count_grouped_lines = len(list(set(cls.po1.order_line.mapped('product_id.id')+cls.po2.order_line.mapped('product_id.id'))))
        _logger.info(f'lines in po:{cls.count_lines}, expect grouped:{cls.count_grouped_lines}')
        for po in cls.po1 + cls.po2:
            _mark = 'mark'
            po.state = 'purchase'
            for line in po.order_line:
                line.mark = _mark
                line.price_unit += 15
            pickings = po._create_picking_from_wms(po.order_line)
            cls.env['wms_integration.order'].complete_picking(pickings[0], datetime.now(), 'some_order_id')
            po.state = 'done'
            po.skip_check_before_invoicing = True
        cls.po1.action_create_invoice()
        cls.move = cls.po1.invoice_ids
        cls.oebs_contract = cls.env['oebs.contract'].create({})

        cls.oebs_supplier = cls.env['oebs.supplier'].create({})
        cls.move.partner_id.oebs_supplier_id = cls.oebs_supplier
        cls.move.partner_id.team_id = cls.env['crm.team'].create({
            'name': 'Test Sales Team',
            'user_id': cls.admin_user.id
        })
        cls.po2.with_context(bill_id=cls.move.id).order_line.add_multiple_invoice_lines_for_bill()

        cls.tax_15 = cls.move.invoice_line_ids[0].tax_ids
        cls.tax_20 = cls.env['account.tax'].create({
            'type_tax_use': 'purchase',
            'name': '20%',
            'oebs_tax_code': 123456,
            'amount': 20
        })

    def test_calculate_product_lines(self):
        move = self.move
        self.assertEqual(move.group_line_ids.product_id, move.invoice_line_ids.product_id)
        calc_groups = defaultdict(lambda: self.env['account.move.line'])
        for invoice in move.invoice_line_ids:
            calc_groups[invoice.product_id] += invoice

        for group in move.group_line_ids:
            key = group.product_id
            calc_group = calc_groups[key]
            self.assertEqualFloat(group.quantity, sum(calc_group.mapped('quantity')))

            calc_prices = calc_group.mapped('price_unit')
            avg_price = sum(calc_prices) / len(calc_prices)
            self.assertEqualFloat(group.price_unit, avg_price)

            self.assertEqual(group.vendor_product_code, calc_group.mapped('vendor_product_code')[0])
            self.assertEqual(group.vendor_product_name, calc_group.mapped('vendor_product_name')[0])

            self.assertEqualFloat(group.wo_vat_sum, sum(calc_group.mapped('wo_vat_sum')))
            self.assertEqualFloat(group.amount_currency, sum(calc_group.mapped('amount_currency')))
            self.assertEqual(group.tax_ids, calc_group.tax_ids)

    def test_on_change_invoice_line(self):
        move = self.move
        invoice_lines = move.invoice_line_ids
        qunaitity_list = [3, 4, 5, 10, 20, 7, 44]
        move.invoice_line_ids.tax_ids = self.tax_15
        move.invoice_line_ids.wo_vat_changed = False
        move_form = Form(move)
        self.assertEqual(len(invoice_lines), self.count_lines)
        for i, _ in enumerate(invoice_lines):
            with move_form.invoice_line_ids.edit(i) as line_form:
                line_form.quantity = qunaitity_list[i]
                line_form.save()
                self.assertEqualFloat(line_form.amount_currency, line_form.quantity * line_form.price_unit)
                self.assertEqualFloat(line_form.wo_vat_sum, (self.tax_15.amount / 100) * line_form.amount_currency)
        move_form.save()

        for group in move.group_line_ids:
            filtered_invoice_lines = move.invoice_line_ids.filtered(lambda x: x.product_id == group.product_id)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('wo_vat_sum')), group.wo_vat_sum)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('amount_currency')), group.amount_currency)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('quantity')), group.quantity)
            avg_price = sum(filtered_invoice_lines.mapped('price_unit')) / len(filtered_invoice_lines.mapped('price_unit'))
            self.assertEqualFloat(avg_price, group.price_unit)

        invoice_lines = move.invoice_line_ids
        price_list = [302, 105, 11, 109, 202, 770, 20.5]
        move.invoice_line_ids.tax_ids = self.tax_15
        move.invoice_line_ids.wo_vat_changed = False
        move_form = Form(move)
        self.assertTrue(len(invoice_lines) == self.count_lines)
        for i, _ in enumerate(invoice_lines):
            with move_form.invoice_line_ids.edit(i) as line_form:
                line_form.price_unit = price_list[i]
                line_form.save()
                self.assertEqualFloat(line_form.amount_currency, line_form.quantity * line_form.price_unit)
                self.assertEqualFloat(line_form.wo_vat_sum, (self.tax_15.amount / 100) * line_form.amount_currency)
        move_form.save()

        for group in move.group_line_ids:
            filtered_invoice_lines = move.invoice_line_ids.filtered(lambda x: x.product_id == group.product_id)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('wo_vat_sum')), group.wo_vat_sum)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('amount_currency')), group.amount_currency)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('quantity')), group.quantity)
            avg_price = sum(filtered_invoice_lines.mapped('price_unit')) / len(
                filtered_invoice_lines.mapped('price_unit'))
            self.assertEqualFloat(avg_price, group.price_unit)

    def test_onchange_product_line(self):
        move = self.move
        move_form = Form(move.with_context({'manual_edit': True}))
        for i, _ in enumerate(move.group_line_ids):
            with move_form.group_line_ids.edit(i) as line_form:
                line_form.tax_ids.clear()
                line_form.tax_ids.add(self.tax_20)
                line_form.save()
                self.assertEqualFloat(line_form.wo_vat_sum, (self.tax_20.amount / 100) * line_form.amount_currency)
            # onchange groups_line
            move_form.save()
            filtered_invoice_lines = move.invoice_line_ids.filtered(lambda x: x.product_id == line_form.product_id)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('wo_vat_sum')), line_form.wo_vat_sum)
            quantity_total = sum(filtered_invoice_lines.mapped('quantity'))
            for invoice in filtered_invoice_lines:
                coef = invoice.quantity / quantity_total
                self.assertEqualFloat(invoice.wo_vat_sum, coef * line_form.wo_vat_sum)

        wo_vat_sum = [30, 100, 500, 0, 205]
        self.assertEqual(len(move.group_line_ids), self.count_grouped_lines)
        move_form = Form(move.with_context({'manual_edit': True}))
        for i, _ in enumerate(move.group_line_ids):
            with move_form.group_line_ids.edit(i) as line_form:
                line_form.wo_vat_changed = True
                line_form.wo_vat_sum = wo_vat_sum[i]
                line_form.save()
            move_form.save()
            filtered_invoice_lines = move.invoice_line_ids.filtered(lambda x: x.product_id == line_form.product_id)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('wo_vat_sum')), line_form.wo_vat_sum)
            quantity_total = sum(filtered_invoice_lines.mapped('quantity'))
            for invoice in filtered_invoice_lines:
                coef = invoice.quantity / quantity_total
                self.assertEqualFloat(invoice.wo_vat_sum, coef * line_form.wo_vat_sum)
                self.assertTrue(invoice.wo_vat_changed)

        amount_currencies = [30, 100, 500, 1, 205]
        self.assertTrue(len(move.group_line_ids) == self.count_grouped_lines)
        move_form = Form(move.with_context({'manual_edit': True}))
        for i, _ in enumerate(move.group_line_ids):
            with move_form.group_line_ids.edit(i) as line_form:
                line_form.amount_currency = amount_currencies[i]
                line_form.save()
            move_form.save()
            filtered_invoice_lines = move.invoice_line_ids.filtered(lambda x: x.product_id == line_form.product_id)
            self.assertEqualFloat(sum(filtered_invoice_lines.mapped('amount_currency')), line_form.amount_currency)
            quantity_total = sum(filtered_invoice_lines.mapped('quantity'))
            for invoice in filtered_invoice_lines:
                coef = invoice.quantity / quantity_total
                self.assertEqualFloat(invoice.amount_currency, coef * line_form.amount_currency)

    def test_calc_tax_and_amount(self):
        move = self.move

        move_form = Form(move)
        for i, _ in enumerate(move.invoice_line_ids):
            with move_form.invoice_line_ids.edit(i) as line_form:
                line_form.tax_ids.clear()
                line_form.tax_ids.add(self.tax_20)
                line_form.save()
                self.assertEqualFloat(line_form.wo_vat_sum, (self.tax_20.amount / 100) * line_form.amount_currency)
            move_form.save()
            break

        tax_total = defaultdict(float)
        amount_untaxed = 0.0
        for line in move.invoice_line_ids:
            self.assertEqual(len(line.tax_ids), 1)
            tax_total[line.tax_ids.name] += line.wo_vat_sum
            amount_untaxed += line.amount_currency
        tax_total['All taxes'] = sum(tax_total.values())

        ALL_TAXES = 1
        self.assertEqual(len(move.amount_by_group), len(move.invoice_line_ids.tax_ids) + ALL_TAXES)
        for tax_group in move.amount_by_group:
            name, total = tax_group[0], tax_group[1]
            self.assertEqual(tax_total[name], total)
        self.assertEqualFloat(move.amount_untaxed, amount_untaxed)
        self.assertEqualFloat(move.amount_total, amount_untaxed + tax_total['All taxes'])

    def test_compute_oebs_requisiton_and_compute_svl_date(self):
        # Падает на контстрейте, что requisition_id должен быть заполнен.

        # self.move.purchase_order_ids.requisition_id = None
        # self.move._compute_oebs_requisition()
        # self.assertEqual(self.move.requisition_id, self.env['purchase.requisition'])
        # self.assertEqual(self.move.oebs_contract_id, self.env['oebs.contract'])

        self.move.purchase_order_ids.requisition_id = self.purchase_requisition
        self.move.purchase_order_ids.requisition_id.oebs_contract_id = self.oebs_contract
        self.move._compute_oebs_requisition()

        self.assertEqual(self.move.oebs_contract_id, self.oebs_contract)
        self.assertEqual(self.move.requisition_id, self.purchase_requisition)

        #related field
        self.assertEqual(self.move.oebs_supplier_id, self.oebs_supplier)
        #
        self.move._compute_svl_date()
        self.assertEqual(self.move.svl_date, False)

        self.move.approve(True) #confirm bill
        self.move.approval_ids.approval_user = self.admin_user
        self.move.approval_ids.with_user(self.admin_user).approve_line()
        self.move.approve(True)
        self.move._compute_svl_date()
        self.assertEqual(self.move.svl_date, self.move.stock_valuation_layer_ids[0].document_datetime.date())

    def test_compute_payments(self):
        self.move.approve(True)
        self.move.approval_ids.approval_user = self.admin_user
        self.move.approval_ids.with_user(self.admin_user).approve_line()
        self.move.approve(True)

        partner = self.move.partner_id
        self.assertEqual(partner.count_of_payments, 0)

        action = partner.action_view_payments()
        self.assertEqual([('id', 'in', [])], action['domain'])

        wizard = Form(self.env['account.payment.register'].with_context(self.move.action_register_payment()['context'])).save()
        meta = wizard.action_create_payments()
        payment = self.env['account.payment'].browse(meta.get('res_id'))
        payment.action_post()
        self.assertTrue(payment.state, 'posted')
        partner._compute_payments()

        self.assertEqual(self.move.payment_date, payment.date)
        self.assertEqual(partner.count_of_payments, 1)

        action = partner.action_view_payments()
        self.assertEqual([('id', 'in', [payment.id])], action['domain'])

    def test_reset_to_draft(self):
        move = self.move
        move.approve(True)
        some_user = self.env['res.users'].create({
            'name': 'some',
            'login': 'some',
            'groups_id': self.env.ref('lavka.group_accountant').ids,
        })
        move.approval_ids.approval_user = some_user

        with self.assertRaises(AccessError):
            move.is_approver(self.admin_user)

        with self.assertRaises(AccessError):
            move.with_user(self.admin_user).set_to_draft()

        move.approval_ids.approval_user = self.admin_user
        action = move.with_user(self.admin_user).set_to_draft()
        model = action['res_model']
        self.assertEqual(model, 'account.move.confirmation')
        wiz = Form(self.env[model].with_context(active_id=move.id)).save()
        wiz.to_draft()

        self.assertEqual(move.state, 'draft')
        self.assertEqual(len(move.approval_ids), 0)
        self.assertEqual(move.approve_requested, False)
        self.assertEqual(move.approves_count, 0)
        self.assertEqual(move.approval_state, 'approved')


@tagged('lavka', 'CreatorBill')
class TestGroupLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=1)
        cls.products = cls.factory.create_products(cls.warehouses, qty=5)
        cls.purchase_requisition = cls.factory.create_purchase_requisition(
            cls.products,
            geo_tag=cls.warehouses.mapped(
                'warehouse_tag_ids')
        )

        cls.admin_user = cls.env.ref('base.user_root')

        cls.po1 = cls.factory.create_purchase_order(cls.products[:5], cls.purchase_requisition, cls.warehouses, qty=1)[0]
        for line in cls.po1.order_line:
            line.qty_received = line.product_init_qty
        _mark = 'mark'
        cls.po1.state = 'purchase'

        for line in cls.po1.order_line:
            line.mark = _mark
            line.price_unit += 15
        pickings = cls.po1._create_picking_from_wms(cls.po1.order_line)
        cls.po1.date_planned = datetime.now()
        cls.env['wms_integration.order'].complete_picking(pickings[0], datetime.now(), 'some_order_id')
        cls.po1.state = 'done'
        cls.po1.skip_check_before_invoicing = True

    def test_creator_of_bill(self):
        creator = self.env['creator.bill'].create({})

        creator_form = Form(creator)
        creator_form.vendor_id = self.po1.partner_id

        creator_form.creator_bill_line_ids
        creator_form.save()
        self.assertEqual(len(creator.creator_bill_line_ids.product_id), len(self.po1.order_line.product_id))

        to_add_po_lines = self.env['purchase.order.line']

        for creator_line, po_product in zip(creator.creator_bill_line_ids, self.po1.order_line.product_id):
            self.assertEqual(creator_line.rfq_qty, sum(po_product.purchase_order_line_ids.mapped('product_init_qty')))
            self.assertEqual(creator_line.qty_received, sum(po_product.purchase_order_line_ids.mapped('qty_received')))
            creator_line.selected = True
            creator_line.fill_qty_required()
            for po_line in po_product.purchase_order_line_ids:
                if sum(po_line.mapped('qty_to_invoice')) <= creator_line.qty_required:
                    to_add_po_lines += po_line


        creator.set_po_lines()

        self.assertEqual(len(creator.order_line), len(to_add_po_lines))
        self.assertEqual(sum(creator.order_line.mapped('qty_to_invoice')), sum(to_add_po_lines.mapped('qty_to_invoice')))

        creator.create_bill()
