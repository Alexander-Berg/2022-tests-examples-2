import ipaddress
import itertools
import logging
import multiprocessing as mp
import shutil
import tempfile
import threading
import time
import typing
from collections import defaultdict
from contextlib import contextmanager
from datetime import timedelta
from queue import Queue
from unittest.mock import patch, Mock, MagicMock

from unittest import skip

from celery import shared_task, chain, states
from celery.result import AsyncResult, ResultSet
from django.conf import settings
from django.contrib.postgres import aggregates
from django.contrib.postgres.fields import ArrayField
from django.core import cache
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.db import connection
from django.db.models import Func, OuterRef, CharField, ProtectedError
from django.dispatch import receiver
from django.test import TransactionTestCase, TestCase, override_settings
from django.utils import timezone
from parameterized import parameterized
from rest_framework.test import APIClient

from l3balancer.services import StartResult, StopResult
from l3common.tasks.utils import LockAcquireError
from l3common.tests import cases
from l3common.tests.cases import with_worker, shared_callback_task, override_celery_settings
from l3common.typing import alias
from l3grafanasync.services import PushResponse
from l3mgr.tests import test_fields
from l3testing import models as testing_models
from l3testing.signals import testing_tasks_status_validated
from l3testing.utils import PullTestingTasksResult
from .base import RESTAPITransactionTestCase
from .. import signals as mgr_signals
from .. import tasks
from ..models import (
    Configuration,
    LoadBalancer,
    RealServerState,
    VirtualServerState,
    LocationRegion,
    Service,
    LocationNetwork,
    VirtualServer,
    RealServer,
    LoadBalancerAccess,
    Deployment,
    ConfigurationPresentation,
    Allocation,
    AllowUsedByMachineFeature,
)
from ..tasks import (
    process_config,
    update_states,
    schedule_state_updating,
    _delay_configuration_deployment,
    _deploy_lb_config_prl,
    _wait_group_result,
    wait_vs_states,
)
from ..utils.tasks import (
    UnexpectedConfigurationStateException,
    clean_configs,
    check_service_locked,
    commit_svn_configuration,
    CleanConfigsResult,
)

logger = logging.getLogger(__file__)


def compress(ip: str) -> str:
    return ipaddress.ip_address(ip).compressed


@shared_task(bind=True)
def lock_svc(self, svc_id, cfg_id=None, lb_id=None, timeout=15 * 60):
    logger.info(f"lock_svc is called: {svc_id}; {cfg_id}; {lb_id}; {timeout}")
    raise ValueError("Expected test exception - do not worry")


@shared_task(bind=True)
def _validate_config(self, cfg_id, src_state, dst_state):
    logger.info(f"_validate_config is called: {cfg_id}; {src_state}; {dst_state}")
    return True


@shared_callback_task
def _failure_config(request, exc, traceback, cfg_id, dst_state):
    logger.info(f"_failure_config is called: {request}; {exc}; {traceback}; {cfg_id}; {dst_state}")

    description = "Task {0} raised exception: {1!r}".format(request.id, exc)
    logger.error("\n".join([description, "Traceback:", traceback]))

    return True


@shared_callback_task(priority=10)
def release_svc(svc_id, cfg_id=None, lb_id=None):
    logger.info(f"release_svc is called: {svc_id}; {cfg_id}; {lb_id}")

    return True


def _get_balancer_host_mock_return_value(fqdn):
    return _build_balancer_host_mock_return_value(80)(fqdn)


def _build_balancer_host_mock_return_value(*ports):
    def get_balancer_host_mock_return_value(fqdn):
        mock = Mock()
        mock.start_keepalived.side_effect = lambda restart=True: StartResult.SKIPPED if restart else StartResult.STARTED
        mock.stop_keepalived.return_value = StopResult.STOPPED

        regions = set(LoadBalancer.objects.get(fqdn=fqdn).region)

        rs_ips = set()
        if LocationRegion.REGION_CHOICES.MAN in regions:
            rs_ips.add("2a02:06b8:b040:3100:0ccc:0000:0000:04c9")
        if LocationRegion.REGION_CHOICES.MSK in regions:
            rs_ips.add("2a02:06b8:0000:1482:0000:0000:0000:0115")
            rs_ips.add("2a02:06b8:b010:0031:0000:0000:0000:0233")

        mock.fetch_balancer_info.return_value = (
            [
                ((compress("2a02:06b8:0000:3400:ffff:0000:0000:04c9"), port, "TCP"), {compress(ip) for ip in rs_ips})
                for port in ports
            ],
            {"192.168.100.2", "fe80::b825:a700:c586:3c07", "2a02:6b8:0:3400:ffff::4c9"},
        )

        def update_config(content, pull_cvs=True):
            pass

        mock.update_config.side_effect = update_config
        mock.restart_firewall.side_effect = update_config

        return mock

    return get_balancer_host_mock_return_value


def _commit_svn_configuration(cfg):
    # just run generator to create VirtualServiceState until TRAFFIC-11075
    list(cfg.generator())


class MockSVNLocalClient:
    commit_message: str = ""

    def update(self):
        pass

    def info(self):
        return_info = MagicMock()
        return_info.get.return_value = "/tmp/path"

        return return_info

    def status(self, _fqdn):
        return_path = MagicMock()
        return_path.name.return_value = _fqdn
        return_path.type_raw_name = "type_raw_name"
        return [return_path]

    def commit(self, message, _filepaths):
        self.commit_message = message


class BasicTasksTestCase(TransactionTestCase):
    @with_worker
    def test_link_error(self):
        """
        We check incompatibility which was introduced in
        https://github.com/celery/celery/pull/5399

        because of which bound tasks errback are interpreted as "old" signature with single argument ones
        """

        def apply_config_chain(cfg_id, svc_id=None):
            fail_task = _failure_config.s(cfg_id, "VCS_FAIL")
            release_task = release_svc.si(svc_id, cfg_id)

            return chain(
                _validate_config.signature(
                    args=(
                        cfg_id,
                        "VCS_PENDING",
                        "VCS_UPDATING",
                    ),
                    immutable=True,
                    link_error=[release_task],
                ),
                lock_svc.signature(
                    args=(
                        "svn-myt-man.yandex.net",
                        cfg_id,
                    ),
                    immutable=True,
                    link_error=[fail_task, release_task],
                ),
            )

        apply_config_chain(123, 456).delay()

        logger.warning("Going to wait for task errbacks called")
        self.assertTrue(_failure_config.completion_event.wait(5 * 60))
        self.assertTrue(release_svc.completion_event.wait(5 * 60))

    @with_worker
    def test_chain_failure_callback(self):
        """
        Checking "on_error" callback called in chain
        """

        fail_task = _failure_config.s(1, "VCS_FAIL")
        release_task = release_svc.si(1, 1)

        tasks = chain(
            _validate_config.signature(
                args=(1, Configuration.STATE_CHOICES.VCS_PENDING, Configuration.STATE_CHOICES.VCS_UPDATING),
                immutable=True,
                link_error=[release_task],
            ),
            lock_svc.signature(args=("svn-myt-man.yandex.net", 1), immutable=True, link_error=[release_task]),
        )

        tasks.on_error(fail_task)
        a_result = tasks.delay()
        a_result.get(timeout=5 * 60, propagate=False)

        self.assertEqual(states.FAILURE, a_result.state)
        self.assertTrue(release_svc.completion_event.wait(5 * 60))
        self.assertTrue(_failure_config.completion_event.wait(5 * 60))


