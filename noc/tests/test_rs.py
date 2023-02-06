from unittest.mock import patch, Mock
import warnings

from django.conf import settings
from django.http import JsonResponse
from django.test import override_settings, tag
from parameterized import parameterized

from l3conductor.exceptions import ConductorException
from l3gencfg.exceptions import GenCfgException
from l3racktables.exceptions import RackTablesResponseFormatException
from .base import RESTAPITest, RESTAPITransactionTestCase
from .. import models


class RSTest(RESTAPITest):
    @tag("core")
    def test_rs_list(self):
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
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        # List RS
        r = user.get(f"{vs['url']}/rs")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(3, len(objects["objects"]), objects)

    @tag("core")
    def test_rs_add(self):
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
                "groups": "%traffic_manage",
            },
        )
        r = user.post(
            f"{vs['url']}/rs", {"ip": "2a02:6b8:b040:3100:ccc::4c9", "fqdn": "lbkp-man-009.search.yandex.net"}
        )
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)

        # Add IPv4 RS to IPv6 VS not allowed
        r = user.post(f"{vs['url']}/rs", {"ip": "37.9.108.100", "fqdn": "sas1-hm.slb.yandex.net"})
        self.assertEqual(400, r.status_code, r.content)
        # List RS
        r = user.get(f"{vs['url']}/rs")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(3, len(objects["objects"]), objects)

        # Replace existing RS
        r = user.post(
            f"{vs['url']}/rs",
            {
                "ip": "2a02:6b8:b040:3100:ccc::4c9",
                "fqdn": "lbkp-man-009.search.yandex.net",
                "config-WEIGHT": 500,
            },
        )
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)
        # List replaced RS
        r = user.get(f"{vs['url']}/rs")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(3, len(objects["objects"]), objects)

    @tag("core")
    def test_rs_add_forbidden(self):
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
                "groups": "%traffic_manage",
            },
        )
        with self.settings(YAUTH_TEST_USER="unknown"):
            # Add to VS
            r = user.post(
                f"{vs['url']}/rs", {"ip": "2a02:6b8:b040:3100:ccc::4c9", "fqdn": "lbkp-man-009.search.yandex.net"}
            )
            self.assertEqual(403, r.status_code, r.content)

    @tag("core")
    @override_settings(YAUTH_TEST_USER="unknown")
    def test_rs_add_global(self):
        # Add to global NS
        user = self._get_auth_client()
        r = user.post(
            f"{self.BASE_URL}/rs", {"ip": "2a02:6b8:b040:3100:ccc::4c9", "fqdn": "lbkp-man-009.search.yandex.net"}
        )
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)

    @tag("core")
    def test_rs_add_global_by_ip(self):
        # Add to global NS
        user = self._get_auth_client()

        r = user.post(f"{self.BASE_URL}/network", {"ip": "2a02:6b8:0:1482::/64", "location": "MYT"})
        self.assertEqual(201, r.status_code, r.content)

        r = user.post(f"{self.BASE_URL}/rs", {"ip": "2a02:6b8:0:1482::115", "fqdn": "mnt-myt.yandex.net"})
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)

        r = user.get(location)
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        rs = r.json()
        self.assertTrue(isinstance(rs, dict), rs)
        self.assertEqual("mnt-myt.yandex.net", rs["fqdn"], rs)
        self.assertEqual("2a02:6b8:0:1482::115", rs["ip"], rs)
        self.assertEqual(["MYT"], rs["location"], rs)

        r = user.post(f"{self.BASE_URL}/rs", {"fqdn": "2a02:6b8:0:1482::115", "location": "IVA"})
        self.assertEqual(400, r.status_code, r.content)

        r = user.post(f"{self.BASE_URL}/rs", {"fqdn": "2a02:6b8:0:1482::115", "config-WEIGHT": 3})
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)
        self.assertNotEqual(rs["id"], obj["object"]["id"], obj)

        r = user.get(location)
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        rs = r.json()
        self.assertTrue(isinstance(rs, dict), rs)
        self.assertEqual("2a02:6b8:0:1482::115", rs["fqdn"], rs)
        self.assertEqual("2a02:6b8:0:1482::115", rs["ip"], rs)
        self.assertEqual(["MYT"], rs["location"], rs)
        self.assertEqual(3, rs["config"]["WEIGHT"], rs)

    @tag("core")
    def test_rs_edit(self):
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
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        r = user.get(f"{vs['url']}/rs")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(3, len(objects["objects"]), objects)
        rs_list = [rs for rs in objects["objects"] if rs["fqdn"] == "lbkp-man-009.search.yandex.net"]
        self.assertEqual(1, len(rs_list), rs_list)
        rs = rs_list[0]
        # Update RS with full data
        r = user.post(
            f"{vs['url']}/rs/{rs['id']}",
            {
                "ip": "2a02:6b8:b040:3100:ccc::4c9",
                "fqdn": "lbkp-man-009.search.yandex.net",
                "config-WEIGHT": 500,
            },
        )
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("id" in obj, obj)
        self.assertTrue("config" in obj, obj)
        self.assertTrue("WEIGHT" in obj["config"], obj)
        self.assertEqual(500, obj["config"]["WEIGHT"], obj)
        # Update RS with config data
        r = user.post(f"{vs['url']}/rs/{rs['id']}", {"config-WEIGHT": 500})
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("id" in obj, obj)
        self.assertTrue("config" in obj, obj)
        self.assertTrue("WEIGHT" in obj["config"], obj)
        self.assertEqual(500, obj["config"]["WEIGHT"], obj)

    @tag("core")
    def test_rs_add_to_active_vs(self):
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
                "groups": "%traffic_manage",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        # Add RS to active VS forbidden
        r = user.post(
            f"{vs['url']}/rs",
            {"ip": "2a02:6b8:b040:3100:ccc::4c9", "fqdn": "lbkp-man-009.search.yandex.net"},
        )
        self.assertEqual(403, r.status_code, r.content)

    def test_rs_get_vips_by_rs_ip(self):
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
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)
        rs_ip = "2a02:6b8:b040:3100:ccc::4c9"
        self._make_rs_state(rs_ip, vs["id"], lb["id"], "INACTIVE")
        r = user.get(f"/api/v1/rs/{rs_ip}/vips")
        self.assertEqual(200, r.status_code, r.content)
        self.assertEqual(vs["ip"], r.content.decode("utf-8"))

    def test_rs_get_vslist_by_rs_ip(self):
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
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)
        rs_ip = "2a02:6b8:b040:3100:ccc::4c9"
        self._make_rs_state(rs_ip, vs["id"], lb["id"], "INACTIVE")

        # existent RS connected to active VS
        r = user.get(f"/api/v1/rs/{rs_ip}/vips?vslist=True")
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        objects = r.json()
        self.assertIsInstance(objects, dict)
        self.assertIn("objects", objects)
        self.assertEqual(1, len(objects["objects"]))
        r_vs = objects["objects"][0]
        self.assertEqual(r_vs["fqdn"], "lbk-man.logbroker-prestable.yandex.net")
        self.assertEqual(r_vs["ip"], "2a02:6b8:0:3400:ffff::4c9")
        self.assertEqual(r_vs["port"], 80)
        self.assertEqual(r_vs["protocol"], "TCP")

        # non-existent RS
        r = user.get("/api/v1/rs/2001:db8::ffff/vips?vslist=True")
        self.assertEqual(400, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        objects = r.json()
        self.assertIsInstance(objects, dict)
        self.assertIn("result", objects)
        self.assertEqual(objects["result"], "ERROR")

        # incorrect IP
        r = user.get("/api/v1/rs/fff:aaa.:99/vips?vslist=True")
        self.assertEqual(400, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        objects = r.json()
        self.assertIsInstance(objects, dict)
        self.assertIn("result", objects)
        self.assertEqual(objects["result"], "ERROR")


class RSLocationTest(RESTAPITest):
    @tag("core")
    def test_ignore_manual_network(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
        )

        self.assertFalse(models.LocationNetwork.objects.filter(ip="2a02:6b8:b040:3100::/56").exists())
        # create manual network API call
        self._add_net(user, ("2a02:6b8:b040:3100::/56", "MAN"))
        self.assertEqual(
            1,
            models.LocationNetwork.objects.filter(
                ip="2a02:6b8:b040:3100::/56",
                location=[models.LocationNetwork.LOCATION_CHOICES.MAN],
                source=models.LocationNetwork.SOURCE_CHOICES.MANUAL,
            ).count(),
        )

        r = user.post(
            f"{svc['url']}/vs",
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "lbkp-man-009.search.yandex.net=2a02:6b8:b040:3100:ccc::4c9",
            },
        )
        self.assertEqual(400, r.status_code, r.content)
        self.assertContains(r, "Could not detect network location for RS: 2a02:6b8:b040:3100:ccc::4c9", status_code=400)

    @tag("core")
    def test_successful_network(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
        )

        self._add_rt_net("2a02:6b8:b040:3100::/64", "MAN")
        r = user.post(
            f"{svc['url']}/vs",
            {
                "ip": "2a02:6b8:0:3400:ffff::4c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": "lbkp-man-009.search.yandex.net=2a02:6b8:b040:3100:ccc::4c9",
            },
        )
        self.assertEqual(201, r.status_code, r.content)


class RSTransactionTest(RESTAPITransactionTestCase):
    databases = ["default", settings.RO_DATABASE]

    @tag("core")
    def test_rs_state_order(self):
        user = self._get_auth_client()

        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable-order.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4ce"],
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
                "ip": "2a02:6b8:0:3400:ffff::4ce",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": (
                    "test-real-one.yandex.net=2a02:6b8:b040:310c:feaa:14ff:fe65:ccb5\n"
                    "test-real-two.yandex.net=2a02:6b8:b040:310c:feaa:14ff:fe65:c940\n"
                    "test-real-three.yandex.net=2a02:6b8:b040:310e:e61d:2dff:fe6c:f490\n",
                ),
            },
        )

        # List RS
        r = user.get(f"{vs['url']}/rs")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        rss = r.json().get("objects")
        self.assertEqual(3, len(rss))

        # Prepare RS states
        for rs in rss:
            self._make_rs_state(rs["ip"], vs["id"], lb["id"], "INACTIVE")

        # Get RSState by VS ID
        r = user.get(f"{vs['url']}/rsstate?_limit=10")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        states = r.json().get("objects")
        self.assertEqual(3, len(states))

        # Check states order by pk
        self.assertEqual(
            [rs.get("ip") for rs in rss],
            [st.get("rs").get("ip") for st in states],
        )


