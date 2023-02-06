from __future__ import print_function, absolute_import

import importlib
import os
import random
import socket

import gevent
import gevent.queue
import pytest

from sandbox.common.joint import errors
from sandbox.common.joint import tests
from sandbox.common.joint.client import RPCClientGevent as RPCClient
from sandbox.common.joint.tests import context

try:
    LocalServer = importlib.import_module("sandbox.common.joint.tests.py3.isolated").LocalServer
except (ImportError, SyntaxError):
    LocalServer = importlib.import_module("sandbox.common.joint.tests.py2").LocalServer

ctx = context.Context(context.Context.Config({
    "rpc": {
        "connection_magic": 0xDEADBEAF,
        "handshake_send_timeout": 1,
        "handshake_receive_timeout": 1,
        "idle_timeout": 6,                  # then no requests are processed - close connection after 10 secs
        "socket_nodelay": True,             # we will send a lot of small packets
        "socket_nodelay_cutoff": 2097152,   # 2mb
        "socket_receive_buffer": 131072,    # 128kb
        "socket_send_buffer": 131072,       # 128kb
        "socket_timeout": 6,                # raw socket timeout, should be bigger than any other
        "receive_buffer": 16384,            # 16kb
        "uid_generation_tries": 10,
        "uid_generation_retry_sleep": 0.1,
        "pingpong_sleep_seconds": 0,

        "client": {
            "connect_timeout": 1,
            "socket_nodelay": True,
            "socket_receive_buffer": 131072,
            "socket_send_buffer": 131072,
            "socket_timeout": 6,
            "idle_timeout": 1,
            "ping_tick_time": 1,            # ping every 10 seconds
            "ping_wait_time": 1,
            "receive_buffer": 16384,
            "job_registration_timeout": 2,
        },
    },

    "server": {
        "host": "",
        "port": 0,
        "unix": None,
        # "host": None,
        # "port": None,
        # "unix": "/tmp/serviceq.%d.rpc.test.sock",

        "backlog": 10,
        "magic_receive_timeout": 10,
        "max_connections": 32,
    },
}))

ctx.stalled_jobs_timeout = .5


def setup_function(func):
    print("")  # Avoid log entries printing on the same line as the result test

    global ctx
    func.ctx = ctx
    port = func.ctx.cfg.server.port
    host = func.ctx.cfg.server.host if port is not None else func.ctx.cfg.server.unix
    if port is None:
        host %= os.getpid()
        func.ctx.cfg.server.unix = host
        if os.path.exists(host):
            os.unlink(host)
    else:
        for i in range(0, 3):
            port = random.randrange(10000, 30000)
            try:
                RPCClient(cfg=func.ctx.cfg.rpc, host="::1", port=port).connect()
            except socket.error:
                break
        func.ctx.cfg.server.port = port

    func.srv = LocalServer(func.ctx).start()
    # Connect to the local server
    func.client = RPCClient(cfg=func.ctx.cfg.rpc, host="::1", port=port)


def teardown_function(func):
    print("")  # Avoid log entries printing on the same line as the result test
    # Stop both client and server
    gevent.sleep(0.1)  # Take time for server to cleanup a bit
    func.client.stop()
    func.srv.stop()


def test_stalled_jobs():
    ctx.stalled = None
    client = test_stalled_jobs.client
    client.call("hang", .1, ctx.stalled_jobs_timeout / 5.).wait(1)
    assert ctx.stalled is None

    with pytest.raises(errors.CallTimeout):
        client.call("hang", 1, ctx.stalled_jobs_timeout / 5.).wait(.1)
    gevent.sleep(ctx.stalled_jobs_timeout * 2)
    assert ctx.stalled is None

    with pytest.raises(errors.CallTimeout):
        client.call("hang", 1, ctx.stalled_jobs_timeout * 2).wait(.1)
    assert ctx.stalled is None
    gevent.sleep(ctx.stalled_jobs_timeout * 2)
    assert ctx.stalled is not None


