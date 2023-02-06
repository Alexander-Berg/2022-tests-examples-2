import copy

import unittest
from unittest.mock import Mock, patch

import yanet_agent


class YanetAgentTestCase(unittest.TestCase):
    AGENT_RESPONSE = {
        "uptime": 1733542,
        "errors": 44,
        "errors_update_controlplane": 0,
        "state": "SLEEP",
        "last_snapshot_timestamp": 1650435415,
        "last_status": "VALID",
        "last_build_time": 14.573441982269287,
        "build_timings": [],
    }

    def test_uptime_error(self):
        resp = copy.deepcopy(self.AGENT_RESPONSE)
        resp.update({"uptime": 0})

        with patch("yanet_agent.get_url", return_value=resp), self.assertRaisesRegex(ValueError, "uptime less than"):
            yanet_agent.main()

    def test_controlplane_error(self):
        resp = copy.deepcopy(self.AGENT_RESPONSE)
        resp.update({"errors_update_controlplane": 1})

        with patch("yanet_agent.get_url", return_value=resp), self.assertRaisesRegex(
            ValueError, "recv errors while update controlplane"
        ):
            yanet_agent.main()

    def test_last_status_error(self):
        resp = copy.deepcopy(self.AGENT_RESPONSE)
        resp.update({"last_status": "INVALID"})

        with patch("yanet_agent.get_url", return_value=resp), self.assertRaisesRegex(
            ValueError, "last_status is not valid"
        ):
            yanet_agent.main()

    def test_successful(self):
        with patch("yanet_agent.get_url", return_value=self.AGENT_RESPONSE):
            yanet_agent.main()
