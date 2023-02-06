import pytest
import os

from datetime import datetime, date
from argparse import Namespace
from typing import Tuple, List

from dmp_suite import datetime_utils as dtu
from dmp_suite.exceptions import DWHError
from dmp_suite.task import PyTask, cli
from dmp_suite.task.base import AbstractTask
from dmp_suite.task.execution import run_task
from dmp_suite.task.run_history.storage import (
    task_run_history_manager, TaskRunStatus, TaskRunHistoryManager, TaskRunHistory
)
from dmp_suite.task.run_history.model import generate_uuid
from dmp_suite.task import splitters
from init_py_env import service
from test_dmp_suite.task.test_base import _patch_luigi_target_tmpdir

patch_luigi_target = pytest.mark.usefixtures(
    _patch_luigi_target_tmpdir.__name__
)


task_name = 'task_test'
default_period = dtu.period('2020-01-01', '2020-02-01 23:59:59')


def _get_run_id():
    return os.environ['TAXIDWH_RUN_ID']


def _get_run_info(task, run_id=None) -> Tuple[TaskRunHistory, List[TaskRunHistory]]:
    manager = task_run_history_manager()
    run_id = run_id or _get_run_id()

    task = manager.get_last_by_task(run_uuid=run_id or _get_run_id(), task=task)
    split_tasks = manager.get_sub_tasks(task)
    return task, split_tasks


def _get_period_task(name: str = task_name, raise_on_n_run: int = None, period=None) -> Tuple[AbstractTask, List]:
    """
    :param raise_on_n_run: при каком N вызове подымать исключение, None - всегда успешно
    Возвращает кортеж:
     - таска в которой выполнение завершается ошибкой при N вызове
     - список, в который будут добавлятся успешно обработанные периоды по мере выполнения
    """
    run_number = 0
    performed_periods = []

    def period_task_func(args):
        nonlocal run_number
        run_number += 1
        # на N вызове валимся с ошибкой
        if raise_on_n_run and run_number == raise_on_n_run:
            raise ValueError(f'Expected raise on {run_number} run')
        performed_periods.append(args.period)
    period = period or dtu.period('2020-01-01', '2020-02-01')
    task = PyTask(
        name,
        period_task_func
    ).split(
        splitters.SplitInMonths()
    ).arguments(
        period=cli.Period(period)
    )
    return task, performed_periods


class TestRunHistoryStoreOnExecute:
    def test_common_case(self):
        """
        Проверим сохранение в базовом кейсе
        """
        task = PyTask(task_name, lambda: True)
        run_task(task)

        task_hist, split_hist = _get_run_info(task)
        # проверим, что записалась информация о родительском таске
        assert task_hist.status == TaskRunStatus.success
        # проверим, что записалась информация в фейковом сплите
        assert split_hist[0].status == TaskRunStatus.success
        assert len(split_hist) == 1

    def test_store_every_split(self):
        """
        Проверим что сохраняется информация о запуске каждого сплита
        """
        # проверим, что записалась информация в первом и втором сплите
        task, performed_periods = _get_period_task()
        run_task(task)

        task_hist, splits_hist = _get_run_info(task)
        assert task_hist.status == TaskRunStatus.success
        assert len(splits_hist) == 2
        assert splits_hist[0].status == TaskRunStatus.success
        assert len(performed_periods) == 2

    def test_store_error_status(self):
        """
        Проверим что сохраняется информация о завершении с ошибкой
        """
        task, performed_periods = _get_period_task(raise_on_n_run=2)

        with pytest.raises(ValueError):
            run_task(task)

        task_hist, splits_hist = _get_run_info(task)
        # проверим, что записалась информация о родительском таске
        assert task_hist.status == TaskRunStatus.error
        # проверим, что записалась информация в первом и втором сплите
        assert splits_hist[0].status == TaskRunStatus.success
        assert splits_hist[1].status == TaskRunStatus.error
        assert len(performed_periods) == 1


