import time
import subprocess as sp

import six
import pytest

pytest_plugins = (
    "sandbox.tests.common.config",
    "sandbox.tests.common.path",
    "sandbox.tests.common.network",
)


@pytest.fixture(scope="session")
def tvmtool(request, tvmtool_port, config_tvmtool, tvmtool_binary, minimal_common_config_path):
    assert minimal_common_config_path  # Why `@pytest.mark.usefixtures("minimal_common_config_path")` doesn't work here?
    tvmtool_proc = sp.Popen(
        [tvmtool_binary, "-c", config_tvmtool, "--port", str(tvmtool_port), "-u"],
        env={"QLOUD_TVM_TOKEN": "DEADBEEF" * 4}
    )

    check_url = "http://[::1]:{}/tvm/ping".format(tvmtool_port)

    start = time.time()
    while time.time() - start < 5:
        try:
            if six.moves.urllib.request.urlopen(check_url, timeout=1).read() == b"OK":
                break
        except Exception:
            time.sleep(.1)
    else:
        raise Exception("Failed to start tvmtool")

    def terminate():
        tvmtool_proc.terminate()
        tvmtool_proc.communicate()

    request.addfinalizer(terminate)