class ProcessGroupRSTest(RESTAPITest):
    @tag("core")
    def test_rsgroup_exclude_fqdn(self):
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
                "groups": "%traffic_manage\n" "-mnt-myt.yandex.net weight=10",
            },
        )
        with warnings.catch_warnings(record=True) as w:
            r = user.get("%s/rs?_all=true" % vs["url"])
            self.assertListEqual([], w)

        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        self.assertNotContains(r, "mnt-myt.yandex.net")
        self.assertGreater(len(r.json().get("objects")), 0)

    @tag("core")
    def test_fqdn_exclude_rsgroup(self):
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
                "groups": (
                    "-%traffic_manage\n"
                    "random-test-host-nZ5RW6jIr7JMGy0XB2QR.yandex.net=2a02:6b8:0:1482::ff:ff\n"
                    "mnt-myt.yandex.net\n"
                    "mnt-sas.yandex.net\n"
                ),
            },
        )
        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        self.assertNotContains(r, "mnt-myt.yandex.net")
        self.assertContains(r, "random-test-host-nZ5RW6jIr7JMGy0XB2QR.yandex.net")
        self.assertEqual(len(r.json().get("objects")), 1)

    @parameterized.expand(
        (
            (
                [
                    "@mtn:MAN_CLOUDAPI_WEATHER_BALANCER/stable-125-r1568",
                    "-man1-6276-man-cloudapi-weather-ba-61e-17973.gencfg-c.yandex.net=2a02:6b8:c01:300:e61d:2dff:fe6e:3b60",
                ],
                ["man1-8084-man-cloudapi-weather-ba-61e-17973.gencfg-c.yandex.net"],
                ["man1-6276-man-cloudapi-weather-ba-61e-17973.gencfg-c.yandex.net"],
            ),
            (
                ["%traffic_manage", "random-test-host.yandex.net=2a02:6b8:b010:31::1315:20ad:447b"],
                ["random-test-host.yandex.net", "mnt-myt.yandex.net"],
                [],
            ),
            (
                [
                    "mnt-sas-focal.tt.yandex.net=2a02:6b8:b010:31::a",
                    "mnt-myt.tt.yandex.net=2a02:6b8:0:1482::b",
                    "-$traffic_manage",
                ],
                ["mnt-sas-focal.tt.yandex.net"],
                ["mnt-myt.tt.yandex.net", "mnt-sas.tt.yandex.net"],
            ),
        )
    )
    @patch("l3racktables.utils._RACKTABLES_API._read_json")
    @patch("l3conductor.utils.get_hosts_by_conductor_group")
    @patch("l3gencfg.utils._GENCFG_API._raw_request")
    @tag("core")
    def test_ipv6_rs_groups(self, groups, contains, not_contains, gencfg_mock, conductor_mock, rt_mock):
        gencfg_mock.return_value = {
            "instances": [
                {
                    "hbf": {
                        "interfaces": {
                            "backbone": {
                                "hostname": "man1-8084-man-cloudapi-weather-ba-61e-17973.gencfg-c.yandex.net",
                                "ipv6addr": "2a02:6b8:c0b:24a4:10d:6c87:0:4635",
                            },
                        },
                    },
                },
                {
                    "hbf": {
                        "interfaces": {
                            "backbone": {
                                "hostname": "man1-6276-man-cloudapi-weather-ba-61e-17973.gencfg-c.yandex.net",
                                "ipv6addr": "2a02:6b8:c0b:e18:10d:6c87:0:4635",
                            },
                        },
                    },
                },
            ]
        }

        conductor_mock.return_value = [
            "mnt-myt.yandex.net",
            "mnt-sas.yandex.net",
        ]

        rt_mock.return_value = {
            "traffic_manage": {
                "vsconfig": "",
                "rsconfig": "",
                "servers": {
                    "mnt-myt.tt.yandex.net": {"port": None, "config": None},
                    "mnt-sas.tt.yandex.net": {"port": None, "config": None},
                },
            }
        }

        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c9"],
            [
                ("2a02:6b8:c00::/40", "MAN"),
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
                "groups": groups,
            },
        )
        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)

        for payload in contains:
            self.assertContains(r, payload)

        for payload in not_contains:
            self.assertNotContains(r, payload)

    @parameterized.expand(
        (
            (
                [
                    "@mtn:MAN_CLOUDAPI_WEATHER_BALANCER/stable-125-r1568",
                    "-man1-6276-man.gencfg-c.yandex.net=1.2.3.4",
                ],
                ["man1-8084-man.gencfg-c.yandex.net"],
                ["man1-6276-man.gencfg-c.yandex.net"],
            ),
            (
                ["%traffic_manage", "random-test-host.yandex.net=1.2.3.5"],
                ["random-test-host.yandex.net", "mnt-myt.yandex.net"],
                [],
            ),
            (
                [
                    "mnt-sas-focal.tt.yandex.net=93.158.158.83",
                    "mnt-myt.tt.yandex.net=77.88.1.115",
                    "-$traffic_manage",
                ],
                ["mnt-sas-focal.tt.yandex.net"],
                ["mnt-myt.tt.yandex.net", "mnt-sas.tt.yandex.net"],
            ),
        )
    )
    @patch("l3racktables.utils._RACKTABLES_API._read_json")
    @patch("l3conductor.utils.get_hosts_by_conductor_group")
    @patch("l3gencfg.utils._GENCFG_API._raw_request")
    @tag("core")
    def test_ipv4_rs_groups(self, groups, contains, not_contains, gencfg_mock, conductor_mock, rt_mock):
        gencfg_mock.return_value = {
            "instances": [
                {
                    "hbf": {
                        "interfaces": {
                            "backbone": {"hostname": "man1-8084-man.gencfg-c.yandex.net", "ipv4addr": "1.2.3.1"}
                        }
                    }
                },
                {
                    "hbf": {
                        "interfaces": {
                            "backbone": {"hostname": "man1-6276-man.gencfg-c.yandex.net", "ipv4addr": "1.2.3.4"}
                        }
                    }
                },
            ]
        }

        conductor_mock.return_value = ["mnt-myt.yandex.net", "mnt-sas.yandex.net"]

        rt_mock.return_value = {
            "traffic_manage": {
                "vsconfig": "",
                "rsconfig": "",
                "servers": {
                    "mnt-myt.tt.yandex.net": {"port": None, "config": None},
                    "mnt-sas.tt.yandex.net": {"port": None, "config": None},
                },
            }
        }

        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["77.88.88.77"],
            [
                ("77.88.1.0/24", "MAN"),
                ("93.158.158.0/24", "MAN"),
                ("1.2.3.0/24", "MAN"),
            ],
        )

        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "77.88.88.77",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": groups,
            },
        )
        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)

        for payload in contains:
            self.assertContains(r, payload)

        for payload in not_contains:
            self.assertNotContains(r, payload)

    @parameterized.expand(
        (
            (["@mtn:NON_EXIST_GENCFG_GROUP"], "Failed to resolve GenCfg group"),
            (["$non-exist-racktales-group"], "Invalid response format"),
            (["%non-exist-conductor-group"], "Conductor group not found"),
            (["non-exist-fqdn-real.yandex"], "Failed to resolve"),
        )
    )
    @patch("l3racktables.utils._RACKTABLES_API._read_json")
    @patch("l3conductor.utils.get_hosts_by_conductor_group")
    @patch("l3gencfg.utils._GENCFG_API._raw_request")
    @tag("core")
    def test_error_groups(self, groups, message, gencfg_mock, conductor_mock, rt_mock):
        gencfg_mock.side_effect = Mock(side_effect=GenCfgException("Failed to resolve GenCfg group"))
        conductor_mock.side_effect = Mock(side_effect=ConductorException("Conductor group not found"))
        rt_mock.side_effect = Mock(side_effect=RackTablesResponseFormatException("Invalid response format", "raw data"))

        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man-non-exist.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::9c9"],
            [
                ("2a02:6b8:c00::/40", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ],
        )

        r = user.post(
            "%s/vs" % svc["url"],
            {
                "ip": "2a02:6b8:0:3400:ffff::9c9",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": groups,
            },
        )
        self.assertEqual(400, r.status_code, r.content)
        self.assertContains(r, message, status_code=400)


