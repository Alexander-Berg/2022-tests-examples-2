import contextlib
import enum
import itertools
import logging
import threading
import time
import typing
import unittest
from collections import defaultdict
from queue import Queue
from unittest import skip
from unittest.mock import patch, Mock

import celery
import celery.result
import celery.states
from celery import exceptions
from django.db import transaction
from django.db.models import Q
from django.dispatch import receiver
from django.test import override_settings
from parameterized import parameterized
from rest_framework.test import APIClient

from l3balancer.exceptions import BalancerCommunicationException
from l3agent import models as agent_models
from l3balancer.services import StartResult, StopResult
from l3common.tests import cases
from l3common.tests.cases import patching, override_celery_settings, verbose_queries, with_worker
from l3common.typing import alias
from l3grafanasync.services import PushResponse
from l3mgr import models as mgr_models
from l3mgr import signals as mgr_signals
from l3mgr import tasks as mgr_tasks
from l3mgr.tests import test_fields
from l3mgr.tests.base import RESTAPITest, RESTAPITransactionTestCase
from l3mgr.tests.test_tasks import (
    _BalancersPrepareMixin,
    compress,
    ExpectedTestException,
    _ORIGINAL_UNEXPECTED_CONFIGURATION_STATE_EXCEPTION_NEW,
)
from l3testing import models as testing_models
from l3testing import signals as testing_signals
from l3testing import utils as testing_utils
from .. import models, signals, tasks, states

logger: logging.Logger = logging.getLogger(__name__)


class ExpectedRetriesExceededError(exceptions.MaxRetriesExceededError):
    def __init__(self, ignored_msg: str = None, *args, **kwargs) -> None:
        super().__init__("[EXPECTED ERROR] - don't worry", *args, **kwargs)


class MetricsMock:
    metrics: typing.Dict[str, int] = defaultdict(int)
    current_label: str = ""

    def __call__(self, label):
        self.current_label = label
        return self

    def inc(self):
        self.metrics[self.current_label] += 1


@contextlib.contextmanager
def patch_task(task: celery.Task):
    with patch.object(task, "max_retries", 0), patch.object(
        task, "MaxRetriesExceededError", ExpectedRetriesExceededError
    ):
        yield task


_deployment_task: celery.Task = typing.cast(celery.Task, tasks.process_deployment)
_process_lb_update_requests_task: celery.Task = typing.cast(celery.Task, mgr_tasks.process_lb_update_requests)
_wait_for_lb_update_request_task: celery.Task = typing.cast(celery.Task, mgr_tasks.wait_for_lb_update_request)


class _BalancerSetupMixin(unittest.TestCase):
    lb: mgr_models.LoadBalancer
    testing_lb: mgr_models.LoadBalancer


class _ConfigurationSetupMixin(unittest.TestCase):
    service: mgr_models.Service
    machine: models.ServiceDeploymentMachine
    rs: mgr_models.RealServer
    vs: mgr_models.VirtualServer
    configuration: mgr_models.Configuration

    def setUp(self) -> None:
        super().setUp()
        self.service: mgr_models.Service = mgr_models.Service.objects.create(
            fqdn="test.localhost", abc="dostavkatraffika"
        )
        self.service.options.dsm = True
        self.service.options.dsm_mode = mgr_models.Service.Options.DsmMode.SOLELY
        self.service.save()
        self.machine: models.ServiceDeploymentMachine = self.service.deployment_machine

        self.rs: mgr_models.RealServer = mgr_models.RealServer.objects.create(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            config={},
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.VLA],
        )
        self.vs: mgr_models.VirtualServer = mgr_models.VirtualServer.objects.create(
            service=self.service,
            ip="2a02:6b8:b040:3100:ccc::4c9",
            port=1234,
            protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
            config=test_fields.make_config(),
            rs_ids=[self.rs.id],
        )
        self.configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[self.vs.id], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )


class _SimpleBalancerSetupMixin(_ConfigurationSetupMixin):
    def setUp(self) -> None:
        super().setUp()
        self.lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            fqdn="vla1-lb2b.yndx.net",
            location=self.rs.location,
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )
        mgr_models.AllowUsedByMachineFeature.objects.create(balancer=self.lb)
        mgr_models.LoadBalancerAccess.objects.create(balancer=self.lb, abc=self.service.abc)
        self.testing_lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            fqdn="vla1-test.yndx.net",
            test_env=True,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.VLA],
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )


class _MultiRegionBalancerSetupMixin(_ConfigurationSetupMixin):
    def setUp(self) -> None:
        super().setUp()
        self.lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            fqdn="vla1-lb2b.yndx.net",
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.VLA, mgr_models.LocationNetwork.LOCATION_CHOICES.IVA],
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )
        mgr_models.AllowUsedByMachineFeature.objects.create(balancer=self.lb)
        mgr_models.LoadBalancerAccess.objects.create(balancer=self.lb, abc=self.service.abc)
        self.testing_lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            fqdn="vla1-test.yndx.net",
            test_env=True,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.VLA],
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )


class _DeploymentTestCaseMixin(unittest.TestCase):
    def refresh_from_db(self):
        assert hasattr(self, "configuration")
        assert hasattr(self, "machine")
        assert hasattr(self, "deployment")
        self.configuration.refresh_from_db()
        self.machine.refresh_from_db()
        self.deployment.refresh_from_db()

    def assertInit(self, skip_tests: bool = False) -> None:
        with transaction.atomic(savepoint=True), patch_task(_deployment_task), verbose_queries(detailed=True):
            self.deployment: mgr_models.Deployment = mgr_models.Deployment.objects.create(
                configuration=self.configuration, target=mgr_models.Deployment.Targets.DEPLOYED, skip_tests=skip_tests
            )

        self.refresh_from_db()
        if skip_tests:
            self.assertEqual(mgr_models.Configuration.STATE_CHOICES.DEPLOYING, self.configuration.state)
            self.assertEqual(self.configuration.id, self.deployment.configuration_id)
            self.assertEqual(models.ServiceDeploymentMachine.States.DEPLOYING, self.machine.state)
            self.testing_task = []
        else:
            self.assertEqual(mgr_models.Configuration.STATE_CHOICES.TESTING, self.configuration.state)
            self.assertEqual(self.configuration.id, self.deployment.configuration_id)
            self.assertEqual(models.ServiceDeploymentMachine.States.TESTING, self.machine.state)
            testing_tasks: typing.List[testing_models.TestingTask] = self.deployment.testing_tasks.all()
            self.assertEqual(1, len(testing_tasks))
            self.testing_task = testing_tasks[0]

    def assertTestingTaskChangeResult(self, result: testing_models.TestingTask.Results) -> None:
        assert hasattr(self, "testing_lb")

        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(self.testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(self.testing_task.id, locked_task.id)
        with patch_task(_deployment_task):
            testing_utils.unlock_task(locked_task, self.testing_lb, result)
        self.testing_task.refresh_from_db()
        self.assertEqual(result, self.testing_task.result)

    def assertDeploying(self) -> None:
        self.refresh_from_db()
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.DEPLOYING, self.configuration.state)
        self.assertEqual(models.ServiceDeploymentMachine.States.DEPLOYING, self.machine.state)
        self.assertEqual(0, self.deployment.current_round)

    def assertAllocationChangeState(self, state: mgr_models.Allocation.UnlockState, rollback: bool) -> None:
        criteria = Q(rollback=rollback, service=self.service, deployment=self.deployment, balancer=self.lb)
        allocations: typing.List[mgr_models.Allocation] = self.deployment.allocations.filter(criteria).lock()
        self.assertEqual(1, len(allocations))
        allocation = allocations[0]
        self.assertEqual(self.lb.id, allocation.balancer.id)
        with patch_task(_deployment_task):
            allocations: typing.List[mgr_models.Allocation] = self.deployment.allocations.filter(
                pk=allocation.id
            ).unlock(state)
        self.assertEqual(1, len(allocations))
        allocation = allocations[0]

    def deployOnce(self, skip_tests: bool) -> None:
        self.assertInit(skip_tests)
        if not skip_tests:
            self.assertTestingTaskChangeResult(testing_models.TestingTask.Results.SUCCESS)
        self.assertDeploying()

        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.REACHED, False)

    def assertDeployOnce(self, skip_tests: bool = False) -> None:
        self.deployOnce(skip_tests)
        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(mgr_models.Deployment.States.REACHED, self.deployment.state)
        self.assertEqual(1, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.ACTIVE, self.configuration.state)


@patching(
    patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=True),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
)
@override_celery_settings(task_always_eager=True)
class NewConfigurationDeploymentTestCase(_MultiRegionBalancerSetupMixin, _DeploymentTestCaseMixin, RESTAPITest):
    @parameterized.expand(
        (
            testing_models.TestingTask.Results.FAILED,
            testing_models.TestingTask.Results.STOPPED,
            testing_models.TestingTask.Results.OVERDUE,
        )
    )
    def test_testing_task_failure(self, result: testing_models.TestingTask.Results) -> None:
        self.assertInit()
        self.assertTestingTaskChangeResult(result)

        self.refresh_from_db()
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.TEST_FAIL, self.configuration.state)
        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(mgr_models.Deployment.States.FAILED, self.deployment.state)
        self.assertEqual(0, self.deployment.current_round)
        self.assertFalse(self.deployment.allocations.exists())

    def test_allocation_failure(self) -> None:
        self.assertInit()
        self.assertTestingTaskChangeResult(testing_models.TestingTask.Results.SUCCESS)
        self.assertDeploying()

        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.FAILED, False)

        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.ROLLBACK, self.machine.state)
        self.assertEqual(0, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.FAIL, self.configuration.state)

        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.REACHED, True)

        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(mgr_models.Deployment.States.FAILED, self.deployment.state)
        self.assertEqual(-1, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.FAIL, self.configuration.state)

    def test_rollback_failure(self) -> None:
        self.assertInit()
        self.assertTestingTaskChangeResult(testing_models.TestingTask.Results.SUCCESS)
        self.assertDeploying()

        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.FAILED, False)

        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.ROLLBACK, self.machine.state)
        self.assertEqual(0, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.FAIL, self.configuration.state)

        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.FAILED, True)

        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.ROLLBACK_FAILED, self.machine.state)
        self.assertEqual(0, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.FAIL, self.configuration.state)

    def test_basic(self) -> None:
        self.assertDeployOnce()


