import logging
from io import StringIO
from collections import namedtuple

from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock

from paramiko import SSHException

from ..exceptions import BalancerCommunicationException
from ..services import (
    BalancerHost,
    BalancerCriticalException,
    BalancerKeepalivedStartFailed,
    BalancerKeepalivedStoppingFailed,
    BalancerUpdateConfigurationPullException,
    BalancerUpdateConfigurationLinkException,
    StartResult,
    StopResult,
)
from ..systems import keepalived, ipvs, ip, iptables

logger = logging.getLogger(__file__)


class ExecResponse(namedtuple("ExecResponse", ["code", "stdout", "stderr", "exc"])):
    __slots__ = ()

    @classmethod
    def of(cls, code=0, stdout="", stderr="", exc=None):
        return cls(code, stdout, stderr, exc)


def _setup_ssh_mock(test, ssh_mock, cmds):
    def ssh_side_effect(cmd):
        result = cmds.get(cmd)
        if result is None:
            test.fail("Test: unexpected cmd for mock: %s" % cmd)

        if result.exc:
            raise result.exc

        class M(StringIO):
            channel = MagicMock()
            channel.recv_exit_status.return_value = result.code

        return result.code, M(result.stdout), M(result.stderr)

    class Receiver:
        cmds = []
        received = []

        def send(self, msg):
            self.received.append(msg)
            return len(msg)

        def shutdown_write(self):
            pass

        def exec_command(self, cmd):
            self.cmds.append(cmd)

        def close(self):
            pass

    receiver = Receiver()

    def ssh(dst):
        class TransportMock:
            def open_session(self):
                return receiver

        class MockSshClient:
            def exec_command(self, cmd):
                return ssh_side_effect(cmd)

            def get_transport(self):
                return TransportMock()

            def close(self):
                pass

        return MockSshClient()

    ssh_mock.side_effect = ssh
    ssh_mock.receiver = receiver


class BalancerHostFactoryMixin:
    @staticmethod
    def make_host():
        host = BalancerHost("man1-lb2b.yndx.net")
        return host


class StartKeepalivedTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @patch("l3balancer.utils.create_ssh")
    def test_start_exiting_process(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(stdout="1"),
                keepalived.RESTART_SERVICE_CMD: ExecResponse.of(),
            },
        )
        host = self.make_host()
        self.assertEqual(StartResult.RESTARTED, host.start_keepalived(restart=True))
        self.assertEqual(StartResult.SKIPPED, host.start_keepalived(restart=False))

    @patch("l3balancer.utils.create_ssh")
    def test_start_not_exiting_process(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(stdout="0"),
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="0"),
                keepalived.START_SERVICE_CMD: ExecResponse.of(),
            },
        )
        host = self.make_host()
        self.assertEqual(StartResult.STARTED, host.start_keepalived(restart=False))
        self.assertEqual(StartResult.STARTED, host.start_keepalived(restart=True))

    @patch("l3balancer.utils.create_ssh")
    def test_start_missed_process(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(stdout="0"),
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="1"),
            },
        )
        host = self.make_host()
        self.assertRaises(BalancerCriticalException, host.start_keepalived, restart=False)
        self.assertRaises(BalancerCriticalException, host.start_keepalived, restart=True)

    @patch("l3balancer.utils.create_ssh")
    def test_start_failed(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(stdout="0"),
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="0"),
                keepalived.START_SERVICE_CMD: ExecResponse.of(code=1),
            },
        )
        host = self.make_host()
        self.assertRaises(BalancerKeepalivedStartFailed, host.start_keepalived, restart=False)
        self.assertRaises(BalancerKeepalivedStartFailed, host.start_keepalived, restart=True)

    @patch("l3balancer.utils.create_ssh")
    def test_restart_failed(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(stdout="1"),
                keepalived.RESTART_SERVICE_CMD: ExecResponse.of(code=1),
            },
        )
        host = self.make_host()
        self.assertRaises(BalancerKeepalivedStartFailed, host.start_keepalived, restart=True)

    @patch("l3balancer.utils.create_ssh")
    def test_check_process_failed(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={keepalived.CHECK_PROCESS_BY_PID_CMD: ExecResponse.of(exc=SSHException("Test error - don't worry"))},
        )
        host = self.make_host()
        self.assertRaises(BalancerCommunicationException, host.start_keepalived)


class StopKeepalivedTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @patch("l3balancer.utils.create_ssh")
    def test_stopping(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="1"),
                keepalived.STOP_SERVICE_CMD: ExecResponse.of(),
            },
        )
        host = self.make_host()
        self.assertEqual(StopResult.STOPPING, host.stop_keepalived())

    @patch("l3balancer.utils.create_ssh")
    def test_ipvs_rules_exists(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="0"),
                ipvs.COUNT_VS_CMD: ExecResponse.of(stdout="4"),
            },
        )
        host = self.make_host()
        self.assertEqual(StopResult.RULES_CLEANUP, host.stop_keepalived())

    @patch("l3balancer.utils.create_ssh")
    def test_already_stopped(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="0"),
                ipvs.COUNT_VS_CMD: ExecResponse.of(stdout="3"),
            },
        )
        host = self.make_host()
        self.assertEqual(StopResult.STOPPED, host.stop_keepalived())

    @patch("l3balancer.utils.create_ssh")
    def test_stopping_failed(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CHECK_PROCESS_CMD: ExecResponse.of(stdout="1"),
                keepalived.STOP_SERVICE_CMD: ExecResponse.of(code=1),
            },
        )
        host = self.make_host()
        self.assertRaises(BalancerKeepalivedStoppingFailed, host.stop_keepalived)


class CleanKeepalivedTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @patch("l3balancer.utils.create_ssh")
    def test_clean_keepalived_config(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                keepalived.CLEAN_CONFIG_CMD: ExecResponse.of(),
            },
        )
        host = self.make_host()
        host.clean_config()


_IPVS_RESPONSE = """\
IP Virtual Server version 1.2.1 (size=1048576)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port Forward Weight ActiveConn InActConn
TCP  [2a02:06b8:0000:3400:ffff:0000:0000:04c9]:0050 wrr 
  -> [2a02:06b8:b040:3100:0ccc:0000:0000:04c9]:0050      Tunnel  1      0          0         
  -> [2a02:06b8:0000:1482:0000:0000:0000:0115]:0050      Tunnel  1      0          0         
  -> [2a02:06b8:b010:0031:0000:0000:0000:0233]:0050      Tunnel  1      0          0         
TCP  [2a02:06b8:0000:0000:0000:0000:0000:0144]:01BB wrr 
  -> [2a02:06b8:0c0c:4683:0000:0697:845f:458c]:01BB      Tunnel  1      0          0         
UDP  8D08927B:0229 wrr  
  -> 258CBE4D:0229      Tunnel  1      0          0         
  -> 5F6C8255:0229      Tunnel  1      0          0         
TCP  5D9E8625:006E wrr  
  -> 258CBE35:006E      Tunnel  100    0          0         
  -> 052DC741:006E      Tunnel  100    0          0         
  -> 4D581D06:006E      Tunnel  100    0          0         
TCP  B29AAAF1:01BB wrr  
  -> [2a02:06b8:b020:4602:0000:0000:0000:0a22]:01BB      Tunnel  46     0          0         
  -> [2a02:06b8:b020:4602:0000:0000:0000:0a19]:01BB      Tunnel  46     0          0         
  -> 5F6C894F:01BB      Tunnel  32     0          0         
  -> 258CB5ED:01BB      Tunnel  32     0          0         
"""
_IP_RESPONSE = """\
199: dummy0    inet 192.168.100.2/32 scope global tun0\\       valid_lft forever preferred_lft forever
199: dummy0    inet6 fe80::b825:a700:c586:3c07/128 scope link stable-privacy \\       valid_lft forever preferred_lft forever
199: dummy0    inet6 2a02:6b8:0:3400:ffff::4c9/128 scope link stable-privacy \\       valid_lft forever preferred_lft forever
"""


class VsInfo(namedtuple("VsInfo", ["ip", "port", "protocal"])):
    pass


class ServiceInfo(namedtuple("ServiceInfo", ["vs", "rss"])):
    @classmethod
    def of(cls, ip, port, protocol):
        # type: (str, int, str) -> ServiceInfo
        return cls(vs=VsInfo(ip, port, protocol), rss=set())

    def add_rss(self, *ip):
        # type: (str) -> ServiceInfo
        self.rss.update(ip)
        return self


class FetchBalancerInfoTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @patch("l3balancer.utils.create_ssh", autospec=True)
    def test_stopping(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                ipvs.CAT_IPVS_CMD: ExecResponse.of(stdout=_IPVS_RESPONSE),
                ip.IP.CAT_IP_CMD: ExecResponse.of(stdout=_IP_RESPONSE),
            },
        )
        host = self.make_host()
        service_info, announced_ips = host.fetch_balancer_info()

        expected_service_info = [
            ServiceInfo.of("2a02:6b8:0:3400:ffff::4c9", 80, "TCP").add_rss(
                "2a02:6b8:0:1482::115",
                "2a02:6b8:b010:31::233",
                "2a02:6b8:b040:3100:ccc::4c9",
            ),
            ServiceInfo.of("2a02:6b8::144", 443, "TCP").add_rss("2a02:6b8:c0c:4683:0:697:845f:458c"),
            ServiceInfo.of("141.8.146.123", 553, "UDP").add_rss("95.108.130.85", "37.140.190.77"),
            ServiceInfo.of("93.158.134.37", 110, "TCP").add_rss("37.140.190.53", "77.88.29.6", "5.45.199.65"),
            ServiceInfo.of("178.154.170.241", 443, "TCP").add_rss(
                "2a02:6b8:b020:4602::a19", "2a02:6b8:b020:4602::a22", "37.140.181.237", "95.108.137.79"
            ),
        ]
        expected_announced_ips = {"192.168.100.2", "fe80::b825:a700:c586:3c07", "2a02:6b8:0:3400:ffff::4c9"}

        self.assertListEqual(expected_service_info, service_info)
        self.assertSetEqual(expected_announced_ips, announced_ips)


class RestartFirewallTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @patch("l3balancer.utils.create_ssh")
    def test_restart_firewall(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={
                iptables.UPDATE_CMD: ExecResponse.of(),
                iptables.INSTALL_CMD: ExecResponse.of(),
                iptables.RESTART_CMD: ExecResponse.of(),
                iptables.INSTALL_TARBALL_CMD: ExecResponse.of(),
            },
        )
        host = self.make_host()
        host.restart_firewall()


class UpdateConfigTestCase(BalancerHostFactoryMixin, SimpleTestCase):
    @staticmethod
    def get_link_config_cmd():
        return keepalived.LINK_CONFIG_BASE_CMD % dict(
            configuration_upload_path=keepalived.Keepalived.configuration_upload_path
        ) + keepalived.LINK_CONFIG_FROM_VCS_CMD % dict(
            svn_working_dir=keepalived.Keepalived.SVN_WORKING_DIRECTORY,
            git_working_dir=keepalived.Keepalived.GIT_WORKING_DIRECTORY,
        )

    @staticmethod
    def get_pull_config_cmd():
        return keepalived.PULL_CONFIG_FROM_VCS_CMD % dict(
            svn_repo_url=keepalived.Keepalived.SVN_REPO_URL,
            svn_working_dir=keepalived.Keepalived.SVN_WORKING_DIRECTORY,
            git_repo_url=keepalived.Keepalived.GIT_REPO_URL,
            git_working_dir=keepalived.Keepalived.GIT_WORKING_DIRECTORY,
        )

    def assert_receiver(self, ssh_mock, content):
        receiver = ssh_mock.receiver
        received = receiver.received
        self.assertListEqual([content], received)
        self.assertEqual(len(receiver.cmds), 1)

    @patch("l3balancer.utils.create_ssh")
    def test_update_with_cvs_pull(self, ssh_mock):
        _setup_ssh_mock(
            self,
            ssh_mock,
            cmds={self.get_pull_config_cmd(): ExecResponse.of(), self.get_link_config_cmd(): ExecResponse.of()},
        )
        host = self.make_host()

        content = "1 - 2 - 3 - 4"
        host.update_config(content, pull_cvs=True)
        self.assert_receiver(ssh_mock, content)

    @patch("l3balancer.utils.create_ssh")
    def test_update_without_cvs_pull(self, ssh_mock):
        _setup_ssh_mock(self, ssh_mock, cmds={self.get_link_config_cmd(): ExecResponse.of()})
        host = self.make_host()

        content = "5 - 6 - 7 - 8"
        host.update_config(content, pull_cvs=False)
        self.assert_receiver(ssh_mock, content)

    @patch("l3balancer.utils.create_ssh")
    def test_update_with_pull_failed(self, ssh_mock):
        _setup_ssh_mock(self, ssh_mock, cmds={self.get_pull_config_cmd(): ExecResponse.of(code=1)})
        host = self.make_host()

        content = "9 - 0 - 1 - 2"
        self.assertRaises(BalancerUpdateConfigurationPullException, host.update_config, content, pull_cvs=True)
        self.assert_receiver(ssh_mock, content)

    @patch("l3balancer.utils.create_ssh")
    def test_update_link_failed(self, ssh_mock):
        _setup_ssh_mock(self, ssh_mock, cmds={self.get_link_config_cmd(): ExecResponse.of(code=1)})
        host = self.make_host()

        content = "3 - 4 - 5 - 6"
        self.assertRaises(BalancerUpdateConfigurationLinkException, host.update_config, content, pull_cvs=False)
        self.assert_receiver(ssh_mock, content)
