import os
import sys
import functools

import py
import six
import pytest
import logging
import requests

if six.PY2:
    import subprocess32 as sp
else:
    import subprocess as sp

from sandbox.common import system

from . import utils as tests_utils


pytest_plugins = (
    "sandbox.tests.common.utils",
)


@pytest.fixture(scope="session")
def sandbox_dir():
    return str(py.path.local(__file__).dirpath(os.path.pardir, os.path.pardir))


@pytest.fixture(scope="session")
def sandbox_tasks_dir(request, sandbox_dir):
    tasks = request.config.getoption("--tasks", sandbox_dir, skip=True)
    if not system.inside_the_binary():
        sys.path = [tasks] + [_ for _ in sys.path if _ != tasks]
    return tasks


@pytest.fixture(scope="session")
def runtime_dir(request, sandbox_dir):

    if system.inside_the_binary():
        import yatest.common
        return yatest.common.output_path()

    rtd = request.config.getoption("--runtime", None)
    if rtd:
        rtd = py.path.local(rtd)
    else:
        rtd = py.path.local(sandbox_dir).dirpath(os.path.pardir, "runtime_data")
    rtd.ensure_dir()
    return str(rtd)


@pytest.fixture(scope="session")
def tests_common_path(runtime_dir):
    if system.inside_the_binary():
        import yatest.common
        path = py.path.local(yatest.common.output_path())
    else:
        path = py.path.local(runtime_dir).join("tests")
    path.ensure_dir()
    return str(path)


@pytest.fixture(scope="session")
def tests_path_getter(tests_common_path, work_id):
    if system.inside_the_binary() and work_id.startswith("master"):
        return functools.partial(os.path.join, tests_common_path)
    path = py.path.local(tests_common_path).join("test_{}".format(work_id))
    path.ensure_dir()
    if work_id.startswith("master"):
        link_target = os.path.join(tests_common_path, "master")
        if os.path.lexists(link_target):
            os.remove(link_target)
        os.symlink(str(path), link_target)
    return functools.partial(os.path.join, str(path))


@pytest.fixture(scope="session")
def ya_tool():
    return str(py.path.local(__file__).dirpath(os.path.pardir, os.path.pardir, os.path.pardir, "ya"))


def _binary_path(rel_path, request, sandbox_dir, ya_tool, tests_common_path):
    # if binary is already built, just return path to it
    if system.inside_the_binary():
        import yatest.common
        return yatest.common.binary_path(os.path.join("sandbox", rel_path))

    # otherwise call `ya make` to build binary on fly
    logging.debug("Prepared binary %s is not found, building it...", rel_path)
    path = os.path.join(sandbox_dir, rel_path)
    if os.path.exists(path):
        return path

    def build():
        sp.check_output([ya_tool, "make", os.path.dirname(path)])

    tests_utils.call_once(request, tests_common_path, build)
    assert os.path.exists(path), ("Binary {} still does not exist. Seems that build was not run. "
                                  "If your start tests locally, try 'rm {}/*.lock'".format(path, tests_common_path))
    return path


@pytest.fixture(scope="session")
def serviceapi_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("serviceapi/serviceapi", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def taskbox_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("taskbox/dispatcher/taskbox", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def preexecutor_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("executor/preexecutor/preexecutor", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def services_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("services/sandbox-services", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def py3_sources_binary(request, sandbox_dir, ya_tool, tests_common_path):
    if system.inside_the_binary():
        return ""
    else:
        return _binary_path("scripts/py3_sources/py3_sources", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def taskboxer_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path(
        "projects/sandbox/taskboxer/isolated/bin/taskboxer", request, sandbox_dir, ya_tool, tests_common_path
    )


@pytest.fixture(scope="session")
def tvmtool_binary(request, tests_common_path):
    path = os.path.join(tests_common_path, "tvmtool")

    def fetch():
        r = requests.get("https://proxy.sandbox.yandex-team.ru/last/TVM_TOOL_BINARY", params={"arch": "linux"})
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        st = os.stat(path)
        os.chmod(path, st.st_mode | 0o100)  # make executable

    tests_utils.call_once(request, tests_common_path, fetch)
    assert os.path.exists(path)
    return path


@pytest.fixture(scope="session")
def fileserver_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("fileserver/fileserver", request, sandbox_dir, ya_tool, tests_common_path)


@pytest.fixture(scope="session")
def agentr_binary(request, sandbox_dir, ya_tool, tests_common_path):
    return _binary_path("agentr/bin/agentr", request, sandbox_dir, ya_tool, tests_common_path)


def _check_uds_pathname(path):
    assert len(path) < 108, "Unix domain socket pathname must be shorter than 108 characters: {}".format(path)
    return path


@pytest.fixture(scope="session")
def phazotron_socket(work_id):
    return _check_uds_pathname(os.path.join("/tmp", "sandbox-test_phazotron_{}.sock".format(work_id)))


@pytest.fixture(scope="session")
def agentr_socket(work_id):
    return _check_uds_pathname(os.path.join("/tmp", "sandbox-test_agentr_{}.sock".format(work_id)))


@pytest.fixture(scope="session")
def fileserver_socket(work_id):
    return _check_uds_pathname(os.path.join("/tmp", "sandbox-test_fileserver_{}.sock".format(work_id)))
