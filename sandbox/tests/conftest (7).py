import time

import pytest
import signal
import requests
import subprocess as sp

import six
import yatest.common


@pytest.fixture(scope="session")
def proxy_port(port_manager):
    return port_manager.get_port()


@pytest.fixture
def proxy(request, proxy_port, config_path, monkeypatch, serviceapi_simulator, s3_simulator):
    env = {
        "SANDBOX_CONFIG": config_path,
        "Y_PYTHON_ENTRY_POINT": "pyuwsgi:run"
    }
    proxy_path = yatest.common.binary_path("sandbox/proxy/proxy")
    address = ":".join(["localhost", str(proxy_port)])
    cmd = [
        proxy_path,
        "--shared-socket", address,
        "--http-socket", "=0",
        "--chunked-input-limit", str(100 << 20),
        "--http-chunked-input",
        "--lazy-apps",
        "--chunked-input-timeout", "21600",
        "--processes", "2",
        "--threads", "2",
        "--hook-as-user-atexit", "print:goodbye cruel world",
        "--die-on-term",
        "--module", "sandbox.proxy.app:create_app()",
        "--need-app",
        "--sharedarea", "200",
        "--log-format", " ".join([
            '[%(ltime)] %(remote_ip) %(user)',
            '"%(method) %(uri) %(proto)" %(status) %(hsize)+%(rsize)',
            '"%(referer)" "%(uagent)" %(msecs)ms [pid: %(pid)|wid: %(wid)|rid: %(rid)]',
        ])
    ]
    process = sp.Popen(cmd, env=env)

    def finalizer():
        process.kill()
        process.wait(5)
        if process.poll() is None:
            process.send_signal(signal.SIGKILL)

    request.addfinalizer(finalizer)
    while True:
        try:
            if requests.get("http://{}/http_check".format(address)).status_code == six.moves.http_client.OK:
                break
            else:
                time.sleep(0.5)
        except:
            time.sleep(0.5)

    return address
