import sys
from unittest.mock import Mock

from box import Box

from balancer_agent.core import config


class MockLibIPVS:
    def expanded_tree(self):
        pass


# Think how to mock pylibipvs
sys.modules["pylibipvs.libipvs"] = Mock()


mock_agent_config = {
    "controller": {"data_collector_url": "mock", "worker_tracking_seconds": 10},
    "main": {"agent_mode": "test", "lb_name": "mock_pb"},
    "stage": "development",
    "startup": {
        "initial_state": "IDLE",
        "l3_hosts_pool": ["mock1", "mock2"],
        "settings_polling_interval": 6000,
        "signal_failure_interval": 10000,
        "tasks_polling_interval": 1000,
    },
    "auth": {
        "tvm": {
            "enabled": False,
            "id": 2025990,
            "secret": "AGENT_TVM_SECRET",
            "destinations": {"l3mgr": 2002629, "solomon": 2010242},
        }
    },
    "monitoring": {
        "solomon": {"ids": ["l3mgr-balancer-agents", "dummy_testenv", "testenv_agents"]},
        "server": {"address": "localhost", "port": 60890},
    },
}

config.init_base_config = lambda *args: Box(mock_agent_config)
