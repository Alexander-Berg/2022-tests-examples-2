import datetime
import mock
import pytest

from frozendict import frozendict
from dmp_suite import scales
from dmp_suite.datetime_utils import Period, utcnow
from dmp_suite.luigi.base import GraphBuildingError, make_luigi_graph
from dmp_suite.task.args import DatetimeArgPipe, const_period_arg, use_period_arg
from dmp_suite.task.base import PyTask, CtlWindow, with_args
from dmp_suite.task.cli import StartEndDate, Datetime, CliArg
from dmp_suite.task.execution import run_task, ExecutionMode, local_execution_args, process_task_args
from dmp_suite.task.run_history.storage import task_run_history_manager
from test_dmp_suite.task.test_base import temp_luigi_target_dir


def test_make_luigi_graph_for_ctl_params():
    period = StartEndDate.from_ctl(
        start=DatetimeArgPipe(utcnow),
        end=DatetimeArgPipe(utcnow),
    )
    def task_func():
        pass
    task = PyTask('test', task_func).arguments(
        period=period,
        now=Datetime(default='2019-01-01'),
    )
    args = process_task_args(
        task,
        raw_args=[],
        execution_mode=ExecutionMode.GRAPH,
    )
    luigi_task = make_luigi_graph(task, args, local_execution_args())
    # id таска должен содержать только один параметр - now,
    # а period должен игнорироваться, потому что он берётся из
    # Сtl и будет известен только в момент запуска таска.
    #
    # ID таска состоит из трёх частей:
    # - имени класса
    # - конкатенации первых трёх параметров приведённых к строке
    #   и урезанных до 16 символов. Тут это "2019_01_01_00_00"
    # - хэша от сортированного и конвертированного в JSON словаря
    #   со всеми значимыми параметрами. Тут это 0c468956ef.
    assert luigi_task.task_id == 'TestLuigiTask_2019_01_01_00_00_0c468956ef'

    # Убедимся, что если убрать из агрументов таска period, то
    # id и хэш останутся теми же:
    task = PyTask('test', task_func).arguments(
        now=Datetime(default='2019-01-01'),
    )
    args = process_task_args(
        task,
        raw_args=[],
        execution_mode=ExecutionMode.GRAPH,
    )
    luigi_task = make_luigi_graph(task, args, local_execution_args())
    assert luigi_task.task_id == 'TestLuigiTask_2019_01_01_00_00_0c468956ef'


def test_run_luigi_graph_for_clt_params(tmp_path):
    # Проверим, что CTL параметры не ресолвятся в дефолтное значение
    # в момент создания графа для Luigi.
    # Такие параметры должны вычисляться в момент запуска узла графа,
    # потому что они могут полагаться на вычисления в дочерних узлах,
    # а в момент создания графа эти вычисления ещё не сделаны.

    do_nothing = mock.MagicMock()
    get_start_date = mock.MagicMock(return_value='2021-01-01')
    get_end_date = mock.MagicMock(return_value='2021-04-01')

    period = StartEndDate.from_ctl(
        start=DatetimeArgPipe(get_start_date),
        end=DatetimeArgPipe(get_end_date),
    )
    # Напрямую передавать do_nothing нельзя,
    # потому что по моку PyTask не сможет понять сигнатуру
    # и не передаст в него args:
    def task_func(args):
        do_nothing(args)

    task = PyTask('test', task_func).arguments(
        period=period,
        now=Datetime(default='2019-01-01'),
    )

    with mock.patch('dmp_suite.task.execution._run_standalone') as run_standalone, \
         temp_luigi_target_dir(tmp_path):
        run_task(task, execution_mode=ExecutionMode.GRAPH)
        assert run_standalone.call_count == 1
        namespace = run_standalone.call_args[0][1]
        # При обработке параметров,
        # всё что связано с CTL должно оставаться нетронутым
        assert isinstance(namespace.period, CtlWindow)
        # а прочие ValueArgs - разворачиваться.
        # Это нужно чтобы Luigi мог понять по каким параметрам
        # сравнивать таски для дедупликации:
        assert isinstance(namespace.now, datetime.datetime)

    # Если же не мокать _run_standalone, то при вызове таска
    # все ValueAccessor должны быть раскрыты, а так же, вызов
    # таска должен быть сохранён в историю и там параметры так же
    # должны иметь свои финальные значения:
    with temp_luigi_target_dir(tmp_path):
        history_manager = task_run_history_manager()
        history_manager.reset()

        run_task(task, execution_mode=ExecutionMode.GRAPH)

        assert do_nothing.call_count == 1
        namespace = do_nothing.call_args[0][0]
        # Внутри таска мы должны иметь дело с конкретным периодом:
        assert isinstance(namespace.period, Period)

        # А в history должны были записаться
        history = history_manager.get_all()
        # В истории будет две записи:
        # - первая про таск целиком
        # - вторая про единственный сплит
        assert len(history) == 2
        # И в истории должен сохраниться конкретный период,
        # чтобы при при перезапусках воспроизводилась та же самая
        # ситуация, что была при первом запуске:
        for run in history.values():
            assert isinstance(run.args.period, Period)


@pytest.mark.parametrize(
    'initial_value, resulting_type',
    [
        ({'foo': 42, 'bar': 'minor'}, frozendict),
        (set(['one', 'two', 'tree']), frozenset),
        (['one', 'two', 'tree'], tuple),
        # Обычные типы
        ('just a string', str),
        (100500, int),

        # если тип уже из хэшируемых, то он не должен измениться
        (frozendict({'one': 1}), frozendict),
        (frozenset(['one', 'two']), frozenset),
        (tuple(['one', 'two']), tuple),
    ],
)
def test_with_dict_param(tmp_path, initial_value, resulting_type):
    def task_func():
        pass
    task = PyTask('test', task_func).arguments(
        ab_params=CliArg('A/B experiment parameters', default=initial_value)
    )
    with mock.patch('dmp_suite.task.execution._run_standalone') as run_standalone, \
         temp_luigi_target_dir(tmp_path):
        run_task(task, execution_mode=ExecutionMode.GRAPH)
        assert run_standalone.call_count == 1
        namespace = run_standalone.call_args[0][1]
        assert isinstance(namespace.ab_params, resulting_type)


def test_pass_args_throw_graph():
    def required_payload(args):
        assert args.period == scales.month.extend_to_period('2020-10-10')

    required = PyTask(
        'required',
        required_payload,
    ).arguments(
        period=StartEndDate(
            default=const_period_arg(start='2021-10-10', end='2021-10-20'),
        ),
    )

    root = PyTask(
        'root',
        lambda _: _,
    ).arguments(
        period=StartEndDate(
            default=const_period_arg(start='2020-10-10', end='2020-10-20'),
        ),
    ).requires(
        with_args(
            required,
            period=use_period_arg().extend(scales.month),
        ),
    )

    run_task(root, execution_mode=ExecutionMode.GRAPH)


def test_pass_args_throw_graph_raises_on_wrong_arg():
    required = PyTask(
        'required',
        lambda _: _,
    ).arguments(
        period=StartEndDate(
            default=const_period_arg(start='2021-10-10', end='2021-10-20'),
        ),
    )

    root = PyTask(
        'root',
        lambda _: _,
    ).arguments(
        periods=StartEndDate(
            default=const_period_arg(start='2020-10-10', end='2020-10-20'),
        ),
    ).requires(
        with_args(
            required,
            period=use_period_arg().extend(scales.month),
        ),
    )
    with pytest.raises(GraphBuildingError):
        run_task(root, execution_mode=ExecutionMode.GRAPH)
