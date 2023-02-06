import ipaddress
import typing
from unittest.mock import patch

from django.core.cache import DEFAULT_CACHE_ALIAS
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.test import override_settings, tag
from parameterized import parameterized

from l3common.tests.cases import override_celery_settings

from .base import RESTAPITest
from .. import models
from ..fields import OptionsField, Options
from ..models import Service
from ..utils.throttling import ServiceOperationsThrottle


class SVCTest(RESTAPITest):
    @tag("core")
    def test_service_list(self):
        user = self._get_auth_client()

        # Empty list
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

        # Create service
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")

        # List created service
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

    def _get_objects(self, data):
        user = self._get_auth_client()

        r = user.get("/api/v1/service", data=data)
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        parsed_response = r.json()
        self.assertIsInstance(parsed_response, dict)
        self.assertIn("objects", parsed_response)
        objects = parsed_response["objects"]
        self.assertIsInstance(objects, list)

        return objects

    @tag("core")
    def test_service_search_by_ip(self):
        user = self._get_auth_client()

        query_params = {"archive": False, "_full": True, "_search": "123.45.0.5"}

        objects = self._get_objects(data=query_params)
        self.assertEqual(0, len(objects))

        data = [
            (
                "lbk-man.logbroker-prestable.yandex.net",
                "Logbroker",
                ["123.45.0.5", "234.43.78.109", "2001:0db8:85a3::8a2e:0370:7334", "2001:db8::1:0:0:1"],
            ),
            (
                "l3.tt.yandex-team.ru",
                "dostavkatraffika",
                ["154.22.234.2", "34.90.78.209", "fe80::01ff:fe23:4567:890a", "f374::1:33:54:41"],
            ),
        ]

        for fqdn, abc, ips in data:
            svc = self._prepare_service(user, fqdn, abc, ips)
            for ip in ips:
                self._prepare_vs(user, svc, {"ip": ip, "port": "323", "protocol": "UDP"})

        for fqdn, abc, ips in data:
            for ip in ips:
                query_params["_search"] = ip
                objects = self._get_objects(data=query_params)
                self.assertLess(0, len(objects))
                objects = map(lambda obj: (obj["fqdn"], obj["abc"]), objects)
                self.assertIn((fqdn, abc), objects)

    @tag("core")
    def test_service_list_perms(self):
        user = self._get_auth_client()
        # Create service
        svc = self._prepare_service(user, "l3mgr-test.slb.yandex.net", "dostavkatraffika")
        # Unknown user
        with self.settings(YAUTH_TEST_USER="unknown"):
            # List created service
            r = user.get("/api/v1/service")
            self.assertEqual(200, r.status_code)
            self.assertTrue(isinstance(r, JsonResponse))
            objects = r.json()
            self.assertTrue(isinstance(objects, dict))
            self.assertTrue("objects" in objects)
            self.assertEqual(0, len(objects["objects"]))
            # Get created service
            r = user.get(svc["url"])
            self.assertEqual(200, r.status_code)
        # tvt have no access to dostavkatraffika
        with self.settings(YAUTH_TEST_USER="tvt"):
            # List created service
            r = user.get("/api/v1/service")
            self.assertEqual(200, r.status_code, r.content)
            self.assertTrue(isinstance(r, JsonResponse), r.content)
            objects = r.json()
            self.assertTrue(isinstance(objects, dict), objects)
            self.assertTrue("objects" in objects, objects)
            self.assertEqual(0, len(objects["objects"]), objects)
            # Get created service
            r = user.get(svc["url"])
            self.assertEqual(200, r.status_code, r.content)
            self.assertTrue(isinstance(r, JsonResponse), r.content)
            obj = r.json()
            self.assertTrue(isinstance(obj, dict), obj)
            self.assertTrue("id" in obj, obj)
            self.assertEqual(svc["id"], obj["id"], obj)

    @tag("core")
    def test_service_unique(self):
        user = self._get_auth_client()
        svc = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")

        # Validate uniq service
        r = user.post(
            "/api/v1/service",
            {
                "fqdn": "lbk-man.logbroker-prestable.yandex.net",
                "abc": "Logbroker",
            },
        )
        self.assertEqual(400, r.status_code)
        r = user.post(
            "/api/v1/service",
            {
                "fqdn": "lbk-man.logbroker-prestable.yandex.net",
                "abc": "Logbroker2",
            },
        )
        self.assertEqual(400, r.status_code)
        # List service
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))
        # Add one more
        svc = self._prepare_service(user, "lbk-man.logbroker.yandex.net", "Logbroker")
        # List service
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))

    @tag("core")
    def test_service_delete(self):
        user = self._get_auth_client()
        svc1 = self._prepare_service(user, "lbk-man.logbroker-prestable.yandex.net", "Logbroker")
        svc2 = self._prepare_service(user, "lbk-man.logbroker.yandex.net", "Logbroker")
        # List both services
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))
        # Remove
        r = user.delete(svc1["url"])
        self.assertEqual(204, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        # List service
        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

    @tag("core")
    def test_service_delete_forbidden(self):
        user = self._get_auth_client()
        svc1 = self._prepare_service(user, "l3mgr-test.slb.yandex.net", "dostavkatraffika")
        svc2 = self._prepare_service(user, "lbk-man.logbroker.yandex.net", "Logbroker")
        # Unknown user
        with self.settings(YAUTH_TEST_USER="unknown"):
            # Remove
            r = user.delete(svc1["url"])
            self.assertEqual(403, r.status_code, r.content)
            r = user.delete(svc2["url"])
            self.assertEqual(403, r.status_code, r.content)
        # tvt have no access to dostavkatraffika
        with self.settings(YAUTH_TEST_USER="tvt"):
            # List one service
            r = user.get("/api/v1/service")
            self.assertEqual(200, r.status_code, r.content)
            self.assertTrue(isinstance(r, JsonResponse), r.content)
            objects = r.json()
            self.assertTrue(isinstance(objects, dict), objects)
            self.assertTrue("objects" in objects, objects)
            self.assertEqual(0, len(objects["objects"]), objects)
            # Remove
            r = user.delete(svc1["url"])
            self.assertEqual(403, r.status_code, r.content)
            r = user.delete(svc2["url"])
            self.assertEqual(403, r.status_code, r.content)

    @tag("core")
    def test_service_assigned_delete(self):
        user = self._get_auth_client()
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
                "lb": [],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        # Remove
        r: HttpResponse = user.delete(svc["url"])
        self.assertEqual(403, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        # List service
        r: HttpResponse = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

    @tag("core")
    @override_settings(VALIDATE_VS_CONFIG_FOR_EDITRS=True)
    def test_vs_update_rs(self):
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
                "config-WEIGHT_DC_MAN": "nodisable",
                "config-WEIGHT_LB123": "100",
                "lb": lb["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )

        # Prepare config
        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        # test vs config form should clean incorrect data in db
        vs_db: models.VirtualServer = models.VirtualServer.objects.get(pk=vs["id"])
        self.assertEqual(1, vs_db.config["CHECK_RETRY"])
        self.assertEqual("nodisable", vs_db.config["WEIGHT_DC_MAN"])
        self.assertEqual(100, vs_db.config["WEIGHT_LB123"])
        self.assertTrue(vs_db.config["ANNOUNCE"])
        vs_db.config["CHECK_RETRY"] = None
        vs_db.config["CONNECT_IP"] = None
        vs_db.config["CONNECT_PORT"] = None
        vs_db.save(update_fields=("config",))

        # Update vs by ext_id
        r: HttpResponse = user.post(
            "%s/editrs" % svc["url"],
            {"groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net"},
        )
        self.assertEqual(201, r.status_code, r.content.decode("utf-8"))
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        c_id = result["object"]["id"]
        self.assertNotEqual(c["id"], c_id, result)

        # Check old config
        c = self.assert_response(user.get(c["url"]))
        self.assertEqual("ACTIVE", c["state"], c)

        # Get C
        obj = self.assert_response(user.get(f"{svc['url']}/config/{c_id}"))
        self.assertEqual(c_id, obj["id"], obj)
        self.assertEqual("NEW", obj["state"], obj)
        self.assertTrue(c["id"] not in obj["history"], obj)

        self.assertEqual(1, len(obj["vs_id"]))
        self.assertNotEqual(vs_db.id, obj["vs_id"][0])
        vs_db = models.VirtualServer.objects.get(pk=obj["vs_id"][0])
        self.assertEqual(1, vs_db.config["CHECK_RETRY"])
        self.assertEqual(vs_db.ip, vs_db.config["CONNECT_IP"])
        self.assertEqual(vs_db.port, vs_db.config["CONNECT_PORT"])
        self.assertEqual("nodisable", vs_db.config["WEIGHT_DC_MAN"])
        self.assertEqual(100, vs_db.config["WEIGHT_LB123"])
        self.assertTrue(vs_db.config["ANNOUNCE"])

        obj = self._deploy_config(user, obj)
        obj = self._activate_config(user, obj)

        # Check old config
        c = self.assert_response(user.get(c["url"]))
        self.assertEqual("INACTIVE", c["state"], c)

    def assert_response(self, r: HttpResponse) -> dict:
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c = r.json()
        self.assertTrue(isinstance(c, dict), c)
        self.assertTrue("id" in c, c)
        return c

    @parameterized.expand(
        [
            ({},),
            ({"subject": "rifler"},),
            ({"subject": "home"},),
            ({"permission": "yes"},),
            ({"permission": "l3mgr.yes"},),
            ({"permission": "l3mgr.editrs_service"},),
            ({"subject": "rifler", "permission": "yes"},),
            ({"subject": "rifler", "permission": "l3mgr.yes"},),
            ({"subject": "rifler", "permission": "l3mgr.editrs_service"},),
            ({"subject": "home", "permission": "yes"},),
            ({"subject": "home", "permission": "l3mgr.yes"},),
            ({"subject": "home", "permission": "l3mgr.editrs_service"},),
        ]
    )
    @tag("core")
    def test_check_fail_with_args(self, kwargs):
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
        required = {"subject": "home", "permission": "l3mgr.editrs_service"}
        successful = required == kwargs
        r = user.post("%s/role" % svc["url"], kwargs)
        self.assertEqual(201 if successful else 400, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertEqual("errors" in result, not successful, result)
        if successful:
            self.assertTrue("object" in result, result)
            self.assertTrue("id" in result["object"], result)
        else:
            for key, value in required.items():
                self.assertEqual(key in result["errors"], kwargs.get(key) != value, result)

    @tag("core")
    def test_svc_permission(self):
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

        r = user.get("%s/role" % svc["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(0, len(objects["objects"]), objects)

        # Add permission
        r = user.post("%s/role" % svc["url"], {"subject": "home", "permission": "l3mgr.editrs_service"})
        self.assertEqual(201, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        role = result["object"]

        r = user.post("%s/role" % svc["url"], {"subject": "home", "permission": "l3mgr.editrs_service"})
        self.assertEqual(400, r.status_code, r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("errors" in result, result)

        # Check role exists
        r = user.get("%s/role" % svc["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(1, len(objects["objects"]), objects)

        r = user.get("%s/role/%s" % (svc["url"], role["id"]))
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        role = r.json()
        self.assertTrue(isinstance(role, dict), role)
        self.assertTrue("id" in role, role)
        self.assertTrue("url" in role, role)

        # Delete role
        r = user.delete(role["url"])
        self.assertEqual(204, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse))

        # Check role does not exist
        r = user.get("%s/role" % svc["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), objects)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(0, len(objects["objects"]), objects)


class SVCMetadataTest(RESTAPITest):
    TEST_OWNER = "awacs"

    @tag("core")
    def test_short_json(self):
        """
        Show JSON service view don't show "meta" field.
        """

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man-meta-short.logbroker-prestable.yandex.net",
            "Logbroker",
            meta={"OWNER": self.TEST_OWNER},
        )

        r = user.get("/api/v1/service")
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)

        objects = r.json()
        self.assertIsInstance(objects, dict)
        self.assertIn("objects", objects)
        self.assertEqual(1, len(objects["objects"]))

        svc = objects["objects"].pop()
        self.assertIsNone(svc.get("meta"))

    @tag("core")
    def test_detailed_json(self):
        """
        Show JSON service view don't show "meta" field.
        """

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man-meta-detailed.logbroker-prestable.yandex.net",
            "Logbroker",
            meta={"OWNER": self.TEST_OWNER},
        )

        r = user.get("/api/v1/service/%s" % svc["id"])
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)

        service = r.json()
        self.assertIsInstance(service, dict)
        self.assertIn("meta", service)
        self.assertEqual(self.TEST_OWNER, service.get("meta").get("OWNER"))
        self.assertIsNone(service.get("meta").get("LINK", not None))

    @parameterized.expand(
        [
            ({"OWNER": "awacs"}, {"OWNER": "awacs", "LINK": None, "LOCKED": False}),
            ({"OWNER": "", "LOCKED": ""}, {"OWNER": None, "LINK": None, "LOCKED": False}),
            ({"OWNER": 0}, {"OWNER": "0", "LINK": None, "LOCKED": False}),
            ({"LINK": "www.yandex.ru", "LOCKED": False}, {"OWNER": None, "LINK": "www.yandex.ru", "LOCKED": False}),
            (
                {"OWNER": "awacs", "LINK": "www.yandex.ru", "LOCKED": True},
                {"OWNER": "awacs", "LINK": "www.yandex.ru", "LOCKED": True},
            ),
        ]
    )
    @tag("core")
    def test_svc_editmeta(self, received, expected):
        user = self._get_auth_client()
        svc = self._prepare_service(user, "lbk-man-editmeta.logbroker-prestable.yandex.net", "Logbroker")

        r = user.get(f"/api/v1/service/{svc['id']}")
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        self.assertDictEqual(r.json().get("meta"), {"OWNER": None, "LINK": None, "LOCKED": False})

        r = user.post(f"{svc['url']}/editmeta", received)
        self.assertEqual(200, r.status_code)
        r = user.get(f"/api/v1/service/{svc['id']}")
        self.assertEqual(200, r.status_code)
        self.assertIsInstance(r, JsonResponse)
        self.assertDictEqual(r.json().get("meta"), expected)


class SVCRateLimitFieldTest(RESTAPITest):
    @tag("core")
    def test_short_json(self):
        """
        Check rate_limit field doesn't show up in the API response
        """

        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man-meta-detailed.logbroker-prestable.yandex.net",
            "Logbroker",
        )

        throttler = ServiceOperationsThrottle(svc["id"])
        throttler.set_rate_limit(100, 1000)

        response = user.get("/api/v1/service")

        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.json()["objects"].pop().get("rate_limit"))

        response = user.get("/api/v1/service/%s" % svc["id"])

        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.json().get("rate_limit"))

        throttler.reset_rate_limit()


class SVCOptionsTest(RESTAPITest):
    @tag("core")
    def test_options_behaviour(self):
        user = self._get_auth_client()
        svc = self._prepare_service(
            user,
            "lbk-man-option-service.logbroker-prestable.yandex.net",
            "Logbroker",
        )

        service: Service = Service.objects.get(pk=svc["id"])
        default_options: Options = OptionsField.default()
        self.assertDictEqual(default_options, service.options)  # initial state of service.options

        service.options.safe_set("remove_states_history", None)
        self.assertDictEqual(default_options, service.options)  # can't store None, state is the same
        service.options.remove_states_history = None
        self.assertDictEqual(default_options, service.options)  # can't store None, state is the same
        self.assertIsNone(service.options.get("remove_states_history"))  # real value
        self.assertFalse(service.options.remove_states_history)  # default value

        expected_options: dict = default_options.copy()
        for state, stored_state in {True: True, False: False, "True": True, "False": False}.items():
            expected_options.update(remove_states_history=stored_state)
            service.options.safe_set("remove_states_history", state)
            self.assertEqual(expected_options, service.options)  # can store this state
            service.options.remove_states_history = state
            self.assertEqual(expected_options, service.options)  # state is the same
            self.assertEqual(stored_state, service.options.get("remove_states_history"))  # real value
            self.assertEqual(stored_state, service.options.remove_states_history)  # also real value, because not None

        service.options.safe_set("remove_states_history", None)
        self.assertDictEqual(default_options, service.options)  # value removed
        service.options.remove_states_history = True
        self.assertTrue(service.options.remove_states_history)  # value added
        service.options.remove_states_history = None
        self.assertDictEqual(default_options, service.options)  # value removed

        with self.assertRaises(ValidationError):
            service.options.remove_states_history = ""
        with self.assertRaises(ValidationError):
            service.options.safe_set("remove_states_history", "")


def _get_vs_description(lb: models.LoadBalancer, ip_address: str) -> typing.Dict[str, typing.Any]:
    return {
        "ip": ip_address,
        "port": "80",
        "protocol": "TCP",
        "config-ANNOUNCE": True,
        "lb": lb["id"],
        "groups": "lbkp-man-009.search.yandex.net=2a02:6b8:c01:300::1",
    }


@override_settings(
    CACHES={DEFAULT_CACHE_ALIAS: {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
    PGAAS_IAM_TOKEN_STORAGE_CACHE=DEFAULT_CACHE_ALIAS,
)
class SVCIPOperationsTest(RESTAPITest):
    @tag("core")
    @patch("l3mgr.utils._tools.resolve_dns", autospec=True, return_value=[])
    def test_release_ip(self, _fake_resolve):
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man-used-ip-service.logbroker-prestable.yandex.net",
            "Logbroker",
            None,
            [("2a02:6b8:c01:300::/56", "MAN")],
        )

        response = user.post("/api/v1/abc/Logbroker/getip")
        self.assertEqual(200, response.status_code)

        ip_address = response.json()["object"]
        self.assertIsInstance(ipaddress.ip_address(ip_address), ipaddress.IPv6Address)

        # use received IPaddress
        self._prepare_vs(
            user,
            svc,
            {
                "ip": ip_address,
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "config-WEIGHT_DC_MAN": "nodisable",
                "config-WEIGHT_LB123": "100",
                "lb": lb["id"],
                "groups": "lbkp-man-009.search.yandex.net=2a02:6b8:c01:300::1",
            },
        )

        # get new IP
        response = user.post("/api/v1/abc/Logbroker/getip")
        self.assertEqual(200, response.status_code)
        new_ip_address = response.json()["object"]
        self.assertIsInstance(ipaddress.ip_address(new_ip_address), ipaddress.IPv6Address)
        self.assertNotEqual(new_ip_address, ip_address)

        # hide service
        c = self._prepare_config(user, svc, [])
        self._activate_config(user, c)
        r = user.post(f"{svc['url']}/hide", {})
        self.assertEqual(200, r.status_code, r.content)

        # and try to get old services IP instead new
        response = user.post("/api/v1/abc/Logbroker/getip")
        self.assertEqual(200, response.status_code)
        new_ip_address = response.json()["object"]
        self.assertEqual(new_ip_address, ip_address)

    @tag("core")
    @patch("l3mgr.utils._tools.resolve_dns", autospec=True, return_value=[])
    def test_intersection_ip_dns_cleared(self, _fake_resolve):
        """
        Func checks that busy address cause error
        and that after release IP it can be used again
        by another service.
        """
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man-used-ip-service.logbroker-prestable.yandex.net",
            "Logbroker",
            None,
            [("2a02:6b8:c01:300::/56", "MAN")],
        )

        response = user.post("/api/v1/abc/Logbroker/getip")
        self.assertEqual(200, response.status_code)

        ip_address = response.json()["object"]
        self.assertIsInstance(ipaddress.ip_address(ip_address), ipaddress.IPv6Address)

        # use received IPaddress
        vs = self._prepare_vs(user, svc, _get_vs_description(lb, ip_address))
        c = self._prepare_config(user, svc, [vs])
        self._activate_config(user, c)

        # use received IPaddress with new service
        svc_new = self._prepare_service(
            user,
            "lbk-man-intersection-ip-service.logbroker-prestable.yandex.net",
            "Logbroker",
        )

        with self.assertRaisesRegex(AssertionError, "IP already in use by VS"):
            self._prepare_vs(user, svc_new, _get_vs_description(lb, ip_address))

        # hide service
        c = self._prepare_config(user, svc, [])
        self._activate_config(user, c)
        r = user.post(f"{svc['url']}/hide", {})
        self.assertEqual(200, r.status_code, r.content)

        # second try to use released IP
        _vs = self._prepare_vs(user, svc_new, _get_vs_description(lb, ip_address))

    @tag("core")
    @patch("l3mgr.utils._tools.resolve_dns", autospec=True, return_value=[])
    def test_intersection_ip_dns_non_cleared(self, fake_resolve):
        """
        Func checks that busy address cause error
        and that after release IP it can be used again
        by another service.
        """
        user = self._get_auth_client()
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "lbk-man-used-ip-service.logbroker-prestable.yandex.net",
            "Logbroker",
            None,
            [("2a02:6b8:c01:300::/56", "MAN")],
        )

        response = user.post("/api/v1/abc/Logbroker/getip")
        self.assertEqual(200, response.status_code)

        ip_address = response.json()["object"]
        self.assertIsInstance(ipaddress.ip_address(ip_address), ipaddress.IPv6Address)

        # use received IPaddress
        vs = self._prepare_vs(user, svc, _get_vs_description(lb, ip_address))
        c = self._prepare_config(user, svc, [vs])
        self._activate_config(user, c)

        # use received IPaddress with new service
        svc_new = self._prepare_service(
            user,
            "lbk-man-intersection-ip-service.logbroker-prestable.yandex.net",
            "Logbroker",
        )

        with self.assertRaisesRegex(AssertionError, "IP already in use by VS"):
            self._prepare_vs(user, svc_new, _get_vs_description(lb, ip_address))

        # hide service - Fails due to fact that dns record still exists - we add `ip_address`
        fake_resolve.return_value = ["2a02:6b8:0:3400:0:2a7:0:5", ip_address]
        c = self._prepare_config(user, svc, [])
        self._activate_config(user, c)
        r = user.post(f"{svc['url']}/hide", {})

        self.assertContains(r, "You should delete A/AAAA DNS records referred to", status_code=400)

        ip_address = response.json()["object"]

        self.assertIsInstance(ipaddress.ip_address(ip_address), ipaddress.IPv6Address)

        # use received IPaddress
        _vs = self._prepare_vs(user, svc, _get_vs_description(lb, ip_address))

        with self.assertRaisesRegex(AssertionError, "IP already in use by VS"):
            self._prepare_vs(user, svc_new, _get_vs_description(lb, ip_address))

        # We simulate DNS cleanup - current ip address is absent. After that - we successfully hide
        fake_resolve.return_value = ["2a02:6b8:0:3400:0:2a7:0:5"]
        c = self._prepare_config(user, svc, [])
        self._activate_config(user, c)
        r = user.post(f"{svc['url']}/hide", {})
        self.assertEqual(200, r.status_code, r.content)

        # second try to use released IP - works fine after DNS clean up
        _vs = self._prepare_vs(user, svc_new, _get_vs_description(lb, ip_address))


class ServiceHideTest(RESTAPITest):
    @override_celery_settings(task_always_eager=True)
    def test_hide_empty_config(self):
        """Validate calls and status after successful /hide."""
        user = self._get_auth_client()
        _ = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "test-hide-empty-config.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:fffe::e1a1"],
            [("2a02:6b8:b010:31::/64", "MAN")],
        )

        # Prepare config with empty VSs
        c = self._prepare_config(user, svc, [])
        c = self._activate_config(user, c)

        r = user.get(c["url"]).json()
        self.assertEqual(models.Configuration.STATE_CHOICES.ACTIVE, r["state"], r)

        with patch(
            "l3mgr.utils.tasks.commit_svn_configuration", autospec=True, return_value=None
        ) as _svn_commit, patch(
            "l3mgr.utils.firewall.upload_fw", autospec=True, return_value=None
        ) as _upload_fw, patch(
            "l3rtsync.utils.sync", autospec=True, side_effect=lambda l: (l, [])
        ) as _l3rtsync:

            r = user.post(f"{svc['url']}/hide", {})
            self.assertEqual(200, r.status_code, r.content)

            _svn_commit.assert_called_once()
            _upload_fw.assert_called_once()
            _l3rtsync.assert_called_once()

        r = user.get(c["url"]).json()
        self.assertEqual(models.Configuration.STATE_CHOICES.ACTIVE, r["state"], r)

    def test_hide_config_forbidden(self):
        """
        Service should be disabled first before /hide" events,
        because it contains deployed config with VSs.
        """
        user = self._get_auth_client()
        _ = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"])
        svc = self._prepare_service(
            user,
            "test-hide-nonempty-config.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:fffe::e1a2"],
            [("2a02:6b8:b010:31::/64", "MAN")],
        )
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:fffe::e1a2",
                "port": "80",
                "protocol": "TCP",
                "config-ANNOUNCE": True,
                "groups": "2a02:6b8:b010:31::e1a2",
            },
        )

        c = self._prepare_config(user, svc, [vs])
        c = self._deploy_config(user, c)
        c = self._activate_config(user, c)

        r = user.post(f"{svc['url']}/hide", {})
        self.assertEqual(403, r.status_code, r.content)
