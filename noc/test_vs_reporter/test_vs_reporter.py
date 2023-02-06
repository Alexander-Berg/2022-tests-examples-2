import re
from http import HTTPStatus
from queue import Empty
from time import sleep
from unittest.mock import Mock, PropertyMock, patch

import pytest
import requests_mock

from balancer_agent.core.status_codes import ServiceErrorCodes, SuccessOperationCodes
from balancer_agent.operations.balancer_configs.config_containers import VirtualServerState, VSDistinguisher
from balancer_agent.operations.reporters.ipvs_reporter import IPVSStatusReporter as VSStatusReporter
from balancer_agent.operations.vs_state_reporter import VSStatusReporterProcess

AGENT_API_HOSTS = "https://host.*"

HOST_A = "https://host_a"
HOST_B = "https://host_b"
ACTIVE_STATE = "ACTIVE"
IDLE_STATE = "IDLE"

VS_DISTINGUISHER_1069928 = VSDistinguisher(ip="2a02:6b8:0:3400::0", port=80, protocol="TCP")
VS_DISTINGUISHER_1069929 = VSDistinguisher(ip="2a02:6b8:0:3400::0", port=801, protocol="TCP")
VS_DISTINGUISHER_1069930 = VSDistinguisher(ip="2a02:6b8:0:3400::1", port=80, protocol="TCP")
VS_DISTINGUISHER_1069931 = VSDistinguisher(ip="2a02:6b8:0:3400::1", port=801, protocol="TCP")


MOCK_SERVICES_IN_IPVS = {
    VS_DISTINGUISHER_1069928: [],
    VS_DISTINGUISHER_1069929: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069930: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
    VS_DISTINGUISHER_1069931: [
        {"address": "2a02:6b8:0:1482::115", "weight": 1},
        {"address": "2a02:6b8:b010:31::233", "weight": 1},
    ],
}

MOCK_BINDTO_IP = "2a02:6b8:0:e00::13:b0aa"

DUMMY_IP = "1.2.3.4"

STATUS_REPORT_FIELDS = {"status", "ip", "port", "protocol", "rss"}


