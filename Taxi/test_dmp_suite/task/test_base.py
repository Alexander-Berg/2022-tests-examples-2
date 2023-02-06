import argparse
import contextlib
import pathlib
import shutil

import mock
import pytest
import time
import threading

from collections import Counter
from contextlib import ExitStack
from datetime import datetime
from functools import partial
from tempfile import NamedTemporaryFile
from typing import List, Text

from connection.yt import Pool
from dmp_suite.ctl import CTL_ENABLED_UNTIL_DTTM
from dmp_suite import datetime_utils as dtu
from dmp_suite.exceptions import RequiredTaskArgumentIsMissing
from dmp_suite.luigi.base import GraphExecutionFailed, _Target
from dmp_suite.py_env.service_setup import Service
from dmp_suite.table import Table
from dmp_suite.task import cli
from dmp_suite.task.args import use_arg
from dmp_suite.task.base import (
    resolve_task_instance, PyTask, AbstractTask, collect_tasks,
    TaskBound, primary_bound_path, BoundPath, AbstractTableTaskTarget,
    TaskRequirementError, with_args,
)
from dmp_suite.task.cli import CliArg, YTPool, RequiredArg, Flag
from dmp_suite.task.exceptions import TaskDependencyDisabledError, TaskSkippedError, InvalidTargetTypeError
from dmp_suite.task.execution import run_task, ExecutionArgs, ExecutionMode, process_task_args
from dmp_suite.task.splitters import (
    SplitInDays, SplitInWeeks, SplitInEqualPeriods, SplitInMonths,
    SplitInYears, Splitter, ListSplitter
)
from dmp_suite.task.cron import Cron
from init_py_env import settings
from test_dmp_suite.task.utils import create_task, fake_module, SimpleTask


@pytest.fixture(autouse=True)
def monitoring_mock():
    patch_ = mock.patch('dmp_suite.task.execution.get_task_monitoring')
    with patch_ as mock_:
        yield mock_


@pytest.fixture(autouse=True)
def accident_mock():
    patch_ = mock.patch('dmp_suite.task.execution._create_accident')
    with patch_ as mock_:
        yield mock_


# luigi таски используют RunAnywayTarget как таргет.
# RunAnywayTarget создает временные файлы - признак что таск завершился.
# Так как в тестах названия тасков пересекаются, нужно обеспечить пересчет таска
# в каждом тесте. Для этого `_patch_luigi_target_tmpdir`/`@patch_luigi_target`
# патчит код так, чтобы  RunAnywayTarget использовал временную директорию
# на каждый тест.

# В рамках же данной фикстуры запрещаем использованние непатченной версии
# RunAnywayTarget.
@pytest.fixture(autouse=True, scope='module')
def _patch_luigi_target_raise():
    def temp_dir(self, obj, cls):
        raise RuntimeError(
            'test luigi graph with `@patch_luigi_target`')

    patch_temp_dir = mock.patch.object(
        _Target, 'temp_dir', new_callable=mock.PropertyMock)

    with patch_temp_dir as temp_dir_mock:
        temp_dir_mock.__get__ = mock.Mock(side_effect=temp_dir)
        yield


@contextlib.contextmanager
def temp_luigi_target_dir(tmp_path: pathlib.Path):
    """
    Этот контекстный менеджер можно использовать
    в тех тестах, где надо запустить run_task
    несколько раз. Каждый запуск следует обернуть
    в этот контекстный менеджер.

    На вход надо передать
    """
    luigi_target_path = tmp_path / "luigi_target"
    luigi_target_path.mkdir()

    patch_temp_dir = mock.patch.object(
        _Target, 'temp_dir', new_callable=mock.PropertyMock)
    with patch_temp_dir as temp_dir_mock:
        temp_dir_mock.__get__ = mock.Mock(return_value=str(luigi_target_path))
        yield
        shutil.rmtree(luigi_target_path)


@pytest.fixture
def _patch_luigi_target_tmpdir(tmp_path):
    with temp_luigi_target_dir(tmp_path):
        yield


patch_luigi_target = pytest.mark.usefixtures(
    _patch_luigi_target_tmpdir.__name__
)


@contextlib.contextmanager
def collect(collected_tasks) -> List[TaskBound]:
    with mock.patch('dmp_suite.task.base.find_objects', return_value=collected_tasks):
        yield collect_tasks('fake_module')


@contextlib.contextmanager
def multiprocess_results():
    with NamedTemporaryFile(mode='w+') as fd:
        class Results:
            @staticmethod
            def add(line):
                fd.read()
                fd.write(line + '\n')
                fd.flush()

            @staticmethod
            def get():
                fd.seek(0)
                return list(filter(None, fd.read().split('\n')))

        yield Results


class fake_module2:
    pass


class TestCollectTask:
    def test_single_task(self):
        task = create_task('task')
        with collect([(fake_module, 'task', task)]) as task_bounds:
            assert len(task_bounds) == 1
            assert task_bounds[0].task == task
            assert primary_bound_path(task_bounds[0]) == BoundPath(fake_module, 'task')

    def test_no_task(self):
        with collect([]) as task_bounds:
            assert len(task_bounds) == 0

    def test_multiple_declaration(self):
        task = create_task('task')
        collected_tasks = [
            (fake_module, 'task_2', task),
            (fake_module, 'task_1', task),
            (fake_module, 'task_3', task),
            (fake_module2, 'task', task)
        ]
        with collect(collected_tasks) as task_bounds:
            assert len(task_bounds) == 1
            assert task_bounds[0].task == task
            assert primary_bound_path(task_bounds[0]) == BoundPath(fake_module, 'task_1')

    def test_primary_module(self):
        task = create_task('task')
        task.set_primary_module(fake_module2.__name__)

        collected_tasks = [
            (fake_module, 'task_2', task),
            (fake_module, 'task_1', task),
            (fake_module, 'task_3', task),
            (fake_module2, 'task', task)
        ]
        with collect(collected_tasks) as task_bounds:
            assert len(task_bounds) == 1
            assert task_bounds[0].task == task
            assert primary_bound_path(task_bounds[0]) == BoundPath(fake_module2, 'task')

    def test_multiple_primary_declaration(self):
        task = create_task('task')
        task.set_primary_module(fake_module2.__name__)

        collected_tasks = [
            (fake_module, 'task_2', task),
            (fake_module, 'task_1', task),
            (fake_module, 'task_3', task),
            (fake_module2, 'task_1', task),
            (fake_module2, 'task_2', task)
        ]
        with collect(collected_tasks) as task_bounds:
            assert len(task_bounds) == 1
            assert task_bounds[0].task == task
            assert primary_bound_path(task_bounds[0]) == BoundPath(fake_module2, 'task_1')

    def test_multiple_task(self):
        task_a = create_task('task_a')
        task_b = create_task('task_b')
        collected_tasks = [
            (fake_module, 'task_a1', task_a),
            (fake_module, 'task_a2', task_a),
            (fake_module, 'task_b', task_b),
        ]
        with collect(collected_tasks) as task_bounds:
            task_bounds.sort(key=lambda d: d.task.name)
            assert [d.task for d in task_bounds] == [task_a, task_b]
            assert primary_bound_path(task_bounds[0]) == BoundPath(fake_module, 'task_a1')
            assert primary_bound_path(task_bounds[1]) == BoundPath(fake_module, 'task_b')


