from collections import defaultdict
from unittest.mock import patch

from django import test
from django.conf import settings
from parameterized import parameterized

from l3common.tests.cases import override_celery_settings, patching
from . import test_fields
from .base import RESTAPITransactionTestCase
from .. import models


class NetworkViewTestCase(test.TestCase):
    @parameterized.expand(
        [
            ["87.250.0.0", "12", 1],
            ["87.250.254.0", "24", 1],
            ["87.250.254.128", "25", 1],
            ["87.250.0.0", "12%20", 0],
            ["87.250.254.0", "24%20", 0],
            ["87.250.254.128", "25%20", 0],
        ]
    )
    def test_spaces_in_request(self, search, mask, result_total):
        ip = "87.250.254.0/24"
        models.LocationNetwork.objects.create(ip=ip, location=[models.LocationNetwork.LOCATION_CHOICES.MAN])
        c = test.Client()
        response = c.get(f"/api/v1/network?_search={search}/{mask}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], result_total)
        if result_total:
            self.assertEqual(response.json()["objects"][0]["ip"], ip)


class StatesReadOnlyTestCase(RESTAPITransactionTestCase):
    databases = [settings.RO_DATABASE, "default"]
    ACTIVE = "ACTIVE"

    def setUp(self):
        self.service: models.Service = models.Service.objects.create(
            abc="dostavkatraffika", fqdn="l3.tt.yandex-team.ru"
        )
        self.balancer: models.LoadBalancer = models.LoadBalancer.objects.create(
            state=models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[
                models.LocationNetwork.LOCATION_CHOICES.SAS,
            ],
            fqdn="sas1-2lb3b.yndx.net",
            test_env=False,
        )
        self.rs: models.RealServer = models.RealServer.objects.create(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            config={},
            location=[models.LocationNetwork.LOCATION_CHOICES.SAS],
        )
        self.vs: models.VirtualServer = models.VirtualServer.objects.create(
            service=self.service,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port=3663,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            lb_ids=[self.balancer.pk],
            rs_ids=[self.rs.id],
            config=test_fields.make_config(URL="/api/v1/clusters", STATUS_CODE=200),
            ext_id="c10e564e78e07f371c4f8397d17922061c5e7cc481a88a0cbc81c700ce161df9",
        )
        self.configuration: models.Configuration = models.Configuration.objects.create(
            service=self.service,
            vs_ids=[self.vs.id],
            description="1th-testing",
            state=models.Configuration.STATE_CHOICES.ACTIVE,
        )
        self.client = test.Client()

    def assertActive(self, state):
        self.assertEqual(state, self.ACTIVE)

    @parameterized.expand(
        [
            ["vs/{vs_id}"],
            ["service/{service_id}/vs/{vs_id}"],
            ["service/{service_id}/vs/c10e564e78e07f371c4f8397d17922061c5e7cc481a88a0cbc81c700ce161df9"],
            ["vs/c10e564e78e07f371c4f8397d17922061c5e7cc481a88a0cbc81c700ce161df9"],
        ]
    )
    def test_RSStateView(self, request):
        models.RealServerState.objects.create(
            balancer=self.balancer,
            vs=self.vs,
            server=self.rs,
            fwmark=1,
            state=models.RealServerState.STATE_CHOICES.ACTIVE,
        )
        response = self.client.get(f"/api/v1/{request.format(vs_id=self.vs.id, service_id=self.service.id)}/rsstate")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertActive(response.json()["objects"][0]["state"])

    @parameterized.expand(
        [
            ["vs/{vs_id}"],
            ["service/{service_id}/vs/{vs_id}"],
            ["service/{service_id}/vs/c10e564e78e07f371c4f8397d17922061c5e7cc481a88a0cbc81c700ce161df9"],
            ["vs/c10e564e78e07f371c4f8397d17922061c5e7cc481a88a0cbc81c700ce161df9"],
        ]
    )
    def test_LBStateView(self, request):
        models.VirtualServerState.objects.create(
            balancer=self.balancer, vs=self.vs, state=models.VirtualServerState.STATE_CHOICES.ACTIVE
        )
        response = self.client.get(f"/api/v1/{request.format(vs_id=self.vs.id, service_id=self.service.id)}/lbstate")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertActive(response.json()["objects"][0]["state"])

    @test.override_settings(DSM_ENABLED_BY_DEFAULT=True)
    @patching(
        patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
        patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=True),
        patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
        patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
    )
    @override_celery_settings(task_always_eager=True)
    def test_action_process(self):
        self.service.options.dsm = True
        self.service.save(update_fields=["options"])
        self.configuration.state = models.Configuration.STATE_CHOICES.NEW
        self.configuration.save(update_fields=["state"])

        response = self.client.post(f"/api/v1/service/{self.service.id}/config/{self.configuration.id}/process")
        self.assertEqual(response.status_code, 202, response.content)
        data: dict = response.json()
        self.assertDictEqual({"result": "OK", "object": {"id": self.configuration.id}}, data)

        self.configuration.refresh_from_db()
        self.assertEqual(models.Configuration.STATE_CHOICES.TESTING, self.configuration.state)
        deployment: models.Deployment = self.configuration.deployments.get()
        self.assertEqual(models.Deployment.States.PROCESSING, deployment.state)
        self.assertEqual(models.Deployment.Targets.DEPLOYED, deployment.target)
