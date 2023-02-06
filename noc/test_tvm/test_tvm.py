import pytest
from tvmauth import TvmClientStatus

from balancer_agent.core.tvm import TVMClient, TvmEnabledStatus, TvmRunningStatus

TMP_CACHE_DIR = "/tmp/tvm_cache"
TVM_LAST_ERROR = "OK"


@pytest.mark.parametrize(
    "tvm_status,expected_running,expected_stopped",
    [
        (
            TvmClientStatus.Ok,
            TVMClient.STATUS(
                TvmEnabledStatus.ENABLED.value,
                TvmRunningStatus.RUNNING.value,
                TvmClientStatus.Ok.value,
                TVM_LAST_ERROR,
            ),
            TVMClient.STATUS(
                TvmEnabledStatus.ENABLED.value,
                TvmRunningStatus.STOPPED.value,
                TVMClient.UNKNOWN_CODE,
                TVMClient.UNKNOWN_ERROR,
            ),
        )
    ],
)
def test_tvm_client_status(tvm_status, expected_running, expected_stopped):
    TVMClient.CACHE_DIR = TMP_CACHE_DIR
    client = TVMClient(enabled=True)

    assert client.status == expected_running
    assert client.get_header_with_ticket()

    client._client.stop()

    assert client.status == expected_stopped
