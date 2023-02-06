import py
import pytest
import functools
import subprocess

from sandbox.common import errors as common_errors
from sandbox.common import system as common_system
from sandbox.common import projects_handler

from sandbox.sdk2.helpers import gdb

from sandbox.sandboxsdk import task as sdk1_task
from sandbox.sandboxsdk import channel as sdk1_channel

from sandbox.yasandbox.manager import tests


@pytest.fixture(scope='function')
def channel(request, server, api_su_session):
    transport = sdk1_channel.channel.sandbox.server.transport
    original_auth = transport.auth
    transport.auth = api_su_session.transport.auth

    def fin():
        transport.auth = original_auth

    request.addfinalizer(fin)


class MemoTestTask(sdk1_task.SandboxTask):

    type = 'MEMO_TEST_TASK'

    first_run = True

    def on_execute(self):
        with self.memoize_stage.waiting(commit_on_entrance=False, commit_on_wait=False) as st:
            if self.first_run:
                raise common_errors.WaitTime
            assert st.runs == 0

        with self.memoize_stage.important_action as st:
            assert st.runs == 1

        with self.memoize_stage.important_action(3) as st:
            assert 1 <= st.runs <= 3

        with self.memoize_stage.action2 as st:
            assert st.runs == 1

        with self.memoize_stage['action2'] as st:
            assert st.runs == 1

        assert st.executed is False


class TestTask:
    def test__client_info(self):
        task = sdk1_task.SandboxTask()
        task.client_info == common_system.get_sysparams()

    def test__is_arch_compatible__any(self):
        linux_task = sdk1_task.SandboxTask()
        linux_task.arch = 'linux'
        freebsd_task = sdk1_task.SandboxTask()
        freebsd_task.arch = 'freebsd'
        assert linux_task.is_arch_compatible('any')
        assert freebsd_task.is_arch_compatible('any')

    def test__is_arch_compatible__linux(self):
        linux_task = sdk1_task.SandboxTask()
        linux_task.arch = 'linux'
        assert linux_task.is_arch_compatible('linux')
        assert linux_task.is_arch_compatible('any')
        assert not linux_task.is_arch_compatible('freebsd')

    def test__is_arch_compatible__freebsd(self):
        freebsd_task = sdk1_task.SandboxTask()
        freebsd_task.arch = 'freebsd'
        assert freebsd_task.is_arch_compatible('freebsd')
        assert freebsd_task.is_arch_compatible('any')
        assert not freebsd_task.is_arch_compatible('linux')

    def test__memoize_stage(self, server, task_manager, channel, task_session, monkeypatch):
        from sandbox import projects
        projects.TYPES["MEMO_TEST_TASK"] = projects_handler.TaskTypeLocation(
            'MemoTestTask', MemoTestTask, None)
        projects.__dict__['GoodTaskMod'] = MemoTestTask

        task = tests._create_task(task_manager, 'MEMO_TEST_TASK', owner='user')

        monkeypatch.setattr(sdk1_channel.channel, "task", task)
        task_session(sdk1_channel.channel.rest.server, task.id, "test", login="test")

        for run in xrange(6):
            t = task_manager.load(task.id)
            t.first_run = not run
            try:
                t.on_execute()
            except common_errors.WaitTime:
                assert t.first_run
            task_manager.update(t)

        task = task_manager.load(task.id)
        assert task.memoize_stage.important_action.runs == 3
        assert task.memoize_stage.important_action.passes == 7
        assert task.memoize_stage.action2.runs == 1
        assert task.memoize_stage.action2.passes == 9
        assert task.memoize_stage.action2.executed is None

        with pytest.raises(ZeroDivisionError):
            with task.memoize_stage.exploded_stage as st:
                assert st.runs == 1
                1 / 0

        assert st.executed is True
        assert st.runs == 1
        assert st.passes == 0
        assert task.memoize_stage.exploded_stage.executed is None

        with task.memoize_stage.exception as st:
            with pytest.raises(ZeroDivisionError):
                assert st.runs == 1
                1 / 0

        assert st.executed is True
        assert st.runs == 1
        assert st.passes == 0
        assert task.memoize_stage.exception.executed is None

        with pytest.raises(ZeroDivisionError):
            with task.memoize_stage.interrupted_section(commit_on_entrance=False) as st:
                assert st.runs == 0
                1 / 0

        assert st.executed is True
        assert st.runs == 0
        assert st.passes == 0

        with task.memoize_stage.interrupted_section(commit_on_entrance=False) as st:
            assert st.runs == 0

        assert st.executed is True
        assert st.runs == 1
        assert st.passes == 0

        assert task.ctx == task_manager.load(task.id).ctx

        # Reload task, check save keys to context on server side
        task = task_manager.load(task.id)

        assert task.memoize_stage.exploded_stage.runs == 1
        assert task.memoize_stage.exception.runs == 1
        assert task.memoize_stage.interrupted_section.runs == 1

    def test__kill_subprocesses(self):
        sleep_code = 'import time; time.sleep(99);'
        ignore_term_code = 'import signal; signal.signal(signal.SIGTERM, signal.SIG_IGN);'

        prs = []
        for time_to_kill in (False, 2):
            pr1 = subprocess.Popen(['python', '-c', sleep_code])
            pr2 = subprocess.Popen(['python', '-c', ' '.join([ignore_term_code, sleep_code])])
            if time_to_kill:
                pr1.time_to_kill = time_to_kill
                pr2.time_to_kill = time_to_kill
            prs.extend([pr1, pr2])

        task = sdk1_task.SandboxTask()
        try:
            task._SandboxTask__kill_registered_subprocesses(prs)
        except Exception:
            for pr in prs:
                if pr.poll() is None:
                    pr.kill()
            raise

    def test__get_core_path(self, tmpdir):
        cores = ['basesearch.27892.11', 'ranking_middlese.14692']
        tmpdir = py.path.local(tmpdir)
        for core in cores:
            tmpdir.join(core).ensure(file=True)

        fn = functools.partial(gdb.get_core_path, str(tmpdir))

        assert fn('basesearch', 27892) == str(tmpdir.join('basesearch.27892.11'))
        assert fn('ranking_middlese', 14692) == str(tmpdir.join('ranking_middlese.14692'))
        assert fn('basesearch', 11) is None
        assert fn('foobar', 27892) is None
        assert fn('foobar', 14692) is None
        assert fn('foobar', 11) is None
