import datetime as dt
import itertools
import typing
from typing import Optional

from django.test import override_settings
from django.utils import timezone
from parameterized import parameterized

from l3mgr import models as mgr_models
from l3mgr.tests import test_fields
from l3mgr.tests.base import RESTAPITest
from l3mgr.utils import process_groups, prepare_svc_networks
from .. import models, utils


class TaskRetryTestCase(RESTAPITest):
    def setUp(self):
        super().setUp()
        svc = mgr_models.Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        models.AllowTestingByMachineFeature.objects.create(service=svc)

        prepare_svc_networks(svc)
        mgr_models.LocationNetwork.objects.bulk_create(
            mgr_models.LocationNetwork(
                ip=ip,
                location=[mgr_models.LocationNetwork.LOCATION_CHOICES.MAN],
                source=mgr_models.LocationNetwork.SOURCE_CHOICES.RACKTABLES,
            )
            for ip in ["2a02:6b8:b040:3100::/56", "77.88.1.0/24", "93.158.0.0/16"]
        )

        self.lb = mgr_models.LoadBalancer.objects.create(
            fqdn="man1-lb2b.yndx.net",
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.MAN],
        )
        self.testing_lb = mgr_models.LoadBalancer.objects.create(
            fqdn="sas1-test-2lb3b.yndx.net",
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            test_env=True,
            location=[mgr_models.LocationNetwork.LOCATION_CHOICES.MAN],
        )

        groups = ["%traffic_manage", "lbkp-man-009.search.yandex.net"]
        rs_ids = process_groups.process_groups(groups)

        self.testing_tasks: typing.List[typing.Tuple[int, models.TestingTask]] = []
        for idx in range(3):
            vip = mgr_models.VirtualServer.objects.create(
                service=svc,
                ip="2a02:6b8:0:3400:ffff::4c9",
                port=80 + idx,
                protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
                lb_ids=[self.lb.pk],
                rs_ids=list(rs_ids),
                groups=groups,
                config=test_fields.make_config(URL="/check", STATUS_CODE=200),
            )

            configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
                service=svc,
                vs_ids=[vip.pk],
                description="test",
                state=mgr_models.Configuration.STATE_CHOICES.TEST_PENDING,
            )
            configuration.create_presentations()

            deployment = mgr_models.Deployment.objects.create(configuration=configuration)
            tasks = utils.create_testing_tasks(deployment)
            self.assertEqual(1, len(tasks))

            self.testing_tasks.append((configuration.id, tasks[0]))

    def assert_lock_task(
        self, expected_id: int, locked_by: typing.Optional[mgr_models.LoadBalancer] = None
    ) -> models.TestingTask:
        if not locked_by:
            locked_by = self.testing_lb
        locked_task: Optional[models.TestingTask] = utils.lock_task(locked_by=locked_by, max_tries=1)
        self.assertIsNotNone(locked_task)
        self.assertEqual(expected_id, locked_task.id)
        return locked_task

    @parameterized.expand(
        [
            (utils.StopTimeoutNoFeedbackState.NO_BALANCER, False, False, False),
            (utils.StopTimeoutNoFeedbackState.NO_BALANCER, False, False, True),
            (utils.StopTimeoutNoFeedbackState.NO_BALANCER, False, True, False),
            (utils.StopTimeoutNoFeedbackState.NO_BALANCER, False, True, True),
            (utils.StopTimeoutNoFeedbackState.NO_AGENT_OR_FSM_CONFIGURED, True, False, False),
            (utils.StopTimeoutNoFeedbackState.FROM_FSM, True, False, True),
            (utils.StopTimeoutNoFeedbackState.FROM_AGENT, True, True, False),
            (utils.StopTimeoutNoFeedbackState.AGENT_AND_FSM_CONFLICT, True, True, True),
        ]
    )
    def test_check_retry(
        self,
        expected_state: utils.StopTimeoutNoFeedbackState,
        is_locked: bool,
        is_agent_active: bool,
        is_fsm_enabled: bool,
    ):
        if is_fsm_enabled:
            models.BalancerTestingMachine.objects.create(balancer=self.testing_lb)

        tasks = self.testing_tasks

        age_timedelta: dt.timedelta = dt.timedelta(minutes=3)

        latest_task = tasks[-1][1]

        if is_locked:
            latest_task = self.assert_lock_task(latest_task.id)

        models.TestingTask.objects.filter(id=latest_task.id).update(
            updated_at=timezone.now() - age_timedelta - dt.timedelta(minutes=1)
        )

        if is_locked:
            from l3agent import models as agent_models

            agent_settings: agent_models.AgentSettings = agent_models.AgentSettings.objects.filter(
                load_balancer=latest_task.balancer
            ).first()
            agent_settings.agent_mode = (
                agent_models.AgentSettings.MODE_CHOICES.ACTIVE
                if is_agent_active
                else agent_models.AgentSettings.MODE_CHOICES.IDLE
            )
            agent_settings.save(update_fields=("agent_mode",))

        latest_stopped_tasks_ids = utils.stop_timeout_testing_tasks(age_timedelta)
        self.assertEqual(1, len(latest_stopped_tasks_ids))
        self.assertIn(latest_task.id, latest_stopped_tasks_ids.keys())
        latest_task.refresh_from_db()
        self.assertEqual(
            models.TestingTask.Results.UNKNOWN
            if is_locked and (is_agent_active or not is_fsm_enabled)
            else models.TestingTask.Results.OVERDUE,
            latest_task.result,
        )

        self.assertIn(expected_state, latest_stopped_tasks_ids.values())


