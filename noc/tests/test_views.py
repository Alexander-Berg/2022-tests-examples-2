import datetime
import itertools
import json
import sys
import time
import typing
from datetime import timedelta
from unittest.mock import patch, Mock

from django import conf
from django.conf import settings
from django.core import cache
from django.http.response import HttpResponse
from django.test import override_settings
from django.utils import timezone
from parameterized import parameterized
from rest_framework import response as drf_response
from rest_framework import status
from rest_framework import test
from rest_framework.utils.serializer_helpers import ReturnList

from l3common.tests import cases
from l3common.tests.cases import verbose_queries
from l3mgr import models
from l3mgr.utils import tasks as tasks_utils
from l3mgr.tests import test_fields
from l3testing import models as testing_models, utils as testing_utils
from . import configuration_response
from .. import models as agent_models, serializers


def _prepare_load_balancer(fqdn: str, **kwargs) -> models.LoadBalancer:
    region: str = kwargs.pop("region", None)
    if region:
        locations = models.LocationRegion.objects.get(code=region).location
        kwargs.setdefault("location", []).extend(locations)
    obj, created = models.LoadBalancer.objects.get_or_create(
        defaults=dict(state=models.LoadBalancer.STATE_CHOICES.ACTIVE, **kwargs),
        fqdn=fqdn,
    )
    return obj


def _prepare_service(**kwargs) -> models.Service:
    defaults = dict(abc="dostavkatraffika", fqdn="l3.tt.yandex-team.ru")
    defaults.update(kwargs)

    obj, created = models.Service.objects.get_or_create(defaults=defaults, fqdn=defaults["fqdn"])
    return obj


def _prepare_agent_settings(agent_id: str, agent_version: str, **kwargs) -> agent_models.AgentSettings:
    lb = _prepare_load_balancer(agent_id)
    settings = lb.agent_settings
    settings.agent_version = agent_version
    for k, v in kwargs.items():
        setattr(settings, k, v)
    settings.save()
    return settings


def _prepare_configuration(service, lbs, **kwargs) -> models.Configuration:
    kwargs = kwargs.copy()
    if "vs_ids" not in kwargs:
        rss = [
            models.RealServer(
                fqdn="mnt-myt.yandex.net",
                ip="2a02:6b8:0:1482::115",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.VLA],
            ),
            models.RealServer(
                fqdn="mnt-myt.yandex.net",
                ip="77.88.1.115",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.VLA],
            ),
            models.RealServer(
                fqdn="mnt-sas.yandex.net",
                ip="2a02:6b8:b010:31::233",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.VLA],
            ),
            models.RealServer(
                fqdn="mnt-sas.yandex.net",
                ip="93.158.158.87",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.VLA],
            ),
        ]
        models.RealServer.objects.bulk_create(rss)

        vips = [
            models.VirtualServer.objects.create(
                service=service,
                ip="2a02:6b8:0:3400:ffff::4c9",
                port="3663",
                protocol="TCP",
                lb_ids=[lb.pk for lb in lbs],
                rs_ids=[rs.id for rs in rss],
                config=test_fields.make_config(URL="/api/v1/clusters", STATUS_CODE="200"),
            )
        ]

        kwargs["vs_ids"] = [vip.pk for vip in vips]
    if "state" not in kwargs:
        kwargs["state"] = models.Configuration.STATE_CHOICES.TESTING

    configuration: models.Configuration = models.Configuration.objects.create(service=service, **kwargs)
    presentations = configuration.create_presentations()
    if not presentations:
        raise AssertionError(f"No presentations generated for configuration: {configuration}")
    return configuration


def _prepare_testing_tasks(
    configuration: models.Configuration, region: typing.Optional[models.LocationRegion.REGION_CHOICES] = None
) -> typing.List[testing_models.TestingTask]:
    deployment: models.Deployment = models.Deployment.objects.create(configuration=configuration)
    tasks = testing_utils.create_testing_tasks(deployment)
    if not tasks:
        raise AssertionError("No testing task created")

    if region:
        for t in tasks:
            if t.presentation.regions != [region]:
                raise AssertionError(
                    f"Unexpected testing tasks' locations: Expected {region}; Actual {t.presentation.regions}"
                )
    return tasks


