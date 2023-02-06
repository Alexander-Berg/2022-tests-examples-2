import copy
import typing

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.test import tag
from parameterized import parameterized

from l3mgr.forms import VSConfigForm
from l3mgr.models import VirtualServer, LoadBalancer, RealServer, RealServerState, LocationRegion
from .base import RESTAPITest, RESTAPITransactionTestCase


class BaseVSTestMixIn:
    def _assert_config(self, config, connection_ip, connection_port, changed_parameters):
        self.assertDictEqual(
            {
                **{
                    "METHOD": "TUN",
                    "ANNOUNCE": False,
                    "QUORUM": 1,
                    "HYSTERESIS": 0,
                    "SCHEDULER": "wrr",
                    "MH_PORT": False,
                    "MH_FALLBACK": False,
                    "CHECK_TYPE": "TCP_CHECK",
                    "HTTP_PROTOCOL": None,
                    "HOST": None,
                    "CHECK_URL": "/ping",
                    "CONNECT_IP": connection_ip,
                    "CONNECT_PORT": connection_port,
                    "DIGEST": None,
                    "STATUS_CODE": 200,
                    "CHECK_TIMEOUT": 1,
                    "CHECK_RETRY": 1,
                    "CHECK_RETRY_TIMEOUT": 1,
                    "DELAY_LOOP": 10,
                    "DC_FILTER": False,
                    "INHIBIT_ON_FAILURE": False,
                    "PERSISTENCE_TIMEOUT": None,
                    "DYNAMICWEIGHT": False,
                    "DYNAMICWEIGHT_RATIO": 30,
                    "DYNAMICWEIGHT_IN_HEADER": False,
                    "DYNAMICWEIGHT_ALLOW_ZERO": False,
                    "OPS": False,
                    "TESTING_LBS": None,
                },
                **changed_parameters,
            },
            config,
        )


