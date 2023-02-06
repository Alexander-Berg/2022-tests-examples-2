import subprocess as sp

import yatest.common


def test_cheaper_algo():
    proxy_path = yatest.common.binary_path("sandbox/proxy/proxy")
    stdout, stderr = sp.Popen(
        [proxy_path, "--cheaper-algo-list"],
        env={"Y_PYTHON_ENTRY_POINT": "pyuwsgi:run"},
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    ).communicate()
    algo_list = []
    algo_list_started = False
    for line in stderr.decode().splitlines():
        if line == "*** uWSGI loaded cheaper algorithms ***":
            algo_list_started = True
        elif line == "--- end of cheaper algorithms list ---":
            break
        elif algo_list_started:
            algo_list.append(line)

    assert "busyness" in algo_list, "Required cheaper algo is not in uWSGI build. \nSTDOUT:\n{}\nSTDERR:\n{}".format(
        stdout,
        stderr,
    )