@pytest.mark.parametrize(
    "matched_ips,services_in_ips,status_code,error_code",
    [
        (
            [VS_DISTINGUISHER_1069928.ip, DUMMY_IP],
            MOCK_SERVICES_IN_IPVS,
            HTTPStatus.OK,
            SuccessOperationCodes.BASE.value,
        ),
        (
            [],
            MOCK_SERVICES_IN_IPVS,
            HTTPStatus.OK,
            SuccessOperationCodes.BASE.value,
        ),
        (
            [VS_DISTINGUISHER_1069928.ip, DUMMY_IP],
            {},
            HTTPStatus.OK,
            SuccessOperationCodes.BASE.value,
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS", return_value=Mock())
@patch("balancer_agent.operations.systems.ip.IP", return_value=Mock())
@patch("balancer_agent.operations.reporters.base.L3_HOST", new_callable=PropertyMock(return_value=HOST_A))
@requests_mock.mock(kw="requests_mocker")
def test_vs_state_reporter_success_cases(
    mocked_l3_host,
    mocked_ip,
    mocked_ipvs,
    matched_ips,
    services_in_ips,
    status_code,
    error_code,
    **kwargs,
):
    requests_mocker = kwargs["requests_mocker"]
    VSStatusReporter.send_report.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    mocked_ip.return_value.find_all.return_value = matched_ips
    mocked_ipvs.return_value.get_services.return_value = services_in_ips

    reporter = VSStatusReporter()
    reporter.can_run.get = Mock(side_effect=[Empty, False])
    reporter.run()

    request_body = mocked_requests_post.last_request.json()
    assert mocked_requests_post.called_once
    assert len(services_in_ips) == len(request_body["vss"])

    assert request_body["error"]["code"] == error_code

    for vs_state in request_body["vss"]:
        assert STATUS_REPORT_FIELDS == vs_state.keys()
        if vs_state["ip"] in matched_ips:
            assert vs_state["status"] == VirtualServerState.ANNOUNCED
        else:
            assert vs_state["status"] == VirtualServerState.DEPLOYED


@pytest.mark.parametrize(
    "matched_ips,services_in_ips,status_code,error_code",
    [
        (
            [VS_DISTINGUISHER_1069928.ip, DUMMY_IP],
            Mock(side_effect=Exception("IPVS call error")),
            HTTPStatus.OK,
            ServiceErrorCodes.UNKNOWN.value,
        ),
        (
            Mock(side_effect=Exception("Collect IPs error")),
            MOCK_SERVICES_IN_IPVS,
            HTTPStatus.OK,
            ServiceErrorCodes.UNKNOWN.value,
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS", return_value=Mock())
@patch("balancer_agent.operations.systems.ip.IP", return_value=Mock())
@patch("balancer_agent.operations.reporters.base.L3_HOST", new_callable=PropertyMock(return_value=HOST_A))
@requests_mock.mock(kw="requests_mocker")
def test_vs_state_reporter_failure_cases(
    mocked_l3_host,
    mocked_ip,
    mocked_ipvs,
    matched_ips,
    services_in_ips,
    status_code,
    error_code,
    **kwargs,
):
    requests_mocker = kwargs["requests_mocker"]
    VSStatusReporter.send_report.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    mocked_ip.return_value.find_all = matched_ips
    mocked_ipvs.return_value.get_services = services_in_ips

    reporter = VSStatusReporter()
    reporter.can_run.get = Mock(side_effect=[Empty, False])
    reporter.run()

    request_body = mocked_requests_post.last_request.json()

    assert request_body["error"]["code"] == error_code
    assert request_body["error"]["message"]


@pytest.mark.parametrize(
    "matched_ips,services_in_ips,status_code",
    [
        (
            [VS_DISTINGUISHER_1069928.ip, DUMMY_IP],
            Mock(side_effect=Exception("IPVS call error")),
            HTTPStatus.BAD_REQUEST,
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS", return_value=Mock())
@patch("balancer_agent.operations.systems.ip.IP", return_value=Mock())
@patch("balancer_agent.operations.reporters.base.L3_HOST", new_callable=PropertyMock(return_value=HOST_A))
@requests_mock.mock(kw="requests_mocker")
def test_vs_state_reporter_backend_failure_retries(
    mocked_l3_host,
    mocked_ip,
    mocked_ipvs,
    matched_ips,
    services_in_ips,
    status_code,
    **kwargs,
):
    requests_mocker = kwargs["requests_mocker"]
    retry_attempts = 5

    VSStatusReporter.send_report.__closure__[1].cell_contents["stop_max_attempt_number"] = retry_attempts
    VSStatusReporter.send_report.__closure__[1].cell_contents["wait_exponential_multiplier"] = 1
    VSStatusReporter.send_report.__closure__[1].cell_contents["wait_exponential_max"] = 0.000001

    mocked_requests_post = requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    mocked_ip.return_value.find_all = matched_ips
    mocked_ipvs.return_value.get_services = services_in_ips

    reporter = VSStatusReporter()
    reporter.can_run.get = Mock(side_effect=[Empty, False])
    reporter.run()

    assert mocked_requests_post.call_count == retry_attempts


@pytest.mark.parametrize(
    "matched_ips,services_in_ips,status_code",
    [
        (
            [VS_DISTINGUISHER_1069928.ip, DUMMY_IP],
            MOCK_SERVICES_IN_IPVS,
            HTTPStatus.OK,
        ),
    ],
)
@patch("balancer_agent.operations.systems.ipvs.IPVS", return_value=Mock())
@patch("balancer_agent.operations.systems.ip.IP", return_value=Mock())
@patch("balancer_agent.operations.reporters.base.L3_HOST", new_callable=PropertyMock(return_value=HOST_A))
@patch("balancer_agent.definitions.AGENT_MODE", new_callable=PropertyMock(return_value="prod"))
@patch("balancer_agent.operations.reporters.base.Queue")
@requests_mock.mock(kw="requests_mocker")
def test_vs_state_reporter_control(
    mocked_queue,
    mock_agent_mode,
    mocked_l3_host,
    mocked_ip,
    mocked_ipvs,
    matched_ips,
    services_in_ips,
    status_code,
    **kwargs,
):
    mocked_queue.return_value.get.side_effect = [Empty, Empty, False]
    requests_mocker = kwargs["requests_mocker"]
    VSStatusReporter.send_report.__closure__[1].cell_contents["stop_max_attempt_number"] = 1

    requests_mocker.post(re.compile(AGENT_API_HOSTS), text="", status_code=status_code)
    mocked_ip.return_value.find_all.return_value = matched_ips
    mocked_ipvs.return_value.get_services.return_value = services_in_ips

    process = VSStatusReporterProcess()
    process.start()

    assert process.worker.is_alive()

    process.stop()

    try_num = 0

    while process.worker.is_alive():
        # to avoid infinite loop if process cannot stop
        if try_num == 1000:
            break

        sleep(0.0001 * try_num)
        try_num += 1

    assert not process.worker.is_alive()
