import difflib
import json
import os.path
import re
from http import HTTPStatus
from unittest.mock import Mock, PropertyMock, mock_open, patch

import pytest
import requests_mock

from balancer_agent.operations.balancer_configs.config_renderers import RENDERERS
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.tasks.handlers.ipvs_prod_tasks import ProdTasksHandler

from .static.configs_from_api import TEST_SERVICE_FQDN, ConfigGenerator, ConfigListGenerator
from .static.configs_rendered import (
    CONFIG_DYNAMIC_WEIGHT_V2,
    CONFIG_L4_ANNOUNCE_DISABLED_V2,
    CONFIG_L4_V2,
    CONFIG_MAGLEV_AND_HTTP_PROTOCOL_V2,
)

import typing

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 2,
}

AGENT_API_HOSTS = "https://host.*"

MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


SCHEDULER_MH = {
    "type": "mh",
    "options": {
        "mh_port": True,
        "mh_fallback": False,
        "ops": True,
    },
}


DYNAMICWEIGHT_ENABLED = {"enabled": True, "options": {"ratio": 30, "allow_zero": False, "in_header": True}}
CONFIG_REAL_PATH = "/home/ttmgmt/services/l3.tt.yandex-team.ru/1"


@pytest.mark.parametrize(
    "l3_response,reference_config,reference_config_announce_disabled,status_code",
    [
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 2), "num_vss": (1, 2)},
                    }
                )
            ),
            CONFIG_L4_V2,
            CONFIG_L4_ANNOUNCE_DISABLED_V2,
            HTTPStatus.OK,
        ),
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 2), "num_vss": (1, 2)},
                        "scheduler": SCHEDULER_MH,
                    }
                )
            ),
            CONFIG_MAGLEV_AND_HTTP_PROTOCOL_V2,
            None,
            HTTPStatus.OK,
        ),
        (
            json.dumps(
                ConfigGenerator.get(
                    {
                        "config_target": "ACTIVE",
                        "vs_group_settings": {"num": 2, "min_up": (1, 2), "num_vss": (1, 2)},
                        "dynamicweight": DYNAMICWEIGHT_ENABLED,
                    }
                )
            ),
            CONFIG_DYNAMIC_WEIGHT_V2,
            None,
            HTTPStatus.OK,
        ),
        # TODO: add fwmark support
        # (
        #     [TASK_FWMARK],
        #     TASK_FWMARK_CONFIG,
        #     TASK_FWMARK_CONFIG_ANNOUNCE_ENABLED,
        #     HTTPStatus.OK,
        # ),
    ],
)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.AGENT_MODE",
    new_callable=PropertyMock(return_value="prod"),
)
@patch("balancer_agent.operations.balancer_configs.config_containers.VSFWMDataset.bindto", MOCK_BINDTO_IP)
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.dns.resolver.resolve",
    Mock(**{"return_value.rrset": [MOCK_BINDTO_IP]}),
)
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=False)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=True)
@patch("balancer_agent.operations.systems.config_manager.open", new_callable=mock_open)
@patch("balancer_agent.operations.systems.config_manager.Path", return_value=Mock())
@patch("balancer_agent.operations.systems.config_manager.ConfigManager.db.delete", new_callable=Mock())
@patch("balancer_agent.operations.systems.config_manager.delete_from_tracking", new_callable=Mock())
@requests_mock.mock(kw="requests_mocker")
def test_handle_task(
    mock_delete_from_tracking,
    mock_db_delete,
    path_mock: Mock,
    mocked_open,
    mock1,
    mock2,
    mocked_agent_mode,
    l3_response,
    reference_config: str,
    reference_config_announce_disabled: typing.Optional[str],
    status_code,
    **kwargs,
):
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()

    requests_mocker.get(
        re.compile("https://host.*/configs$"),
        text=json.dumps(
            ConfigListGenerator.get(
                ConfigListGenerator.ACTIVE,
            )
        ),
        status_code=status_code,
    )
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    requests_mocker.get(re.compile("https://host.*/configs/.*"), text=l3_response, status_code=status_code)

    path_mock.return_value.mkdir.return_value = None

    handler: ProdTasksHandler = ProdTasksHandler(runtime_settings.runtime)
    configs = handler.get_configs()
    handler.keepalived.find_unsynchronized_configs = lambda *args, configs=configs.configs: configs

    assert handler.collect_tasks() == 1
    handler.task = handler.tasks_queue.get_next_task()
    generator = RENDERERS[handler.agent_settings.generator_version]
    config_data = generator(handler.task.config.body).get_full_config()
    manager = handler.keepalived.config_manager

    def get_full_config() -> str:
        names: typing.List[str] = [os.path.basename(call[0][0]) for call in mocked_open.call_args_list]
        configs: typing.List[str] = [call[0][0] for call in mocked_open.return_value.write.call_args_list]
        return "".join(f"# {name}\n{config}\n" for name, config in zip(names, configs))

    manager.save_config(handler.task.config.body, config_data)
    config_rendered: str = get_full_config()

    found_diff = "".join(
        difflib.unified_diff(config_rendered.splitlines(keepends=True), reference_config.splitlines(keepends=True))
    )

    assert not found_diff, found_diff

    if not reference_config_announce_disabled:
        return

    mocked_open.return_value.write.reset_mock()
    mocked_open.reset_mock()

    for vs in handler.task.config.body.vss:
        vs.announce = False

    config_data = generator(handler.task.config.body).get_full_config()
    manager.save_config(handler.task.config.body, config_data)

    assert mock_db_delete.call_args_list[0][0][0] == TEST_SERVICE_FQDN
    assert mock_db_delete.call_args_list[1][0][0] == TEST_SERVICE_FQDN

    assert mock_delete_from_tracking.call_args_list[0][0][0] == CONFIG_REAL_PATH
    assert mock_delete_from_tracking.call_args_list[1][0][0] == CONFIG_REAL_PATH

    config_rendered = get_full_config()

    found_diff = "".join(
        difflib.unified_diff(
            config_rendered.splitlines(keepends=True), reference_config_announce_disabled.splitlines(keepends=True)
        )
    )

    assert not found_diff, found_diff
