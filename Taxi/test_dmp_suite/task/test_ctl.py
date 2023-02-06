from argparse import Namespace
from datetime import datetime, timedelta
from functools import partial

import mock
import pytest

from connection import ctl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE, CTL_LAST_SYNC_DATE, Ctl, CTL_LAST_LOAD_DATE_MICROSECONDS
from dmp_suite.ctl.extensions.domain.greenplum import GPDomainProvider
from dmp_suite.ctl.storage import DictStorage
from dmp_suite.datetime_utils import Period, utcnow, format_datetime
from dmp_suite.greenplum import GPTable
from dmp_suite.table import LayeredLayout, Table
from dmp_suite.task import cli
from dmp_suite.task.args import use_ctl_last_load_date, utcnow_arg, use_arg, DatetimeArgPipe, ValueAccessor, CtlValueAccessor
from dmp_suite.task.base import AbstractPeriodCtlTask, AbstractTableTaskTarget, AbstractTaskTarget, CTL_EPOCH
from dmp_suite.task.cli import StartEndDate, parse_cli_args
from dmp_suite.task.execution import run_task, _expand_value_accessors, process_task_args
from dmp_suite.task.splitters import SplitInDays
from dmp_suite.greenplum.task import transformations as gp_transformations 

class FooPeriodCtlTask(AbstractPeriodCtlTask):
    def do_actual_work(self, args):
        yield


class TaskTarget(AbstractTaskTarget):
    @property
    def ctl_entity(self):
        pass


class FooTable(Table):
    pass


class TableTaskTarget(AbstractTableTaskTarget):
    table = FooTable


def ctl_getter(storage):
    return GPDomainProvider(Ctl(storage=storage))


default_ctl_getter = partial(ctl_getter, storage=DictStorage())


def test_task_without_target():
    task = FooPeriodCtlTask('test')
    with pytest.raises(ValueError):
        run_task(task)


def test_ctl_property():
    with pytest.raises(ValueError):
        assert FooPeriodCtlTask('test').ctl
    assert FooPeriodCtlTask('test', ctl_getter=default_ctl_getter).ctl


def test_ctl_entity():
    with pytest.raises(ValueError):
        assert FooPeriodCtlTask('test', ctl_getter=default_ctl_getter, targets=[TaskTarget()]).ctl_entity
    assert FooPeriodCtlTask('test', ctl_getter=default_ctl_getter, targets=[TableTaskTarget()]).ctl_entity


class GPFooTable(GPTable):
    __layout__ = LayeredLayout(name='test', layer='test')


class GPFooFooTable(GPTable):
    __layout__ = LayeredLayout(name='test_test', layer='test')


gp_foo_target = gp_transformations.GPTableTaskTarget(GPFooTable)
gp_foo_foo_target = gp_transformations.GPTableTaskTarget(GPFooFooTable)


def test_last_sync_date_trivial():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    now = utcnow()
    task = FooPeriodCtlTask('test', ctl_getter=local_ctl_getter, targets=[gp_foo_target])
    run_task(task)

    assert now < task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)


def test_last_sync_date_shifted_to_future():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    now = utcnow()
    task = FooPeriodCtlTask('test', ctl_getter=local_ctl_getter, targets=[gp_foo_target])

    task.ctl.set_param(GPFooTable, CTL_LAST_SYNC_DATE, now + timedelta(days=2))

    run_task(task)

    assert now + timedelta(days=2) == task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)


class LoopPeriodCtlTask(AbstractPeriodCtlTask):

    def __init__(self, name, ctl_getter, targets, loop_range=(-10, 1)):
        super().__init__(name, ctl_getter=ctl_getter, targets=targets)
        self.loop_range = loop_range

    def do_actual_work(self, args):
        for shift in range(*self.loop_range):
            yield args.now + timedelta(days=shift)
        if not len(range(*self.loop_range)):
            yield


def test_last_sync_date_in_loop():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    now = utcnow()
    task = LoopPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target]
    ).arguments(
        now=cli.Datetime(now)
    )

    run_task(task)

    assert now < task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)


def test_ctl_argument_is_required():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)
    task = LoopPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target]
    ).set_ctl()

    with pytest.raises(ValueError):
        run_task(task)


def test_ctl_date_in_loop():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)
    now = utcnow()

    task = LoopPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target]
    ).arguments(
        now=cli.Datetime(now),
        period=StartEndDate.from_ctl(start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH), end=utcnow_arg())
    ).set_ctl()

    task.ctl.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))

    run_task(task)

    assert now == task.ctl.get_param(GPFooTable, CTL_LAST_LOAD_DATE)


def test_ctl_date_for_multiple_targets():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)
    now = utcnow()

    task = LoopPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target, gp_foo_foo_target]
    ).arguments(
        now=cli.Datetime(now),
        period=StartEndDate.from_ctl(start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH), end=utcnow_arg())
    ).set_ctl()

    task.ctl.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))
    task.ctl.set_param(GPFooFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))

    run_task(task)

    assert now == task.ctl.get_param(GPFooTable, CTL_LAST_LOAD_DATE)
    assert now == task.ctl.get_param(GPFooFooTable, CTL_LAST_LOAD_DATE)


