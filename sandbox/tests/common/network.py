import os
import random
import socket
import functools

import pytest

from sandbox.common import system
import sandbox.common.itertools as cit

import sandbox.tests.common as tests_common


pytest_plugins = (
    "sandbox.tests.common.path",
    "sandbox.tests.common.utils",
)


@pytest.fixture(scope="session")
def port_manager(request, host, tests_common_path):
    if system.inside_the_binary():
        from yatest.common import network
        pm = network.PortManager()
    else:
        pm = PortManager(request, host, tests_common_path)

    def release_ports():
        pm.release()
    request.addfinalizer(release_ports)

    return pm


@pytest.fixture(scope="session")
def legacy_server_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def serviceapi_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def client_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def fileserver_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def serviceq_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def taskbox_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def devbox_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def tvmtool_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def mds_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def abc_port(port_manager):
    return port_manager.get_port()


@pytest.fixture(scope="session")
def s3_port(port_manager):
    return port_manager.get_port()


def wait_until_port_is_ready(host, port, timeout):

    def check_port():
        try:
            s = socket.create_connection((host, port))
            s.close()
            return True
        except socket.error:
            pass

    ret, _ = cit.progressive_waiter(0, 1, timeout, check_port)
    if not ret:
        raise Exception("Waited for port '{}' for {}s, but it's not ready".format(port, timeout))


class PortManager(object):

    TEST_PORTS_RANGE = (11000, 29999)  # range of ports used for random selection for test services

    def __init__(self, request, host, tests_common_path):
        random.seed()  # uses os.urandom underneath
        self._request = request
        self._host = host
        self._busy_ports_file_path = os.path.join(tests_common_path, "busy_ports")

    def _remove_port(self, port):
        with tests_common.global_lock:
            with open(self._busy_ports_file_path, "a+") as f:
                busy_ports = f.read().split()
            try:
                busy_ports.remove(str(port))
            except ValueError:
                pass
            with open(self._busy_ports_file_path, "w+") as f:
                f.write(" ".join(busy_ports))

    def release(self):
        pass

    def get_port(self):
        import socket
        ports_filename = self._busy_ports_file_path
        with tests_common.global_lock:
            with open(ports_filename, "a+") as f:
                busy_ports = f.read().split()
            while True:
                port = random.randint(*self.TEST_PORTS_RANGE)
                if str(port) in busy_ports:
                    continue
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self._host, port))
                    sock.close()
                except socket.error:
                    break
                else:
                    pass
            busy_ports.append(str(port))
            with open(ports_filename, "w+") as f:
                f.write(" ".join(busy_ports))
        self._request.addfinalizer(functools.partial(self._remove_port, port))
        return port
