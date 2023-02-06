import os
import shutil
from copy import deepcopy
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

# noinspection PyUnresolvedReferences
from helpers import (
    MockDatetime,
    keepalived_initial_state_running_with_config,
    keepalived_initial_state_running_with_empty_config,
    keepalived_initial_state_stopped_with_config,
    keepalived_initial_state_stopped_with_empty_config,
    keepalived_initial_state_stopped_with_no_config,
)
from tasks_from_l3 import CONFIG_TEMPLATE_V2

from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigPreprocessor, BalancerConfigShort
from balancer_agent.operations.balancer_configs.config_renderers import ConfigRenderer
from balancer_agent.operations.systems.config_manager import ConfigManager
from balancer_agent.operations.systems.keepalived import MonaliveProd

from typing import Set, Tuple


class ConfigGen:
    _default_start_id = 1000
    _default_start_port = 44444
    _default_ip = "2a02:6b8:0:3400:0:43c:0:3"
    _default_ip_2 = "2a02:6b8:0:3400:0:43c:0:3333"
    _default_service = "l3manager-agent-successful-integration-test.yandex.net"

    def __init__(self, service=None, start_id=None, start_port=None, ip=None, max_configs=4):
        self._current = 0
        self._max = max_configs
        self.config = deepcopy(CONFIG_TEMPLATE_V2)

        self._id = start_id or self._default_start_id
        self._port = start_port or self._default_start_port

        group_info = deepcopy(self.config["vs_group"]["IP"])
        del self.config["vs_group"]["IP"]
        self.ip = ip or self._default_ip
        self.config["vs_group"][self.ip] = deepcopy(group_info)
        # This VS is just to have more that one VS in config dir
        self.config["vs_group"][self._default_ip_2] = deepcopy(group_info)
        self.config["service"] = service or self._default_service

    def __iter__(self):
        return self

    def new_config(self):
        self.config["id"] = self._id
        self.config["vs_group"][self.ip]["vss"][0]["port"] = self._port
        self.config["vs_group"][self.ip]["vss"][0]["config"]["check"]["connect_params"]["port"] = self._port

        result = deepcopy(self.config), self.ip, self._port

        self._id += 1
        self._port += 1

        return result

    def __next__(self):
        if self._current == self._max:
            raise StopIteration
        self._current += 1

        return self.new_config()


def stop_services() -> None:
    raise NotImplementedError()


def check_process_exists() -> None:
    raise NotImplementedError()


def remove_config_directories(stop=False):
    """
    Remove all config directories and files
    """
    for target_path in ConfigManager.DEFAULT_CONFIGURATION_UPLOAD_PATH, ConfigManager.KEEPALIVED_CONFIGURATIONS_LINKS:
        try:
            shutil.rmtree(target_path, ignore_errors=False)
        except FileNotFoundError:
            pass

    try:
        os.remove(ConfigManager.KEEPALIVED_WILDCARD_CONFIG_PATH)
    except FileNotFoundError:
        pass

    if stop:
        stop_services()


def assert_vs_installed_and_removed(installed: Set[Tuple[str, int]], removed: Set[Tuple[str, int]]) -> None:
    from balancer_agent.operations.systems.monalive import Monalive, VsStatus
    from balancer_agent.operations.systems.yanet import YaNetCli

    ip_installed = installed.copy()
    yanet = YaNetCli()
    for vs in yanet.get_services():
        pair = (vs.ip, vs.port)
        assert pair not in removed
        try:
            ip_installed.remove(pair)
        except KeyError:
            pass
    assert not ip_installed
    ip_installed = installed.copy()
    with Monalive() as monalive:
        status: VsStatus
        for status in monalive.get_status()["conf"]:
            pair = (status["vip"], status["port"])
            assert pair not in removed
            try:
                ip_installed.remove(pair)
            except KeyError:
                pass
    assert ip_installed


def assert_vs_installed(ip: str, port: int) -> None:
    assert_vs_installed_and_removed({(ip, port)}, set())


