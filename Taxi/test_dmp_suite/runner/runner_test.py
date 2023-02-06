import argparse
import contextlib
import functools
import logging
from collections import defaultdict

import os
import shutil
import signal
import tempfile
import threading
import time
import sys
from typing import Dict, List, Iterable, Text

import pytest
import mock

import init_py_env
from dmp_suite.lock.base import BatchLock, LocalLock
from dmp_suite.maintenance.accident import ExecutionType
from dmp_suite.runner import (
    ScriptExecutor,
    ScriptExecutionError,
    ExecutionEvent, ErrorListener, RunnerError,
    DefaultErrorListener, ScriptCallResult, ShellScript, Script,
    PythonScript, _get_execution_args, TaskScript, parse_cli_args)
from dmp_suite.string_utils import to_unicode
from test_dmp_suite.testing_utils.assertions import regex


script_dir = os.path.join(
    os.path.dirname(__file__),
    'scripts'
)

patch_typed_lock = mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock')


@pytest.fixture(scope="module")
def temp_dir():
    tmp_path = None
    try:
        tmp_path = tempfile.mkdtemp(prefix='taxidwh_test')

        yield tmp_path
    finally:
        if tmp_path is not None:
            shutil.rmtree(tmp_path)


@pytest.fixture
def temp_pid(temp_dir):
    pidfile = None
    try:
        _, pidfile = tempfile.mkstemp(dir=temp_dir)
        os.environ['TAXIDWH_TEST_RUNNER_PID_PATH'] = pidfile
        yield pidfile
    finally:
        if pidfile is not None:
            del os.environ['TAXIDWH_TEST_RUNNER_PID_PATH']
            os.remove(pidfile)


class HelpStderrRecoder(object):
    def __init__(self):
        self.result = []

    def __call__(self, message, event_context):
        self.result.append((event_context.script.name, message))


TAXIDWH_RUN_ID = 'f02ba147'


def _create_local_lock(lock_dir):
    def local_lock_provider(*keys_, **kwargs):
        return BatchLock(
            functools.partial(LocalLock, lock_dir),
            *keys_
        )
    return local_lock_provider