def _prepare_data(
    custom_vs_config: typing.Optional[dict] = None,
) -> (
    models.Service,
    typing.List[models.LoadBalancer],
    typing.List[models.VirtualServer],
    typing.List[models.RealServer],
    models.Configuration,
):
    if custom_vs_config is None:
        custom_vs_config = {}

    service = _prepare_service()

    lbs = [
        _prepare_load_balancer("sas1-2lb3b.yndx.net", location=[models.LocationNetwork.LOCATION_CHOICES.SAS]),
        _prepare_load_balancer("myt-lb0.yndx.net", location=[models.LocationNetwork.LOCATION_CHOICES.MYT]),
        _prepare_load_balancer("vlx-lb1a.yndx.net", location=[models.LocationNetwork.LOCATION_CHOICES.VLX]),
    ]

    rs_config = {"WEIGHT": 1}
    rss = [
        models.RealServer(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            config=rs_config,
            location=[models.LocationNetwork.LOCATION_CHOICES.MYT],
        ),
        models.RealServer(
            fqdn="mnt-myt.yandex.net",
            ip="77.88.1.115",
            config=rs_config,
            location=[models.LocationNetwork.LOCATION_CHOICES.MYT],
        ),
        models.RealServer(
            fqdn="mnt-sas.yandex.net",
            ip="2a02:6b8:b010:31::233",
            config=rs_config,
            location=[models.LocationNetwork.LOCATION_CHOICES.SAS],
        ),
        models.RealServer(
            fqdn="mnt-sas.yandex.net",
            ip="93.158.158.87",
            config=rs_config,
            location=[models.LocationNetwork.LOCATION_CHOICES.SAS],
        ),
        models.RealServer(
            fqdn="vlx-kvm-lb0b.yndx.net",
            ip="2a02:6b8:0:b00::b3b",
            config=rs_config,
            location=[models.LocationNetwork.LOCATION_CHOICES.VLX],
        ),
    ]
    models.RealServer.objects.bulk_create(rss)

    vs_base_config = {
        **test_fields.BASE_CONFIG,
        **custom_vs_config,
    }

    from l3common import utils as common_utils

    def make_vs(ip, port, proto, rs_ids, **config_kwargs):
        return models.VirtualServer(
            ext_id=common_utils.get_network_settings_hash(ip, port, proto),
            ip=ip,
            port=port,
            protocol=proto,
            config=dict(vs_base_config, CONNECT_IP=ip, CONNECT_PORT=port, **config_kwargs),
            lb_ids=[lb.pk for lb in lbs],
            rs_ids=rs_ids,
            service=service,
        )

    # previous vss contain only 80 port
    previous_vss = [
        make_vs(
            "2a02:6b8:0:3400::50",
            80,
            models.VirtualServer.PROTOCOL_CHOICES.TCP,
            [rss[0].pk, rss[2].pk],
            HOST="l3.tt.yandex-team.ru",
        ),
        make_vs(
            "5.255.240.50",
            80,
            models.VirtualServer.PROTOCOL_CHOICES.TCP,
            [rss[1].pk, rss[3].pk],
            HOST="l3.tt.yandex-team.ru",
        ),
    ]
    models.VirtualServer.objects.bulk_create(previous_vss)

    # partically alive service: IPv6 addr is alive and IPv4 is not announced
    previous_vss_state = [
        models.VirtualServerState(
            balancer=lbs[0], vs=previous_vss[0], state=models.VirtualServerState.STATE_CHOICES.ANNOUNCED
        ),
        models.VirtualServerState(
            balancer=lbs[0], vs=previous_vss[1], state=models.VirtualServerState.STATE_CHOICES.ACTIVE
        ),
    ]
    models.VirtualServerState.objects.bulk_create(previous_vss_state)

    vss = [
        make_vs("2a02:6b8:0:3400::50", 443, models.VirtualServer.PROTOCOL_CHOICES.TCP, [rss[0].pk, rss[2].pk]),
        make_vs(
            "2a02:6b8:0:3400::50",
            80,
            models.VirtualServer.PROTOCOL_CHOICES.TCP,
            [rss[0].pk, rss[2].pk],
            HOST="l3.tt.yandex-team.ru",
        ),
        make_vs("5.255.240.50", 443, models.VirtualServer.PROTOCOL_CHOICES.TCP, [rss[1].pk, rss[3].pk]),
        make_vs(
            "5.255.240.50",
            80,
            models.VirtualServer.PROTOCOL_CHOICES.TCP,
            [rss[1].pk, rss[3].pk],
            HOST="l3.tt.yandex-team.ru",
        ),
        make_vs("2a02:6b8:0:3400::5050", 443, models.VirtualServer.PROTOCOL_CHOICES.TCP, [rss[4].pk]),
    ]
    models.VirtualServer.objects.bulk_create(vss)

    configuration = _prepare_configuration(service=service, lbs=lbs, vs_ids=[vs.pk for vs in vss])
    testing_models.AllowTestingByMachineFeature.objects.create(service=configuration.service)
    return service, lbs, vss, rss, configuration


