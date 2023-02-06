import logging
import typing
from ipaddress import IPv4Address, ip_address
from random import randrange
from unittest.mock import patch

import dns
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.test import Client, TestCase, override_settings, TransactionTestCase, SimpleTestCase

from .. import models
from ..tasks import _success_config, change_config_state

_AUTH_TEST_MIDDLEWARE = "django_yauth.middleware.YandexAuthTestMiddleware"
_AUTH_MIDDLEWARE = "django_yauth.middleware.YandexAuthMiddleware"

logger: logging.Logger = logging.getLogger(__name__)


def resolve_by_type_mock_side_effect():
    def resolve_by_type(fqdn, query_type, tcp=False):
        class _Fake_answer:
            def __init__(self, _fqdn):
                self.fqdn = _fqdn

            def to_text(self):
                return self.fqdn

        if query_type not in (dns.rdatatype.A, dns.rdatatype.AAAA):
            raise ValueError("query_type must be dns.rdatatype.A or dns.rdatatype.AAAA.")
        known = {
            "any3-lb-check.yndx.net": (None, ["2a02:6b8:0:3400:ccc::4c9"]),
            "any4-lb-check.yndx.net": (None, ["2a02:6b8:0:3400:ccc::4cA"]),
            "lbkp-man-009.search.yandex.net": (None, ["2a02:6b8:b040:3100:ccc::4c9"]),
            "mnt-myt.yandex.net": (["77.88.1.115"], ["2a02:6b8:0:1482::115"]),
            "mnt-sas.yandex.net": (["93.158.158.87"], ["2a02:6b8:b010:31::233"]),
            "man1-lb2b.yndx.net": (["141.8.136.155"], ["2a02:6b8:0:e00::1a"]),
            "myt2-lb2b.yndx.net": (["141.8.136.151"], ["2a02:6b8:0:e00::11"]),
            "google.com": (None, ["2a00:1450:4010:c05::65", "2a00:1450:4010:c05::64"]),
        }.get(fqdn, (None, None))[0 if query_type == dns.rdatatype.A else 1]
        if known:
            return [_Fake_answer(k) for k in known]
        try:
            if type(ip_address(fqdn)) is IPv4Address:
                if query_type == dns.rdatatype.A:
                    return [_Fake_answer(fqdn)]
            elif query_type == dns.rdatatype.AAAA:
                return [_Fake_answer(fqdn)]
        except ValueError:
            pass
        return []

    return resolve_by_type


