from django.http import JsonResponse
from django.test import tag
from parameterized import parameterized

from .base import RESTAPITest
from .. import models, tasks


class LBTest(RESTAPITest):
    @tag("core")
    def test_balancer_list(self):
        user = self._get_auth_client()

        # Empty list
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(0, len(objects["objects"]))

        reference_load_balancer_fqdn = "man1-lb2b.yndx.net"
        reference_load_balancer_dict = {
            "abc_count": 0,
            "fqdn": reference_load_balancer_fqdn,
            "full": False,
            "location": [],
            "name": "man1-lb2b",
            "state": "ACTIVE",
            "sticky": False,
            "test_env": False,
            "visible": True,
        }

        # Create balancer
        lb = self._prepare_balancer(user, reference_load_balancer_fqdn)
        lb_id = lb["id"]
        reference_load_balancer_dict["url"] = f"/api/v1/balancer/{lb_id}"
        reference_load_balancer_dict["id"] = lb_id

        # List created balancer
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))
        api_load_balancer = objects["objects"][0]

        self.assertDictEqual(reference_load_balancer_dict, api_load_balancer)

    @tag("core")
    def test_balancer_list_perms(self):
        user = self._get_auth_client()

        # Create balancer
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")

        # tvt have no access to dostavkatraffika
        with self.settings(YAUTH_TEST_USER="tvt"):
            # Empty list
            r = user.get("/api/v1/balancer")
            self.assertEqual(200, r.status_code)
            self.assertTrue(isinstance(r, JsonResponse))
            objects = r.json()
            self.assertTrue(isinstance(objects, dict))
            self.assertTrue("objects" in objects)
            self.assertEqual(0, len(objects["objects"]), objects)

        self._assign_lbs(user, "dostavkatraffika", [lb["id"]])

        # tvt have no access to dostavkatraffika
        with self.settings(YAUTH_TEST_USER="tvt"):
            # Empty list
            r = user.get("/api/v1/balancer")
            self.assertEqual(200, r.status_code)
            self.assertTrue(isinstance(r, JsonResponse))
            objects = r.json()
            self.assertTrue(isinstance(objects, dict))
            self.assertTrue("objects" in objects)
            self.assertEqual(0, len(objects["objects"]), objects)

    @tag("core")
    def test_balancer_unique(self):
        user = self._get_auth_client()

        # Create balancer
        lb = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        # Validate uniq balancer
        r = user.post(
            "/api/v1/balancer",
            {
                "fqdn": "man1-lb2b.yndx.net",
            },
        )
        self.assertEqual(400, r.status_code)
        # List balancer
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(1, len(objects["objects"]))

    @tag("core")
    def test_balancer_more(self):
        user = self._get_auth_client()

        # Create balancers
        lb1 = self._prepare_balancer(user, "man1-lb1b.yndx.net")
        lb2 = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        # List balancers
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))
        # One more
        lb3 = self._prepare_balancer(user, "man1-lb3b.yndx.net")
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(3, len(objects["objects"]))

    @tag("core")
    def test_balancer_remove(self):
        user = self._get_auth_client()

        # Create balancers
        lb1 = self._prepare_balancer(user, "man1-lb1b.yndx.net")
        lb2 = self._prepare_balancer(user, "man1-lb2b.yndx.net")
        lb3 = self._prepare_balancer(user, "man1-lb3b.yndx.net")
        # List balancers
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(3, len(objects["objects"]))
        # Remove
        r = user.delete(lb2["url"])
        self.assertEqual(204, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        # List balancers
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        objects = r.json()
        self.assertTrue(isinstance(objects, dict))
        self.assertTrue("objects" in objects)
        self.assertEqual(2, len(objects["objects"]))
        # Check removed
        r = user.get(lb2["url"])
        self.assertEqual(404, r.status_code)

    @tag("core")
    def test_balancer_remove_assigned(self):
        user = self._get_auth_client()

        lb1 = self._prepare_balancer(user, "man1-lb1b.yndx.net", ["Logbroker"])
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
                "lb": lb1["id"],
                "groups": "%traffic_manage\n" "lbkp-man-009.search.yandex.net",
            },
        )
        self.assertEqual(1, len(vs["lb"]), vs)
        # List balancer
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), r.content)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(1, len(objects["objects"]), objects)
        # Remove
        r = user.delete(lb1["url"])
        self.assertEqual(403, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        # List balancers
        r = user.get("/api/v1/balancer")
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        objects = r.json()
        self.assertTrue(isinstance(objects, dict), r.content)
        self.assertTrue("objects" in objects, objects)
        self.assertEqual(1, len(objects["objects"]), objects)
        # Check removed
        r = user.get(lb1["url"])
        self.assertEqual(200, r.status_code, r.content)


class BalancerModeTest(RESTAPITest):
    def test_update_request_active_mode(self):
        user = self._get_auth_client()
        lb_object = self._prepare_balancer(user, "man1-lb1b.yndx.net", ["Logbroker"])
        lb = models.LoadBalancer.objects.get(pk=lb_object["id"])

        self.assertEqual(models.LoadBalancer.ModeChoices.ACTIVE, lb.mode)

        tasks.schedule_lb_update_request(lb.id, None)
        self.assertTrue(models.LoadBalancerConfigurationUpdateRequest.objects.filter(balancer_id=lb.id).exists())

    @parameterized.expand(
        (
            models.LoadBalancer.ModeChoices.IDLE,
            models.LoadBalancer.ModeChoices.DISABLED,
        ),
    )
    def test_update_request_inactive_mode(self, mode):
        user = self._get_auth_client()
        lb_object = self._prepare_balancer(user, "man1-lb1b.yndx.net", ["Logbroker"])
        lb = models.LoadBalancer.objects.get(pk=lb_object["id"])
        lb.mode = mode
        lb.save()

        self.assertEqual(mode, lb.mode)
        tasks.schedule_lb_update_request(lb.id, None)

        request_qs = models.LoadBalancerConfigurationUpdateRequest.objects.filter(balancer_id=lb.id)
        self.assertFalse(request_qs.exists())

    @parameterized.expand(
        (
            models.LoadBalancer.ModeChoices.ACTIVE,
            models.LoadBalancer.ModeChoices.IDLE,
        ),
    )
    def test_vs_balancer_non_disabled(self, mode):
        user = self._get_auth_client()

        lb_object = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"], ["MAN"])
        lb = models.LoadBalancer.objects.get(pk=lb_object["id"])
        lb.mode = mode
        lb.save()

        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4d0"],
            [("2a02:6b8:b040:3100::/64", "MAN")],
        )
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4d0",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "groups": "2a02:6b8:b040:3100::ffff",
            },
        )

        cfg = self.prepare_config_presentation(svc, vs)
        vs_balancers = cfg.presentations.last().balancers

        self.assertGreater(len(vs_balancers), 0)
        self.assertIn(lb.pk, vs_balancers)

    def test_vs_balancer_disabled(self):
        user = self._get_auth_client()

        lb_object = self._prepare_balancer(user, "man1-lb2b.yndx.net", ["Logbroker"], ["MAN"])
        models.LoadBalancer.objects.filter(pk=lb_object["id"]).update(mode=models.LoadBalancer.ModeChoices.DISABLED)

        svc = self._prepare_service(
            user,
            "lbk-man.logbroker-prestable.yandex.net",
            "Logbroker",
            ["2a02:6b8:0:3400:ffff::4d0"],
            [("2a02:6b8:b040:3100::/64", "MAN")],
        )
        vs = self._prepare_vs(
            user,
            svc,
            {
                "ip": "2a02:6b8:0:3400:ffff::4d0",
                "port": "80",
                "protocol": "TCP",
                "config-CHECK_URL": "/ping",
                "config-ANNOUNCE": True,
                "groups": "2a02:6b8:b040:3100::ffff",
            },
        )

        cfg = self.prepare_config_presentation(svc, vs)
        self.assertFalse(cfg.presentations.exists())

    def prepare_config_presentation(self, svc, *vss) -> models.Configuration:
        user = self._get_auth_client()

        c = self._prepare_config(user, svc, vss)
        cfg = models.Configuration.objects.get(pk=c["id"])
        cfg.create_presentations()

        return cfg