@patching(
    patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=True),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
)
@override_celery_settings(task_always_eager=True)
class RedeploymentConfigurationTestCase(_SimpleBalancerSetupMixin, _DeploymentTestCaseMixin, RESTAPITest):
    def setUp(self) -> None:
        super().setUp()
        self.previous_configurations: typing.List[mgr_models.Configuration] = []
        self.previous_deployments: typing.List[mgr_models.Deployment] = []

    def assertDeployOnce(self, skip_tests: bool = False):
        super().assertDeployOnce(skip_tests)

        self.previous_configurations.append(self.configuration)
        self.previous_deployments.append(self.deployment)

        self.configuration = None
        self.deployment = None

    def refresh_from_db(self):
        super().refresh_from_db()
        self.refresh_previous_from_db()

    def refresh_previous_from_db(self):
        for m in itertools.chain(self.previous_configurations, self.previous_deployments):
            m.refresh_from_db()

    @override_settings(FW_UPDATE_PERIODIC=False)
    @patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True)
    def test_basic(self, upload_fw_mock):
        self.assertDeployOnce()

        self.configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[self.vs.id], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )

        self.assertDeployOnce()

        self.assertEqual(2, len(self.previous_configurations))
        self.assertEqual(2, len(self.previous_deployments))

        # check history is in order
        self.assertFalse(self.previous_configurations[0].history)
        self.assertListEqual([self.previous_configurations[0].id], self.previous_configurations[1].history)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.INACTIVE, self.previous_configurations[0].state)

        # check firewall rules were not uploaded twice as they have not changed
        upload_fw_mock.assert_called_once_with(self.previous_configurations[0])

    @override_settings(FW_UPDATE_PERIODIC=True)
    @patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True)
    def test_upload_fw_skipping(self, upload_fw_mock):
        self.assertDeployOnce(skip_tests=True)
        upload_fw_mock.assert_not_called()

    @parameterized.expand([(True,), (False,)])
    @patching(patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True))
    def test_same_config_redeploy(self, force_deploy: bool):
        self.assertDeployOnce()

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(1, len(self.previous_deployments))

        self.configuration: mgr_models.Configuration = self.previous_configurations.pop()

        self.assertDeployOnce(force_deploy)

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(2, len(self.previous_deployments))

        # check history in order
        self.assertFalse(self.previous_configurations[0].history)

    # todo: parametrize with skip-test
    @skip("TRAFFIC-12842")
    @patching(patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True))
    def test_same_config_redeploy_with_balancer_set_changed(self, force_deploy: bool = False):
        self.service.options.dsm_mode = mgr_models.Service.Options.DsmMode.OFF
        self.service.save()

        extra_lb: mgr_models.LoadBalancer = mgr_models.LoadBalancer.objects.create(
            fqdn="vla1-lb4b-extra.yndx.net",
            location=self.rs.location,
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )

        self.assertDeployOnce()

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(1, len(self.previous_deployments))

        self.configuration: mgr_models.Configuration = self.previous_configurations.pop()

        allocations: typing.List[mgr_models.Allocation] = list(self.lb.allocations.all())
        self.assertEqual(1, len(allocations))
        allocation: mgr_models.Allocation = allocations[0]
        self.assertEqual(mgr_models.Allocation.States.DEPLOYED, allocation.state)
        self.assertEqual(self.configuration.id, allocation.presentation.configuration_id)

        self.assertFalse(extra_lb.allocations.exists())

        mgr_models.AllowUsedByMachineFeature.objects.create(balancer=extra_lb)
        mgr_models.LoadBalancerAccess.objects.create(balancer=extra_lb, abc=self.service.abc)
        self.service.options.dsm_mode = mgr_models.Service.Options.DsmMode.OFF
        self.service.save()

        self.assertDeployOnce(force_deploy)

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(2, len(self.previous_deployments))

        self.configuration: mgr_models.Configuration = self.previous_configurations.pop()
        self.assertEqual(
            self.configuration.id, allocation.presentation.configuration_id, "Configuration is not the same"
        )

        allocations: typing.List[mgr_models.Allocation] = list(self.lb.allocations.all())
        self.assertEqual(2, len(allocations))
        self.assertIn(allocation, allocations)
        allocations.remove(allocation)
        allocation: mgr_models.Allocation = allocations[0]
        self.assertEqual(mgr_models.Allocation.States.DEPLOYED, allocation.state)
        self.assertEqual(self.configuration.id, allocation.presentation.configuration_id)

        allocations: typing.List[mgr_models.Allocation] = list(extra_lb.allocations.all())
        self.assertEqual(1, len(allocations))
        allocation: mgr_models.Allocation = allocations[0]
        self.assertEqual(mgr_models.Allocation.States.DEPLOYED, allocation.state)
        self.assertEqual(self.configuration.id, allocation.presentation.configuration_id)

        # check history in order
        self.assertFalse(self.previous_configurations[0].history)

    def assertEmptyRedeploy(self, skip_tests: bool = False):
        with transaction.atomic(savepoint=True), patch_task(_deployment_task), verbose_queries(detailed=True):
            self.deployment: mgr_models.Deployment = mgr_models.Deployment.objects.create(
                configuration=self.configuration, target=mgr_models.Deployment.Targets.DEPLOYED, skip_tests=skip_tests
            )
        self.assertDeploying()
        self.assertAllocationChangeState(mgr_models.Allocation.UnlockState.REACHED, False)

        self.refresh_from_db()
        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(mgr_models.Deployment.States.REACHED, self.deployment.state)
        self.assertEqual(1, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.ACTIVE, self.configuration.state)

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(1, len(self.previous_deployments))

        # check history in order
        self.assertFalse(self.previous_configurations[0].history)
        self.assertListEqual([self.previous_configurations[0].id], self.configuration.history)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.INACTIVE, self.previous_configurations[0].state)

    def assertRedundantDeploy(self, skip_tests: bool = False):
        with transaction.atomic(savepoint=True), patch_task(_deployment_task), verbose_queries(detailed=True):
            self.deployment: mgr_models.Deployment = mgr_models.Deployment.objects.create(
                configuration=self.configuration, target=mgr_models.Deployment.Targets.DEPLOYED, skip_tests=skip_tests
            )
        self.refresh_from_db()
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.ACTIVE, self.configuration.state)
        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(0, self.deployment.current_round)
        self.assertFalse(self.deployment.allocations.exists())
        self.assertEqual(mgr_models.Deployment.States.REDUNDANT, self.deployment.state)

    @parameterized.expand(list(itertools.product(*([(True, False)] * 3))))
    @patching(patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True))
    def test_deploy_empty_vs_config_to_remove(self, *skip_tests: bool):
        self.assertDeployOnce()
        self.configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )
        self.assertEmptyRedeploy(skip_tests[0])
        self.assertRedundantDeploy(skip_tests[1])
        self.assertRedundantDeploy(skip_tests[2])

    @parameterized.expand(list(itertools.product(*([(True, False)] * 3))))
    @patching(patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True))
    def test_deploy_empty_rs_config_to_remove(self, *skip_tests: bool):
        self.assertDeployOnce()

        self.vs.id = None
        self.vs.rs_ids = []
        self.vs.save()
        self.configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[self.vs.id], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )
        self.assertEmptyRedeploy(skip_tests[0])
        self.assertRedundantDeploy(skip_tests[1])
        self.assertRedundantDeploy(skip_tests[2])


@patching(
    patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=True),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
)
@override_celery_settings(task_always_eager=True)
@override_settings(FW_UPDATE_PERIODIC=False)
class NonstopDeploymentTestCase(_SimpleBalancerSetupMixin, _DeploymentTestCaseMixin, RESTAPITest):
    def setUp(self) -> None:
        super().setUp()
        self.previous_configurations: typing.List[mgr_models.Configuration] = []
        self.previous_deployments: typing.List[mgr_models.Deployment] = []

        self.injected_configuration: typing.Optional[mgr_models.Configuration] = None
        self.injected_deployment: typing.Optional[mgr_models.Deployment] = None
        self.inject_new_deploy: bool = False

    def assertDeployOnce(self, skip_tests: bool = False):
        super().assertDeployOnce(skip_tests)

        self.previous_configurations.append(self.configuration)
        self.previous_deployments.append(self.deployment)

        self.configuration = None
        self.deployment = None

    def assertDeploying(self) -> None:
        super().assertDeploying()

        if not self.inject_new_deploy:
            return
        self.inject_new_deploy = False

        self.injected_configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )
        self.injected_deployment: mgr_models.Deployment = mgr_models.Deployment.objects.bulk_create(
            [
                mgr_models.Deployment(
                    configuration=self.injected_configuration, target=mgr_models.Deployment.Targets.DEPLOYED
                )
            ]
        )[0]

        self.refresh_from_db()
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.PREPARED, self.injected_configuration.state)
        self.assertEqual(self.injected_configuration.id, self.injected_deployment.configuration_id)
        self.assertEqual(models.ServiceDeploymentMachine.States.DEPLOYING, self.machine.state)
        self.testing_task = []

    def refresh_from_db(self):
        super().refresh_from_db()
        for m in itertools.chain(self.previous_configurations, self.previous_deployments):
            m.refresh_from_db()
        if self.injected_configuration:
            self.injected_configuration.refresh_from_db()
        if self.injected_deployment:
            self.injected_deployment.refresh_from_db()

    def test_basic(self):
        """TRAFFIC-13256"""
        self.assertDeployOnce()

        self.configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=self.service, vs_ids=[], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )

        self.inject_new_deploy = True
        self.deployOnce(skip_tests=True)
        self.refresh_from_db()

        self.assertEqual(models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG, self.machine.state)
        self.assertEqual(mgr_models.Deployment.States.REACHED, self.deployment.state)
        self.assertEqual(1, self.deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.INACTIVE, self.configuration.state)

        self.assertEqual(mgr_models.Deployment.States.REDUNDANT, self.injected_deployment.state)
        self.assertEqual(0, self.injected_deployment.current_round)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.ACTIVE, self.injected_configuration.state)

        self.assertEqual(1, len(self.previous_configurations))
        self.assertEqual(1, len(self.previous_deployments))

        # check history is in order
        self.assertFalse(self.previous_configurations[0].history)
        self.assertEqual(mgr_models.Configuration.STATE_CHOICES.INACTIVE, self.previous_configurations[0].state)
        self.assertListEqual([self.previous_configurations[0].id], self.configuration.history)
        self.assertListEqual(
            [self.previous_configurations[0].id, self.configuration.id], self.injected_configuration.history
        )


MachineCheck = typing.Callable[
    [models.ServiceDeploymentMachine, typing.Union[states.RetryException, states.StopException]], None
]


