import unittest
import unittest.mock

import commit_api


class TestCommitApiRestartServices(unittest.TestCase):
    def setUp(self):
        self._command_mock = unittest.mock.Mock(return_value=(b"mock stdout", b"mock stderr"))
        self._command_patcher = unittest.mock.patch("commit_api.command", self._command_mock)
        self._command_patcher.start()

    def tearDown(self):
        self._command_patcher.stop()

    def test_restart_services(self):
        command = self._command_mock
        s1 = commit_api.ServiceReload("s1.service")
        commit_api.restart_services([s1])
        command.assert_called_with(['systemctl', 'try-reload-or-restart', 's1.service'], timeout=commit_api.SERVICE_RELOAD_TIMEOUT)

    def test_restart_services_multi(self):
        command = self._command_mock
        s1 = commit_api.ServiceReload("s1.service")
        s2 = commit_api.ServiceReload("s2.service")
        commit_api.restart_services([s1, s2])
        command.assert_has_calls([
            unittest.mock.call(['systemctl', 'is-active', 's1.service'], ok_if_retcode=True),
            unittest.mock.call(['systemctl', 'try-reload-or-restart', 's1.service'], timeout=commit_api.SERVICE_RELOAD_TIMEOUT),
            unittest.mock.call(['systemctl', 'is-active', 's2.service'], ok_if_retcode=True),
            unittest.mock.call(['systemctl', 'try-reload-or-restart', 's2.service'], timeout=commit_api.SERVICE_RELOAD_TIMEOUT),
        ])

    def test_restart_services_with_reload(self):
        command = self._command_mock
        s1 = commit_api.ServiceReload("s1.service", reload_command="some-cmd")
        commit_api.restart_services([s1])
        command.assert_called_with(['systemctl', 'some-cmd', 's1.service'], timeout=commit_api.SERVICE_RELOAD_TIMEOUT)

    def test_restart_services_oneshot(self):
        command = self._command_mock
        s1 = commit_api.ServiceReload("s1.service", params={"Type": "oneshot"})
        commit_api.restart_services([s1])
        command.assert_called_with(['systemctl', 'restart', 's1.service'], timeout=commit_api.SERVICE_RELOAD_TIMEOUT)

    def test_restart_services_timeout(self):
        command = self._command_mock
        timeout = 123
        s1 = commit_api.ServiceReload("s1.service", timeout=timeout)
        commit_api.restart_services([s1])
        command.assert_called_with(['systemctl', 'try-reload-or-restart', 's1.service'], timeout=timeout)
