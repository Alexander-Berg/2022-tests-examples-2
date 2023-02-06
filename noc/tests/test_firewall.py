import os
import pathlib
import tempfile
import tenacity
import typing
from unittest import mock

from django.conf import settings
from django import test
from parameterized import parameterized

from .. import AcquireLockTimoutExceedError
from .. import firewall
from ... import models


@test.override_settings(
    FW_YAML_SERVICES=tempfile.NamedTemporaryFile(
        prefix="firewall-find-services-ip",
        suffix=".yaml",
        dir="",
    ).name,
)
class FirewallFindServicesIP(test.SimpleTestCase):
    def tearDown(self):
        """Cleanup temporary files."""
        pathlib.Path(settings.FW_YAML_SERVICES).unlink(missing_ok=True)
        super().tearDown()

    @parameterized.expand(
        [
            (
                """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8:0:3400::935]
  fwmark: 12345
---
# ns1.yandex.ru
ns1.yandex.net:
  ips: [213.180.193.1, 2a02:6b8::1]
  chain_name: ns1.y.ru
""",
                ["2a02:6b8::1", "87.250.250.242"],
                {
                    "2a02:6b8::1": ["ns1.yandex.net"],
                    "87.250.250.242": ["ya.ru"],
                },
            ),
            (
                """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8:0:3400::935]
  fwmark: 12345
---
# ns1.yandex.ru
ns1.yandex.net:
  ips: [213.180.193.1, 2a02:6b8::1]
  chain_name: ns1.y.ru
""",
                ["213.180.205.35"],
                {},
            ),
            (
                """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8:0:3400::935]
  fwmark: 12345
""",
                [],
                {},
            ),
            ("", ["127.0.0.1"], {}),
        ]
    )
    def test_success_scenarios(self, yaml_content, ips, expected_result):
        with open(settings.FW_YAML_SERVICES, "w") as fh:
            fh.write(yaml_content)

        with mock.patch("l3mgr.utils.vcs.CVS.checkout", autospec=True, return_value=True):
            result = firewall.find_fw_svcs_by_ip(ips)
            self.assertSequenceEqual(expected_result.keys(), result.keys())
            for ip in expected_result.keys():
                self.assertListEqual(sorted(expected_result[ip]), sorted(result[ip]))

    @parameterized.expand(
        [
            (
                """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8:0:3400::935]
---
ns42.yandex.net:
  ips: [87.250.250.242]""",
            ),
            (
                """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8:0:3400::935]
---
ya.ru:
  ips: [127.0.0.1]""",
            ),
        ]
    )
    def test_parse_exception(self, services_yaml):
        func = firewall.find_fw_svcs_by_ip
        func.retry.wait = tenacity.wait_none()

        with mock.patch("l3mgr.utils.vcs.CVS.checkout", autospec=True, return_value=True), self.assertRaises(
            firewall.FindFwSvcsByIpResult.YamlConfigParsingFailed
        ):
            with open(settings.FW_YAML_SERVICES, "w") as fh:
                fh.write(services_yaml)
            firewall.find_fw_svcs_by_ip([])

        self.assertEqual(3, func.retry.statistics["attempt_number"])

    def test_checkout_exception(self):
        func = firewall.find_fw_svcs_by_ip
        func.retry.wait = tenacity.wait_none()

        with mock.patch(
            "l3mgr.utils.vcs.CVS.checkout",
            autospec=True,
            side_effect=firewall.FindFwSvcsByIpResult.CvsCheckoutFailed("test exception"),
        ), self.assertRaisesRegex(firewall.FindFwSvcsByIpResult.CvsCheckoutFailed, "test exception"):
            firewall.find_fw_svcs_by_ip([])

        self.assertEqual(3, func.retry.statistics["attempt_number"])

    def test_cleanup_directory(self):
        with open(settings.FW_YAML_SERVICES, "w") as fh:
            fh.write("---\n")

        directory_name = "firewall-find-services-ip-test_cleanup_directory"
        with mock.patch("l3mgr.utils.vcs.CVS.checkout", autospec=True, return_value=None), mock.patch(
            "tempfile.mkdtemp", autospec=True, return_value=directory_name
        ):
            firewall.find_fw_svcs_by_ip([])

        self.assertFalse(pathlib.Path(directory_name).exists())


