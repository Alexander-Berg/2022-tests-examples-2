import datetime
import logging
import typing
from unittest.mock import patch

from django.http import JsonResponse
from django.test import tag, Client, override_settings
from django.utils import timezone
from parameterized import parameterized
from rest_framework import status

from .base import RESTAPITest
from .. import models
from ..utils.throttling import ServiceOperationsThrottle
from ..views import UNSTRICT_QUERY_KEY

if typing.TYPE_CHECKING:
    from l3common.typing import JSON

logger: logging.Logger = logging.getLogger(__file__)


class ConfigTest(RESTAPITest):
    def _prepare_data(self) -> "typing.Tuple[Client, JSON, JSON, JSON, JSON]":
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        return user, svc, lb, vs, c

    @tag("core")
    def test_config_deploy(self):
        user, svc, lb, vs, c = self._prepare_data()
        c = self._deploy_config(user, c)

    @tag("core")
    def test_config_generator(self):
        # Case 1: No lbs in VS config - no config generated
        user = self._get_auth_client()

        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:3400:ffff::4ca"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )

        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        configs_generated = self._show_config_chunks(user, c)

        self.assertEqual(0, len(configs_generated), configs_generated)

        # Case 2: Static balancer's location doesn't overlap with real servers location. No configs generated
        lb1 = self._prepare_balancer(
            user, "vla0.yndx.net", ["Logbroker"], region=models.LocationRegion.REGION_CHOICES.VLA
        )
        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "443",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )

        c = self._prepare_config(user, svc, [vs1, vs2])
        configs_generated = self._show_config_chunks(user, c)

        self.assertEqual(0, len(configs_generated), configs_generated)

        # Case 3: one static balancer matches location with reals in two VSs - two configs generated
        lb2 = self._prepare_balancer(
            user, "man1-lb2b.yndx.net", ["Logbroker"], region=models.LocationRegion.REGION_CHOICES.MAN
        )

        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "443",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"], lb2["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"], lb2["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )

        c = self._prepare_config(user, svc, [vs1, vs2])
        configs_generated = self._show_config_chunks(user, c)

        self.assertEqual(2, len(configs_generated), configs_generated)

        # Case 4: Static balancer's location doesn't match reals location.
        # Dynamic balancer has skipped due to presence of static balancer in config
        # So, no config generated

        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "443",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb1["id"]],
                "groups": "lbkp-man-009.search.yandex.net",
            },
        )

        c = self._prepare_config(user, svc, [vs1, vs2])
        configs_generated = self._show_config_chunks(user, c)
        self.assertEqual(0, len(configs_generated), configs_generated)

    @tag("core")
    def test_config_activate(self):
        user, svc, lb, vs, c = self._prepare_data()
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

    @tag("core")
    def test_config_NEW_update(self):
        user, svc, lb, vs1, c = self._prepare_data()
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "443",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb["id"]],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        r = user.post(c["url"], {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(200, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("id" in result, result)
        self.assertEqual(c["id"], result["id"], result)
        self.assertTrue("vs_id" in result, result)
        self.assertSetEqual({vs1["id"], vs2["id"]}, set(result["vs_id"]), result)

    @tag("core")
    def test_config_incorrect(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs1])
        r = user.post(c["url"], {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(400, r.status_code, r.content)

    @tag("core")
    def test_config_incorrect_lb_weight(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [lb["id"]],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        vs2 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "443",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "config-WEIGHT_LB%s" % lb["id"]: "300",
                "lb": [lb["id"]],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs1])
        r = user.post(c["url"], {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(400, r.status_code, r.content)

    @tag("core")
    @patch("l3mgr.utils._tools.resolve_dns", autospec=True, return_value=[])
    def test_config_disable(self, _resolve_dns_mock):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:3400::4ca"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        c = self._activate_config(user, c)

        r = user.post("%s/hide" % svc["url"], {})
        self.assertEqual(403, r.status_code, r.content)

        r = user.post("%s/disable" % svc["url"], {})
        self.assertEqual(202, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        self.assertNotEqual(c["id"], result["object"]["id"], result)

        r = user.get("%s/config/%s" % (svc["url"], result["object"]["id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c2 = r.json()
        self.assertEqual("PREPARED", c2["state"], c2)

        c2 = self._activate_config(user, c2)
        self.assertEqual([], c2["vs_id"], c2)

        r = user.get(c["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c1 = r.json()
        self.assertEqual("INACTIVE", c1["state"], c1)

        abc = self._get_abc(user, svc["abc"])
        self.assertTrue(vs["ip"] in (ip["ip"] for ip in abc["ip"]), abc)

        r = user.post("%s/hide" % svc["url"], {})
        self.assertEqual(200, r.status_code, r.content)

        abc = self._get_abc(user, svc["abc"])
        self.assertFalse(vs["ip"] in (ip["ip"] for ip in abc["ip"]), abc)
        self.assertTrue("2a02:6b8:0:3400::4ca" in (ip["ip"] for ip in abc["ip"]), abc)

    @tag("core")
    def test_config_throttle(self):
        """
        Checking service config modification throttling
        """

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:3400:ffff::4ca"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )

        vs_data = {
            "ip": "2a02:6b8:0:3400:ffff::4c9",
            "port": "80",
            "protocol": "TCP",
            "config-CHECK_URL": "/ping",
            "config-ANNOUNCE": True,
            "lb": [],
            "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
        }

        throttler = ServiceOperationsThrottle(svc["id"])
        # Setting 2 configs in 3 seconds rate
        throttler.set_rate_limit(2, 3)

        vs = self._prepare_vs(user, svc, vs_data)
        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)

        vs = self._prepare_vs(user, svc, vs_data)
        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)

        time_boundary = timezone.now() - datetime.timedelta(seconds=4)
        models.Configuration.objects.filter(service_id=svc["id"], timestamp__gte=time_boundary).update(
            timestamp=timezone.now()
        )

        # The limit of two configs should exceed here, unless timedelta between 1st and 3rd requests is > 3s
        vs = self._prepare_vs(user, svc, vs_data)
        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(429, response.status_code)
        self.assertTrue(response.has_header("retry-after"))

        # instead of sleeping
        models.Configuration.objects.filter(service_id=svc["id"], timestamp__gte=time_boundary).update(
            timestamp=timezone.now() - datetime.timedelta(seconds=10)
        )

        # After throttling time expired requests should be allowed again
        vs = self._prepare_vs(user, svc, vs_data)
        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)

        throttler.reset_rate_limit()

    @tag("core")
    def test_config_order(self):
        """Checking service config order list."""

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::f4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )

        vs_data = {
            "ip": "2a02:6b8:0:3400:ffff::f4c9",
            "port": "80",
            "protocol": "TCP",
            "config-CHECK_URL": "/ping",
            "config-ANNOUNCE": True,
            "lb": [],
            "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
        }
        vs = self._prepare_vs(user, svc, vs_data)

        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)
        object = response.json()["object"]
        first_created_config_id = object["id"]

        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)
        object = response.json()["object"]
        second_created_config_id = object["id"]

        r = user.get("%s/config?_order=id" % svc["url"])
        self.assertEqual(200, r.status_code)
        configs = r.json()["objects"]
        self.assertListEqual([first_created_config_id, second_created_config_id], [cfg.get("id") for cfg in configs])

        r = user.get("%s/config?_order=-id" % svc["url"])
        self.assertEqual(200, r.status_code)
        configs = r.json()["objects"]
        self.assertListEqual([second_created_config_id, first_created_config_id], [cfg.get("id") for cfg in configs])

    @tag("core")
    def test_config_order_by_incorrect_fieldname(self):
        """Incorrect field must be ignored."""

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::f4c9"],
            [("2a02:6b8:b010:31::/64", "SAS")],
        )

        vs_data = {
            "ip": "2a02:6b8:0:3400:ffff::f4c9",
            "port": "80",
            "protocol": "TCP",
            "config-ANNOUNCE": True,
            "lb": [],
            "groups": "random-test-real.yandex.net=2a02:6b8:b010:31::f",
        }
        vs = self._prepare_vs(user, svc, vs_data)

        response = user.post("%s/config" % svc["url"], {"vs": vs["id"], "comment": "test config"})
        self.assertEqual(201, response.status_code)

        r = user.get("%s/config?_order=non-exist-field" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertEqual(1, len(r.json()["objects"]))

    def test_config_modification_success(self):
        user, svc, lb, vs1, c = self._prepare_data()
        cfg: models.Configuration = models.Configuration.objects.get(id=c["id"])
        self.assertEqual(models.Configuration.STATE_CHOICES.NEW, cfg.state)
        vs2 = self._prepare_vs(
            user,
            svc,
            {"ip": "2a02:6b8:0:3400:ffff::4c9", "port": "443", "protocol": "TCP", "groups": "%traffic_manage"},
        )
        r = user.post(c["url"], {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(200, r.status_code, r.content)
        self.assertEqual(c["id"], r.json()["id"], r.json())

    @parameterized.expand(
        [
            models.Configuration.STATE_CHOICES.PREPARED,
            models.Configuration.STATE_CHOICES.TEST_PENDING,
            models.Configuration.STATE_CHOICES.TESTING,
            models.Configuration.STATE_CHOICES.TEST_SUCCESS,
            models.Configuration.STATE_CHOICES.TEST_FAIL,
            models.Configuration.STATE_CHOICES.VCS_PENDING,
            models.Configuration.STATE_CHOICES.VCS_UPDATING,
            models.Configuration.STATE_CHOICES.VCS_COMMITED,
            models.Configuration.STATE_CHOICES.VCS_COMMITTED,
            models.Configuration.STATE_CHOICES.VCS_FAIL,
            models.Configuration.STATE_CHOICES.PENDING,
            models.Configuration.STATE_CHOICES.DEPLOYING,
            models.Configuration.STATE_CHOICES.FAIL,
            models.Configuration.STATE_CHOICES.ACTIVE,
            models.Configuration.STATE_CHOICES.INACTIVE,
        ]
    )
    @override_settings(USE_STRICT_API_REQUEST_MODE=True)
    def test_config_modification_fail(self, cfg_state):
        user, svc, lb, vs1, c = self._prepare_data()
        cfg: models.Configuration = models.Configuration.objects.get(id=c["id"])
        self.assertEqual(models.Configuration.STATE_CHOICES.NEW, cfg.state)
        cfg.state = cfg_state
        cfg.save()
        vs2 = self._prepare_vs(
            user,
            svc,
            {"ip": "2a02:6b8:0:3400:ffff::4c9", "port": "443", "protocol": "TCP", "groups": "%traffic_manage"},
        )
        r = user.post(c["url"], {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(status.HTTP_409_CONFLICT, r.status_code, r.content)

    @parameterized.expand(
        [
            (models.Configuration.STATE_CHOICES.NEW, status.HTTP_204_NO_CONTENT),
            (models.Configuration.STATE_CHOICES.PREPARED, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.TEST_PENDING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.TESTING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.TEST_SUCCESS, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.TEST_FAIL, status.HTTP_204_NO_CONTENT),
            (models.Configuration.STATE_CHOICES.VCS_PENDING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.VCS_UPDATING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.VCS_COMMITED, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.VCS_COMMITTED, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.VCS_FAIL, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.PENDING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.DEPLOYING, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.FAIL, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.ACTIVE, status.HTTP_409_CONFLICT),
            (models.Configuration.STATE_CHOICES.INACTIVE, status.HTTP_409_CONFLICT),
        ]
    )
    @override_settings(USE_STRICT_API_REQUEST_MODE=True)
    def test_config_deletion(self, cfg_state: models.Configuration.STATE_CHOICES, expected_status: int) -> None:
        user, svc, lb, vs1, c = self._prepare_data()
        cfg: models.Configuration = models.Configuration.objects.get(id=c["id"])
        self.assertEqual(models.Configuration.STATE_CHOICES.NEW, cfg.state)
        cfg.state = cfg_state
        cfg.save()
        r = user.delete(c["url"])
        self.assertEqual(expected_status, r.status_code, r.content)

    @parameterized.expand(
        [
            (models.Configuration.STATE_CHOICES.PREPARED, status.HTTP_200_OK),
            (models.Configuration.STATE_CHOICES.TEST_PENDING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.TESTING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.TEST_SUCCESS, status.HTTP_200_OK),
            (models.Configuration.STATE_CHOICES.TEST_FAIL, status.HTTP_200_OK),
            (models.Configuration.STATE_CHOICES.VCS_PENDING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.VCS_UPDATING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.VCS_COMMITED, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.VCS_COMMITTED, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.VCS_FAIL, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.PENDING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.DEPLOYING, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.FAIL, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.ACTIVE, status.HTTP_403_FORBIDDEN),
            (models.Configuration.STATE_CHOICES.INACTIVE, status.HTTP_403_FORBIDDEN),
        ]
    )
    @override_settings(USE_STRICT_API_REQUEST_MODE=True)
    def test_config_modification_with_unstrict(self, cfg_state, expected_status_code):
        user, svc, lb, vs1, c = self._prepare_data()
        cfg: models.Configuration = models.Configuration.objects.get(id=c["id"])
        self.assertEqual(models.Configuration.STATE_CHOICES.NEW, cfg.state)
        cfg.state = cfg_state
        cfg.save()
        vs2 = self._prepare_vs(
            user,
            svc,
            {"ip": "2a02:6b8:0:3400:ffff::4c9", "port": "443", "protocol": "TCP", "groups": "%traffic_manage"},
        )
        r = user.post(f"{c['url']}?{UNSTRICT_QUERY_KEY}", {"vs": [vs1["id"], vs2["id"]], "comment": "test update"})
        self.assertEqual(expected_status_code, r.status_code, r.content)
