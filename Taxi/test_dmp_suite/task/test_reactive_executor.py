import contextlib
import logging
import multiprocessing
import types
import typing as tp
from datetime import datetime

import mock
import pytest
from click.testing import CliRunner

import init_py_env
from connection.ctl import WrapCtl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.ctl import CTL_LAST_SEEN_STATE
from dmp_suite.ctl.storage import MPDictStorage
from dmp_suite.ext_source_proxy import ExternalSourceProxy
from dmp_suite.task import PyTask
from dmp_suite.task.base import AbstractTask
from dmp_suite.task.base import BoundPath, TaskBound
from dmp_suite.task.cli import CliArg
from dmp_suite.task.execution import run_task
from dmp_suite.task.reactive import trigger as tr
from dmp_suite.task.reactive.executor import ReactiveExecutorTask
from dmp_suite.task.splitters import Splitter
from test_dmp_suite.task.test_base import _patch_luigi_target_tmpdir

patch_luigi_target = pytest.mark.usefixtures(
    _patch_luigi_target_tmpdir.__name__
)

pytestmark = [pytest.mark.enable_socket]


logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def monitoring_mock():
    patch_one = mock.patch('dmp_suite.task.execution.get_task_monitoring')
    patch_two = mock.patch('dmp_suite.task.execution.report_task_result')
    patch_three = mock.patch('dmp_suite.task.execution._create_accident')

    with patch_one, patch_two, patch_three:
        yield


@pytest.fixture(autouse=True)
def executor_run_task():
    patch = mock.patch(
        'dmp_suite.task.reactive.executor._run_task',
        _reactor_executor_run_task_patch,
    )
    with patch:
        yield


@pytest.fixture
def mp_ctl():
    # multiprocessing лок нужен, потому что таска запускается в отдельном
    # процессе и меняет ctl (а на ctl завязана реактивность)
    with MPDictStorage() as ctl_storage:
        ctl = WrapCtl(ctl_storage)
        patch_one = mock.patch('connection.ctl.get_ctl', return_value=ctl)
        patch_two = mock.patch('dmp_suite.task.execution.get_ctl', return_value=ctl)
        with patch_one, patch_two:
            yield ctl


@pytest.fixture(autouse=True)
def typed_lock():
    with mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock'):
        yield


class MPCounter:
    """Counter synchronized between processes"""

    def __init__(self):
        self._counter = multiprocessing.Value('i', 0)
        self._lock = multiprocessing.Lock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            self._counter.value += 1

    @property
    def call_count(self):
        with self._lock:
            return self._counter.value


def _get_mock_for_mp_call_count():
    return mock.MagicMock(side_effect=MPCounter())


class DummyExtSourceProxy(ExternalSourceProxy):
    @property
    def ctl_entity(self):
        return 'dummy#dummy'

    def get_new_ctl_value(self):
        """Абстрактный метод, который не используется в тестах"""


def _reactor_executor_run_task_patch(
        task: AbstractTask,
        path: BoundPath,
        options: tp.List[tp.Text],
        env: tp.Dict[tp.Text, tp.Text],
):
    from dmp_suite.task.__main__ import main

    # Все тесты должны выполнятся в одном треде (see CliRunner.__doc__)
    args = [f'{path.module.__name__}.{task.name}'] + options
    result = CliRunner().invoke(main, args, env=env)
    if result.exit_code == 0:
        logger.info(result.output)
    else:
        logger.error(result.output)