class MachinesWaiter:
    def __init__(self, timeout: float = 15.0):
        self.machines_stopped_event = threading.Event()
        self.awaiting: typing.Dict[int, typing.List[typing.Optional[MachineCheck]]] = {}
        self.checks: typing.Optional[MachineCheck] = None
        self.fail: typing.Optional[Exception] = None

        self._default_timeout = timeout

        signals.deployment_machine_stopped.connect(self._callback)

    def _callback(
        self,
        sender: None,
        machine: models.ServiceDeploymentMachine,
        flow_control_exc: typing.Union[states.RetryException, states.StopException],
        **kwargs,
    ) -> None:
        try:
            awaiting = self.awaiting
            if machine.id not in awaiting:
                raise AssertionError(
                    f"Unexpected machine #{machine.id} if {machine.service.fqdn} stop receive: {flow_control_exc}"
                )
            if self.checks:
                self.checks(machine, flow_control_exc)
            checks: typing.List[typing.Optional[MachineCheck]] = awaiting[machine.id]
            check: typing.Optional[MachineCheck] = checks.pop()
            if check:
                check(machine, flow_control_exc)
            if not checks:
                del awaiting[machine.id]
            if not awaiting:
                self.machines_stopped_event.set()
        except Exception as e:
            self.fail = e
            self.machines_stopped_event.set()

    @contextlib.contextmanager
    def wait(
        self,
        machines_ids: typing.Union[typing.List[int], typing.Set[int], typing.Dict[int, MachineCheck]],
        checks: typing.Optional[MachineCheck] = None,
    ) -> None:
        if self.fail:
            raise AssertionError("Exception left after previous run") from self.fail

        self.machines_stopped_event.clear()
        self.awaiting.clear()
        self.fail = None
        if isinstance(machines_ids, (set, list)):
            d = defaultdict(list)
            for machine_id in machines_ids:
                d[machine_id].append(None)
        else:
            d = {k: [v] for k, v in machines_ids.items()}
        self.awaiting.update(d)
        self.checks = checks

        yield
        if not self.machines_stopped_event.wait(timeout=self._default_timeout):
            raise AssertionError(f"Failed to wait until machines stops: {self.awaiting}")
        if self.fail:
            raise AssertionError("Exception raise during waiting") from self.fail
        if self.awaiting:
            raise AssertionError(f"Some machines didn't stop: {self.awaiting}")


