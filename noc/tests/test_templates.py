import difflib
import os
from unittest import SkipTest

from django.template import loader
from django.test import SimpleTestCase

from l3common import utils as common_utils
from ..forms import VSConfigForm
from ..models import (
    LoadBalancer,
    Service,
    RealServer,
    RealServerState,
    VirtualServer,
    LocationNetwork,
)
from ..utils import is_IPv6


class BaseDefaultTCPServiceTest(SimpleTestCase):
    template_name: str = "keepalived.conf"
    rendered_filename: str

    def setUp(self):
        self.lb = LoadBalancer(
            **{
                "id": 567,
                "state": LoadBalancer.STATE_CHOICES.ACTIVE,
                "full": False,
                "fqdn": "sas1-1lb7a.yndx.net",
                "test_env": False,
                "sticky": True,
                "location": [LocationNetwork.LOCATION_CHOICES.SAS],
            }
        )
        self.lb.ip = "2a02:6b8:0:1a00::1b7a"

        self.service = Service(
            **{"id": 137, "archive": False, "abc": "dostavkatraffika", "fqdn": "l3.tt.yandex-team.ru"}
        )

        self.vs = VirtualServer(
            **{
                "id": 1069929,
                "service_id": 137,
                "rs_ids": [1554, 1555],
                "groups": ["%traffic_manage"],
                "config": {
                    "ANNOUNCE": True,
                    "DYNAMICWEIGHT": False,
                    "DYNAMICWEIGHT_ALLOW_ZERO": False,
                    "PERSISTENCE_TIMEOUT": None,
                    "DC_FILTER": False,
                    "STATUS_CODE": "204",
                    "HOST": "l3.tt.yandex-team.ru",
                    "CHECK_TYPE": "SSL_GET",
                    "SCHEDULER": "wrr",
                    "WEIGHT_LB67": 100,
                    "CHECK_TIMEOUT": None,
                    "DIGEST": "",
                    "QUORUM": 1,
                    "METHOD": "TUN",
                    "DYNAMICWEIGHT_IN_HEADER": False,
                    "HYSTERESIS": 0,
                    "INHIBIT_ON_FAILURE": False,
                    "CONNECT_PORT": 443,
                    "CHECK_URL": "/ping",
                    "ANNOUNCE_WEIGHT": 2,
                },
                "port": 80,
                "lb_ids": [],
                "ip": "2a02:6b8:0:3400::50",
                "protocol": VirtualServer.PROTOCOL_CHOICES.TCP,
                "ext_id": "fedf943ccce1c167475dcd820360ba49772affc22aba23720521a7605aff728e",
            }
        )

        self.rss = [
            RealServerState(
                **{
                    "id": 7968972,
                    "balancer": self.lb,
                    "vs": self.vs,
                    "fwmark": 1767,
                    "state": RealServerState.STATE_CHOICES.ACTIVE,
                    "server": RealServer(
                        **{
                            "id": 1554,
                            "config": {},
                            "ip": "2a02:6b8:0:1482::115",
                            "location": ["MYT"],
                            "fqdn": "mnt-myt.yandex.net",
                            "group": "%traffic_manage",
                        }
                    ),
                }
            ),
            RealServerState(
                **{
                    "id": 7968973,
                    "balancer": self.lb,
                    "vs": self.vs,
                    "fwmark": 1768,
                    "state": "ACTIVE",
                    "server": RealServer(
                        **{
                            "id": 1555,
                            "ip": "2a02:6b8:b010:31::233",
                            "location": ["SAS"],
                            "fqdn": "mnt-sas.yandex.net",
                            "group": "%traffic_manage",
                            "config": {"WEIGHT": 191},
                        }
                    ),
                }
            ),
        ]

    def render_output(self) -> str:
        t = loader.get_template(self.template_name)
        return t.render({"svc": self.service, "vs": self.vs, "lb": self.lb, "rss": self.rss})

    def assert_rendering_default(self):
        output: str = self.render_output()

        if not os.path.isfile(self.rendered_filename):
            with open(self.rendered_filename, "w") as fh:
                fh.write(output)

        with open(self.rendered_filename) as fh:
            expected = fh.read()

        ndiff = difflib.ndiff(expected.splitlines(keepends=True), output.splitlines(keepends=True))
        self.assertEqual(output, expected, "".join(ndiff))


