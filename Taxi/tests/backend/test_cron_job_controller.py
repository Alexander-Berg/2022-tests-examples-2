import base64
import requests
from odoo.tests import tagged
from odoo.tests.common import HttpSavepointCase, get_db_name
from odoo.tools import config

@tagged("lavka", "cron_jobs")
class TestCronJobs(HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cron_jobs = cls.env['ir.cron'].search([
            ('active', 'in', [True, False])
        ])
        cls.job_ids = []
        for i, job in enumerate(cron_jobs):
            job.active = True
            job.suspended = False
            cls.job_ids.append(job.id)

        cls.demo_user = cls.env.ref('base.user_admin')
        cls.db_name = get_db_name()

    def request_by_token(self, user, authorized=True, *args, **kwargs):
        token = f"{self.db_name}:{user.openapi_token}"
        _token = base64.b64encode(token.encode()).decode()
        headers = {}
        if authorized:
            headers = {
                'Authorization': f'Basic {_token}',
            }
        p = kwargs.get("params")
        port = config["http_port"]
        url = f'http://localhost:{port}/api/v1/cron_jobs'
        self.opener = requests.Session()
        return self.opener.request(
            'GET', url, timeout=30, headers=headers, params=p
        )

    def test_jobs(self):
        # выключаем
        data = {
            "action": "suspend",
        }
        resp = self.request_by_token(self.demo_user, params=data)
        # self.env.cr.commit()
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        jobs = {i['job']: i for i in resp_data['jobs']}

        suspended_cron_jobs = self.env['ir.cron'].search([])
        for job in suspended_cron_jobs:
            self.assertTrue(job.suspended, job.name)
            self.assertFalse(job.active, job.name)
            info = jobs[job.cron_name]
            self.assertEqual(info['active'], job.active)
            self.assertEqual(info['suspended'], job.suspended)
        # включаем
        data = {
            "action": "active",
        }

        resp = self.request_by_token(self.demo_user, params=data)
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        jobs = {i['job']: i for i in resp_data['jobs']}
        active_cron_jobs = self.env['ir.cron'].search([])
        for job in active_cron_jobs:
            self.assertTrue(job.active)
            self.assertFalse(job.suspended)
            info = jobs[job.cron_name]
            self.assertEqual(info['active'], job.active)
            self.assertEqual(info['suspended'], job.suspended)
        # выключаем на всякий случай
        data = {
            "action": "suspend",
        }
        self.request_by_token(self.demo_user, params=data)