@patching(
    patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=True),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
    patch.object(_deployment_task, "max_retries", 0),
    patch.object(_deployment_task, "MaxRetriesExceededError", ExpectedRetriesExceededError),
)
@override_celery_settings(task_always_eager=True)
class SeveralServiceDeploymentTestCase(RESTAPITransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.waiter = MachinesWaiter()

        self.services: typing.List[mgr_models.Service] = mgr_models.Service.objects.bulk_create(
            [
                mgr_models.Service(fqdn="dostavkatraffika.localhost", abc="dostavkatraffika"),
                mgr_models.Service(fqdn="logbroker.localhost", abc="Logbroker"),
                mgr_models.Service(fqdn="portal.localhost", abc="portal"),
                mgr_models.Service(fqdn="home.localhost", abc="home"),
                mgr_models.Service(fqdn="tanker.localhost", abc="tanker"),
                mgr_models.Service(fqdn="wapconverter.localhost", abc="wapconverter"),
            ]
        )
        for service in self.services:
            service.options.dsm = True
            service.options.dsm_mode = mgr_models.Service.Options.DsmMode.SOLELY
        mgr_models.Service.objects.bulk_update(self.services, fields=["options"])

        self.machines: typing.List[
            models.ServiceDeploymentMachine
        ] = models.ServiceDeploymentMachine.objects.bulk_create(
            [models.ServiceDeploymentMachine(service=service) for service in self.services]
        )

        regions: typing.List[mgr_models.LocationRegion] = list(mgr_models.LocationRegion.objects.all())
        self.rss: typing.List[mgr_models.RealServer] = mgr_models.RealServer.objects.bulk_create(
            [
                mgr_models.RealServer(
                    fqdn=f"rs-{region.location[0]}.yandex.net",
                    ip=f"2a02:6b8:0:1482::{idx}",
                    config={},
                    location=[region.location[0]],
                )
                for idx, region in enumerate(regions, start=115)
            ]
        )

        self.lbs: typing.List[mgr_models.LoadBalancer] = mgr_models.LoadBalancer.objects.bulk_create(
            mgr_models.LoadBalancer(
                fqdn=f"lb-{region.location[0].lower()}.yndx.net",
                location=region.location,
                state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            )
            for region in regions
        )
        mgr_models.AllowUsedByMachineFeature.objects.bulk_create(
            [mgr_models.AllowUsedByMachineFeature(balancer=lb) for lb in self.lbs]
        )
        self.testing_lbs: typing.List[mgr_models.LoadBalancer] = mgr_models.LoadBalancer.objects.bulk_create(
            mgr_models.LoadBalancer(
                fqdn=f"test-lb-{region.location[0].lower()}.yndx.net",
                test_env=True,
                location=region.location,
                state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            )
            for region in regions
        )

        mgr_models.LoadBalancerAccess.objects.bulk_create(
            mgr_models.LoadBalancerAccess(balancer=lb, abc=service.abc) for service in self.services for lb in self.lbs
        )

    def refresh_from_db(self):
        for m in itertools.chain(self.deployments, self.machines, self.lbs, self.testing_lbs):
            m.refresh_from_db()

    def assertRetry(self, m: models.ServiceDeploymentMachine, flow_control_exc) -> None:
        self.assertIsInstance(
            flow_control_exc,
            states.RetryException,
            f"Unexpected termination for {m.id}: {m.service_id} - {m.service.fqdn}",
        )

    def assertStop(self, m: models.ServiceDeploymentMachine, flow_control_exc) -> None:
        self.assertIsInstance(
            flow_control_exc,
            states.StopException,
            f"Unexpected termination for {m.id}: {m.service_id} - {m.service.fqdn}",
        )
        self.assertIsNone(flow_control_exc.exc)

    def assertTestingReached(self, expected_tasks_count: int) -> typing.List[testing_models.TestingTask]:
        assert hasattr(self, "deployments")
        assert hasattr(self, "machines")
        self.assertSetEqual(
            {mgr_models.Configuration.STATE_CHOICES.TESTING}, {d.configuration.state for d in self.deployments}
        )
        self.assertSetEqual({models.ServiceDeploymentMachine.States.TESTING}, {m.state for m in self.machines})

        testing_tasks: typing.List[testing_models.TestingTask] = list(
            itertools.chain.from_iterable(d.testing_tasks.all() for d in self.deployments)
        )
        self.assertEqual(expected_tasks_count, len(testing_tasks))
        return testing_tasks

    def waiting(self, c, ids: typing.Union[None, typing.Set[int], typing.Dict[int, MachineCheck]] = None):
        assert hasattr(self, "waiter")

        if ids is None and isinstance(c, dict):
            ids = c
            c = None
        if not ids:
            ids = {m.id for m in self.machines}
        return self.waiter.wait(ids, c)

    def make_default_config(self, idx: int):
        assert hasattr(self, "services")

        vs: mgr_models.VirtualServer = mgr_models.VirtualServer.objects.create(
            service=self.services[idx % len(self.services)],
            ip=f"2a02:6b8:b040:3100:ccc::{idx}",
            port=1234,
            protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
            config=test_fields.make_config(),
            rs_ids=[self.rss[0].id],
        )
        configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=vs.service, vs_ids=[vs.id], state=mgr_models.Configuration.STATE_CHOICES.PREPARED
        )
        return configuration

    def assertAllocations(
        self,
        lb_fqdn: str,
        expected_states: typing.Dict[
            str, typing.Tuple[mgr_models.Allocation.Targets, mgr_models.Allocation.States, int]
        ],
    ) -> typing.List[mgr_models.Allocation]:
        allocations: typing.List[mgr_models.Allocation] = list(mgr_models.Allocation.objects.for_balancer(lb_fqdn))
        self.assertEqual(len(expected_states), len(allocations))
        self.assertDictEqual(
            expected_states,
            {a.service_id: (a.target, a.state, a.deployment_id) for a in allocations},
        )
        return allocations

    @with_worker
    def test_basic(self):
        """
        1. deploy empty configuration (no vs or no rs)
        2. rollback to empty configuration
        3. redeploy same configuration # todo:
        4. squash deployments # todo:
        5. rollback failure manual recovery # todo:
        6. failed deploy
        7. new deploy during rollback
        8. several balancers test # todo:
        """
        with self.waiting(self.assertRetry):
            self.deployments: typing.List[mgr_models.Deployment] = [
                mgr_models.Deployment.objects.create(
                    configuration=self.make_default_config(idx), target=mgr_models.Deployment.Targets.DEPLOYED
                )
                for idx in range(len(self.services))
            ]

        self.refresh_from_db()
        testing_tasks: typing.List[testing_models.TestingTask] = self.assertTestingReached(6)

        with self.waiting(self.assertRetry):
            for testing_task in testing_tasks:
                locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(self.testing_lbs[0])
                self.assertIsNotNone(locked_task, f"Lb {self.testing_lbs[0].fqdn} failed to lock task")
                self.assertEqual(testing_task.id, locked_task.id)
                testing_utils.unlock_task(locked_task, self.testing_lbs[0], testing_models.TestingTask.Results.SUCCESS)

        self.refresh_from_db()
        self.assertSetEqual(
            {mgr_models.Configuration.STATE_CHOICES.DEPLOYING}, {d.configuration.state for d in self.deployments}
        )
        self.assertSetEqual({models.ServiceDeploymentMachine.States.DEPLOYING}, {m.state for m in self.machines})
        self.assertSetEqual({0}, {d.current_round for d in self.deployments})

        for t in testing_tasks:
            t.refresh_from_db()
            self.assertEqual(testing_models.TestingTask.Results.SUCCESS, t.result)

        allocations: typing.List[mgr_models.Allocation] = list(
            mgr_models.Allocation.objects.for_balancer(self.lbs[0].fqdn)
        )
        self.assertEqual(6, len(allocations))
        self.assertSetEqual({mgr_models.Allocation.Targets.ACTIVE}, {a.target for a in allocations})
        self.assertSetEqual({mgr_models.Allocation.States.UNKNOWN}, {a.state for a in allocations})
        self.assertSetEqual({d.id for d in self.deployments}, {a.deployment_id for a in allocations})
        self.assertSetEqual({s.fqdn for s in self.services}, {a.service_id for a in allocations})

        with self.waiting(self.assertStop):
            for deployment in self.deployments:
                with transaction.atomic(savepoint=True):
                    qs = deployment.allocations.filter(
                        rollback=False,
                        service=deployment.configuration.service,
                        deployment=deployment,
                        balancer=self.lbs[0],
                    )
                    if deployment.configuration.service_id == self.services[0].id:
                        allocations: typing.List[mgr_models.Allocation] = qs.mark_skipped()
                        self.assertEqual(1, len(allocations))
                    else:
                        allocations: typing.List[mgr_models.Allocation] = qs.lock()
                        self.assertEqual(1, len(allocations))
                        allocation = allocations[0]
                        qs = deployment.allocations.filter(pk=allocation.id)
                        if deployment.configuration.service_id == self.services[1].id:
                            result = qs.mark_skipped()
                        else:
                            result = qs.unlock(mgr_models.Allocation.UnlockState.REACHED)
                        self.assertSetEqual({allocation.id}, {a.id for a in result})

        self.refresh_from_db()
        self.assertSetEqual(
            {models.ServiceDeploymentMachine.States.LOOKING_FOR_CONFIG}, {m.state for m in self.machines}
        )
        self.assertSetEqual(
            {mgr_models.Configuration.STATE_CHOICES.ACTIVE}, {d.configuration.state for d in self.deployments}
        )
        self.assertSetEqual({mgr_models.Deployment.States.REACHED}, {d.state for d in self.deployments})
        self.assertSetEqual({1}, {d.current_round for d in self.deployments})

        with alias(mgr_models.Allocation) as A:
            allocations: typing.List[A] = self.assertAllocations(
                self.lbs[0].fqdn,
                {
                    self.services[0].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, self.deployments[0].id),
                    self.services[1].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, self.deployments[1].id),
                    self.services[2].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.deployments[2].id),
                    self.services[3].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.deployments[3].id),
                    self.services[4].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.deployments[4].id),
                    self.services[5].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.deployments[5].id),
                },
            )

            self.assertSetEqual(
                {self.services[0].fqdn, self.services[1].fqdn}, {a.service_id for a in allocations if a.skipped}
            )
            self.assertSetEqual({self.services[1].fqdn}, {a.service_id for a in allocations if a.locked_at})

            with self.assertRaises(A.LockReleaseError), transaction.atomic(savepoint=True):
                self.deployments[0].allocations.unlock(A.UnlockState.REACHED)

            with self.waiting(self.assertStop, {m.id for m in self.machines[:2]}), transaction.atomic(savepoint=True):
                allocations = self.deployments[0].allocations.lock()
                self.assertEqual(1, len(allocations))
                allocations = self.deployments[0].allocations.unlock(A.UnlockState.REACHED)
                self.assertEqual(1, len(allocations))
                allocations = self.deployments[1].allocations.unlock(A.UnlockState.REACHED)
                self.assertEqual(1, len(allocations))

        # second deploy: skip first; same config for second (will fail on test), third (will fail on deploy),
        # and fourth (success one); empty for fifths (will fail on deploy) and sixths (success one)

        self.previous_deployments: typing.List[mgr_models.Deployment] = self.deployments

        configurations: typing.List[mgr_models.Configuration] = [d.configuration for d in self.deployments]

        def _recreate(cfg: mgr_models.Configuration) -> None:
            cfg.id = None
            cfg.state = mgr_models.Configuration.STATE_CHOICES.PREPARED
            if cfg.vs_ids:
                vss: typing.List[mgr_models.VirtualServer] = list(cfg.vss)
                for vs in vss:
                    vs.id = None
                vss: typing.List[mgr_models.VirtualServer] = mgr_models.VirtualServer.objects.bulk_create(vss)
                cfg.vs_ids = [vs.id for vs in vss]
            cfg.history = []
            cfg.save()

        _recreate(configurations[1])
        _recreate(configurations[2])
        _recreate(configurations[3])

        configurations[4].vs_ids = []
        _recreate(configurations[4])
        configurations[5].vs_ids = []
        _recreate(configurations[5])

        latest_updates = [m.updated_at for m in self.machines]
        with self.waiting(self.assertRetry, {m.id for m in self.machines[1:]}):
            self.deployments: typing.List[mgr_models.Deployment] = [
                mgr_models.Deployment.objects.create(configuration=conf, target=mgr_models.Deployment.Targets.DEPLOYED)
                for conf in configurations[1:]
            ]

        self.refresh_from_db()
        with alias(mgr_models.Configuration.STATE_CHOICES) as CS:
            self.assertListEqual(
                [CS.TESTING] * 3 + [CS.DEPLOYING] * 2, [d.configuration.state for d in self.deployments]
            )
        with alias(models.ServiceDeploymentMachine.States) as MS:
            self.assertListEqual([MS.TESTING] * 3 + [MS.DEPLOYING] * 2, [m.state for m in self.machines[1:]])

        testing_tasks: typing.List[testing_models.TestingTask] = list(
            itertools.chain.from_iterable(d.testing_tasks.all() for d in self.deployments)
        )
        self.assertEqual(3, len(testing_tasks))

        self.assertEqual(latest_updates[0], self.machines[0].updated_at)
        latest_updates = [m.updated_at for m in self.machines]

        with self.waiting(
            {
                self.machines[1].id: self.assertStop,
                self.machines[2].id: self.assertRetry,
                self.machines[3].id: self.assertRetry,
            }
        ), alias(testing_models.TestingTask.Results) as TR:
            for testing_task in testing_tasks:
                locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(self.testing_lbs[0])
                self.assertIsNotNone(locked_task)
                self.assertEqual(testing_task.id, locked_task.id)
                if testing_task.configuration.service.id == self.services[1].id:
                    testing_task_result = TR.FAILED
                else:
                    testing_task_result = TR.SUCCESS
                testing_utils.unlock_task(locked_task, self.testing_lbs[0], testing_task_result)

        self.refresh_from_db()
        with alias(mgr_models.Configuration.STATE_CHOICES) as CS:
            self.assertListEqual([CS.TEST_FAIL] + [CS.DEPLOYING] * 4, [d.configuration.state for d in self.deployments])
        with alias(models.ServiceDeploymentMachine.States) as MS:
            self.assertListEqual([MS.LOOKING_FOR_CONFIG] * 2 + [MS.DEPLOYING] * 4, [m.state for m in self.machines])
        self.assertSetEqual({0}, {d.current_round for d in self.deployments})

        self.assertEqual(latest_updates[0], self.machines[0].updated_at)
        self.assertEqual(latest_updates[4], self.machines[4].updated_at)
        self.assertEqual(latest_updates[5], self.machines[5].updated_at)

        for t in testing_tasks:
            t.refresh_from_db()
        self.assertDictEqual(
            {
                self.services[1].id: testing_models.TestingTask.Results.FAILED,
                self.services[2].id: testing_models.TestingTask.Results.SUCCESS,
                self.services[3].id: testing_models.TestingTask.Results.SUCCESS,
            },
            {t.configuration.service_id: t.result for t in testing_tasks},
        )

        with alias(mgr_models.Allocation) as A:
            self.assertAllocations(
                self.lbs[0].fqdn,
                {
                    self.services[0].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.previous_deployments[0].id),
                    self.services[1].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, self.previous_deployments[1].id),
                    self.services[2].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, self.deployments[1].id),
                    self.services[3].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, self.deployments[2].id),
                    self.services[4].fqdn: (A.Targets.REMOVED, A.States.UNKNOWN, self.deployments[3].id),
                    self.services[5].fqdn: (A.Targets.REMOVED, A.States.UNKNOWN, self.deployments[4].id),
                },
            )

        with self.waiting(
            {
                self.machines[2].id: self.assertRetry,
                self.machines[3].id: self.assertStop,
                self.machines[4].id: self.assertRetry,
                self.machines[5].id: self.assertStop,
            }
        ):
            for deployment in self.deployments[1:]:
                with transaction.atomic(savepoint=True):
                    allocations: typing.List[mgr_models.Allocation] = deployment.allocations.filter(
                        rollback=False,
                        service=deployment.configuration.service,
                        deployment=deployment,
                        balancer=self.lbs[0],
                    ).lock()
                    self.assertEqual(1, len(allocations))
                    allocation = allocations[0]
                    if deployment.configuration.service_id in {self.services[2].id, self.services[4].id}:
                        state = mgr_models.Allocation.UnlockState.FAILED
                    elif deployment.configuration.service_id in {self.services[3].id, self.services[5].id}:
                        state = mgr_models.Allocation.UnlockState.REACHED
                    else:
                        self.fail("Unexpected deployment")
                    deployment.allocations.filter(id=allocation.id).unlock(state)

        self.refresh_from_db()
        with alias(models.ServiceDeploymentMachine.States) as MS:
            self.assertDictEqual(
                {
                    self.services[0].id: MS.LOOKING_FOR_CONFIG,
                    self.services[1].id: MS.LOOKING_FOR_CONFIG,
                    self.services[2].id: MS.ROLLBACK,
                    self.services[3].id: MS.LOOKING_FOR_CONFIG,
                    self.services[4].id: MS.ROLLBACK,
                    self.services[5].id: MS.LOOKING_FOR_CONFIG,
                },
                {m.service_id: m.state for m in self.machines},
            )
        with alias(mgr_models.Configuration.STATE_CHOICES) as CS, alias(mgr_models.Deployment.States) as DS:
            self.assertDictEqual(
                {
                    self.services[1].id: (CS.TEST_FAIL, DS.FAILED, 0),
                    self.services[2].id: (CS.FAIL, DS.PROCESSING, 0),
                    self.services[3].id: (CS.ACTIVE, DS.REACHED, 1),
                    self.services[4].id: (CS.FAIL, DS.PROCESSING, 0),
                    self.services[5].id: (CS.ACTIVE, DS.REACHED, 1),
                },
                {
                    d.configuration.service_id: (d.configuration.state, d.state, d.current_round)
                    for d in self.deployments
                },
            )

        allocations: typing.List[mgr_models.Allocation] = list(
            mgr_models.Allocation.objects.for_balancer(self.lbs[0].fqdn)
        )
        self.assertEqual(5, len(allocations))

        with alias(mgr_models.Allocation) as A:
            p = self.previous_deployments
            d = self.deployments
            self.assertDictEqual(
                {
                    self.services[0].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, p[0].id, p[0].configuration_id),
                    self.services[1].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, p[1].id, p[1].configuration_id),
                    self.services[2].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, d[1].id, p[2].configuration_id),
                    self.services[3].fqdn: (A.Targets.ACTIVE, A.States.DEPLOYED, d[2].id, d[2].configuration_id),
                    self.services[4].fqdn: (A.Targets.ACTIVE, A.States.UNKNOWN, d[3].id, p[4].configuration_id),
                },
                {
                    a.service_id: (a.target, a.state, a.deployment_id, a.presentation.configuration_id)
                    for a in allocations
                },
            )

        # add deployments (first will fail, other will  and try to process them during rollback
        configurations[1].vs_ids = []
        _recreate(configurations[1])
        configurations[3].vs_ids = []
        _recreate(configurations[3])

        with self.waiting(self.assertRetry, {self.machines[1].id, self.machines[3].id}):
            self.assertEqual(self.deployments[0].configuration.service_id, configurations[1].service_id)
            self.assertEqual(self.deployments[2].configuration.service_id, configurations[3].service_id)
            self.deployments[0] = mgr_models.Deployment.objects.create(
                configuration=configurations[1], target=mgr_models.Deployment.Targets.DEPLOYED
            )
            self.deployments[2] = mgr_models.Deployment.objects.create(
                configuration=configurations[3], target=mgr_models.Deployment.Targets.DEPLOYED
            )

        self.refresh_from_db()

        with self.waiting({self.machines[1].id: self.assertRetry, self.machines[3].id: self.assertStop}):
            with transaction.atomic(savepoint=True):
                allocations: typing.List[mgr_models.Allocation] = list(
                    itertools.chain.from_iterable(
                        d.allocations.filter(
                            rollback=False,
                            service=d.configuration.service,
                            deployment=d,
                            balancer=self.lbs[0],
                        ).lock()
                        for d in (self.deployments[0], self.deployments[2])
                    )
                )
                for allocation in allocations:
                    if allocation.service.id == self.services[1].id:
                        state = mgr_models.Allocation.UnlockState.FAILED
                    elif allocation.service.id == self.services[3].id:
                        state = mgr_models.Allocation.UnlockState.REACHED
                    else:
                        self.fail(f"Unexpected service: {allocation.service.fqdn}")
                    mgr_models.Allocation.objects.filter(id=allocation.id).unlock(state)

            # todo: should be an error here as we should prevent moving new deployment while rollback in progress

        with self.waiting(self.assertStop, {self.machines[2].id, self.machines[4].id}):
            for deployment in (self.deployments[1], self.deployments[3]):
                with transaction.atomic(savepoint=True):
                    allocations: typing.List[mgr_models.Allocation] = deployment.allocations.filter(
                        rollback=True,
                        service=deployment.configuration.service,
                        deployment=deployment,
                        balancer=self.lbs[0],
                    ).lock()
                    self.assertEqual(1, len(allocations))
                    allocation = allocations[0]
                    deployment.allocations.filter(id=allocation.id).unlock(mgr_models.Allocation.UnlockState.REACHED)

        self.refresh_from_db()
        with alias(models.ServiceDeploymentMachine.States) as MS:
            self.assertDictEqual(
                {
                    self.services[0].id: MS.LOOKING_FOR_CONFIG,
                    self.services[1].id: MS.ROLLBACK,
                    self.services[2].id: MS.LOOKING_FOR_CONFIG,
                    self.services[3].id: MS.LOOKING_FOR_CONFIG,
                    self.services[4].id: MS.LOOKING_FOR_CONFIG,
                    self.services[5].id: MS.LOOKING_FOR_CONFIG,
                },
                {m.service_id: m.state for m in self.machines},
            )

        with alias(mgr_models.Configuration.STATE_CHOICES) as CS, alias(mgr_models.Deployment.States) as DS:
            self.assertDictEqual(
                {
                    self.services[1].id: (CS.FAIL, DS.PROCESSING, 0),
                    self.services[2].id: (CS.FAIL, DS.FAILED, -1),
                    self.services[3].id: (CS.ACTIVE, DS.REACHED, 1),
                    self.services[4].id: (CS.FAIL, DS.FAILED, -1),
                    self.services[5].id: (CS.ACTIVE, DS.REACHED, 1),
                },
                {
                    d.configuration.service_id: (d.configuration.state, d.state, d.current_round)
                    for d in self.deployments
                },
            )
        allocations: typing.List[mgr_models.Allocation] = list(
            mgr_models.Allocation.objects.for_balancer(self.lbs[0].fqdn)
        )
        self.assertEqual(4, len(allocations))

        with alias(mgr_models.Allocation) as A:
            p = self.previous_deployments
            d = self.deployments
            self.assertSetEqual({A.Targets.ACTIVE}, {a.target for a in allocations})
            self.assertDictEqual(
                {
                    self.services[0].fqdn: (A.States.DEPLOYED, p[0].id, p[0].configuration_id),
                    self.services[1].fqdn: (A.States.UNKNOWN, d[0].id, p[1].configuration_id),
                    self.services[2].fqdn: (A.States.DEPLOYED, d[1].id, p[2].configuration_id),
                    # self.services[3].fqdn: (d[2].id, d[2].configuration_id),
                    self.services[4].fqdn: (A.States.DEPLOYED, d[3].id, p[4].configuration_id),
                },
                {a.service_id: (a.state, a.deployment_id, a.presentation.configuration_id) for a in allocations},
            )