@cases.patching(
    patch("l3mgr.utils.get_ip", Mock(return_value="127.0.0.1")),
    patch("l3mgr.utils.resolve_by_type", Mock(return_value=[])),
    patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True)),
)
class TasksTestCase(test.APITestCase):
    client: test.APIClient

    def test_task_list(self) -> None:
        url = "/api/v1/agent/{agent_id}/tasks"

        def request(agent_id, **kwargs):
            response: HttpResponse = self.client.get(url.format(agent_id=agent_id), kwargs)
            self.assertEqual(200, response.status_code)
            return json.loads(response.content.decode())

        service = _prepare_service()
        testing_models.AllowTestingByMachineFeature.objects.create(service=service)

        lb = _prepare_load_balancer("myt-lb0.yndx.net", location=[models.LocationNetwork.LOCATION_CHOICES.MYT])
        models.LoadBalancerAccess.objects.create(abc=service.abc, balancer=lb)
        testing_lb = _prepare_load_balancer(
            "vla1-test-2lb1a.yndx.net",
            location=[
                models.LocationNetwork.LOCATION_CHOICES.MYT,
                models.LocationNetwork.LOCATION_CHOICES.SAS,
                models.LocationNetwork.LOCATION_CHOICES.IVA,
            ],
            test_env=True,
        )

        rss = [
            models.RealServer(
                fqdn="mnt-myt.yandex.net",
                ip="2a02:6b8:0:1482::115",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.SAS],
            ),
            models.RealServer(
                fqdn="mnt-myt.yandex.net",
                ip="77.88.1.115",
                config={},
                location=[models.LocationNetwork.LOCATION_CHOICES.MYT],
            ),
        ]
        models.RealServer.objects.bulk_create(rss)

        vss = [
            models.VirtualServer.objects.create(
                service=service,
                ip="2a02:6b8:0:3400:ffff::4c9",
                port="3663",
                protocol="TCP",
                rs_ids=[rs.id for rs in rss],
                config=test_fields.make_config(URL="/api/v1/clusters", STATUS_CODE="200"),
            )
        ]

        tasks_by_lb = {
            testing_lb.fqdn: (
                _prepare_testing_tasks(
                    _prepare_configuration(service, [], description="1th-testing", vs_ids=[vs.id for vs in vss]),
                    models.LocationRegion.REGION_CHOICES.MSK,
                )
                + _prepare_testing_tasks(
                    _prepare_configuration(service, [], description="2nd-testing", vs_ids=[vs.id for vs in vss]),
                    models.LocationRegion.REGION_CHOICES.MSK,
                )
            ),
        }

        for agent_id, tasks in tasks_by_lb.items():
            locked_task = testing_utils.lock_task(testing_lb, max_tries=1)
            self.assertIsNotNone(locked_task)

            reference = serializers.TaskSerializer([locked_task], many=True).data
            response_data = request(agent_id)
            self.assertEqual(reference, response_data)
            response_data = request(agent_id, view="full")
            self.assertEqual(reference, response_data)

            reference = serializers.TaskShortSerializer([locked_task], many=True).data
            response_data = request(agent_id, view="short")
            self.assertEqual(reference, response_data)

    def test_task_current(self) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()
        testing_lb = _prepare_load_balancer("sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True)
        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertEqual(2, len(testing_tasks))
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)

        response: HttpResponse = self.client.post(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/current", {"id": testing_lb.fqdn, "generator_version": "v1.0"}
        )
        self.assertIsInstance(response, drf_response.Response)

        self.assertEqual(200, response.status_code, response.content.decode("utf8"))

        task = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )
        self.assertIsNotNone(task.lock)
        serializer_data = serializers.TaskSerializer([task], many=True).data
        response_data = response.data
        self.assertListEqual(serializer_data, response_data)

    @parameterized.expand(
        (
            (100, 100, 100, False),
            (300, 100, 300, False),
            ("nodisable", 100, "nodisable", False),
            (100, 300, 300, False),
            (300, 300, 300, False),
            ("nodisable", 300, "nodisable", False),
            (100, "nodisable", "nodisable", False),
            (300, "nodisable", "nodisable", False),
            ("nodisable", "nodisable", "nodisable", False),
            (100, 100, 100, True),
            (300, 100, 100, True),
            ("nodisable", 100, 100, True),
            (100, 300, 100, True),
            (300, 300, 100, True),
            ("nodisable", 100, 100, True),
            (100, "nodisable", 100, True),
            (300, "nodisable", 100, True),
            ("nodisable", "nodisable", 100, True),
        )
    )
    def test_multy_regional_lb(self, weight_MSK, weight_VLA, expected_weight, got_value) -> None:
        required_locations = list(
            itertools.chain.from_iterable(
                models.LocationRegion.objects.filter(
                    code__in=[models.LocationRegion.REGION_CHOICES.MSK, models.LocationRegion.REGION_CHOICES.VLA]
                ).values_list("location", flat=True)
            )
        )

        testing_lb = _prepare_load_balancer(
            "sas1-test-2lb3b.yndx.net",
            location=required_locations,
            test_env=True,
        )
        service, lbs, vss, rss, configuration = _prepare_data(
            {
                "WEIGHT_DC_MSK": weight_MSK,
                "WEIGHT_DC_VLA": weight_VLA,
                "TESTING_LBS": [testing_lb.id] if got_value else None,
                f"WEIGHT_LB{testing_lb.id}": 100 if got_value else None,
            }
        )
        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)

        response: HttpResponse = self.client.post(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/current", {"id": testing_lb.fqdn, "generator_version": "v1.0"}
        )
        self.assertIsInstance(response, drf_response.Response)

        for vs in response.data[0]["data"]["vss"]:
            self.assertEqual(expected_weight, vs["config"]["weight"])

        self.assertEqual(200, response.status_code, response.content.decode("utf8"))

        task = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )
        self.assertIsNotNone(task.lock)
        self.assertListEqual(serializers.TaskSerializer([task], many=True).data, response.data)

    @parameterized.expand(
        (
            (100,),
            (300,),
            ("nodisable",),
        )
    )
    def test_custom_weight(self, weight) -> None:
        service, lbs, vss, rss, configuration = _prepare_data({"WEIGHT_DC_MSK": weight})
        testing_lb: models.LoadBalancer = _prepare_load_balancer(
            "sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True
        )
        for testing_lb, vs_response_data in self.parametrized_test_task_current_with_dc_filter(
            service, lbs, vss, configuration, testing_lb
        ):
            self.assertEqual(weight, vs_response_data["config"]["weight"])
            rss_response_data = vs_response_data["rss"]
            self.assertIsInstance(rss_response_data, list)
            self.assertEqual(2, len(rss_response_data))

            vs: models.VirtualServer = models.VirtualServer.objects.get(pk=vs_response_data["id"])
            self.assertSetEqual(set(vs.rs_ids), {d["server_id"] for d in rss_response_data})

    def test_task_current_with_dc_filter(self) -> None:
        service, lbs, vss, rss, configuration = _prepare_data({"DC_FILTER": True})
        testing_lb: models.LoadBalancer = _prepare_load_balancer(
            "sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True
        )
        for testing_lb, vs_response_data in self.parametrized_test_task_current_with_dc_filter(
            service, lbs, vss, configuration, testing_lb
        ):
            vs: models.VirtualServer = models.VirtualServer.objects.get(pk=vs_response_data["id"])

            rss = models.RealServer.objects.filter(id__in=vs.rs_ids)
            expected_rss_ids = {rs.id for rs in rss if set(rs.location).issubset(testing_lb.location)}
            self.assertEqual(1, len(expected_rss_ids))

            self.assertTrue(vs_response_data["config"]["dc_filter"])
            rss_response_data = vs_response_data["rss"]
            self.assertIsInstance(rss_response_data, list)
            self.assertEqual(1, len(rss_response_data))
            rs_response_data = rss_response_data[0]
            self.assertIn(rs_response_data["server_id"], expected_rss_ids)

        tasks: typing.List[testing_models.TestingTask] = list(configuration.testing_tasks.all())
        self.assertEqual(3, len(tasks))

        first_task: testing_models.TestingTask
        second_task: testing_models.TestingTask
        third_task: testing_models.TestingTask
        first_task, second_task, third_task = sorted(
            tasks, key=lambda t: sys.maxsize if t.balancer_id is None else t.balancer_id
        )

        self.assertEqual(first_task.balancer_id, testing_lb.id)
        self.assertIsNotNone(first_task.lock)
        self.assertEqual(
            0,
            len(first_task.presentation.regions),
            f"Not empty regions for dc_filter: {first_task.presentation.regions}",
        )
        self.assertListEqual(first_task.presentation.locations, testing_lb.location)

        for t in (second_task, third_task):
            self.assertIsNone(t.lock)
            self.assertIsNone(t.balancer_id)
            self.assertNotEqual(t.id, first_task.id)
            self.assertEqual(
                0,
                len(t.presentation.regions),
                f"Not empty regions for dc_filter: {t.presentation.regions}",
            )
            self.assertFalse(set(t.presentation.locations).issubset(testing_lb.location))

    def parametrized_test_task_current_with_dc_filter(self, service, lbs, vss, configuration, testing_lb):
        testing_tasks: typing.List[testing_models.TestingTask] = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)

        response: HttpResponse = self.client.post(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/current", {"id": testing_lb.fqdn, "generator_version": "v1.0"}
        )
        self.assertIsInstance(response, drf_response.Response)

        self.assertEqual(200, response.status_code, response.content.decode("utf8"))
        response_data: ReturnList = response.data
        self.assertIsInstance(response_data, list)
        self.assertEqual(1, len(response_data))
        self.assertEqual(locked_task.id, response_data[0]["id"])
        self.assertEqual("test", response_data[0]["task"])
        response_data: dict = response_data[0]["data"]
        self.assertIsInstance(response_data, dict)
        self.assertEqual(configuration.id, response_data["id"])

        self.assertEqual(service.id, response_data["service"]["id"])
        self.assertEqual(service.fqdn, response_data["service"]["fqdn"])
        self.assertEqual(service.abc, response_data["service"]["name"])

        self.assertEqual(testing_lb.id, response_data["lb"]["id"])
        self.assertEqual(testing_lb.fqdn, response_data["lb"]["fqdn"])

        vss_response_data: list = response_data["vss"]
        self.assertIsInstance(vss_response_data, list)
        self.assertEqual(4, len(vss_response_data))
        for vs_response_data in vss_response_data:
            self.assertIn(vs_response_data["id"], [vs.id for vs in vss])
            yield testing_lb, vs_response_data

    @override_settings(PERSIST_TESTING_TASK_FEEDBACK_STATE=True)
    def test_task_deployment_status(self) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()

        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        testing_lb = _prepare_load_balancer("sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True)
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)
        task = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )

        response: HttpResponse = self.client.put(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/{task.pk}/deployment-status",
            {
                "id": task.pk,
                "ts": time.time(),
                "error": {"message": None, "code": 200},
                "overall_deployment_status": "SUCCESS",
                "vss": [
                    {
                        "id": vss[0].pk,
                        "status": "UP",
                        "rss": [
                            {"id": rss[0].pk, "status": "SUCCESS"},
                            {"id": rss[2].pk, "status": "SUCCESS"},
                        ],
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task = testing_models.TestingTask.objects.get(pk=task.pk)
        self.assertIsNone(task.lock)
        self.assertEqual(testing_models.TestingTask.Results.SUCCESS, task.result)

        self.assertEqual(
            models.VirtualServerState.STATE_CHOICES.ANNOUNCED,
            models.VirtualServerState.objects.get(balancer=testing_lb, vs=vss[0]).state,
        )
        self.assertEqual(
            models.RealServerState.STATE_CHOICES.ACTIVE,
            models.RealServerState.objects.get(balancer=testing_lb, vs=vss[0], server=rss[0]).state,
        )
        self.assertEqual(
            models.RealServerState.STATE_CHOICES.ACTIVE,
            models.RealServerState.objects.get(balancer=testing_lb, vs=vss[0], server=rss[2]).state,
        )

    @patch("l3agent.tasks.log_tshoot_info", return_value="")
    @override_settings(PERSIST_TESTING_TASK_FEEDBACK_STATE=True)
    def test_task_deployment_status_error(self, mocked_log_tshoot_info) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()

        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        testing_lb = _prepare_load_balancer("sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True)
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)
        self.assertEqual(0, locked_task.retries)
        self.assertEqual(testing_lb.id, locked_task.balancer_id)
        task: testing_models.TestingTask = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )
        self.assertEqual(locked_task.id, task.id)

        response: HttpResponse = self.client.put(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/{task.pk}/deployment-status",
            {
                "id": task.pk,
                "ts": time.time(),
                "error": {"message": "Wait keepalived failure", "code": 400},
                "overall_deployment_status": "FAILURE",
                "vss": [],
            },
            format="json",
        )

        mocked_log_tshoot_info.delay.assert_called_once_with(configuration.id, testing_lb.id, testing_lb.fqdn, task.id)
        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task = testing_models.TestingTask.objects.get(pk=task.pk)
        self.assertIsNone(task.lock)
        self.assertEqual(testing_models.TestingTask.Results.UNKNOWN, task.result)
        self.assertIsNone(task.balancer)
        self.assertEqual(1, task.retries)

    @override_settings(PERSIST_TESTING_TASK_FEEDBACK_STATE=True)
    def test_repeatable_send_task_deployment_status(self) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()

        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        testing_lb = _prepare_load_balancer("sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True)
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)
        task: testing_models.TestingTask = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )

        def send_deployment_status() -> HttpResponse:
            return self.client.put(
                f"/api/v1/agent/{testing_lb.fqdn}/tasks/{task.pk}/deployment-status",
                {
                    "id": task.pk,
                    "ts": time.time(),
                    "error": {"message": None, "code": 200},
                    "overall_deployment_status": "SUCCESS",
                    "vss": [
                        {
                            "id": vss[0].pk,
                            "status": "UP",
                            "rss": [
                                {"id": rss[0].pk, "status": "SUCCESS"},
                                {"id": rss[2].pk, "status": "SUCCESS"},
                            ],
                        }
                    ],
                },
                format="json",
            )

        response: HttpResponse = send_deployment_status()
        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task.refresh_from_db()
        self.assertIsNone(task.lock)
        self.assertEqual(testing_models.TestingTask.Results.SUCCESS, task.result)

        response: HttpResponse = send_deployment_status()
        self.assertEqual(409, response.status_code, response.content.decode("utf8"))

        # check task was not changed
        task.refresh_from_db()
        self.assertIsNone(task.lock)
        self.assertEqual(testing_models.TestingTask.Results.SUCCESS, task.result)

    @override_settings(PERSIST_TESTING_TASK_FEEDBACK_STATE=True)
    def test_receive_unexpected_task_deployment_status(self) -> None:
        def send_deployment_status(lb_fqdn: str, task_id: int = 0) -> HttpResponse:
            return self.client.put(
                f"/api/v1/agent/{lb_fqdn}/tasks/{task_id}/deployment-status",
                {
                    "id": task_id,
                    "ts": time.time(),
                    "error": {"message": None, "code": 200},
                    "overall_deployment_status": "SUCCESS",
                    "vss": [
                        {
                            "id": vss[0].pk,
                            "status": "UP",
                            "rss": [
                                {"id": rss[0].pk, "status": "SUCCESS"},
                                {"id": rss[2].pk, "status": "SUCCESS"},
                            ],
                        }
                    ],
                },
                format="json",
            )

        service, lbs, vss, rss, configuration = _prepare_data()

        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        testing_lb_a = _prepare_load_balancer("sas1-test-2lb3a.yndx.net", location=lbs[0].location, test_env=True)
        testing_lb_b = _prepare_load_balancer("sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True)

        response: HttpResponse = send_deployment_status(testing_lb_b.fqdn)
        self.assertEqual(404, response.status_code, response.content.decode("utf8"))

        task: testing_models.TestingTask = configuration.testing_tasks.get(
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK]
        )

        response: HttpResponse = send_deployment_status(testing_lb_b.fqdn, task.pk)
        self.assertEqual(409, response.status_code, response.content.decode("utf8"))

        testing_utils.lock_task(testing_lb_a)

        response: HttpResponse = send_deployment_status(testing_lb_b.fqdn, task.pk)
        self.assertEqual(409, response.status_code, response.content.decode("utf8"))

        # check task was not changed
        task.refresh_from_db()
        self.assertIsNotNone(task.lock)
        self.assertEqual(testing_models.TestingTask.Results.UNKNOWN, task.result)

    @parameterized.expand(
        (
            # IPv6 previous state is announced,
            # this test already returns failure state and recv failure task result.
            # Looks like ANNOUNCE service previous state enable strict mode.
            ((0,), (1, 2, 3, 4), testing_models.TestingTask.Results.FAILED),
            # incorrect status len return UNKNOWN state too
            ((0,), (1,), testing_models.TestingTask.Results.FAILED),
            # IPv4 previous state is not announced;
            # this test already returns failure state, but its ignored based on announce state.
            ((2,), (0, 1, 3, 4), testing_models.TestingTask.Results.SUCCESS),
        )
    )
    @patch("l3agent.tasks.log_tshoot_info", return_value="")
    @override_settings(PERSIST_TESTING_TASK_FEEDBACK_STATE=True)
    def test_task_deployment_partically_status(
        self, failed_vs_ids, successful_vs_ids, expected_task_status, mocked_log_tshoot_info
    ) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()

        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))
        testing_lb: models.LoadBalancer = _prepare_load_balancer(
            "sas1-test-2lb3b.yndx.net", location=lbs[0].location, test_env=True
        )
        locked_task: typing.Optional[testing_models.TestingTask] = testing_utils.lock_task(testing_lb)
        self.assertIsNotNone(locked_task)
        self.assertEqual(configuration.pk, locked_task.configuration.pk)
        task: testing_models.TestingTask = configuration.testing_tasks.get(
            balancer=testing_lb,
            locations__len=0,
            presentation__locations__len=0,
            presentation__regions=[models.LocationRegion.REGION_CHOICES.MSK],
        )

        response: HttpResponse = self.client.put(
            f"/api/v1/agent/{testing_lb.fqdn}/tasks/{task.pk}/deployment-status",
            {
                "id": task.pk,
                "ts": time.time(),
                "error": {"message": None, "code": 300},
                "overall_deployment_status": "FAILURE",
                "vss": [
                    # generate expanded list of failed statuses
                    *[
                        {
                            "id": vss[failed_vs].pk,
                            "status": "DOWN",
                            "rss": [],
                        }
                        for failed_vs in failed_vs_ids
                    ],
                    # generate expanded list of successful statuses
                    *[
                        {
                            "id": vss[successful_vs_id].pk,
                            "status": "UP",
                            "rss": [
                                {"id": rss[0].pk, "status": "SUCCESS"},
                                {"id": rss[2].pk, "status": "SUCCESS"},
                            ],
                        }
                        for successful_vs_id in successful_vs_ids
                    ],
                ],
            },
            format="json",
        )

        mocked_log_tshoot_info.delay.assert_called_once_with(configuration.id, testing_lb.id, testing_lb.fqdn, task.id)
        self.assertEqual(204, response.status_code, response.content.decode("utf8"))
        task.refresh_from_db()
        self.assertIsNone(task.lock)
        self.assertEqual(expected_task_status, task.result)


