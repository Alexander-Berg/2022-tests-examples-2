import itertools
import random
import socket
import string
import typing
import unittest
from unittest.mock import patch

import django.db.utils as db_utils
from django.test import tag, TestCase
from parameterized import parameterized

from l3common.typing import alias
from . import base
from . import test_fields
from .. import models
from .. import utils


class ConfigBindtoTest(base.RESTAPITest):
    def setUp(self):
        super().setUp()

        self.service = models.Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        self.lb = models.LoadBalancer.objects.create(
            fqdn="man1-lb2b.yndx.net",
            location=[models.LocationNetwork.LOCATION_CHOICES.MAN],
            state=models.LoadBalancer.STATE_CHOICES.ACTIVE,
        )
        models.LoadBalancerAccess.objects.create(balancer=self.lb, abc=self.service.abc)

        self.rs = models.RealServer.objects.create(
            fqdn="mnt-myt.yandex.net",
            ip="2a02:6b8:0:1482::115",
            location=[models.LocationNetwork.LOCATION_CHOICES.MAN],
        )

        self.vs = models.VirtualServer.objects.create(
            service_id=self.service.id,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port=80,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            rs_ids=[self.rs.id],
            config=test_fields.make_config(),
        )

    def assert_render_with_expected_ip(self, expected_ip) -> None:

        from django.template.backends import jinja2

        key = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

        with patch.object(jinja2.Template, "render") as render_mock:

            def side_effect(context=None, _=None):
                self.assertEqual(expected_ip, context["lb"].ip)
                return key

            render_mock.side_effect = side_effect

            with patch("l3mgr.utils.get_ip", autospec=True, return_value=expected_ip):
                config = models.Configuration.objects.create(service=self.service, vs_ids=[self.vs.id])
                config.create_presentations()
                _, output = next(config.generator(lb_id=self.lb.id))

            render_mock.assert_called_once()
            self.assertEqual(key, output)

    @parameterized.expand(
        (
            ("2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:e00::1a"),
            ("1.1.1.1", "2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:e00::1a"),
            ("2a02:6b8:0:3400:ffff::4c9", "1.1.1.1", "141.8.136.155"),
            ("2a02:6b8:0:3400:ffff::4c9", None, "2a02:6b8:0:e00::1a"),
            ("1.1.1.1", None, "141.8.136.155"),
        )
    )
    @tag("core")
    def test_config_bindto(self, vs_ip: str, connect_ip: str, expected_ip: str) -> None:
        if connect_ip:
            self.vs.config["CONNECT_IP"] = connect_ip
        self.vs.ip = vs_ip
        self.vs.save()
        self.assert_render_with_expected_ip(expected_ip)

    @parameterized.expand(
        (
            ("2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:e00::1a"),
            ("1.1.1.1", "2a02:6b8:0:3400:ffff::4c9", "2a02:6b8:0:e00::1a"),
            ("2a02:6b8:0:3400:ffff::4c9", "1.1.1.1", "141.8.136.155"),
            ("2a02:6b8:0:3400:ffff::4c9", None, "2a02:6b8:0:e00::1a"),
            ("1.1.1.1", None, "141.8.136.155"),
        )
    )
    @tag("core")
    def test_rss_fwmark_config_bindto(self, vs_ip: str, connect_ip: str, expected_ip: str) -> None:
        self.rss = [
            models.RealServerState.objects.create(
                balancer_id=self.lb.id,
                vs_id=self.vs.id,
                server=self.rs,
                fwmark=1001,
                state=models.RealServerState.STATE_CHOICES.ACTIVE,
            )
        ]

        if connect_ip:
            self.vs.config["CONNECT_IP"] = connect_ip
        self.vs.ip = vs_ip
        self.vs.save()

        with patch.object(models.VirtualServer, "get_states_for_lb", return_value=self.rss):
            self.assert_render_with_expected_ip(expected_ip)


class ConfigExceptionTestCase(TestCase):
    def setUp(self):
        try:
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET)
            socket.getaddrinfo("ya.ru", 80, socket.AF_INET6)
        except Exception as e:
            raise unittest.SkipTest(f"Internet connection isn't available: {e}")
        super().setUp()
        self.service = models.Service.objects.create(fqdn="lbk-man.logbroker-prestable.yandex.net", abc="Logbroker")
        self.lb = models.LoadBalancer.objects.create(
            fqdn="amazon.com", location=[models.LocationNetwork.LOCATION_CHOICES.VLA]
        )
        models.LoadBalancerAccess.objects.create(abc=self.service.abc, balancer=self.lb)
        self.rs = models.RealServer.objects.create(
            fqdn="mnt-myt.yandex.net", ip="2a02:6b8:0:1482::115", location=[models.LocationNetwork.LOCATION_CHOICES.VLA]
        )
        self.vs = models.VirtualServer.objects.create(
            service_id=self.service.id,
            ip="2a02:6b8:0:3400:ffff::4c9",
            port=80,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            rs_ids=[self.rs.id],
            config=test_fields.make_config(SCHEDULER="wrr"),
        )
        self.config: models.Configuration = models.Configuration.objects.create(
            service=self.service, vs_ids=[self.vs.id]
        )
        self.rss = [
            models.RealServerState.objects.create(
                balancer_id=self.lb.id,
                vs_id=self.vs.id,
                server=self.rs,
                fwmark=1001,
                state=models.RealServerState.STATE_CHOICES.ACTIVE,
            )
        ]
        self.config.create_presentations()

    def test_noIPs_exception(self):
        with (self.assertRaises(utils.NoIPsException)):
            next(self.config.generator(lb_id=self.lb.id))
        logged: models.TaskLog = (
            models.TaskLog.objects.filter(lb=self.lb, config=self.config).order_by("timestamp").last()
        )
        self.assertTrue(logged.description.startswith("No suitable ip was found."))

    def test_ManyIPs_exception(self):
        self.vs.ip = "141.8.136.155"
        self.vs.save()
        with (self.assertRaises(utils.ManyIPsException)):
            next(self.config.generator(lb_id=self.lb.id))
        logged: models.TaskLog = (
            models.TaskLog.objects.filter(lb=self.lb, config=self.config).order_by("timestamp").last()
        )
        self.assertTrue(logged.description.startswith("There are many ips."))


