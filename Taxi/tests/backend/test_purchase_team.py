
import uuid
import logging
from odoo.exceptions import AccessError
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase, Form

_logger = logging.getLogger(__name__)
rnd = lambda x: f'{x}-{uuid.uuid4().hex}'


# use as example
@tagged('lavka', 'team')
class TestTeamRights(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.products = cls.env['product.product']
        for i in range(10):
            cls.products += cls.products.create(
                {
                    'name': f'test_product_{i}',
                    'default_code': f'code_{i}',
                    'type': 'product',
                    'wms_id': f'wms_id_{i}',
                    'taxes_id': 1,
                }
            )

        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': f'test_wh_1',
            'code': f'1234',
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'store_wms_id'
        })

        # создаем катманов
        cls.mapped_users = {}
        cls.users = cls.env['res.users']
        for i in range(8):
            curr_user = cls.users.create({
                'login': f'test_{i}',
                'password': 'test',
                'partner_id': cls.env['res.partner'].create({
                    'name': f'Test_{i}'
                }).id
            })

            cls.users += curr_user
            groups = curr_user.groups_id.mapped('display_name')
            cls.mapped_users[i] = curr_user
            _logger.debug(f'CREATED USER {curr_user.name} with groups {groups}')

        # создаем пользователя, который может аппрувить налог
        cls.buh = cls.users.create({
            'login': f'test_buh',
            'password': 'test_buh',
            'partner_id': cls.env['res.partner'].create({
                'name': f'Test_buh'
            }).id
        })
        buhs = cls.env.ref('account.group_account_manager')
        buhs.users += cls.buh



        # первая команда
        team_form = Form(cls.env['crm.team'])
        team_form.user_id = cls.mapped_users[0]
        team_form.name = 'Purchase'
        for i in range(1, 4):
            with team_form.team_members.new() as line_form:
                line_form.member_id = cls.mapped_users[i]
                if i == 2:
                    line_form.vice = True
        cls.team = team_form.save()

        for mem in cls.team.team_members:
            if not mem.vice:
                cls.just_purch = mem.member_id
                break

        # вторая команда
        team_form2 = Form(cls.env['crm.team'])
        team_form2.user_id = cls.mapped_users[4]
        team_form2.name = 'Purchase 2'
        for i in range(4, 8):
            with team_form2.team_members.new() as line_form:
                line_form.member_id = cls.mapped_users[i]
                if i == 5:
                    line_form.vice = True
        cls.team2 = team_form2.save()

        # создаем прайсы
        # нормальный активный без аппрувов
        cls.partner_team = cls.env['res.partner'].create({
            'name': 'Vendor',
            'team_id': cls.team.id,
        })

        cls.partner_team_2 = cls.env['res.partner'].create({
            'name': 'Vendor',
            'team_id': cls.team2.id,
        })

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_team.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.purchase_requsition_2 = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner_team_2.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })

        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'price_unit': 11.1,
            'start_date': fields.Datetime.today(),
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products]

        for r in cls.requsition_lines:
            r._compute_approve()

        for r in cls.requsition_lines:
            r.price_unit += 3
            r._compute_approve()

        _logger.debug(f'Normal Active Purchase requsition  {cls.purchase_requsition.id} confirmed')

        cls.requsition_lines_2 = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'price_unit': 11.1,
            'start_date': fields.Datetime.today(),
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition_2.id,
            'product_qty': 1,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products]

        for r in cls.requsition_lines_2:
            r._compute_approve()

        for r in cls.requsition_lines_2:
            r.price_unit += 3
            r._compute_approve()

    def test_team(self):

        can_approve_price_group = self.env.ref('lavka.group_approve_price')
        team_leader_group = self.env.ref('lavka.group_team_leader')
        # проверим, что создалось member_ids
        self.assertEqual(len(self.team.member_ids), 3)

        # у тимлида должно быть допом две группы
        self.assertTrue(can_approve_price_group in self.mapped_users[0].mapped('groups_id'))
        self.assertTrue(team_leader_group in self.mapped_users[0].mapped('groups_id'))

        # у зама одна!
        self.assertTrue(can_approve_price_group in self.mapped_users[2].mapped('groups_id'))
        self.assertFalse(team_leader_group in self.mapped_users[2].mapped('groups_id'))

        # убираем
        team_form_1 = Form(self.team)
        for i, _ in enumerate(self.team.team_members):
            with team_form_1.team_members.edit(i) as line_form:
                if line_form.vice:
                    line_form.vice = False
        team_form_1.save()

        # теперь это никакой не зам!
        self.assertFalse(can_approve_price_group in self.mapped_users[2].mapped('groups_id'))
        self.assertFalse(team_leader_group in self.mapped_users[2].mapped('groups_id'))

        # ставим нового зама
        team_form_2 = Form(self.team)
        for i, _ in enumerate(self.team.team_members):
            with team_form_2.team_members.edit(i) as line_form:
                if i == 0:
                    line_form.vice = True
        team_form_2.save()

        # у зама одна!
        self.assertTrue(can_approve_price_group in self.mapped_users[1].mapped('groups_id'))
        self.assertFalse(team_leader_group in self.mapped_users[1].mapped('groups_id'))

        # поменяем тимлида
        team_form_3 = Form(self.team)
        team_form_3.user_id = self.mapped_users[3]
        team_form_3.save()

        # у старого не должно быть прав
        self.assertFalse(team_leader_group in self.mapped_users[0].mapped('groups_id'))
        self.assertFalse(can_approve_price_group in self.mapped_users[0].mapped('groups_id'))

        # а у нового должно!
        self.assertTrue(can_approve_price_group in self.mapped_users[3].mapped('groups_id'))
        self.assertTrue(team_leader_group in self.mapped_users[3].mapped('groups_id'))

        # обычный пользователь не может менять команду
        with self.assertRaises(Exception):
            self.team.with_user(self.mapped_users[0]).name = 'New name'

        with self.assertRaises(Exception):
            for line in self.team.team_members:
                line.with_user(self.mapped_users[0]).vice = True

        # тимлид может
        self.team.with_user(self.mapped_users[3]).name = 'New name'

        for line in self.team.team_members:
            line.with_user(self.mapped_users[3]).vice = True

        req_form = Form(self.requsition_lines[1], view=self.env.ref('lavka.pr_line_tree'))
        self.assertIsNotNone(req_form._view['fields'].get('diff_last_price'))

        admin_user = self.env['res.users'].search([('name', '=', 'Administrator')])

        # проверяем, что админ может редактировать агрименты и лайны
        self.purchase_requsition.with_user(admin_user).write({
            'name': 'new_name'
        })
        self.assertEqual(self.purchase_requsition.name, 'new_name')
        for line in self.requsition_lines:
            line.with_user(admin_user).write({
                'active': False
            })
        self.assertFalse(all([i.active for i in self.requsition_lines]), False)

        # проверяем что все юзеры могут читать лайны
        for curr_user in self.users:
            for line in self.requsition_lines:
                c = line.price_unit
            for line2 in self.requsition_lines_2:
                d = line2.price_unit
        c = 1

    def test_approve_rights(self):
        # обычный пользователь может менять цену и активность только у своей команды
        app = self.env.ref('lavka.group_approve_price')
        app.users -= self.just_purch
        app.users -= self.buh

        self.assertFalse(self.just_purch.has_group('lavka.group_approve_price'))
        self.assertFalse(self.just_purch.has_group('lavka.group_team_leader'))

        for line in self.purchase_requsition.line_ids:
            line.with_user(self.just_purch).write({
                'active': False,
                'price_unit': 1233,
            })

        # у чужой команды не может ничего сделать
        for not_his_line in self.purchase_requsition_2.line_ids:
            with self.assertRaises(Exception):
                not_his_line.with_user(self.just_purch).write({
                    'active': False,
                    'price_unit': 1233,
                })
        # проверим что бух может аппрувить налог
        self.assertTrue(self.buh.has_group('account.group_account_manager'))
        self.assertFalse(self.buh.has_group('lavka.group_approve_price'))
        self.assertFalse(self.buh.has_group('lavka.group_team_leader'))

        # сбрасываем аппрув налога
        for line in self.requsition_lines:
            line.approve_tax = False

        # Ставим налог под бухом
        for line in self.requsition_lines:
            line.with_user(self.buh).write({
                'approve_tax': True,
            })
        # сбрасываем аппрув налога
        for line in self.requsition_lines:
            line.approve_tax = False
        # без права - не можем
        self.env.ref('account.group_account_manager').users -= self.just_purch
        for line2 in self.requsition_lines:
            with self.assertRaises(Exception):
                line2.with_user(self.just_purch).write({
                    'approve_tax': True,
                })

    def test_approve_outgoing_tax(self):
        group_out_tax = self.env.ref('account.group_account_manager')
        group_out_tax.users -= self.buh
        self.assertFalse(self.buh.has_group('account.group_account_manager'))
        error_string = f"You don't have right: '{group_out_tax.name}'. You can ask to approve: \n"
        with self.assertRaises(AccessError) as context:
            self.products[0].with_user(self.buh).product_tmpl_id.tax_validate()
        self.assertTrue(
            context.exception.args[0].startswith(
                error_string
            )
        )
        with self.assertRaises(AccessError) as context:
            self.products[0].product_tmpl_id.with_user(self.buh).set_new_vat_tax_from_vendor_tax()
        self.assertTrue(
            context.exception.args[0].startswith(
                error_string
            )
        )
        with self.assertRaises(AccessError) as context:
            self.products[0].product_tmpl_id.with_user(self.buh).validation_failure()
        self.assertTrue(
            context.exception.args[0].startswith(
                error_string
            )
        )
