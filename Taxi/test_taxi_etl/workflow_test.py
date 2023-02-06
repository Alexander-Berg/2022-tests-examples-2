import pytest
import mock

from dmp_suite.py_env.service_setup import resolve_service_by_path
from dmp_suite.task.reactive.executor import ReactiveExecutorTask, _collect_reactive_tasks
from init_py_env import settings
from tests.workflow_test import base_workflow_checks
from contextlib import ExitStack

file_service = resolve_service_by_path(__file__)


@pytest.mark.parametrize('check', base_workflow_checks.get())
def test_all_case(check):
    check(file_service)


TOTAL = object()

@pytest.mark.skip(reason="Тест не работает на частично перевезённом сервисе")
# Этот тест я не стал добавлять во все сервисы,
# потому что он временный и нужен только пока не
# перевезём все сервисы в RTC:
@pytest.mark.parametrize(
    'gradual,rtc,num_tasks,fake_move_to_rtc',
     [
        (False, False, TOTAL, False),
        (False, True, TOTAL, False),
        (True, False, TOTAL, False),
        (True, True, 0, False),
         # После перемещения одного таска в RTC
        (True, False, (TOTAL, -1), True), # в LXC остаётся на 1 таск меньше
        (True, True, 1, True),   # в в RTC начинает запускаться 1 таск
         # Если gradual режим отключен, то независимо от флагов
         # и для LXC и для RTC будет одинаковое число тасков
        (False, False, TOTAL, True),
        (False, True, TOTAL, True),
     ]
)
def test_reactive_tasks_collection(gradual, rtc, num_tasks, fake_move_to_rtc):
    from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_metric.tariff_class_msk.loader import task as task_to_move

    # Чтобы тест не ломался каждый раз, когда добавляют новый таск,
    # нужно в параметрах передавать точку отсчёта и дельту
    # точка отсчёта может быть либо 0 либо TOTAL.
    # При этом TOTAL мы заменим на реальное число тасок с реактивным шедулингом
    if isinstance(num_tasks, tuple):
        anchor_count, delta = num_tasks
    else:
        anchor_count, delta = num_tasks, 0

    if anchor_count is TOTAL:
        anchor_count = len(_collect_reactive_tasks('taxi_etl'))

    num_tasks = anchor_count + delta

    with ExitStack() as stack:
        stack.enter_context(settings.patch({'reactive': {'gradual_rtc_migration': gradual}}))
        stack.enter_context(mock.patch('dmp_suite.task.reactive.executor.running_in_rtc', return_value=rtc))

        if fake_move_to_rtc:
            stack.enter_context(
                mock.patch.object(task_to_move.scheduler, 'enable_rtc', new=True)
            )
            stack.enter_context(
                mock.patch.object(task_to_move.scheduler, 'disable_lxc', new=True)
            )

        executor = ReactiveExecutorTask(service_name='taxi_etl')

        bounds = executor._collect_tasks()
        assert len(bounds) == num_tasks