class TestResolveTaskInstance:
    def test_class_task(self):
        with pytest.raises(TypeError):
            # Мы не можем автоматически сделать из класса таска его инстанс,
            # так как для этого требуется передать в него name.
            resolve_task_instance(SimpleTask)

    def test_instance_task(self):
        # resolve_task_instance возвращает инстанс как есть
        task_instance = create_task('test_task')
        result = resolve_task_instance(task_instance)
        assert result is task_instance

    def test_string_task_path(self):
        task_instance = create_task('test_task')

        with mock.patch('dmp_suite.task.base.get_object_by_path', return_value=task_instance):
            result = resolve_task_instance('path.to.task_instance')
            assert isinstance(result, SimpleTask)

    def test_string_task_name(self):
        task_instance = create_task('test_task')

        with ExitStack() as stack:
            stack.enter_context(
                mock.patch(
                    'sources_root.ETL_SERVICES',
                    ['test_etl']
                )
            )
            stack.enter_context(
                mock.patch(
                    'init_py_env.service',
                    Service('test_etl', None, None, None),
                )
            )
            stack.enter_context(
                mock.patch(
                    'dmp_suite.task.base.collect_tasks',
                    return_value=[TaskBound(task_instance)],
                )
            )
            stack.enter_context(
                mock.patch(
                    'dmp_suite.task.base.primary_bound_path',
                    return_value=BoundPath(mock, 'mock'),
                )
            )
            result = resolve_task_instance('test_task')
            assert isinstance(result, SimpleTask)

    def test_invalid_task(self):
        with pytest.raises(TypeError):
            resolve_task_instance(object())


class TestRunTask:
    NoGivenExpected = object()

    @pytest.mark.parametrize('cli_args_def, cli_args, local_default, expected', [
        (None, None, None, NoGivenExpected),
        (dict(pool=YTPool()), None, None, None),
        (dict(pool=YTPool()), ['--pool', Pool.TAXI_DWH_PRIORITY.value], None, Pool.TAXI_DWH_PRIORITY),
        (dict(pool=YTPool(Pool.TAXI_DWH_BATCH)), None, None, Pool.TAXI_DWH_BATCH),
        (
        dict(pool=YTPool(Pool.TAXI_DWH_BATCH)), ['--pool', Pool.TAXI_DWH_PRIORITY.value], None, Pool.TAXI_DWH_PRIORITY),
        (dict(pool=YTPool()), None, {'pool': Pool.RESEARCH}, Pool.RESEARCH),
        (dict(pool=YTPool()), ['--pool', Pool.TAXI_DWH_PRIORITY.value], {'pool': Pool.RESEARCH}, Pool.RESEARCH),
        (dict(pool=YTPool(Pool.TAXI_DWH_BATCH)), None, {'pool': Pool.RESEARCH}, Pool.RESEARCH),
        (dict(pool=YTPool(Pool.TAXI_DWH_BATCH)), ['--pool', Pool.TAXI_DWH_PRIORITY.value], {'pool': Pool.RESEARCH},
         Pool.RESEARCH),
    ])
    def test_args(self, cli_args_def, cli_args, local_default, expected):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask(
            'task', func, sources=None, targets=None
        )
        if cli_args_def:
            task.arguments(**cli_args_def)

        run_task(task, cli_args, **(local_default or {}))
        func_mock.assert_called()
        if expected is not self.NoGivenExpected:
            assert func_mock.call_args[0][0].pool is expected

    @pytest.mark.parametrize('cli_args_def, cli_args, local_default', [
        ({}, None, {'pool': Pool.RESEARCH}),
        (dict(flag=Flag()), None, {'pool': Pool.RESEARCH}),
    ])
    def test_unexpected_local_args(self, cli_args_def, cli_args, local_default):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask(
            'task', func, sources=None, targets=None
        )
        if cli_args_def:
            task.arguments(**cli_args_def)

        with pytest.raises(Exception):
            run_task(task, cli_args, **(local_default or {}))

    def test_argparse_namespace_and_optional_args(self):
        # Проверим, что в PyTask можно передать функцию,
        # которая принимает один позиционный аргумент и опциональные
        # аргументы со значениями по-умолчанию.
        passed_args = None

        def func(args, some_arg=100500):
            nonlocal passed_args
            passed_args = {'args': args, 'some_arg': some_arg}

        task = PyTask('task', func)
        run_task(task)
        assert isinstance(passed_args['args'], argparse.Namespace)
        assert passed_args['some_arg'] == 100500

    def test_optional_args_only(self):
        # Проверим, что в PyTask можно передать функцию,
        # которая имеет только опциональные
        # аргументы со значениями по-умолчанию.
        #
        # В этом случае, PyTask не должен пытаться передать
        # в функцию аргументы от argparse.
        passed_args = None

        def func(some_arg=100500):
            nonlocal passed_args
            passed_args = {'some_arg': some_arg}

        task = PyTask('task', func)
        run_task(task)
        assert passed_args == {'some_arg': 100500}

    def test_variadic_args(self):
        # Проверим, что в PyTask можно передать функцию,
        # которая имеет произвольное количество аргументов.
        #
        # В такую функцию, PyTask не должен передавать никаких
        # аргументов.
        passed_args = None

        def func(*args, **kwargs):
            nonlocal passed_args
            passed_args = {'args': args, 'kwargs': kwargs}

        task = PyTask('task', func)
        run_task(task)
        assert len(passed_args['args']) == 0
        assert len(passed_args['kwargs']) == 0

    def test_class_cli_args(self):
        # Проверим, что если class-level атрибуты
        # автоматически возвращаются методом get_arguments

        class FooTask(AbstractTask):
            pool = YTPool(Pool.RESEARCH)

            def _run(self, args):
                pass

        task = FooTask('test')
        result = task.get_arguments()
        assert result['pool'] is FooTask.pool

    def test_arguments_method_does_not_affect_other_instances(self):
        class FooTask(AbstractTask):
            pool = YTPool(Pool.RESEARCH)

            def _run(self, args):
                pass

        first = FooTask('first')
        second = FooTask('second').arguments(pool=YTPool(Pool.TAXI_DWH_BATCH))
        third = FooTask('third').arguments(pool=YTPool(Pool.TAXI_DWH_PRIORITY))

        assert first.get_arguments()['pool'] is FooTask.pool
        assert second.get_arguments()['pool'].default == Pool.TAXI_DWH_BATCH.value
        assert third.get_arguments()['pool'].default == Pool.TAXI_DWH_PRIORITY.value

    def test_nested_class_cli_args(self):
        # Проверим, что если class-level атрибуты
        # автоматически возвращаются методом get_arguments
        # даже для классов-наследников

        class FooTask(AbstractTask):
            pool = YTPool(Pool.RESEARCH)

            def _run(self, args):
                pass

        class BarTask(FooTask):
            another_pool = YTPool(Pool.RESEARCH)

        task = BarTask('test')
        result = task.get_arguments()
        assert result['pool'] is FooTask.pool
        assert result['another_pool'] is BarTask.another_pool

    def test_required_args_should_be_provided(self):
        # Если какого-то обязательного параметра не задали через
        # вызов метода arguments, то попытка распарсить аргументы
        # должна падать.
        class SomeTask(AbstractTask):
            pool = RequiredArg()

            def _run(self, args):
                pass

        task = SomeTask('test')

        with pytest.raises(RequiredTaskArgumentIsMissing):
            # Тут совершенно неважно, что мы передаём в метод.
            task.parse_cli_args([])