@patching(
    patch("l3mgr.utils.get_ip", autospec=True, return_value="2a02:6b8:0:1a00::1b1a"),
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
)
@override_celery_settings(task_always_eager=True)
class ConfigurationGeneratorTestCase(_MultiRegionBalancerSetupMixin, _DeploymentTestCaseMixin, RESTAPITest):
    _generated_configs: typing.List[typing.Tuple[str, str]] = []

    def _svc_commit_hook(self, cfg: mgr_models.Configuration) -> None:
        mocked_rs = Mock(id=467, fqdn="mnt-myt.yandex.net", ip="2a02:6b8:0:1482::115", config={"WEIGHT": 1})
        mocked_rs.__str__ = lambda _: f"({self.rs.id}) [{self.rs.fqdn}] {self.rs.ip}"

        mocked_rs_state = Mock(id=1234, fwmark=1001, server=mocked_rs)
        with patch("l3mgr.models.VirtualServer.get_states_for_lb", return_value=[mocked_rs_state]):
            self._generated_configs = list(cfg.generator())

    @parameterized.expand([(True,), (False,)])
    def test_default_generator(self, force_deploy: bool) -> None:
        with patch(
            "l3mgr.utils.tasks.commit_svn_configuration",
            autospec=True,
            return_value=True,
            side_effect=self._svc_commit_hook,
        ):
            self.assertDeployOnce(force_deploy)
        filepath, content = self._generated_configs[0]

        (expected_filepath, expected_content) = (
            "test.localhost/vla1-lb2b.yndx.net/2a02:6b8:b040:3100:ccc::4c9-1234-TCP.conf",
            f"\n# SVC: {self.service}"
            f"\n# LB: {self.lb}"
            f"\n# VS: {self.vs}"
            "\nvirtual_server 2a02:6b8:b040:3100:ccc::4c9 1234 {"
            "\n        protocol TCP\n        \n          "
            '\n        quorum_up   "/etc/keepalived/quorum-handler2.sh up   2a02:6b8:b040:3100:ccc::4c9,1234/TCP,b-100,1"'
            '\n        quorum_down "/etc/keepalived/quorum-handler2.sh down 2a02:6b8:b040:3100:ccc::4c9,1234/TCP,b-100,1"'
            "\n        quorum 1"
            "\n        hysteresis 0"
            "\n          \n        "
            "\n        alpha"
            "\n        omega"
            "\n        lvs_method TUN"
            "\n        lvs_sched wrr"
            "\n        \n        "
            "\n        delay_loop 10"
            "\n        \n        "
            "\n        \n        real_server 2a02:6b8:0:1482::115 1234 {"
            f"\n                # RS: ({self.rs.id}) [{self.rs.fqdn}] {self.rs.ip}"
            "\n                # RS state ID: 1234"
            "\n                weight 1"
            "\n                \n                HTTP_GET {"
            "\n                        \n                        "
            "\n                        url {"
            "\n                                path /ping"
            "\n                                status_code 204"
            "\n                                "
            "\n                        }"
            "\n                        connect_ip 2a02:6b8:b040:3100:ccc::4c9"
            "\n                        connect_port 1234"
            "\n                        bindto 2a02:6b8:0:1a00::1b1a"
            "\n                        connect_timeout 1"
            "\n                        fwmark 1001"
            "\n                        "
            "\n                        nb_get_retry 1"
            "\n                        "
            "\n                        delay_before_retry 1"
            "\n                        "
            "\n                }"
            "\n        }"
            "\n        \n}\n",
        )

        self.assertEqual(expected_filepath, filepath)

        self.maxDiff = None
        self.assertEqual(expected_content, content)


@patching(
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", autospec=True, return_value=defaultdict(list)),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=True),
    patch("l3mgr.models.Configuration.generator", return_value=[]),
)
@override_celery_settings(task_always_eager=True)
class SVNCommitActionTestCase(_MultiRegionBalancerSetupMixin, _DeploymentTestCaseMixin, RESTAPITest):
    def test_changes(self):
        filepath = "test.localhost/README.md"

        mocked_svn = Mock(
            **{
                "info.return_value": {"entry_path": ""},
                "status.return_value": [Mock(name=filepath, type_raw_name="unversioned")],
            }
        )
        with patch("os.path.relpath", return_value=filepath), patch(
            "svn.local.LocalClient", autospec=True, return_value=mocked_svn
        ):
            self.assertDeployOnce()

        mocked_svn.add.assert_called_once_with(filepath)
        mocked_svn.commit.assert_called_once()

    def test_unchanged_repo(self):
        mocked_svn = Mock(**{"info.return_value": {"entry_path": ""}, "status.return_value": []})
        with patch("svn.local.LocalClient", autospec=True, return_value=mocked_svn):
            self.assertDeployOnce()

        # no changes for commit
        mocked_svn.commit.assert_not_called()


def _commit_svn_configuration(cfg):
    list(cfg.generator())


