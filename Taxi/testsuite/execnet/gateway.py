import itertools
import os
import socket
import subprocess
import sys

from . import channel

RUNNER = """
import gevent.monkey
gevent.monkey.patch_all()

import importlib.util
import socket

import execnet.channel

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(%r)
channel = execnet.channel.Channel(sock)

xdist_remote_spec = importlib.util.spec_from_file_location(
    '__channelexec__', %r,
)
module = importlib.util.module_from_spec(xdist_remote_spec)
module.channel=channel
xdist_remote_spec.loader.exec_module(module)
"""


class RSync:
    def __init__(self):
        raise NotImplementedError('RSync')


class RInfo:
    version_info = sys.version_info[:5]
    platform = sys.platform
    cwd = os.getcwd()
    pid = os.getpid()


class Gateway:
    def __init__(self, spec):
        self.spec = spec
        self.id = spec.id
        self.process = None
        socket.setdefaulttimeout(10)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_path = '/tmp/myexecnet-%s-%s.sock' % (os.getpid(), self.id)
        self.sock.bind(self.sock_path)
        self.sock.listen(1)

    def remote_exec(self, module):
        assert self.process is None
        assert module.__name__ == 'xdist.remote', module.__name__
        self.process = subprocess.Popen(
            [
                sys.executable,
                '-u',
                '-c',
                RUNNER % (self.sock_path, module.__file__),
            ],
        )
        self.connection, _ = self.sock.accept()
        self.connection.settimeout(None)
        self.channel = channel.Channel(self.connection)
        return self.channel

    def terminate(self, exit_timeout=None):
        self.channel.close()
        if exit_timeout is not None:
            self.process.terminate()
            try:
                self.process.wait(exit_timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
        else:
            self.process.kill()
        os.remove(self.sock_path)

    def _rinfo(self):
        return RInfo()


class Group:
    _id = itertools.count()

    def __init__(self):
        self._gateways = []

    def allocate_id(self, spec):
        spec.id = 'gw%d' % next(self._id)

    def makegateway(self, spec):
        gateway = Gateway(spec)
        self._gateways.append(gateway)
        return gateway

    def terminate(self, exit_timeout=None):
        for gateway in self._gateways:
            gateway.terminate(exit_timeout)


class XSpec:
    def __init__(self, arg):
        assert arg == 'popen'
        self.chdir = None
        self.popen = True
        self.id = None