class DefaultTCPServiceTest(BaseDefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-default-tcp.conf"

    def test_rendering_default(self) -> None:
        self.assert_rendering_default()


class DefaultUDPServiceTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-default-udp.conf"

    def setUp(self) -> None:
        super().setUp()

        self.vs.port = 53
        self.vs.protocol = "UDP"
        self.vs.config = {
            "METHOD": "TUN",
            "SCHEDULER": "wlc",
            "OPS": False,
            "CHECK_TYPE": "TCP_CHECK",
            "CONNECT_PORT": 53,
            "ANNOUNCE": False,
            "QUORUM": 1,
            "HYSTERESIS": 0,
        }


class OPSUDPServiceTest(DefaultUDPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-ops-udp.conf"

    def setUp(self) -> None:
        super().setUp()
        self.vs.config["OPS"] = True


class DigestTCPServiceTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-digest-tcp.conf"

    def setUp(self) -> None:
        super().setUp()
        self.vs.config.update({"DIGEST": "02e2fdad2277038aeb85149eabc28137", "INHIBIT_ON_FAILURE": True})


class DynamicWeightTCPServiceTest(DefaultTCPServiceTest):
    def test_rendering_default(self) -> None:
        self.rendered_filename = "l3mgr/tests/templates/keepalived-dynamic-weight-tcp.conf"

        self.vs.config.update(
            {"DYNAMICWEIGHT": True, "DYNAMICWEIGHT_IN_HEADER": True, "DYNAMICWEIGHT_ALLOW_ZERO": False}
        )

        super().test_rendering_default()

    def test_second_rendering_default(self) -> None:
        self.rendered_filename = "l3mgr/tests/templates/keepalived-dynamic-weight-second-tcp.conf"

        self.vs.config.update(
            {
                "DYNAMICWEIGHT": True,
                "DYNAMICWEIGHT_IN_HEADER": False,
                "DYNAMICWEIGHT_RATIO": 55,
                "DYNAMICWEIGHT_ALLOW_ZERO": True,
            }
        )

        super().test_rendering_default()


class ExtendedTCPServiceTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-extended-tcp.conf"

    def setUp(self) -> None:
        super().setUp()
        self.vs.config.update(
            {
                "PERSISTENCE_TIMEOUT": 300,
                "INHIBIT_ON_FAILURE": False,
                "DELAY_LOOP": 7,
                "HYSTERESIS": 1,
                "CHECK_TIMEOUT": 5,
                "CHECK_RETRY": 3,
                "CHECK_RETRY_TIMEOUT": 2,
            }
        )


class OptionsTCPServiceTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-options-tcp.conf"


class NoneOptionsTCPServiceTest(DefaultTCPServiceTest):
    def setUp(self):
        super().setUp()
        self.service.options = None


class LBWeightTCPServiceTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-lb-weight-tcp.conf"

    def setUp(self):
        super().setUp()
        self.vs.config.update({"WEIGHT_LB%s" % self.lb.id: "nodisable"})


class MaglevSchedulerTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-mh-tcp.conf"

    def setUp(self):
        super().setUp()
        self.vs.config.update({"SCHEDULER": "mh"})


class MaglevOptionsTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-mh-options-tcp.conf"

    def setUp(self):
        super().setUp()
        self.vs.config.update({"SCHEDULER": "mh", "MH_PORT": True, "MH_FALLBACK": True})


class MaglevEmptyOptionsTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-empty-mh-options-tcp.conf"

    def setUp(self):
        super().setUp()
        self.vs.config.update({"SCHEDULER": "wrr", "MH_PORT": True, "MH_FALLBACK": True})


class HTTPOptionsTest(DefaultTCPServiceTest):
    rendered_filename: str = "l3mgr/tests/templates/keepalived-http-options-tcp.conf"

    def setUp(self):
        super().setUp()
        self.vs.config.update({"HTTP_PROTOCOL": VSConfigForm.HTTP_PROTOCOL_CHOICES.HTTP_1_0C})


class DefaultFwmarkServiceTest(DefaultTCPServiceTest):
    template_name = "keepalived_fw.conf"
    rendered_filename = "l3mgr/tests/templates/keepalived_fw-default-fwmark.conf"

    def setUp(self):
        self.lb = LoadBalancer(
            **{
                "id": 12381,
                "state": LoadBalancer.STATE_CHOICES.ACTIVE,
                "full": False,
                "fqdn": "sas1-2lb9b.yndx.net",
                "test_env": False,
                "sticky": True,
                "location": [LocationNetwork.LOCATION_CHOICES.SAS],
            }
        )
        self.lb.ip = "2a02:6b8:0:1a00::ba9b"

        self.service = Service(**{"id": 977, "archive": False, "abc": "undefined", "fqdn": "mirror.yandex.ru"})

        self.vs = VirtualServer(
            **{
                "id": 1069929,
                "service_id": 977,
                "rs_ids": [1554, 1555],
                "groups": ["%traffic_manage"],
                "config": {
                    "ANNOUNCE": True,
                    "DYNAMICWEIGHT": False,
                    "DYNAMICWEIGHT_ALLOW_ZERO": False,
                    "PERSISTENCE_TIMEOUT": 900,
                    "STATUS_CODE": "200",
                    "CHECK_TYPE": "HTTP_GET",
                    "SCHEDULER": "wrr",
                    "WEIGHT_LB12381": 101,
                    "METHOD": "TUN",
                    "CONNECT_PORT": 80,
                    "CHECK_URL": "/.ok.txt",
                    "ANNOUNCE_WEIGHT": 0,
                },
                "port": 52407,
                "lb_ids": [],
                "ip": "2a02:6b8::183",
                "protocol": "FWM",
            }
        )

        self.vs.ext_id = common_utils.get_network_settings_hash(self.vs.ip, self.vs.port, self.vs.protocol)
        self.vs.config.setdefault("IP_FAMILY", "inet6" if is_IPv6(self.vs.ip) else "inet")

        self.rss = [
            RealServerState(
                **{
                    "id": 7968973,
                    "balancer": self.lb,
                    "vs": self.vs,
                    "fwmark": 2975,
                    "state": RealServerState.STATE_CHOICES.ACTIVE,
                    "server": RealServer(
                        **{
                            "id": 14003,
                            "config": {},
                            "ip": "2a02:6b8:c02:7f4:0:1429:f3fd:d8d0",
                            "location": ["SAS"],
                            "fqdn": "mirror01sas.mds.yandex.net",
                        }
                    ),
                }
            ),
        ]

        self.vs_list = [self.vs]

    def render_output(self) -> str:
        t = loader.get_template(self.template_name)
        return t.render({"svc": self.service, "vs_list": self.vs_list, "lb": self.lb, "rss": self.rss})