class TestSplitting:

    def test_split_by_class_attribute(self):
        runned_with_args = []

        class SplitByChars(Splitter):
            def split(self, value: Text):
                return list(value)

        class ParametrizedTask(SimpleTask):
            text = SplitByChars(CliArg('Текст для обработки'))

            def _run(self, args):
                runned_with_args.append(args.text)

        task = ParametrizedTask('test')

        run_task(task, text='Hello')
        assert runned_with_args == ['H', 'e', 'l', 'l', 'o']

    def test_split_by_arguments_method(self):
        runned_with_args = []

        class SplitByChars(Splitter):
            def split(self, value: Text):
                return list(value)

        class ParametrizedTask(SimpleTask):
            def _run(self, args):
                runned_with_args.append(args.text)

        # Зададим параметр через метод, сплиттер должен работать и в этом случае
        task = ParametrizedTask('test') \
            .arguments(
            text=SplitByChars(CliArg('Текст для обработки'))
        )

        run_task(task, text='Hello')
        assert runned_with_args == ['H', 'e', 'l', 'l', 'o']

    def test_split_by_split_method(self):
        runned_with_args = []

        class SplitByChars(Splitter):
            def split(self, value: Text):
                return list(value)

        class ParametrizedTask(SimpleTask):
            text = CliArg('Текст для обработки')

            def _run(self, args):
                runned_with_args.append(args.text)

        # Зададим параметр через метод, сплиттер должен работать и в этом случае
        task = ParametrizedTask('test') \
            .split(SplitByChars(argument_name='text'))

        run_task(task, text='Hello')
        assert runned_with_args == ['H', 'e', 'l', 'l', 'o']

    @pytest.mark.parametrize(
        ['splitter_cls', 'num_parts', 'first_period_start', 'second_period_start'],
        [
            (SplitInDays, 20, '2020-03-01 00:00:00', '2020-03-02 00:00:00'),
            # Сплит по неделям бъет интервал именно по календарным неделям.
            # Поэтому тут получается 4 периода и первый состоит всего из одного дня,
            # ведь 1 марта это воскресенье.
            (SplitInWeeks, 4, '2020-03-01 00:00:00', '2020-03-02 00:00:00'),
        ],
    )
    def test_period_splitter(self, splitter_cls, num_parts, first_period_start, second_period_start):
        args = argparse.Namespace()
        args.text = 'foo'
        args.period = dtu.Period('2020-03-01', '2020-03-20')

        result = list(splitter_cls(argument_name='period')(args))
        assert len(result) == num_parts

        first_period_start = dtu.parse_datetime(first_period_start)
        second_period_start = dtu.parse_datetime(second_period_start)

        assert result[0].period.start == first_period_start
        assert result[1].period.start == second_period_start

    @pytest.mark.parametrize('splitter_cls, arg_name', zip(
        (SplitInDays, SplitInWeeks, SplitInMonths, SplitInYears),
        (None, 'period', 'custom'),
    ))
    def test_period_splitter_with_none(self, splitter_cls, arg_name):
        args = argparse.Namespace()
        args.text = 'foo'
        arg_name = arg_name or 'period'
        setattr(args, arg_name, None)
        result = list(splitter_cls(argument_name=arg_name)(args))
        assert len(result) == 1
        assert getattr(result[0], arg_name) is None

    @pytest.mark.parametrize('arg_name', [None, 'period', 'custom'])
    def test_period_splitter_arg_name(self, arg_name):
        args = argparse.Namespace()
        args.text = 'foo'
        arg_name = arg_name or 'period'
        setattr(args, arg_name, dtu.Period('2020-03-01', '2020-03-02'))
        result = list(SplitInDays(argument_name=arg_name)(args))
        assert len(result) == 2
        assert getattr(result[0], arg_name) == dtu.Period('2020-03-01 00:00:00', '2020-03-01 23:59:59.999999')
        assert getattr(result[1], arg_name) == dtu.Period('2020-03-02 00:00:00', '2020-03-02')

    @pytest.mark.parametrize('arg_name', [None, 'period', 'custom'])
    def test_equal_period_splitter(self, arg_name):
        args = argparse.Namespace()
        args.text = 'foo'
        arg_name = arg_name or 'period'
        setattr(args, arg_name, dtu.Period('2020-03-01', '2020-03-20'))

        # Разобъем период на кусочки по три дня.
        result = list(SplitInEqualPeriods(argument_name=arg_name, days=3)(args))
        assert len(result) == 7
        assert getattr(result[0], arg_name) == dtu.Period('2020-03-01 00:00:00', '2020-03-03 23:59:59.999999')
        assert getattr(result[1], arg_name) == dtu.Period('2020-03-04 00:00:00', '2020-03-06 23:59:59.999999')

    def test_equal_period_splitter_no_period(self):
        args = argparse.Namespace()
        args.text = 'foo'
        args.period = None

        result = list(SplitInEqualPeriods(argument_name='period', days=3)(args))
        assert len(result) == 1
        assert result[0].period is None

    def prepare_list_splitter_args(self, periods_list):
        args = argparse.Namespace()
        args.text = 'foo'
        args.period = periods_list

        return list(ListSplitter(argument_name='period')(args))

    def test_list_splitter_regular(self):
        periods_list = [
            dtu.Period('2020-03-01', '2020-03-20'),
            dtu.Period('2020-03-22', '2020-04-01'),
            dtu.Period('2020-01-01', '2020-01-15'),
        ]
        result = self.prepare_list_splitter_args(periods_list)
        assert len(result) == len(periods_list)

        for res, expect in zip(result, periods_list):
            assert res.period.start == expect.start
            assert res.period.end == expect.end

    def test_list_splitter_days(self):
        periods_list = [
            dtu.Period('2020-03-01', '2020-03-02'),
            dtu.Period('2020-03-02', '2020-03-03'),
            dtu.Period('2020-03-15', '2020-03-16'),
        ]

        result = self.prepare_list_splitter_args(periods_list)
        assert len(result) == len(periods_list)

        for res, expect in zip(result, periods_list):
            assert res.period.start == expect.start
            assert res.period.end == expect.end

    def test_list_splitter_months(self):
        periods_list = [
            dtu.Period('2020-03-01', '2020-03-31'),
            dtu.Period('2020-02-01', '2020-02-28'),
            dtu.Period('2020-05-01', '2020-05-31'),
        ]

        result = self.prepare_list_splitter_args(periods_list)
        assert len(result) == len(periods_list)

        for res, expect in zip(result, periods_list):
            assert res.period.start == expect.start
            assert res.period.end == expect.end

@patch_luigi_target
def test_run_task_as_graph_no_lock():
    task_results = {}

    def set_result(task_name):
        task_results[task_name] = True

    t1 = PyTask('t1', lambda args: set_result('t1'))
    t2 = PyTask('t2', lambda args: set_result('t2'))
    root = PyTask('root', lambda args: set_result('root')).requires(t1, t2)

    run_task(root, execution_mode=ExecutionMode.GRAPH)
    assert all(task_results[task.name] for task in [t1, t2, root])


# разрешаем сокет, run_task использует Pipe
@pytest.mark.enable_socket
@patch_luigi_target
def test_run_task_as_graph_locked():
    # таски выполняются в отдельных процессах,
    # файл дескриптор доступен в дочернем процессе
    with multiprocess_results() as results:
        t1 = PyTask('t1', lambda args: results.add('t1'))
        t2 = PyTask('t2', lambda args: results.add('t2'))
        root = PyTask('root', lambda args: results.add('root')).requires(t1, t2)

        exc_args = ExecutionArgs(
            accident_used=False,
            lock_used=True
        )

        patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')
        with patch_typed_lock:
            run_task(
                root,
                execution_mode=ExecutionMode.GRAPH,
                execution_args=exc_args,
            )

        task_results = set(results.get())
        assert all(task.name in task_results for task in [t1, t2, root])


@patch_luigi_target
@pytest.mark.parametrize('extra_args, expected', [
    (
            {},
            {'t1': 'AttributeError', 't2': 't2', 'root': 'root'}
    ),
    # Если параметр передать явно, то он должен измениться только для корневого
    # таска и не проброситься в остальные, иначе возможны проблемы:
    # https://st.yandex-team.ru/TAXIDWH-6655
    (
            {'foo': 'bar'},
            {'t1': 'AttributeError', 't2': 't2', 'root': 'bar'}
    )
])
def test_run_task_as_graph_does_not_pass_arguments_no_lock(monitoring_mock, extra_args, expected):
    # При выполнении графа, аргументы не должны передаваться по цепочке
    # от вершины к листьям. Если у какого-то из тасков задан аргумент
    # со значением по-умолчанию, то именно это значение по-умолчанию и будет
    # использоваться.

    # здесь будем регистрировать, с каким значением вызван таск
    task_results = {}

    def make_body(task_name):
        def body(args):
            try:
                task_results[task_name] = args.foo
            except AttributeError:
                task_results[task_name] = 'AttributeError'

        return body

    # для самого листа дерева,  мы не указываем никаких аргументов,
    # так что у него в результатах должно быть AtrributeError
    t1 = PyTask('t1', make_body('t1'))

    t2 = PyTask('t2', make_body('t2')) \
        .arguments(foo=CliArg('The argument', default='t2')) \
        .requires(t1)

    root = PyTask('root', make_body('root')) \
        .arguments(foo=CliArg('The argument', default='root')) \
        .requires(t2)

    patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')

    with patch_typed_lock as typed_lock_mock:
        run_task(root, execution_mode=ExecutionMode.GRAPH, **extra_args)
        assert typed_lock_mock.call_count == 0
        assert monitoring_mock().record_time.call_count == 4

    assert task_results == expected


