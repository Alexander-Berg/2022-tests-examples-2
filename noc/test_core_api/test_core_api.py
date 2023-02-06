import http

import requests

import balancer_agent.core.api as core_api
import balancer_agent.core.metrics as core_metrics

SERVER_PORT = 60890


# @patch.object("balancer_agent.core.tvm", "TVMClient", return_value=Mock())
def test_not_found():
    server = core_api.Server("localhost", SERVER_PORT)
    server.start()

    try:
        assert requests.get(f"http://localhost:{SERVER_PORT}/not-found").status_code == http.HTTPStatus.NOT_FOUND
    finally:
        server.stop()


def test_status():
    def _get_status_json():
        r = requests.get(f"http://localhost:{SERVER_PORT}/api/v1/status")
        assert r.status_code == http.HTTPStatus.OK

        return r.json()

    server = core_api.Server("localhost", SERVER_PORT)
    server.start()

    try:
        r = _get_status_json()
        assert r["errors"] == 0

        core_metrics.METRICS_REPORTER.set_exception(RuntimeError("test exception"))
        r = _get_status_json()
        assert r["errors"] == 1
        assert "RuntimeError" in r["exceptions"]
        assert r["exceptions"]["RuntimeError"] == 1

        core_metrics.METRICS_REPORTER.set_tvm("tvm_enabled", 0)
        r = _get_status_json()
        assert r["tvm"] == {"tvm_enabled": 0}
        assert r["updated_at"] > r["created_at"]

    finally:
        server.stop()
