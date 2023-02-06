# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.tests import MagicMock, MemoizeStageMock

from sandbox.common.errors import TaskFailure
from sandbox.common.utils import singleton_property
from sandbox.projects.sandbox_ci import managers
from sandbox.projects.sandbox_ci.sandbox_ci_blockstat_test import SandboxCiBlockstatTest
from sandbox.projects.sandbox_ci.tests import DotDict


class BeforeEach:
    @singleton_property
    def meta(self):
        return managers.MetaTaskManager(self)

    @singleton_property
    def release(self):
        return managers.ReleaseManager(self)

    class Parameters():
        description = 'serp/web4#release/v1.200.0'
        platform = 'desktop'
        project = 'web4'
        templates = DotDict({'id': '1'})
        blockstat_format = 'raw'
        is_apphost = False

    class Context():
        report_resources = []

    memoize_stage = MemoizeStageMock()
    wait = MagicMock()
    set_info = MagicMock()
    benchmark_plan_resource_id = 2
    rr_bundle_resource_id = 3
    get_blockstat_logs = MagicMock(return_value=DotDict({'id': '4'}))
    get_subtask = MagicMock(return_value=DotDict({'status': 'SUCCESS'}))
    get_subtask_context = MagicMock(return_value={
        'result_stats': {'sessions_count': 6277, 'test_result': 'OK', 'skips_count': 0, 'errors_count': 0},
        'test_task_resources': ['1', '2', '3'],
    })


class TestWait(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should wait subtasks"""
        self.create_subtask = MagicMock(side_effect=['1', '2'])
        SandboxCiBlockstatTest.execute.im_func(self)

        self.assertEqual(self.wait.call_count, 2)
        self.wait.assert_any_call('1')
        self.wait.assert_any_call('2')


class TestFooter(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should add report ids to Context"""
        self.Context.report_resources = []
        self.create_subtask = MagicMock(side_effect=['1', '2'])
        SandboxCiBlockstatTest.execute.im_func(self)

        self.assertEqual(self.Context.report_resources, ['1', '2', '3'])


class TestTaskFail(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should raise TaskFail error in case of FAILED test result from subtask"""
        self.create_subtask = MagicMock(side_effect=['1', '2'])
        self.get_subtask_context = MagicMock(return_value={
            'result_stats': {'sessions_count': 6277, 'test_result': 'FAILED', 'skips_count': 0, 'errors_count': 1},
            'test_task_resources': ['1', '2', '3'],
        })
        with self.assertRaises(TaskFailure):
            SandboxCiBlockstatTest.execute.im_func(self)

    def test_failure(self):
        """Should arise TaskFail error in case of FAILURE"""
        self.create_subtask = MagicMock(side_effect=['1', '2'])
        self.get_subtask = MagicMock(return_value={'status': 'FAILURE'})
        self.get_subtask_context = MagicMock()

        with self.assertRaises(TaskFailure):
            SandboxCiBlockstatTest.execute.im_func(self)

        self.assertEqual(self.get_subtask_context.call_count, 0)

    def test_exception(self):
        """Should arise TaskFail error in case of EXCEPTION"""
        self.create_subtask = MagicMock(side_effect=['1', '2'])
        self.get_subtask = MagicMock(return_value={'status': 'EXCEPTION'})
        self.get_subtask_context = MagicMock()

        with self.assertRaises(TaskFailure):
            SandboxCiBlockstatTest.execute.im_func(self)

        self.assertEqual(self.get_subtask_context.call_count, 0)


class TestBeforeEnd(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should call add_status_comment in case of release"""
        self.Parameters.send_comment_to_issue = 'SEAREL-1234'
        self.release.add_status_comment = MagicMock()
        SandboxCiBlockstatTest.before_end.im_func(self, 'SUCCESS')
        self.release.add_status_comment.assert_called_with('SEAREL-1234', 'SUCCESS')

    def test_fail(self):
        """Should not call add_status_comment in case of regular task"""
        self.Parameters.send_comment_to_issue = ''
        self.release.add_status_comment = MagicMock()
        SandboxCiBlockstatTest.before_end.im_func(self, 'SUCCESS')
        self.assertEqual(self.release.add_status_comment.call_count, 0)