@pytest.mark.yanet
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
def test_prod_config_management_with_keepalived(mocked_agent_mode, mocked_datetime, keepalived_state_setter):
    """
    Installing Prod configs one by one, then trying to rollback and to add new configs after rollback.
    Checking that yanet works and loads proper configs
    """

    remove_config_directories()

    config_manager = MonaliveProd()

    generated_configs = []

    config_generator = ConfigGen(max_configs=100)
    # test adding new configs
    test_config, ip, port = next(config_generator)
    config_parsed = BalancerConfigPreprocessor(test_config, 2)
    config_rendered = ConfigRenderer(config_parsed).get_full_config()
    config_manager.apply_config(config_rendered, config_parsed)
    config_manager.apply_config(config_rendered, config_parsed)
    current_link_path = os.path.join(
        ConfigManager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn, "current"
    )
    previous_link_path = os.path.join(
        ConfigManager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn, "previous"
    )
    # When we re-apply config for service that have not had a previous config, previous and current should be the same
    assert Path(current_link_path).resolve() == Path(previous_link_path).resolve()

    for _ in range(3):
        test_config, ip, port = next(config_generator)
        config_parsed = BalancerConfigPreprocessor(test_config, 2)
        config_rendered = ConfigRenderer(config_parsed).get_full_config()
        config_manager.apply_config(config_rendered, config_parsed)

        generated_configs.append((config_rendered, config_parsed, ip, port))

        assert_vs_installed(ip, port)

        assert check_process_exists()

    # Apply already applied config (in case if backend wants re-deploy)
    config_rendered, config_parsed, ip, port = generated_configs[-1]
    config_manager.apply_config(config_rendered, config_parsed)

    assert_vs_installed(ip, port)

    current_link_path = os.path.join(
        ConfigManager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn, "current"
    )
    previous_link_path = os.path.join(
        ConfigManager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn, "previous"
    )
    # When we re-apply config for service that already had several configs, previous and current should not match
    assert Path(current_link_path).resolve() != Path(previous_link_path).resolve()

    assert check_process_exists()

    remove_config_directories(stop=True)


@pytest.mark.yanet
@pytest.mark.parametrize(
    "keepalived_state_setter",
    [
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_no_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_config")),
        (True, pytest.lazy_fixture("keepalived_initial_state_running_with_empty_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_config")),
        (False, pytest.lazy_fixture("keepalived_initial_state_stopped_with_empty_config")),
    ],
)
@patch("balancer_agent.operations.systems.keepalived.datetime", new_callable=MockDatetime)
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
def test_prod_config_management_with_keepalived_delete_service(
    mocked_agent_mode, mocked_datetime, keepalived_state_setter
):
    """
    Installing one Prod config. Trying to rollback, which should fail due to missing previous config.
    Then trying to delete service config which should succeed
    """

    remove_config_directories()

    config_manager = MonaliveProd()

    config_generator = ConfigGen()
    test_config, ip, port = next(config_generator)

    config_parsed = BalancerConfigPreprocessor(test_config, 2)
    config_rendered = ConfigRenderer(config_parsed).get_full_config()
    config_manager.apply_config(config_rendered, config_parsed)

    assert_vs_installed(ip, port)

    assert check_process_exists()

    config_manager.erase_config(config_parsed.service.fqdn)

    assert_vs_installed_and_removed(set(), {(ip, port)})

    assert check_process_exists()

    # This config will be kept in keepalived to check that
    # parallel service modifications don't affect each other
    config_to_keep_always, config_to_keep_always_ip, config_to_keep_always_port = next(
        ConfigGen(service="always-keep-in-keepalived.yandex.net", ip="2a02:6b8:0:3400:0:43c:0:9000", start_port=60000)
    )
    config_parsed = BalancerConfigPreprocessor(config_to_keep_always, 2)
    config_rendered = ConfigRenderer(config_parsed).get_full_config()
    config_manager.apply_config(config_rendered, config_parsed)

    removed_vs: Set[Tuple[str, int]] = set()
    # test new configs can be added after failed rollbacks
    for i in range(2):
        test_config, ip, port = next(config_generator)

        removed_vs.add((ip, port))

        config_parsed = BalancerConfigPreprocessor(test_config, 2)
        config_rendered = ConfigRenderer(config_parsed).get_full_config()
        config_manager.apply_config(config_rendered, config_parsed)

        assert_vs_installed(ip, port)

        assert check_process_exists()

    config_manager.erase_config(config_parsed.service.fqdn, with_history=True)

    # Check that config for deleted service doesn't exist in IPVS
    # Check that config to keep is installed in IPVS
    assert_vs_installed_and_removed({(config_to_keep_always_ip, config_to_keep_always_port)}, removed_vs)

    # Check not deleted unexpected
    assert Path(config_manager.config_manager.DEFAULT_CONFIGURATION_UPLOAD_PATH).exists()
    assert Path(config_manager.config_manager.KEEPALIVED_CONFIGURATIONS_LINKS).exists()
    assert Path(config_manager.config_manager.KEEPALIVED_WILDCARD_CONFIG_PATH).exists()

    # Check deleted expected
    assert not Path(
        os.path.join(config_manager.config_manager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn)
    ).exists()

    # Delete already deleted config (case when the backend wants to re-delete config)
    config_manager.erase_config(config_parsed.service.fqdn, with_history=True)

    # Check that config for deleted service doesn't exist in IPVS
    # Check that config to keep is installed in IPVS
    assert_vs_installed_and_removed({(config_to_keep_always_ip, config_to_keep_always_port)}, removed_vs)

    # Check not deleted unexpected
    assert Path(config_manager.config_manager.DEFAULT_CONFIGURATION_UPLOAD_PATH).exists()
    assert Path(config_manager.config_manager.KEEPALIVED_CONFIGURATIONS_LINKS).exists()
    assert Path(config_manager.config_manager.KEEPALIVED_WILDCARD_CONFIG_PATH).exists()

    # Check deleted expected
    assert not Path(
        os.path.join(config_manager.config_manager.DEFAULT_CONFIGURATION_UPLOAD_PATH, config_parsed.service.fqdn)
    ).exists()

    assert check_process_exists()

    remove_config_directories(stop=True)


