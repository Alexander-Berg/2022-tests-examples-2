import difflib
import json
import re
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
import requests_mock

from balancer_agent.operations.balancer_configs.config_renderers import RENDERERS
from balancer_agent.operations.settings import SettingsCollector
from balancer_agent.operations.tasks.handlers.ipvs_test_tasks import TestTasksHandler

from .static.configs_rendered import (
    TASK_DYNAMIC_WEIGHT_CONFIG,
    TASK_DYNAMIC_WEIGHT_CONFIG_ANNOUNCE_ENABLED,
    TASK_FWMARK_CONFIG,
    TASK_FWMARK_CONFIG_ANNOUNCE_ENABLED,
    TASK_L4_CONFIG,
    TASK_L4_CONFIG_ANNOUNCE_ENABLED,
    TASK_MAGLEV_AND_HTTP_PROTOCOL_CONFIG,
)
from .static.tasks_from_api import TASK_DYNAMIC_WEIGHT, TASK_FWMARK, TASK_L4, TASK_MAGLEV_AND_HTTP_PROTOCOL

import typing

HOST_A = "host_a"
HOST_B = "host_b"
ACTIVE_STATE = "ACTIVE"
L3_HOSTS_MOCKED_FQDNS = [HOST_A, HOST_B]

MOCK_COLLECTED_CONFIG = {
    "l3_hosts_pool": L3_HOSTS_MOCKED_FQDNS,
    "polling_interval": 300,
    "agent_mode": ACTIVE_STATE,
    "generator_version": 1,
}

AGENT_API_HOSTS = "https://host.*"

MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"


@pytest.mark.parametrize(
    "l3_response,reference_config,reference_config_announce_enabled,status_code",
    [
        (
            [TASK_L4],
            TASK_L4_CONFIG,
            TASK_L4_CONFIG_ANNOUNCE_ENABLED,
            HTTPStatus.OK,
        ),
        (
            [TASK_FWMARK],
            TASK_FWMARK_CONFIG,
            TASK_FWMARK_CONFIG_ANNOUNCE_ENABLED,
            HTTPStatus.OK,
        ),
        (
            [TASK_DYNAMIC_WEIGHT],
            TASK_DYNAMIC_WEIGHT_CONFIG,
            TASK_DYNAMIC_WEIGHT_CONFIG_ANNOUNCE_ENABLED,
            HTTPStatus.OK,
        ),
        (
            [TASK_MAGLEV_AND_HTTP_PROTOCOL],
            TASK_MAGLEV_AND_HTTP_PROTOCOL_CONFIG,
            None,
            HTTPStatus.OK,
        ),
    ],
)
@patch("balancer_agent.operations.balancer_configs.config_containers.VSFWMDataset.bindto", MOCK_BINDTO_IP)
@patch("requests.put")
@patch(
    "balancer_agent.operations.balancer_configs.config_containers.dns.resolver.resolve",
    Mock(**{"return_value.rrset": [MOCK_BINDTO_IP]}),
)
@patch("balancer_agent.operations.balancer_configs.config_containers.is_test_agent", return_value=True)
@patch("balancer_agent.operations.tasks.handlers.base.is_prod_agent", return_value=False)
@requests_mock.mock(kw="requests_mocker")
def test_handle_task(
    mock1,
    mock2,
    mocked_requests_put,
    l3_response,
    reference_config: str,
    reference_config_announce_enabled: typing.Optional[str],
    status_code,
    **kwargs,
):
    mocked_requests_put().status_code = HTTPStatus.NO_CONTENT
    requests_mocker = kwargs["requests_mocker"]
    runtime_settings = SettingsCollector()
    SettingsCollector._collect_settings_callback = lambda *args: MOCK_COLLECTED_CONFIG
    runtime_settings.collect_settings()
    requests_mocker.post(re.compile(AGENT_API_HOSTS), text=json.dumps(l3_response), status_code=status_code)

    handler = TestTasksHandler(runtime_settings.runtime)
    assert handler.collect_tasks() == 1
    handler.task = handler.tasks_queue.get_next_task()
    generator = RENDERERS[handler.agent_settings.generator_version]
    config_rendered = handler.keepalived.config_manager.format_config(
        generator(handler.task.config.body).get_full_config()
    )

    found_diff = "".join(
        difflib.unified_diff(config_rendered.splitlines(keepends=True), reference_config.splitlines(keepends=True))
    )

    assert not found_diff

    if not reference_config_announce_enabled:
        return

    for vs in handler.task.config.body.vss:
        vs.announce = True

    config_rendered = handler.keepalived.config_manager.format_config(
        generator(handler.task.config.body).get_full_config()
    )

    found_diff = "".join(
        difflib.unified_diff(
            config_rendered.splitlines(keepends=True), reference_config_announce_enabled.splitlines(keepends=True)
        )
    )

    assert not found_diff
