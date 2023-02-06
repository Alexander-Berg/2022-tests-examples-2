from odoo.tests.common import tagged, SavepointCase
from odoo.addons.queue_job.job import FAILED

@tagged('lavka', 'fail')
class TestUserDomain(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_group = cls.env.ref('queue_job.group_queue_job_user')
        manager_group = cls.env.ref('queue_job.group_queue_job_manager')
        cls.users = cls.env['res.users']
        for i in range(2):
            curr_user = cls.users.create([{
                'login': f'test_{i}',
                'password': 'test',
                'partner_id': cls.env['res.partner'].create([{
                    'name': f'Test_{i}'
                }]).id
            }])
            cls.users += curr_user
        user_group.users += cls.users[0]
        manager_group.users += cls.users[1]

    def test_user_domain(self):
        domain = self.env['queue.job']._subscribe_users_domain()
        users = self.env["res.users"].search(domain)
        # проверим, что обычного пользователя для queue_job нет в рассылке
        self.assertTrue(self.users[0] not in users)

    def test_not_send_fail_message_on_testing(self):
        job_ = self.env["res.partner"].with_delay().create({"name": "test"})
        db_job = job_.db_record()
        db_job.state = FAILED
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('queue_job.mt_job_failed')
        message = self.env['mail.message'].search([('subtype_id', '=', subtype_id)])
        self.assertTrue(not message, 'Job Que fail message in testing mode')