class FirewallTest(test.SimpleTestCase):
    def setUp(self):
        self.base_yaml = """---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8::2:242]
  fwmark: 12345
---
# ns1.yandex.ru
ns1.yandex.net:
  ips: [213.180.193.1, 2a02:6b8::1]
  chain_name: ns1.y.ru
"""
        fd, self.filename = tempfile.mkstemp(prefix="FirewallTestCase", text=True)
        with open(fd, "w") as fh:
            fh.write(self.base_yaml)

    def tearDown(self):
        os.unlink(self.filename)

    def test_modify_file(self):
        result_yaml = """---
# ns1.yandex.ru
ns1.yandex.net:
  ips:
    - 2a02:6b8:a::a
    - 5.255.255.5
    - 77.88.55.80
    - 77.88.55.88
  chain_name: ns1.y.ru
---
new-service.yandex.net:
  ips: ['2a02:6b8::', 87.250.250.0]
"""

        yserv = (
            firewall.YAMLservices()
            .load(self.filename)
            .delete("ya.ru")
            .insert_or_update(
                "ns1.yandex.net",
                ["5.255.255.5", "77.88.55.80", "77.88.55.88", "2a02:6b8:a::a"],
            )
            .insert_or_update("new-service.yandex.net", ["87.250.250.0", "2a02:6b8::"])
            .save(f"{self.filename}.tmp")
        )
        try:
            self.assertTrue(yserv.loaded, "File wasn't loaded")
            self.assertTrue(yserv.changed, "File wasn't changed")
            self.assertTrue(yserv.saved, "File wasn't saved")

            with open(f"{self.filename}.tmp") as fh:
                data = fh.read()

            self.assertEqual(data, result_yaml, "Results files are different")
        finally:
            os.unlink(f"{self.filename}.tmp")

    def test_null_changes(self):
        yserv = (
            firewall.YAMLservices()
            .load(self.filename)
            .insert_or_update("ns1.yandex.net", ["213.180.193.1", "2a02:6b8::1"])
        )

        self.assertFalse(yserv.changed, "Changes exist on equal file")

    def test_services_ips(self):
        yserv = firewall.YAMLservices().load(self.filename)
        self.assertEqual(
            yserv.get_services_by_ips(["213.180.193.1"]), {"ns1.yandex.net"}, "Received wrong services IPs"
        )

    def test_fwmark_changes(self):
        result_yaml = """---
ya.ru:
  ips: [2a02:6b8::2:242, 87.250.250.242]
---
# ns1.yandex.ru
ns1.yandex.net:
  ips: [213.180.193.1, 2a02:6b8::1]
  chain_name: ns1.y.ru
  fwmark: 54321
"""
        yserv = (
            firewall.YAMLservices()
            .load(self.filename)
            .insert_or_update("ya.ru", ["87.250.250.242", "2a02:6b8::2:242"])
            .insert_or_update("ns1.yandex.net", ["213.180.193.1", "2a02:6b8::1"], 54321)
            .save(f"{self.filename}.tmp")
        )
        try:
            self.assertTrue(yserv.loaded, "File wasn't loaded")
            self.assertTrue(yserv.changed, "File wasn't changed")
            self.assertTrue(yserv.saved, "File wasn't saved")

            with open(f"{self.filename}.tmp") as fh:
                data = fh.read()
            self.assertEqual(data, result_yaml, "Results files are different")
        finally:
            os.unlink(f"{self.filename}.tmp")

    def test_exceptions(self):
        with self.assertRaises(FileNotFoundError):
            firewall.YAMLservices().load("NON-EXIST-FILENAME.tmp")

        with self.assertRaises(ValueError):
            firewall.YAMLservices().load(self.filename).insert_or_update(
                "ns1.yandex.NOT-EXIST-DOMAIN",
                ["213.180.193.1", "2a02:6b8::1"],
            )

    def test_empty_service(self):
        result_yaml = """---
ya.ru:
  ips: []
"""

        yserv = (
            firewall.YAMLservices()
            .load(self.filename)
            .delete("ns1.yandex.net")
            .insert_or_update("ya.ru", set(), None)
            .save(f"{self.filename}.tmp")
        )
        try:
            self.assertTrue(yserv.loaded, "File wasn't loaded")
            self.assertTrue(yserv.changed, "File wasn't changed")
            self.assertTrue(yserv.saved, "File wasn't saved")

            with open(f"{self.filename}.tmp") as fh:
                data = fh.read()

            self.assertEqual(data, result_yaml, "Results files are different")
        finally:
            os.unlink(f"{self.filename}.tmp")