def test_ctl_period_splitting():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    with mock.patch('connection.ctl.get_ctl', return_value=ctl.WrapCtl(storage=storage)):
        now = utcnow()

        ctl.get_ctl().gp.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))

        task = FooPeriodCtlTask(
            'test',
            ctl_getter=local_ctl_getter,
            targets=[gp_foo_target]
        ).arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH),
                end=utcnow_arg()
            ),
        ).set_ctl().split(
            splitter=SplitInDays()
        )

        args = process_task_args(task)
        # При обработке таска сначала вызывается process_task_args
        # затем _expand_value_accessors и только потом split_args
        _expand_value_accessors(args)
        splits = list(task.split_args(args))

    assert len(splits) == 11


def test_ctl_period_last_sync_with_splitting():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    now = utcnow()

    with mock.patch('connection.ctl.get_ctl', return_value=ctl.WrapCtl(storage=storage)):
        ctl.get_ctl().gp.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))
        ctl.get_ctl().gp.set_param(GPFooTable, CTL_LAST_SYNC_DATE, now - timedelta(days=10))

        task = FooPeriodCtlTask(
            'test',
            ctl_getter=local_ctl_getter,
            targets=[gp_foo_target]
        ).arguments(
            period=StartEndDate.from_ctl(
                start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH),
                end=utcnow_arg()
            ),
        ).set_ctl().split(
            splitter=SplitInDays()
        )

        run_task(task)

        assert now < task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)


def test_ctl_date_and_manual_period():
    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)
    now = utcnow()

    task = FooPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target]
    ).arguments(
        period=StartEndDate.from_ctl(start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH), end=utcnow_arg())
    ).set_ctl()

    task.ctl.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))

    args = Namespace()
    setattr(args, 'period', Period(now - timedelta(days=5), now))

    with pytest.raises(ValueError):
        task.split_args(args)

    args = Namespace()
    setattr(args, 'period', Period(now - timedelta(days=11), now))

    assert task.split_args(args)


def test_parse_cli_args_uses_user_specified_values_instead_of_ctl():
    # Проверяем, что настройки можно переопределить
    # из командной строки.

    default_time = datetime(2020, 1, 1)
    default_time_pipe = DatetimeArgPipe(lambda _, __: default_time)
    args = {
        'period': StartEndDate.from_ctl(
            start=default_time_pipe,
            end=default_time_pipe,
        )
    }

    # Сначала убедимся, что если с командной строки ничего не передано,
    # то будут результатом парсинга будет CtlValueAccessor.
    # Таким образом мы сможем отложить его вычисление до момента, когда уже
    # должен будет запускаться конкретный таск.
    command_line_args = []
    parsed = parse_cli_args(args, command_line_args)

    assert isinstance(parsed.period, CtlValueAccessor)

    # Теперь попробуем переопределить значения
    command_line_args = [
        '--start_date', '2021-03-04',
        '--end_date', '2021-07-08',
    ]
    parsed = parse_cli_args(args, command_line_args)
    assert parsed.period.start == datetime(2021, 3, 4, 0, 0, 0, 0)
    assert parsed.period.end == datetime(2021, 7, 8, 23, 59, 59, 999999)


class AddDeltaTestHook(ValueAccessor):

    def __init__(self, delta):
        self.delta = delta

    def get_value(self, args, _):
        return args.now + self.delta


PRE_HOOK = use_arg('now').transform(lambda x: x + timedelta(days=51))
POST_HOOK = AddDeltaTestHook(timedelta(days=51))


@pytest.mark.parametrize(
    'hook,force,n_loops,expected_ctl_delta', [
        (None, False, 0, timedelta(days=-10)),
        (None, False, 1, timedelta(days=1)),
        (None, False, 10, timedelta(days=10)),
        (None, True, 0, timedelta(days=-10)),
        (None, True, 1, timedelta(days=1)),
        (None, True, 10, timedelta(days=10)),
        (PRE_HOOK, False, 0, timedelta(days=51)),
        (PRE_HOOK, False, 1, timedelta(days=1)),
        (PRE_HOOK, False, 10, timedelta(days=10)),
        (PRE_HOOK, True, 0, timedelta(days=51)),
        (PRE_HOOK, True, 1, timedelta(days=51)),
        (PRE_HOOK, True, 10, timedelta(days=51)),
        (POST_HOOK, False, 0, timedelta(days=51)),
        (POST_HOOK, False, 1, timedelta(days=1)),
        (POST_HOOK, False, 10, timedelta(days=10)),
        (POST_HOOK, True, 0, timedelta(days=51)),
        (POST_HOOK, True, 1, timedelta(days=51)),
        (POST_HOOK, True, 10, timedelta(days=51)),
    ]
)
def test_ctl_setting_with_hook(hook, force, n_loops, expected_ctl_delta):

    storage = DictStorage()
    local_ctl_getter = partial(ctl_getter, storage=storage)

    now = utcnow()

    task = LoopPeriodCtlTask(
        'test', ctl_getter=local_ctl_getter, targets=[gp_foo_target], loop_range=(1, 1 + n_loops)
    ).arguments(
        now=cli.Datetime(now),
        period=StartEndDate.from_ctl(start=use_ctl_last_load_date(GPFooTable, default=CTL_EPOCH), end=utcnow_arg())
    ).set_ctl(
        hook=hook,
        force=force,
    )

    task.ctl.set_param(GPFooTable, CTL_LAST_LOAD_DATE, now - timedelta(days=10))

    run_task(task)
    assert now + expected_ctl_delta == task.ctl.get_param(GPFooTable, CTL_LAST_LOAD_DATE)


