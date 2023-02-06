# pylint: disable=protected-access, redefined-outer-name
import asyncio
import logging
import queue
import time

import pytest

from stq.server.dbhandlers import task_tuple
from taxi import default_executor
from taxi.logs import log
from taxi.logs import utils as log_util
from taxi.stq import async_worker_old
from testsuite.utils import callinfo


class CallQueue:
    def __init__(self, func):
        self._func = func
        self._name = func.__name__
        self._queue = queue.Queue()
        self._get_callinfo = callinfo.callinfo(func)

    def __call__(self, *args, **kwargs):
        try:
            return self._func(*args, **kwargs)
        finally:
            self._queue.put((args, kwargs))

    def flush(self):
        self._queue = queue.Queue()

    @property
    def has_calls(self):
        return self.times_called > 0

    @property
    def times_called(self):
        return self._queue.qsize()

    def next_call(self):
        try:
            return self._get_callinfo(*self._queue.get_nowait())
        except queue.Empty:
            raise callinfo.CallQueueEmptyError(
                f'No calls for {self._name}() left in the queue',
            )

    def wait_call(self, timeout=10.0):
        try:
            return self._get_callinfo(*self._queue.get(timeout=timeout))
        except queue.Empty:
            raise callinfo.CallQueueTimeoutError(
                f'Timeout while waiting for {self._name}() to be called',
            )


def callqueue(func):
    if isinstance(func, CallQueue):
        return func
    return CallQueue(func)


@pytest.fixture
def run_in_thread():
    futures = []
    executor = default_executor.ThreadPoolExecutor()

    def func(task, *args, **kwargs):
        future = executor.submit(task, *args, **kwargs)
        futures.append(future)
        return future

    yield func

    not_done_futures = []

    for future in futures:
        if not future.done():
            future.cancel()
            not_done_futures.append(future)

    if not_done_futures:
        raise RuntimeError('Not all futures was done! %s' % not_done_futures)


@pytest.fixture
def exchange_mock(mock):
    def do_it(queue_name='queue'):
        class ExchangeMock:
            def __init__(self):
                self.identifier = f'worker-{queue_name} pid-1000 proc-number-0'
                self.exec_func = None
                self.stop_func = None

            def register_exec(self, func):
                self.exec_func = func

            def register_stop(self, func):
                self.stop_func = func

            @staticmethod
            def recv_command(arg):
                return False

            def exec_callback(self, *args, **kwargs):
                self.exec_func(*args, **kwargs)

            @staticmethod
            @mock
            def mark_done():
                pass

            @staticmethod
            @mock
            def mark_failed():
                pass

            @staticmethod
            @callqueue
            def notify_ready():
                pass

        return ExchangeMock

    return do_it


@pytest.mark.parametrize('use_async_gen', [True, False])
@pytest.mark.parametrize(
    'enter_error, body_error', [(True, False), (False, False), (False, True)],
)
async def test_coro_context_setup_manager(
        use_async_gen, enter_error, body_error, monkeypatch, stub, loop, mock,
):
    monkeypatch.setattr(
        async_worker_old._Context, 'exchange', stub(identifier=1),
    )

    @mock
    def loop_stop():
        pass

    monkeypatch.setattr(
        async_worker_old._Context, 'loop', stub(stop=loop_stop),
    )

    data = object()

    gen_entered = False
    gen_exited = False

    async def gen(loop):
        nonlocal gen_entered, gen_exited
        gen_entered = True
        if enter_error:
            raise RuntimeError('enter error')
        yield data
        gen_exited = True

    async def coro(loop):
        if enter_error:
            raise RuntimeError('enter error')
        return data

    on_run_callback = gen(loop) if use_async_gen else coro(loop)

    if body_error:
        with pytest.raises(RuntimeError) as exc_info:
            async with async_worker_old.ContextSetup(
                    on_run_callback,
            ) as got_data:
                if body_error:
                    raise RuntimeError('body error')
        if body_error:
            assert exc_info.value.args == ('body error',)
    else:
        async with async_worker_old.ContextSetup(on_run_callback) as got_data:
            pass

    if not enter_error:
        assert got_data == data
    else:
        assert loop_stop.calls == [{}]

    if use_async_gen:
        assert gen_entered
        if not enter_error:
            assert gen_exited


