from unittest.mock import Mock, patch

import pytest
from tvmauth import TvmClientStatus

from balancer_agent.core.tvm import TVM_CLIENT_SETTINGS, TVMClient, TvmEnabledStatus, TvmRunningStatus

TVM_LAST_ERROR = "OK"


class TVMStatus:
    def __init__(self, code, last_error):
        self.code = code
        self.last_error = str.encode(last_error)


class FakeTvmClient:
    def __init__(
        self,
        *args,
        tvm_running=True,
        tvm_status=True,
        tvm_error=True,
        **kwargs,
    ):
        self.tvm_running = tvm_running
        self.tvm_status = tvm_status
        self.tvm_error = tvm_error

    def is_alive(self):
        return not self.tvm_running.value

    @property
    def status(self):
        return TVMStatus(self.tvm_status.value, self.tvm_error)

    @property
    def _thread(self):
        return self

    def get_service_ticket_for(self, tvm_id):
        return f"ticket_for_{tvm_id}"


def tvm_exception(*args):
    raise Exception("TVM Error")


@pytest.mark.parametrize(
    "tvm_enabled,tvm_running,tvm_status,tvm_error,expected",
    [
        (
            TvmEnabledStatus.ENABLED,
            TvmRunningStatus.RUNNING,
            TvmClientStatus.Ok,
            TVM_LAST_ERROR,
            TVMClient.STATUS(
                TvmEnabledStatus.ENABLED.value,
                TvmRunningStatus.RUNNING.value,
                TvmClientStatus.Ok.value,
                TVM_LAST_ERROR,
            ),
        ),
        (
            TvmEnabledStatus.DISABLED,
            None,
            None,
            None,
            TVMClient.STATUS(
                TvmEnabledStatus.DISABLED.value,
                TvmRunningStatus.STOPPED.value,
                TVMClient.UNKNOWN_CODE,
                TVMClient.UNKNOWN_ERROR,
            ),
        ),
        (
            TvmEnabledStatus.ENABLED,
            TvmRunningStatus.STOPPED,
            TvmClientStatus.Error,
            TVM_LAST_ERROR,
            TVMClient.STATUS(
                TvmEnabledStatus.ENABLED.value,
                TvmRunningStatus.STOPPED.value,
                TvmClientStatus.Error.value,
                TVM_LAST_ERROR,
            ),
        ),
    ],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
@patch("balancer_agent.core.tvm.Path")
def test_tvm_client_status(mocked_path, mocked_settings, tvm_enabled, tvm_running, tvm_status, tvm_error, expected):
    with patch(
        "balancer_agent.core.tvm.TVMClient._create_tvm_client",
        return_value=FakeTvmClient(
            tvm_running=tvm_running, tvm_status=tvm_status, tvm_error=tvm_error, tvm_last_error=tvm_error
        ),
    ) as _:

        client = TVMClient(not tvm_enabled.value)

        assert client.status == expected


@pytest.mark.parametrize(
    "tvm_enabled,tvm_running,tvm_status,tvm_error,expected",
    [
        (
            TvmEnabledStatus.ENABLED,
            TvmRunningStatus.STOPPED,
            TvmClientStatus.Ok,
            TVM_LAST_ERROR,
            TVMClient.STATUS(
                TvmEnabledStatus.ENABLED.value,
                TvmRunningStatus.STOPPED.value,
                TVMClient.UNKNOWN_CODE,
                TVMClient.UNKNOWN_ERROR,
            ),
        ),
    ],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
@patch("balancer_agent.core.tvm.Path")
def test_tvm_client_status_exception(
    mocked_path, mocked_settings, tvm_enabled, tvm_running, tvm_status, tvm_error, expected
):
    with patch(
        "balancer_agent.core.tvm.TVMClient._create_tvm_client",
        return_value=FakeTvmClient(
            tvm_running=tvm_running, tvm_status=tvm_status, tvm_error=tvm_error, tvm_last_error=tvm_error
        ),
    ) as _:

        FakeTvmClient.status = property(tvm_exception)
        client = TVMClient(not tvm_enabled.value)

        assert client.status == expected


@pytest.mark.parametrize(
    "tvm_enabled,expected",
    [
        (
            TvmEnabledStatus.ENABLED,
            {TVMClient.SERVICE_TICKET_HEADER: f"ticket_for_{TVM_CLIENT_SETTINGS.destinations.l3mgr}"},
        ),
    ],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
@patch("balancer_agent.core.tvm.Path")
def test_get_header_with_ticket(mocked_path, mocked_settings, tvm_enabled, expected):
    with patch("balancer_agent.core.tvm.TVMClient._create_tvm_client", return_value=FakeTvmClient()) as _:

        client = TVMClient(not tvm_enabled.value)

        assert client.get_header_with_ticket() == expected


@pytest.mark.parametrize(
    "tvm_enabled",
    [TvmEnabledStatus.ENABLED],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
@patch("balancer_agent.core.tvm.Path")
def test_get_header_with_ticket_exception(mocked_path, mocked_settings, tvm_enabled):
    with patch("balancer_agent.core.tvm.TVMClient._create_tvm_client", return_value=FakeTvmClient()) as _:

        client = TVMClient(not tvm_enabled.value)
        FakeTvmClient.get_service_ticket_for = property(tvm_exception)

        with pytest.raises(Exception):
            TVMClient._get_service_ticket.__closure__[1].cell_contents["stop_max_attempt_number"] = 1
            client.get_header_with_ticket()


@pytest.mark.parametrize(
    "tvm_enabled",
    [TvmEnabledStatus.ENABLED],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
def test_create_cache_dir(mocked_settings, tvm_enabled):
    with patch("balancer_agent.core.tvm.TVMClient._create_tvm_client", return_value=FakeTvmClient()) as _, patch(
        "balancer_agent.core.tvm.Path", Mock()
    ) as mocked_path:

        client = TVMClient(not tvm_enabled.value)
        client._create_cache_dir()

        assert mocked_path.return_value.mkdir.called_once()


@pytest.mark.parametrize(
    "tvm_enabled",
    [TvmEnabledStatus.DISABLED],
)
@patch("balancer_agent.core.tvm.TvmApiClientSettings")
def test_tvm_disabled(mocked_settings, tvm_enabled):
    with patch(
        "balancer_agent.core.tvm.TVMClient._create_tvm_client", return_value=FakeTvmClient(tvm_enabled=tvm_enabled)
    ) as _, patch("balancer_agent.core.tvm.Path", Mock()):

        client = TVMClient(not tvm_enabled.value)

        assert not client._client
        assert not client._enabled