class VSTest(BaseVSTestMixIn, RESTAPITest):
    @tag("core")
    def test_vs_list(self):
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

        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

        # Add VS
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

        # List RS
        r = user.get("%s/rs" % vs["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(3, len(objects["objects"]))

    @tag("core")
    def test_vs_not_unique(self):
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

        # Add VS
        vs1 = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertNotEqual(vs1["id"], vs2["id"])
        self.assertEqual(vs1["ext_id"], vs2["ext_id"])
        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))

    @tag("core")
    def test_vs_assigned_ip(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")

        # Add VS
        r = user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(400, r.status_code, r.content)
        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

    @tag("core")
    def test_vs_unique_ip(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc1 = self._prepare_service(
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
        svc2 = self._prepare_service(user, "lbk-man.logbroker-stable.yandex.net", "Logbroker")

        # Add VS
        vs1 = self._prepare_vs(
            user,
            svc1,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        r = user.post(
            "%s/vs" % svc2["url"],
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
        self.assertEqual(400, r.status_code, r.content)
        # List VS
        r = user.get("%s/vs" % svc2["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

    @tag("core")
    def test_vs_update_by_id(self):
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
                "lb": lb["id"],
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Update vs by id
        r = user.post(
            vs["url"],
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
        self.assertEqual(200, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict))
        self.assertTrue("id" in result)
        self.assertEqual(vs["id"], result["id"])
        self.assertEqual([], result["lb"])

        # Delete vs by id
        r = user.delete(vs["url"])
        self.assertEqual(204, r.status_code, r.content)
        r = user.get(vs["url"])
        self.assertEqual(404, r.status_code, r.content)

    @tag("core")
    def test_vs_assign_to_NEW_config(self):
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
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        self._assert_config(vs["config"], "2a02:6b8:0:3400:ffff::4c9", 80, {"ANNOUNCE": True})

        c = self._prepare_config(user, svc, [vs])

        # Update vs by id
        r = user.post(
            vs["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-DIGEST": "1f2e3f",
                "config-ANNOUNCE": True,
                "lb": [lb["id"]],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(200, r.status_code, r.content)

        vs_data = r.json()
        self._assert_config(
            vs_data["config"],
            "2a02:6b8:0:3400:ffff::4c9",
            80,
            {"ANNOUNCE": True, "DIGEST": "1f2e3f", "STATUS_CODE": None},
        )

        # Delete vs by id
        r = user.delete(vs["url"])
        self.assertEqual(403, r.status_code, r.content)
        r = user.get(vs["url"])
        self.assertEqual(200, r.status_code, r.content)

    @tag("core")
    def test_vs_assign_to_not_NEW_config(self):
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
        c = self._deploy_config(user, c)

        # Update vs by id
        r = user.post(
            vs["url"],
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
        self.assertEqual(403, r.status_code, r.content)

        # Delete vs by id
        r = user.delete(vs["url"])
        self.assertEqual(403, r.status_code, r.content)
        r = user.get(vs["url"])
        self.assertEqual(200, r.status_code, r.content)

    @tag("core")
    def test_vs_global_add(self):
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

        # Add VS using fqdn and abc_code
        r = user.post(
            "/api/v1/vs",
            {
                "fqdn": "lbk-man.logbroker-prestable.yandex.net",
                "abc": "Logbroker",
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(201, r.status_code)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

        # Add VS using service_id
        r = user.post(
            "/api/v1/vs",
            {
                "service": svc["id"],
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))

    @tag("core")
    def test_vs_global_add_new_svc(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        abc = self._get_abc(user, "Logbroker")
        self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        self._add_rt_net("2a02:6b8:c01:300::/56", "MAN")
        self._add_rt_net("2a02:6b8:b040:3100::/56", "MAN")
        self._add_rt_net("2a02:6b8:0:1482::/64", "MYT")
        self._add_rt_net("2a02:6b8:b010:31::/64", "SAS")
        # Add VS to new fqdn and abc_code
        r = user.post(
            "/api/v1/vs",
            {
                "fqdn": "lbk-man.logbroker-prestable.yandex.net",
                "abc": "Logbroker",
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping1",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        self.assertTrue("service" in result["object"], result)
        # List VS
        r = user.get("/api/v1/service/%s/vs" % result["object"]["service"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        response_data = r.json()
        self.assertTrue(isinstance(response_data, dict))
        self.assertTrue("objects" in response_data)
        self.assertEqual(1, len(response_data["objects"]))

        service_data = response_data["objects"][0]
        config = service_data["config"]
        self._assert_config(config, "2a02:6b8:0:3400:ffff::4c9", 80, {"CHECK_URL": "/ping1", "ANNOUNCE": True})

    @tag("core")
    def test_vs_basic(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["dostavkatraffika"])
        abc = self._get_abc(user, "dostavkatraffika")
        self._add_ip(user, abc, "2a02:6b8:0:3400:0:4a8:0:3")

        # Add VS to new fqdn and abc_code
        r = user.post(
            "/api/v1/vs",
            {
                "ip": "2a02:6b8:0:3400:0:4a8:0:3",
                "port": 443,
                "abc": "dostavkatraffika",
                "fqdn": "testenv-fsm-ezhicker-service.yandex.net",
                "protocol": "TCP",
                "config-HOST": "",
                "config-METHOD": "TUN",
                "config-QUORUM": "1",
                "config-ANNOUNCE": "false",
                "config-CHECK_URL": "/pingggg",
                "config-SCHEDULER": "wrr",
                "config-OPS": "false",
                "config-CHECK_TYPE": "SSL_GET",
                "config-HYSTERESIS": "0",
                "config-STATUS_CODE": "200",
                "config-DC_FILTER": "false",
                "config-INHIBIT_ON_FAILURE": "false",
                "config-DYNAMICWEIGHT": "false",
                "config-DYNAMICWEIGHT_IN_HEADER": "true",
                "config-DYNAMICWEIGHT_RATIO": "30",
                "config-DYNAMICWEIGHT_ALLOW_ZERO": "false",
                "config-WEIGHT_DC_MSK": "100",
                "config-WEIGHT_DC_VLA": "100",
                "config-WEIGHT_DC_MAN": "100",
                "groups": "",
            },
        )
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        self.assertTrue("service" in result["object"], result)
        # List VS
        r = user.get("/api/v1/service/%s/vs" % result["object"]["service"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        response_data = r.json()
        self.assertTrue(isinstance(response_data, dict))
        self.assertTrue("objects" in response_data)
        self.assertEqual(1, len(response_data["objects"]))

        service_data = response_data["objects"][0]
        config = service_data["config"]
        self._assert_config(
            config,
            "2a02:6b8:0:3400:0:4a8:0:3",
            443,
            {
                "HOST": None,
                "METHOD": "TUN",
                "QUORUM": 1,
                "ANNOUNCE": False,
                "CHECK_URL": "/pingggg",
                "SCHEDULER": "wrr",
                "OPS": False,
                "CHECK_TYPE": "SSL_GET",
                "HYSTERESIS": 0,
                "STATUS_CODE": 200,
                "DC_FILTER": False,
                "INHIBIT_ON_FAILURE": False,
                "DYNAMICWEIGHT": False,
                "DYNAMICWEIGHT_IN_HEADER": True,
                "DYNAMICWEIGHT_RATIO": 30,
                "DYNAMICWEIGHT_ALLOW_ZERO": False,
                "WEIGHT_DC_MSK": 100,
                "WEIGHT_DC_VLA": 100,
                "WEIGHT_DC_MAN": 100,
            },
        )

    @tag("core")
    def test_vs_update_by_ext_id(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Update vs by ext_id
        r = user.post(
            "%s/vs/%s" % (svc["url"], vs["ext_id"]),
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
        self.assertEqual(404, r.status_code, r.content)

    @tag("core")
    def test_vs_update_existing_config_by_ext_id(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Prepare config
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        # Update vs by ext_id
        r = user.post(
            "%s/vs/%s" % (svc["url"], vs["ext_id"]),
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
        self.assertEqual(202, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        c_id = result["object"]["id"]
        self.assertNotEqual(c["id"], c_id, result)

        # Check old config
        r = user.get(c["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c = r.json()
        self.assertTrue(isinstance(c, dict), c)
        self.assertTrue("id" in c, c)
        self.assertEqual("ACTIVE", c["state"], c)

        # Get C
        r = user.get("%s/config/%s" % (svc["url"], c_id))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("id" in obj, obj)
        self.assertEqual(c_id, obj["id"], obj)
        self.assertEqual("PREPARED", obj["state"], obj)
        self.assertTrue(c["id"] not in obj["history"], obj)
        obj = self._activate_config(user, obj)

        # Check old config
        r = user.get(c["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c = r.json()
        self.assertTrue(isinstance(c, dict), c)
        self.assertTrue("id" in c, c)
        self.assertEqual("INACTIVE", c["state"], c)

    @tag("core")
    def test_vs_delete_by_ext_id(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Delete VS by ext_id
        r = user.delete("%s/vs/%s" % (svc["url"], vs["ext_id"]))
        self.assertEqual(404, r.status_code, r.content)

        # Prepare config
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        # Delete VS by ext_id
        r = user.delete("%s/vs/%s" % (svc["url"], vs["ext_id"]))
        self.assertEqual(202, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        c_id = result["object"]["id"]
        self.assertNotEqual(c_id, c["id"], result)

        # Get C
        r = user.get("%s/config/%s" % (svc["url"], c_id))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c = r.json()
        self.assertTrue(isinstance(c, dict), c)
        self.assertTrue("id" in c, c)
        self.assertEqual(c_id, c["id"], c)
        self.assertEqual("PREPARED", c["state"], c)

    @tag("core")
    def test_vs_global_access(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Get by id
        r = user.get("/api/v1/vs/%s" % vs["id"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("id" in obj, obj)
        self.assertEqual(vs["id"], obj["id"], obj)

    @tag("core")
    def test_vs_global_access_by_ext_id(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Get by id
        r = user.get("/api/v1/vs/%s" % vs["ext_id"])
        self.assertEqual(404, r.status_code, r.content)

        # Prepare config
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        r = user.get("/api/v1/vs/%s" % vs["ext_id"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("id" in obj, obj)
        self.assertEqual(vs["id"], obj["id"], obj)

    @tag("core")
    def test_vs_get_through_wrong_svc(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Get by id through wrong svc
        r = user.get("%s0/vs/%s" % (svc["url"], vs["id"]))
        self.assertEqual(404, r.status_code, r.content)

    @tag("core")
    def test_vs_get_with_wrong_ext_id(self):
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Prepare config
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        # Get by wrong ext_id
        r = user.get("%s/vs/000%s" % (svc["url"], vs["ext_id"][3:]))
        self.assertEqual(404, r.status_code, r.content)

    @tag("core")
    def test_minival_vs(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker", ["2a02:6b8:0:3400:ffff::4c9"]
        )

        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

        # Add VS
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
            },
        )

        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

    @tag("core")
    def test_vs_rs_params(self):
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

        # Add VS
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net weight=1000",
            },
        )

        # List VS
        r = user.get("%s/vs" % svc["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

        # List RS
        r = user.get("%s/rs" % vs["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(3, len(objects["objects"]))
        for rs in objects["objects"]:
            if rs["fqdn"] == "lbkp-man-009.search.yandex.net":
                self.assertEqual(1000, int(rs["config"].get("WEIGHT")), rs)
            else:
                self.assertEqual(1, int(rs["config"].get("WEIGHT", 1)), rs)

    @tag("core")
    def test_vs_ops_validation_error(self):
        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
        )

        with self.assertRaisesRegex(AssertionError, "201 != 400.*Incompatible protocol type"):
            self._prepare_vs(
                user,
                svc,
                {
                    "ip": "2a02:6b8:0:3400:ffff::4c9",
                    "port": "1080",
                    "protocol": "TCP",
                    "config-OPS": True,
                },
            )

        with self.assertRaisesRegex(AssertionError, "201 != 400.*Incompatible scheduler type"):
            self._prepare_vs(
                user,
                svc,
                {
                    "ip": "2a02:6b8:0:3400:ffff::4c9",
                    "port": "1080",
                    "protocol": "UDP",
                    "config-OPS": True,
                    "config-SCHEDULER": "wlc",
                },
            )

        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "1080",
                "protocol": "UDP",
                "config-OPS": True,
            },
        )
        self.assertTrue(vs.get("config", {}).get("OPS", False))

    @tag("core")
    def test_vs_parameters_validation(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")

        # Add VS
        r = user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-STATUS_CODE": "200,302",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "group": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(400, r.status_code, r.content)


class VSDatabaseObjectTest(RESTAPITest):
    def prepare_lb_and_vs(
        self, custom_lb_weight: typing.Optional[typing.Union[str, int]] = None
    ) -> typing.Tuple[LoadBalancer, VirtualServer]:
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        lb = LoadBalancer.objects.get(pk=lb["id"])

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

        vs_config = {
            "ip": "2a02:6b8:0:3400:ffff::4c9",
            "port": "80",
            "protocol": "TCP",
            "config-CHECK_URL": "/ping",
            "config-ANNOUNCE": True,
            "lb": lb.pk,
            "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
        }
        if custom_lb_weight:
            vs_config["config-WEIGHT_LB%s" % lb.pk] = custom_lb_weight

        # Add VS
        vs = self._prepare_vs(user, svc, vs_config)
        # Database object tests
        vs = VirtualServer.objects.get(pk=vs["id"])

        return lb, vs

    @tag("core")
    def test_vs_custom_lb_weight(self):
        default_lb_weight = 100
        custom_lb_weight = "nodisable"

        lb, vs = self.prepare_lb_and_vs(custom_lb_weight)

        vs.config.update_lb_weight(lb, vs.lb_ids)
        self.assertEqual(custom_lb_weight, vs.config.get("WEIGHT_LB%s" % lb.pk))

        # ignore specific lb list
        vs.config.update_lb_weight(lb)
        self.assertEqual(default_lb_weight, vs.config.get("WEIGHT_LB%s" % lb.pk))

    @tag("core")
    def test_vs_unspecified_lb_weight(self):
        default_lb_weight = 100

        lb, vs = self.prepare_lb_and_vs()

        vs.config.update_lb_weight(lb, vs.lb_ids)
        self.assertEqual(default_lb_weight, vs.config.get("WEIGHT_LB%s" % lb.pk))

        # ignore specific lb list
        vs.config.update_lb_weight(lb)
        self.assertEqual(default_lb_weight, vs.config.get("WEIGHT_LB%s" % lb.pk))

    @parameterized.expand(((-100,), (123,), ("abcde",)))
    @tag("core")
    def test_vs_invalid_lb_weight(self, invalid_lb_weight):
        with self.assertRaisesRegex(AssertionError, f"201 != 400.*Invalid weight.*{invalid_lb_weight}"):
            self.prepare_lb_and_vs(invalid_lb_weight)


class TestingLbsTestCase(RESTAPITest):
    def setUp(self):
        super().setUp()
        self._client = self._get_auth_client()

        self.lb = self.prepare_balancer("man1-lb2b", ["Logbroker"])
        self.svc = self._prepare_service(
            self._client,
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

    def prepare_balancer(self, fqdn, abcs=None, locations=None, testing=False):
        self.assertIsNotNone(self._client)
        return self._prepare_balancer(
            self._client, fqdn=fqdn, abcs=abcs, locations=locations, testing=testing
        )

    def test_vs_with_specified_testing_lb(self):
        testing_lb_id = self.prepare_balancer(fqdn="any4-lb-check.yndx.net", locations={"MAN"}, testing=True)["id"]
        vs = self.prepare_vs(testing_lb_id)
        testing_lbs_ids = vs.config["TESTING_LBS"]
        self.assertListEqual(testing_lbs_ids, [testing_lb_id])

    def test_vs_with_specified_several_testing_lbs(self):
        testing_lb_ids = [
            self.prepare_balancer(fqdn="any4-lb-check.yndx.net", locations={"MAN"}, testing=True)["id"],
            self.prepare_balancer(fqdn="any5-lb-check.yndx.net", locations={"VLA"}, testing=True)["id"],
        ]
        vs = self.prepare_vs(",".join(map(str, testing_lb_ids)))
        testing_lbs_ids = vs.config["TESTING_LBS"]
        self.assertListEqual(testing_lbs_ids, testing_lb_ids)

    def test_vs_with_specified_testing_lb_as_production(self):
        testing_lb_id = self.prepare_balancer(fqdn="any4-lb-check.yndx.net", locations={"MAN"}, testing=False)["id"]
        r = self._client.post("%s/vs" % self.svc["url"], self.get_prepare_vs_params(testing_lb_id))
        self.assertEqual(400, r.status_code, r.content)
        response_data = r.json()
        self.assertIn("errors", response_data)
        errors = response_data["errors"]
        self.assertIn("config", errors)
        self.assertListEqual([f'* TESTING_LBS\n  * Invalid TESTING_LBS "[{testing_lb_id}]"'], errors["config"])

    def test_vs_with_specified_several_testing_lb_with_invalid_one(self):
        testing_lb_ids = [
            self.prepare_balancer(fqdn="any4-lb-check.yndx.net", locations={"MAN"}, testing=True)["id"],
            self.prepare_balancer(fqdn="any5-lb-check.yndx.net", locations={"VLA"}, testing=False)["id"],
        ]
        r = self._client.post("%s/vs" % self.svc["url"], self.get_prepare_vs_params(",".join(map(str, testing_lb_ids))))
        self.assertEqual(400, r.status_code, r.content)
        response_data = r.json()
        self.assertIn("errors", response_data)
        errors = response_data["errors"]
        self.assertIn("config", errors)
        self.assertListEqual([f'* TESTING_LBS\n  * Invalid TESTING_LBS "[{testing_lb_ids[1]}]"'], errors["config"])

    def test_vs_with_invalid_specified_testing_lb(self):
        r = self._client.post("%s/vs" % self.svc["url"], self.get_prepare_vs_params("123"))
        self.assertEqual(400, r.status_code, r.content)
        response_data = r.json()
        self.assertIn("errors", response_data)
        errors = response_data["errors"]
        self.assertIn("config", errors)
        self.assertListEqual(['* TESTING_LBS\n  * Invalid TESTING_LBS "[123]"'], errors["config"])

    def prepare_vs(self, config_testing_lbs_value):
        # Add VS
        vs = self._prepare_vs(
            self._client,
            self.svc,
            self.get_prepare_vs_params(config_testing_lbs_value),
        )

        # Database object tests
        vs = VirtualServer.objects.get(pk=vs["id"])
        return vs

    def get_prepare_vs_params(self, config_testing_lbs_value):
        return {
            "ip": "2a02:6b8:0:3400:ffff::4c9",
            "port": "80",
            "protocol": "TCP",
            "config-TESTING_LBS": config_testing_lbs_value,
            "lb": self.lb["id"],
            "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
        }


class VirtualVSTest(RESTAPITest):
    def setUp(self):
        super().setUp()
        self.vs = VirtualServer(
            **{
                "id": 1069929,
                "service_id": 137,
                "rs_ids": [],
                "groups": [],
                "config": {
                    "OPS": False,
                },
                "port": 80,
                "lb_ids": [],
                "ip": "2a02:6b8:0:3400::50",
                "protocol": "TCP",
                "ext_id": "fedf943ccce1c167475dcd820360ba49772affc22aba23720521a7605aff728e",
            }
        )

    @tag("core")
    def test_default_values(self):
        self.vs.validate()

    @parameterized.expand(
        (
            ({"OPS": True}, None, "Incompatible protocol type for one packet scheduler flag"),
            ({"OPS": True, "SCHEDULER": "wlc"}, "UDP", "Incompatible scheduler type for one packet scheduler flag"),
            (
                {"INHIBIT_ON_FAILURE": True, "PERSISTENCE_TIMEOUT": 1},
                None,
                "Incompatible persistence timeout for inhibit on failure flag",
            ),
        )
    )
    @tag("core")
    def test_incompatibles_values(self, config, protocol, msg):
        vs = copy.deepcopy(self.vs)
        vs.config = config
        if protocol:
            vs.protocol = protocol
        with self.assertRaisesMessage(ValidationError, msg):
            vs.validate()


class QuorumIntegerBehaviourTest(RESTAPITest):
    def setUp(self):
        super().setUp()

        user = self._get_auth_client()
        self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
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
                "groups": "2a02:6b8:c01:300:0:42d5:f4a7:0\n"
                "2a02:6b8:b040:3100:0:4daf:d87e:0\n"
                "2a02:6b8:b040:3100:0:42d5:b5b8:0",
            },
        )
        self._prepare_config(user, svc, [vs])

        self.lb = LoadBalancer.objects.get(fqdn="man1-lb2b.yndx.net")
        self.vs = VirtualServer.objects.get(ip="2a02:6b8:0:3400:ffff::4c9")

        for rs in RealServer.objects.all():
            RealServerState.objects.get_or_create(balancer=self.lb, vs=self.vs, server=rs, fwmark=1)

    @tag("core")
    def test_default_values(self):
        # check default quorum value
        config = self.vs.config
        config.update({"QUORUM": 1, "HYSTERESIS": 0})
        VirtualServer.objects.filter(pk=self.vs.id).update(config=config)

        RealServerState.objects.all().update(state="INACTIVE")

        amount, expected = self.vs.servers_amount_for_lb(self.lb)
        self.assertEqual(0, amount)
        self.assertEqual(1, expected)

    @tag("core")
    def test_changed_quorum(self):
        # Check changes quorum value
        config = self.vs.config
        config.update({"QUORUM": 2})
        self.vs.config = config
        self.vs.save()

        _, expected = self.vs.servers_amount_for_lb(self.lb)
        self.assertEqual(2, expected)

    @tag("core")
    def test_active_reals(self):
        # enable real states
        RealServerState.objects.all().update(state="ACTIVE")
        amount, _ = self.vs.servers_amount_for_lb(self.lb)
        self.assertEqual(3, amount)


class QuorumPercentBehaviourTest(RESTAPITest):
    def setUp(self):
        super().setUp()

        user = self._get_auth_client()
        self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
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
                "groups": "2a02:6b8:b040:3100:0:42d5:f4a7:0 weight=11\n"
                "2a02:6b8:b040:3100:0:4daf:d87e:0\n"
                "2a02:6b8:b040:3100:0:42d5:b5b8:0 weight=29\n"
                "2a02:6b8:b040:3100:0:1452:7894:bdd6\n"
                "2a02:6b8:b040:3100:10c:e83d:0:60fe weight=43",
            },
        )
        self._prepare_config(user, svc, [vs])

        self.lb = LoadBalancer.objects.get(fqdn="man1-lb2b.yndx.net")
        self.vs = VirtualServer.objects.get(ip="2a02:6b8:0:3400:ffff::4c9")

        for rs in RealServer.objects.all():
            RealServerState.objects.get_or_create(balancer=self.lb, vs=self.vs, server=rs, fwmark=1)

    @tag("core")
    def test_percent_quorum(self):
        config = self.vs.config
        config.update({"QUORUM": "33%", "HYSTERESIS": 10})
        VirtualServer.objects.filter(pk=self.vs.id).update(config=config)

        RealServerState.objects.all().update(state="DISABLED")
        RealServerState.objects.filter(server__ip="2a02:6b8:b040:3100:0:1452:7894:bdd6").update(state="INACTIVE")
        RealServerState.objects.filter(
            server__ip__in=[
                "2a02:6b8:b040:3100:0:42d5:f4a7:0",
                "2a02:6b8:b040:3100:0:4daf:d87e:0",
                "2a02:6b8:b040:3100:0:42d5:b5b8:0",
            ]
        ).update(state="ACTIVE")
        actual, expected = self.vs.servers_amount_for_lb(self.lb)

        # 41 = (11 + 1 + 29), where 11, 1 and 29 are weights of
        # 2a02:6b8:b040:3100:0:42d5:f4a7:0, 2a02:6b8:b040:3100:0:4daf:d87e:0, 2a02:6b8:b040:3100:0:42d5:b5b8:0
        self.assertEqual(41, actual)

        # 39 = (11 + 1 + 29 + 1 + 0 (disabled)) * 33% + 10 = CEIL(13.86) + 10
        self.assertEqual(24, expected)

    @tag("core")
    def test_percent_histeresys(self):
        config = self.vs.config
        config.update({"QUORUM": 20, "HYSTERESIS": "5%"})
        VirtualServer.objects.filter(pk=self.vs.id).update(config=config)

        RealServerState.objects.all().update(state="INACTIVE")
        RealServerState.objects.filter(
            server__ip__in=[
                "2a02:6b8:b040:3100:0:1452:7894:bdd6",
                "2a02:6b8:b040:3100:10c:e83d:0:60fe",
            ]
        ).update(state="ACTIVE")
        actual, expected = self.vs.servers_amount_for_lb(self.lb)

        # 44 = (1 + 43), where 1 and 43 are weights of
        # 2a02:6b8:b040:3100:0:1452:7894:bdd6, 2a02:6b8:b040:3100:10c:e83d:0:60fe
        self.assertEqual(44, actual)

        # 24 = 20 + (11 + 1 + 29 + 1 + 43) * 5% = 20 + FLOOR(4.25)
        self.assertEqual(24, expected)


class VSValidatorHelpersTest(RESTAPITest):
    def setUp(self):
        super().setUp()

        self.user = self._get_auth_client()
        self.lb = self._prepare_balancer(
            self.user, "man1-lb2b.yndx.net",  ["Logbroker", "dostavkatraffika"]
        )

    @tag("core")
    def test_meta_service_owner(self):
        svc = self._prepare_service(
            self.user,
            "test-slb-meta-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
            {"OWNER": "exclude-awacs"},
        )
        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
            },
        )

        payload = vs.json().get("object")
        self.assertIsNotNone(payload.get("message"))
        self.assertIn("test-alert-real.yp-c.yandex.net", payload.get("message"))
        self.assertIn("https://wiki.yandex-team.ru/cplb/awacs/tutorial/L3-L7/#add", payload.get("message"))

    @tag("core")
    def test_reals_intersection_messages(self):
        svc = self._prepare_service(
            self.user,
            "test-slb-logroker-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c0"],
            [("2a02:6b8:b040:3102::/56", "MAN")],
        )
        vs = self._prepare_vs(
            self.user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c0",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "random-backendname.yandex.net=2a02:6b8:b040:3102:0:42d5:f4a7:0",
            },
        )
        self._make_rs_state("2a02:6b8:b040:3102:0:42d5:f4a7:0", vs["id"], self.lb["id"], "INACTIVE")

        svc = self._prepare_service(
            self.user,
            "test-slb-dostavkatraffika-service.yandex.net",
            "dostavkatraffika",
            ["2a02:6b8:0:3400:ffff::4c1"],
        )
        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4c1",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "random-backendname.yandex.net=2a02:6b8:b040:3102:0:42d5:f4a7:0",
            },
        )

        payload = vs.json().get("object")
        self.assertIsNotNone(payload.get("message"))
        self.assertIn("Some RSs already in use", payload.get("message"))

    @tag("core")
    def test_no_messages(self):
        svc = self._prepare_service(
            self.user,
            "test-slb-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4ca"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
            {"OWNER": "awacs"},
        )
        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
            },
        )

        payload = vs.json().get("object")
        self.assertIsNone(payload.get("message"))

    @tag("core")
    def test_no_owner_messages(self):
        svc = self._prepare_service(
            self.user,
            "test-slb-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4ca"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
        )
        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
            },
        )

        payload = vs.json().get("object")
        self.assertIsNotNone(payload.get("message"))
        self.assertIn("https://wiki.yandex-team.ru/cplb/awacs/tutorial/L3-L7/#add", payload.get("message"))

    @tag("core")
    def test_use_zero_port_messages(self):
        svc = self._prepare_service(
            self.user,
            "test-slb-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4ca"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
        )
        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "0",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
            },
        )
        msg = vs.json().get("message")
        self.assertIsNotNone(msg)
        self.assertIn("Ensure this value is greater than or equal to 1.", msg)

        vs = self.user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::4ca",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "config-CONNECT_PORT": "0",
                "lb": [],
                "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
            },
        )
        msg = vs.json().get("message")
        self.assertIsNotNone(msg)
        self.assertIn("Ensure this value is greater than or equal to 1.", msg)


class VSMaglevOptionsTest(RESTAPITest):
    def setUp(self):
        super().setUp()

        self.user = self._get_auth_client()
        self.lb = self._prepare_balancer(
            self.user, "man1-lb2b.yndx.net", ["Logbroker", "dostavkatraffika"]
        )
        self.svc = self._prepare_service(
            self.user,
            "test-slb-config-options-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
        )
        self.vs_config = {
            "ip": "2a02:6b8:0:3400:ffff::4c9",
            "port": "80",
            "protocol": "TCP",
            "config-ANNOUNCE": True,
            "lb": [],
            "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
        }

    @tag("core")
    def test_false_maglev_options(self):
        r = self.user.post("%s/vs" % self.svc["url"], self.vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertFalse(vs.config.get("MH_PORT"))
        self.assertFalse(vs.config.get("MH_FALLBACK"))

    @tag("core")
    def test_overwrite_to_false_maglev_options(self):
        vs_config = self.vs_config.copy()
        vs_config.update({"config-MH_FALLBACK": True})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertNotEqual(VSConfigForm.SCHEDULER_CHOICES.mh, vs.config.get("SCHEDULER"))
        self.assertFalse(vs.config.get("MH_PORT"))
        self.assertFalse(vs.config.get("MH_FALLBACK"))

    @tag("core")
    def test_port_maglev_options(self):
        vs_config = self.vs_config.copy()
        vs_config.update(
            {
                "config-SCHEDULER": "mh",
                "config-MH_PORT": True,
            }
        )
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertTrue(vs.config.get("MH_PORT"))
        self.assertEqual(VSConfigForm.SCHEDULER_CHOICES.mh, vs.config.get("SCHEDULER"))

    @tag("core")
    def test_maglev_options_and_inhibit(self):
        vs_config = self.vs_config.copy()
        vs_config.update(
            {
                "config-MH_FALLBACK": True,
                "config-INHIBIT_ON_FAILURE": True,
            }
        )
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertTrue(vs.config.get("MH_FALLBACK"))

    @tag("core")
    def test_maglev_options_and_dynamic_weight(self):
        vs_config = self.vs_config.copy()
        vs_config.update(
            {
                "config-MH_FALLBACK": True,
                "config-DYNAMICWEIGHT": True,
            }
        )
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertFalse(vs.config.get("MH_FALLBACK"))

        # Enable zero weight support
        vs_config.update({"config-DYNAMICWEIGHT_ALLOW_ZERO": True})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertTrue(vs.config.get("MH_FALLBACK"))


class VSHTTPProtocolOptionsTest(RESTAPITest):
    def setUp(self):
        super().setUp()

        self.user = self._get_auth_client()
        self.lb = self._prepare_balancer(
            self.user, "man1-lb2b.yndx.net", ["Logbroker", "dostavkatraffika"]
        )
        self.svc = self._prepare_service(
            self.user,
            "test-slb-config-options-service.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [("2a02:6b8:b040:3100::/56", "MAN")],
        )
        self.vs_config = {
            "ip": "2a02:6b8:0:3400:ffff::4c9",
            "port": "80",
            "protocol": "TCP",
            "config-ANNOUNCE": True,
            "lb": [],
            "groups": "test-alert-real.yp-c.yandex.net=2a02:6b8:b040:3100:0:42d5:f4a7:0",
        }

    @tag("core")
    def test_empty_option(self):
        r = self.user.post("%s/vs" % self.svc["url"], self.vs_config)
        self.assertEqual(201, r.status_code, r.content)

        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertIsNone(vs.config.get("HTTP_PROTOCOL"))

    @tag("core")
    def test_bad_request(self):
        vs_config = self.vs_config.copy()
        vs_config.update({"config-HTTP_PROTOCOL": "HTTP_1_0C"})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(400, r.status_code, r.content)

    @tag("core")
    def test_exist_options(self):
        vs_config = self.vs_config.copy()

        vs_config.update({"config-HTTP_PROTOCOL": "1.0"})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)
        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertEqual(VSConfigForm.HTTP_PROTOCOL_CHOICES.HTTP_1_0, vs.config.get("HTTP_PROTOCOL"))

        vs_config.update({"config-HTTP_PROTOCOL": "1.0C"})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)
        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertEqual(VSConfigForm.HTTP_PROTOCOL_CHOICES.HTTP_1_0C, vs.config.get("HTTP_PROTOCOL"))

        vs_config.update({"config-HTTP_PROTOCOL": "1.1"})
        r = self.user.post("%s/vs" % self.svc["url"], vs_config)
        self.assertEqual(201, r.status_code, r.content)
        vs = VirtualServer.objects.get(pk=r.json().get("object", {}).get("id"))
        self.assertEqual(VSConfigForm.HTTP_PROTOCOL_CHOICES.HTTP_1_1, vs.config.get("HTTP_PROTOCOL"))


class VSTransactionTest(BaseVSTestMixIn, RESTAPITransactionTestCase):
    databases = ["default", settings.RO_DATABASE]

    @tag("core")
    def test_vs_get_by_ext_id(self):
        user = self._get_auth_client()
        LocationRegion.objects.update_or_create(code="MAN", location=["MAN"])
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"], region="MAN")
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
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # List VS
        r = user.get("%s/vs/%s" % (svc["url"], vs["ext_id"]))
        self.assertEqual(404, r.status_code)

        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        # Get VS by ext_id
        r = user.get("%s/vs/%s" % (svc["url"], vs["ext_id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        vs_ext = r.json()
        self.assertTrue(isinstance(vs_ext, dict), vs_ext)
        self.assertTrue("id" in vs_ext, vs_ext)
        self.assertEqual(vs["id"], vs_ext["id"], vs_ext)

        # Get RS by ext_id
        r = user.get("%s/vs/%s/rs" % (svc["url"], vs["ext_id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(3, len(objects["objects"]), objects)

        # Get RSState by ext_id
        r = user.get("%s/vs/%s/rsstate" % (svc["url"], vs["ext_id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(0, len(objects["objects"]), objects)

        # Generate config to create RSStates
        content = self._show_config(user, c)
        parts = list(content)
        self.assertEqual(2, len(parts), parts)

        # Get RSState by ext_id
        r = user.get("%s/vs/%s/rsstate" % (svc["url"], vs["ext_id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(1, len(objects["objects"]), objects)