class LockingTaskMixin:
    def assert_task_locked(self, expected_id: int, locked_by: typing.Optional[mgr_models.LoadBalancer]):
        locked_task: Optional[models.TestingTask] = utils.lock_task(locked_by=locked_by, max_tries=1)
        self.assertIsNotNone(locked_task)
        self.assertEqual(expected_id, locked_task.id)
        return locked_task


class TaskLockingTestCase(RESTAPITest, LockingTaskMixin):
    def setUp(self):
        super().setUp()
        svc = mgr_models.Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        models.AllowTestingByMachineFeature.objects.create(service=svc)

        prepare_svc_networks(svc)
        mgr_models.LocationNetwork.objects.bulk_create(
            mgr_models.LocationNetwork(
                ip=ip,
                location=["MAN"],
                source=mgr_models.LocationNetwork.SOURCE_CHOICES.RACKTABLES,
            )
            for ip in ["2a02:6b8:b040:3100::/56", "77.88.1.0/24", "93.158.0.0/16"]
        )
        self.lb = mgr_models.LoadBalancer.objects.create(
            fqdn="man1-lb2b.yndx.net",
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=["MAN"],
        )
        self.testing_lb = mgr_models.LoadBalancer.objects.create(
            fqdn="sas1-test-2lb3b.yndx.net",
            state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
            test_env=True,
            location=["MAN"],
        )

        groups = ["%traffic_manage", "lbkp-man-009.search.yandex.net"]
        rs_ids = process_groups.process_groups(groups)

        self.testing_tasks: typing.List[typing.Tuple[int, models.TestingTask]] = []
        for idx in range(3):
            vip = mgr_models.VirtualServer.objects.create(
                service=svc,
                ip="2a02:6b8:0:3400:ffff::4c9",
                port=80 + idx,
                protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
                lb_ids=[self.lb.pk],
                rs_ids=list(rs_ids),
                groups=groups,
                config=test_fields.make_config(URL="/check", STATUS_CODE=200),
            )

            configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
                service=svc,
                vs_ids=[vip.pk],
                description="test",
                state=mgr_models.Configuration.STATE_CHOICES.TEST_PENDING,
            )
            configuration.create_presentations()

            deployment = mgr_models.Deployment.objects.create(configuration=configuration)
            tasks = utils.create_testing_tasks(deployment)
            self.assertEqual(1, len(tasks))

            self.testing_tasks.append((configuration.id, tasks[0]))

    def assert_lock_task(
        self, expected_id: int, locked_by: typing.Optional[mgr_models.LoadBalancer] = None
    ) -> models.TestingTask:
        if not locked_by:
            locked_by = self.testing_lb
        return self.assert_task_locked(expected_id, locked_by)

    def test_several_services_prefer_older_deploy(self):
        latest_configuration_id, latest_task = self.testing_tasks[-1]

        svc = mgr_models.Service.objects.create(fqdn="lbk-l3mgr.yandex.net", abc="dostavkatraffika")
        models.AllowTestingByMachineFeature.objects.create(service=svc)

        prepare_svc_networks(svc)

        groups = ["lbkp-man-009.search.yandex.net"]
        rs_ids = process_groups.process_groups(groups)

        vip = mgr_models.VirtualServer.objects.create(
            service=svc,
            ip="2a02:6b8:0:3400:ffff::4cA",
            port=8181,
            protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
            lb_ids=[self.lb.pk],
            rs_ids=list(rs_ids),
            groups=groups,
            config=test_fields.make_config(URL="/check", STATUS_CODE=200),
        )

        configuration: mgr_models.Configuration = mgr_models.Configuration.objects.create(
            service=svc,
            vs_ids=[vip.pk],
            description="test-second-service-config",
            state=mgr_models.Configuration.STATE_CHOICES.TEST_PENDING,
        )
        configuration.create_presentations()

        deployment = mgr_models.Deployment.objects.create(configuration=configuration)
        tasks = utils.create_testing_tasks(deployment)
        self.assertEqual(1, len(tasks))

        locked_task = self.assert_lock_task(latest_task.id)
        utils.unlock_task(locked_task, self.testing_lb, models.TestingTask.Results.SUCCESS)

        self.assert_lock_task(tasks[0].id)

    def test_task_lock_latest_only(self):
        latest_configuration_id, latest_task = self.testing_tasks[-1]

        locked_task = self.assert_lock_task(latest_task.id)
        utils.unlock_task(locked_task, self.testing_lb, models.TestingTask.Results.SUCCESS)

        result = mgr_models.Configuration.objects.filter(pk=latest_configuration_id).update(
            state=mgr_models.Configuration.STATE_CHOICES.ACTIVE
        )
        self.assertEqual(1, result)

        locked_task = utils.lock_task(locked_by=self.testing_lb, max_tries=1)
        self.assertIsNone(locked_task)

    def test_lock_redeployed(self):
        previous_configuration_id, previous_task = self.testing_tasks[1]
        deployment = mgr_models.Deployment.objects.create(configuration_id=previous_configuration_id)
        tasks = utils.create_testing_tasks(deployment)
        self.assertEqual(1, len(tasks))
        latest_task = tasks[0]
        self.assertNotEqual(previous_task.id, latest_task.id)

        locked_task = self.assert_lock_task(latest_task.id)
        utils.unlock_task(locked_task, self.testing_lb, models.TestingTask.Results.SUCCESS)

        locked_task = utils.lock_task(locked_by=self.testing_lb, max_tries=1)
        self.assertIsNone(locked_task)

    @override_settings(TESTING_TASKS_RETRIES_LIMIT=1)
    def test_stop_timeout_tasks(self):
        tasks = self.testing_tasks

        stopped_tasks_ids: typing.Dict[int, utils.StopTimeoutNoFeedbackState] = utils.stop_timeout_testing_tasks()
        self.assertFalse(stopped_tasks_ids)

        age_timedelta: dt.timedelta = dt.timedelta(minutes=3)

        task = tasks[0][1]
        task.refresh_from_db()
        models.TestingTask.objects.filter(id=task.id).update(
            updated_at=timezone.now() - age_timedelta - dt.timedelta(minutes=1)
        )

        stopped_tasks_ids = utils.stop_timeout_testing_tasks(age_timedelta)
        self.assertEqual(1, len(stopped_tasks_ids))
        self.assertIn(task.id, stopped_tasks_ids)
        self.assertIn(utils.StopTimeoutNoFeedbackState.NO_BALANCER, stopped_tasks_ids.values())

        latest_task = tasks[-1][1]
        locked_task = self.assert_lock_task(latest_task.id)
        models.TestingTask.objects.filter(id=locked_task.id).update(
            updated_at=timezone.now() - age_timedelta - dt.timedelta(minutes=1)
        )

        latest_stopped_tasks_ids: typing.Dict[int, utils.StopTimeoutNoFeedbackState]
        latest_stopped_tasks_ids = utils.stop_timeout_testing_tasks(age_timedelta)
        self.assertEqual(1, len(latest_stopped_tasks_ids))
        self.assertIn(locked_task.id, latest_stopped_tasks_ids)
        self.assertIn(utils.StopTimeoutNoFeedbackState.NO_BALANCER, stopped_tasks_ids.values())
        locked_task.refresh_from_db()
        self.assertEqual(models.TestingTask.Results.UNKNOWN, locked_task.result)
        self.assertEqual(1, locked_task.retries)

        stopped_tasks_ids = utils.stop_timeout_testing_tasks(age_timedelta)
        self.assertFalse(stopped_tasks_ids)

        testing_lb = self.testing_lb
        testing_lb.pk = None
        testing_lb.fqdn = ("copy-sas1-test-2lb3b.yndx.net",)
        testing_lb.save()
        more_locked_task = self.assert_lock_task(locked_task.id, locked_by=testing_lb)
        self.assertEqual(locked_task.id, more_locked_task.id)
        models.TestingTask.objects.filter(id=more_locked_task.id).update(
            updated_at=timezone.now() - age_timedelta - dt.timedelta(minutes=1)
        )

        stopped_tasks_ids = utils.stop_timeout_testing_tasks(age_timedelta)
        self.assertEqual(1, len(stopped_tasks_ids))
        self.assertIn(more_locked_task.id, stopped_tasks_ids)
        self.assertIn(utils.StopTimeoutNoFeedbackState.NO_AGENT_OR_FSM_CONFIGURED, stopped_tasks_ids.values())

        more_locked_task.refresh_from_db()
        self.assertEqual(models.TestingTask.Results.FAILED, more_locked_task.result)
        self.assertEqual(2, more_locked_task.retries)


