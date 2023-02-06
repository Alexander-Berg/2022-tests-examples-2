import pytest

from dmp_suite.task.__main__ import main
import mock
from click.testing import CliRunner

from dmp_suite.task.execution import ExecutionMode, ExecutionArgs

STANDALONE_TASK = ExecutionMode.STANDALONE_TASK
GRAPH = ExecutionMode.GRAPH
task = 'test'


def test_no_task():
    runner = CliRunner()

    patch_run_task = mock.patch('dmp_suite.task.__main__.run_task')
    with patch_run_task as run_task_mock:
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert 'Usage: main' in result.output
        assert run_task_mock.call_count == 0


@pytest.mark.parametrize('cli_args, mode, check_enabled, other_args, exec_args', [
    ([task], STANDALONE_TASK, False, (), ExecutionArgs(rewrite_targets=False)),
    ([task, '--check-enabled'], STANDALONE_TASK, True, (), ExecutionArgs(rewrite_targets=False)),
    ([task, '--rewrite-targets'], STANDALONE_TASK, False, (), ExecutionArgs(rewrite_targets=True)),
    ([task, '--as-graph'], GRAPH, False, (), ExecutionArgs(rewrite_targets=False)),
    (
        [task, '--no-accident', '--no-lock', '--some-flag', '--some-value', 'hello'],
        STANDALONE_TASK, False, ('--some-flag', '--some-value', 'hello'),
        ExecutionArgs(accident_used=False, lock_used=False, rewrite_targets=False)
    ),
    (
        [task, '--as-graph', '--no-accident', '--no-lock',
         '--some-flag', '--some-value', 'hello'],
        GRAPH, False, ('--some-flag', '--some-value', 'hello'),
        ExecutionArgs(accident_used=False, lock_used=False, rewrite_targets=False)
    ),
    (
        [task, '--lock-wait-sleep', '1', '--lock-wait-limit', '50'],
        STANDALONE_TASK, False, (), ExecutionArgs(lock_wait_limit=50, lock_wait_sleep=1, rewrite_targets=False)
    ),
    (
        [task, '--as-backfill', '--reverse'],
        STANDALONE_TASK, False, (), ExecutionArgs(as_backfill=True, reverse=True)
    ),
])
def test_args(cli_args, mode, check_enabled, other_args, exec_args):
    runner = CliRunner()
    patch_run_task = mock.patch('dmp_suite.task.__main__.run_task')

    with patch_run_task as run_task_mock:
        result = runner.invoke(main, cli_args)
        assert result.exit_code == 0
        run_task_mock.assert_called_once_with(
            task, other_args, mode, exec_args, check_enabled
        )


@pytest.mark.parametrize(
    'exec_params, has_exception',
    [
        ({'as_backfill': True}, False),
        ({'as_backfill': True, 'reverse': True}, False),
        ({'as_backfill': False, 'reverse': True}, True),
        ({'reverse': True}, True),
    ]
)
def test_execution_args_backfill_reverse(exec_params, has_exception):
    if has_exception:
        with pytest.raises(ValueError):
            ExecutionArgs(**exec_params)
    else:
        ExecutionArgs(**exec_params)


def test_raise_exception():
    runner = CliRunner()

    class TestException(Exception):
        pass

    def do_raise(*args, **kwargs):
        raise TestException()

    with mock.patch('dmp_suite.task.__main__.run_task', side_effect=do_raise):
        result = runner.invoke(main, [task])
        assert result.exit_code != 0
        assert result.exc_info[0] is TestException

