import logging
import random

import pytest
import mock
import time
import threading
import datetime as dt
import os

from multiprocessing import Event
from multiprocessing.managers import SyncManager

from connection.ctl import get_ctl
from connection.yt import Pool
from dmp_suite.ctl import CTL_DISABLED_UNTIL_DTTM
from dmp_suite.lock.postgres import prolongable_lock
from dmp_suite.lock.typed_lock.lock import TypedBatchLock
from dmp_suite.migration.exceptions import MigrationError
from dmp_suite.migration.flow import _DisableTasksTask, _EnableTasksTask
from dmp_suite.task.locks import TaskExclusiveLockProvider
from dmp_suite.yt.migration.base import _YtMigrationTask
from dmp_suite.table import LayeredLayout
from dmp_suite.task import PyTask, cli
from dmp_suite.task.base import IdempotentPyTask
from dmp_suite.task.execution import run_migration, MIGRATION_EXECUTION_ARGS
from dmp_suite.yt import YTTable, Int, dtu
from dmp_suite.yt.migration import add_columns
from dmp_suite.migration import migration, run_backfill
from init_py_env import settings
from test_dmp_suite.yt import utils
from dmp_suite.yt.task import target as yt_task_target

from .utils import create, write, random_ticket


# PyCharm рисует сереньким, но без этого не работает фикстура в тесте:
from test_dmp_suite.task.test_base import patch_luigi_target, _patch_luigi_target_tmpdir


@pytest.mark.slow
@patch_luigi_target
def test_task_disable():
    # Проверяем, что таск, создающий исходную таблицу,
    # будет отключён на время миграции.
    ctl = get_ctl()

    @utils.random_yt_table
    class TableBefore(YTTable):
        a = Int()

    class TableAfter(TableBefore):
        b = Int()

    # Подготовим данные в табличке
    create(TableBefore)
    write(TableBefore, [{'a': 100500}])

    # Опишем миграцию
    # Сначала сделаем фейковый таск, который "создаёт" таблицу
    table_creator = PyTask(
        'table_creator',
        lambda: None,
        targets=[yt_task_target.YtTaskTarget(TableAfter)],
    )

    # Чтобы убедиться, что таск отключен, добавим в состав миграции
    # шаг, который проверит CTL.
    # Так как каждый run_migration запускает каждый шаг в подпроцессе,
    # то для проверки используем Event из multiprocessing.
    check_called = Event()

    def do_the_check():
        assert ctl.task.is_disabled(table_creator)
        check_called.set()

    check_table = IdempotentPyTask('checking_task', do_the_check)

    # Так как тут мы таски определяем внутри теста,
    # сборка дерева тасков работать не будет, поэтому замокаем
    # функцию, которая возвращает таски создающие табличку.
    # Потом алгоритм должен будет задисейблить эти таски:
    def fake_table_to_creator_tasks(table):
        if table is TableAfter:
            return [table_creator]
        else:
            return []

    ctl.task.reset_disable(table_creator)  # на всякий случай сбросим флаг отключенного таска

    with mock.patch('dmp_suite.migration.flow._table_to_creator_tasks', fake_table_to_creator_tasks):
        task = migration(
            random_ticket(),
            add_columns(TableAfter),
            check_table,
        )

    run_migration(task)

    # На всякий случай проверим, что наш проверочный таск вызвался.
    # Потому что если цепочка тасков строится неправильно, то он может и не быть вызван.
    assert check_called.is_set()

    # По завершении миграции нужно удостовериться, что CTL сбросился
    disabled_util = ctl.task.get_param(table_creator, CTL_DISABLED_UNTIL_DTTM)
    assert disabled_util is None


def test_migration_steps_shouldnt_have_requirements():
    # Проверяем, что таск, использующиеся, как шаги миграции, не являются графами.
    # Потому что мы пока не хотим ничего усложнять в этом месте.

    def do_nothing():
        pass

    dependency = PyTask('dependency', do_nothing)

    step = PyTask('task', do_nothing) \
        .requires(dependency)

    with pytest.raises(MigrationError):
        migration(random_ticket(), step)