class TestRunHistoryManager:
    @pytest.mark.slow
    @pytest.mark.parametrize("src_args", [
        Namespace(),
        Namespace(dttm=datetime(2020, 1, 1, 23, 59, 59), dt=date(2021, 1, 1), i=1, f=22.2, s='ss'),
        Namespace(period=dtu.period('2020-01-01', '2020-01-01 23:59:59')),
    ])
    def test_base_case(self, src_args):
        # проверим инициализацию класса из аргументов Namespace
        etl_service = service.name
        task, _ = _get_period_task('test')
        parent_id = generate_uuid()
        run_hist = TaskRunHistory.from_args(task, split_name=1, args=src_args, parent_id=parent_id)
        assert TaskRunStatus.created == run_hist.status
        assert f'{etl_service}.test' == run_hist.entity_name
        assert 1 == run_hist.split_name
        assert src_args == run_hist.args
        assert parent_id == run_hist.parent_id

        # проверим корректность записи/чтения из БД
        with TaskRunHistoryManager() as manager:
            manager.create(run_hist)
            run_hist_from_storage = manager.get_last_by_task(_get_run_id(), task, 1)
            assert run_hist == run_hist_from_storage
            manager.update_status(TaskRunStatus.success, run_hist_from_storage)

        # проверим смену статуса
        with TaskRunHistoryManager() as manager2:
            run_hist_from_storage = manager2.get_last_by_task(_get_run_id(), task, 1)
            assert TaskRunStatus.success == run_hist_from_storage.status
            assert TaskRunStatus.success.value == run_hist_from_storage.status_id

    @pytest.mark.slow
    def test_sub_tasks(self):
        # проверим не меняется порядок при чтение из БД
        run_id = _get_run_id()
        args = Namespace()
        with TaskRunHistoryManager() as manager:
            task, _ = _get_period_task('test')
            parent_task_hist = TaskRunHistory.from_args(task, run_uuid=run_id,  args=args)
            manager.create(parent_task_hist)
            items = [
                TaskRunHistory.from_args(task, run_uuid=run_id, split_name=i, args=args, parent_id=parent_task_hist.id)
                for i in range(12)
            ]

            manager.create_many(items)
            sub_tasks = manager.get_sub_tasks(parent_task_hist)
            assert len(sub_tasks) == 12
            assert list(sorted(sub_tasks, key=lambda i: int(i.split_name))) == sub_tasks

    @pytest.mark.slow
    def test_get_last_failed(self, generate_new_taxidwh_run_id):
        # проверим не меняется порядок при чтение из БД
        uniq_task_name = f'test_{generate_uuid()}'
        task, _ = _get_period_task(uniq_task_name
                                   )
        run_id = _get_run_id()
        item1 = TaskRunHistory.from_args(task, run_uuid=run_id, args=Namespace())
        generate_new_taxidwh_run_id()
        run_id = _get_run_id()
        item2 = TaskRunHistory.from_args(task, run_uuid=run_id, args=Namespace())
        generate_new_taxidwh_run_id()
        run_id = _get_run_id()
        item3 = TaskRunHistory.from_args(task, run_uuid=run_id, args=Namespace())

        with TaskRunHistoryManager() as manager:
            manager.create_many([item1, item2, item3])
            manager.update_status(TaskRunStatus.running, item2)
            manager.update_status(TaskRunStatus.error, item2)
            manager.update_status(TaskRunStatus.success, item3)

            last_failed = manager.get_last_failed_by_task(task)
            assert last_failed == item2


class TestRerunTask:
    @pytest.mark.slow
    def test_continue_on_exception(self, generate_new_taxidwh_run_id):
        """
        Проверка продолжения выполнения с места завершения
        """
        task, performed_periods = _get_period_task(raise_on_n_run=2)

        with pytest.raises(ValueError):
            run_task(task)

        task_hist, split_hist = _get_run_info(task)
        # проверим, что второй запуск завершился ошибкой
        assert task_hist.status == TaskRunStatus.error
        assert split_hist[0].status == TaskRunStatus.success
        assert split_hist[1].status == TaskRunStatus.error
        assert len(performed_periods) == 1
        rerun_id = _get_run_id()

        # перезапускаем с указанием rurun_id для продолжения
        generate_new_taxidwh_run_id()
        run_task(task, raw_args=['--rerun-id', rerun_id])
        task_hist, split_hist = _get_run_info(task, run_id=rerun_id)  # при перерасчетах история сохраняется под rerun_id
        # проверим, что успешно завершился расчет воторого периода и первый не пересчитывается повторно
        assert task_hist.status == TaskRunStatus.success
        assert split_hist[0].status == TaskRunStatus.success
        assert split_hist[1].status == TaskRunStatus.success
        assert len(performed_periods) == 2

        # проверим, что пересчет успешно завершенного таска не приводит к повторным расчетам и завершается успешно
        run_task(task, raw_args=['--rerun-id', rerun_id])
        assert len(performed_periods) == 2

    def test_got_error_with_wrong_rerun_id(self):
        task, performed_periods = _get_period_task(raise_on_n_run=2)
        with pytest.raises(DWHError):
            run_task(task, raw_args=['--rerun-id', 'wrong_guid'])