class MockExecutor(object):
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self._executor = None
        self._out_tmpfile = None
        self.executed_scripts = None
        self.execution_success = None
        self.error_recoder = None
        self.execution_timeout = init_py_env.settings('system.execution.execution_timeout')
        self.lock_provider = None

    def __enter__(self):
        self.executed_scripts = []
        self.execution_success = None
        self._out_tmpfile = tempfile.NamedTemporaryFile(
            prefix="out", dir=self.temp_dir)
        self._out_tmpfile.__enter__()
        os.environ['TAXIDWH_TEST_RUNNER_OUT_PATH'] = self._out_tmpfile.name
        self.error_recoder = HelpStderrRecoder()
        self._executor = ScriptExecutor(
            execution_timeout=self.execution_timeout,
            run_id=TAXIDWH_RUN_ID
        )
        self._executor.add_callbacks(
            ExecutionEvent.AFTER_CALL,
            ErrorListener(self.error_recoder)
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executed_scripts = None
        self.execution_success = None
        self._executor = None
        del os.environ['TAXIDWH_TEST_RUNNER_OUT_PATH']
        self._out_tmpfile.__exit__(exc_type, exc_val, exc_tb)
        self._out_tmpfile = None

    def execute_all(self, scripts, lock_names=None):
        try:
            self._executor.execute_all(scripts, lock_names)
        except ScriptExecutionError:
            self.execution_success = False
        else:
            self.execution_success = True
        self.executed_scripts = [
            to_unicode(l.strip(b'\n'))
            for l in self._out_tmpfile.readlines()
        ]

    def execute_shell(self, scripts, lock_used):
        shell_scripts = [ShellScript(s, script_dir) for s in scripts]
        self.execute_all(
            scripts=shell_scripts,
            lock_names=(s.name for s in shell_scripts) if lock_used else None
        )

    def assert_executed_scripts(self, expected):
        assert self.executed_scripts == expected

    def assert_execution_status(self, expected):
        assert self.execution_success == expected

    def assert_stderr(self, expected):
        assert self.error_recoder.result == expected


ERROR_STRING = 'Script "error" (taxidwh_run_id={}) ' \
               'is finished with exit code 1'.format(TAXIDWH_RUN_ID)
ERROR_STDERR_STRING = 'Write to stderr and exit with fail\n'
SUCCESS_STDERR_STRING = 'Write to stderr and exit success\n'


def test_no_script(temp_dir):
    mock_executor = MockExecutor(temp_dir)
    with pytest.raises(RunnerError):
        with mock_executor:
            mock_executor.execute_all(scripts=None)

    with pytest.raises(RunnerError):
        with mock_executor:
            mock_executor.execute_all(scripts=None, lock_names=['success'])

    with pytest.raises(RunnerError):
        with mock_executor:
            mock_executor.execute_all(scripts=[])

    # empty generator/iterator
    with pytest.raises(RunnerError):
        with mock_executor:
            mock_executor.execute_all(scripts=iter([]))


def test_single_script(temp_dir):
    mock_executor = MockExecutor(temp_dir)
    with mock_executor, patch_typed_lock as lock_mock:
        script_name = 'success'
        mock_executor.execute_shell([script_name], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts([script_name])
        mock_executor.assert_stderr([])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        script_string = 'success arg1'
        mock_executor.execute_shell([script_string], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts(['success 1'])
        mock_executor.assert_stderr([])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        script_string = 'success arg1 "hello world"'
        mock_executor.execute_shell([script_string], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts(['success 2'])
        mock_executor.assert_stderr([])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        script_string = 'success arg1 hello world'
        mock_executor.execute_shell([script_string], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts(['success 3'])
        mock_executor.assert_stderr([])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        script_name = 'success_stderr'
        mock_executor.execute_shell([script_name], False)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts([script_name])
        mock_executor.assert_stderr([(
            script_name, SUCCESS_STDERR_STRING
        )])
        assert lock_mock.call_count == 0  # lock_used in mock == False

    with mock_executor, patch_typed_lock as lock_mock:
        script_name = 'error'
        mock_executor.execute_shell([script_name], False)
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts([script_name])
        mock_executor.assert_stderr([(script_name, ERROR_STRING)])
        assert lock_mock.call_count == 0  # lock_used in mock == False

    with mock_executor, patch_typed_lock as lock_mock:
        script_name = 'error_stderr'
        mock_executor.execute_shell([script_name], False)
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts([script_name])
        mock_executor.assert_stderr([(
            script_name, ERROR_STDERR_STRING
        )])
        assert lock_mock.call_count == 0  # lock_used in mock == False


def test_scripts_chain(temp_dir):
    mock_executor = MockExecutor(temp_dir)
    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_shell(['success', 'success'], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts(['success', 'success'])
        mock_executor.assert_stderr([])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_shell(['success', 'success_stderr'], True)
        mock_executor.assert_execution_status(True)
        mock_executor.assert_executed_scripts(['success', 'success_stderr'])
        mock_executor.assert_stderr([('success_stderr', SUCCESS_STDERR_STRING)])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_shell(['success', 'error_stderr'], True)
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts(['success', 'error_stderr'])
        mock_executor.assert_stderr([('error_stderr', ERROR_STDERR_STRING)])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_shell(['success_stderr', 'error_stderr', 'success'], True)
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts(['success_stderr', 'error_stderr'])
        mock_executor.assert_stderr([
            ('success_stderr', SUCCESS_STDERR_STRING),
            ('error_stderr', ERROR_STDERR_STRING)
        ])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_shell(['error_stderr', 'success'], True)
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts(['error_stderr'])
        mock_executor.assert_stderr([('error_stderr', ERROR_STDERR_STRING)])
        assert lock_mock.call_count == 1

    with mock_executor, patch_typed_lock as lock_mock:
        mock_executor.execute_all(
            scripts=[
                ShellScript('success', script_dir),
                ShellScript('error_stderr', script_dir)],
            lock_names=['success', None]
        )
        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts(['success', 'error_stderr'])
        mock_executor.assert_stderr([('error_stderr', ERROR_STDERR_STRING)])
        assert lock_mock.call_count == 1

    # not all locks are specified
    with pytest.raises(RunnerError):
        with mock_executor, patch_typed_lock:
            mock_executor.execute_all(
                scripts=['error_stderr', 'success'],
                lock_names=['success']
            )


def test_no_lock(temp_dir):
    with patch_typed_lock as fake_lock:
        mock_executor = MockExecutor(temp_dir)
        mock_executor.lock_provider = fake_lock
        lock_used = False
        with mock_executor:
            mock_executor.execute_shell(['success'], lock_used)
            assert fake_lock.called is False
            mock_executor.assert_execution_status(True)
            mock_executor.assert_executed_scripts(['success'])
            mock_executor.assert_stderr([])


class ScriptExecutorModified(ScriptExecutor):
    def __init__(self, *args, **kwargs):
        self.attempt = defaultdict(int)
        super(ScriptExecutorModified, self).__init__(*args, **kwargs)

    def _call_script(self, script):
        """fake execute with raise in the first call of script"""
        self.attempt[script.name] += 1
        if self.attempt[script.name] < 2:
            return ScriptCallResult(
                run_id=TAXIDWH_RUN_ID,
                returncode=1,
                stderr_string='err msg'
            )
        return ScriptCallResult(
            run_id=TAXIDWH_RUN_ID,
            returncode=0,
            stderr_string=''
        )


class TestScript(Script):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def execution_type(self) -> ExecutionType:
        return ExecutionType.SH

    def executable_args(self):
        return [self._name]

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)


class TestRetry:
    @pytest.mark.parametrize('legacy_lock_enabled', [
        (True,),
        (False,),
    ])
    def test_with_2_attempts_with_lock(self, temp_dir, legacy_lock_enabled):
        mock_executor = ScriptExecutorModified(
            _create_local_lock(lock_dir=temp_dir), retry_times=2, retry_sleep=0
        )
        scripts = ['1', '2']
        with patch_typed_lock as lock_mock:
            mock_executor.execute_all(
                scripts=[TestScript(s) for s in scripts],
                lock_names=scripts
            )
        assert mock_executor.attempt['1'] == 2
        assert mock_executor.attempt['2'] == 2
        assert lock_mock.call_count == 1

    def test_with_2_attempts_without_lock(self, temp_dir):
        mock_executor = ScriptExecutorModified(
            _create_local_lock(lock_dir=temp_dir), retry_times=2, retry_sleep=0
        )
        mock_executor.execute_all(
            scripts=[TestScript(s) for s in ['1', '2']]
        )
        assert mock_executor.attempt['1'] == 2
        assert mock_executor.attempt['2'] == 2

    def test_without_attempts(self, temp_dir):
        mock_executor = ScriptExecutorModified(
            _create_local_lock(lock_dir=temp_dir), retry_sleep=0
        )  # default without retry
        with pytest.raises(ScriptExecutionError):
            mock_executor.execute_all(
                scripts=[TestScript(s) for s in ['1', '2']]
            )

        assert mock_executor.attempt['1'] == 1
        assert mock_executor.attempt['2'] == 0


def test_init_shell_script_executor_with_invalid_param_retry_times(temp_dir):
    with pytest.raises(ValueError):
        ScriptExecutor(temp_dir, retry_times=0)


def kill_subproc(pidfile):
    for i in range(1, 20):
        time.sleep(0.05)
        with open(pidfile, 'r') as f:
            pid_string = f.readline().strip('\n')
            if pid_string:
                os.kill(int(pid_string), signal.SIGTERM)
                return
    raise RuntimeError('Could not find pid')


def test_kill(temp_dir, temp_pid):
    mock_executor = MockExecutor(temp_dir)
    with mock_executor:
        script_name = 'test_kill'
        killer_thread = threading.Thread(
            target=kill_subproc, args=(temp_pid,)
        )
        killer_thread.start()
        mock_executor.execute_shell([script_name], False)
        killer_thread.join(1)

        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts([script_name])
        error_string = 'Script "{}" (taxidwh_run_id={}) is ' \
                       'finished with exit code -15'.format(script_name,
                                                            TAXIDWH_RUN_ID)
        mock_executor.assert_stderr([(script_name, error_string)])


def test_timeout(temp_dir, temp_pid):
    mock_executor = MockExecutor(temp_dir)
    mock_executor.execution_timeout = 0.05
    with mock_executor:
        script_name = 'test_kill'
        mock_executor.execute_shell([script_name], False)

        mock_executor.assert_execution_status(False)
        mock_executor.assert_executed_scripts([script_name])

        error_string = regex(
            'Terminated \\(timeout by {} seconds\\)\n'
            'Script "{}" \\(taxidwh_run_id={}\\) is '
            'finished with exit code -(2|15)'.format(
                mock_executor.execution_timeout, script_name, TAXIDWH_RUN_ID)
        )
        mock_executor.assert_stderr([(script_name, error_string)])


class RaiseHelper(object):
    def __init__(self):
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        raise ValueError()


def test_safe_callback(temp_dir):
    f = RaiseHelper()

    executor = ScriptExecutor()
    executor.add_safe_callbacks(ExecutionEvent.BEFORE_CALL, f)
    executor.add_safe_callbacks(ExecutionEvent.AFTER_CALL, f)

    with mock.patch('subprocess.Popen') as popen_mock:
        popen_mock.return_value.communicate.return_value = (None, '')
        popen_mock.return_value.returncode = 0

        executor.execute_all([ShellScript('success', script_dir)])
    assert 2 == f.count


@pytest.mark.parametrize('event', [
    ExecutionEvent.BEFORE_CALL,
    ExecutionEvent.AFTER_CALL,
])
def test_raise_callback(temp_dir, event):
    f = RaiseHelper()
    executor = ScriptExecutor()
    executor.add_callbacks(event, f)
    with mock.patch('subprocess.Popen') as popen_mock:
        popen_mock.return_value.communicate.return_value = (None, '')
        popen_mock.return_value.returncode = 0

        with pytest.raises(RunnerError):
            executor.execute_all([ShellScript('success', script_dir)])
    assert 1 == f.count


def test_ignored_stdout(temp_dir, capfd):
    prev_disabled_level = logging.root.manager.disable
    try:
        logging.disable(logging.CRITICAL)
        executor = ScriptExecutor()
        executor.add_safe_callbacks(
            ExecutionEvent.AFTER_CALL, DefaultErrorListener(None, False)
        )
        executor.execute_all([ShellScript('test_stdout', script_dir)])
        captured = capfd.readouterr()
        assert '' == captured.out
        assert 'Write to stderr' in captured.err.split('\n')
    finally:
        logging.disable(prev_disabled_level)


class TestShellScript(object):
    bash = '/bin/bash'

    def test_no_script(self):
        with pytest.raises(RunnerError):
            ShellScript(None, script_dir)

        with pytest.raises(RunnerError):
            ShellScript('', script_dir)

        with pytest.raises(RunnerError):
            ShellScript(' ', script_dir)

    def test_no_args_script(self):
        script = ShellScript('success', script_dir)
        expected_path = os.path.join(script_dir, 'success.sh')
        assert 'success' == script.name
        assert expected_path == script.path
        assert [self.bash, '-e', expected_path] == script.executable_args()

    def test_args_script(self):
        script = ShellScript('success arg1', script_dir)
        expected_path = os.path.join(script_dir, 'success.sh')
        assert 'success' == script.name
        assert expected_path == script.path
        assert [self.bash, '-e', expected_path, 'arg1'] == script.executable_args()

    def test_whitespace_args_script(self):
        script = ShellScript('success arg1 "arg20 arg21"', script_dir)
        expected_path = os.path.join(script_dir, 'success.sh')
        assert 'success' == script.name
        assert expected_path == script.path
        expected_exec = [self.bash, '-e', expected_path, 'arg1', 'arg20 arg21']
        assert expected_exec == script.executable_args()

    def test_non_exists_script(self):
        script = ShellScript('non_exists', script_dir)
        with pytest.raises(RunnerError):
            script.executable_args()

    eq_params = [
            ('success', 'dir', 'success', 'dir', True),
            ('success arg1', 'dir', 'success arg1', 'dir', True),
            ('success arg1 arg2', 'dir', 'success arg1 arg2', 'dir', True),
            ('success arg1', 'dir', 'success      arg1   ', 'dir', True),
            ('success', 'dir', 'success_r', 'dir', False),
            ('success', 'dir', 'success', 'dir_r', False),
            ('success arg1', 'dir', 'success arg1 agr2', 'dir', False),
            ('success arg2 arg1', 'dir', 'success arg1 arg2', 'dir', False),
        ]

    @pytest.mark.parametrize(
        'string_lht, dir_lht, string_rht, dir_rht, expected', eq_params)
    def test_eq(self, string_lht, dir_lht, string_rht, dir_rht, expected):
        script_lht = ShellScript(string_lht, dir_lht)
        script_rht = ShellScript(string_rht, dir_rht)
        assert expected == (script_lht == script_rht)
        assert expected == (hash(script_lht) == hash(script_rht))

    @pytest.mark.parametrize(
        'string_lht, dir_lht, string_rht, dir_rht, opposite', eq_params)
    def test_ne(self, string_lht, dir_lht, string_rht, dir_rht, opposite):
        script_lht = ShellScript(string_lht, dir_lht)
        script_rht = ShellScript(string_rht, dir_rht)
        assert opposite != (script_lht != script_rht)
        assert opposite != (hash(script_lht) != hash(script_rht))

    def test_repr(self):
        assert 'ShellScript' in repr(ShellScript('success', script_dir))


class AbstractTestScript(object):
    base_class = None
    base_exec = None

    @pytest.mark.parametrize('script_string', [
        None, '', ' '
    ])
    def test_no_script(self, script_string):
        with pytest.raises(RunnerError):
            self.base_class(script_string)

    def test_no_args_script(self):
        script = self.base_class('test.success')
        assert 'test_success' == script.name
        assert self.base_exec + ['test.success'] == script.executable_args()

    @pytest.mark.parametrize('script_string', [
        'test.success arg1',
        'test.success      arg1   '
    ])
    def test_args_script(self, script_string):
        script = self.base_class(script_string)
        assert 'test_success' == script.name
        expected_exec = self.base_exec + ['test.success', 'arg1']
        assert expected_exec == script.executable_args()

    def test_whitespace_args_script(self):
        script = self.base_class('test.success arg1 "arg20 arg21"')
        assert 'test_success' == script.name
        expected_exec = self.base_exec + ['test.success', 'arg1', 'arg20 arg21']
        assert expected_exec == script.executable_args()

    eq_params = [
        ('success', 'success', True),
        ('success arg1', 'success arg1', True),
        ('success arg1', 'success      arg1   ', True),
        ('success', 'success2', False),
        ('success arg1', 'success arg2', False),
        ('success arg1', 'success arg1 arg2', False),
        ('success arg1 arg2', 'success arg2 arg1', False)
    ]

    @pytest.mark.parametrize('string_lht, string_rht, expected', eq_params)
    def test_eq(self, string_lht, string_rht, expected):
        script_lht = self.base_class(string_lht)
        script_rht = self.base_class(string_rht)
        assert expected == (script_lht == script_rht)
        assert expected == (hash(script_lht) == hash(script_rht))

    @pytest.mark.parametrize('string_lht, string_rht, opposite', eq_params)
    def test_ne(self, string_lht, string_rht, opposite):
        script_lht = self.base_class(string_lht)
        script_rht = self.base_class(string_rht)
        assert opposite != (script_lht != script_rht)
        assert opposite != (hash(script_lht) != hash(script_rht))


class TestPythonScript(AbstractTestScript):
    base_class = PythonScript
    base_exec = [sys.executable, '-m']

    def test_repr(self):
        assert 'PythonScript' in repr(PythonScript('test.success'))


class TestTaskScript(AbstractTestScript):
    base_class = TaskScript
    base_exec = [sys.executable, '-m', 'dmp_suite.task']
    non_changed_runner_args = dict(
        execution_type='task',
        retry_times=1,
        retry_sleep=0,
        lock_used=False,
        enable_time_recoder=False,
        lock_names=None
    )

    def assert_partial_args(self, expected_args: Dict, args: argparse.Namespace):
        for key, expected_value in expected_args.items():
            real_value = getattr(args, key)
            message = f'{key} attribute is {real_value} but {expected_value} was expected'
            assert expected_value == real_value, message

    @pytest.mark.parametrize('extra_cli_args, runner_args, extra_executable', [
        (
            ['test_task'],
            dict(
                accident_used=True,
                scheduler_lock_used=True,
            ),
            [['test_task']]
        ),
        (
            ['test_task1', 'test_task2'],
            dict(
                accident_used=True,
                scheduler_lock_used=True,
            ),
            [['test_task1'], ['test_task2']]
        ),
        (
            ['test_task --range 0 5'],
            dict(
                accident_used=True,
                scheduler_lock_used=True,
            ),
            [['test_task', '--range', '0', '5']]
        ),
        (
            ['test_task', '--no-accident'],
            dict(
                accident_used=False,
                scheduler_lock_used=True,
            ),
            [['test_task', '--no-accident']]
        ),
        (
            ['test_task --range 0 5', '--no-accident', '--lock-wait-limit', '30'],
            dict(
                accident_used=False,
                scheduler_lock_used=True,
            ),
            [['test_task', '--range', '0', '5', '--no-accident',
             '--lock-wait-limit', '30']]
        ),
        (
            ['test_task --range 0 5', 'test_task2', '--no-accident', '--lock-wait-limit', '30'],
            dict(
                accident_used=False,
                scheduler_lock_used=True,
            ),
            [
                ['test_task', '--range', '0', '5', '--no-accident',
                 '--lock-wait-limit', '30'],
                ['test_task2', '--no-accident', '--lock-wait-limit', '30'],
            ]
        ),
        (
            ['--no-scheduler-lock', 'test_task --range 0 5', '--no-accident', '--lock-wait-limit',
             '30'],
            dict(
                accident_used=False,
                scheduler_lock_used=False,
            ),
            [['test_task', '--range', '0', '5', '--no-accident',
             '--lock-wait-limit', '30']]
        ),
        (
            ['--no-accident', '--no-scheduler-lock', '--no-lock', 'test_task'],
            dict(
                accident_used=False,
                scheduler_lock_used=False,
            ),
            [['test_task', '--no-accident', '--no-lock']]
        ),
        (
            ['--as-graph', '-r', '2', '-s', '60', '-t', '10', '--no-lock',
             '--no-accident', 'test_task --range 0 5'],
            dict(
                accident_used=False,
                execution_timeout=10,
                scheduler_lock_used=True,
            ),
            [['test_task', '--range', '0', '5', '--as-graph',
             '-r', '2', '-s', '60', '--no-lock', '--no-accident']]
        ),
        (
            ['--as-graph', '-r', '2', '-s', '60', '-t', '10', '--no-lock',
             '--no-accident', 'test_task --range 0 5', 'test_task2'],
            dict(
                accident_used=False,
                execution_timeout=10,
                scheduler_lock_used=True,
            ),
            [
                ['test_task', '--range', '0', '5', '--as-graph',
                 '-r', '2', '-s', '60', '--no-lock', '--no-accident'],
                ['test_task2', '--as-graph',
                 '-r', '2', '-s', '60', '--no-lock', '--no-accident'],
            ]
        ),

    ])
    def test_parser(self,
                    extra_cli_args: Iterable,
                    runner_args: Dict,
                    extra_executable: List[Text]):
        task_path = 'test_task'
        resolve_patch = mock.patch('dmp_suite.runner.resolve_task_instance')
        with resolve_patch as resolve_mock:
            resolve_mock(task_path).name = task_path

            cli_args = ['task']
            cli_args.extend(extra_cli_args)
            args = parse_cli_args(cli_args)
            executor_args = args.execution_args(args)

            if 'execution_timeout' not in runner_args:
                runner_args['execution_timeout'] = init_py_env.settings('system.execution.execution_timeout')

            self.assert_partial_args(self.non_changed_runner_args, args)
            self.assert_partial_args(runner_args, args)

            assert executor_args['lock_names'] is None
            assert len(executor_args['scripts']) == len(extra_executable)
            for i, extra_exec in enumerate(extra_executable):
                task_script = executor_args['scripts'][i]
                executable = [sys.executable, '-m', 'dmp_suite.task']
                executable.extend(extra_exec)
                assert task_script.executable_args() == executable


@pytest.mark.parametrize(
    'scripts, lock_used, lock_names, expected_scripts, expected_lock_names', [
        (['script1', 'script2'], False, None,
         [TestScript('script1'), TestScript('script2')],
         None),

        (['script1', 'script2'], True, None,
         [TestScript('script1'), TestScript('script2')],
         ['script1', 'script2']),

        (['script1', 'script2'], True, '',
         [TestScript('script1'), TestScript('script2')],
         ['script1', 'script2']),

        (['script1', 'script2'], True, '    ',
         [TestScript('script1'), TestScript('script2')],
         ['script1', 'script2']),

        (['script1', 'script2'], False, 'script1 other_script',
         [TestScript('script1'), TestScript('script2')],
         None),

        (['script1', 'script2 arg'], False, None,
         [TestScript('script1'), TestScript('script2 arg')],
         None),

        (['script1', 'script2'], True, 'script1 other_script',
         [TestScript('script1'), TestScript('script2')],
         ['script1', 'other_script']),

        (['script1', 'script2'], True, 'none script2',
         [TestScript('script1'), TestScript('script2')],
         [None, 'script2']),

        (['script1', 'script2'], True, 'script1            none',
         [TestScript('script1'), TestScript('script2')],
         ['script1', None]),
    ])
def test_get_execution_args(scripts, lock_used, lock_names, expected_scripts,
                            expected_lock_names):
    args = argparse.Namespace()
    args.scripts = scripts
    args.lock_used = lock_used
    args.lock_names = lock_names
    args.dev = False

    result = _get_execution_args(
        lambda args: [TestScript(s) for s in args.scripts],
        args
    )
    assert expected_scripts == result['scripts']
    assert expected_lock_names == result['lock_names']