def test_all_migration_steps_are_idempotent():
    # Проверяем, что таск, использующиеся, как шаги миграции, не являются графами.
    # Потому что мы пока не хотим ничего усложнять в этом месте.

    def do_nothing():
        pass

    task1 = IdempotentPyTask('task1', do_nothing)

    task2 = PyTask('task2', do_nothing)

    with pytest.raises(MigrationError):
        migration(
            random_ticket(),
            task1,
            task2,
        )


def test_disable_task_lock_list():
    # Проверяем, что Disable таск, в качестве списка локов выдаёт
    # локи всех отключаемых тасков.

    # Сначала сделаем фейковый таск, который "создаёт" таблицу
    task_a = PyTask('task_a', lambda: None)
    task_b = PyTask('task_b', lambda: None)
    task_c = PyTask('task_c', lambda: None)
    # Тут таски специально идут вразнобой, чтобы проверить
    # что get_lock вернёт их в отсортированном порядке:
    disable_task = _DisableTasksTask('ticket', [task_c, task_a, task_b])
    assert disable_task._get_locks_to_wait() == ('task_a', 'task_b', 'task_c')


def test_disable_enable_task_lock_name():
    # Имя лока должно содержать названия всех
    # отключаемых тасок в алфавитном порядке.
    task_a = PyTask('task_a', lambda: None)
    task_b = PyTask('task_b', lambda: None)
    task_c = PyTask('task_c', lambda: None)

    disable_task = _DisableTasksTask('ticket', [task_c, task_a, task_b])
    assert disable_task.get_lock() == ('disable_tasks_ticket_task_a_task_b_task_c',)

    enable_task = _EnableTasksTask('ticket', [task_c, task_a, task_b])
    assert enable_task.get_lock() == ('enable_tasks_ticket_task_a_task_b_task_c',)


@pytest.mark.slow
def test_disable_task_waits_for_locks():
    # Проверяем, что Disable таск, дождётся пока нужные локи будут отпущены
    # Сначала сделаем фейковый таск, который "создаёт" таблицу
    random_suffix = str(random.randint(1000, 9999))
    task_a = PyTask(f'task_a_{random_suffix}', lambda: None)
    task_b = PyTask(f'task_b_{random_suffix}', lambda: None)
    task_c = PyTask(f'task_c_{random_suffix}', lambda: None)

    # Стартанём отдельный тред, который подержит локи в течении 5 секунд
    locker_sleep_time = 10
    lock_aquired = threading.Barrier(2, timeout=30)

    def locker():
        nonlocal lock_aquired
        locks = []
        locks.extend(task_b.get_lock())
        locks.extend(task_c.get_lock())

        requested_locks = []
        for provider in TaskExclusiveLockProvider.from_names(locks):
            requested_locks.extend(provider.static_locks())

        lock = TypedBatchLock(
            *requested_locks,
            # Теоретически, мы должны захватить лок сразу же,
            # но на всякий случай установим таймаут в 3s, чтобы
            # не ждать бесконечно в случае если лок почему-то занят
            acquire_timeout=dt.timedelta(seconds=3),
            acquire_interval=dt.timedelta(seconds=1),
        )
        with lock:
            lock_aquired.wait()
            time.sleep(locker_sleep_time)

    started_at = time.monotonic()
    locker_thread = threading.Thread(target=locker, daemon=True)
    locker_thread.start()

    # Дадим время локеру захватить локи
    lock_aquired.wait()

    # Так как локи старого образца "reentrant" и в разных
    # потоках одного процесса попытка взятия лока повторно
    # будет приводить к успеху, то нам надо сэмулировать
    # ситуацию, что миграция запускается в каком-то
    # другом процессе:
    fake_pid = random.randint(1, 65535)
    fake_ppid = random.randint(1, 65535)

    with mock.patch('os.getpid', return_value=fake_pid), \
         mock.patch('os.getppid', return_value=fake_ppid):
        # Теперь стартанём отключающий таск и убедимся, что он будет
        # работать не меньше locker_sleep_time секунд, потому что должен дождаться пока
        # locker отпустит локи:
        disable_task = _DisableTasksTask(random_suffix, [task_c, task_a, task_b])

        # Оборачиваем _run в декоратор, т.к. mock не шарится между процессами
        def deco(function):
            def inner(*args, **kwargs):
                disable_task.send_metrics_to_juggler = mock.MagicMock()
                function(*args, **kwargs)
                assert disable_task.send_metrics_to_juggler.call_count == 1
            return inner

        disable_task._run = deco(disable_task._run)

        run_migration(disable_task)
        total = time.monotonic() - started_at

        assert total >= locker_sleep_time


