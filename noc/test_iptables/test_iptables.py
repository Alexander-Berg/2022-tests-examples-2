from unittest.mock import Mock, patch

import pytest

from balancer_agent.operations.balancer_configs.config_containers import AFSpec
from balancer_agent.operations.systems.base import CommandExecutionError
from balancer_agent.operations.systems.iptables import UPDATE_FW_RETRIES, IpTables

from .static import V4_RULES_MC, V6_RULES_MC, MockedConfig, MockVS


@pytest.mark.parametrize(
    "vss,fqdn,expected_restart",
    [
        # Success case
        [[], MockedConfig.fqdn, False],
        # Failure case - VS IP not in iptables rules
        [[MockVS("2a02:6b8::DEAD:BEEF", AFSpec.IPV6)], MockedConfig.fqdn, True],
    ],
)
def test_iptables(vss, fqdn, expected_restart):
    MockedConfig.vss += vss
    MockedConfig.fqdn = fqdn

    iptables = IpTables()

    # # Cache will have rules by the first .update() call
    iptables._V4_CACHE._get_rules = lambda *args: V4_RULES_MC
    iptables._V6_CACHE._get_rules = lambda *args: V6_RULES_MC

    iptables.v4_ips, iptables.v6_ips = iptables._get_ips(MockedConfig().body.vss)
    iptables.fqdn = MockedConfig.fqdn

    assert iptables.need_restart() == expected_restart


@patch("balancer_agent.operations.systems.iptables.CommandExecutor.run_cmd", new_callable=Mock)
@patch("balancer_agent.operations.systems.iptables.IpTables._decorated.need_restart", lambda *args: True)
def test_iptables_restart(mock_run_cmd):
    iptables = IpTables()
    iptables.restart(MockedConfig())

    assert mock_run_cmd.mock_calls[0][1][0] == iptables.UPDATE_RULES_COMPLETE_CYCLE_CMD


@patch("balancer_agent.operations.systems.iptables.CommandExecutor.run_cmd", Mock(side_effect=CommandExecutionError))
@patch("balancer_agent.operations.systems.iptables.IpTables._decorated.need_restart", lambda *args: True)
def test_iptables_restart_failure():
    IpTables._decorated.restart.__closure__[1].cell_contents["wait_exponential_multiplier"] = 1
    IpTables._decorated.restart.__closure__[1].cell_contents["wait_exponential_max"] = 1

    iptables = IpTables()

    with pytest.raises(CommandExecutionError):
        iptables.restart(MockedConfig())

    assert iptables.execute.call_count == UPDATE_FW_RETRIES