@pytest.mark.parametrize(
    'ctl_param, ctl_dttm, start_dttm', [
        (CTL_LAST_LOAD_DATE, datetime(2021, 4, 6, 23, 59, 59), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE, datetime(2021, 4, 7, 0, 0, 0), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE, datetime(2021, 4, 7, 0, 0, 1), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE_MICROSECONDS, datetime(2021, 4, 6, 23, 59, 59, 999999), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE_MICROSECONDS, datetime(2021, 4, 7, 0, 0, 0), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE_MICROSECONDS, datetime(2021, 4, 7, 0, 0, 1), datetime(2021, 4, 7)),
    ]
)
def test_period_start_check_success(ctl_param, ctl_dttm, start_dttm):

    domain = GPDomainProvider(Ctl(storage=DictStorage()))
    domain.set_param(GPFooTable, ctl_param, ctl_dttm)

    task = FooPeriodCtlTask(
        'test_period_start_check_success',
        ctl_getter=lambda: domain,
        targets=[gp_foo_target],
    ).set_ctl(
        param=ctl_param,
    ).arguments(
        period=StartEndDate(default=Period(start_dttm, start_dttm + timedelta(days=1)))
    )

    run_task(task)


@pytest.mark.parametrize(
    'ctl_param, ctl_dttm, start_dttm', [
        (CTL_LAST_LOAD_DATE, datetime(2021, 4, 6, 23, 59, 58), datetime(2021, 4, 7)),
        (CTL_LAST_LOAD_DATE_MICROSECONDS, datetime(2021, 4, 6, 23, 59, 59, 999998), datetime(2021, 4, 7)),
    ]
)
def test_period_start_check_fail(ctl_param, ctl_dttm, start_dttm):
    domain = GPDomainProvider(Ctl(storage=DictStorage()))
    domain.set_param(GPFooTable, ctl_param, ctl_dttm)

    task = FooPeriodCtlTask(
        'test_period_start_check_success',
        ctl_getter=lambda: domain,
        targets=[gp_foo_target],
    ).set_ctl(
        param=ctl_param,
    ).arguments(
        period=StartEndDate(default=Period(start_dttm, start_dttm + timedelta(days=1)))
    )

    with pytest.raises(ValueError) as error:
        run_task(
            task,
            [
                '--start_date', format_datetime(start_dttm),
                '--end_date', format_datetime(start_dttm + timedelta(days=1))
            ]
        )
    assert 'should be before or at or just one tick after CTL' in error.value.args[0]


@pytest.mark.parametrize(
    'ctl_param, ctl_dttm, start_dttm', [
        (CTL_LAST_LOAD_DATE, datetime(2021, 4, 6, 23, 59, 58), datetime(2021, 4, 6)),
        (CTL_LAST_LOAD_DATE_MICROSECONDS, datetime(2021, 4, 6, 23, 59, 59, 999998), datetime(2021, 4, 6)),
    ]
)
def test_period_in_past(ctl_param, ctl_dttm, start_dttm):
    domain = GPDomainProvider(Ctl(storage=DictStorage()))
    domain.set_param(GPFooTable, ctl_param, ctl_dttm)

    task = FooPeriodCtlTask(
        'test_period_start_check_success',
        ctl_getter=lambda: domain,
        targets=[gp_foo_target],
    ).set_ctl(
        param=ctl_param,
    ).arguments(
        period=StartEndDate(default=Period(start_dttm, start_dttm + timedelta(days=1)))
    )

    now = utcnow()
    run_task(task)
    assert now < task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)

    # Period is in the past
    last_sync_date = task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)
    run_task(
        task,
        [
            '--start_date', format_datetime(start_dttm - timedelta(days=3)),
            '--end_date', format_datetime(start_dttm - timedelta(days=2))
        ]
    )
    assert last_sync_date == task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)

    # Period is in the future
    now = utcnow()
    run_task(
        task,
        [
            '--start_date', format_datetime(start_dttm),
            '--end_date', format_datetime(start_dttm + timedelta(days=1))
        ]
    )
    assert now < task.ctl.get_param(GPFooTable, CTL_LAST_SYNC_DATE)
