import argparse
import contextlib
import datetime
from multiprocessing import Process, Lock

import mock
import pytest
import typing as tp

import dmp_suite.yt.task.logbroker as lb
from connection.ctl import WrapCtl
from dmp_suite import datetime_utils as dtu
from dmp_suite.ctl import CTL_LAST_LOAD_ID
from dmp_suite.ctl.storage import DictStorage
from dmp_suite.yt import Int, LayeredLayout, YTTable, resolve_meta
from dmp_suite.yt.dyntable_operation.operations import select_rows
from dmp_suite.yt.task.logbroker import IncrementLogbrokerTask, LogbrokerSource, TableTypeUnsupportedError
from test_dmp_suite.logbroker_test import write_to_logbroker


class StaticTable(YTTable):
    a = Int()


class TestTable(YTTable):
    __dynamic__ = True
    __layout__ = LayeredLayout(name='test', layer='test')
    __unique_keys__ = True
    a = Int(sort_key=True)
    b = Int()


class MockReader:
    def __init__(self, values, timeout_if_none=1):
        self.values = values
        self.timeout = timeout_if_none

    def run(self, *_, **kwargs):
        import os
        pid = os.getpid()

        if self.values is None:
            stop_event = kwargs['stop_event']
            while not stop_event.is_set():
                pass
            return

        for v in self.values:
            if isinstance(v, Exception):
                raise v
            else:
                v['pid'] = pid
                yield v


def test_dynamic_table_check():
    with pytest.raises(TableTypeUnsupportedError):
        IncrementLogbrokerTask(
            name='test_logbroker_task',
            source=None,
            target=StaticTable,
            extractors={'a': 'a', 'b': 'a'},
        )

    IncrementLogbrokerTask(
        name='test_logbroker_task',
        source=None,
        target=TestTable,
        extractors={'a': 'a'},
    )


EXPECTED = [
    {'a': 0, 'b': None},
    {'a': 1, 'b': None},
    {'a': 2, 'b': None},
    {'a': 3, 'b': None},
    {'a': 4, 'b': None},
    {'a': 5, 'b': None},
    {'a': 6, 'b': None},
    {'a': 7, 'b': None},
    {'a': 8, 'b': None},
    {'a': 9, 'b': None}
]


@pytest.mark.slow
@pytest.mark.skip(reason='Тест флапает из-за проблем с TVM, которые пока не удалось разрешить. При запуске одиночного теста флап не воспроизводится.')
def test_logbroker_task():
    ctl_storage = DictStorage()
    ctl = WrapCtl(ctl_storage)

    write_to_logbroker(producer_name='logbroker_task_test')

    source = LogbrokerSource(
        name='logbroker_task_test',
        message_decoder=lambda x: {'a': int.from_bytes(x, 'big')},
    )

    task = IncrementLogbrokerTask(
        name='test_logbroker_task',
        source=source,
        target=TestTable,
        extractors={'a': 'a'},
        batch_size=10
    )

    with mock.patch('connection.ctl.get_ctl', return_value=ctl):
        task._run_task(argparse.Namespace())

    rows = list(select_rows(resolve_meta(TestTable)))
    assert rows == EXPECTED

    # actually we do not know real CLT entity
    has_ctl = False
    for key, value in ctl_storage.data.items():
        if key.name.startswith(resolve_meta(TestTable).target_path()):
            if value.get(CTL_LAST_LOAD_ID):
                has_ctl = True
                break

    assert has_ctl


def test_logbroker_task_with_negative_lifetime():
    source = LogbrokerSource(
        name='logbroker_task_test',
        message_decoder=lambda x: {'a': int.from_bytes(x, 'big')},
    )

    with pytest.raises(ValueError):
        IncrementLogbrokerTask(
            name='test_logbroker_task',
            source=source,
            target=TestTable,
            extractors={'a': 'a'},
            batch_size=10,
            task_lifetime=datetime.timedelta(seconds=-1)
        )