@pytest.mark.parametrize('error', [True, False])
def test_worker(error, patch, run_in_thread, exchange_mock):
    data = object()

    @patch('asyncio.set_event_loop')
    def set_loop(loop):
        pass

    async def task_function(data, log_extra=None):
        if error:
            raise RuntimeError('error')

    async def on_run_callback(loop):
        return data

    exchange_mock_cls = exchange_mock()
    exchange = exchange_mock_cls()

    future = run_in_thread(
        async_worker_old.init_and_start,
        exchange,
        task_function,
        on_run_callback,
    )

    exchange_mock_cls.notify_ready.wait_call()

    exchange.exec_callback(
        task_tuple.Task(
            'my_task_id',
            exec_tries=0,
            args=[],
            kwargs={},
            reschedule_counter=0,
        ),
    )
    time.sleep(0.5)
    exchange.stop_func()

    assert len(set_loop.calls) == 1

    if error:
        assert exchange_mock_cls.mark_failed.calls
    else:
        assert exchange_mock_cls.mark_done.calls
    assert future.result(1) is None


@pytest.fixture
def init_logging():
    log_settings = {
        'logger_names': ['taxi'],
        'ident': 'log_extra',
        'log_level': logging.INFO,
        'log_format': '',
    }
    log.init_logger(**log_settings)
    try:
        yield
    finally:
        log.cleanup_logger(log_settings['logger_names'])


@pytest.mark.parametrize('error', [True, False])
async def test_extra_logs(
        caplog, run_in_thread, exchange_mock, error, init_logging,
):
    logger = logging.getLogger('taxi.stq.test')
    data = object()

    @async_worker_old.pass_task_info
    async def task_function(data, *args, **kwargs):
        log_extra = kwargs['log_extra']
        log_extra = log_util.extend_log_extra(log_extra, some_tag='some_val')
        logger.info('Some interesting thing', extra=log_extra)
        if error:
            raise RuntimeError('some error')

    async def on_run_callback(loop):
        return data

    exchange_mock_cls = exchange_mock('test_queue')
    exchange = exchange_mock_cls()

    future = run_in_thread(
        async_worker_old.init_and_start,
        exchange,
        task_function,
        on_run_callback,
    )
    exchange_mock_cls.notify_ready.wait_call()

    exchange.exec_callback(
        task_tuple.Task(
            'my_task_id',
            exec_tries=0,
            args=[1, 2],
            kwargs={'a': 'b'},
            reschedule_counter=0,
        ),
    )
    await asyncio.sleep(0.5)
    exchange.stop_func()

    assert future.result(1) is None

    if not error:
        assert exchange.mark_done.call is not None
        assert exchange.mark_failed.call is None
    else:
        assert exchange.mark_done.call is None
        assert exchange.mark_failed.call is not None

    records = caplog.records
    stq_task_finish_logs = [
        x
        for x in records
        if getattr(x, 'extdict', {}).get('_type') == 'stq_task_finish'
    ]
    assert len(stq_task_finish_logs) == 1
    task_run_id = stq_task_finish_logs[0].extdict['stq_run_id']

    stq_logs = [
        x
        for x in records
        if getattr(x, 'extdict', {}).get('stq_run_id') == task_run_id
    ]

    assert len(stq_logs) == 4

    assert stq_logs[0].extdict['body']['args'] == [1, 2]
    assert stq_logs[0].extdict['body']['kwargs']['a'] == 'b'

    assert [
        'test_queue task started',
        'Some interesting thing',
        'test_queue task finished',
    ] == [x.getMessage() for x in stq_logs[:3]]
    assert stq_logs[1].extdict['some_tag'] == 'some_val'
    assert stq_logs[2].extdict['some_tag'] == 'some_val'

    assert (
        stq_logs[-1]
        .getMessage()
        .startswith(
            '[worker-test_queue pid-1000 proc-number-0] '
            'Task <function test_extra_logs.<locals>.task_function at',
        )
    )
    if error:
        assert stq_logs[2].levelname == 'ERROR'
        assert stq_logs[2].extdict['exc_info']
    else:
        assert stq_logs[2].levelname == 'INFO'
        assert 'exc_info' not in stq_logs[2].extdict