class ConfigurationValidationTest(TestCase):
    def test_blank_fields_validation(self):
        config = models.Configuration()
        with self.assertRaises(db_utils.IntegrityError) as validation_exception:
            config.save()
        self.assertIn(
            'null value in column "service_id" violates not-null constraint', validation_exception.exception.args[0]
        )

    def test_save_default_values(self):
        svc = models.Service.objects.create(abc="test", fqdn="test.yndx.net")
        config = models.Configuration(service=svc)
        config.save()
        self.assertEqual("", config.comment)
        self.assertEqual([], config.vs_ids)
        self.assertEqual([], config.history)

    def test_comment_format_validation(self):
        svc = models.Service.objects.create(abc="test", fqdn="test.yndx.net")
        config = models.Configuration(service=svc)
        config.comment = "Initial\r\ncomment"
        config.save()
        self.assertEqual(config.comment, "Initial\r\ncomment")
        self.assertEqual([], config.vs_ids)
        self.assertEqual([], config.history)


class ConfigGetUpdatedHistoryTest(TestCase):
    def test_get_updated_history(self):
        n = 4  # value less than default for max_history_length
        svc = models.Service.objects.create(abc="test", fqdn="test.yndx.net")
        svc.options.max_history_length = n
        models.Configuration.objects.bulk_create(models.Configuration(service=svc) for i in range(n))
        cfg: models.Configuration = models.Configuration.objects.create(service=svc)
        # cfg.history was empty so cleaned_history returns [cfg.id]
        self.assertListEqual([cfg.id], cfg.cleaned_history)
        old_cfg_ids = sorted(models.Configuration.objects.exclude(pk=cfg.id).values_list("pk", flat=True))
        # make sure that cleaned_history further will return list shorter than max_history_length
        self.assertLessEqual(len(old_cfg_ids), cfg.service.options.max_history_length)
        cfg.history = old_cfg_ids.copy()[:-2]
        # take all the ids (since len(cfg.history) < n) and add cfg.id in the end
        self.assertListEqual(cfg.history + [cfg.id], cfg.cleaned_history)
        cfg.history = old_cfg_ids.copy()
        # take n-1 last ids and add cfg.id in the end
        self.assertListEqual(cfg.history[1:] + [cfg.id], cfg.cleaned_history)
        models.Configuration.objects.exclude(pk=cfg.id).order_by("pk").last().delete()
        # take n-1 last ids, remove deleted one and add cfg.id in the end
        self.assertListEqual(cfg.history[1:-1] + [cfg.id], cfg.cleaned_history)

        d = 1
        svc.options.max_history_length = n - d
        # take n-d-1 last ids, remove deleted one and add cfg.id in the end
        self.assertListEqual(cfg.history[1 + d : -1] + [cfg.id], cfg.cleaned_history)  #
        models.Configuration.objects.exclude(pk=cfg.id).order_by("pk").first().delete()
        # id of Configuration deleted at previous step wouldn't be in n-d-1 last ids anyway so nothing changed in result
        self.assertListEqual(cfg.history[1 + d : -1] + [cfg.id], cfg.cleaned_history)
        models.Configuration.objects.exclude(pk=cfg.id).order_by("pk").last().delete()
        # take n-d-1 last ids, remove deleted ones and add cfg.id in the end
        self.assertListEqual(cfg.history[1 + d : -2] + [cfg.id], cfg.cleaned_history)


class BalancersSelectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.service: models.Service = models.Service.objects.create(fqdn="test.localhost", abc="dostavkatraffika")

        cls.regions: typing.Dict[
            models.LocationRegion.REGION_CHOICES, typing.List[models.LocationNetwork.LOCATION_CHOICES]
        ] = {r.code: sorted(r.location) for r in models.LocationRegion.objects.all()}

        locations: typing.List[models.LocationNetwork.LOCATION_CHOICES] = sorted(
            itertools.chain.from_iterable(cls.regions.values())
        )

        cls.rss: typing.Dict[models.LocationNetwork.LOCATION_CHOICES, models.RealServer] = {
            r.location[0]: r
            for r in models.RealServer.objects.bulk_create(
                [
                    models.RealServer(
                        fqdn=f"{location.lower()}-{idx}.yandex.net",
                        ip=f"2a02:6b8:0:1482::{idx}",
                        config={},
                        location=[location],
                    )
                    for idx, location in enumerate(locations)
                ]
            )
        }

        cls.lbs: typing.Dict[models.LocationRegion.REGION_CHOICES, models.LoadBalancer] = {
            r.code: models.LoadBalancer(
                fqdn=f"{r.code}.yndx.net",
                location=r.location,
                state=models.LoadBalancer.STATE_CHOICES.ACTIVE,
            )
            for r in models.LocationRegion.objects.all()
        }
        models.LoadBalancer.objects.bulk_create(cls.lbs.values())

    def setUp(self) -> None:
        self.vss: typing.List[models.VirtualServer] = []

    def make_vs(self, *args: models.LocationNetwork.LOCATION_CHOICES, **kwargs) -> models.VirtualServer:
        self.assertGreater(len(args), 0)
        idx: int = len(self.vss)
        vs: models.VirtualServer = models.VirtualServer.objects.create(
            service=self.service,
            ip=f"2a02:6b8:b040:3100:ccc::{idx}",
            port=idx,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            config=test_fields.make_config(ANNOUNCE=True, **kwargs),
            rs_ids=[self.rss[location].id for location in args],
        )
        self.vss.append(vs)
        return vs

    def test_without_access_or_previous(self) -> None:
        vs = self.make_vs(models.LocationNetwork.LOCATION_CHOICES.MAN, models.LocationNetwork.LOCATION_CHOICES.VLA)
        balancers: typing.List[models.LoadBalancer] = list(vs.balancers)
        self.assertEqual(0, len(balancers))

    def test_without_previous(self) -> None:
        codes = (models.LocationRegion.REGION_CHOICES.VLA, models.LocationRegion.REGION_CHOICES.MSK)
        models.LoadBalancerAccess.objects.bulk_create(
            [models.LoadBalancerAccess(balancer=self.lbs[r], abc=self.service.abc) for r in codes]
        )
        with alias(models.LocationNetwork.LOCATION_CHOICES) as L:
            vs = self.make_vs(L.MAN, L.VLA, L.SAS)
        balancers: typing.List[models.LoadBalancer] = list(vs.balancers)
        self.assertEqual(2, len(balancers))
        self.assertSetEqual(
            set(tuple(b.location) for b in balancers),
            set(tuple(r.location) for r in models.LocationRegion.objects.filter(code__in=codes)),
        )

    def test_dc_filtered_mixed(self) -> None:
        def single(values: typing.List[int]) -> int:
            self.assertEqual(1, len(values))
            return values[0]

        with alias(models.LocationNetwork.LOCATION_CHOICES) as L:
            lbs: typing.Dict[L, models.LoadBalancer] = {
                location: models.LoadBalancer(
                    fqdn=f"{location}.yndx.net", location=[location], state=models.LoadBalancer.STATE_CHOICES.ACTIVE
                )
                for location in [L.SAS, L.IVA]
            }
            models.LoadBalancer.objects.bulk_create(lbs.values())

            models.LoadBalancerAccess.objects.bulk_create(
                [models.LoadBalancerAccess(balancer=lb, abc=self.service.abc) for lb in lbs.values()]
            )

            vs_regional: models.VirtualServer = self.make_vs(L.IVA, L.SAS)
            vs_locational: models.VirtualServer = self.make_vs(L.IVA, L.SAS, DC_FILTER=True)

            config: models.Configuration = models.Configuration.objects.create(
                service=self.service, vs_ids=[vs_regional.id, vs_locational.id]
            )

            prepared_presentations = config.prepare_presentations()
            presentations: typing.Dict[int, models.ConfigurationPresentation] = {
                single(p.balancers): p for p in prepared_presentations
            }
            self.assertEqual(2, len(presentations))

            sas_data: typing.Dict[int, models.ConfigurationPresentation.VirtualServerConfiguration] = presentations[
                lbs[L.SAS].id
            ].data
            self.assertEqual(2, len(sas_data))
            self.assertSetEqual(set(sas_data[vs_regional.id]["rs_ids"]), {self.rss[L.IVA].id, self.rss[L.SAS].id})
            self.assertEqual(sas_data[vs_locational.id]["rs_ids"], [self.rss[L.SAS].id])

            iva_data: typing.Dict[int, models.ConfigurationPresentation.VirtualServerConfiguration] = presentations[
                lbs[L.IVA].id
            ].data
            self.assertEqual(2, len(iva_data))
            self.assertSetEqual(set(iva_data[vs_regional.id]["rs_ids"]), {self.rss[L.IVA].id, self.rss[L.SAS].id})
            self.assertEqual(iva_data[vs_locational.id]["rs_ids"], [self.rss[L.IVA].id])