@pytest.mark.parametrize(
    "task_lifetime, remains_ctls", [
        (datetime.timedelta(milliseconds=100), [{1: 2}]),
        (datetime.timedelta(milliseconds=300), []),
    ]
)
def test_logbroker_task_lifetime(task_lifetime, remains_ctls):
    fake_utc = dtu.utcnow()

    class MockReader:
        ctls = [{1: 1}, {1: 2}]

        def run(self, *_, **__):
            nonlocal fake_utc
            while self.ctls:
                fake_utc += datetime.timedelta(milliseconds=200)
                yield self.ctls.pop(0)

    reader = MockReader()

    class FakeSource:
        def __init__(self):
            self.name = 'fake'

        @contextlib.contextmanager
        def get_reader(self, *_, **__):
            yield reader

    task = IncrementLogbrokerTask(
        name='test_logbroker_task',
        source=tp.cast(LogbrokerSource, FakeSource()),
        target=TestTable,
        extractors={'a': 'a'},
        batch_size=10,
        task_lifetime=task_lifetime
    )

    with mock.patch('connection.logbroker.get_logbroker_connection', return_value=mock.MagicMock()):
        with mock.patch('dmp_suite.datetime_utils.utcnow', side_effect=lambda: fake_utc):
            task._run_task(argparse.Namespace())

    assert reader.ctls == remains_ctls


class TestMultiprocessingTermination:

    class FakeSource:
        def __init__(self, reader):
            self.name = 'fake'
            self.reader = reader

        @contextlib.contextmanager
        def get_reader(self, *_, **__):
            yield self.reader

    @staticmethod
    def __raise_keyboard_interrupt():
        raise KeyboardInterrupt("TEST!")

    @pytest.mark.parametrize(
        "task_lifetime, expected_utc_now_deltas", [
            (datetime.timedelta(milliseconds=100), [
                datetime.timedelta(milliseconds=0),  # для 1го last_sync_date
                datetime.timedelta(milliseconds=0),  # для вычисления expires_at
                datetime.timedelta(milliseconds=200),  # для проверки тухлости
            ]),
            (datetime.timedelta(milliseconds=300), [
                datetime.timedelta(milliseconds=0),  # для 1го last_sync_date
                datetime.timedelta(milliseconds=0),  # для вычисления expires_at
                datetime.timedelta(milliseconds=0),  # для первой проверки тухлости
                datetime.timedelta(milliseconds=400),  # для второй проверки тухлости
            ])
        ]
    )
    @mock.patch('dmp_suite.yt.task.logbroker.NEW_CTL_IN_QUEUE_TIMEOUT', 0)
    @pytest.mark.enable_socket  # for multiprocessing.Manager
    def test_logbroker_multiprocessing_task_lifetime(self, task_lifetime, expected_utc_now_deltas):
        """
        Проверяет, что таска завершается после того, как был достигнут или превышен ее expiration_time.

        :param task_lifetime: дельта, через которую будет выставлен expires_at
        :param expected_utc_now_deltas: список дельт для каждого следующего вызова dtu.utcnow()
        """

        # task_lifetime = kwargs['task_lifetime']
        # expected_utc_now_deltas = kwargs['expected_utc_now_deltas']
        fake_utc_test_started = dtu.utcnow()
        fake_utc_now_stamps = list(map(
            lambda delta: fake_utc_test_started + delta,
            expected_utc_now_deltas)
        )

        def fake_now_ts_supplier():
            return fake_utc_now_stamps.pop(0)

        reader = MockReader(None, 30)

        task = lb.IncrementLogbrokerTaskMultiprocessing(
            name='test_logbroker_task',
            source=tp.cast(LogbrokerSource, self.FakeSource(reader)),
            target=TestTable,
            extractors={'a': 'a'},
            batch_size=10,
            task_lifetime=task_lifetime
        )

        with mock.patch('connection.logbroker.get_logbroker_connection', return_value=mock.MagicMock()):
            with mock.patch('dmp_suite.datetime_utils.utcnow', side_effect=fake_now_ts_supplier):
                task._run_task(argparse.Namespace())

        assert len(fake_utc_now_stamps) == 0

    @pytest.mark.enable_socket  # for multiprocessing.Manager
    @mock.patch('dmp_suite.yt.task.logbroker.NEW_CTL_IN_QUEUE_TIMEOUT', 1)
    @mock.patch('dmp_suite.yt.operation.init_yt_table', side_effect=lambda *a: None)
    @mock.patch('dmp_suite.yt.dyntable_operation.operations.is_table_mounted', True)
    def test_logbroker_multiprocessing_task_read_everything(self, *mocks):
        reader = MockReader([
            {'partition_0': 0},
            {'partition_1': 1},
            {'partition_2': 2},
            {'partition_3': 3},
        ])

        task = lb.IncrementLogbrokerTaskMultiprocessing(
            name='test_logbroker_task',
            source=tp.cast(LogbrokerSource, self.FakeSource(reader)),
            target=TestTable,
            extractors={'a': 'a'},
            batch_size=10,
            parallel_factor=1
        )

        with mock.patch('connection.logbroker.get_logbroker_connection', return_value=mock.MagicMock()):
            task._run_task(argparse.Namespace())
            assert task._ctl_by_source_id_getter('partition_0') == 0
            assert task._ctl_by_source_id_getter('partition_1') == 1
            assert task._ctl_by_source_id_getter('partition_2') == 2
            assert task._ctl_by_source_id_getter('partition_3') == 3

    @pytest.mark.enable_socket  # for multiprocessing.Manager
    @mock.patch('dmp_suite.yt.task.logbroker.NEW_CTL_IN_QUEUE_TIMEOUT', 1)
    @mock.patch('dmp_suite.yt.operation.init_yt_table', side_effect=lambda *a: None)
    @mock.patch('dmp_suite.yt.dyntable_operation.operations.is_table_mounted', True)
    def test_logbroker_multiprocessing_task_interrupted(self, *mocks):
        """
        Проверяет, что если суб-процессы сломались, то вся таска завершится.
        """

        reader = MockReader([
            {'OI': 1337},
            Exception('This exception will terminate the task!')
        ])

        task = lb.IncrementLogbrokerTaskMultiprocessing(
            name='test_logbroker_task',
            source=tp.cast(LogbrokerSource, self.FakeSource(reader)),
            target=TestTable,
            extractors={'a': 'a'},
            batch_size=10,
            # default parallel factor is 1.
        )

        with mock.patch('connection.logbroker.get_logbroker_connection', return_value=mock.MagicMock()):
            actual_error = None
            try:
                task._run_task(argparse.Namespace())
            except Exception as e:
                actual_error = e
            assert actual_error is not None
            assert isinstance(actual_error, lb.SubProcessFailedError)