@test.override_settings(FW_UPDATE_PERIODIC=False)
class FirewallRulesTestCase(test.TestCase):
    def test_fw_update(self):
        configuration: models.Configuration = self._prepare_data(
            "lbk-man.logbroker-prestable.yandex.net", "sas1-2lb3b.yndx.net"
        )
        with mock.patch("l3mgr.utils.firewall._update_fw_yaml_rules") as yaml_update_mock:
            firewall.upload_fw(configuration)
            vs_ips = {configuration.vss[0].ip}
            self.assert_yaml_update_mock_called(yaml_update_mock, configuration.service.fqdn, vs_ips)

    @test.override_settings(FW_UPDATE_PERIODIC=True)
    def test_ignore_update(self):
        configuration: models.Configuration = self._prepare_data("test-ignore-update.yandex.net", "sas1-2lb3b.yndx.net")
        with mock.patch("l3mgr.utils.firewall._update_fw_yaml_rules") as yaml_update_mock:
            firewall.upload_fw(configuration)
            yaml_update_mock.assert_not_called()

    def test_exception_lock_error(self):
        configuration: models.Configuration = self._prepare_data("l3.tt.yandex-team.ru", "man1-lb2b.yndx.net")
        func = firewall._update_fw_yaml_rules

        with mock.patch("l3mgr.utils.firewall._upload_fw_yaml_rules") as yaml_upload_mock, mock.patch(
            "l3mgr.utils._tools.open_and_lock"
        ) as open_and_lock_mock:
            open_and_lock_mock.side_effect = AcquireLockTimoutExceedError("Lock cvs.log error")
            yaml_upload_mock.return_value = None

            func.retry.wait = tenacity.wait_none()
            with self.assertRaisesRegex(AcquireLockTimoutExceedError, "Lock cvs.log error"):
                firewall.upload_fw(configuration)
            self.assertEqual(5, func.retry.statistics["attempt_number"])

    def assert_yaml_update_mock_called(self, yaml_update_mock: mock.Mock, fqdn: str, vs_ips: typing.Set[str]):
        yaml_update_mock.assert_called_once()
        calls = yaml_update_mock.mock_calls[0]
        self.assertEqual(2, len(calls.args))
        self.assertEqual(fqdn, calls.args[0])
        m = mock.Mock()
        calls.args[1](m, fqdn)
        m.assert_has_calls([mock.call.insert_or_update(fqdn, vs_ips, None)])

    @staticmethod
    def _prepare_data(service_fqdn: str, balancer_fqdn: str) -> models.Configuration:
        svc: models.Service = models.Service.objects.create(fqdn=service_fqdn, abc="dostavkatraffika")
        rs: models.RealServer = models.RealServer.objects.create(
            fqdn=service_fqdn,
            ip="2a02:6b8:0:1482::115",
            config={},
            location=[models.LocationRegion.REGION_CHOICES.MAN],
        )
        balancer: models.LoadBalancer = models.LoadBalancer.objects.create(
            state=models.LoadBalancer.STATE_CHOICES.ACTIVE,
            location=[
                models.LocationNetwork.LOCATION_CHOICES.SAS,
            ],
            fqdn=balancer_fqdn,
            test_env=True,
        )
        vip: models.VirtualServer = models.VirtualServer.objects.create(
            service=svc,
            ip="2a02:6b8:0:3400:ffff::4cA",
            port=8181,
            protocol=models.VirtualServer.PROTOCOL_CHOICES.TCP,
            lb_ids=[balancer.pk],
            rs_ids=[rs.id],
            config={"URL": "/check", "STATUS_CODE": 200},
        )
        configuration: models.Configuration = models.Configuration.objects.create(
            service=svc,
            vs_ids=[vip.pk],
            description="test-second-service-config",
            state=models.Configuration.STATE_CHOICES.TEST_PENDING,
        )
        return configuration
