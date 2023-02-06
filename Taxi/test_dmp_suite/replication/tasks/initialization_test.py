import time
import signal
import multiprocessing
from collections import defaultdict

import mock
import pytest

from dmp_suite import yt
from dmp_suite.replication.tasks.initialization import StreamingInitializationTask, WaitTimeout
from dmp_suite.task import cli
from dmp_suite.task.execution import run_task
from test_dmp_suite.replication.test_ods_streaming import DummyDynamicTable


class RawTable(DummyDynamicTable):
    __layout__ = yt.NotLayeredYtLayout('test_initialization', 'raw')


class OdsTable(DummyDynamicTable):
    __layout__ = yt.NotLayeredYtLayout('test_initialization', 'ods')


def get_streaming_initialization_tasks() -> StreamingInitializationTask:
    task = StreamingInitializationTask(
        name='streaming_initialization_task',
        raw_table=RawTable,
        target_table=OdsTable,
        extractors={},
    )
    return task


def get_fake_ctl(raw_values=None):
    """
    создадим фейковый ctl который будет возвращать необходимы нам значения
    для ods таблицы всегда
       - '2021-02-02 01:01:01'
    для raw таблицы (по умолчанию)
       - первый вызов -> '2021-02-01 01:01:01'
       - второй вызов -> '2021-02-02 01:01:01'
    """
    values = {
        OdsTable: iter(['2021-02-02 01:01:01'] * 10),
        RawTable: iter(raw_values or ['2021-02-01 01:01:01', '2021-02-02 01:01:01']),
    }

    def fake_ctl_getter(table, _):
        fake_ctl_getter.called[table] += 1
        return next(values[table])

    fake_ctl_getter.called = defaultdict(int)
    fake_ctl = mock.MagicMock()
    fake_ctl.yt.get_param = fake_ctl_getter
    return fake_ctl


class TestStreamingInitializationTask:
    def test_wait_for_equalize_raw_ctl_to_ods(self):
        # проверим что работает ожидание выравнивания ctl
        task = get_streaming_initialization_tasks()
        fake_ctl = get_fake_ctl()
        with mock.patch('dmp_suite.replication.tasks.initialization.get_ctl', return_value=fake_ctl):
            start = time.monotonic()
            task._wait_for_equalize_raw_ctl_to_ods(sleep_time=1, wait_time=3)
            # проверим что было ожидание 1 секунду и скрипт запрашивал 2 раза значение ctl для raw таблицы
            perform_time = time.monotonic() - start
            assert fake_ctl.yt.get_param.called[RawTable] == 2
            assert fake_ctl.yt.get_param.called[OdsTable] == 1
            assert perform_time > 1

    def test_wait_for_equalize_raw_ctl_to_ods_raised(self):
        # проверим что сработал timeout и скрипт не дождался выравнивания ctl
        task = get_streaming_initialization_tasks()
        fake_ctl = get_fake_ctl(raw_values=['2021-02-01 01:01:01'] * 2)
        with mock.patch('dmp_suite.replication.tasks.initialization.get_ctl', return_value=fake_ctl):
            with pytest.raises(WaitTimeout):
                task._wait_for_equalize_raw_ctl_to_ods(sleep_time=1, wait_time=1)

            assert fake_ctl.yt.get_param.called[RawTable] == 2

    # TODO: Remove xfail after DMPDEV-5976
    @pytest.mark.xfail
    @pytest.mark.slow
    def test_with_timeout(self):
        def just_sleep(*a):
            time.sleep(1)

        # проверим что срабатывает timeout при долгом выполнении таски
        task = get_streaming_initialization_tasks().arguments(
            backfill_timeout=cli.Float(default=0.1),
        )
        # переопределим метод '_run' у базового класса, что бы эмулировать долгое выполнение

        with mock.patch('dmp_suite.replication.tasks.initialization._InitializationTask._run', just_sleep):
            # после превышения ожидания прибивается процесс по пиду, что бы избежать завершения самого теста, запускаем
            # выполнение таски в отдельном процессе
            new_process = multiprocessing.Process(target=run_task, args=(task,))
            new_process.start()
            new_process.join(timeout=30)

            # сработал timeout на join и процесс не завершился по timout-у внутри кода
            assert new_process.exitcode is not None

            # проверяем, что этот процесс завершается принудительно
            assert abs(new_process.exitcode) in (signal.SIGINT, signal.SIGTERM)