@patch_luigi_target
@pytest.mark.enable_socket
@pytest.mark.parametrize('extra_args, expected', [
    (
            {},
            {'t1': 'AttributeError', 't2': 't2', 'root': 'root'},
    ),
    # Если параметр передать явно, то он должен измениться только для корневого
    # таска и не проброситься в остальные, иначе возможны проблемы:
    # https://st.yandex-team.ru/TAXIDWH-6655
    (
            {'foo': 'bar'},
            {'t1': 'AttributeError', 't2': 't2', 'root': 'bar'},
    ),
    (
            {},
            {'t1': 'AttributeError', 't2': 't2', 'root': 'root'},
    ),
])
def test_run_task_as_graph_does_not_pass_arguments_locked(monitoring_mock, extra_args, expected):
    # При выполнении графа, аргументы не должны передаваться по цепочке
    # от вершины к листьям. Если у какого-то из тасков задан аргумент
    # со значением по-умолчанию, то именно это значение по-умолчанию и будет
    # использоваться.

    # таски выполняются в отдельных процессах,
    # файл дескриптор доступен в дочернем процессе
    with multiprocess_results() as results:
        patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')

        with patch_typed_lock as typed_lock_mock:
            def make_body(task_name):
                def body(args):
                    # таски выполняются последовательно
                    # дозаписываем в конец файла
                    msg = getattr(args, 'foo', 'AttributeError')
                    results.add(f'{task_name}:{msg}\n')

                    lock_args, lock_kwargs = typed_lock_mock.call_args
                    typed_lock_mock(*lock_args, **lock_kwargs).__enter__.assert_called()

                    # проверяем запись таймингов выполнения
                    assert monitoring_mock().record_time.call_args == mock.call(task_name)
                    monitoring_mock().record_time(task_name).__enter__.assert_called()

                return body

            # для самого листа дерева,  мы не указываем никаких аргументов,
            # так что у него в результатах должно быть AtrributeError
            t1 = PyTask('t1', make_body('t1'))

            t2 = PyTask('t2', make_body('t2')) \
                .arguments(foo=CliArg('The argument', default='t2')) \
                .requires(t1)

            root = PyTask('root', make_body('root')) \
                .arguments(foo=CliArg('The argument', default='root')) \
                .requires(t2)

            exc_args = ExecutionArgs(
                accident_used=False,
                lock_used=True
            )

            run_task(
                root,
                execution_mode=ExecutionMode.GRAPH,
                execution_args=exc_args,
                **extra_args,
            )

            assert typed_lock_mock.call_count == 4
            assert monitoring_mock().record_time.call_count == 4

        task_results = {}
        for l in results.get():
            k, v = l.split(':')
            task_results[k] = v

        assert task_results == expected


def test_pytask():
    result = False

    def f():
        nonlocal result
        result = True

    task = PyTask('test', f)
    run_task(task)
    assert result

    result = False

    def f(args):
        nonlocal result
        result = True

    task = PyTask('test', f)
    run_task(task)
    assert result

    def f(args, more):
        pass

    with pytest.raises(ValueError):
        PyTask('test', f)


@patch_luigi_target
def test_run_task_raises_exception_if_graph_cant_be_executed_non_locked(
        monitoring_mock, accident_mock
):
    def do_raise(args):
        raise RuntimeError('BLAH')

    def do_nothing(args):
        pass

    dependency = PyTask('t1', do_raise)
    root = PyTask('root', do_nothing).requires(dependency)

    exc_args = ExecutionArgs(accident_used=True, lock_used=False)

    patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')
    with patch_typed_lock as typed_lock_mock:
        with pytest.raises(GraphExecutionFailed):
            run_task(root,
                     execution_mode=ExecutionMode.GRAPH,
                     execution_args=exc_args)

        assert typed_lock_mock.call_count == 0
        assert accident_mock.call_count == 2
        assert monitoring_mock().record_time.call_count == 2


@patch_luigi_target
@pytest.mark.enable_socket
def test_run_task_raises_exception_if_graph_cant_be_executed_locked(
        monitoring_mock, accident_mock,
):
    def do_raise(args):
        raise RuntimeError('BLAH')

    def do_nothing(args):
        pass

    dependency = PyTask('t1', do_raise)
    root = PyTask('root', do_nothing).requires(dependency)

    exc_args = ExecutionArgs(
        accident_used=True,
        lock_used=True
    )

    patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')
    with patch_typed_lock as typed_lock_mock:
        with pytest.raises(GraphExecutionFailed):
            run_task(root,
                     execution_mode=ExecutionMode.GRAPH,
                     execution_args=exc_args)

        assert typed_lock_mock.call_count == 2
        assert accident_mock.call_count == 2
        assert monitoring_mock().record_time.call_count == 2