@override_settings(AUTO_SKIP_INACTIVE_AGENT_ALLOCATIONS=True)
@cases.patching(
    patch("l3mgr.utils.firewall.find_fw_svcs_by_ip", return_value=defaultdict(list), autospec=True),
    patch("l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None),
    patch("l3mgr.utils.tasks.commit_svn_configuration", autospec=True, side_effect=_commit_svn_configuration),
    patch(
        "l3grafanasync.services.GrafanaApi.push_dashboard", autospec=True, return_value=PushResponse(id=1, uid="abc")
    ),
    patch("l3rtsync.utils.sync", autospec=True, side_effect=lambda l: (l, [])),
    patch.object(_deployment_task, "max_retries", 0),
    patch.object(_deployment_task, "MaxRetriesExceededError", ExpectedRetriesExceededError),
)
class ConfigurationProcessingTestCase(_BalancersPrepareMixin, RESTAPITransactionTestCase):
    DEFAULT_TIMEOUT: float = 3 * 60

    class Mocks(enum.Enum):
        fetch_balancer_info = enum.auto()
        update_config = enum.auto()
        restart_firewall = enum.auto()

    PORTS_MUTEX = threading.Lock()
    FETCH_BALANCER_INFO_PORTS = [80]
    EXCEPTIONS: typing.Dict[Mocks, Exception] = {}

    @contextlib.contextmanager
    def balancer_fetch_info(self, *ports):
        with acquire(self.PORTS_MUTEX):
            original = self.FETCH_BALANCER_INFO_PORTS[:]
            self.FETCH_BALANCER_INFO_PORTS.clear()
            self.FETCH_BALANCER_INFO_PORTS.extend(ports)
        try:
            yield
        finally:
            with acquire(self.PORTS_MUTEX):
                self.FETCH_BALANCER_INFO_PORTS.clear()
                self.FETCH_BALANCER_INFO_PORTS.extend(original)

    @contextlib.contextmanager
    def inject_exception(self, mock: Mocks, ex):
        with acquire(self.PORTS_MUTEX):
            self.EXCEPTIONS[mock] = ex
            logger.info(f">>>>>>>>>> error for {mock} injected")
        try:
            yield
        finally:
            with acquire(self.PORTS_MUTEX):
                del self.EXCEPTIONS[mock]
                logger.info(f"<<<<<<<<<< error for {mock} removed")

    def _get_balancer_host_mock_side_effect(self, fqdn):
        mock = Mock()
        mock.start_keepalived.side_effect = lambda restart=True: StartResult.SKIPPED if restart else StartResult.STARTED
        mock.stop_keepalived.return_value = StopResult.STOPPED

        regions = set(mgr_models.LoadBalancer.objects.get(fqdn=fqdn).region)

        rs_ips = set()
        if mgr_models.LocationRegion.REGION_CHOICES.MAN in regions:
            rs_ips.add("2a02:06b8:b040:3100:0ccc:0000:0000:04c9")
        if mgr_models.LocationRegion.REGION_CHOICES.MSK in regions:
            rs_ips.add("2a02:06b8:0000:1482:0000:0000:0000:0115")
            rs_ips.add("2a02:06b8:b010:0031:0000:0000:0000:0233")

        def fetch_balancer_info():
            with acquire(self.PORTS_MUTEX):
                if self.Mocks.fetch_balancer_info in self.EXCEPTIONS:
                    raise self.EXCEPTIONS[self.Mocks.fetch_balancer_info]
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

        mock.fetch_balancer_info.side_effect = fetch_balancer_info

        def update_config(content: str, pull_cvs: bool = True) -> None:
            with acquire(self.PORTS_MUTEX):
                if self.Mocks.update_config in self.EXCEPTIONS:
                    raise self.EXCEPTIONS[self.Mocks.update_config]

        mock.update_config.side_effect = update_config

        def restart_firewall() -> None:
            with acquire(self.PORTS_MUTEX):
                if self.Mocks.restart_firewall in self.EXCEPTIONS:
                    raise self.EXCEPTIONS[self.Mocks.restart_firewall]

        mock.restart_firewall.side_effect = restart_firewall

        return mock

    def setUp(self):
        self._patchers.append(
            patch("l3mgr.models.BalancerHost", autospec=True, side_effect=self._get_balancer_host_mock_side_effect)
        )

        super().setUp()
        self.api_client = APIClient()
        self.client = self.api_client

        self.waiter = MachinesWaiter(timeout=self.DEFAULT_TIMEOUT)

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

        @receiver(testing_signals.testing_tasks_status_validated, weak=False)
        def on_testing_tasks_status_validated(sender, deployment, failed, *args, **kwargs):
            logger.info(f"receive deployment#{deployment.id} testing results: {failed}")
            self.testing_tasks_status_validated_results.put((deployment, failed))

        self.balancers = self._prepare_balancers(self.client)

        self.svc = self._service_builder().build(self.client)
        self.service: mgr_models.Service = mgr_models.Service.objects.get(id=self.svc["id"])
        testing_models.AllowTestingByMachineFeature.objects.create(service_id=self.svc["id"])

        mgr_models.LoadBalancerAccess.objects.bulk_create(
            [
                mgr_models.LoadBalancerAccess(abc=self.svc["abc"], balancer=lb)
                for lb in self.balancers
                if not lb.test_env
            ]
        )
        mgr_models.AllowUsedByMachineFeature.objects.bulk_create(
            [mgr_models.AllowUsedByMachineFeature(balancer=lb) for lb in self.balancers if not lb.test_env]
        )

        agent_models.AgentSettings.objects.filter(
            load_balancer__in=[lb for lb in self.balancers if not lb.test_env]
        ).update(agent_mode=agent_models.AgentSettings.MODE_CHOICES.IDLE)

    def tearDown(self):
        try:
            super().tearDown()
        finally:
            self._patchers.pop()

    def assertStopOrRetry(self, m: models.ServiceDeploymentMachine, flow_control_exc) -> None:
        self.assertIsInstance(
            flow_control_exc,
            (states.StopException, states.RetryException),
            f"Unexpected termination for {m.id}: {m.service_id} - {m.service.fqdn}",
        )

    def assertRetry(self, m: models.ServiceDeploymentMachine, flow_control_exc) -> None:
        self.assertIsInstance(
            flow_control_exc,
            states.RetryException,
            f"Unexpected termination for {m.id}: {m.service_id} - {m.service.fqdn}",
        )

    def waiting(
        self, c, ids: typing.Union[None, typing.List[int], typing.Set[int], typing.Dict[int, MachineCheck]] = None
    ):
        if ids is None and isinstance(c, dict):
            ids = c
            c = None
        if not ids:
            ids = {m.id for m in (self.service.deployment_machine,)}
        return self.waiter.wait(ids, c)

    def assert_deploy(self, c_id: int, vs: dict) -> None:
        self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
        cfg: mgr_models.Configuration = self.assert_configuration_started()
        self.assertEquals(c_id, cfg.id)
        self.started_configurations.clear()

        cfg.refresh_from_db()
        self.assertEquals(mgr_models.Configuration.STATE_CHOICES.TESTING, cfg.state)

        balancer = self.balancers[2]
        self.assertTrue(balancer.test_env)
        task = self._send_lock_and_status(balancer, c_id, vs)

        with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
            expected_failed_regions = [R.MAN, R.MSK]
            while True:
                deployment: mgr_models.Deployment
                deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                self.assertEquals(task.deployment_id, deployment.pk)
                self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
                self.assertListEqual(expected_failed_regions, failed.regions)
                if expected_failed_regions != [R.MAN]:
                    expected_failed_regions = [R.MAN]
                elif self.testing_tasks_status_validated_results.empty():
                    break

        with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (1 + 2)):
            # we expect 3 process_deployment scheduled: 1 by test task unlock in deployment-status and 2 by release_lb
            balancer = self.balancers[3]
            self.assertTrue(balancer.test_env)
            task = self._send_lock_and_status(balancer, c_id, vs)

        deployment.refresh_from_db()
        self.assertEqual(mgr_models.Deployment.States.REACHED, deployment.state)

        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertIsNone(failed, msg=str(failed))
        self.assertEquals(task.deployment_id, deployment.pk)

        allocations: typing.List[mgr_models.Allocation] = list(deployment.allocations.all())
        for allocation in allocations:
            self.assertEqual(mgr_models.Allocation.CeleryStates.PROCESSED, allocation.celery_state)

        cfg.refresh_from_db()
        self.assertEquals(mgr_models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        vs_state: mgr_models.VirtualServerState = mgr_models.VirtualServerState.objects.get(
            balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
        )
        self.assertEquals(mgr_models.VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

    @parameterized.expand(
        [
            mgr_models.Service.Options.DsmMode.OFF,
            mgr_models.Service.Options.DsmMode.SKIP,
            mgr_models.Service.Options.DsmMode.RESPECT,
            mgr_models.Service.Options.DsmMode.PREFER,
            # mgr_models.Service.Options.DsmMode.SOLELY,
        ]
    )
    @with_worker
    @patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True))
    def test_configuration_processing_in_parallel_with_agents(self, dsm_mode: mgr_models.Service.Options.DsmMode):
        vs = self.prepare_vs({"groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"])})
        self.service.options.dsm = True
        self.service.options.dsm_mode = dsm_mode
        self.service.save()

        c = self._prepare_config(self.client, self.svc, [vs])
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)
        # lets begin testing
        with self.waiting(self.assertRetry):
            self.assert_process_config(c["id"])
        self.assert_deploy(c["id"], vs)

        while not self.testing_tasks_status_validated_results.empty():
            self.testing_tasks_status_validated_results.get_nowait()
        # second deploy
        with self.waiting(self.assertRetry):
            c_id = self._send_vs_update(self.client, self.svc, vs)
        self.assertNotEqual(c["id"], c_id)
        self.assert_deploy(c_id, vs)

    @parameterized.expand(
        [
            mgr_models.Service.Options.DsmMode.OFF,
            mgr_models.Service.Options.DsmMode.SKIP,
            mgr_models.Service.Options.DsmMode.RESPECT,
            mgr_models.Service.Options.DsmMode.PREFER,
            # mgr_models.Service.Options.DsmMode.SOLELY,
        ]
    )
    @with_worker
    @patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True))
    def test_configuration_deployed_on_sticky_only(self, dsm_mode: mgr_models.Service.Options.DsmMode):
        vs = self.prepare_vs({"groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"])})
        self.service.options.dsm = True
        self.service.options.dsm_mode = dsm_mode
        self.service.save()

        c = self._prepare_config(self.client, self.svc, [vs])
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)
        # lets begin testing
        with self.waiting(self.assertRetry):
            self.assert_process_config(c["id"])
        self.assert_deploy(c["id"], vs)

        while not self.testing_tasks_status_validated_results.empty():
            self.testing_tasks_status_validated_results.get_nowait()

        unsticky_balancers = []
        for balancer in self.balancers:
            if not balancer.test_env:
                balancer.sticky = True
                balancer.save()
                balancer = mgr_models.LoadBalancer.objects.get(id=balancer.id)
                balancer.id = None
                balancer.fqdn = f"unsticky-{balancer.fqdn}"
                unsticky_balancers.append(balancer)
        unsticky_balancers = mgr_models.LoadBalancer.objects.bulk_create(unsticky_balancers)

        removed_allocations_count, _ = mgr_models.Allocation.objects.filter(
            deployment__configuration_id=c["id"]
        ).delete()
        self.assertEqual(2, removed_allocations_count)

        # second deploy
        with self.waiting(self.assertRetry):
            c_id = self._send_vs_update(self.client, self.svc, vs)
        self.assertNotEqual(c["id"], c_id)
        self.assert_deploy(c_id, vs)

        allocations: typing.List[mgr_models.Allocation] = list(
            mgr_models.Allocation.objects.filter(deployment__configuration_id=c_id)
        )
        self.assertEqual(2, len(allocations))
        for allocation in allocations:
            self.assertTrue(allocation.balancer.sticky)
            self.assertNotIn(allocation.balancer, unsticky_balancers)

    @parameterized.expand(
        itertools.product(
            [
                mgr_models.Service.Options.DsmMode.OFF,
                mgr_models.Service.Options.DsmMode.SKIP,
                mgr_models.Service.Options.DsmMode.RESPECT,
                mgr_models.Service.Options.DsmMode.PREFER,
                # mgr_models.Service.Options.DsmMode.SOLELY,
            ],
            [
                (
                    Mocks.fetch_balancer_info,
                    mgr_models.VirtualServerState.STATE_CHOICES.INACTIVE,
                    mgr_models.Allocation.CeleryStates.PROCESSED,
                ),
                (
                    Mocks.update_config,
                    mgr_models.VirtualServerState.STATE_CHOICES.COMMITTED,
                    mgr_models.Allocation.CeleryStates.FAILED,
                ),
                (
                    Mocks.restart_firewall,
                    mgr_models.VirtualServerState.STATE_CHOICES.ANNOUNCED,
                    mgr_models.Allocation.CeleryStates.PROCESSED,
                ),
            ],
        )
    )
    @with_worker
    @override_settings(DSM_IGNORE_FAILED_CELERY_DEPLOY=True)
    @patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True))
    @cases.patching(
        patch.object(_process_lb_update_requests_task, "max_retries", 0),
        patch.object(_process_lb_update_requests_task, "MaxRetriesExceededError", ExpectedRetriesExceededError),
        patch.object(_wait_for_lb_update_request_task, "max_retries", 0),
        patch.object(_wait_for_lb_update_request_task, "MaxRetriesExceededError", ExpectedRetriesExceededError),
    )
    @patch.object(_process_lb_update_requests_task, "retry")
    def test_configuration_processing_with_failure_in_parallel_with_agents(
        self,
        dsm_mode: mgr_models.Service.Options.DsmMode,
        parameters: typing.Tuple[
            Mocks, mgr_models.VirtualServerState.STATE_CHOICES, mgr_models.Allocation.CeleryStates
        ],
        retry_mock,
    ):
        def _retry(*args, **kwargs):
            raise _process_lb_update_requests_task.MaxRetriesExceededError()

        retry_mock.side_effect = _retry

        vs = self.prepare_vs({"groups": "\n".join(["%traffic_manage", "lbkp-man-009.search.yandex.net"])})
        self.service.options.dsm = True
        self.service.options.dsm_mode = dsm_mode
        self.service.save()

        def assert_deploy(c_id: int) -> None:
            self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
            cfg: mgr_models.Configuration = self.assert_configuration_started()
            self.assertEquals(c_id, cfg.id)
            self.started_configurations.clear()

            cfg.refresh_from_db()
            self.assertEquals(mgr_models.Configuration.STATE_CHOICES.TESTING, cfg.state)

            balancer = self.balancers[2]
            self.assertTrue(balancer.test_env)
            task = self._send_lock_and_status(balancer, c_id, vs)

            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                expected_failed_regions = [R.MAN, R.MSK]
                while True:
                    deployment: mgr_models.Deployment
                    deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                    self.assertEquals(task.deployment_id, deployment.pk)
                    self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
                    self.assertListEqual(expected_failed_regions, failed.regions)
                    if expected_failed_regions != [R.MAN]:
                        expected_failed_regions = [R.MAN]
                    elif self.testing_tasks_status_validated_results.empty():
                        break

            with self.inject_exception(
                parameters[0], BalancerCommunicationException("[DON'T WORRY] Expected test exception")
            ):
                with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (1 + 2)):
                    # we expect 3 process_deployment scheduled: 1 by test task unlock in deployment-status and 2 by release_lb
                    balancer = self.balancers[3]
                    self.assertTrue(balancer.test_env)
                    task = self._send_lock_and_status(balancer, c_id, vs)

                vs_state: mgr_models.VirtualServerState = mgr_models.VirtualServerState.objects.get(
                    balancer=self.balancers[0], vs_id__in=cfg.vs_ids
                )
                self.assertEquals(
                    parameters[1],
                    vs_state.state,
                    f"Unexpected state for {vs_state}",
                )

            deployment.refresh_from_db()
            self.assertEqual(mgr_models.Deployment.States.REACHED, deployment.state)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsNone(failed, msg=str(failed))
            self.assertEquals(task.deployment_id, deployment.pk)

            allocations: typing.List[mgr_models.Allocation] = list(deployment.allocations.all())
            for allocation in allocations:
                self.assertEqual(parameters[2], allocation.celery_state)

            cfg.refresh_from_db()
            self.assertEquals(mgr_models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)

        c = self._prepare_config(self.client, self.svc, [vs])
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)
        # lets begin testing
        with self.waiting(self.assertRetry):
            self.assert_process_config(c["id"])
        assert_deploy(c["id"])

        while not self.testing_tasks_status_validated_results.empty():
            self.testing_tasks_status_validated_results.get_nowait()
        # second deploy
        with self.waiting(self.assertRetry):
            c_id = self._send_vs_update(self.client, self.svc, vs)
        self.assertNotEqual(c["id"], c_id)
        assert_deploy(c_id)

    @with_worker
    @patch("l3mgr.utils.tasks.UnexpectedConfigurationStateException.__new__")
    def test_configuration_processing_metrics_in_order_with_fsm(self, exc_init_mock):
        self.service.options.dsm = True
        self.service.options.dsm_mode = mgr_models.Service.Options.DsmMode.PREFER
        self.service.save()

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
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        unlocked_balancers_queue = Queue()

        @receiver(mgr_signals.allocations_unlocked, weak=False)
        def on_balancers_unlocked(sender, allocations: typing.List[mgr_models.Allocation], *args, **kwargs):
            processed = set()
            for allocation in allocations:
                key = allocation.balancer.id, allocation.service.id, allocation.deployment.configuration_id
                if key not in processed:
                    unlocked_balancers_queue.put(key)

        # lets begin testing
        with self.balancer_fetch_info(443):
            with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (1 + 2 + 2)):
                self.assert_process_config(c["id"])

            self.assertTrue(self.deploy_process_started_event.is_set())
            self.deploy_process_started_event.clear()

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                self.assertListEqual([R.MAN, R.MSK], failed.regions)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsNone(failed)

            cfg: mgr_models.Configuration = self.assert_configuration_started()

            required_balancers = {b.id for b in self.balancers if not b.test_env}
            self.assertTrue(required_balancers)
            while required_balancers:
                lb_id, service_id, configuration_id = unlocked_balancers_queue.get(timeout=self.DEFAULT_TIMEOUT)
                self.assertIn(lb_id, required_balancers)
                required_balancers.remove(lb_id)
                self.assertEqual(self.service.id, service_id)
                self.assertEqual(cfg.id, configuration_id)

        cfg.refresh_from_db()
        self.assertEquals(c["id"], cfg.id)
        self.assertEquals(mgr_models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        vs_state: mgr_models.VirtualServerState = mgr_models.VirtualServerState.objects.get(
            balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
        )
        self.assertEquals(mgr_models.VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

        while not self.testing_tasks_status_validated_results.empty():
            # there may be two results as there are two tasks, and in case of rase they can be not optimized
            self.testing_tasks_status_validated_results.get_nowait()

        # second deploy
        logger.info(f"[{self.id()}] second deploy")

        # with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (2 + 2)):
        c_id: int = self._send_vs_update(self.client, self.svc, vss[0])
        self.assertNotEqual(c["id"], c_id)

        self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
        cfg1 = self.assert_configuration_started(1)
        cfg, task_id = self.started_configurations[1]
        self.assertEqual(cfg1.id, cfg.id)
        r = celery.result.AsyncResult(task_id)
        r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
        state = r.state
        if state != celery.states.SUCCESS:
            self.fail(f"`process_config` task state is {state}, but SUCCESS expected: {r.result}")
        self.assertEqual(celery.states.SUCCESS, state)

        deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
        self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)

        from l3deployment.machine import run_machine

        metrics_mock = MetricsMock()
        run_machine(self.service.fqdn, metrics_mock)
        self.assertEqual(len(metrics_mock.metrics), 0)

        run_machine("xxx", metrics_mock)
        self.assertEqual(metrics_mock.metrics["service_not_found"], 1)

        with patch(
            "l3deployment.machine._tick",
            side_effect=BaseException,
            autospec=True,
            **{"return_value.side_effect": BaseException()},
        ):
            run_machine(self.service.fqdn, metrics_mock)
        self.assertEqual(metrics_mock.metrics[self.service.fqdn], 1)

        with patch(
            "l3deployment.machine._tick",
            side_effect=BaseException,
            autospec=True,
            **{"return_value.side_effect": BaseException()},
        ):
            run_machine(self.service.fqdn, metrics_mock)
        self.assertEqual(metrics_mock.metrics[self.service.fqdn], 2)

    @parameterized.expand(
        [
            mgr_models.Service.Options.DsmMode.OFF,
            mgr_models.Service.Options.DsmMode.SKIP,
            mgr_models.Service.Options.DsmMode.RESPECT,
            mgr_models.Service.Options.DsmMode.PREFER,
        ]
    )
    @with_worker
    @patch("l3mgr.utils.tasks.UnexpectedConfigurationStateException.__new__")
    def test_configuration_processing_in_order_with_fsm(
        self, dsm_mode: mgr_models.Service.Options.DsmMode, exc_init_mock
    ):
        self.service.options.dsm = True
        self.service.options.dsm_mode = dsm_mode
        self.service.save()

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
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        unlocked_balancers_queue = Queue()

        @receiver(mgr_signals.allocations_unlocked, weak=False)
        def on_balancers_unlocked(sender, allocations: typing.List[mgr_models.Allocation], *args, **kwargs):
            processed = set()
            for allocation in allocations:
                key = allocation.balancer.id, allocation.service.id, allocation.deployment.configuration_id
                if key not in processed:
                    unlocked_balancers_queue.put(key)

        # lets begin testing
        with self.balancer_fetch_info(443):
            with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (1 + 2 + 2)):
                self.assert_process_config(c["id"])

            self.assertTrue(self.deploy_process_started_event.is_set())
            self.deploy_process_started_event.clear()

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                self.assertListEqual([R.MAN, R.MSK], failed.regions)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsNone(failed)

            cfg: mgr_models.Configuration = self.assert_configuration_started()

            required_balancers = {b.id for b in self.balancers if not b.test_env}
            self.assertTrue(required_balancers)
            while required_balancers:
                lb_id, service_id, configuration_id = unlocked_balancers_queue.get(timeout=self.DEFAULT_TIMEOUT)
                self.assertIn(lb_id, required_balancers)
                required_balancers.remove(lb_id)
                self.assertEqual(self.service.id, service_id)
                self.assertEqual(cfg.id, configuration_id)

        cfg.refresh_from_db()
        self.assertEquals(c["id"], cfg.id)
        self.assertEquals(mgr_models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        vs_state: mgr_models.VirtualServerState = mgr_models.VirtualServerState.objects.get(
            balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
        )
        self.assertEquals(mgr_models.VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

        while not self.testing_tasks_status_validated_results.empty():
            # there may be two results as there are two tasks, and in case of rase they can be not optimized
            self.testing_tasks_status_validated_results.get_nowait()

        # second deploy
        logger.info(f"[{self.id()}] second deploy")

        with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (2 + 2)):
            c_id: int = self._send_vs_update(self.client, self.svc, vss[0])
            self.assertNotEqual(c["id"], c_id)

            self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
            cfg1 = self.assert_configuration_started(1)
            cfg, task_id = self.started_configurations[1]
            self.assertEqual(cfg1.id, cfg.id)
            r = celery.result.AsyncResult(task_id)
            r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
            state = r.state
            if state != celery.states.SUCCESS:
                self.fail(f"`process_config` task state is {state}, but SUCCESS expected: {r.result}")
            self.assertEqual(celery.states.SUCCESS, state)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                self.assertListEqual([R.MAN, R.MSK], failed.regions)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
            self.assertEquals(2, len(tasks))

            self.assertDictEqual(
                {
                    (mgr_models.LocationRegion.REGION_CHOICES.MSK,): testing_models.TestingTask.Results.SUCCESS,
                    (mgr_models.LocationRegion.REGION_CHOICES.MAN,): testing_models.TestingTask.Results.UNKNOWN,
                },
                {tuple(t.presentation.regions): t.result for t in tasks},
            )
            with self.balancer_fetch_info(80, 443):
                for idx in range(5):
                    self.assertEqual(cfg.id, deployment.configuration_id)
                    self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
                    self.assertListEqual([mgr_models.LocationRegion.REGION_CHOICES.MAN], failed.regions)
                    deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                    if failed is None:
                        break
                else:
                    self.fail(f"Failed to complete configuration testing in {idx} tries")

        tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
        self.assertEquals(2, len(tasks))
        self.assertSetEqual({testing_models.TestingTask.Results.SUCCESS}, {t.result for t in tasks})

    @parameterized.expand(
        [
            mgr_models.Service.Options.DsmMode.OFF,
            mgr_models.Service.Options.DsmMode.SKIP,
            mgr_models.Service.Options.DsmMode.RESPECT,
            mgr_models.Service.Options.DsmMode.PREFER,
        ]
    )
    @with_worker
    @patch("l3mgr.utils.tasks.UnexpectedConfigurationStateException.__new__")
    def test_dsm_switching_on(self, dsm_mode: mgr_models.Service.Options.DsmMode, exc_init_mock):
        mgr_models.AllowUsedByMachineFeature.objects.filter(
            balancer__in=[lb for lb in self.balancers if not lb.test_env]
        ).delete()

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
        c = self._deploy_config(self.client, c, mgr_models.Configuration.STATE_CHOICES.PREPARED)

        deploy_chains = Queue()

        @receiver(mgr_signals.configuration_deploy_chain_delayed, weak=False)
        def on_configuration_deploy_chain_delayed(sender, configuration, chain_result, *args, **kwargs):
            deploy_chains.put(chain_result)

        # lets begin testing
        with self.balancer_fetch_info(443):
            with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (1 + 2)):
                self.assert_process_config(c["id"])

            self.assertTrue(self.deploy_process_started_event.is_set())
            self.deploy_process_started_event.clear()

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                self.assertListEqual([R.MAN, R.MSK], failed.regions)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsNone(failed)

            cfg: mgr_models.Configuration = self.assert_configuration_started()

            chain_result: celery.result.ResultSet = deploy_chains.get(timeout=self.DEFAULT_TIMEOUT)
            chain_result.get(timeout=self.DEFAULT_TIMEOUT)

        cfg.refresh_from_db()
        self.assertEquals(c["id"], cfg.id)
        self.assertEquals(mgr_models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        vs_state: mgr_models.VirtualServerState = mgr_models.VirtualServerState.objects.get(
            balancer_id=self.balancers[0].id, vs_id__in=cfg.vs_ids
        )
        self.assertEquals(mgr_models.VirtualServerState.STATE_CHOICES.ANNOUNCED, vs_state.state)

        while not self.testing_tasks_status_validated_results.empty():
            # there may be two results as there are two tasks, and in case of rase they can be not optimized
            self.testing_tasks_status_validated_results.get_nowait()

        # second deploy
        logger.info(f"[{self.id()}] second deploy")
        self.service.options.dsm = True
        self.service.options.dsm_mode = dsm_mode
        self.service.save()
        mgr_models.AllowUsedByMachineFeature.objects.bulk_create(
            [mgr_models.AllowUsedByMachineFeature(balancer=lb) for lb in self.balancers if not lb.test_env]
        )

        with self.waiting(self.assertStopOrRetry, [self.service.deployment_machine.id] * (2 + 2)):
            c_id: int = self._send_vs_update(self.client, self.svc, vss[0])
            self.assertNotEqual(c["id"], c_id)

            self.assertTrue(self.deploy_process_started_event.wait(self.DEFAULT_TIMEOUT))
            cfg1 = self.assert_configuration_started(1)
            cfg, task_id = self.started_configurations[1]
            self.assertEqual(cfg1.id, cfg.id)
            r = celery.result.AsyncResult(task_id)
            r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
            state = r.state
            if state != celery.states.SUCCESS:
                self.fail(f"`process_config` task state is {state}, but SUCCESS expected: {r.result}")
            self.assertEqual(celery.states.SUCCESS, state)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
            with alias(mgr_models.LocationRegion.REGION_CHOICES) as R:
                self.assertListEqual([R.MAN, R.MSK], failed.regions)

            deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
            tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
            self.assertEquals(2, len(tasks))

            self.assertDictEqual(
                {
                    (mgr_models.LocationRegion.REGION_CHOICES.MSK,): testing_models.TestingTask.Results.SUCCESS,
                    (mgr_models.LocationRegion.REGION_CHOICES.MAN,): testing_models.TestingTask.Results.UNKNOWN,
                },
                {tuple(t.presentation.regions): t.result for t in tasks},
            )
            with self.balancer_fetch_info(80, 443):
                for idx in range(5):
                    self.assertEqual(cfg.id, deployment.configuration_id)
                    self.assertIsInstance(failed, testing_utils.PullTestingTasksResult.StillTesting)
                    self.assertListEqual([mgr_models.LocationRegion.REGION_CHOICES.MAN], failed.regions)
                    deployment, failed = self.testing_tasks_status_validated_results.get(timeout=self.DEFAULT_TIMEOUT)
                    if failed is None:
                        break
                else:
                    self.fail(f"Failed to complete configuration testing in {idx} tries")

        tasks: typing.List[testing_models.TestingTask] = list(deployment.testing_tasks.all())
        self.assertEquals(2, len(tasks))
        self.assertSetEqual({testing_models.TestingTask.Results.SUCCESS}, {t.result for t in tasks})

    def _send_lock_and_status(self, balancer: mgr_models.LoadBalancer, c_id: int, vs) -> testing_models.TestingTask:
        task = self._send_lock_task(balancer, c_id)
        self._send_deployment_status(balancer, task, vs)
        return task

    def _send_lock_task(self, balancer: mgr_models.LoadBalancer, c_id: int) -> testing_models.TestingTask:
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

    def _send_deployment_status(self, balancer: mgr_models.LoadBalancer, task: testing_models.TestingTask, vs):
        url = "/api/v1/agent/{agent_id}/tasks/{task_id}/deployment-status"
        response = self.api_client.put(
            url.format(agent_id=balancer.fqdn, task_id=task.pk),
            {
                "id": task.pk,
                "ts": time.time(),
                "error": {"message": None, "code": 200},
                "overall_deployment_status": "SUCCESS",
                "vss": [
                    {"id": vs["id"], "status": "UP", "rss": [{"id": rs_id, "status": "SUCCESS"} for rs_id in vs["rs"]]}
                ],
            },
            format="json",
        )
        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task.refresh_from_db()
        self.assertEquals(testing_models.TestingTask.Results.SUCCESS, task.result)
        return response

    def assert_process_config(self, configuration_id: int) -> None:
        r = mgr_tasks.process_config.delay(configuration_id)
        r.get(timeout=self.DEFAULT_TIMEOUT)
        state = r.state
        self.assertEqual(celery.states.SUCCESS, state)

    def assert_configuration_started(self, started_configurations_idx: int = 0) -> mgr_models.Configuration:
        cfg, task_id = self.started_configurations[started_configurations_idx]
        r = celery.result.AsyncResult(task_id)
        r.get(timeout=self.DEFAULT_TIMEOUT, propagate=False)
        state = r.state
        self.assertEqual(
            celery.states.SUCCESS,
            state,
            msg=f"`process_config` task state is {state}, but SUCCESS expected: {r.result}",
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


@contextlib.contextmanager
def acquire(mutex):
    try:
        mutex.acquire()
        yield
    finally:
        mutex.release()