@contextlib.contextmanager
def collect_resolve_tasks(*tasks: AbstractTask):

    fake_module = types.ModuleType('fake_module')

    for task in tasks:
        task.set_primary_module(fake_module)

    def _make_collect_result():
        return [
            TaskBound(
                task=task,
                bound_paths={BoundPath(module=fake_module, name=task.name)},
            )
            for task in tasks
        ]

    def resolve_callback(
            task_being_resolved: tp.Union[AbstractTask, tp.Text],
    ) -> AbstractTask:
        if isinstance(task_being_resolved, AbstractTask):
            task_being_resolved = f'fake_module.{task_being_resolved.name}'

        return {
            f'fake_module.{task.name}': task
            for task in tasks
        }[task_being_resolved]

    collect_patch = mock.patch(
        'dmp_suite.task.reactive.executor.collect_tasks',
        return_value=_make_collect_result(),
    )

    resolve_patch = mock.patch(
        'dmp_suite.task.execution.resolve_task_instance',
        resolve_callback,
    )

    with collect_patch, resolve_patch:
        yield


def _get_ready_to_run_once_trigger(ctl):
    entity_proxy = DummyExtSourceProxy()

    ctl.source.set_param(
        entity_proxy.ctl_entity,
        CTL_LAST_LOAD_DATE,
        '2015-04-01'  # какая-то дата без смысла, главное, чтобы была
    )

    return tr.new_day_arrived(entity_proxy)