class TestRetry:
    # используем кастомное исключение, которые может быть брошено только тестом,
    # чтобы случайно не заскипать реальное исключение
    class TestException(Exception):
        pass

    class SplitByChars(Splitter):
        def split(self, value: Text):
            return list(value)

    def retry_cli_args(self, retry_times: int):
        return ['--retry-times', str(retry_times), '--retry-sleep', '0']

    def create_task(self,
                    splitted: bool,
                    raised_args: str = None,
                    default_arg_text: str = None):
        # через raised_args контролируем бросание исключения в таске
        raised_args = list(raised_args or '') if splitted else [raised_args]
        raised_args = Counter(raised_args)

        runned_with_args_ = []

        class ParametrizedTask(SimpleTask):
            runned_with_args = runned_with_args_
            if splitted:
                text = TestRetry.SplitByChars(
                    CliArg('Текст для обработки', default=default_arg_text)
                )
            else:
                text = CliArg('Текст для обработки', default=default_arg_text)

            def _run(self, args):
                raise_count = raised_args.get(args.text)
                if raise_count:
                    raised_args[args.text] -= 1
                    raise TestRetry.TestException('test retry')
                runned_with_args_.append(args.text)

        return ParametrizedTask('test')

    def test_non_splitted(self):
        # фактически повторяет тесты из `TestSplitting`, но позволяет провериь
        # что self.create_task работает правильно
        task = self.create_task(splitted=False)
        run_task(task, text='Hello')
        assert task.runned_with_args == ['Hello']

    def test_splitted(self):
        task = self.create_task(splitted=True)
        run_task(task, text='Hello')
        assert task.runned_with_args == ['H', 'e', 'l', 'l', 'o']

    def test_no_retry_non_splitted(self, accident_mock):
        # ретрай не задан (по умолчанию), должно возникнуть исключение
        task = self.create_task(splitted=False, raised_args='Hello')
        exc_args = ExecutionArgs(accident_used=True, lock_used=False)

        with mock.patch('dmp_suite.task.monitoring.short_link', return_value=''), \
                pytest.raises(TestRetry.TestException):
            run_task(task, execution_args=exc_args, text='Hello')
        assert accident_mock.call_count == 1

    def test_retry_non_splitted(self, accident_mock):
        # в случае успешного ретрая, accident не создаются
        task = self.create_task(splitted=False, raised_args='Hello')
        exc_args = ExecutionArgs(accident_used=True, lock_used=False)

        run_task(task, raw_args=self.retry_cli_args(2), text='Hello')
        assert accident_mock.call_count == 0
        assert task.runned_with_args == ['Hello']

    def test_no_retry_splitted(self):
        # ретрай не задан (по умолчанию), должно возникнуть исключение
        task = self.create_task(splitted=True, raised_args='Hello')

        with pytest.raises(TestRetry.TestException):
            run_task(task, text='Hello')

    @pytest.mark.parametrize('raised_args', [
        'H', 'o', 'el', 'He', 'lo', 'Hello'
    ])
    def test_retry_limit_exceed_splitted(self, raised_args):

        retry_limit = len(raised_args)
        task = self.create_task(splitted=True, raised_args=raised_args)

        with pytest.raises(TestRetry.TestException):
            run_task(task,
                     raw_args=self.retry_cli_args(retry_limit),
                     text='Hello')

    @pytest.mark.parametrize('raised_args', [
        'H', 'o', 'el', 'He', 'lo', 'Hello'
    ])
    def test_retry_splitted(self, raised_args):
        # в случае ретрая, сплит аргументы должны быть обработаны все
        # и в правильном порядке

        # кол-во ретраев должно быть больше на 1, чем кол-во ошибок
        retry_limit = len(raised_args) + 1
        task = self.create_task(splitted=True, raised_args=raised_args)
        run_task(task,
                 raw_args=self.retry_cli_args(retry_limit),
                 text='Hello')
        assert task.runned_with_args == ['H', 'e', 'l', 'l', 'o']

    @patch_luigi_target
    def test_retry_graph(self):
        dependency_task = self.create_task(
            splitted=True, raised_args='tt', default_arg_text='attempt'
        )

        task = self.create_task(
            splitted=True, raised_args='H'
        ).requires(
            dependency_task
        )

        run_task(
            task,
            raw_args=self.retry_cli_args(3),
            text='Hello',
            execution_mode=ExecutionMode.GRAPH
        )

        assert dependency_task.runned_with_args == ['a', 't', 't', 'e', 'm', 'p', 't']
        assert task.runned_with_args == ['H', 'e', 'l', 'l', 'o']

    @patch_luigi_target
    def test_retry_graph_limit_exceed_on_dependency(self):
        dependency_task = self.create_task(
            splitted=True, raised_args='ttt', default_arg_text='attempt'
        )

        root_task = self.create_task(
            splitted=True, raised_args='H'
        ).requires(
            dependency_task
        )

        # зависимый таск упадет 3 раза, а ретрая только 1
        with pytest.raises(Exception) as exc:
            run_task(
                root_task,
                raw_args=self.retry_cli_args(1),
                text='Hello',
                execution_mode=ExecutionMode.GRAPH
            )

        # зависимый таск смог обработать только первый символ
        assert dependency_task.runned_with_args == ['a']
        # рутовый таск не выполнялся так как упал зависимый
        assert not root_task.runned_with_args

    @patch_luigi_target
    def test_retry_graph_limit_exceed_on_root(self):
        dependency_task = self.create_task(
            splitted=True, raised_args='t', default_arg_text='attempt'
        )

        task = self.create_task(
            splitted=True, raised_args='ello'
        ).requires(
            dependency_task
        )

        # рутовый таск упадет 4 раза, а ретрая только 2
        with pytest.raises(Exception):
            run_task(
                task,
                raw_args=self.retry_cli_args(2),
                text='Hello',
                execution_mode=ExecutionMode.GRAPH
            )

        # зависимый таск отработает
        assert dependency_task.runned_with_args == ['a', 't', 't', 'e', 'm', 'p', 't']
        # рутовый таск смог обработать только первый символ
        assert not task.runned_with_args == ['H']


def test_task_args_with_multiple_workers():
    def noop(args):
        pass

    t1 = PyTask('t1', noop)
    t2 = PyTask('t2', noop)
    root = PyTask('root', noop)

    # Запомним общие параметры, чтобы не дублировать их при каждом вызове:
    process = partial(process_task_args, root, execution_mode=ExecutionMode.GRAPH)

    # по умолчанию, число воркеров в таске – 1
    args = process()
    assert args.workers == 1

    # У таска можно явно указать число воркеров:
    root = root.requires(t1, t2).max_workers(2)
    args = process()
    assert args.workers == 2

    # И число воркеров можно переопределить с командной строки:
    args = process(raw_args=['--workers', '5'])
    assert args.workers == 5

    # Или параметром, при вызове run_task:
    args = process(workers=7)
    assert args.workers == 7


