import sys
from unittest.mock import Mock

from box import Box

from balancer_agent.core import config

HOST_A = "host_a"
HOST_B = "host_b"
IDLE_STATE = "IDLE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_INITIAL_CONFIG = {
    "controller": {
        "data_collector_url": "https://l3-test.tt.yandex-team.ru/api/v1/agent",
        "worker_tracking_seconds": 0.01,
    },
    "main": {"agent_mode": "test", "balancing_type": "ipvs", "lb_name": "man1-testenv-lb0bb.yndx.net"},
    "stage": "development",
    "startup": {
        "initial_state": IDLE_STATE,
        "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
        "settings_polling_interval": 0.2,
        "signal_failure_interval": 10000,
        "tasks_polling_interval": 0.1,
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

# Replacing config.init_base_config, because by default it loads config file from BASE_CONFIG_PATH
# which may be not available in test/dev env
config.init_base_config = lambda *args: Box(MOCK_INITIAL_CONFIG)


class MockLibIPVS:
    def expanded_tree(self):
        pass


# Think how to mock pylibipvs
sys.modules["pylibipvs.libipvs"] = Mock()