@pytest.mark.enable_socket  # for multiprocessing.Manager
@mock.patch('dmp_suite.yt.operation.init_yt_table', side_effect=lambda *a: None)
@mock.patch('dmp_suite.yt.dyntable_operation.operations.is_table_mounted', True)
class TestMultiprocessing:

    @staticmethod
    def __acquire_and_assert(lock, timeout, lock_evaluator, assertion_message):
        def f():
            with lb.acquire_with_timeout(lock, timeout) as successfully_acquired:
                assert lock_evaluator(successfully_acquired), assertion_message

        return f

    def test_acquire_with_timeout_timed_out(self, *mocks):
        """
        Проверяет, что механизм лока настроен верно и дважды его взять не получится.
        """
        timeout = 1
        lock = Lock()
        p = Process(
            target=TestMultiprocessing.__acquire_and_assert(lock, timeout, lambda l: not l,
                                                            "Expected a lock to be taken and not acquired, "
                                                            "but managed to take it.")
        )
        with lb.acquire_with_timeout(lock, timeout) as main_lock:
            assert main_lock is not None
            print(f'Result is: {main_lock}')

            p.start()
            p.join()
            assert p.exitcode == 0, "Inner processed exited with non-zero exit-code, something wrong, see the logs. " \
                                    "Most likely it succeeded in acquiring the lock."
        p = Process(
            target=TestMultiprocessing.__acquire_and_assert(lock, timeout, lambda l: l,
                                                            "Expected a lock to be released, "
                                                            "but did not manage to take it.")
        )
        p.start()
        p.join()
        assert p.exitcode == 0, "Inner processed exited with non-zero exit-code, something wrong, see the logs. " \
                                "Most likely it could not take a lock"

    def test_lb_target_cant_take_second_lock(self, *mocks):
        """
        Проверяет, что если лок уже взят, то при попытке заинитить таблицу процесс завершится.
        """
        lock = Lock()
        target1 = lb.LogbrokerMultiprocessTarget(lock, TestTable, {})
        with lb.acquire_with_timeout(lock, 1) as main_lock:
            assert main_lock
            p1 = Process(
                target=lambda: target1._init_partition_table_synchronized(None, 1)
            )
            p1.start()
            p1.join()
            assert p1.exitcode == 1, 'Processed should NOT have been able to take a lock and finish successfully'
