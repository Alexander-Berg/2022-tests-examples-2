import itertools
import logging
import threading
import typing
from collections import defaultdict
from unittest.mock import patch

from celery import group, states
from celery.result import result_from_tuple
from django.dispatch import receiver

from l3common.tests import cases
from l3common.tests.cases import with_worker
from l3grafanasync.services import PushResponse
from l3mgr import models as mgr_models
from l3mgr.models import LoadBalancer, VirtualServer, VirtualServerState, Configuration, LocationRegion
from l3mgr.tasks import process_config
from l3mgr.tests.base import RESTAPITransactionTestCase
from l3mgr.utils import tasks as utils_tasks
from . import test_utils
from .. import models
from ..signals import testing_tasks_status_validated
from ..tasks import schedule_testing_result_tasks_group
from ..utils import lock_task, PullTestingTasksResult

logger: logging.Logger = logging.getLogger(__file__)


def _commit_svn_configuration(cfg: mgr_models.Configuration):
    # just run generator to create VirtualServiceState until TRAFFIC-11075
    list(cfg.generator())


@cases.patching(
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", return_value=defaultdict(list), autospec=True),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, side_effect=_commit_svn_configuration),
    patch(
        "l3grafanasync.services.GrafanaApi.push_dashboard", autospec=True, return_value=PushResponse(id=1, uid="abc")
    ),
    patch("l3rtsync.utils.sync", autospec=True, side_effect=lambda l: (l, [])),
)
class TestingTasksTestCase(test_utils.LockingTaskMixin, RESTAPITransactionTestCase):
    DEFAULT_TIMEOUT: float = 5 * 60

    def prepare_data(self):
        self.client = self._get_auth_client()

        self.lb_ids = []
        for lb_data in [
            dict(
                fqdn="man1-lb2b.yndx.net",
                abcs=["Logbroker"],
                locations={mgr_models.LocationNetwork.LOCATION_CHOICES.MAN},
            ),
            dict(
                fqdn="myt2-lb2b.yndx.net",
                abcs=["Logbroker"],
                locations={
                    mgr_models.LocationNetwork.LOCATION_CHOICES.MYT,
                    mgr_models.LocationNetwork.LOCATION_CHOICES.SAS,
                },
            ),
            dict(
                fqdn="any3-lb-check.yndx.net",
                locations={
                    mgr_models.LocationNetwork.LOCATION_CHOICES.MYT,
                    mgr_models.LocationNetwork.LOCATION_CHOICES.SAS,
                },
                testing=True,
            ),
            dict(
                fqdn="any4-lb-check.yndx.net",
                locations={mgr_models.LocationNetwork.LOCATION_CHOICES.MAN},
                testing=True,
            ),
        ]:
            lb_response = self._prepare_balancer(self.client, **lb_data)
            if lb_data.get("testing", False):
                self.lb_ids.append(lb_response["id"])

        svc = self._service_builder().build(self.client)
        models.AllowTestingByMachineFeature.objects.create(service_id=svc["id"])

        from l3deployment.signals import deployment_machine_stopped

        deployment_machine_stopped_event = threading.Event()

        @receiver(deployment_machine_stopped, weak=False)
        def on_machine_stopped(sender, machine, flow_control_exc, *args, **kwargs):
            deployment_machine_stopped_event.set()

        config_data = {"ANNOUNCE": True, "CHECK_URL": "/ping"}

        self.vs = self._prepare_vs(
            self.client,
            svc,
            {
                **{
                    "ip": "2a02:6b8:0:3400:ffff::4c9",
                    "port": "80",
                    "protocol": "TCP",
                    "lb": [],
                    "groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"]),
                },
                **{f"config-{k}": v for k, v in config_data.items()},
            },
        )
        self.config = self._prepare_config(self.client, svc, [self.vs])
        self.config = self._deploy_config(self.client, self.config, Configuration.STATE_CHOICES.PREPARED)

        virtual_server = VirtualServer.objects.get(pk=self.vs["id"])
        self.balancers = []
        for lb_id in self.lb_ids:
            balancer = LoadBalancer.objects.get(pk=lb_id)
            self.balancers.append(balancer)
            virtual_server.get_states_for_lb(balancer)
        self.assertEqual(len(self.balancers), 2)
        VirtualServerState.objects.filter(balancer_id__in=self.lb_ids).update(
            state=VirtualServerState.STATE_CHOICES.ACTIVE
        )

        r = process_config.delay(self.config["id"])
        r.get(timeout=self.DEFAULT_TIMEOUT)
        state = r.state
        self.assertEqual(states.SUCCESS, state)
        self.assertTrue(deployment_machine_stopped_event.wait(timeout=self.DEFAULT_TIMEOUT))

    @with_worker
    def test_svn_commit_message(self):
        self.prepare_data()
        configuration = Configuration.objects.get(pk=self.config["id"])
        configuration.comment = "line1\nline2\r\nline3"
        commit_message = utils_tasks.format_svn_commit_message(configuration)
        self.assertIn("line1\nline2\nline3", commit_message)
        self.assertNotIn("\r\n", commit_message)

    @with_worker
    def test_check_testing_result_task(self):
        self.prepare_data()

        testing_tasks: typing.Dict[int, typing.List[mgr_models.LocationRegion.REGION_CHOICES]] = dict(
            models.TestingTask.objects.filter(
                configuration_id=self.config["id"],
                lock__isnull=True,
                balancer__isnull=True,
                result=models.TestingTask.Results.UNKNOWN,
            ).values_list("pk", "presentation__regions")
        )
        self.assertEqual(2, len(testing_tasks))

        for balancer in self.balancers:
            task = lock_task(balancer)
            self.assertIsNotNone(task)
            self.assertEqual(self.config["id"], task.configuration_id)
            self.assertIn(task.id, testing_tasks)
            self.assertListEqual(task.presentation.regions, testing_tasks[task.id])

        signal_was_called_count = itertools.count()

        @receiver(testing_tasks_status_validated)
        def _callback(sender, deployment, failed, **kwargs):
            if not failed and deployment.configuration_id == self.config["id"]:
                next(signal_was_called_count)

        group_result = group(*[schedule_testing_result_tasks_group.s(lb_id) for lb_id in self.lb_ids]).delay()
        group_result.get(self.DEFAULT_TIMEOUT)
        self.assertSetEqual({states.SUCCESS}, {r.state for r in group_result.results})

        group_results = [result_from_tuple(tp) for tp in group_result.get(timeout=self.DEFAULT_TIMEOUT)]

        testing_results = [
            group_result.get(timeout=self.DEFAULT_TIMEOUT, propagate=False) for group_result in group_results
        ]
        self.assertEquals(testing_results[1], [True])
        self.assertEquals(len(testing_results[0]), 1)
        exception = testing_results[0][0]
        self.assertIsInstance(exception, PullTestingTasksResult.StillTesting)
        self.assertListEqual([LocationRegion.REGION_CHOICES.MAN], exception.regions)

        signal_was_called = next(signal_was_called_count)
        self.assertEquals(signal_was_called, 2) # one by  `check_configuration_testing_result` and other by `process_deployment`

        testing_tasks_result: typing.Dict[
            typing.Tuple[mgr_models.LocationRegion.REGION_CHOICES], models.TestingTask.Results
        ] = {
            tuple(k): v
            for k, v in models.TestingTask.objects.filter(
                configuration_id=self.config["id"],
                lock__isnull=True,
            ).values_list("presentation__regions", "result")
        }
        self.assertDictEqual(
            {
                (LocationRegion.REGION_CHOICES.MSK,): models.TestingTask.Results.SUCCESS,
                (LocationRegion.REGION_CHOICES.MAN,): models.TestingTask.Results.SUCCESS,
            },
            testing_tasks_result,
        )

    @with_worker
    def test_task_locking(self):
        self.prepare_data()
        old_times = {
            pk: (create_time, update_time)
            for pk, create_time, update_time in models.TestingTask.objects.filter(
                configuration_id=self.config["id"],
                lock__isnull=True,
                balancer__isnull=True,
                result=models.TestingTask.Results.UNKNOWN,
            ).values_list("pk", "created_at", "updated_at")
        }
        self.assertEqual(2, len(old_times))

        for balancer in self.balancers:
            task = lock_task(balancer)
            self.assertIsNotNone(task)
            self.assertIn(task.pk, old_times)
            # check second lock will return same task
            self.assert_task_locked(task.pk, balancer)

        new_times = {
            pk: (create_time, update_time)
            for pk, create_time, update_time in models.TestingTask.objects.filter(
                pk__in=old_times,
                configuration_id=self.config["id"],
                lock__isnull=False,
                balancer__isnull=False,
                result=models.TestingTask.Results.UNKNOWN,
            ).values_list("pk", "created_at", "updated_at")
        }
        self.assertEqual(2, len(new_times))
        for pk in old_times:
            self.assertEqual(old_times[pk][0], new_times[pk][0])
            self.assertLess(old_times[pk][1], new_times[pk][1])
