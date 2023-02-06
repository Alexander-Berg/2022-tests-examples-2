from unittest.mock import patch

from django.http import JsonResponse
from django.test import override_settings, tag

from .base import RESTAPITest
import l3abc.services as l3abc_services
import l3abc.utils as l3abc_utils


class ABCTest(RESTAPITest):
    def _add_lb(self, client, abc, lb):
        r = client.post(
            "%s/balancer" % abc["url"],
            {"lb": lb["id"]},
        )
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        self.assertEqual(lb["id"], result["object"]["id"], result)
        lb_id = result["object"]["id"]
        # Get LB
        abc = self._get_abc(client, abc["code"])
        lbs = [lb for lb in abc["lb"] if lb["id"] == lb_id]
        self.assertEqual(1, len(lbs), lbs)
        return lbs[0]

    def _add_lbs(self, client, abc, lbs):
        return self._assign_lbs(client, abc["code"], [lb["id"] for lb in lbs])

    @tag("core")
    @override_settings(YAUTH_TEST_USER="ezhichek")
    def test_abc_list(self):
        user = self._get_auth_client()

        # Full list
        r = user.get("/api/v1/abc")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(20, len(objects["objects"]))

    @tag("core")
    @override_settings(YAUTH_TEST_USER="some-robot")
    def test_abc_list_empty(self):
        user = self._get_auth_client()

        # Limited list
        r = user.get("/api/v1/abc")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

    @tag("core")
    @override_settings(YAUTH_TEST_USER="ezhichek")
    def test_abc_create(self):
        user = self._get_auth_client()

        # Created ABC
        r = user.post(
            "/api/v1/abc",
            {"abc": "dostavkatraffika"},
        )
        self.assertEqual(403, r.status_code)

        # Get ABC
        self._get_abc(user, "dostavkatraffika")

    @tag("core")
    def test_abc_assign_ip(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        self.assertEqual(0, len(abc["ip"]))
        # Add IP
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(1, len(abc["ip"]), abc)

    @tag("core")
    @override_settings(YAUTH_TEST_USER="some-robot")
    def test_abc_assign_ip_forbidden(self):
        user = self._get_auth_client()
        abc = "dostavkatraffika"
        r = user.get("/api/v1/abc/%s" % abc)
        self.assertEqual(200, r.status_code, r.content)

        # Add IP
        r = user.post(
            "/api/v1/abc/%s/ip" % abc,
            {"ip": "2a02:6b8:0:3400:ffff::4c9"},
        )
        self.assertEqual(403, r.status_code, r.content)

    @tag("core")
    def test_abc_edit_ip(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        # Add IP
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        r = user.post(
            ip["url"],
            {"ip": "2a02:6b8:0:3400:ffff::4c9"},
        )
        self.assertEqual(403, r.status_code, r.content)

    @tag("core")
    def test_abc_assign_ip_unique(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        r = user.post(
            "%s/ip" % abc["url"],
            {"ip": "2a02:6b8:0:3400:ffff::4c9"},
        )
        self.assertEqual(400, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(1, len(abc["ip"]), abc)

    @tag("core")
    def test_abc_delete_ip(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        r = user.delete(ip["url"])
        self.assertEqual(204, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(0, len(abc["ip"]), abc)

    @tag("core")
    def test_abc_delete_ip_forbidden(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        with self.settings(YAUTH_TEST_USER="some-robot"):
            r = user.delete(ip["url"])
            self.assertEqual(403, r.status_code, r.content)
            r = user.get("/api/v1/abc/%s" % abc["code"])
            self.assertEqual(200, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(1, len(abc["ip"]), abc)

    @tag("core")
    @override_settings(YAUTH_TEST_USER="lb-user")
    def test_abc_delete_assigned_ip(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "Logbroker")
        self.assertEqual(0, len(abc["ip"]), abc)
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")
        abc = self._get_abc(user, "Logbroker")
        self.assertEqual(1, len(abc["ip"]), abc)
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        self._add_rt_net("2a02:6b8:c01:300::/56", "MAN")
        self._add_rt_net("2a02:6b8:b040:3100::/56", "MAN")
        self._add_rt_net("2a02:6b8:0:1482::/64", "MYT")
        self._add_rt_net("2a02:6b8:b010:31::/64", "SAS")
        abc = self._get_abc(user, "Logbroker")
        self.assertEqual(2, len(abc["ip"]), abc)
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": ip["ip"],
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        r = user.delete(ip["url"])
        self.assertEqual(403, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(2, len(abc["ip"]), abc)

    @tag("core")
    @override_settings(YAUTH_TEST_USER="lb-user")
    def test_abc_assign_lb(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        abc = self._get_abc(user, "dostavkatraffika")
        self.assertEqual(0, len(abc["lb"]))
        # Add IP
        lbl = self._add_lb(user, abc, lb)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(1, len(abc["lb"]), abc)

    @tag("core")
    def test_abc_assign_lb_forbidden(self):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        abc = self._get_abc(user, "dostavkatraffika")
        self.assertEqual(0, len(abc["lb"]))
        with self.settings(YAUTH_TEST_USER="some-robot"):
            # Add LB
            r = user.post(
                "%s/balancer" % abc["url"],
                {"lb": lb["id"]},
            )
            self.assertEqual(403, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(0, len(abc["lb"]), abc)

    @tag("core")
    def test_abc_assign_lb_multiple(self):
        user = self._get_auth_client()
        lb1 = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb2 = self._prepare_balancer(user, "man1-lb2a.yndx.net")
        lb3 = self._prepare_balancer(user, "man1-lb2c.yndx.net")
        abc = self._get_abc(user, "dostavkatraffika")
        self.assertEqual(0, len(abc["lb"]))
        with self.settings(YAUTH_TEST_USER="some-robot"):
            # Add LBs
            r = user.post(
                "%s/assignlbs" % abc["url"],
                {"lb": [lb["id"] for lb in [lb1, lb2, lb3]]},
            )
            self.assertEqual(403, r.status_code, r.content)

    @tag("core")
    def test_abc_assign_lb_multiple_forbidden(self):
        user = self._get_auth_client()
        lb1 = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb2 = self._prepare_balancer(user, "man1-lb2a.yndx.net")
        lb3 = self._prepare_balancer(user, "man1-lb2c.yndx.net")
        abc = self._get_abc(user, "dostavkatraffika")
        self.assertEqual(0, len(abc["lb"]))
        # Add LBs
        abc = self._add_lbs(user, abc, [lb1, lb2, lb3])
        # Modify LBs
        abc = self._add_lbs(user, abc, [lb2, lb3])
        abc = self._add_lbs(user, abc, [lb1, lb2])

    @tag("core")
    def test_abc_assign_lb_unique(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb = self._add_lb(user, abc, lb)
        r = user.post(
            "%s/balancer" % abc["url"],
            {"lb": lb["id"]},
        )
        self.assertEqual(400, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(1, len(abc["lb"]), abc)

    @tag("core")
    def test_abc_delete_lb(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "dostavkatraffika")
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb = self._add_lb(user, abc, lb)
        r = user.delete("%s/balancer/%s" % (abc["url"], lb["id"]))
        self.assertEqual(204, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(0, len(abc["lb"]), abc)

    @tag("core")
    def test_abc_delete_assigned_lb(self):
        user = self._get_auth_client()
        abc = self._get_abc(user, "Logbroker")
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb = self._add_lb(user, abc, lb)
        ip = self._add_ip(user, abc, "2a02:6b8:0:3400:ffff::4c9")
        self._add_rt_net("2a02:6b8:c01:300::/56", "MAN")
        self._add_rt_net("2a02:6b8:b040:3100::/56", "MAN")
        self._add_rt_net("2a02:6b8:0:1482::/64", "MYT")
        self._add_rt_net("2a02:6b8:b010:31::/64", "SAS")
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")
        vs = self._prepare_vs(
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
        r = user.delete("%s/balancer/%s" % (abc["url"], lb["id"]))
        self.assertEqual(204, r.status_code, r.content)
        # Get ABC
        abc = self._get_abc(user, abc["code"])
        self.assertEqual(0, len(abc["lb"]), abc)


class ABCInheritLBsTestCase(RESTAPITest):
    @tag("core")
    def test_inherit_success(self):
        client = self._get_auth_client()
        with patch("l3abc.utils._ABC_API") as abc_api_mock:
            abc = self._get_abc(client, "dostavkatraffika")
            abc_api_mock.fetch_services.return_value = [
                l3abc_services.ABCServiceInfo(11011, "root_child", abc["id"]),
            ]
            self.assertTrue(l3abc_utils.pull_abc_service_info())

        lb = self._prepare_balancer(client, "man1-lb2b.yndx.net")
        abc = self._get_abc(client, "dostavkatraffika")
        lb = self._assign_lbs(client, abc["code"], [lb["id"]])

        abc = self._get_abc(client, "root_child")
        r = client.post("%s/inheritlbs" % abc["url"])
        self.assertContains(r, "1 balancer's allocations have been created", status_code=201)

        r = client.post("%s/inheritlbs" % abc["url"])
        self.assertEqual(200, r.status_code, r.content)

    @tag("core")
    def test_inherit_empty(self):
        with patch("l3abc.utils._ABC_API") as abc_api_mock:
            abc_api_mock.fetch_services.return_value = [
                l3abc_services.ABCServiceInfo(11002, "another_root_service", None),
                l3abc_services.ABCServiceInfo(11012, "another_root_child", 11002),
            ]
            self.assertTrue(l3abc_utils.pull_abc_service_info(force=True))

        client = self._get_auth_client()
        abc = self._get_abc(client, "another_root_child")
        r = client.post("%s/inheritlbs" % abc["url"])
        self.assertContains(r, "Could not found balancers among service parents", status_code=404)

    @tag("core")
    def test_inherit_no_abc(self):
        client = self._get_auth_client()
        r = client.post("/api/v1/abc/non_exist_abc/inheritlbs")
        self.assertEqual(404, r.status_code, r.content)
        self.assertEqual("No abc service found matching the query", r.json()["message"])