class RSIDsDefinedTest(RESTAPITest):
    @tag("core")
    def test_skip_process_group_on_rsids(self):
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
        r = user.post(
            "%s/rs" % self.BASE_URL,
            {"ip": "2a02:6b8:b040:3100:ccc::4c9", "fqdn": "lbkp-man-009.search.yandex.net"},
        )
        self.assertEqual(201, r.status_code, r.content)

        rs_ids = [r.json()["object"]["id"]]
        group = ["-%traffic_manage", "mnt-myt.yandex.net", "mnt-sas.yandex.net"]

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
                "groups": group,
                "rs": rs_ids,
            },
        )

        r = user.get("%s/vs/%s" % (svc["url"], vs["id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertListEqual(r.json().get("group"), group)
        self.assertListEqual(r.json().get("rs"), rs_ids)

        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        self.assertContains(r, "lbkp-man-009.search.yandex.net")
        self.assertEqual(len(r.json().get("objects")), 1)

    @tag("core")
    def test_ignore_empty_rsids(self):
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

        group = ["mnt-myt.yandex.net", "mnt-sas.yandex.net"]
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
                "groups": group,
                "rs": [],
            },
        )

        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        self.assertContains(r, "mnt-myt.yandex.net")
        self.assertEqual(len(r.json().get("objects")), 2)


class RSTestConfig(RESTAPITest):
    @parameterized.expand(
        (
            ({"ip": "2a02:6b8:b040:3100:ccc::4c0", "fqdn": "2a02:6b8:b040:3100:ccc::4c0"}, {"WEIGHT": 1}),
            ({"ip": "2a02:6b8:b040:3100:ccc::4c1", "fqdn": "2a02:6b8:b040:3100:ccc::4c1", "config": ""}, {"WEIGHT": 1}),
            (
                {
                    "ip": "2a02:6b8:b040:3100:ccc::4c2",
                    "fqdn": "2a02:6b8:b040:3100:ccc::4c2",
                    "config-WEIGHT": "",
                },
                {"WEIGHT": 1},
            ),
            (
                {
                    "ip": "2a02:6b8:b040:3100:ccc::4c3",
                    "fqdn": "2a02:6b8:b040:3100:ccc::4c3",
                    "config-WEIGHT": 15,
                },
                {"WEIGHT": 15},
            ),
            (
                {
                    "ip": "2a02:6b8:b040:3100:ccc::4c3",
                    "fqdn": "2a02:6b8:b040:3100:ccc::4c3",
                    "config-WEIGHT": "1",
                },
                {"WEIGHT": 1},
            ),
        )
    )
    @tag("core")
    def test_create_rs(self, rs_desc, config):
        user = self._get_auth_client()
        r = user.post(f"{self.BASE_URL}/rs", rs_desc)
        self.assertEqual(201, r.status_code, r.content)
        obj = r.json()

        self.assertTrue("object" in obj, obj)
        self.assertTrue("id" in obj["object"], obj)

        r = user.get(f"{self.BASE_URL}/rs/{obj['object']['id']}")
        self.assertEqual(200, r.status_code, r.content)
        print(r.json())
        self.assertDictEqual(config, r.json().get("config", None))

    @tag("core")
    def test_error_rs(self):
        user = self._get_auth_client()
        r = user.post(
            f"{self.BASE_URL}/rs",
            {
                "ip": "2a02:6b8:b040:3100:ccc::4c0",
                "fqdn": "2a02:6b8:b040:3100:ccc::4c0",
                "config-WEIGHT": "non_digit",
            },
        )
        self.assertEqual(400, r.status_code, r.content)
        self.assertIn("Enter a whole number.", str(r.content))

    @parameterized.expand(
        (
            ("test-real-1.yandex.net=2a02:6b8:c01:300::1", {"WEIGHT": 1}),
            ("test-real-2.yandex.net=2a02:6b8:c01:300::2 weight=", {"WEIGHT": 1}),
            ("test-real-1.yandex.net=2a02:6b8:c01:300::1 weight=0", {"WEIGHT": 0}),
            ("test-real-3.yandex.net=2a02:6b8:c01:300::3 weight=13", {"WEIGHT": 13}),
        )
    )
    @tag("core")
    def test_groups_config(self, group, config):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c10"],
            [("2a02:6b8:c01:300::/56", "MAN")],
        )

        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4c10",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": lb["id"],
                "groups": (group),
            },
        )
        r = user.get("%s/rs?_all=true" % vs["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)

        obj = r.json()
        self.assertTrue(obj)

        rs = obj["objects"].pop()
        self.assertDictEqual(config, rs["config"])

    @parameterized.expand(
        (
            (("test-real-3.yandex.net=2a02:6b8:c01:300::3 weight=non-digit"), "Enter a whole number."),
            (
                ("test-real-3.yandex.net=2a02:6b8:c01:300::3 weight=-1"),
                "Ensure this value is greater than or equal to 0.",
            ),
        )
    )
    @tag("core")
    def test_error_groups_config(self, groups, error_message):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4c10"],
            [("2a02:6b8:c01:300::/56", "MAN")],
        )

        params = {
            "ip": "2a02:6b8:0:3400:ffff::4c10",
            "port": "80",
            "protocol": "TCP",
            "config-CHECK_URL": "/ping",
            "config-ANNOUNCE": True,
            "lb": lb["id"],
            "groups": groups,
        }
        r = user.post("%s/vs" % svc["url"], params)
        self.assertEqual(400, r.status_code, r.content)
        self.assertIn(error_message, str(r.content))