class TestDisableTask:

    def test_disabled_task_does_not_run(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)
        ctl_mock.task.disable(task)
        run_task(task)
        assert not func_mock.called

    def test_disabled_task_runs_after_disability_expired(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)
        ctl_mock.task.disable(task, datetime(1, 9, 3))
        run_task(task)
        func_mock.assert_called()

    def test_disabled_task_runs_with_no_check(self, ctl_mock):
        # Проверяем, что отключенные таски запускаются
        # если выставлена опция run_disabled=True
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)
        ctl_mock.task.disable(task)
        exc_args = ExecutionArgs(
            accident_used=False,
            lock_used=False,
            run_disabled=True,
        )
        run_task(task, execution_args=exc_args)
        func_mock.assert_called()

    @patch_luigi_target
    def test_disabled_graph_task_does_not_run(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        dependency_task = PyTask('dependency_task', func)
        task = PyTask('task', func).requires(dependency_task)
        ctl_mock.task.disable(task)

        run_task(task, execution_mode=ExecutionMode.GRAPH)
        assert not func_mock.called

    @patch_luigi_target
    def test_disabled_graph_task_runs_with_no_check(self, ctl_mock):
        # Проверяем, что отключенные таски запускаются
        # если выставлена опция run_disabled=True
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        dependency_task = PyTask('dependency_task', func)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.disable(task)

        exc_args = ExecutionArgs(
            accident_used=False,
            lock_used=False,
            run_disabled=True,
        )
        run_task(task, execution_args=exc_args, execution_mode=ExecutionMode.GRAPH)

        func_mock.assert_called()

    @patch_luigi_target
    def test_graph_task_with_disabled_deps_raises(self, ctl_mock):
        # Проверяем, что если запускается граф, в котором одна из зависимостей
        # помечена как disabled, то граф не запустится и будет ошибка.
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        leaf_task = PyTask('req_dep_task', func)
        dependency_task = PyTask('dep_task', func).requires(leaf_task)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.disable(leaf_task)

        with pytest.raises(TaskDependencyDisabledError) as exc:
            run_task(task, execution_mode=ExecutionMode.GRAPH)

        assert 'req_dep_task' in exc.value.args[0]
        assert not func_mock.called

    @patch_luigi_target
    def test_graph_task_can_be_skipped(self, ctl_mock):
        # Проверяем, что если запускается граф, в котором одна из зависимостей
        # помечена как skip, то граф запустится и все ноды кроме одной будут вычеслены.
        leaf_run = mock.MagicMock()
        dependency_run = mock.MagicMock()
        root_run = mock.MagicMock()

        leaf_task = PyTask('leaf_task', leaf_run)
        dependency_task = PyTask('dep_task', dependency_run) \
            .requires(leaf_task)
        root_task = PyTask('root_task', root_run) \
            .requires(dependency_task)

        ctl_mock.task.skip(dependency_task)

        run_task(root_task, execution_mode=ExecutionMode.GRAPH)

        assert leaf_run.called
        assert not dependency_run.called
        assert root_run.called

    @patch_luigi_target
    def test_skip_on_task_could_be_reset(self, ctl_mock):
        # Проверяем, что CTL параметр skip можно сбросить методом reset_skip.
        leaf_run = mock.MagicMock()
        dependency_run = mock.MagicMock()
        root_run = mock.MagicMock()

        leaf_task = PyTask('leaf_task', leaf_run)
        dependency_task = PyTask('dep_task', dependency_run) \
            .requires(leaf_task)
        root_task = PyTask('root_task', root_run) \
            .requires(dependency_task)

        ctl_mock.task.skip(dependency_task)
        ctl_mock.task.reset_skip(dependency_task)

        run_task(root_task, execution_mode=ExecutionMode.GRAPH)

        assert leaf_run.called
        assert dependency_run.called
        assert root_run.called

    @patch_luigi_target
    def test_dont_skip_with_run_disabled_option(self, ctl_mock):
        # Проверяем, что CTL параметр skip будет проигнорирован,
        # если при запуске таска использована опция --run_disabled
        leaf_run = mock.MagicMock()
        dependency_run = mock.MagicMock()
        root_run = mock.MagicMock()

        leaf_task = PyTask('leaf_task', leaf_run)
        dependency_task = PyTask('dep_task', dependency_run) \
            .requires(leaf_task)
        root_task = PyTask('root_task', root_run) \
            .requires(dependency_task)

        ctl_mock.task.skip(dependency_task)

        exc_args = ExecutionArgs(
            lock_used=False,
            accident_used=False,
            # Нам важна только эта опция.
            # lock_used задан, чтобы
            # запускалка не запускала его в
            # отдельном процессе:
            run_disabled=True,
        )

        run_task(
            root_task,
            execution_mode=ExecutionMode.GRAPH,
            execution_args=exc_args,
        )

        assert leaf_run.called
        assert dependency_run.called
        assert root_run.called

    @patch_luigi_target
    def test_skipped_task_runned_not_in_graph_mode_raises(self, ctl_mock):
        """Использование "skip" параметра с таском, который может запускаться
           сам по себе, а не в составе графа, должно считаться ошибкой.
           Это нужно чтобы защититься от ситуации, когда у таска есть своё расписание,
           но его выполнение заскипали и из-за этого у нас перестали считаться данные.
        """
        func_mock = mock.MagicMock()
        task = PyTask('task', func_mock)

        ctl_mock.task.skip(task)

        with pytest.raises(TaskSkippedError) as exc:
            run_task(task, execution_mode=ExecutionMode.STANDALONE_TASK)

        assert 'task' in exc.value.args[0]
        assert not func_mock.called

    @patch_luigi_target
    def test_graph_task_with_disabled_deps_and_no_check_raises(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        recursive_dependency_task = PyTask('req_dep_task', func)
        dependency_task = PyTask('dependency_task', func).requires(recursive_dependency_task)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.disable(recursive_dependency_task)

        with pytest.raises(TaskDependencyDisabledError) as exc:
            run_task(task, execution_mode=ExecutionMode.GRAPH)

        assert 'req_dep_task' in exc.value.args[0]
        assert not func_mock.called

    @patch_luigi_target
    def test_disabled_graph_task_with_disabled_deps_does_not_raise(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        recursive_dependency_task = PyTask('req_dep_task', func)
        dependency_task = PyTask('dependency_task', func).requires(recursive_dependency_task)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.disable(recursive_dependency_task)
        ctl_mock.task.disable(task)

        run_task(task, execution_mode=ExecutionMode.GRAPH)
        assert not func_mock.called

    @patch_luigi_target
    def test_disabled_graph_task_with_disabled_deps(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        recursive_dependency_task = PyTask('req_dep_task', func)
        dependency_task = PyTask('dependency_task', func).requires(recursive_dependency_task)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.disable(recursive_dependency_task)

        exc_args = ExecutionArgs(
            accident_used=False,
            lock_used=False,
            run_disabled=True,
        )

        run_task(
            task,
            execution_args=exc_args,
            execution_mode=ExecutionMode.GRAPH,
        )

        assert func_mock.called


class TestNotEnabledTask:

    @pytest.mark.parametrize(
        'is_enabled_until_set', [True, False]
    )
    def test_not_enabled_task_does_not_run(self, ctl_mock, is_enabled_until_set):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)

        if is_enabled_until_set:
            ctl_mock.task.set_param(
                task,
                CTL_ENABLED_UNTIL_DTTM,
                datetime(1000, 9, 3)
            )
        run_task(task, check_enabled=True)
        assert not func_mock.called

    def test_enabled_task_runs_with_check(self, ctl_mock, ):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)
        ctl_mock.task.set_param(
            task,
            CTL_ENABLED_UNTIL_DTTM,
            datetime(9999, 9, 3)
        )
        run_task(task, check_enabled=True)
        func_mock.assert_called()

    @pytest.mark.parametrize(
        'is_enabled_until_set', [True, False]
    )
    def test_enability_expired_but_task_runs_without_check(
            self,
            ctl_mock,
            is_enabled_until_set
    ):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        task = PyTask('task', func)
        if is_enabled_until_set:
            ctl_mock.task.set_param(
                task,
                CTL_ENABLED_UNTIL_DTTM,
                datetime(1000, 9, 3)
            )
        run_task(task)
        func_mock.assert_called()

    @patch_luigi_target
    def test_not_enabled_graph_task_does_not_run(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        dependency_task = PyTask('dependency_task', func)
        task = PyTask('task', func).requires(dependency_task)
        ctl_mock.task.set_param(task, CTL_ENABLED_UNTIL_DTTM, datetime(1000, 9, 3))

        run_task(task, execution_mode=ExecutionMode.GRAPH, check_enabled=True)
        assert not func_mock.called

    @patch_luigi_target
    def test_graph_task_runs_with_not_enabled_required_task(self, ctl_mock):
        func_mock = mock.MagicMock()

        def func(args):
            func_mock(args)

        dependency_task = PyTask('dependency_task', func)
        task = PyTask('task', func).requires(dependency_task)

        ctl_mock.task.set_param(dependency_task, CTL_ENABLED_UNTIL_DTTM, datetime(1000, 9, 3))
        ctl_mock.task.set_param(task, CTL_ENABLED_UNTIL_DTTM, datetime(9999, 9, 3))

        run_task(task, execution_mode=ExecutionMode.GRAPH, check_enabled=True)

        func_mock.assert_called()


def test_setting_critical():
    not_critical_task = SimpleTask('first')
    critical_task = SimpleTask('second').critical()

    assert not_critical_task.is_critical() == False
    assert critical_task.is_critical() == True


def test_ensure_responsible():
    from dmp_suite.staff import User, Department, Service, ServiceWithScope, ensure_staff_entity

    assert ensure_staff_entity('art') == User('art')
    assert ensure_staff_entity('group:some-staff-group') == Department('some-staff-group')
    assert ensure_staff_entity('service:some-abc-service') == Service('some-abc-service')
    assert ensure_staff_entity('service:some-abc-service@develop') == ServiceWithScope('some-abc-service', 'develop')

    with pytest.raises(ValueError):
        # префикс staff - неправильный. Должно быть group:
        ensure_staff_entity('staff:some-staff-group')

    # Объекты должны пробрасываться как есть:
    user = User('art')
    assert ensure_staff_entity(user) is user

    # Но объекты неправильного типа должны приводить к ошибке
    with pytest.raises(ValueError):
        ensure_staff_entity(100500)


def test_responsible():
    from dmp_suite.staff import User

    # Проверим, что таскам можно задать разных ответственных
    first = SimpleTask('first')
    second = SimpleTask('second').responsible(
        'art', 'igsaf'
    )
    assert first.who_is_responsible() == []
    assert second.who_is_responsible() == [User('art'), User('igsaf')]


def test_get_graph_locks():
    # Проверим, что метод get_graph_locks отдаёт
    # имена локов для всех связанных тасков и
    # при этом они отсортированы по алфовиту.
    # Сортировка важна, поскольку позволит избежать dead-locks
    # при запуске графов, которые включают в себя одни и те же таски.
    def func(args):
        pass

    dependency_1 = PyTask('a_dependency_1', func)
    dependency_2 = PyTask('b_dependency_2', func)
    task = PyTask('c_task', func).requires(dependency_1, dependency_2)

    expected_result = ('a_dependency_1', 'b_dependency_2', 'c_task')
    assert task._get_graph_locks() == expected_result

    # Теперь изменим порядок зависимостей
    task = PyTask('c_task', func).requires(dependency_2, dependency_1)

    # Результат должен остаться тот же:
    assert task._get_graph_locks() == expected_result


@patch_luigi_target
@pytest.mark.slow
# Этот тест стартует графы из тредов, и не работает в параллельном режиме,
# когда сам тест запускается из подпроцесса. Я, art@ потратил несколько дней,
# чтобы в этом разобраться и пришёл к тому, что лучше всего не запускать
# этот тест из подпроцесса. Иначе возникают странные ошибки о том, что
# наши settings не проинициализированы.
@pytest.mark.no_parallel
# Тест почему-то всё равно не хочет работать на TeamCity,
# когда запускается вместе со всеми остальными.
# Непонятно что за ерунда происходит с конфигами и почему
# они становятся недоступныы внутри тасков запускаемых
# в подпроцессах. Сил больше нет это дебажить.
# За сим, оставляю этот тест для ручного запуска.
#                                            art@
@pytest.mark.manual
def test_error_when_graph_has_two_schedules():
    # Здесь мы моделируем ситуацию, когда есть цепочка тасков
    # и разные её части запускаются и бегут параллельно, каждая
    # по своему расписанию. В этом случае, один из запусков
    # должен ждать и завершаться с сообщением Luigi.

    # Локальный шедулер не выполняет дедупликации, так как в каждом подпроцессе
    # он будет свой и каждый граф выполнится полностью.
    #
    # Поэтому для правильной работы этого теста нужно установить local_scheduler в False,
    # запустить шедулер:
    #
    #     PYTHONPATH=scheduler:$PYTHONPATH python -m scheduler
    #
    # а потом и тест.
    assert settings('luigi.local_scheduler') == False, 'Этот тест должен запускаться с отдельным шедулером, иначе результаты будут неверны.'

    with multiprocess_results() as results:
        def do_1():
            results.add('do1')
            time.sleep(10)

        def do_2():
            results.add('do2')

        def do_3():
            results.add('do3')

        first = PyTask('first_task', do_1)
        second = PyTask('second_task', do_2).requires(first) \
            .set_scheduler(
            Cron('10 * * * *')
        )
        third = PyTask('third_task', do_3).requires(second) \
            .set_scheduler(
            Cron('11 * * * *')
        )

        def run_graph_in_thread(task):
            def runner():
                exc_args = ExecutionArgs(
                    accident_used=False,
                    lock_used=True
                )

                run_task(
                    task,
                    execution_mode=ExecutionMode.GRAPH,
                    execution_args=exc_args,
                )

            thread = threading.Thread(target=runner)
            thread.start()
            return thread

        first_thread = run_graph_in_thread(second)
        time.sleep(5)
        second_thread = run_graph_in_thread(third)

        first_thread.join()
        second_thread.join()

        # Второй запуск не должен приводить к дополнительным вызовам do1 и do2,
        # так как сработает дедупликация
        assert results.get() == ['do1', 'do2', 'do3']


class TestBackFillTask:
    common_period = dtu.Period('2020-03-01', '2020-03-02')
    common_splitter = SplitInDays()
    common_args = dict(flag=Flag(default=True), period=cli.Period(common_period))
    bf_cli_period = cli.Period(default=None)
    bf_split = SplitInYears()

    def _get_common_task(self, name):
        return create_task(name).arguments(**self.common_args).split(self.common_splitter)

    def test_base_case(self):
        # Проверим, что возвращается копия базового класса
        task_name = 'bf_base_case'
        base_task = self._get_common_task(task_name)
        backfill_task = base_task.get_backfill_task()
        assert type(base_task) == type(backfill_task)
        assert backfill_task is not base_task
        assert base_task.get_arguments() == backfill_task.get_arguments()
        assert base_task.splitter == backfill_task.splitter
        run_task(base_task)
        assert len(backfill_task._run_logger[task_name])
        assert backfill_task.get_arguments()['pool'].default == Pool.TAXI_DWH_BACKFILL

    def test_replace_params(self):
        task_name = 'bf_replace_params'

        base_task = self._get_common_task(
            task_name
        ).backfill_split(
            self.bf_split
        ).backfill_arguments(
            period=self.bf_cli_period
        )

        backfill_task = base_task.get_backfill_task()
        bf_args = backfill_task.get_arguments()
        # Проверим, что у исторического пересчета работает замена аргументов и сплита
        assert self.bf_cli_period == bf_args['period']
        assert self.bf_split == backfill_task.splitter
        assert backfill_task.get_arguments()['pool'].default == Pool.TAXI_DWH_BACKFILL

    def test_custom_task(self):
        run_log = []
        task_for_backfill = PyTask('task_for_backfill', lambda *args: run_log.append(args)).arguments(ct=Flag(False))

        task_name = 'bf_custom_task'

        base_task = self._get_common_task(
            task_name
        ).set_backfill_task(
            task_for_backfill
        ).backfill_split(
            self.bf_split
        ).backfill_arguments(
            period=self.bf_cli_period
        )

        backfill_task = base_task.get_backfill_task()
        # Проверим, что работает возвращается таск для backfill
        assert backfill_task is task_for_backfill

        bf_args = backfill_task.get_arguments()
        # Проверим, что переопределился параметр period
        assert self.bf_cli_period == bf_args['period']
        # Проверим, что переопределился сплиттер
        assert self.bf_split == backfill_task.splitter
        # Проверим, что сохранился исходный аргумент у task_for_backfill
        assert isinstance(bf_args['ct'], Flag)
        assert backfill_task.get_arguments()['pool'].default == Pool.TAXI_DWH_BACKFILL

        run_task(base_task)

    def test_backfill_arguments_defaults(self):
        def f(): pass

        class TaskWithBackfillDefaults(PyTask):
            _backfill_arguments = dict(
                a=cli.CliArg('aaa'),
            )

        task = TaskWithBackfillDefaults('name', f)
        assert task.get_backfill_arguments()['a'] == cli.CliArg('aaa')

        task = TaskWithBackfillDefaults('name', f).backfill_arguments(
            b=cli.CliArg('bbb'),
        )
        assert task.get_backfill_arguments()['b'] == cli.CliArg('bbb')
        assert task.get_backfill_arguments()['a'] == cli.CliArg('aaa')

        task = TaskWithBackfillDefaults('name', f).backfill_arguments(
            a=cli.CliArg('a'),
        )
        assert task.get_backfill_arguments()['a'] == cli.CliArg('a')
        task = TaskWithBackfillDefaults('name', f).backfill_arguments(
            a=cli.CliArg('a'),
            b=cli.CliArg('bbb'),
        )
        assert task.get_backfill_arguments()['a'] == cli.CliArg('a')
        assert task.get_backfill_arguments()['b'] == cli.CliArg('bbb')

    def test_reverse_periods(self):
        task_name = 'bf_reverse_periods'

        base_task = self._get_common_task(
            task_name
        ).backfill_split(
            self.bf_split
        ).backfill_arguments(
            period=self.bf_cli_period
        )

        backfill_task = base_task.get_backfill_task()
        period = dtu.period('2020-01-01', '2022-01-02')
        args = argparse.Namespace(period=period)
        expected = [
            argparse.Namespace(
                period=dtu.Period('2022-01-01 00:00:00', '2022-01-02 00:00:00')),
            argparse.Namespace(
                period=dtu.Period('2021-01-01 00:00:00', '2021-12-31 23:59:59.999999')),
            argparse.Namespace(
                period=dtu.Period('2020-01-01 00:00:00', '2020-12-31 23:59:59.999999'))
        ]
        assert list(backfill_task.split_args(args, reverse=True)) == expected

    def test_reverse_run(self):
        run_log = []
        task_for_backfill = PyTask(
            'task_for_backfill_reverse_run',
            lambda args_: run_log.append(args_.period.start)
        ).arguments(period=cli.Period(self.common_period))

        task_name = 'bf_reverse_run_task'

        base_task = self._get_common_task(
            task_name
        ).set_backfill_task(
            task_for_backfill
        ).backfill_split(
            self.bf_split
        ).backfill_arguments(
            period=self.bf_cli_period
        )

        args = argparse.Namespace(
           period=dtu.period('2020-01-01', '2022-01-02'),
        )

        run_task(base_task, args, execution_args=ExecutionArgs(reverse=True, as_backfill=True, lock_used=False))

        assert run_log == [
            datetime(2022, 1, 1, 0, 0),
            datetime(2021, 1, 1, 0, 0),
            datetime(2020, 1, 1, 0, 0)
        ]


def test_task_with_with_processing():
    registrator = mock.MagicMock()

    class ArbitraryTask(AbstractTask):
        stage_start = cli.CliArg('start call', default='s1')
        stage_work = cli.CliArg('work call', default='s2')
        stage_finish = cli.CliArg('finish call', default='s3')

        def __init__(self, name, func):
            super().__init__(name)
            self.func = func

        def _run(self, args: argparse.Namespace) -> None:
            self.func(args)

    def processing(args: argparse.Namespace):
        registrator(args.stage_start)
        yield
        registrator(args.stage_finish)

    def work(args: argparse.Namespace):
        registrator(args.stage_work)

    task = ArbitraryTask('test', work).with_processing(processing)
    run_task(task, raw_args=[
        '--stage_start', 'processing-start',
        '--stage_work', 'task-work',
        '--stage_finish', 'processing-finish',
    ])

    registrator.assert_has_calls([
        mock.call('processing-start'),
        mock.call('task-work'),
        mock.call('processing-finish'),
    ])


class TestTaskExternalSources:

    class DummyExternalSource:
        """ Макетный источник для выполнения тестов """
        pass

    class DummyNestedSource:
        """ Макетный источник для выполнения тестов с вложенными в нем источниками """
        def __init__(self, sources: List):
            self.sources = sources

        def get_sources(self) -> List:
            return self.sources.copy()

    class DummyTable(Table):
        """ Макетная таблица для выполнения тестов """
        pass

    def test_one_external(self):
        """ Проверить, что таски выдают свой заданный источник """
        sources = [self.DummyExternalSource()]
        task = SimpleTask("task", sources=sources)

        assert task.get_sources() == sources, "Task didn't return external source in `get_sources()`"

    def test_table_and_external(self):
        """ Проверить, что таски выдают несколько разных источников: таблицу и некоторый внешний источник """
        sources = [self.DummyExternalSource(), self.DummyTable]
        task = SimpleTask("task", sources=sources)

        assert set(task.get_sources()) == set(sources), "Task didn't return external source and table in `get_sources()`"

    def test_nested_sources(self):
        """ Проверить, что таски выдают вложенные источники """
        inner_sources = [self.DummyExternalSource(), self.DummyExternalSource()]
        nested_source = self.DummyNestedSource(inner_sources)
        task = SimpleTask("task", sources=[nested_source])

        assert set(task.get_sources()) == set(inner_sources), "Task didn't return nested sources in `get_sources()`"

    def test_doubly_nested_sources(self):
        """ Проверить, что таски выдают источники, вложенные на два уровня """
        inner_source = self.DummyExternalSource()
        nested_source = self.DummyNestedSource([inner_source])
        doubly_nested_source = self.DummyNestedSource([nested_source])
        task = SimpleTask("task", sources=[doubly_nested_source])

        assert task.get_sources() == [inner_source], "Task didn't return doubly nested source in `get_sources()`"

    def test_mixed_sources(self):
        """ Проверить, что таски выдают вложенные и невложенные источники """
        class DummyTable2(Table):
            pass

        inner_sources = [self.DummyExternalSource(), DummyTable2, self.DummyExternalSource()]
        nested = self.DummyNestedSource(inner_sources)
        sources = [self.DummyExternalSource(), self.DummyTable]

        task = SimpleTask("task", sources=sources + [nested])

        assert set(task.get_sources()) == set(inner_sources + sources), \
            "Task didn't return nested mixed sources (ExternalSources + Tables + Nested) in `get_sources()`"

    def test_recursive_sources(self):
        """ Проверить, что выдаются рекурсивные источники, и не зацикливаются """
        class RecursiveSource:
            def get_sources(self):
                return [self]

        sources = [RecursiveSource()]
        task = SimpleTask("task", sources=sources)

        assert set(task.get_sources()) == set(sources), "Task didn't return a recursive source in `get_sources()`"

    def test_cross_recursive_sources(self):
        """ Проверить, что выдаются источники, ссылающиеся друг на друга """
        source1 = self.DummyNestedSource([])
        source2 = self.DummyNestedSource([source1])
        source1.sources = [source2]

        sources = [source1, source2]
        task = SimpleTask("task", sources=sources)
        assert set(task.get_sources()) == set(sources), "Task didn't return cross recursive sources in `get_sources()`"

    def test_shared_source(self):
        """ Проверить, что общий источник выдается в одном экземпляре """
        shared = self.DummyTable
        sources = [self.DummyNestedSource([shared]), self.DummyNestedSource([shared])]
        task = SimpleTask("task", sources=sources)
        assert task.get_sources() == [shared], "Task didn't return shared source in `get_sources()`"


def test_error_on_table_as_target():
    class DummyTable(Table):
        pass

    with pytest.raises(InvalidTargetTypeError):
        task = SimpleTask('first', targets=[DummyTable])

    class DummyTaskTarget(AbstractTableTaskTarget):
        def __init__(self, table):
            self.table = table

    task = SimpleTask('first', targets=[DummyTaskTarget(DummyTable)])


def test_with_args_raises_on_wrong_args():
    task = PyTask('test', lambda _: _)
    with pytest.raises(TaskRequirementError):
        task.requires(with_args(task, 'a'))
    with pytest.raises(TaskRequirementError):
        task.requires(with_args(task, a='b'))
    with pytest.raises(TaskRequirementError):
        task.requires(with_args(task, a=use_arg('b')))


def test_with_args():
    task = PyTask('test', lambda _: _).arguments(a=cli.CliArg('my arg'))
    task_req = with_args(task, 'a')
    assert task_req.get_args(argparse.Namespace(a=1)) == argparse.Namespace(a=1)
    assert task_req.get_args(argparse.Namespace(a=None, b=1)) == argparse.Namespace(a=None)
    task = task.arguments(b=cli.CliArg('my arg', default=22), c=cli.CliArg('my arg'))
    task_req = with_args(task, 'a', 'b', c='a')
    assert task_req.get_args(argparse.Namespace(a=1, b=2)) == argparse.Namespace(a=1, b=2, c=1)
    task_req = with_args(task, c='a')
    assert task_req.get_args(argparse.Namespace(a=1, b=2)) == argparse.Namespace(a=None, b=22, c=1)
    task_req = with_args(task, a=use_arg('a').transform(lambda x: x + 1))
    assert task_req.get_args(argparse.Namespace(a=1, b=2)) == argparse.Namespace(a=2, b=22, c=None)
    task_req = with_args(task, c=use_arg('a').transform(lambda x: x + 1))
    assert task_req.get_args(argparse.Namespace(a=1, b=2)) == argparse.Namespace(a=None, b=22, c=2)

    task_req = with_args(task, 'c')
    with pytest.raises(TaskRequirementError):
        task_req.get_args(argparse.Namespace(a=1))


def test_with_args_pass_retry_args():
    task = PyTask('test', lambda _: _).arguments(a=cli.CliArg('my arg'))
    task_req = with_args(task, 'a')
    expected = argparse.Namespace(
        a=1,
        retry_times=5,
        retry_sleep=100,
        retry_backoff_params=dict(base=2, power=3, limit=100),
    )
    actual = task_req.get_args(argparse.Namespace(
        a=1,
        retry_times=5,
        retry_sleep=100,
        retry_backoff_params=dict(base=2, power=3, limit=100),
    ))
    assert actual == expected


def test_requires():
    required_1 = PyTask('requried_1', lambda _: _)
    required_2 = PyTask('requried_2', lambda _: _)

    parent = PyTask('test', lambda _: _).requires(
        required_1,
        with_args(required_2),
    )

    assert parent.get_required_tasks() == [required_1, required_2]
    requirements = [with_args(required_1), with_args(required_2)]
    assert parent.get_task_requirements() == requirements
