import os
import sys
import subprocess as sp

import py
import pytest

from sandbox import common

__all__ = ["qserver_with_data_proc", "qclient", "serviceq_server", "serviceq"]


@pytest.fixture(scope="session")
def serviceq_server(request, tests_path_getter, serviceq_config_path, sandbox_dir):
    py.path.local(tests_path_getter("logs", "")).ensure_dir()
    py.path.local(tests_path_getter("run", "")).ensure_dir()
    if common.system.inside_the_binary():
        # noinspection PyUnresolvedReferences
        import yatest.common
        serviceq_proc = sp.Popen([yatest.common.binary_path("sandbox/serviceq/bin/serviceq")], close_fds=True)
    else:
        serviceq_proc = sp.Popen(
            [sys.executable, os.path.join(sandbox_dir, "serviceq", "bin", "server.py")], close_fds=True
        )

    def terminate():
        serviceq_proc.terminate()
        serviceq_proc.communicate()

    request.addfinalizer(terminate)


@pytest.fixture()
def serviceq(serviceq_server):
    import sandbox.serviceq.client
    import sandbox.serviceq.config
    import sandbox.serviceq.errors

    settings = sandbox.serviceq.config.Registry()
    settings.reload()
    qclient = sandbox.serviceq.client.Client(settings)

    def ready():
        try:
            qclient.sync([], reset=True)
            return True
        except sandbox.serviceq.errors.QRetry:
            return False

    assert common.utils.progressive_waiter(0, 0.1, 10, ready)[0]
    return qclient


@pytest.fixture()
def qserver_with_data_proc(serviceq, test_queue, qclient):
    serviceq.sync([[task_id, item[0], item[1], item[2]] for task_id, item in test_queue.iteritems()], reset=True)


@pytest.fixture()
def qclient(serviceq_config_path):
    import sandbox.serviceq.client
    import sandbox.serviceq.config
    settings = sandbox.serviceq.config.Registry()
    settings.reload()
    return sandbox.serviceq.client.Client(sandbox.serviceq.config.Registry())