@pytest.mark.slow
@patch_luigi_target
def test_backfill_run():
    def _to_task_bound(task):
        o = mock.Mock()
        o.task = task
        return o

    with SyncManager() as sync_manager:
        run_log = sync_manager.dict()
        ctl = get_ctl()

        class SimpleMigration(_YtMigrationTask):
            def _run(self, args):
                # проверим что миграция запускается без ретраев
                assert args.retry_times == 1
                assert args.retry_sleep == 11
                assert args.pool == Pool.TAXI_DWH_BACKFILL

        class FakeTable(YTTable):
            __layout__ = LayeredLayout(name='test', layer='test')

            a = Int()

        class FakeTableNotOff(YTTable):
            __layout__ = LayeredLayout(name='test', layer='test')

            a = Int()

        def task1_func(args):
            # проверим что первая таска выключена через ctl
            assert ctl.task.is_disabled(task1)
            run_log['task1'] = args

        def task2_func(args):
            # проверим что вторая таска осталась включенной
            assert not ctl.task.is_disabled(task2)
            run_log['task2'] = args

        def task3_func(args):
            # проверим что выключилась по расписанию
            assert ctl.task.is_disabled(task3)
            run_log['task3'] = args

        period = dtu.Period('2020-01-01', '2020-02-01')
        task1 = PyTask('task1', task1_func, targets=[yt_task_target.YtTaskTarget(FakeTable)]).arguments(period=cli.Period(None))
        task2 = PyTask('task2', task2_func, targets=[yt_task_target.YtTaskTarget(FakeTableNotOff)])
        task3 = PyTask('task3', task3_func, targets=[yt_task_target.YtTaskTarget(FakeTableNotOff)])
        task1.requires(task2)
        backfill_task1 = run_backfill(task1, False, disable_by_targets=True, force_idempotent=True, period=cli.Period(period))
        backfill_task2 = run_backfill(task2, False, disable_by_targets=False, force_idempotent=True, flag=cli.Flag('test', True))
        backfill_task3 = run_backfill(task3, True, force_idempotent=True).backfill_arguments(flag=cli.Flag('test', True))

        ctl.task.reset_disable(task1)  # сбросим признак отключенного таска
        ctl.task.reset_disable(task2)
        ctl.task.reset_disable(task3)

        with mock.patch('dmp_suite.migration.flow.collect_tasks', return_value=[
            _to_task_bound(task1), _to_task_bound(task2), _to_task_bound(task3)
        ]):
            migration_task = migration(
                random_ticket(),
                backfill_task1,
                backfill_task2,
                backfill_task3,
                SimpleMigration('test', FakeTable),
            )
            with mock.patch.object(MIGRATION_EXECUTION_ARGS, 'lock_used', new=False):
                run_migration(migration_task)

        # проверим что работает запуск исторического пересчета как часть миграции
        assert run_log.get('task1')
        assert run_log.get('task2')
        assert run_log.get('task3')

        # проверим что в таску были переданы корректные аргументы
        assert period == run_log['task1'].period
        assert getattr(run_log['task2'], 'period', None) is None

        # проверим что при историческом пересчете, не запускались зависимые таски
        assert task2 not in backfill_task1.get_required_tasks()
        # проверим что таска включилась
        assert not ctl.task.is_disabled(task1)
        assert not ctl.task.is_disabled(task3)
