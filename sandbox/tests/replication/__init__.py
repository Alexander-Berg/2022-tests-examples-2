import copy
import socket
import logging

import py
import pytest
import gevent
import gevent.event
import zake.fake_client
import kazoo.handlers.gevent

from sandbox import common

import sandbox.common.joint.errors as jerrors

import sandbox.serviceq.state as qstate
import sandbox.serviceq.types as qtypes
import sandbox.serviceq.errors as qerrors
import sandbox.serviceq.election as qelection

from sandbox.serviceq.tests.client import utils as client_utils


def setup_logger(logger, prefix):
    formatter = logging.Formatter("[{}] %(asctime)s - %(message)s".format(prefix))
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@pytest.fixture()
def fake_contender():
    class FakeContender(qelection.Contender):
        __storage = zake.fake_client.FakeClient().storage

        def __init__(self, hosts, zk_root, name, **kws):
            kws["do_fork"] = False
            self.__stop_event = gevent.event.Event()
            kws.setdefault("logger", setup_logger(logging.getLogger("contender_{}".format(name)), name))
            super(FakeContender, self).__init__(hosts, zk_root, name, **kws)

        def _create_zk_client(self):
            zk_client = zake.fake_client.FakeClient(
                storage=self.__storage,
                handler=kazoo.handlers.gevent.SequentialGeventHandler()
            )
            zk_client.start()
            return zk_client

        def _start_primary_lock_thread(self):
            self._primary_lock_thread = gevent.spawn(self._primary_lock_watcher)

        @property
        def _primary_lock_thread_alive(self):
            return self._primary_lock_thread and not self._primary_lock_thread.dead

        def _stop_primary_lock_thread(self):
            self._primary_lock.cancel()
            self._primary_lock_thread.kill()
            self._primary_lock_thread.join()

        def _start_primary_watchdog_thread(self):
            pass

        def start(self):
            self.__stop_event.clear()
            return super(FakeContender, self).start()

        def stop(self):
            ret = super(FakeContender, self).stop()
            self.__stop_event.set()
            return ret

        def wait(self):
            self.__stop_event.wait()

    return FakeContender


# noinspection PyUnusedLocal
# noinspection PyShadowingNames
@pytest.fixture()
def config(serviceq_config_path, monkeypatch):
    import sandbox.serviceq.config
    config = sandbox.serviceq.config.Registry()
    config.reload()
    monkeypatch.setattr(config.serviceq.zookeeper, "enabled", True)
    monkeypatch.setattr(config.serviceq.server.server, "host", "")
    monkeypatch.setattr(config.serviceq.server.server, "port", 0)
    return config


# noinspection PyUnusedLocal
# noinspection PyShadowingNames
@pytest.fixture()
def server(config, monkeypatch, fake_contender, tests_path_getter):
    import gevent.lock
    import sandbox.serviceq.server
    py.path.local(tests_path_getter("run", "")).ensure_dir()
    monkeypatch.setattr(common.utils.singleton_property, "_lock", gevent.lock.RLock())
    monkeypatch.setattr(sandbox.serviceq.server.Server, "Contender", fake_contender)
    return sandbox.serviceq.server.Server


# noinspection PyShadowingNames
@pytest.fixture()
def qclient(config, monkeypatch):
    import sandbox.serviceq.client
    import sandbox.common.joint.client
    monkeypatch.setattr(sandbox.serviceq.client.Client, "RPCClient", sandbox.common.joint.client.RPCClientGevent)
    client = sandbox.serviceq.client.Client(config)
    return client