def test_standalone_task_with_trigger_run(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    task = PyTask(
        'super_task',
        func=func_mock,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 1


@patch_luigi_target
def test_graph_with_trigger_run(mp_ctl):
    func_mock_tail = _get_mock_for_mp_call_count()
    func_mock_head = _get_mock_for_mp_call_count()

    task_tail = PyTask(
        'tail_task',
        func_mock_tail,
    )

    task_head = PyTask(
        'head_task',
        func_mock_head,
    ).requires(
        task_tail,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task_head, task_tail):
        run_task(executor)

    assert func_mock_tail.side_effect.call_count == 1
    assert func_mock_head.side_effect.call_count == 1


def test_standalone_task_with_trigger_run_exactly_once(mp_ctl):

    func_mock = _get_mock_for_mp_call_count()

    task = PyTask(
        'super_task',
        func=func_mock,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task):
        run_task(executor)
        run_task(executor)

    assert func_mock.side_effect.call_count == 1


@patch_luigi_target
def test_graph_with_trigger_run_exactly_once(mp_ctl):
    func_mock_tail = _get_mock_for_mp_call_count()
    func_mock_head = _get_mock_for_mp_call_count()

    task_tail = PyTask(
        'tail_task',
        func_mock_tail,
    )

    task_head = PyTask(
        'head_task',
        func_mock_head,
    ).requires(
        task_tail,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task_head, task_tail):
        run_task(executor)
        run_task(executor)

    assert func_mock_tail.side_effect.call_count == 1
    assert func_mock_head.side_effect.call_count == 1


def test_standalone_task_not_run(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    entity_proxy = DummyExtSourceProxy()

    task = PyTask(
        'super_task',
        func=func_mock,
    ).set_scheduler(
        tr.new_day_arrived(entity_proxy)
    )

    mp_ctl.source.set_param(
        entity_proxy.ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    mp_ctl.task.set_param(
        task,
        CTL_LAST_SEEN_STATE,
        {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 0


def test_graph_task_not_run(mp_ctl):
    func_mock_tail = _get_mock_for_mp_call_count()
    func_mock_head = _get_mock_for_mp_call_count()

    task_tail = PyTask(
        'tail_task',
        func_mock_tail,
    )

    task_head = PyTask(
        'head_task',
        func_mock_head,
    ).requires(
        task_tail,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    mp_ctl.task.set_param(
        task_head,
        CTL_LAST_SEEN_STATE,
        {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task_head, task_tail):
        run_task(executor)

    assert func_mock_tail.side_effect.call_count == 0
    assert func_mock_head.side_effect.call_count == 0


@patch_luigi_target
def test_graph_task_run_ignoring_required_task_ctl_state(mp_ctl):
    func_mock_tail = _get_mock_for_mp_call_count()
    func_mock_head = _get_mock_for_mp_call_count()

    task_tail = PyTask(
        'tail_task',
        func_mock_tail,
    )

    task_head = PyTask(
        'head_task',
        func_mock_head,
    ).requires(
        task_tail,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    mp_ctl.task.set_param(
        task_tail,
        CTL_LAST_SEEN_STATE,
        {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task_head, task_tail):
        run_task(executor)

    assert func_mock_tail.side_effect.call_count == 1
    assert func_mock_head.side_effect.call_count == 1


def test_standalone_task_updates_ctl_state_on_success(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    task = PyTask(
        'super_task',
        func=func_mock,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    executor = ReactiveExecutorTask('dummy')

    assert mp_ctl.task.get_param(task, CTL_LAST_SEEN_STATE) is None

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 1
    expected = {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
    assert mp_ctl.task.get_param(task, CTL_LAST_SEEN_STATE) == expected


class FakeSplitter(Splitter):
    def __init__(self, argument_name, values):
        super().__init__(argument_name=argument_name)
        self._values = values

    def split(self, value):
        return self._values


def test_standalone_task_dont_update_ctl_state_if_second_split_failed(mp_ctl):
    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    def fail_on_second(args):
        if args.argument == 2:
            raise RuntimeError('Failed')

    task = PyTask(
        'bad_task',
        func=fail_on_second,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    ).arguments(
        argument=CliArg('help'),
    ).split(
        FakeSplitter('argument', [1, 2])
    )

    executor = ReactiveExecutorTask('dummy')

    assert mp_ctl.task.get_param(task, CTL_LAST_SEEN_STATE) is None

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert mp_ctl.task.get_param(task, CTL_LAST_SEEN_STATE) is None


@patch_luigi_target
def test_only_head_graph_tasks_update_ctl_state_on_success(mp_ctl):
    func_mock_tail = _get_mock_for_mp_call_count()
    func_mock_head = _get_mock_for_mp_call_count()

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    task_tail = PyTask(
        'tail_task',
        func_mock_tail,
    )

    task_head = PyTask(
        'head_task',
        func_mock_head,
    ).requires(
        task_tail,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    executor = ReactiveExecutorTask('dummy')

    assert mp_ctl.task.get_param(task_head, CTL_LAST_SEEN_STATE) is None
    assert mp_ctl.task.get_param(task_tail, CTL_LAST_SEEN_STATE) is None

    with collect_resolve_tasks(executor, task_tail, task_head):
        run_task(executor)

    expected = {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
    assert mp_ctl.task.get_param(task_head, CTL_LAST_SEEN_STATE) == expected
    assert mp_ctl.task.get_param(task_tail, CTL_LAST_SEEN_STATE) is None

    assert func_mock_tail.side_effect.call_count == 1
    assert func_mock_head.side_effect.call_count == 1


def test_standalone_task_does_not_update_ctl_state_on_failure(mp_ctl):

    def load(args):
        raise RuntimeError

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    task = PyTask(
        'super_task',
        func=load,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert mp_ctl.task.get_param(task, CTL_LAST_SEEN_STATE) is None


@patch_luigi_target
def test_graph_task_does_not_update_ctl_state_on_failure(mp_ctl):
    def load_tail():
        raise RuntimeError

    task_tail = PyTask(
        'tail_task',
        load_tail,
    )

    task_head = PyTask(
        'head_task',
        lambda: None,
    ).requires(
        task_tail,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task_head, task_tail):
        run_task(executor)

    assert mp_ctl.task.get_param(task_head, CTL_LAST_SEEN_STATE) is None
    assert mp_ctl.task.get_param(task_tail, CTL_LAST_SEEN_STATE) is None


def test_executor_continues_to_run_on_task_failure(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    def success():
        func_mock()

    def failure():
        raise RuntimeError

    success_task = PyTask(
        'success_task',
        func=success,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    failure_task = PyTask(
        'failure_task',
        func=failure,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    executor = ReactiveExecutorTask('dummy')

    # назначение теста подразумевает, что failure_task будет до success_task
    with collect_resolve_tasks(executor, failure_task, success_task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 1


def test_new_trigger_makes_new_run(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    class DummyExtSourceProxyNew(DummyExtSourceProxy):
        @property
        def ctl_entity(self):
            return 'dummy#dummy_new'

    def load(args):
        func_mock()

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    task = PyTask(
        'super_task',
        func=load,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    task = PyTask(
        'super_task',
        func=load,
    ).set_scheduler(
        tr.any_trigger(
            tr.new_day_arrived(DummyExtSourceProxy()),
            tr.new_day_arrived(DummyExtSourceProxyNew()),
        )
    )

    mp_ctl.source.set_param(
        DummyExtSourceProxyNew().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 2


def test_new_trigger_does_not_make_new_run(mp_ctl):
    func_mock = _get_mock_for_mp_call_count()

    class DummyExtSourceProxyNew(DummyExtSourceProxy):
        @property
        def ctl_entity(self):
            return 'dummy#dummy_new'

    def load(args):
        func_mock()

    mp_ctl.source.set_param(
        DummyExtSourceProxy().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    task = PyTask(
        'super_task',
        func=load,
    ).set_scheduler(
        tr.new_day_arrived(DummyExtSourceProxy())
    )

    executor = ReactiveExecutorTask('dummy')

    with collect_resolve_tasks(task, executor):
        run_task(executor)

    task = PyTask(
        'super_task',
        func=load,
    ).set_scheduler(
        tr.all_triggers(
            tr.new_day_arrived(DummyExtSourceProxy()),
            tr.new_day_arrived(DummyExtSourceProxyNew()),
        )
    )

    mp_ctl.source.set_param(
        DummyExtSourceProxyNew().ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2020, 4, 1)
    )

    with collect_resolve_tasks(executor, task):
        run_task(executor)

    assert func_mock.side_effect.call_count == 1


def test_reactive_task_run_under_different_env_run_id(mp_ctl):
    from dmp_suite import py_env
    with multiprocessing.Manager() as manager:
        reactive_task_env = manager.dict({'run_id': None})
        env_executor_run_id = None

        def callback():
            reactive_task_env['run_id'] = py_env.get_taxidwh_run_id()

        task = PyTask(
            'super_task',
            func=callback,
        ).set_scheduler(
            _get_ready_to_run_once_trigger(mp_ctl)
        )

        def _save_executor_run_id(method):
            def inner(*args, **kwargs):
                nonlocal env_executor_run_id
                env_executor_run_id = py_env.get_taxidwh_run_id()
                method(*args, **kwargs)
            return inner

        executor = ReactiveExecutorTask('dummy')
        executor._run = _save_executor_run_id(executor._run)

        with collect_resolve_tasks(executor, task):
            run_task(executor)

        assert reactive_task_env['run_id']
        assert env_executor_run_id is not None
        assert env_executor_run_id != reactive_task_env['run_id']


def test_reactive_task_run_under_correct_task_name(mp_ctl):
    from dmp_suite import py_env
    with multiprocessing.Manager() as manager:
        reactive_task_env = manager.dict({'task': None})

        def callback():
            reactive_task_env['task'] = py_env.get_taxidwh_task()

        task = PyTask(
            'super_task',
            func=callback,
        ).set_scheduler(
            _get_ready_to_run_once_trigger(mp_ctl)
        )

        executor = ReactiveExecutorTask('dummy')

        with collect_resolve_tasks(executor, task):
            run_task(executor)

        assert reactive_task_env['task'] == 'super_task'


def test_putting_task_into_local_queue(mp_ctl):
    # Этот мок не должен вызваться, так как
    # мы только поставим задачу в очередь
    task_mock = _get_mock_for_mp_call_count()

    task = PyTask(
        'super_task',
        func=task_mock,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    with mock.patch('dmp_suite.task.reactive.executor.push_command_to_local_queue') as push_mock, \
        mock.patch('dmp_suite.task.reactive.executor.is_local_queue_running', return_value=True), \
        mock.patch('dmp_suite.task.reactive.executor.running_in_rtc', return_value=True), \
         init_py_env.settings.patch({'reactive': {'use_local_queue': True}}):

        executor = ReactiveExecutorTask('dummy')

        with collect_resolve_tasks(executor, task):
            run_task(executor)

        # Таск не должен был вызваться
        assert task_mock.side_effect.call_count == 0
        # Но мы должны были поставить его в очередь
        assert push_mock.call_count == 1
        assert push_mock.call_args == mock.call(
            ['task', '--reactive', 'fake_module.super_task'],
            priority=False,
            queue_timeout=900,
            ignore_local_queue_timeout=False,
        )


def test_dont_put_task_into_local_queue_when_it_is_not_available(mp_ctl):
    # Если по какой-то причине сокет local-queue недоступен, то таски должны запускаться,
    # как подпроцессы
    task_mock = _get_mock_for_mp_call_count()

    task = PyTask(
        'super_task',
        func=task_mock,
    ).set_scheduler(
        _get_ready_to_run_once_trigger(mp_ctl)
    )

    # Тут мы специально делаем чтобы is_local_queue_running возвращал False,
    # чтобы сэмулировать недоступность очереди.
    with mock.patch('dmp_suite.task.reactive.executor.push_command_to_local_queue') as push_mock, \
        mock.patch('dmp_suite.task.reactive.executor.is_local_queue_running', return_value=False), \
         init_py_env.settings.patch({'reactive': {'use_local_queue': True}}):

        executor = ReactiveExecutorTask('dummy')

        with collect_resolve_tasks(executor, task):
            run_task(executor)

        # Таск не должен был вызваться
        assert task_mock.side_effect.call_count == 1
        # И мы не должны были поставить его в очередь
        assert push_mock.call_count == 0


def test_standalone_task_not_run_on_clt_change(mp_ctl):
    # После проверки триггера таск помещается в local_queue.
    # В local_queue таск может быть довольно долго. Условие триггера
    # может быть неактуальным на момент реального запуска таска.
    # Нужно проверить, что триггер проверяется еще раз непосредственно
    # при выполнении таска.
    func_mock = _get_mock_for_mp_call_count()

    entity_proxy = DummyExtSourceProxy()

    task = PyTask(
        'super_task',
        func=func_mock,
    ).set_scheduler(
        tr.new_day_arrived(entity_proxy)
    )

    mp_ctl.source.set_param(
        entity_proxy.ctl_entity,
        CTL_LAST_LOAD_DATE,
        datetime(2015, 1, 1)
    )

    # на самом деле тут неоригинальная версия метода, а ранее пропатченный вариант
    # см фикстуру `executor_run_task`
    from dmp_suite.task.reactive.executor import _run_task as original_run_task

    # Изменяем ctl непосредственно перед запуском таска
    # и после проверки триггера в ReactiveExecutorTask.
    # После этого изменения ctl триггер уже оказывается неактивным
    # и таск не должен запуститься.
    def change_ctl(*args, **kwargs):
        mp_ctl.source.set_param(
            entity_proxy.ctl_entity,
            CTL_LAST_LOAD_DATE,
            datetime(2020, 4, 1)
        )

        mp_ctl.task.set_param(
            task,
            CTL_LAST_SEEN_STATE,
            {'last_load_date@dummy#dummy@source': datetime(2020, 4, 1)}
        )
        return original_run_task(*args, **kwargs)

    with mock.patch('dmp_suite.task.reactive.executor._run_task', change_ctl):
        executor = ReactiveExecutorTask('dummy')

        with collect_resolve_tasks(executor, task):
            run_task(executor)

    assert func_mock.side_effect.call_count == 0
    assert mp_ctl.source.get_param(entity_proxy.ctl_entity, CTL_LAST_LOAD_DATE) == datetime(2020, 4, 1)
