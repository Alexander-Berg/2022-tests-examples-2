import logging
from odoo.tests import tagged
from odoo.tests.common import SavepointCase, Form

_logger = logging.getLogger(__name__)
USER_DEMO = "base.user_admin"

@tagged('lavka', 'user_readonly')
class TestTeamRights(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        team = cls.env['crm.team'].search([])[0]
        cls.partner = cls.env['res.partner'].create({
            'company_type':'company',
            'name': 'Test Purchaser',
            'team_id': team.id,
            'email':'test@yandex.ru',
            'vat': '3213213213213',
            'city': 'Moscow',
            'country_id': cls.env['res.country'].search([], limit=1).id
        })

        cls.admin_user = cls.env.ref(USER_DEMO)


    def test_ro_rights(self):

        partner_form = Form(self.partner.with_user(self.admin_user))
        partner_form.name = 'New name'
        partner_form.save()

        ro_group = self.env.ref('lavka.group_readonly_user')
        ro_group.users += self.admin_user

        partner_form = Form(self.partner.with_user(self.admin_user))
        with self.assertRaises(Exception):
            partner_form.name = 'New name 2'