@pytest.mark.yanet
@patch("balancer_agent.operations.systems.keepalived.MonaliveBase.restart", lambda *args, **kwargs: None)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
def test_find_next_config(mocked_agent_mode):
    """
    Installing one Prod config. Trying to rollback, which should fail due to missing previous config.
    Then trying to delete service config which should succeed
    """

    def make_config_states(configs, keep_locked=True):
        config_states = []

        for config in configs:
            config = deepcopy(config)
            if not keep_locked:
                del config["locked"]
            config_states.append(BalancerConfigShort(config))

        return config_states

    remove_config_directories()

    config_manager = MonaliveProd()
    generated_configs = []

    config_generator = ConfigGen(max_configs=100)

    # adding new configs
    for _ in range(2):
        test_config, ip, port = next(config_generator)
        test_config["state"] = "DEPLOYED"
        generated_configs.append(test_config)
        config_parsed = BalancerConfigPreprocessor(test_config, 2)
        config_rendered = ConfigRenderer(config_parsed).get_full_config()
        config_manager.apply_config(config_rendered, config_parsed)

    *_, current_config = generated_configs
    not_applied_config, _, _ = next(config_generator)

    # This config will be kept in keepalived to check that
    # parallel service modifications don't affect each other
    config_to_keep_always, _, _ = next(
        ConfigGen(service="always-keep-in-keepalived.yandex.net", ip="2a02:6b8:0:3400:0:43c:0:9000", start_id=10000)
    )
    config_to_keep_always["state"] = "DEPLOYED"
    config_parsed = BalancerConfigPreprocessor(config_to_keep_always, 2)
    config_rendered = ConfigRenderer(config_parsed).get_full_config()
    config_manager.apply_config(config_rendered, config_parsed)

    # 1. Check all configs in sync and no locked configs
    config_states = make_config_states([current_config, config_to_keep_always], keep_locked=False)
    assert not config_manager.find_unsynchronized_configs(config_states)

    # 2. Check all configs in sync, but new configs are locked and will be re-deployed
    config_states = make_config_states([current_config, config_to_keep_always], keep_locked=True)
    assert len(config_manager.find_unsynchronized_configs(config_states)) == len(config_states)

    # 3. Check all configs in sync, but new configs are locked and will be re-deployed
    config_to_keep_always_unknown = deepcopy(config_to_keep_always)
    config_to_keep_always_unknown["state"] = "UNKNOWN"
    config_states = make_config_states([current_config, config_to_keep_always_unknown], keep_locked=False)
    assert len(config_manager.find_unsynchronized_configs(config_states)) == 1
    assert config_manager.find_unsynchronized_configs(config_states)[0].id == config_to_keep_always_unknown["id"]

    # 4. Check collected new config to deploy
    config_states = make_config_states([current_config, not_applied_config, config_to_keep_always], keep_locked=False)
    assert len(config_manager.find_unsynchronized_configs(config_states)) == 1
    assert config_manager.find_unsynchronized_configs(config_states)[0].id == not_applied_config["id"]

    # 5. Check found config to delete
    current_config, config_to_keep_always = make_config_states([current_config, config_to_keep_always])
    config_to_delete = deepcopy(current_config)
    config_to_delete.target = ConfigManager.TARGET_DELETED

    found_diff = config_manager.find_unsynchronized_configs([config_to_delete, config_to_keep_always])
    assert len(found_diff) == 1
    assert found_diff[0].id == config_to_keep_always.id

    # 6. Check logged unexpected service deployed on balancer
    with patch("balancer_agent.operations.systems.config_manager.logger.error") as mock_error_log:
        config_manager.find_unsynchronized_configs([config_to_keep_always])
        assert len(mock_error_log.call_args[1]["extra"]["additional"]["unexpected"]) == 1
        mock_error_log.assert_called_once()

    remove_config_directories(stop=True)
