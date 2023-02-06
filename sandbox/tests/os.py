from __future__ import absolute_import

import os
import time
import gevent
import logging
import threading as th

import six
import pytest

from sandbox.common import os as common_os


class ExceptionTest(Exception):
    pass


class TestSubprocess(object):
    @staticmethod
    def __worker(i):
        return i, os.getpid()

    @pytest.mark.parametrize("using_gevent", (False, True), ids=("threads", "gevent"))
    def test__subprocess_simple(self, using_gevent):
        main_pid = os.getpid()
        sp_ctx = common_os.Subprocess(using_gevent=using_gevent)
        result = 42
        with sp_ctx:
            sp_ctx.result = result, os.getpid()
        assert sp_ctx.result[0] == result
        assert sp_ctx.result[1] != main_pid

    @pytest.mark.parametrize("using_gevent", (False, True), ids=("threads", "gevent"))
    def test__subprocess_exception(self, using_gevent):
        sp_ctx = common_os.Subprocess(using_gevent=using_gevent)
        err_msg = "Error in subprocess "
        with pytest.raises(ExceptionTest) as exc_info:
            with sp_ctx:
                raise ExceptionTest(err_msg + str(os.getpid()))
        value = str(exc_info.value)
        assert value.startswith(err_msg)
        assert int(value[len(err_msg):]) != os.getpid()

    @pytest.mark.parametrize("using_gevent", (False, True), ids=("threads", "gevent"))
    def test__subprocess_big_result(self, using_gevent):
        main_pid = os.getpid()
        sp_ctx = common_os.Subprocess(using_gevent=using_gevent)
        result = "\0" * 1000000
        with sp_ctx:
            sp_ctx.result = result, os.getpid()
        assert sp_ctx.result[0] == result
        assert sp_ctx.result[1] != main_pid

    def test__subprocess_watchdog(self):
        sp_ctx = common_os.Subprocess(using_gevent=False, watchdog=1)
        with pytest.raises(common_os.SubprocessAborted), sp_ctx:
            time.sleep(2)
        sp_ctx = common_os.Subprocess(using_gevent=False, watchdog=2)
        with sp_ctx:
            time.sleep(1)
        sp_ctx = common_os.Subprocess(using_gevent=False, watchdog=2)
        with sp_ctx:
            time.sleep(1)
            sp_ctx.stop_watchdog()
            time.sleep(2)

    def test__subprocess_logging_locks(self):
        class TestHandler(logging.StreamHandler):
            def emit(self, record):
                time.sleep(1)
                super(TestHandler, self).emit(record)

        logger = logging.getLogger("logger")
        sub_logger = logger.getChild("sub_logger")
        logger.addHandler(TestHandler())
        t1 = th.Thread(target=lambda: logger.debug("main process"))
        t1.start()
        t2 = th.Thread(target=lambda: sub_logger.debug("main process"))
        t2.start()
        sp_ctx = common_os.Subprocess(using_gevent=False, watchdog=3)
        with sp_ctx:
            logger.debug("subprocess")
            sub_logger.debug("subprocess")
            sp_ctx.stop_watchdog()
        t1.join()
        t2.join()

    def test__subprocess_pool(self):
        pool = common_os.SubprocessPool(10, using_gevent=False)
        jobs = {}
        for i in range(10):
            job_id = pool.spawn(self.__worker, (i,), {})
            jobs[job_id] = i
        ready = set()
        while len(ready) < len(jobs):
            time.sleep(.1)
            ready = set(pool.ready_jobs())
            print(ready)
        assert ready == set(jobs.keys())
        pids = set()
        for job_id in ready:
            i, pid = pool.result(job_id)
            pids.add(pid)
            assert jobs[job_id] == i
        assert len(pids) == len(jobs)
        assert os.getpid() not in pids