class _BalancersPrepareMixin:
    BALANCERS_DATA = [
        dict(fqdn="man1-lb2b.yndx.net", abcs=["Logbroker"], region=LocationRegion.REGION_CHOICES.MAN),
        dict(fqdn="myt2-lb2b.yndx.net", abcs=["Logbroker"], region=LocationRegion.REGION_CHOICES.MSK),
        dict(fqdn="any3-lb-check.yndx.net", region=LocationRegion.REGION_CHOICES.MSK, testing=True),
        dict(fqdn="any4-lb-check.yndx.net", region=LocationRegion.REGION_CHOICES.MAN, testing=True),
    ]

    def _prepare_balancers(self, client):
        balancers = []
        for lb_data in self.BALANCERS_DATA:
            balancer_data = self._prepare_balancer(client, **lb_data)
            balancer: LoadBalancer = LoadBalancer.objects.get(pk=balancer_data["id"])
            balancers.append(balancer)
        return balancers

    def _send_vs_update(self, client, svc, vs) -> int:
        r = client.post(
            f"{svc['url']}/vs/{vs['ext_id']}",
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": vs["port"],
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"]),
            },
        )
        self.assertEqual(202, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        c_id = result["object"]["id"]
        return c_id


class SVNCommitTestCase(_BalancersPrepareMixin, RESTAPITransactionTestCase):
    _patchers = RESTAPITransactionTestCase._patchers + [
        patch("os.path.isdir", autospec=True, return_value=False),
        patch("os.path.relpath", autospec=True, return_value="lbk-man.logbroker-prestable.yandex.net"),
        patch("l3mgr.models.Configuration.generator", autospec=True, return_value=[]),
    ]

    def setUp(self):
        super().setUp()
        client = self._get_auth_client()
        svc = self._service_builder().build(client)
        vs = self._prepare_vs(
            client,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "\n".join(
                    [
                        "%traffic_manage",
                        "lbkp-man-009.search.yandex.net",
                    ]
                ),
            },
        )
        self.config = self._prepare_config(client, svc, [vs])

    @with_worker
    def test_svn_commit_newline_character(self):
        config = Configuration.objects.get(pk=self.config["id"])
        config.comment = "Initial\r\ncommit"
        mock_svn_local_client = MockSVNLocalClient()
        with patch("svn.local.LocalClient", autospec=True, return_value=mock_svn_local_client):
            commit_svn_configuration(config)
            self.assertIn(
                "Initial\ncommit", mock_svn_local_client.commit_message, "Should contain correct formatted message"
            )
            self.assertNotIn("\r\n", mock_svn_local_client.commit_message, "Commit comment should not contain \\r\\n")


class TasksTestCase(_BalancersPrepareMixin, RESTAPITransactionTestCase):
    _patchers = RESTAPITransactionTestCase._patchers + [
        patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", return_value=defaultdict(list), autospec=True),
        patch("l3mgr.models.BalancerHost", autospec=True, side_effect=_get_balancer_host_mock_return_value),
        patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None),
        patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, side_effect=_commit_svn_configuration),
    ]

    @with_worker
    def test_wait_keepalived(self):
        self._test_wait_keepalived(False)

    @with_worker
    def test_wait_keepalived_with_fsm(self):
        self._test_wait_keepalived(True)

    def _test_wait_keepalived(self, allow_testing_by_machine_feature):
        client = self._get_auth_client()

        thread_lock = threading.Lock()
        deploy_process_started_event = threading.Event()
        started_configurations = []

        @receiver(mgr_signals.start_config_processing)
        def on_deploy_process_started(sender, configuration, task, *args, **kwargs):
            with thread_lock:
                started_configurations.append(
                    (
                        configuration,
                        task.request.id,
                    )
                )
            deploy_process_started_event.set()

        balancers = self._prepare_balancers(client)

        svc = self._service_builder().build(client)
        if allow_testing_by_machine_feature:
            testing_models.AllowTestingByMachineFeature.objects.create(service_id=svc["id"])
            testing_models.BalancerTestingMachine.objects.bulk_create(
                testing_models.BalancerTestingMachine(balancer=b) for b in balancers if b.test_env
            )

        vs = self._prepare_vs(
            client,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "\n".join(
                    [
                        "%traffic_manage",
                        "lbkp-man-009.search.yandex.net",
                    ]
                ),
            },
        )
        c = self._prepare_config(client, svc, [vs])
        c = self._deploy_config(client, c, Configuration.STATE_CHOICES.PREPARED)

        # lets begin testing
        from l3mgr.tasks import process_config

        r = process_config.delay(c["id"])
        r.get(timeout=5 * 60)
        state = r.state
        self.assertEqual(states.SUCCESS, state)

        self.assertTrue(deploy_process_started_event.is_set())
        deploy_process_started_event.clear()

        self._activate_config(client, c)

        c_id = self._send_vs_update(client, svc, vs)
        self.assertNotEqual(c["id"], c_id)

        deploy_process_started_event.wait(5 * 60)
        cfg, task_id = started_configurations[1]
        r = AsyncResult(task_id)
        r.get(timeout=5 * 60, propagate=False)
        state = r.state
        self.assertEqual(states.SUCCESS, state)


_ORIGINAL_UNEXPECTED_CONFIGURATION_STATE_EXCEPTION_NEW = UnexpectedConfigurationStateException.__new__


class ExpectedTestException(UnexpectedConfigurationStateException):
    def __init__(self, msg, *args):
        msg = "[EXPECTED TEST EXCEPTION]: " + msg + "; [DON'T WORRY !!!]"
        super().__init__(msg, *args)