class RESTAPITestCaseMixin(SimpleTestCase):
    BASE_URL = "/api/v1"

    _patchers = [
        patch("l3racktables.utils._RACKTABLES_API.get_vs", return_value=None, autospec=True),
        patch(
            "l3conductor.utils.get_hosts_by_conductor_group",
            return_value=["mnt-myt.yandex.net", "mnt-sas.yandex.net"],
            autospec=True,
        ),
        patch("l3mgr.utils.resolve_by_type", side_effect=resolve_by_type_mock_side_effect(), autospec=True),
        patch("l3mgr.utils._tools.resolve_by_type", side_effect=resolve_by_type_mock_side_effect(), autospec=True),
        patch("l3mgr.utils._tools.reverse_dns", return_value=[], autospec=True),
    ]

    @classmethod
    def setUpTestData(cls):
        try:
            parent_setup = super().setUpTestData
        except AttributeError:
            pass
        else:
            parent_setup()

        from l3abc.models import ABCMember, ABCService

        for abc_svc in [
            {"abc_slug": "portal", "abc_id": 1},
            {"abc_slug": "home", "abc_id": 2},
            {"abc_slug": "wwwyaru", "abc_id": 3},
            {"abc_slug": "home5", "abc_id": 4},
            {"abc_slug": "home3", "abc_id": 5},
            {"abc_slug": "mobile", "abc_id": 6},
            {"abc_slug": "mobile2", "abc_id": 7},
            {"abc_slug": "phonedetect", "abc_id": 8},
            {"abc_slug": "apiopredeljalkidetektor", "abc_id": 9},
            {"abc_slug": "wapconverter", "abc_id": 10},
            {"abc_slug": "mobileyandex", "abc_id": 11},
            {"abc_slug": "supportwgts", "abc_id": 12},
            {"abc_slug": "obshheportalnyetexnologiiijelementy", "abc_id": 13},
            {"abc_slug": "passp", "abc_id": 14},
            {"abc_slug": "moiservisy", "abc_id": 15},
            {"abc_slug": "lbs", "abc_id": 16},
            {"abc_slug": "tanker", "abc_id": 17},
            {"abc_slug": "keyboard", "abc_id": 18},
            {"abc_slug": "operapanel", "abc_id": 19},
            {"abc_slug": "stat", "abc_id": 20},
            {"abc_slug": "oops", "abc_id": 609},
            {"abc_slug": "QLOUD", "abc_id": 741},
            {"abc_slug": "net", "abc_id": 922},
            {"abc_slug": "dostavkatraffika", "abc_id": 1192},
            {"abc_slug": "srertc", "abc_id": 3389},
            {"abc_slug": "drug", "abc_id": 3494},
            {"abc_slug": "qyp_personal", "abc_id": 4172},
            {"abc_slug": "ydeploybetatesting", "abc_id": 4298},
            {"abc_slug": "Logbroker", "abc_id": 679},
        ]:
            ABCService.objects.create(**abc_svc)

        # creating child service
        logbroker = ABCService.objects.get(abc_id=679)
        logbroker_child = ABCService.objects.create(abc_slug="logbroker_child", abc_id=889, parent=logbroker)
        ABCService.objects.create(abc_slug="logbroker_grandchild", abc_id=8899, parent=logbroker_child)

        ABCMember.objects.bulk_create(
            [
                ABCMember(**v)
                for v in [
                    {
                        "person": "ezhichek",
                        "abc_id": 1,
                        "role_abc_id": 16,
                        "service_slug": "dostavkatraffika",
                        "admin": True,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 2,
                        "role_abc_id": 16,
                        "service_slug": "qyp_personal",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 3,
                        "role_abc_id": 16,
                        "service_slug": "net",
                        "admin": True,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 4,
                        "role_abc_id": 16,
                        "service_slug": "drug",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 5,
                        "role_abc_id": 16,
                        "service_slug": "srertc",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 6,
                        "role_abc_id": 16,
                        "service_slug": "home",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 7,
                        "role_abc_id": 16,
                        "service_slug": "lbs",
                        "admin": True,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 8,
                        "role_abc_id": 16,
                        "service_slug": "passp",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 9,
                        "role_abc_id": 16,
                        "service_slug": "mobile",
                        "admin": False,
                    },
                    {
                        "person": "ezhichek",
                        "abc_id": 10,
                        "role_abc_id": 16,
                        "service_slug": "portal",
                        "admin": False,
                    },
                    {
                        "person": "lb-user",
                        "abc_id": 11,
                        "role_abc_id": 700,
                        "service_slug": "Logbroker",
                        "admin": True,
                    },
                    {
                        "person": "lb-user",
                        "abc_id": 12,
                        "role_abc_id": 700,
                        "service_slug": "dostavkatraffika",
                        "admin": True,
                    },
                ]
            ]
        )

    def setUp(self):
        super().setUp()
        try:
            for patcher in self._patchers:
                patcher.start()
        except:
            self.tearDown()
            raise

    def tearDown(self):
        try:
            for patcher in reversed(self._patchers):
                patcher.stop()
        finally:
            super().tearDown()

    def _get_auth_client(self) -> Client:
        # TODO: authenticate
        return Client()

    def _prepare_balancer(
        self,
        client,
        fqdn: str,
        abcs: typing.Optional[typing.List[str]] = None,
        locations: typing.Optional[typing.List[str]] = None,
        testing: bool = False,
        region: typing.Optional[str] = None,
    ):
        abcs = [] if abcs is None else abcs
        locations = {} if locations is None else locations

        # Add balancer
        balancer_data = {"fqdn": fqdn, "state": "ACTIVE", "visible": True}
        if locations:
            balancer_data["location"] = list(locations)
        if region:
            balancer_data.setdefault("location", []).extend(models.LocationRegion.objects.get(code=region).location)
        if testing:
            balancer_data["test_env"] = True
        r = client.post("/api/v1/balancer", balancer_data)
        lb_id = self.assert_object_response(r)
        location = r.get("Location", None)
        self.assertNotEqual(None, location, r.content)
        # Get balancer
        r = client.get(location)
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        lb = r.json()
        self.assertTrue(isinstance(lb, dict), lb)
        self.assertTrue("id" in lb, lb)
        self.assertEqual(lb_id, lb["id"], lb)
        # Assign to abcs
        for abc in abcs:
            r = client.post("/api/v1/abc/%s/balancer" % abc, {"lb": lb_id})
            self.assertEqual(201, r.status_code, r.content)
        return lb

    def assert_object_response(self, r):
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        return result["object"]["id"]

    def _get_abc(self, client, abc):
        r = client.get("/api/v1/abc/%s" % abc)
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        obj = r.json()
        self.assertTrue(isinstance(obj, dict), obj)
        self.assertTrue("code" in obj, obj)
        self.assertEqual(abc, obj["code"], obj)
        self.assertTrue(isinstance(obj["ip"], list), obj)
        self.assertTrue(isinstance(obj["lb"], list), obj)
        return obj

    def _assign_lbs(self, client, abc_code, lb_ids):
        r = client.post("/api/v1/abc/%s/assignlbs" % abc_code, {"lb": lb_ids})
        self.assertEqual(202, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        # Get LB
        abc = self._get_abc(client, abc_code)
        self.assertEqual(len(abc["lb"]), len(lb_ids), abc)
        return abc

    def _service_builder(self):
        class ServiceBuilder:
            fqdn = "lbk-man.logbroker-prestable.yandex.net"
            abc = "Logbroker"
            ips = ["2a02:6b8:0:3400:ffff::4c9"]
            nets = [
                ("2a02:6b8:c01:300::/56", "MAN"),
                ("2a02:6b8:b040:3100::/56", "MAN"),
                ("2a02:6b8:0:1482::/64", "MYT"),
                ("2a02:6b8:b010:31::/64", "SAS"),
            ]

            def __init__(self, test):
                self._test = test

            def with_fqdn(self, fqdn):
                self.fqdn = fqdn
                return self

            def with_abc(self, abc):
                self.abc = abc
                return self

            def with_ips(self, ips):
                self.ips = ips
                return ips

            def with_nets(self, nets):
                self.nets = nets
                return nets

            def build(self, client):
                return self._test._prepare_service(client, self.fqdn, self.abc, self.ips, self.nets)

        return ServiceBuilder(self)

    def _prepare_service(self, client, fqdn, abc, ips=None, nets=None, meta=None):
        ips = [] if ips is None else ips
        nets = [] if nets is None else nets
        meta = {} if meta is None else meta

        post_payload = {"fqdn": fqdn, "abc": abc}
        post_payload.update({f"meta-{key}": value for key, value in meta.items()})

        # Add service
        r = client.post("/api/v1/service", post_payload)
        self.assertEqual(201, r.status_code, r.content)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), r.content)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)
        self.assertTrue("object" in result, result)
        self.assertTrue("id" in result["object"], result)
        svc_id = result["object"]["id"]
        # Get service
        r = client.get(location)
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        svc = r.json()
        self.assertTrue(isinstance(svc, dict), r.content)
        self.assertTrue("id" in svc, svc)
        self.assertEqual(svc_id, svc["id"], svc)
        # Prepare IPs
        if len(ips) > 0:
            abc = self._get_abc(client, svc["abc"])
            for ip in ips:
                self._add_ip(client, abc, ip)
        for net in nets:
            self._add_rt_net(ip=net[0], location=net[1])
        return svc

    def _add_ip(self, client, abc, ip):
        r = client.post("/api/v1/network", {"ip": ip, "external": False})
        self.assertEqual(201, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        result = r.json()
        self.assertTrue(isinstance(result, dict), result)
        self.assertTrue("result" in result, result)
        self.assertEqual("OK", result["result"], result)

        r = client.post("%s/ip" % abc["url"], {"ip": ip})
        ip_id = self.assert_object_response(r)
        # Get IP
        abc = self._get_abc(client, abc["code"])
        ips = [ip for ip in abc["ip"] if ip["id"] == ip_id]
        self.assertEqual(1, len(ips), ips)
        return ips[0]

    def _add_net(self, client, net):
        r = client.post("/api/v1/network", {"ip": net[0], "location": net[1]})
        return self.assert_object_response(r)

    def _add_rt_net(self, ip: str, location: str) -> None:
        models.LocationNetwork(
            ip=ip, location=[location], source=models.LocationNetwork.SOURCE_CHOICES.RACKTABLES
        ).save()

    def _prepare_vs(self, client, svc, params) -> dict:
        # Add VS
        r = client.post("%s/vs" % svc["url"], params)
        self.assertEqual(201, r.status_code, r.content)
        vs_id = self.assert_object_response(r)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        # Get VS
        r = client.get(location)
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        vs = r.json()
        self.assertTrue(isinstance(vs, dict))
        self.assertTrue("id" in vs)
        self.assertEqual(vs_id, vs["id"])
        return vs

    def _prepare_config(self, client, svc, vss):
        # Add C
        config_data = {"vs": [vs["id"] for vs in vss], "comment": "test config"}
        r = client.post(f"{svc['url']}/config", config_data)
        c_id = self.assert_object_response(r)
        location = r.get("Location", None)
        self.assertNotEqual(None, location)
        # Get C
        r = client.get(location)
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        c = r.json()
        self.assertTrue(isinstance(c, dict))
        self.assertTrue("id" in c)
        self.assertEqual(c_id, c["id"])
        return c

    def _deploy_config(self, client, c, target_state=models.Configuration.STATE_CHOICES.TESTING):
        change_config_state(c["id"], models.Configuration.STATE_CHOICES.NEW, target_state)
        # Get C
        r = client.get(c["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        c = r.json()
        self.assertTrue(isinstance(c, dict))
        self.assertTrue("id" in c)
        self.assertTrue("state" in c)
        self.assertEqual(target_state, c["state"])
        return c

    def _show_config(self, client, c):
        # Get C
        r = client.get(c["url"])
        self.assertEqual(200, r.status_code, r.content)
        self.assertTrue(isinstance(r, JsonResponse), r.content)
        c = r.json()
        self.assertTrue(isinstance(c, dict), c)
        self.assertTrue("url" in c, c)

        # create presentation without deploy
        models.Configuration.objects.get(id=c["id"]).create_presentations()

        r = client.post("%s/show" % c["url"])
        self.assertEqual(
            200,
            r.status_code,
            r.streaming_content if r.streaming_content else r.content,
        )
        self.assertTrue(
            isinstance(r, StreamingHttpResponse),
            r.streaming_content if r.streaming_content else r.content,
        )
        return r.streaming_content

    def _show_config_chunks(self, client, c) -> typing.List[typing.Tuple[typing.ByteString, typing.ByteString]]:
        """
        Returns a list of (keeplived_config, config_path) pairs
        """
        result = []

        parts = list(self._show_config(client, c))

        while parts:
            result += [(parts.pop(), parts.pop())]

        return result

    def _activate_config(self, client, c: dict, announced_lbs: typing.Optional[typing.Iterable[int]] = None) -> dict:
        _success_config(c["id"], models.Configuration.STATE_CHOICES.ACTIVE)
        cfg = models.Configuration.objects.get(pk=c["id"])
        self.assertEquals(models.Configuration.STATE_CHOICES.ACTIVE, cfg.state)
        if announced_lbs:
            lb_ids = list(announced_lbs)
            configuration = models.Configuration.objects.get(pk=c["id"])
            # required to create VirtualServerState
            rendered_configs = [list(configuration.generator(lb_id)) for lb_id in lb_ids]
            update_states_count = models.VirtualServerState.objects.filter(
                balancer_id__in=lb_ids,
                vs_id__in=configuration.vs_ids,
            ).update(state=models.VirtualServerState.STATE_CHOICES.ANNOUNCED)
            self.assertEquals(len(lb_ids), update_states_count)

        # Get C
        r = client.get(c["url"])
        self.assertEqual(200, r.status_code)
        self.assertTrue(isinstance(r, JsonResponse))
        c = r.json()
        self.assertTrue(isinstance(c, dict))
        self.assertTrue("id" in c)
        self.assertTrue("state" in c)
        self.assertEqual("ACTIVE", c["state"])
        return c

    def _make_rs_state(self, rs_ip: str, vs_id: int, lb_id: int, state: str) -> models.RealServerState:
        rs = models.RealServer.objects.filter(ip=rs_ip).first()
        return models.RealServerState.objects.create(
            balancer_id=lb_id, vs_id=vs_id, server=rs, fwmark=randrange(1000, 10000, 100), state=state
        )


@override_settings(
    YAUTH_TEST_USER="ezhichek",
    MIDDLEWARE=[(_AUTH_TEST_MIDDLEWARE if mc == _AUTH_MIDDLEWARE else mc) for mc in settings.MIDDLEWARE],
)
class RESTAPITest(RESTAPITestCaseMixin, TestCase):
    pass


@override_settings(
    YAUTH_TEST_USER="ezhichek",
    MIDDLEWARE=[(_AUTH_TEST_MIDDLEWARE if mc == _AUTH_MIDDLEWARE else mc) for mc in settings.MIDDLEWARE],
)
class RESTAPITransactionTestCase(RESTAPITestCaseMixin, TransactionTestCase):
    def _fixture_setup(self):
        # this hack is used to refill db with data set in migrations because in TransactionTestCase all data is truncated after test
        try:
            from django.db import connection
            from django.apps import apps
            import l3mgr.migrations

            with connection.schema_editor() as schema_editor:
                getattr(l3mgr.migrations, "0021_auto_20170504_0653").fill_regions(apps, schema_editor)
                getattr(l3mgr.migrations, "0067_auto_20220505_1221").change_regions(apps, schema_editor)
        except:
            pass

        self.setUpTestData()
        super()._fixture_setup()
