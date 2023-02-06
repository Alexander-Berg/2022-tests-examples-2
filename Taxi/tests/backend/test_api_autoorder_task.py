import datetime as dt
import logging
import random
from random import randrange
import requests
from odoo.addons.openapi.controllers import pinguin
from odoo.tests.common import HttpSavepointCase, get_db_name, tagged
from odoo.tools import config

from odoo.addons.lavka.tests.utils import get_products_from_csv

_logger = logging.getLogger(__name__)

USER_DEMO = "base.user_admin"
USER_ADMIN = "base.user_root"


@tagged("lavka", "api_autoorder_task")
class TestAutoorderTask(HttpSavepointCase):
    @classmethod
    def setUpClass(self):
        super(TestAutoorderTask, self).setUpClass()

        self.db_name = get_db_name()
        self.demo_user = self.env.ref(USER_DEMO)
        self.admin_user = self.env.ref(USER_ADMIN)
        self.model_name = 'autoorder.task'

    def request(self, method, url, auth=None, **kwargs):
        kwargs.setdefault("model", self.model_name)
        kwargs.setdefault("namespace", "autoorder_task")
        url = (
            "http://localhost:%d/api/v1/autoorder.task" % config["http_port"] + url
        ).format(**kwargs)
        self.opener = requests.Session()
        return self.opener.request(
            method, url, timeout=30, auth=auth, json=kwargs.get("data_json")
        )

    def request_from_user(self, user, *args, **kwargs):
        kwargs["auth"] = requests.auth.HTTPBasicAuth(self.db_name, user.openapi_token)
        return self.request(*args, **kwargs)

    def request_from_not_auth_user(self, *args, **kwargs):
        kwargs["auth"] = requests.auth.HTTPBasicAuth(self.db_name, 'some token')
        return self.request(*args, **kwargs)

    def test_create_autoorder_task(self):

        data = {
            "external_id": "12345",
            "func_name": "import_orders_from_yt",
            "namespace": "autoorder_task",
        }
        resp = self.request_from_user(self.demo_user, "POST", "", data_json=data)

        new_task = self.env['queue.job'].search([
            ('identity_key', 'like', '12345'),
            ('state', '!=', 'done')
        ])

        self.assertTrue(new_task, "New autooreder task is not created")

        data = {
            "external_id": "123456",
            "func_name": "import_orders_from_yt2",
            "namespace": "autoorder_task",
        }
        resp = self.request_from_user(self.demo_user, "POST", "", data_json=data)

        self.assertEqual(resp.status_code, 400)
        self.assertTrue(new_task, "Autooreder task with wrong name was created")

        resp = self.request_from_not_auth_user("POST", '', data_json=data)
        self.assertEqual(resp.status_code, 401, "Autooreder task for non authorized user was created")