@cases.patching(
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", return_value=defaultdict(list), autospec=True),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, side_effect=_commit_svn_configuration),
    patch(
        "l3grafanasync.services.GrafanaApi.push_dashboard", autospec=True, return_value=PushResponse(id=1, uid="abc")
    ),
    patch("l3rtsync.utils.sync", autospec=True, side_effect=lambda l: (l, [])),
)
class ConfigurationProcessingTestCase(_BalancersPrepareMixin, RESTAPITransactionTestCase):
    DEFAULT_TIMEOUT: float = 5 * 60

    PORTS_MUTEX = threading.Lock()
    FETCH_BALANCER_INFO_PORTS = [80]

    @contextmanager
    def balancer_fetch_info(self, *ports):
        self.PORTS_MUTEX.acquire()
        try:
            original = self.FETCH_BALANCER_INFO_PORTS[:]
            self.FETCH_BALANCER_INFO_PORTS.clear()
            self.FETCH_BALANCER_INFO_PORTS.extend(ports)
        finally:
            self.PORTS_MUTEX.release()
        try:
            yield
        finally:
            try:
                self.PORTS_MUTEX.acquire()
                self.FETCH_BALANCER_INFO_PORTS.clear()
                self.FETCH_BALANCER_INFO_PORTS.extend(original)
            finally:
                self.PORTS_MUTEX.release()

    def _get_balancer_host_mock_side_effect(self, fqdn):
        mock = Mock()
        mock.start_keepalived.side_effect = lambda restart=True: StartResult.SKIPPED if restart else StartResult.STARTED
        mock.stop_keepalived.return_value = StopResult.STOPPED

        regions = set(LoadBalancer.objects.get(fqdn=fqdn).region)

        rs_ips = set()
        if LocationRegion.REGION_CHOICES.MAN in regions:
            rs_ips.add("2a02:06b8:b040:3100:0ccc:0000:0000:04c9")
        if LocationRegion.REGION_CHOICES.MSK in regions:
            rs_ips.add("2a02:06b8:0000:1482:0000:0000:0000:0115")
            rs_ips.add("2a02:06b8:b010:0031:0000:0000:0000:0233")

        def fetch_balancer_info():
            self.PORTS_MUTEX.acquire()
            try:
                return (
                    [
                        (
                            (compress("2a02:06b8:0000:3400:ffff:0000:0000:04c9"), port, "TCP"),
                            {compress(ip) for ip in rs_ips},
                        )
                        for port in self.FETCH_BALANCER_INFO_PORTS
                    ],
                    {"192.168.100.2", "fe80::b825:a700:c586:3c07", "2a02:6b8:0:3400:ffff::4c9"},
                )
            finally:
                self.PORTS_MUTEX.release()

        mock.fetch_balancer_info.side_effect = fetch_balancer_info

        def update_config(content, pull_cvs=True):
            pass

        mock.update_config.side_effect = update_config
        mock.restart_firewall.side_effect = update_config

        return mock

    def setUp(self):
        self._patchers.append(
            patch("l3mgr.models.BalancerHost", autospec=True, side_effect=self._get_balancer_host_mock_side_effect)
        )

        super().setUp()
        self.api_client = APIClient()
        self.client = self.api_client

        self.deploy_process_started_event = threading.Event()
        self.started_configurations = []

        @receiver(mgr_signals.start_config_processing, weak=False)
        def on_deploy_process_started(sender, configuration, task, *args, **kwargs):
            self.started_configurations.append((configuration, task.request.id))
            self.deploy_process_started_event.set()

        self.configuration_state_changed_history = Queue()

        @receiver(mgr_signals.configuration_state_changed, weak=False)
        def on_configuration_state_changed(sender, configuration, previous_state, *args, **kwargs):
            self.configuration_state_changed_history.put(
                (sender, configuration.id, configuration.state, previous_state)
            )

        self.testing_tasks_status_validated_results = Queue()

        @receiver(testing_tasks_status_validated, weak=False)
        def on_testing_tasks_status_validated(sender, deployment, failed, *args, **kwargs):
            logger.info(f"receive deployment#{deployment.id} testing results: {failed}")
            self.testing_tasks_status_validated_results.put((deployment, failed))

        self.balancers = self._prepare_balancers(self.client)

        self.svc = self._service_builder().build(self.client)
        testing_models.AllowTestingByMachineFeature.objects.create(service_id=self.svc["id"])

    def tearDown(self):
        try:
            super().tearDown()
        finally:
            self._patchers.pop()

    @parameterized.expand([(True,), (False,)])
    @with_worker
    @patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True))
    def test_configuration_processing_in_parallel_with_agents(self, skip_test: bool = True):
        vs = self.prepare_vs({"groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"])})

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        from l3deployment.signals import deployment_machine_stopped

        deployment_machine_stopped_event = threading.Event()

        @receiver(deployment_machine_stopped, weak=False)
        def on_machine_stopped(sender, machine, flow_control_exc, *args, **kwargs):
            deployment_machine_stopped_event.set()

        def assert_testing(cfg: Configuration, vs: dict) -> None:
            new_state = None
            while new_state != Configuration.STATE_CHOICES.TESTING:
                sender, cfg_id, new_state, previous_state = self.configuration_state_changed_history.get(
                    timeout=self.DEFAULT_TIMEOUT
                )
                self.assertEquals(cfg.id, cfg_id)
            self.assertTrue(self.configuration_state_changed_history.empty())

            self.assertTrue(deployment_machine_stopped_event.wait(timeout=self.DEFAULT_TIMEOUT))
            deployment_machine_stopped_event.clear()
            cfg.refresh_from_db()
            self.assertEquals(Configuration.STATE_CHOICES.TESTING, cfg.state)

            balancer = self.balancers[2]
            self.assertTrue(balancer.test_env)
            task = self._send_lock_and_status(balancer, cfg.id, vs)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
            self.assertListEqual([LocationRegion.REGION_CHOICES.MAN, LocationRegion.REGION_CHOICES.MSK], failed.regions)

            for idx in range(2):
                # one for `check_deployment_testing_result`, other for `process_deployment` (retry from this schedule)
                deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                self.assertIsNotNone(failed)
                self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
                self.assertListEqual([LocationRegion.REGION_CHOICES.MAN], failed.regions)
                self.assertEquals(task.deployment_id, deployment.pk)

            self.assertTrue(deployment_machine_stopped_event.wait(timeout=self.DEFAULT_TIMEOUT))
            deployment_machine_stopped_event.clear()

            balancer = self.balancers[3]
            self.assertTrue(balancer.test_env)
            task = self._send_lock_and_status(balancer, cfg.id, vs)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsNone(failed, msg=str(failed))
            self.assertEquals(task.deployment_id, deployment.pk)

            self.assertTrue(deployment_machine_stopped_event.wait(timeout=self.DEFAULT_TIMEOUT))
            deployment_machine_stopped_event.clear()

        def assert_deploy(c_id: int, vs: dict, force: bool) -> None:
            self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
            cfg: Configuration = self.assert_configuration_started()
            self.assertEquals(c_id, cfg.id)
            self.started_configurations.clear()

            if not force:
                assert_testing(cfg, vs)

            chain_result: ResultSet = deploy_chains.get(timeout=self.DEFAULT_TIMEOUT)
            chain_result.get(timeout=self.DEFAULT_TIMEOUT)

            cfg.refresh_from_db()
            self.assertEquals(Configuration.STATE_CHOICES.ACTIVE, cfg.state)
            vs_state: VirtualServerState = VirtualServerState.objects.get(
                balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
            )
            self.assertEquals(VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

            presentations: typing.List[ConfigurationPresentation] = list(cfg.presentations.all())
            rss_qs = (
                RealServer.objects.filter(id__in=vs["rs"])
                .annotate(
                    regions=Func(
                        LocationRegion.objects.filter(location__overlap=OuterRef("location")).values("code"),
                        output_field=ArrayField(base_field=CharField()),
                        function="ARRAY",
                    )
                )
                .values("regions")
                .annotate(rs_ids=aggregates.ArrayAgg("id"))
                .values_list("regions", "rs_ids")
            )
            rss = {region: set(rs_ids) for regions, rs_ids in rss_qs for region in regions}
            with alias(LocationRegion.REGION_CHOICES) as R:
                self.assertDictEqual(
                    {
                        R.MAN: ([self.balancers[0].id], {vs["id"]}, rss[R.MAN]),
                        R.MSK: ([self.balancers[1].id], {vs["id"]}, rss[R.MSK]),
                    },
                    {
                        region: (
                            p.balancers,
                            set(p.data.keys()),
                            {rs_id for v in p.data.values() for rs_id in v["rs_ids"]},
                        )
                        for p in presentations
                        for region in p.regions
                    },
                )
            self.assertFalse(any(p.locations for p in presentations))

            deployment: Deployment = cfg.deployments.get()
            self.assertEqual(Deployment.Targets.TESTED, deployment.target)
            self.assertEqual(Deployment.States.REACHED, deployment.state)
            self.assertEqual(force, deployment.skip_tests)

            if not self.testing_tasks_status_validated_results.empty():
                # there may be two results as there are two tasks, and in case of rase they can be not optimized
                self.testing_tasks_status_validated_results.get_nowait()
            self.assertTrue(self.testing_tasks_status_validated_results.empty())

            while not self.configuration_state_changed_history.empty():
                self.configuration_state_changed_history.get_nowait()
            self.assertTrue(self.configuration_state_changed_history.empty())

            self.assertTrue(deploy_chains.empty())
            deployment_machine_stopped_event.clear()

        c = self._prepare_config(self.client, self.svc, [vs])
        c = self._deploy_config(self.client, c, Configuration.STATE_CHOICES.PREPARED)
        # lets begin testing
        self.assert_process_config(c["id"], force=skip_test)
        assert_deploy(c["id"], vs, skip_test)

        # second deploy
        self.assertTrue(self.deploy_process_started_event.is_set())
        self.deploy_process_started_event.clear()
        self.assertFalse(deployment_machine_stopped_event.is_set())

        c_id = self._send_vs_update(self.client, self.svc, vs)
        self.assertNotEqual(c["id"], c_id)
        (vs_id,) = Configuration.objects.get(id=c_id).vs_ids
        r = self.client.get(f"{self.svc['url']}/vs/{vs_id}")
        self.assertEqual(200, r.status_code)
        vs: dict = r.json()
        self.assertTrue(vs_id, vs["id"])
        assert_deploy(c_id, vs, False)

    @with_worker
    def test_specified_test_lbs(self):
        testing_models.BalancerTestingMachine.objects.bulk_create(
            testing_models.BalancerTestingMachine(balancer=b) for b in self.balancers if b.test_env
        )

        target_test_lb = self.balancers[3]
        self.assertTrue(target_test_lb.test_env)
        vss = [
            self.prepare_vs(
                {"port": 443, "groups": "lbkp-man-009.search.yandex.net", "config-TESTING_LBS": target_test_lb.id}
            ),
        ]
        c = self._prepare_config(self.client, self.svc, vss)

        # lets begin testing
        c = self._deploy_config(self.client, c, Configuration.STATE_CHOICES.PREPARED)
        self.assert_process_config(c["id"])

        self.assertTrue(self.deploy_process_started_event.is_set())
        self.deploy_process_started_event.clear()

        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
        self.assertListEqual([LocationRegion.REGION_CHOICES.MAN], failed.regions)
        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertIsNone(failed)

        cfg = self.assert_configuration_started()
        cfg.refresh_from_db()
        self.assertEqual(Configuration.STATE_CHOICES.TESTING, cfg.state)

        testing_tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
        self.assertEqual(1, len(testing_tasks))
        self.assertEqual(target_test_lb.id, testing_tasks[0].balancer_id)
        self.assertFalse(testing_models.TestingTask.objects.exclude(balancer=target_test_lb).exists())

    @with_worker
    def test_empty_vs_configuration_processing_with_fsm(self):
        vs = self.prepare_vs({"port": 80})
        self._base_test_empty_configurations_processing_with_fsm([vs])

    @with_worker
    def test_empty_configuration_processing_with_fsm(self):
        self._base_test_empty_configurations_processing_with_fsm([])

    def _base_test_empty_configurations_processing_with_fsm(self, vss):
        testing_models.BalancerTestingMachine.objects.bulk_create(
            testing_models.BalancerTestingMachine(balancer=b) for b in self.balancers if b.test_env
        )
        c = self._prepare_config(self.client, self.svc, vss)
        c = self._deploy_config(self.client, c, Configuration.STATE_CHOICES.PREPARED)

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        # lets begin testing

        self.assert_process_config(c["id"])

        self.assertTrue(self.deploy_process_started_event.is_set())
        self.deploy_process_started_event.clear()

        cfg: Configuration = self.assert_configuration_started()
        chain_result: ResultSet = deploy_chains.get(timeout=self.DEFAULT_TIMEOUT)
        chain_result.get(timeout=self.DEFAULT_TIMEOUT)

        previous_state = None
        while previous_state != Configuration.STATE_CHOICES.PREPARED:
            sender, cfg_id, new_state, previous_state = self.configuration_state_changed_history.get(
                timeout=self.DEFAULT_TIMEOUT
            )
            self.assertEquals(c["id"], cfg_id)

        cfg.refresh_from_db()
        self.assertNotIn(
            cfg.state,
            {
                Configuration.STATE_CHOICES.NEW,
                Configuration.STATE_CHOICES.PREPARED,
                Configuration.STATE_CHOICES.TEST_PENDING,
                Configuration.STATE_CHOICES.TESTING,
                Configuration.STATE_CHOICES.TEST_FAIL,
            },
        )

        self.assertTrue(self.testing_tasks_status_validated_results.empty())
        self.assertEquals(c["id"], cfg.id)

        cfg.refresh_from_db()
        self.assertIn(
            cfg.state,
            {
                Configuration.STATE_CHOICES.VCS_PENDING,
                Configuration.STATE_CHOICES.VCS_UPDATING,
                Configuration.STATE_CHOICES.VCS_COMMITTED,
                Configuration.STATE_CHOICES.PENDING,
                Configuration.STATE_CHOICES.DEPLOYING,
                Configuration.STATE_CHOICES.ACTIVE,
            },
        )
        self.assertFalse(VirtualServerState.objects.filter(vs_id__in=cfg.vs_ids).exists())
        self.assertFalse(testing_models.TestingTask.objects.filter(configuration=cfg).exists())

    @with_worker
    @patch("l3mgr.utils.tasks.UnexpectedConfigurationStateException.__new__")
    def test_configuration_processing_in_order_with_fsm(self, exc_init_mock):
        exc_init_mock.side_effect = lambda cls, *args, **kwargs: _ORIGINAL_UNEXPECTED_CONFIGURATION_STATE_EXCEPTION_NEW(
            ExpectedTestException, *args, **kwargs
        )
        testing_models.BalancerTestingMachine.objects.bulk_create(
            testing_models.BalancerTestingMachine(balancer=b) for b in self.balancers if b.test_env
        )
        vss = [
            self.prepare_vs({"port": 80, "groups": "%traffic_manage"}),
            self.prepare_vs({"port": 443, "groups": "lbkp-man-009.search.yandex.net"}),
        ]
        c = self._prepare_config(self.client, self.svc, vss)
        c = self._deploy_config(self.client, c, Configuration.STATE_CHOICES.PREPARED)

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        # lets begin testing
        with self.balancer_fetch_info(443):
            self.assert_process_config(c["id"])

            self.assertTrue(self.deploy_process_started_event.is_set())
            self.deploy_process_started_event.clear()

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
            self.assertListEqual([LocationRegion.REGION_CHOICES.MAN, LocationRegion.REGION_CHOICES.MSK], failed.regions)
            for idx in range(2):
                # one for `check_deployment_testing_result`, other for `process_deployment`
                deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                self.assertIsNone(failed)

            cfg: Configuration = self.assert_configuration_started()
            chain_result: ResultSet = deploy_chains.get(timeout=self.DEFAULT_TIMEOUT)
            chain_result.get(timeout=self.DEFAULT_TIMEOUT)

        cfg.refresh_from_db()
        self.assertEquals(c["id"], cfg.id)
        self.assertEquals(Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        vs_state: VirtualServerState = VirtualServerState.objects.get(
            balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
        )
        self.assertEquals(VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

        if not self.testing_tasks_status_validated_results.empty():
            # there may be two results as there are two tasks, and in case of rase they can be not optimized
            self.testing_tasks_status_validated_results.get(block=False)
        self.assertTrue(self.testing_tasks_status_validated_results.empty())

        # second deploy
        logger.info("[test_configuration_processing_in_order_with_fsm] second deploy")

        c_id: int = self._send_vs_update(self.client, self.svc, vss[0])
        self.assertNotEqual(c["id"], c_id)

        self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
        cfg1 = self.assert_configuration_started(1)
        cfg, task_id = self.started_configurations[1]
        self.assertEqual(cfg1.id, cfg.id)
        r = AsyncResult(task_id)
        r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
        state = r.state
        if state != states.SUCCESS:
            self.fail(f"`process_config` task state is {state}, but SUCCESS expected: {r.result}")
        self.assertEqual(states.SUCCESS, state)

        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
        self.assertListEqual([LocationRegion.REGION_CHOICES.MAN, LocationRegion.REGION_CHOICES.MSK], failed.regions)
        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)

        with self.balancer_fetch_info(80, 443):
            self.assertEqual(cfg.id, deployment.configuration_id)
            self.assertIsInstance(failed, PullTestingTasksResult.StillTesting)
            self.assertListEqual(
                [LocationRegion.REGION_CHOICES.MAN], typing.cast(PullTestingTasksResult.StillTesting, failed).regions
            )

            tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
            self.assertEquals(2, len(tasks))

            self.assertDictEqual(
                {
                    (LocationRegion.REGION_CHOICES.MSK,): testing_models.TestingTask.Results.SUCCESS,
                    (LocationRegion.REGION_CHOICES.MAN,): testing_models.TestingTask.Results.UNKNOWN,
                },
                {tuple(t.presentation.regions): t.result for t in tasks},
            )

            chain_result: ResultSet = deploy_chains.get(timeout=self.DEFAULT_TIMEOUT)
            chain_result.get(timeout=self.DEFAULT_TIMEOUT)

            tasks = list(deployment.testing_tasks.all())
            self.assertEquals(2, len(tasks))
            self.assertSetEqual({testing_models.TestingTask.Results.SUCCESS}, {t.result for t in tasks})

    def _send_lock_and_status(self, balancer: LoadBalancer, c_id: int, vs) -> testing_models.TestingTask:
        task = self._send_lock_task(balancer, c_id)
        self._send_deployment_status(balancer, task, vs)
        return task

    def _send_lock_task(self, balancer: LoadBalancer, c_id: int) -> testing_models.TestingTask:
        url = "/api/v1/agent/{agent_id}/tasks/current"
        response = self.api_client.post(
            url.format(agent_id=balancer.fqdn), {"id": balancer.fqdn, "generator_version": "v1.0"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEquals(1, len(response.data))
        self.assertEquals(c_id, response.data[0]["data"]["id"])
        task = testing_models.TestingTask.objects.get(pk=response.data[0]["id"])
        self.assertEquals(testing_models.TestingTask.Results.UNKNOWN, task.result)
        return task

    def _send_deployment_status(self, balancer: LoadBalancer, task: testing_models.TestingTask, vs):
        url = "/api/v1/agent/{agent_id}/tasks/{task_id}/deployment-status"
        response = self.api_client.put(
            url.format(agent_id=balancer.fqdn, task_id=task.pk),
            {
                "id": task.pk,
                "ts": time.time(),
                "error": {"message": None, "code": 200},
                "overall_deployment_status": "SUCCESS",
                "vss": [
                    {
                        "id": vs["id"],
                        "status": "UP",
                        "rss": [{"id": rs_id, "status": "SUCCESS"} for rs_id in vs["rs"]],
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task.refresh_from_db()
        self.assertEquals(testing_models.TestingTask.Results.SUCCESS, task.result)
        return response

    def assert_process_config(self, configuration_id: int, force: bool = False) -> None:
        r = process_config.delay(configuration_id, force=force)
        r.get(timeout=self.DEFAULT_TIMEOUT)
        state = r.state
        self.assertEqual(states.SUCCESS, state)

    def assert_configuration_started(self, started_configurations_idx: int = 0) -> Configuration:
        cfg, task_id = self.started_configurations[started_configurations_idx]
        r = AsyncResult(task_id)
        r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
        state = r.state
        self.assertEqual(
            states.SUCCESS, state, msg=f"`process_config` task state is {state}, but SUCCESS expected: {r.result}"
        )
        return cfg

    def prepare_vs(self, params: typing.Dict[str, typing.Union[bool, int, float, str]]) -> dict:
        params = {
            **{
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": 80,
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
            },
            **params,
        }
        return self._prepare_vs(self.client, self.svc, params)


class TestCleanTables(TestCase):
    def test_clean_with_removed_restored_allocation(self):
        all_locations = [LocationNetwork.LOCATION_CHOICES.MAN, LocationNetwork.LOCATION_CHOICES.VLA]
        svc: Service = Service.objects.create(fqdn="test.yndx.net", abc="test")
        # svc.options.max_history_length = 2
        svc.save(update_fields=["options"])
        rss: typing.List[RealServer] = RealServer.objects.bulk_create(
            [
                RealServer(
                    fqdn=f"mnt-{l.lower()}.yandex.net",
                    ip="2a02:6b8:0:1482::115",
                    config={"WEIGHT": 1},
                    location=[l],
                )
                for l in all_locations
            ]
        )
        lbs: typing.List[LoadBalancer] = LoadBalancer.objects.bulk_create(
            [
                LoadBalancer(
                    fqdn=f"lb-{l.lower()}.yndx.net",
                    state=LoadBalancer.STATE_CHOICES.ACTIVE,
                    location=[l],
                )
                for l in all_locations
            ]
        )
        LoadBalancerAccess.objects.bulk_create([LoadBalancerAccess(abc=svc.abc, balancer=lb) for lb in lbs])

        with alias(Configuration.STATE_CHOICES) as S:
            cfg_states = [S.INACTIVE] * (svc.options.max_history_length + 1) + [S.ACTIVE, S.DEPLOYING]
        vss: typing.List[VirtualServer] = VirtualServer.objects.bulk_create(
            [
                VirtualServer(
                    service=svc,
                    ip="2a02:6b8:0:3400:ffff::4c9",
                    port=80,
                    protocol=VirtualServer.PROTOCOL_CHOICES.TCP,
                    config=test_fields.make_config(),
                    rs_ids=[rs.id for rs in rss][: 1 + (i + 1) % len(all_locations)],
                )
                for i in range(len(cfg_states))
            ]
        )
        cfgs: typing.List[Configuration] = Configuration.objects.bulk_create(
            Configuration(service=svc, state=state, vs_ids=[vs.id]) for state, vs in zip(cfg_states, vss)
        )
        # let's generate more data to make cleanup more realistic
        for cfg in cfgs:
            presentations = cfg.create_presentations()
            self.assertTrue(presentations)
            # using bulk_create to prevent signals sending which will trigger dsm
            deployment: Deployment = Deployment.objects.bulk_create([Deployment(configuration=cfg)])[0]
            allocations: typing.List[Allocation] = deployment.prepare_allocations(lambda d, lbs: [lbs])
            self.assertTrue(allocations)
            for allocation in allocations:
                allocation.state = Allocation.States.UNKNOWN
            Allocation.objects.bulk_create(allocations)

        result, stuck_configuration = svc.cleanup()
        self.assertFalse(stuck_configuration, "should be no stuck configs")
        self.assertEqual(1, result[Allocation._meta.label])
        self.assertEqual(1, result[Deployment._meta.label])
        self.assertEqual(2, result[ConfigurationPresentation._meta.label])
        self.assertEqual(1, result[Configuration._meta.label])
        self.assertEqual(1, result[VirtualServer._meta.label])
        self.assertEqual(5, len(result))

    @parameterized.expand(
        (
            (dict(celery_state=Allocation.CeleryStates.PROCESSED),),
            (dict(state=Allocation.States.REMOVED),),
        )
    )
    def test_clean_configs(self, allocation_update_fields: dict):
        rs: RealServer = RealServer.objects.create(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            config={"WEIGHT": 1},
            location=[LocationNetwork.LOCATION_CHOICES.MAN],
        )
        n_svcs = 3
        n_vss_for_cfg = 2
        svcs: typing.List[Service] = Service.objects.bulk_create(
            Service(fqdn=f"test-{i}.yndx.net", abc=f"test-{i}") for i in range(n_svcs)
        )
        states_from_last_active = [Configuration.STATE_CHOICES.ACTIVE, Configuration.STATE_CHOICES.INACTIVE]
        cfg_states = [Configuration.STATE_CHOICES.INACTIVE] * n_svcs + states_from_last_active
        n_cfgs = len(cfg_states)

        lbs: typing.List[LoadBalancer] = LoadBalancer.objects.bulk_create(
            [
                LoadBalancer(
                    fqdn=f"man-{i}.yndx.net",
                    state=LoadBalancer.STATE_CHOICES.ACTIVE,
                    location=[LocationNetwork.LOCATION_CHOICES.MAN],
                )
                for i in range(n_cfgs)
            ]
        )

        cfgs: typing.List[Configuration] = []
        for i, svc in enumerate(svcs):
            LoadBalancerAccess.objects.bulk_create([LoadBalancerAccess(abc=svc.abc, balancer=lb) for lb in lbs])
            vss = VirtualServer.objects.bulk_create(
                VirtualServer(
                    service=svc,
                    ip="2a02:6b8:0:3400:ffff::4c9",
                    port=80 + j,
                    protocol=VirtualServer.PROTOCOL_CHOICES.TCP,
                    config=test_fields.make_config(),
                    rs_ids=[rs.id],
                )
                for j in range(n_cfgs + n_vss_for_cfg - 1)
            )
            vs_ids_generator = ([vs.id for vs in vss[j : j + n_vss_for_cfg]] for j in range(n_cfgs))
            cfgs.extend(
                Configuration.objects.bulk_create(
                    Configuration(service=svc, state=state, vs_ids=next(vs_ids_generator)) for state in cfg_states
                )
            )
            svc.options.max_history_length = i + 1
            svc.save(update_fields=["options"])

        # let's generate more data to make cleanup more realistic
        for cfg in cfgs:
            presentations = cfg.create_presentations()
            self.assertTrue(presentations)
            # using bulk_create to prevent signals sending which will trigger dsm
            deployment: Deployment = Deployment.objects.bulk_create([Deployment(configuration=cfg)])[0]
            allocations: typing.List[Allocation] = deployment.prepare_allocations(lambda d, lbs: [lbs])
            self.assertTrue(allocations)
            for allocation in allocations:
                allocation.state = Allocation.States.UNKNOWN
            Allocation.objects.bulk_create(allocations)
            LoadBalancerAccess.objects.filter(abc=cfg.service.abc).first().delete()

        # should fail on first service's configurations delete as it contains unremoved allocations
        result: CleanConfigsResult = clean_configs()
        self.assertTrue(result.stuck_configuration)

        # second try should do the same
        second_result = clean_configs()
        self.assertListEqual(result.stuck_configuration, second_result.stuck_configuration)

        self.assertSetEqual(
            {
                (svcs[0].fqdn, lbs[0].fqdn),
                (svcs[0].fqdn, lbs[1].fqdn),
                (svcs[1].fqdn, lbs[0].fqdn),
            },
            set(
                Allocation.objects.filter(target=Allocation.Targets.REMOVED)
                .filter(presentation__configuration_id__in=second_result.stuck_configuration)
                .values_list("service_id", "balancer_id")
            ),
        )

        self.assertEqual(
            3,
            Allocation.objects.filter(target=Allocation.Targets.REMOVED)
            .filter(presentation__configuration_id__in=second_result.stuck_configuration)
            .update(**allocation_update_fields),
        )

        result = clean_configs()
        self.assertFalse(result.stuck_configuration)
        svc: Service
        for i, svc in enumerate(svcs):
            skipped_vss = set()
            skipped_cfgs = svc.configurations
            self.assertEqual(svc.options.max_history_length, i + 1)
            # max_history_length (=i+1) + one active and one inactive cfgs
            self.assertEqual(
                svc.options.max_history_length + len(states_from_last_active),
                skipped_cfgs.count(),
                f"wrong number of left configurations for {svc}",
            )
            for cfg in skipped_cfgs.all():
                self.assertEqual(n_vss_for_cfg, len(cfg.vss))
                skipped_vss |= set(vs.id for vs in cfg.vss)
            self.assertSetEqual(
                skipped_vss, set(VirtualServer.objects.filter(service=svc).values_list("id", flat=True))
            )

        # check that second use of function doesn't delete any cfg or vs from db
        def get_ids(model) -> typing.Set[int]:
            return set(model.objects.all().values_list("id", flat=True))

        cfg_ids = get_ids(Configuration)
        vs_ids = get_ids(VirtualServer)
        clean_configs()
        self.assertSetEqual(cfg_ids, get_ids(Configuration))
        self.assertSetEqual(vs_ids, get_ids(VirtualServer))


@cases.patching(
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=None),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", return_value=defaultdict(list), autospec=True),
    patch(
        "l3grafanasync.services.GrafanaApi.push_dashboard", autospec=True, return_value=PushResponse(id=1, uid="abc")
    ),
    patch("l3rtsync.utils.sync", autospec=True, side_effect=lambda l: (l, [])),
)
@override_settings(GRAFANA_URL=None)
class TestTasksChain(RESTAPITransactionTestCase):
    MOCKED_FAILING_TASK_ERROR = "[EXPECTED test error - don't worry] Error in mocked_failing_task"
    DEFAULT_TIMEOUT: float = 5 * 60

    @staticmethod
    @shared_task
    def mocked_failing_task(*args, **kwargs):
        raise Exception(TestTasksChain.MOCKED_FAILING_TASK_ERROR)

    def setUp(self) -> None:
        self.lb: LoadBalancer = LoadBalancer.objects.create(
            fqdn="lb.ya",
            location=[LocationNetwork.LOCATION_CHOICES.VLA],
            state=LoadBalancer.STATE_CHOICES.ACTIVE,
        )
        LoadBalancerAccess.objects.create(abc="Logbroker", balancer=self.lb)
        self.svc: Service = Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        self.rs: RealServer = RealServer.objects.create(
            fqdn="my.yn", ip="2.3.4.5", group="", location=[LocationNetwork.LOCATION_CHOICES.VLA]
        )
        self.vs: VirtualServer = VirtualServer.objects.create(
            ip="1.2.3.4",
            port=80,
            protocol=VirtualServer.PROTOCOL_CHOICES.TCP,
            config={"ANNOUNCE": True},
            service=self.svc,
            rs_ids=[self.rs.id],
        )

    def create_cfg(self) -> Configuration:
        cfg: Configuration = Configuration.objects.create(
            service=self.svc, state=Configuration.STATE_CHOICES.PENDING, vs_ids=[self.vs.id]
        )
        cfg.create_presentations()
        return cfg

    @parameterized.expand(
        (
            ("l3mgr.tasks.change_config_state",),
            ("l3mgr.tasks._commit_svn_config",),
            ("l3mgr.tasks._update_fw",),
            ("l3mgr.tasks._success_config",),
            ("l3mgr.tasks.validate_lbs",),
            ("l3mgr.tasks._deploy_lb_config_prl",),
            ("l3mgr.tasks._wait_group_result",),
            # ("l3mgr.tasks._schedule_vs_states_prl",),
            ("l3mgr.tasks._post_deploy_processing_prl",),
        )
    )
    @with_worker
    @patch.object(LoadBalancer, "exec_remotely")
    @patch("l3mgr.tasks._push_svc")
    def test__build_configuration_deployment_tasks(
        self, failing_task: str, mocked__push_svc: Mock, mock_lb_exec_remotely: Mock
    ):
        mock_lb_exec_remotely.return_value.fetch_balancer_info = Mock(
            return_value=([((self.vs.ip, self.vs.port, self.vs.protocol), {self.rs.ip})], {self.vs.ip})
        )
        mocked__push_svc.delay = TestTasksChain.dummy_task.delay
        self.assertEqual(self.vs.balancers.get(), self.lb)
        cfg: Configuration = self.create_cfg()
        release_service_event: threading.Event = threading.Event()

        from l3mgr.utils.tasks import release_service_lock

        def _waiter(svc_id: int, cfg_id: int):
            release_service_lock(svc_id, cfg_id)
            release_service_event.set()

        with patch(failing_task) as mocked_task, patch(
            "l3mgr.utils.tasks.release_service_lock", autospec=True, side_effect=_waiter
        ):
            mocked_task.signature = TestTasksChain.mocked_failing_task.signature
            mocked_task.si = TestTasksChain.mocked_failing_task.si
            mocked_task.s = TestTasksChain.mocked_failing_task.s
            res: AsyncResult = _delay_configuration_deployment(cfg, Configuration.STATE_CHOICES.PENDING)
            with self.assertRaisesMessage(Exception, TestTasksChain.MOCKED_FAILING_TASK_ERROR):
                res.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertTrue(release_service_event.wait(self.DEFAULT_TIMEOUT))
            self.assertFalse(check_service_locked(self.svc.id))

    @override_celery_settings(task_always_eager=True)
    @patch("l3mgr.tasks._update_config")
    @patch.object(LoadBalancer, "exec_remotely")
    def test_deploy_lb_config_should_call_update_config(self, exec_remotely_mock: Mock, update_config_mock: Mock):
        self.assertEqual(self.vs.balancers.get(), self.lb)
        m = Mock()
        m.start_keepalived.return_value = StartResult.STARTED
        m.stop_keepalived.return_value = StopResult.STOPPED
        m.fetch_balancer_info.return_value = (
            [((self.vs.ip, self.vs.port, self.vs.protocol), {self.rs.ip})],
            {self.vs.ip},
        )
        exec_remotely_mock.return_value = m
        result: AsyncResult = tasks.deploy_lb_config(self.lb.id)
        self.assertTrue(result.successful())
        update_config_mock.assert_called_once_with(self.lb.id, None, cfg_ids=[])

    @with_worker
    @patch.object(LoadBalancer, "exec_remotely")
    def test_default__build_configuration_deployment_tasks(self, mock_lb_exec_remotely: Mock):
        mock_lb_exec_remotely.return_value.fetch_balancer_info = Mock(
            return_value=([((self.vs.ip, self.vs.port, self.vs.protocol), {self.rs.ip})], {self.vs.ip})
        )
        cfg: Configuration = self.create_cfg()
        release_service_event: threading.Event = threading.Event()

        from l3mgr.utils.tasks import release_service_lock

        def _waiter(svc_id: int, cfg_id: int):
            release_service_lock(svc_id, cfg_id)
            release_service_event.set()

        with patch("l3mgr.utils.tasks.release_service_lock", side_effect=_waiter):
            res: AsyncResult = _delay_configuration_deployment(cfg, Configuration.STATE_CHOICES.PENDING)
            res.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertTrue(release_service_event.wait(timeout=self.DEFAULT_TIMEOUT))
        self.assertFalse(check_service_locked(self.svc.id))

    @staticmethod
    @shared_task
    def dummy_task(*args, **kwargs):
        pass

    @with_worker
    @patch("l3mgr.tasks._build_deploy_lb_config_chain")
    def test_wait_group_result(self, mock_deploy_lb_config_chain: Mock):
        mock_deploy_lb_config_chain.return_value = chain(TestTasksChain.dummy_task.si())
        n = 5
        lb_ids = list(range(n))
        cfg_id = 1
        res = chain(
            _deploy_lb_config_prl.signature(args=(lb_ids, cfg_id), immutable=True),
            _wait_group_result.signature(args=(cfg_id,)),
        ).delay()
        res.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertEqual(states.SUCCESS, res.state)
        self.assertListEqual([((i, cfg_id),) for i in lb_ids], mock_deploy_lb_config_chain.call_args_list)


temp_directory_path = tempfile.mkdtemp(prefix="l3mgr-tests-TestRaceUpdateStates")


@override_settings(
    PGAAS_IAM_TOKEN_STORAGE_CACHE=DEFAULT_CACHE_ALIAS,
    CACHES={
        DEFAULT_CACHE_ALIAS: {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": temp_directory_path,
        },
        settings.FASTEST_CACHE: {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    },
)
class TestRaceUpdateStates(TransactionTestCase):
    DEFAULT_TIMEOUT: float = 5

    def setUp(self) -> None:
        self.lb: LoadBalancer = LoadBalancer.objects.create(
            fqdn="test.yndx.net",
            state=LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[LocationNetwork.LOCATION_CHOICES.MAN],
        )
        svc: Service = Service.objects.create(fqdn="test.yndx.net", abc="test")
        self.cfg: Configuration = Configuration.objects.create(service=svc)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(temp_directory_path)
        finally:
            super().tearDownClass()

    @staticmethod
    def run_process(process_args: typing.Tuple[typing.Callable, typing.Collection[typing.Any]]):
        process, args = process_args
        process(*args)

    @staticmethod
    def run_processes_concurrently(
        processes: typing.Collection[typing.Callable],
        args: typing.Collection[typing.Any],
    ):
        n = len(processes)
        with mp.Pool(n) as p:
            p.map(
                TestRaceUpdateStates.run_process,
                [(process, args) for process in processes],
            )

    @staticmethod
    @patch.object(LoadBalancer, "exec_remotely")
    def first_serial(lb_id: int, cfg_id: int, event_start: mp.Event, event_stop: mp.Event, mock_lb_exec_remotely: Mock):
        mock_lb_exec_remotely.return_value.fetch_balancer_info = Mock(return_value=("first", []))
        connection.ensure_connection()
        try:
            update_states(lb_id, cfg_id)
            event_start.set()
        finally:
            connection.close()

    @staticmethod
    @patch.object(LoadBalancer, "exec_remotely")
    def first_parallel(
        lb_id: int, cfg_id: int, event_start: mp.Event, event_stop: mp.Event, mock_lb_exec_remotely: Mock
    ):
        def waiting_side_effect(event_start: mp.Event) -> typing.Tuple[str, list]:
            event_start.set()
            return "first", []

        mock_lb_exec_remotely.return_value.fetch_balancer_info = Mock(
            side_effect=lambda: waiting_side_effect(event_start)
        )
        connection.ensure_connection()
        try:
            update_states(lb_id, cfg_id)
        finally:
            connection.close()

    @staticmethod
    def second(lb_id: int, cfg_id: int, event_start: mp.Event, event_stop: mp.Event):
        try:
            if not event_start.wait(timeout=TestRaceUpdateStates.DEFAULT_TIMEOUT):
                raise AssertionError("Timeout for event_start exceeded")
            with patch.object(LoadBalancer, "exec_remotely") as mock_lb_exec_remotely:
                mock_fetch_balancer_info = Mock()
                mock_fetch_balancer_info.return_value = ("second", [])
                mock_lb_exec_remotely.return_value.fetch_balancer_info = mock_fetch_balancer_info
                connection.ensure_connection()
                update_states(lb_id, cfg_id)
        finally:
            event_stop.set()
            connection.close()

    @patch("l3mgr.utils.tasks.persist_balancer_states")
    def test_serial(self, mock_persist_balancer_states: Mock):
        """
        Checks that task "update_states" can be executed in different processes one after another
        """
        with mp.Manager() as m:
            pqueue = m.Queue()
            event_start, event_stop = m.Event(), m.Event()
            mock_persist_balancer_states.side_effect = lambda _1, tag, _2: pqueue.put(tag)
            connection.close()
            TestRaceUpdateStates.run_processes_concurrently(
                (TestRaceUpdateStates.first_serial, TestRaceUpdateStates.second),
                (self.lb.id, self.cfg.id, event_start, event_stop),
            )
            self.assertTrue(event_stop.wait(timeout=TestRaceUpdateStates.DEFAULT_TIMEOUT))
            self.assertEqual(pqueue.get(), "first")
            self.assertEqual(pqueue.get(), "second")

    @patch("l3mgr.utils.tasks.persist_balancer_states")
    def test_parallel(self, persist_balancer_states_mock: Mock):
        """
        Checks that only one process at a time can execute task "update_states" (other raise self.retry)
        """

        def waiting_side_effect(tag: str, event_stop: mp.Event, pqueue: mp.Queue) -> None:
            self.assertTrue(
                event_stop.wait(timeout=TestRaceUpdateStates.DEFAULT_TIMEOUT), "Failed to wait until stop-event set"
            )
            pqueue.put(tag)

        with mp.Manager() as m:
            queue: mp.Queue = m.Queue()
            event_start: mp.Event = m.Event()
            event_stop: mp.Event = m.Event()
            persist_balancer_states_mock.side_effect = lambda _1, tag, _2: waiting_side_effect(tag, event_stop, queue)
            connection.close()
            with self.assertRaisesMessage(
                LockAcquireError,
                f"Lock `lb-state-{self.lb.id}` already acquired by None, requested by None",
            ):
                TestRaceUpdateStates.run_processes_concurrently(
                    (TestRaceUpdateStates.first_parallel, TestRaceUpdateStates.second),
                    (self.lb.id, self.cfg.id, event_start, event_stop),
                )
            self.assertEqual(queue.get(), "first")
            self.assertTrue(queue.empty())


class TestWaitVsStates(TestCase):
    def setUp(self) -> None:
        self.lb = LoadBalancer.objects.create(fqdn="test.yndx.net")
        self.svc = Service.objects.create(fqdn="test.yndx.net", abc="test")
        self.v_servers: typing.List[VirtualServer] = VirtualServer.objects.bulk_create(
            VirtualServer(service=self.svc, ip=ip, port=80, protocol=VirtualServer.PROTOCOL_CHOICES.TCP, config={})
            for ip in ("1:2:3:4::0", "2:3:4:5::0")
        )
        self.vs_states: typing.List[VirtualServerState] = VirtualServerState.objects.bulk_create(
            VirtualServerState(balancer=self.lb, vs=vs) for vs in self.v_servers
        )
        self.cfg: Configuration = Configuration.objects.create(service=self.svc)

    def setup_parameters(
        self,
        vs_bound_to_cfg: bool,
        first_vs_state: VirtualServerState.STATE_CHOICES,
        second_vs_state: VirtualServerState.STATE_CHOICES,
    ):
        self.cfg.vs_ids = [vs.id for vs in self.v_servers] if vs_bound_to_cfg else []
        self.cfg.save(update_fields=["vs_ids"])
        self.vs_states[0].state = first_vs_state
        self.vs_states[1].state = second_vs_state
        VirtualServerState.objects.bulk_update(self.vs_states, fields=["state"])

    @parameterized.expand(
        [
            # INACTIVE raises an error anyway
            (VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.INACTIVE),
            (VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.ACTIVE),
            (VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.ANNOUNCED),
            (VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.INACTIVE),
            (VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.INACTIVE),
            # ACTIVE raises an error only if vs_ip was announced
            (VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.ACTIVE),
            (VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.ANNOUNCED),
        ]
    )
    @patch("l3mgr.tasks.update_states")
    def test_wait_vs_states_raising(
        self,
        first_vs_state: VirtualServerState.STATE_CHOICES,
        second_vs_state: VirtualServerState.STATE_CHOICES,
        mocked_update_states: Mock,
    ) -> None:
        self.setup_parameters(True, first_vs_state, second_vs_state)
        unready_vs_ids = []
        if self.vs_states[0].state != VirtualServerState.STATE_CHOICES.ANNOUNCED:
            unready_vs_ids.append(self.vs_states[0].vs.id)
        if self.vs_states[1].state not in {
            VirtualServerState.STATE_CHOICES.ANNOUNCED,
            VirtualServerState.STATE_CHOICES.ACTIVE,
        }:
            unready_vs_ids.append(self.vs_states[1].vs.id)
        with self.assertRaisesMessage(
            Exception, f"VSs are not ready for CFG #{self.cfg.id} on LB #{self.lb.id}: {unready_vs_ids}"
        ):
            wait_vs_states(self.lb.id, self.cfg.id, [self.v_servers[0].ip])

    @parameterized.expand(
        [
            # if vs not in cfg.vs_ids, no errors will be raised
            (False, VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.INACTIVE),
            (False, VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.ACTIVE),
            (False, VirtualServerState.STATE_CHOICES.INACTIVE, VirtualServerState.STATE_CHOICES.ANNOUNCED),
            (False, VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.INACTIVE),
            (False, VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.INACTIVE),
            (False, VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.ACTIVE),
            (False, VirtualServerState.STATE_CHOICES.ACTIVE, VirtualServerState.STATE_CHOICES.ANNOUNCED),
            (False, VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.ACTIVE),
            (False, VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.ANNOUNCED),
            # ACTIVE raises an error only if vs_ip was announced
            (True, VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.ACTIVE),
            # ANNOUNCED does not raise an error
            (True, VirtualServerState.STATE_CHOICES.ANNOUNCED, VirtualServerState.STATE_CHOICES.ANNOUNCED),
        ]
    )
    @patch("l3mgr.tasks.update_states")
    def test_wait_vs_states_normal(
        self,
        vs_bound_to_cfg: bool,
        first_vs_state: VirtualServerState.STATE_CHOICES,
        second_vs_state: VirtualServerState.STATE_CHOICES,
        mocked_update_states: Mock,
    ) -> None:
        self.setup_parameters(vs_bound_to_cfg, first_vs_state, second_vs_state)
        wait_vs_states(self.lb.id, self.cfg.id, [self.v_servers[0].ip])


@override_settings(
    CACHES={cache.DEFAULT_CACHE_ALIAS: {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
    PGAAS_IAM_TOKEN_STORAGE_CACHE=DEFAULT_CACHE_ALIAS,
)
class StateUpdateSelectionTestCase(TestCase):
    def setUp(self):
        self.balancers: typing.Dict[int, LoadBalancer] = {
            lb.id: lb
            for lb in LoadBalancer.objects.bulk_create(
                [
                    LoadBalancer(
                        fqdn=f"vlx-lb-{state}-{mode}.yndx.net",
                        location=[LocationNetwork.LOCATION_CHOICES.VLX],
                        state=state,
                        mode=mode,
                    )
                    for state, mode in itertools.product(
                        LoadBalancer.STATE_CHOICES.values, LoadBalancer.ModeChoices.values
                    )
                ]
            )
        }

        self.svc = Service.objects.create(abc="test", fqdn="test.yndx.net")
        self.vs = VirtualServer.objects.create(
            service=self.svc,
            ip="2a02::4ca",
            port=8181,
            protocol=VirtualServer.PROTOCOL_CHOICES.TCP,
            config=test_fields.make_config(),
        )
        self.rs = RealServer.objects.create(
            fqdn="vlx-mnt-server.yandex.net",
            ip="2a02:6b8:b010:31::8080",
            group="",
            location=[LocationNetwork.LOCATION_CHOICES.VLX],
        )

        ts = timezone.now() - timedelta(days=1)
        VirtualServerState.objects.bulk_create(
            [
                VirtualServerState(balancer_id=lb_id, vs=self.vs, state=VirtualServerState.STATE_CHOICES.INACTIVE)
                for lb_id in self.balancers
            ]
        )
        VirtualServerState.objects.filter(vs=self.vs).update(timestamp=ts)
        RealServerState.objects.bulk_create(
            [
                RealServerState(
                    balancer_id=lb_id,
                    vs=self.vs,
                    server=self.rs,
                    fwmark=1,
                    state=RealServerState.STATE_CHOICES.INACTIVE,
                )
                for lb_id in self.balancers
            ]
        )
        RealServerState.objects.filter(server_id=self.rs).update(timestamp=ts)

        self.config = Configuration.objects.create(
            service=self.svc, vs_ids=[self.vs.pk], state=Configuration.STATE_CHOICES.ACTIVE
        )

    @parameterized.expand(((True,), (False,)))
    def test_schedule_all_except_disabled(self, allow_used_by_machine_feature: bool):
        if allow_used_by_machine_feature:
            AllowUsedByMachineFeature.objects.bulk_create(
                [AllowUsedByMachineFeature(balancer_id=lb_id) for lb_id in self.balancers]
            )

        with patch("l3mgr.tasks.update_states.apply_async") as mock:
            schedule_state_updating()

        self.assertTrue(6, len(mock.call_args_list))
        called_lb_ids = {c[1]["args"][0] for c in mock.call_args_list}
        should_be_called = {lb.id for lb in self.balancers.values() if lb.mode != LoadBalancer.ModeChoices.DISABLED}

        self.assertSetEqual(should_be_called, called_lb_ids)

    @parameterized.expand(
        [
            (LoadBalancer.ModeChoices.ACTIVE, True),
            (LoadBalancer.ModeChoices.IDLE, False),
            (LoadBalancer.ModeChoices.DISABLED, False),
        ]
    )
    def test_update_state_with_lb_modes(self, mode: "LoadBalancer.ModeChoices", should_be_updated: bool):
        """
        Only active balancers might update state via exec_remotely.
        Checks exec_remotely calls and update's result.
        """
        lb: LoadBalancer = {_lb for _lb in self.balancers.values() if _lb.mode == mode}.pop()

        with patch.object(LoadBalancer, "exec_remotely") as mock_lb:
            mock_lb.return_value.fetch_balancer_info = Mock(
                return_value=([((self.vs.ip, self.vs.port, self.vs.protocol), {self.rs.ip})], {self.vs.ip})
            )
            update_states(lb.id)

            vs_state: VirtualServerState = VirtualServerState.objects.get(balancer_id=lb.id, vs_id=self.vs.id)
            rs_state: RealServerState = RealServerState.objects.get(
                balancer_id=lb.id, vs_id=self.vs.id, server_id=self.rs.id
            )

            if should_be_updated:
                mock_lb.assert_called_once()
                self.assertEquals(VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)
                self.assertEquals(RealServerState.STATE_CHOICES.ACTIVE, rs_state.state)
            else:
                mock_lb.assert_not_called()
                self.assertEquals(VirtualServerState.STATE_CHOICES.INACTIVE, vs_state.state)
                self.assertEquals(RealServerState.STATE_CHOICES.INACTIVE, rs_state.state)

    @skip("TRAFFIC-13194")
    def test_skip_locked_lbs(self):
        # locked balancers should be skipped and not scheduled for update
        pass

    @skip("TRAFFIC-13194")
    def test_inactive_forcing(self):
        # not disable balancer in active state should be scheduled for update, even if they don't have vs-states or active configuration
        # (NB this requirement can be obsoleted)
        pass

    @skip("TRAFFIC-13194")
    def test_schedule_expires_distribution(self):
        # task should be scheduled with some distribution
        pass
