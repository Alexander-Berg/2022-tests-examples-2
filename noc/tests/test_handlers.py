from unittest.mock import patch

from l3mgr import models as mgr_models
from l3mgr.tests import test_fields
from l3mgr.tests.base import RESTAPITest
from l3testing import models as testing_models, utils as testing_utils
from l3testing.signals import testing_tasks_created
from ..models import AgentSettings


class FSMAndAgentTestCase(RESTAPITest):
    def setUp(self) -> None:
        super().setUp()
        self.test_lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.SAS],
            fqdn="sas1-test-2lb3b.yndx.net",
            test_env=True,
        )
        self.service: mgr_models.Service = mgr_models.Service.objects.create(
            abc="dostavkatraffika", fqdn="l3.tt.yandex-team.ru"
        )
        self.lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.SAS],
            fqdn="prod.yndx.net",
        )
        mgr_models.LoadBalancerAccess.objects.create(abc="dostavkatraffika", balancer=self.lb)

        rs: mgr_models.RealServer = mgr_models.RealServer.objects.create(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            config={},
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.SAS],
        )
        vip: mgr_models.VirtualServer = mgr_models.VirtualServer.objects.create(
            service=self.service,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port="3663",
            protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
            lb_ids=[self.lb.pk],
            rs_ids=[rs.id],
            config=test_fields.make_config(URL="/api/v1/clusters", STATUS_CODE="200"),
        )
        configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[vip.pk], description="1th-testing"
        )
        configuration.create_presentations()
        self.deployment: mgr_models.Deployment = mgr_models.Deployment.objects.create(configuration=configuration)
        self.tasks = testing_utils.create_testing_tasks(self.deployment)
        self.assertTrue(self.tasks)
        self.tasks[0].balancer = self.test_lb

    def test_tasks_without_FSM_without_agents(self) -> None:
        from l3agent.signals.handlers import tlogger

        self.test_lb.agent_settings.agent_mode = AgentSettings.MODE_CHOICES.IDLE
        self.test_lb.agent_settings.save()
        with patch.object(tlogger, "warning") as mock_logger:
            testing_tasks_created.send(None, deployment=self.deployment, tasks=self.tasks)
            mock_logger.assert_called_once()

    def test_tasks_without_FSM_with_agents(self) -> None:
        from l3agent.signals.handlers import tlogger

        with patch.object(tlogger, "warning") as mock_logger:
            testing_tasks_created.send(None, deployment=self.deployment, tasks=self.tasks)
            mock_logger.assert_not_called()

    def test_tasks_with_FSM_without_agents(self) -> None:
        from l3agent.signals.handlers import tlogger

        testing_models.BalancerTestingMachine.objects.create(balancer=self.test_lb)
        self.test_lb.agent_settings.agent_mode = AgentSettings.MODE_CHOICES.IDLE
        with patch.object(tlogger, "warning") as mock_logger:
            testing_tasks_created.send(None, deployment=self.deployment, tasks=self.tasks)
            mock_logger.assert_not_called()