# noinspection PyUnusedLocal
# noinspection PyShadowingNames
# noinspection PyUnresolvedReferences
@pytest.mark.serviceq_replication
class TestQReplication(object):
    full_queue = [
        qtypes.TaskQueueItem(task_id=2, priority=30, hosts=[
            qtypes.TaskQueueHostsItem(score=3, host="host3"),
            qtypes.TaskQueueHostsItem(score=2, host="host2"),
            qtypes.TaskQueueHostsItem(score=1, host="host1")
        ], task_ref=None, task_info=qtypes.TaskInfo(type="T2", owner="O2"), score=None),
        qtypes.TaskQueueItem(task_id=3, priority=20, hosts=[
            qtypes.TaskQueueHostsItem(score=2, host="host1"),
            qtypes.TaskQueueHostsItem(score=1, host="host2")
        ], task_ref=None, task_info=qtypes.TaskInfo(type="T3", owner="O3"), score=None),
        qtypes.TaskQueueItem(task_id=4, priority=20, hosts=[
            qtypes.TaskQueueHostsItem(score=2, host="host2"),
            qtypes.TaskQueueHostsItem(score=1, host="host1")
        ], task_ref=None, task_info=qtypes.TaskInfo(type="T4", owner="O4"), score=None),
        qtypes.TaskQueueItem(task_id=1, priority=10, hosts=[
            qtypes.TaskQueueHostsItem(score=3, host="host1"),
            qtypes.TaskQueueHostsItem(score=2, host="host2"),
            qtypes.TaskQueueHostsItem(score=1, host="host3")
        ], task_ref=None, task_info=qtypes.TaskInfo(type="T1", owner="O1"), score=None),
        qtypes.TaskQueueItem(task_id=5, priority=5, hosts=[
            qtypes.TaskQueueHostsItem(score=3, host="host3"),
            qtypes.TaskQueueHostsItem(score=2, host="host2"),
            qtypes.TaskQueueHostsItem(score=1, host="host1")
        ], task_ref=None, task_info=qtypes.TaskInfo(type="T5", owner="O5"), score=None)
    ]

    @staticmethod
    def init_queue(client, data):
        client.sync([
            [item.task_id, item.priority, item.hosts, item.task_info]
            for item in data
        ])

    @staticmethod
    def qserver(request, config, server, start_loop=True, quotas_enabled=False):
        server = server(config)
        server.STATE_FILENAME_PREFIX = ".".join((server.STATE_FILENAME_PREFIX, str(id(server))))
        server.start()
        server._Server__server.cfg = copy.deepcopy(server._Server__server.cfg)
        server._Server__server.cfg.port = server._Server__server.port
        server.quotas_enabled = quotas_enabled
        node_addr = server._node_addr
        logger = server._logger = logging.getLogger("qserver_{}".format(server._Server__server.port))
        setup_logger(logger, node_addr)
        g = []
        if start_loop:
            g.append(gevent.spawn(lambda: server.loop()))

        def stop_server():
            server._Server__primary_addr = None
            server.stop()
            if g:
                g[0].kill()
                g[0].join()

        request.addfinalizer(stop_server)
        return g, server

    @staticmethod
    def contender(server):
        return server._contender

    @staticmethod
    def qretry(func, do_assert=True):
        import sandbox.serviceq.errors
        try:
            return func()
        except sandbox.serviceq.errors.QRetry:
            if do_assert:
                assert False

    @classmethod
    def retry_wrapper(cls, func):
        return common.utils.progressive_waiter(0, 1, 5, lambda: cls.qretry(lambda: func(), do_assert=False))[0]

    @classmethod
    def wait_primary(cls, *servers):
        result = [0]
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: cls.qretry(
                lambda: len([result.__setitem__(0, _) for _ in servers if _[1]._is_primary]) == 1,
                do_assert=False
            )
        )[0], {s[1]._node_addr: s[1]._is_primary for s in servers}
        return result[0]

    @staticmethod
    def wait_election(inverse, *servers):
        ret, _ = common.utils.progressive_waiter(
            0, 1, 5, lambda: all(_[1]._Server__primary_addr is not None for _ in servers),
            inverse=inverse
        )
        return not ret if inverse else ret

    @staticmethod
    def wait_replication(*servers):
        def check():
            ids = [s._Server__state.operation_id for _, s in servers]
            return len(set(ids)) == 1 and ids[0] > 0
        return common.utils.progressive_waiter(0, 1, 5, check)[0]

    @staticmethod
    def wait_server(client, status=qtypes.Status.PRIMARY):
        def check():
            try:
                return client.status(secondary=(status != qtypes.Status.PRIMARY)) == status
            except (socket.error, qerrors.QRetry, jerrors.CallError):
                pass
        return common.utils.progressive_waiter(0, 1, 5, check)[0]

    @staticmethod
    def stop_server_loop(server):
        g, s = server
        g[0].kill()
        s.stop()

    @staticmethod
    def start_server_loop(server):
        g, s = server
        if g:
            cfg = copy.deepcopy(s._config.serviceq.server)
            cfg.server.port = s._node_addr.split(":")[1]
            s._init_joint(cfg)
            s.start()
        else:
            g.append(None)
        g[0] = gevent.spawn(lambda: s.loop())

    @staticmethod
    def force_client_to_use_server(client, server):
        _, s = server
        del client._local_rpc
        del client._secondary_rpc
        client._server_port = s._Server__server.port

    def test__replication(self, request, qclient, config, server):
        qserver1 = self.qserver(request, config, server)
        qserver2 = self.qserver(request, config, server)
        qserver3 = self.qserver(request, config, server)
        primary1 = self.wait_primary(qserver1, qserver2, qserver3)
        self.force_client_to_use_server(qclient, primary1)
        assert self.wait_server(qclient)
        self.init_queue(qclient, self.full_queue[:4])
        last_operation_id = primary1[1].operation_id(job=None)
        assert not primary1[1]._wait_commit(last_operation_id, timeout=0)
        assert qclient.queue() == self.full_queue[:4]
        assert dict(qclient.current_consumptions()) == {}
        assert dict(qclient.recalculate_consumptions()) == {}

        self.wait_replication(qserver1, qserver2, qserver3)
        assert primary1[1]._wait_commit(last_operation_id, timeout=1)

        for _ in (qserver1, qserver2, qserver3):
            self.force_client_to_use_server(qclient, _)
            assert qclient.queue(secondary=None) == self.full_queue[:4]

        secondary = filter(lambda _: _ is not primary1, (qserver1, qserver2, qserver3))[0]
        self.stop_server_loop(secondary)
        assert self.wait_election(True, secondary)
        assert self.wait_election(False, *filter(lambda _: _ is not secondary, (qserver1, qserver2, qserver3)))
        self.start_server_loop(secondary)
        assert self.wait_primary(qserver1, qserver2, qserver3) is primary1

        gen = client_utils.qpop(qclient, "host1")
        assert gen.next() == [2, 1]
        client_utils.qcommit(gen)
        qclient.push(5, 5, ((3, "host3"), (2, "host2"), (1, "host1")), qtypes.TaskInfo(type="T5", owner="O5"))
        last_operation_id = primary1[1].operation_id(job=None)
        assert not primary1[1]._wait_commit(last_operation_id, timeout=0)
        assert self.wait_replication(qserver1, qserver2, qserver3)
        assert primary1[1]._wait_commit(last_operation_id, timeout=1)
        map(lambda _: _[1]._collect_garbage(), (qserver1, qserver2, qserver3))
        self.stop_server_loop(primary1)
        primary2 = self.wait_primary(*[_ for _ in (qserver1, qserver2, qserver3) if _ is not primary1])
        assert primary2 is not primary1
        assert self.retry_wrapper(lambda: primary1[1]._is_primary) is False
        self.start_server_loop(primary1)
        assert self.wait_primary(qserver1, qserver2, qserver3) is primary2
        assert self.wait_server(qclient)

        assert self.qretry(lambda: qclient.queue()) == self.full_queue[1:]

        assert self.wait_replication(qserver1, qserver2, qserver3)

        for _ in (qserver1, qserver2, qserver3):
            self.force_client_to_use_server(qclient, _)
            assert qclient.queue(secondary=None) == self.full_queue[1:]

        assert primary2[1]._Server__primary_addr is not None
        self.contender(primary2[1]).stop()
        assert primary2[1]._Server__primary_addr is not None
        gevent.sleep()
        assert primary2[1]._Server__primary_addr is None
        assert self.wait_election(False, qserver1, qserver2, qserver3)

        qserver4 = self.qserver(request, config, server, start_loop=False, quotas_enabled=True)
        self.force_client_to_use_server(qclient, qserver4)
        assert qclient.queue(secondary=None) == []
        self.start_server_loop(qserver4)
        assert self.wait_election(False, qserver1, qserver2, qserver3, qserver4)
        assert self.wait_replication(qserver1, qserver2, qserver3, qserver4)
        assert qclient.queue(secondary=None) == self.full_queue[1:]

    def test__primary_presistent_state(self, request, qclient, config, server, monkeypatch):
        qserver = self.qserver(request, config, server)
        assert self.wait_primary(qserver) is qserver
        self.force_client_to_use_server(qclient, qserver)
        assert self.wait_server(qclient)

        assert qclient.queue() == []

        self.init_queue(qclient, self.full_queue[:4])
        assert qclient.queue() == self.full_queue[:4]

        qclient.sync([], reset=True)
        assert qclient.queue() == []

        self.stop_server_loop(qserver)
        self.start_server_loop(qserver)
        assert self.retry_wrapper(qclient.queue) == self.full_queue[:4]

        qserver[1].dump_snapshot()
        qclient.sync([], reset=True)
        assert qclient.queue() == []
        self.stop_server_loop(qserver)
        self.start_server_loop(qserver)
        assert self.retry_wrapper(qclient.queue) == self.full_queue[:4]

        qserver[1].dump_snapshot()
        qclient.sync([], reset=True)
        assert qclient.queue() == []
        self.stop_server_loop(qserver)
        self.start_server_loop(qserver)
        assert self.retry_wrapper(qclient.queue) == self.full_queue[:4]

        self.init_queue(qclient, self.full_queue[4:])
        assert qclient.queue() == self.full_queue

        qclient.sync([], reset=True)
        assert qclient.queue() == []
        self.stop_server_loop(qserver)
        decode = qstate.PersistentState.decode
        monkeypatch.setattr(
            qstate.PersistentState,
            "decode",
            classmethod(lambda _, *args, **kws: (gevent.sleep(5), decode(*args, **kws))[1])
        )
        self.start_server_loop(qserver)
        with pytest.raises(qerrors.QElectionInProgress):
            qclient.queue()
        with pytest.raises(qerrors.QRetry) as error:
            qclient.queue()
        assert not isinstance(error.value, qerrors.QElectionInProgress)
        assert self.retry_wrapper(qclient.queue) == self.full_queue

    def test__secondary_presistent_state(self, request, qclient, config, server):
        qserver1 = self.qserver(request, config, server)
        self.force_client_to_use_server(qclient, qserver1)
        assert self.wait_server(qclient)
        qserver2 = self.qserver(request, config, server)
        qserver3 = self.qserver(request, config, server)
        self.force_client_to_use_server(qclient, qserver2)
        assert self.wait_server(qclient, qtypes.Status.SECONDARY)
        assert self.wait_primary(qserver1, qserver2, qserver3) is qserver1

        self.init_queue(qclient, self.full_queue[:4])
        assert self.wait_replication(qserver1, qserver2)
        assert qclient.queue() == self.full_queue[:4]

        map(self.stop_server_loop, (qserver3, qserver2, qserver1))
        for s in qserver2, qserver3:
            s[1]._reset()
        map(self.start_server_loop, (qserver3, qserver2))
        assert self.wait_election(False, qserver2, qserver3)
        assert self.wait_server(qclient)
        assert qclient.queue() == self.full_queue[:4]

        self.start_server_loop(qserver1)
        self.wait_replication(qserver1, qserver2, qserver3)
        for s in qserver1, qserver2, qserver3:
            s[1].dump_snapshot()
        self.init_queue(qclient, self.full_queue[4:])
        self.wait_replication(qserver1, qserver2, qserver3)
        primary = self.wait_primary(qserver1, qserver2, qserver3)
        map(self.stop_server_loop, (qserver1, qserver2, qserver3))
        secondaries = filter(lambda _: _ is not primary, (qserver1, qserver2, qserver3))
        for s in qserver1, qserver2, qserver3:
            s[1]._reset()
        map(self.start_server_loop, secondaries)
        self.wait_primary(*secondaries)
        self.start_server_loop(primary)
        self.wait_replication(qserver1, qserver2, qserver3)
        assert self.wait_server(qclient)
        assert qclient.queue() == self.full_queue

    def test__reuse_secondary_state(self, request, qclient, config, server):
        qserver1 = self.qserver(request, config, server)
        self.force_client_to_use_server(qclient, qserver1)
        assert self.wait_server(qclient)
        self.init_queue(qclient, self.full_queue[:4])

        qserver2 = self.qserver(request, config, server)
        qserver3 = self.qserver(request, config, server)
        self.wait_replication(qserver1, qserver2, qserver3)
        primary = self.wait_primary(qserver1, qserver2, qserver3)
        assert primary is qserver1
        states = [s[1]._Server__state for s in (qserver1, qserver2, qserver3)]

        self.stop_server_loop(primary)
        assert self.wait_election(False, qserver2, qserver3)
        primary = self.wait_primary(qserver2, qserver3)
        assert primary is not qserver1
        self.start_server_loop(qserver1)
        assert self.wait_server(qclient, qtypes.Status.SECONDARY)
        self.init_queue(qclient, self.full_queue[4:])
        self.wait_replication(qserver1, qserver2, qserver3)

        for i, s in enumerate((qserver1, qserver2, qserver3)):
            assert s[1]._Server__state is states[i]