class TestPipeQueue(object):
    def test__pipe_queue(self):
        pipe_queue = common_os.PipeQueue(size=3)
        for i in range(3):
            assert pipe_queue.main_put(i)
        assert not pipe_queue.main_put(4)
        for i in range(3):
            assert pipe_queue.worker_get() == (True, i)
            pipe_queue.worker_put(2 - i)
        assert pipe_queue.worker_get(timeout=0) == (False, None)
        for i in range(2, -1, -1):
            assert pipe_queue.main_get() == (True, i)
        assert pipe_queue.main_get(timeout=0) == (False, None)

    def test__pipe_queue_subprocess(self):
        pipe_queue = common_os.PipeQueue(size=3)
        for i in range(3):
            assert pipe_queue.main_put(i)
        with common_os.Subprocess(using_gevent=False):
            for i in range(3):
                assert pipe_queue.worker_get() == (True, i)
                pipe_queue.worker_put(2 - i)
        for i in range(2, -1, -1):
            assert pipe_queue.main_get() == (True, i)

    @pytest.mark.parametrize("using_gevent", (False, True), ids=("threads", "gevent"))
    def test__pipe_queue_big_message(self, using_gevent):
        pipe_queue = common_os.PipeQueue(size=1, using_gevent=using_gevent)
        big_data = "\0" * 1000000
        put_result = [None]
        get_result = [None]

        def thread_func_put():
            put_result[0] = pipe_queue.main_put(big_data)

        def thread_func_get():
            get_result[0] = pipe_queue.worker_get()

        if using_gevent:
            tp = gevent.spawn(thread_func_put)
            tg = gevent.spawn(thread_func_get)
        else:
            tp = th.Thread(target=thread_func_put)
            tp.start()
            tg = th.Thread(target=thread_func_get)
            tg.start()
        tp.join()
        tg.join()
        assert get_result[0] == (True, big_data)
        assert put_result[0]


class TestPipeRPC(object):
    class RPCServer(common_os.PipeRPCServer):
        @staticmethod
        def ping(value):
            return value

    def test__rpc(self):
        pipe_rpc = common_os.PipeRPC(using_gevent=False)
        rpc_server = self.RPCServer(pipe_rpc)
        t = th.Thread(target=rpc_server)
        t.start()
        value = 42
        assert pipe_rpc("ping", value) == value
        pipe_rpc("__stop__")
        t.join()

    @staticmethod
    def __subproc(rpc_server):
        with common_os.Subprocess(using_gevent=False):
            rpc_server()

    def test__rpc_subprocess(self):
        pipe_rpc = common_os.PipeRPC(using_gevent=False)
        rpc_server = self.RPCServer(pipe_rpc)
        t = th.Thread(target=self.__subproc, args=(rpc_server,))
        t.start()
        value = 42
        assert pipe_rpc("ping", value) == value
        pipe_rpc("__stop__")
        t.join()


class TestWorkersPool(object):
    @staticmethod
    def square(i):
        return i * i

    def test__workers_pool(self, request):
        process_pool_size = 5
        thread_pool_size = 20
        number_of_values = 1000
        max_jobs = process_pool_size * thread_pool_size
        pool = common_os.WorkersPool(self.square, process_pool_size, thread_pool_size, title="[test worker]")
        pool.start()
        request.addfinalizer(pool.stop)
        jobs = {}
        total = 0
        for i in six.moves.range(number_of_values):
            while True:
                assert len(jobs) <= max_jobs
                ready_jobs = pool.ready_jobs()
                for job_id in ready_jobs:
                    value = jobs.pop(job_id)
                    result = pool.result(job_id)
                    total += 1
                    assert result == value * value
                job_id = pool.spawn(i)
                if job_id is not None:
                    jobs[job_id] = i
                    break
                else:
                    time.sleep(.01)
        assert len(jobs) <= max_jobs
        while jobs:
            ready_jobs = pool.ready_jobs()
            for job_id in ready_jobs:
                value = jobs.pop(job_id)
                result = pool.result(job_id)
                total += 1
                assert result == value * value
            if not ready_jobs:
                time.sleep(.01)
        assert total == number_of_values