@cases.patching(
    patch("l3mgr.utils.get_ip", Mock(return_value="127.0.0.1")),
    patch("l3mgr.utils.resolve_by_type", Mock(return_value=[])),
    patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True)),
)
class DeploymentTestCase(test.APITestCase):
    client: test.APIClient

    def setUp(self) -> None:
        service, lbs, vss, rss, configuration = _prepare_data()
        testing_tasks = _prepare_testing_tasks(configuration)
        self.assertNotEqual(0, len(testing_tasks))

        service.options.dsm_mode = models.Service.Options.DsmMode.SOLELY
        service.save()

        self.allocation: models.Allocation = models.Allocation.objects.create(
            service=service,
            deployment=testing_tasks[0].deployment,
            balancer=lbs[0],
            round=0,
            presentation=configuration.presentations.filter(balancers__contains=[lbs[0].pk]).get(),
            state=models.Allocation.States.UNKNOWN,
            target=models.Allocation.Targets.ACTIVE,
            locked_at=None,
        )
        self.lbs: typing.List[models.LoadBalancer] = lbs
        self.vss: typing.List[models.VirtualServer] = vss
        self.rss: typing.List[models.RealServer] = rss

    @property
    def config_id(self) -> int:
        return typing.cast(int, self.allocation.presentation.configuration_id)

    def test_schema(self):
        response: drf_response.Response = self.client.get(f"/api/v1/agent/schema/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("application/vnd.oai.openapi", response.accepted_media_type)
        print(response.content.decode("utf8"))
        # todo: add some expected assertions

    def test_configs_list(self):
        response: drf_response.Response = self.client.get(f"/api/v1/agent/{self.lbs[0].fqdn}/configs")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertListEqual(
            [
                {
                    "revision": self.allocation.id,
                    "id": self.config_id,
                    "target": "ACTIVE",
                    "locked": None,
                    "state": "UNKNOWN",
                    "service": "l3.tt.yandex-team.ru",
                }
            ],
            response.data,
        )

    def test_configs_retrieve(self):
        response: drf_response.Response = self.client.get(f"/api/v1/agent/{self.lbs[0].fqdn}/configs/{self.config_id}")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content.decode())
        data = json.loads(response.content)
        self.maxDiff = None
        self.assertDictEqual(configuration_response.get_expected(self.allocation), data)

    def test_configs_list_with_ids_filtering(self):
        response: drf_response.Response = self.client.get(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs?ids={self.config_id}"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @parameterized.expand(
        [
            (
                models.Allocation.Targets.REMOVED,
                models.Allocation.States.REMOVED,
                models.VirtualServerState.STATE_CHOICES.DISABLED,
            ),
            (
                models.Allocation.Targets.ACTIVE,
                models.Allocation.States.DEPLOYED,
                models.VirtualServerState.STATE_CHOICES.ANNOUNCED,
            ),
        ]
    )
    def test_lock_and_unlock_through_success_deployment_status(
        self,
        target: models.Allocation.Targets,
        expected_state: models.Allocation.States,
        expected_vs_state: models.VirtualServerState.STATE_CHOICES,
    ):
        self.allocation.target = target
        self.allocation.save()

        self.assertIsNone(self.allocation.locked_at)
        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/{self.config_id}/lock"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content.decode())
        self.allocation.refresh_from_db()
        self.assertIsNotNone(self.allocation.locked_at)

        vs_state: models.VirtualServerState = models.VirtualServerState.objects.create(
            balancer=self.lbs[0], vs=self.vss[0], state=models.VirtualServerState.STATE_CHOICES.UNKNOWN
        )

        with verbose_queries(detailed=True):
            response: drf_response.Response = self.client.post(
                f"/api/v1/agent/{self.lbs[0].fqdn}/configs/{self.config_id}/deployment-status",
                data=json.dumps(
                    {
                        "id": self.config_id,
                        "overall_deployment_status": "SUCCESS",
                        "vs_status": {"FAILED": [], "DEPLOYED": [], "ANNOUNCED": [self.vss[0].id]},
                        "ts": timezone.now().timestamp(),
                        "error": {"message": None, "code": 200},
                    }
                ),
                content_type="application/json",
            )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content.decode("utf8"))
        self.allocation.refresh_from_db()
        self.assertIsNone(self.allocation.locked_at)
        self.assertEqual(expected_state, self.allocation.state)
        vs_state.refresh_from_db()
        self.assertEqual(expected_vs_state, vs_state.state)

    @parameterized.expand(
        [
            (
                models.Allocation.Targets.REMOVED,
                models.Allocation.States.REMOVED,
                models.VirtualServerState.STATE_CHOICES.DISABLED,
            ),
            (
                models.Allocation.Targets.ACTIVE,
                models.Allocation.States.DEPLOYED,
                models.VirtualServerState.STATE_CHOICES.ANNOUNCED,
            ),
        ]
    )
    def test_bulk_lock_and_unlock_through_success_deployment_status(
        self,
        target: models.Allocation.Targets,
        expected_state: models.Allocation.States,
        expected_vs_state: models.VirtualServerState.STATE_CHOICES,
    ):
        self.allocation.target = target
        self.allocation.save()

        self.assertIsNone(self.allocation.locked_at)
        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/lock?ids={self.config_id}"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual({"locked": [self.config_id]}, response.json())
        self.allocation.refresh_from_db()
        self.assertIsNotNone(self.allocation.locked_at)

        vs_state: models.VirtualServerState = models.VirtualServerState.objects.create(
            balancer=self.lbs[0], vs=self.vss[0], state=models.VirtualServerState.STATE_CHOICES.UNKNOWN
        )

        with verbose_queries(detailed=True):
            response: drf_response.Response = self.client.post(
                f"/api/v1/agent/{self.lbs[0].fqdn}/configs/deployment-status?ids={self.config_id}",
                data=json.dumps(
                    {
                        "overall_deployment_status": "SUCCESS",
                        "vs_status": {"FAILED": [], "DEPLOYED": [], "ANNOUNCED": [self.vss[0].id]},
                        "ts": timezone.now().timestamp(),
                        "error": {"message": None, "code": 200},
                    }
                ),
                content_type="application/json",
            )
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content.decode("utf8"))
        self.assertDictEqual({"unlocked": [self.config_id]}, response.json())
        self.allocation.refresh_from_db()
        self.assertIsNone(self.allocation.locked_at)
        self.assertEqual(expected_state, self.allocation.state)
        vs_state.refresh_from_db()
        self.assertEqual(expected_vs_state, vs_state.state)

    @parameterized.expand([models.Allocation.Targets.REMOVED, models.Allocation.Targets.ACTIVE])
    def test_lock_and_unlock_through_deployment_status_with_error(self, target: models.Allocation.Targets):
        self.allocation.target = target
        self.allocation.save()

        self.assertIsNone(self.allocation.locked_at)
        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/{self.config_id}/lock"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content.decode())
        self.allocation.refresh_from_db()
        self.assertIsNotNone(self.allocation.locked_at)

        vs_state: models.VirtualServerState = models.VirtualServerState.objects.create(
            balancer=self.lbs[0], vs=self.vss[0], state=models.VirtualServerState.STATE_CHOICES.UNKNOWN
        )

        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/{self.config_id}/deployment-status",
            data=json.dumps(
                {
                    "id": self.config_id,
                    "overall_deployment_status": "SUCCESS",
                    "vs_status": {"FAILED": [], "DEPLOYED": [], "ANNOUNCED": [self.vss[0].id]},
                    "ts": timezone.now().timestamp(),
                    "error": {"message": "UnknownError", "code": 599},
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content.decode("utf8"))
        self.allocation.refresh_from_db()
        self.assertIsNone(self.allocation.locked_at)
        self.assertEqual(models.Allocation.States.FAILED, self.allocation.state)
        vs_state.refresh_from_db()
        self.assertEqual(models.VirtualServerState.STATE_CHOICES.UNKNOWN, vs_state.state)

    @parameterized.expand([models.Allocation.Targets.REMOVED, models.Allocation.Targets.ACTIVE])
    def test_bulk_lock_and_unlock_through_deployment_status_with_error(self, target: models.Allocation.Targets):
        self.allocation.target = target
        self.allocation.save()

        self.assertIsNone(self.allocation.locked_at)
        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/lock?ids={self.config_id}"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertDictEqual({"locked": [self.config_id]}, response.json())
        self.allocation.refresh_from_db()
        self.assertIsNotNone(self.allocation.locked_at)

        vs_state: models.VirtualServerState = models.VirtualServerState.objects.create(
            balancer=self.lbs[0], vs=self.vss[0], state=models.VirtualServerState.STATE_CHOICES.UNKNOWN
        )

        response: drf_response.Response = self.client.post(
            f"/api/v1/agent/{self.lbs[0].fqdn}/configs/deployment-status?ids={self.config_id}",
            data=json.dumps(
                {
                    "overall_deployment_status": "SUCCESS",
                    "vs_status": {"FAILED": [], "DEPLOYED": [], "ANNOUNCED": [self.vss[0].id]},
                    "ts": timezone.now().timestamp(),
                    "error": {"message": "UnknownError", "code": 599},
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content.decode("utf8"))
        self.assertDictEqual({"unlocked": [self.config_id]}, response.json())
        self.allocation.refresh_from_db()
        self.assertIsNone(self.allocation.locked_at)
        self.assertEqual(models.Allocation.States.FAILED, self.allocation.state)
        vs_state.refresh_from_db()
        self.assertEqual(models.VirtualServerState.STATE_CHOICES.UNKNOWN, vs_state.state)

    @override_settings(
        CACHES={
            cache.DEFAULT_CACHE_ALIAS: {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
            settings.STATES_CACHE: {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        },
    )
    def test_report_status(self) -> None:
        timestamp: datetime.datetime = timezone.now() + datetime.timedelta(hours=10)
        from l3common.tests.cases import verbose_queries

        vs_states: typing.List[models.VirtualServerState] = list(models.VirtualServerState.objects.all())
        self.assertEqual(len(vs_states), 2)

        rs_states: typing.List[models.RealServerState] = models.RealServerState.objects.bulk_create(
            [
                models.RealServerState(
                    balancer=self.lbs[0],
                    vs=vs_state.vs,
                    server=rs,
                    fwmark=fwmark,
                )
                for idx, vs_state in enumerate(vs_states)
                for fwmark, rs in enumerate(vs_state.vs.servers, start=1000 * idx + 1)
            ]
        )

        active_vs_state: models.VirtualServerState = vs_states[0]
        disabled_vs_state: models.VirtualServerState = vs_states[1]
        with verbose_queries(detailed=True):
            response: drf_response.Response = self.client.post(
                f"/api/v1/agent/{self.lbs[0].fqdn}/report/status",
                data=json.dumps(
                    {
                        "vss": [
                            {
                                "status": "DEPLOYED",
                                "ip": active_vs_state.vs.ip,
                                "port": active_vs_state.vs.port,
                                "protocol": "TCP",
                                "rss": [
                                    "2a02:6b8:c0c:4c05:0:409a:aef4:2006",
                                    "2a02:6b8:c0c:4c05:0:409a:aef4:2007",
                                ],
                            },
                            {
                                "status": "ANNOUNCED",
                                "ip": active_vs_state.vs.ip,
                                "port": active_vs_state.vs.port,
                                "protocol": active_vs_state.vs.protocol,
                                "rss": [
                                    "2a02:6b8:0:1482::115",
                                ]
                                + [rs.ip for rs in active_vs_state.vs.servers],
                            },
                        ],
                        "ts": timestamp.timestamp(),
                        "error": {"message": "You will be OK", "code": 200},
                    }
                ),
                content_type="application/json",
            )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        tasks_utils.fetch_and_persist(self.lbs[0], Mock(), False)

        vs_states: typing.List[models.VirtualServerState] = list(self.lbs[0].vss.all())
        self.assertDictEqual(
            {
                active_vs_state.vs.ip: models.VirtualServerState.STATE_CHOICES.ANNOUNCED,
                disabled_vs_state.vs.ip: models.VirtualServerState.STATE_CHOICES.DISABLED,
            },
            {st.vs.ip: st.state for st in vs_states},
        )
        self.assertSetEqual({timestamp}, {st.timestamp for st in vs_states})

        for rs_state in rs_states:
            rs_state.refresh_from_db()
            if rs_state.server.id in active_vs_state.vs.rs_ids:
                self.assertEqual(models.RealServerState.STATE_CHOICES.ACTIVE, rs_state.state)
            elif rs_state.server.id in disabled_vs_state.vs.rs_ids:
                self.assertEqual(models.RealServerState.STATE_CHOICES.INACTIVE, rs_state.state)
            else:
                self.fail("Unexpected real server state")

        self.assertSetEqual({timestamp}, set(models.RealServerState.objects.values_list("timestamp", flat=True)))

    def test_ip_port_absence_parameters_status(self) -> None:
        timestamp: datetime.datetime = timezone.now() + datetime.timedelta(seconds=10)
        vs_states: typing.List[models.VirtualServerState] = list(models.VirtualServerState.objects.all())
        self.assertEqual(len(vs_states), 2)

        active_vs_state: models.VirtualServerState = vs_states[0]
        with verbose_queries(detailed=True):
            response: drf_response.Response = self.client.post(
                f"/api/v1/agent/{self.lbs[0].fqdn}/report/status",
                data=json.dumps(
                    {
                        "vss": [
                            {
                                "status": "DEPLOYED",
                                "protocol": "TCP",
                                "port": active_vs_state.vs.port,
                                "rss": [
                                    "2a02:6b8:c0c:4c05:0:409a:aef4:2006",
                                    "2a02:6b8:c0c:4c05:0:409a:aef4:2007",
                                ],
                            },
                            {
                                "status": "ANNOUNCED",
                                "ip": active_vs_state.vs.ip,
                                "protocol": active_vs_state.vs.protocol,
                                "rss": [
                                    "2a02:6b8:0:1482::115",
                                ]
                                + [rs.ip for rs in active_vs_state.vs.servers],
                            },
                            {
                                "status": "ANNOUNCED",
                                "ip": active_vs_state.vs.ip,
                                "port": active_vs_state.vs.port,
                                "protocol": "fwmark",
                                "rss": ["2a02:6b8:0:1482::115"],
                            },
                        ],
                        "ts": timestamp.timestamp(),
                        "error": {"message": "You will be OK", "code": 200},
                    }
                ),
                content_type="application/json",
            )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        vs_responses = response.json()["data"]["vss"]

        self.assertEqual(len(vs_responses), 3, "There should be 3 errors.")

        for vs_response in vs_responses:
            if "non_field_errors" in vs_response:
                self.assertIn(
                    "Required `ip`+`port` or `fwmark`", vs_response["non_field_errors"], "ip, port error not fired"
                )
            if "protocol" in vs_response:
                self.assertIn('"fwmark" is not a valid choice.', vs_response["protocol"], "protocol error not fired")


@cases.patching(
    patch("l3agent.auth.TVMServicePermission.has_permission", Mock(return_value=True)),
)
class AgentTestCase(test.APITestCase):
    def test_service_settings(self) -> None:
        def check_data(data_list) -> None:
            for agent_id, agent_version, values in data_list:
                response: HttpResponse = self.client.get(
                    f"/api/v1/agent/{agent_id}/settings", {"agent-version": agent_version}, format="json"
                )
                self.assertIsInstance(response, drf_response.Response)
                if values is None:
                    self.assertEqual(404, response.status_code)
                    self.assertEqual("error", response.data["status"])
                else:
                    self.assertEqual(200, response.status_code)
                    self.assertEqual(int(values["polling_interval"].total_seconds()), response.data["polling_interval"])
                    self.assertEqual(conf.settings.L3_HOSTS_POOL, response.data["l3_hosts_pool"])
                    for key in "agent_mode", "generator_version":
                        self.assertEqual(values[key], response.data[key])

        data: typing.List[typing.Tuple[str, str, typing.Optional[dict]]] = [
            (f"fqdn{i}", f"v{i}", None) for i in range(3)
        ]
        check_data(data)

        new_data = [
            ("one", "ver", {"polling_interval": timedelta(seconds=3324), "agent_mode": "IDLE", "generator_version": 1}),
            (
                "two",
                "ver",
                {"polling_interval": timedelta(days=999999999), "agent_mode": "ACTIVE", "generator_version": 1},
            ),
        ]
        for agent_id, agent_version, values in new_data:
            _prepare_agent_settings(agent_id, agent_version, **values)
        data.extend(new_data)
        check_data(data)

    def test_service_status(self) -> None:
        data = [
            (
                {
                    "id": "t-322",
                    "changed_at": 1594642473,
                    "current": "IDLE",
                    "counters": {
                        "IDLE": 1234,
                        "WAITING": 2345,
                        "ACTIVE": 3456,
                        "LB_UPDATED": 4567,
                        "RESTORE": 5678,
                        "ROLLBACK": 6789,
                        "ROLLBACK_LB_UPDATED": 7890,
                        "RESTORE_ON_ROLLBACK": 890,
                        "FAILURE": 90,
                    },
                },
                None,
            ),
            (
                {
                    "id": "t-322",
                    "changed_at": 1599992473,
                    "current": "ACTIVE",
                    "counters": {
                        "IDLE": 1234,
                        "WAITING": 2345,
                        "ACTIVE": 3456,
                        "LB_UPDATED": 4567,
                        "RESTORE": 5678,
                        "ROLLBACK": 6789,
                        "ROLLBACK_LB_UPDATED": 7890,
                        "RESTORE_ON_ROLLBACK": 890,
                        "FAILURE": 90,
                    },
                },
                None,
            ),
            (
                {
                    "id": "t-322",
                    "changed_at": 1594642473,
                    "current": "IDLE",
                    "counters": {
                        "IDLE": 1234,
                        "WAITING": 2345,
                        "RESTORE": 5678,
                        "ROLLBACK": 6789,
                        "ROLLBACK_LB_UPDATED": 7890,
                        "RESTORE_ON_ROLLBACK": 890,
                        "FAILURE": 90,
                    },
                },
                400,
            ),
            (
                {
                    "id": "t-322",
                    "changed_at": 1594642473,
                    "current": "INVALID_VALUE",
                    "counters": {
                        "IDLE": 1234,
                        "WAITING": 2345,
                        "ACTIVE": 3443,
                        "RESTORE": 5678,
                        "ROLLBACK": 6789,
                        "ROLLBACK_LB_UPDATED": 7890,
                        "RESTORE_ON_ROLLBACK": 890,
                        "FAILURE": 90,
                    },
                },
                400,
            ),
            (
                {
                    "id": "unknown_agent",
                    "changed_at": 1594642473,
                    "current": "IDLE",
                    "counters": {
                        "IDLE": 1234,
                        "WAITING": 2345,
                        "ACTIVE": 3456,
                        "LB_UPDATED": 4567,
                        "RESTORE": 5678,
                        "ROLLBACK": 6789,
                        "ROLLBACK_LB_UPDATED": 7890,
                        "RESTORE_ON_ROLLBACK": 890,
                        "FAILURE": 90,
                    },
                },
                404,
            ),
        ]

        url = "/api/v1/agent/%s/status"
        for status, error_code in data:
            if error_code is None:
                _prepare_load_balancer(status["id"])
                response: HttpResponse = self.client.post(url % status["id"], status, format="json")
                self.assertIsInstance(response, drf_response.Response)
                self.assertEqual(204, response.status_code)
                self.assertIsNone(response.data)
                obj: agent_models.AgentStatus = agent_models.AgentStatus.objects.order_by("pk").last()
                self.assertEqual(status, serializers.AgentStatusSerializer(obj).data)
            else:
                response = self.client.post(url % status["id"], status, format="json")
                self.assertEqual(error_code, response.status_code)