class TaskCreationTestCase(RESTAPITest):
    def setUp(self) -> None:
        super().setUp()
        self.svc = mgr_models.Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")

    def prepare_data(
        self,
        required_locations: typing.Iterable[typing.Union[str, typing.List[str], typing.Set[str], typing.Tuple[str]]],
        vs_config: typing.Optional[
            typing.Dict[str, typing.Union[bool, str, int, typing.List[typing.Union[bool, str, int]]]]
        ] = None,
    ) -> None:
        locations = [
            location if isinstance(location, (list, set, tuple)) else [location] for location in required_locations
        ]
        ips = zip(itertools.cycle(locations), ["2a02:6b8:b040:3100::/56", "77.88.1.0/24", "93.158.0.0/16"])

        mgr_models.LocationNetwork.objects.bulk_create(
            mgr_models.LocationNetwork(
                ip=ip,
                location=location,
                source=mgr_models.LocationNetwork.SOURCE_CHOICES.RACKTABLES,
            )
            for location, ip in ips
        )
        groups = ["%traffic_manage", "lbkp-man-009.search.yandex.net"]
        rs_ids = process_groups.process_groups(groups)

        self.lbs = mgr_models.LoadBalancer.objects.bulk_create(
            mgr_models.LoadBalancer(
                fqdn=f"{'-'.join(location).lower()}.yndx.net",
                state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
                location=location,
            )
            for location in locations
        )

        vs_config = vs_config or {}
        vip = mgr_models.VirtualServer.objects.create(
            service=self.svc,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port=80,
            protocol=mgr_models.VirtualServer.PROTOCOL_CHOICES.TCP,
            lb_ids=[lb.pk for lb in self.lbs],
            rs_ids=list(rs_ids),
            groups=groups,
            config=test_fields.make_config(URL="/check", STATUS_CODE=200, **vs_config),
        )

        self.configuration = mgr_models.Configuration.objects.create(
            service=self.svc,
            vs_ids=[vip.pk],
            description="test",
            state=mgr_models.Configuration.STATE_CHOICES.TEST_PENDING,
        )

        self.deployment = mgr_models.Deployment.objects.create(configuration=self.configuration)
        self.configuration.create_presentations()

    def assert_tasks(
        self,
        tasks: typing.List[models.TestingTask],
        expected_len: int,
        expected_results: typing.Set[str],
        expected_regions: typing.Optional[typing.Set[str]] = None,
        expected_locations: typing.Optional[typing.Set[str]] = None,
    ) -> None:
        self.assertEqual(expected_len, len(tasks))
        self.assertSetEqual(expected_results, {t.result for t in tasks})
        self.assertSetEqual({self.deployment.id}, {t.deployment_id for t in tasks})
        self.assertSetEqual({self.deployment.configuration_id}, {t.configuration_id for t in tasks})
        if expected_locations is not None:
            self.assertSetEqual(expected_locations, set(itertools.chain(*[t.presentation.locations for t in tasks])))
            self.assertFalse(set(itertools.chain(*[t.presentation.regions for t in tasks])))
        if expected_regions is not None:
            self.assertFalse(set(itertools.chain(*[t.presentation.locations for t in tasks])))
            self.assertSetEqual(expected_regions, set(itertools.chain(*[t.presentation.regions for t in tasks])))

    def test_single_region(self) -> None:
        self.prepare_data({mgr_models.LocationNetwork.LOCATION_CHOICES.MAN})
        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(
            tasks,
            1,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationRegion.REGION_CHOICES.MAN},
        )

    def test_same_region(self) -> None:
        self.prepare_data(
            {mgr_models.LocationNetwork.LOCATION_CHOICES.MYT, mgr_models.LocationNetwork.LOCATION_CHOICES.SAS}
        )
        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(
            tasks,
            1,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationRegion.REGION_CHOICES.MSK},
        )

    def test_several_region(self) -> None:
        self.prepare_data(
            {mgr_models.LocationNetwork.LOCATION_CHOICES.MAN, mgr_models.LocationNetwork.LOCATION_CHOICES.VLA}
        )
        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(
            tasks,
            2,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationNetwork.LOCATION_CHOICES.MAN, mgr_models.LocationRegion.REGION_CHOICES.VLA},
        )

    def test_sub_locations_from_region(self) -> None:
        msk = mgr_models.LocationRegion.objects.get(code=mgr_models.LocationRegion.REGION_CHOICES.MSK)
        self.assertLess(1, len(msk.location))
        man = mgr_models.LocationRegion.objects.get(code=mgr_models.LocationRegion.REGION_CHOICES.MAN)

        self.prepare_data(
            [
                msk.location[:2],
                man.location,
            ]
        )
        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(
            tasks,
            2,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationRegion.REGION_CHOICES.MAN, mgr_models.LocationRegion.REGION_CHOICES.MSK},
        )

    def test_with_dc_filter_on(self) -> None:
        self.prepare_data(
            {
                mgr_models.LocationNetwork.LOCATION_CHOICES.MYT,
                mgr_models.LocationNetwork.LOCATION_CHOICES.SAS,
                mgr_models.LocationNetwork.LOCATION_CHOICES.VLA,
            },
            {"DC_FILTER": True},
        )
        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assertEqual(3, len(tasks))
        self.assert_tasks(
            tasks,
            3,
            {models.TestingTask.Results.UNKNOWN},
            expected_locations={
                mgr_models.LocationNetwork.LOCATION_CHOICES.MYT,
                mgr_models.LocationNetwork.LOCATION_CHOICES.SAS,
                mgr_models.LocationNetwork.LOCATION_CHOICES.VLA,
            },
        )

    def test_with_specified_test_balancer(self) -> None:
        location = [mgr_models.LocationNetwork.LOCATION_CHOICES.MAN]
        testing_lbs: typing.List[mgr_models.LoadBalancer] = mgr_models.LoadBalancer.objects.bulk_create(
            [
                mgr_models.LoadBalancer(
                    fqdn=f"{'-'.join(location).lower()}-testenv.yndx.net",
                    state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
                    test_env=True,
                    location=location,
                )
            ]
        )

        self.prepare_data(
            {mgr_models.LocationNetwork.LOCATION_CHOICES.MAN, mgr_models.LocationNetwork.LOCATION_CHOICES.VLA},
            {"TESTING_LBS": [lb.id for lb in testing_lbs]},
        )

        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assertEqual(2, len(tasks))
        self.assert_tasks(
            tasks,
            2,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationRegion.REGION_CHOICES.MAN, mgr_models.LocationRegion.REGION_CHOICES.VLA},
        )

        self.assertSetEqual(
            {
                (testing_lbs[0].id, (mgr_models.LocationNetwork.LOCATION_CHOICES.MAN,)),
                (None, (mgr_models.LocationNetwork.LOCATION_CHOICES.VLA,)),
            },
            {(t.balancer_id, tuple(t.presentation.regions)) for t in tasks},
        )

    def test_with_specified_test_balancer_with_multiply_locations(self) -> None:
        msk = mgr_models.LocationRegion.objects.get(code=mgr_models.LocationRegion.REGION_CHOICES.MSK)
        self.assertLess(1, len(msk.location))
        man = mgr_models.LocationRegion.objects.get(code=mgr_models.LocationRegion.REGION_CHOICES.MAN)

        location = msk.location
        testing_lbs = mgr_models.LoadBalancer.objects.bulk_create(
            [
                mgr_models.LoadBalancer(
                    fqdn=f"{'-'.join(location).lower()}-testenv.yndx.net",
                    state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
                    test_env=True,
                    location=location,
                )
            ]
        )
        self.prepare_data(
            [
                msk.location[:2],
                man.location,
            ],
            {"TESTING_LBS": [lb.id for lb in testing_lbs]},
        )

        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(
            tasks,
            2,
            {models.TestingTask.Results.UNKNOWN},
            {mgr_models.LocationRegion.REGION_CHOICES.MAN, mgr_models.LocationRegion.REGION_CHOICES.MSK},
        )

        self.assertSetEqual(
            {
                (testing_lbs[0].id, (msk.code,)),
                (None, (mgr_models.LocationNetwork.LOCATION_CHOICES.MAN,)),
            },
            {(t.balancer_id, tuple(t.presentation.regions)) for t in tasks},
        )

    def test_lock_retried(self) -> None:
        region = mgr_models.LocationRegion.REGION_CHOICES.MAN
        self.prepare_data({region})
        models.AllowTestingByMachineFeature.objects.create(service=self.svc)

        tasks = utils.create_testing_tasks(deployment=self.deployment)
        self.assert_tasks(tasks, 1, {models.TestingTask.Results.UNKNOWN}, {region})

        location = mgr_models.LocationRegion.objects.get(code=region).location
        testing_lbs: typing.List[mgr_models.LoadBalancer] = mgr_models.LoadBalancer.objects.bulk_create(
            [
                mgr_models.LoadBalancer(
                    fqdn="first-testenv.yndx.net",
                    state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
                    test_env=True,
                    location=location,
                ),
                mgr_models.LoadBalancer(
                    fqdn="second-testenv.yndx.net",
                    state=mgr_models.LoadBalancer.STATE_CHOICES.ACTIVE,
                    test_env=True,
                    location=location,
                ),
            ]
        )

        locked_task = utils.lock_task(locked_by=testing_lbs[0], max_tries=1)
        self.assertIsNotNone(locked_task)
        self.assertEqual(tasks[0].id, locked_task.id)
        self.assertEqual(testing_lbs[0].id, locked_task.balancer_id)
        self.assertEqual(0, locked_task.retries)
        utils.unlock_task_for_retry(locked_task, testing_lbs[0], "[testing]", 123)

        task = utils.lock_task(locked_by=testing_lbs[0], max_tries=1)
        self.assertIsNone(task)
        task = utils.lock_task(locked_by=testing_lbs[1], max_tries=1)
        self.assertIsNotNone(task)
        self.assertEqual(tasks[0].id, task.id)
        self.assertEqual(1, task.retries)
        self.assertEqual(models.TestingTask.Results.UNKNOWN, task.result)
        self.assertEqual(testing_lbs[1].id, task.balancer_id)