def test_basic():
    ctx = test_basic.ctx
    client = test_basic.client

    # Attempt to connect to non-listening port
    try:
        port = client.port
        host = client.host
        if port is None:
            host += ".notexistingsocket"
        else:
            port += 1
        RPCClient(cfg=ctx.cfg.rpc, host=host, port=port).ping()
        assert False and "This point should not be reached - the operation should fail."
    except socket.error:
        pass

    # Perform server ping
    client.ping()

    # Check that call to a method, which will raise an exception will not be raised on client-side,
    # if the client will immediately discard the method call result.
    call = client.call("exception")
    gevent.sleep(0.1)  # Get some sleep to take a chance for server to perform the actual call

    # Check that call to a non-existing method and discarding the result immediately
    # will not raise any exceptions on client-side.
    call = client.call("noSuchMethod")
    gevent.sleep(0.5)  # Get some sleep to take a chance for server to perform the actual call

    # Check that server-side exception correctly restored on client-side.
    call = client.call("exception")
    try:
        call.wait()
    except errors.ServerError as ex:
        assert isinstance(ex, tests.ServerSideException)
        assert ex.args[0] == "Something wrong!"
        assert ex.args[1] == 42
        assert ex.sid == call.sid
        assert ex.jid == call.jid
        assert len(ex.tb)

    try:
        client.call('exception', False).wait()
    except errors.ServerError as ex:
        assert ex.__class__ is errors.ServerError
        assert ex.args[0] == "Something wrong!"
        assert ex.args[1] == 42
        assert len(ex.tb)

    # Check regular method processing
    for i in range(0, 2):
        magic = random.random()
        assert client.call("ping", magic).wait(timeout=0.1) == magic
        # Check client will resurrect after reactor stop
        client.stop()

    # Check regular method processing with intermediate server pinging
    call = client.call("ping", 42)
    client.ping()
    assert call.wait() == 42

    call = client.call("range2", 2, 8)
    assert next(call) == 2
    client.ping()
    assert next(call) == 3
    client.ping()
    assert call.wait() == 10

    call = client.call("duplex_gen", 2, 10)
    gen = call.generator
    sample = iter(range(2, 10))
    for i in gen:
        assert i == next(sample)
    assert call.wait() == 12

    call = client.call("duplex_gen", 2, 10)
    gen = call.generator
    sample = iter(range(2, 5))
    i = None
    for i in gen:
        if i == 5:
            try:
                assert gen.send(True) == i
            except StopIteration:
                pass
        else:
            assert next(sample) == i
    assert i == 5
    assert call.wait() == 12

    call = client.call("duplex_gen2", 1, 11)
    gen = call.generator
    sample = iter(range(1, 11))
    i = None
    for i in gen:
        if i % 2:
            i += 1
            assert gen.send(True) == i
        else:
            assert next(sample) == i
    assert i == 10
    assert call.wait() == sum(range(1, 11, 2))

    # Check methods with intermediate results returning
    for meth in ["range", "range2"]:
        call = client.call(meth, 8, 20)
        for i in call:
            assert 8 <= i < 20
        assert call.wait(timeout=0) == 28

    # Check non-existing methods call
    call = client.call("noSuchMethod", "foo")
    try:
        call.wait()
        assert False and "This point should not be reached - the operation should fail."
    except errors.CallError as ex:
        # Check also that the exception provides session and job IDs
        assert ex.args[1] == call.sid
        assert ex.args[2] == call.jid

    # Check timeout with intermediate results fetch
    try:
        call = client.call("range", 8, 20)
        for i in call.iter(timeout=0.1):
            assert 8 <= i < 20
        assert False and "This point should not be reached - the operation should time out."
    except errors.CallTimeout:
        pass

    # Check timeout on simple call form
    try:
        client.call("range", 8, 20).wait(timeout=0.1)
        assert False and "This point should not be reached - the operation should time out."
    except errors.CallTimeout:
        pass

    # Check empty generator call
    call = client.call("empty_gen")
    for i in call:
        assert False
    assert call.wait(timeout=0) is None

    # Check the reactor will correctly handle just-created-and-immediately-dropped job
    client.call("ping", 42).__del__()

    # Check reactor abort
    assert client.call("ping", 0xC01CDE).wait(timeout=0.1) == 0xC01CDE
    c = client.call("ping", 42)
    old_rsid = c.reactor.sid

    # `gevent.queue.Queue` cannot be monkey-patched, so we should perform some more magic
    class Queue(object):
        def __init__(self, original):
            self.__queue = original

        def __getattr__(self, item):
            return getattr(self.__queue, item) if item != "get" else self.get

        def get(self, *args, **kwargs):
            data = self.__queue.get(*args, **kwargs)
            if data[0] == "REGISTERED":
                data[0] = "COMPLETE"
            return data

    c.job.queue = Queue(c.job.queue)

    try:
        c.wait()
        assert "This point should never be reached!"
    except errors.ProtocolError:
        pass

    # Here reactor should be restarted finely
    c = client.call("ping", 0xC01CDE)
    assert c.wait(timeout=0.1) == 0xC01CDE
    assert c.reactor.sid != old_rsid

    # Let"s perform several jobs simultaneously
    def grn(client):
        for meth in ["range", "range2"]:
            call = client.call(meth, 8, 20)
            for i in call:
                assert 8 <= i < 20
            assert call.wait(timeout=0) == 28

    grns = [gevent.spawn(grn, client) for i in range(0, 3)]
    for g in grns:
        g.get()
