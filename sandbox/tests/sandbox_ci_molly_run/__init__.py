# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.tests import MagicMock, MemoizeStageMock

from sandbox.common.errors import TaskFailure
from sandbox.common.utils import singleton_property
from sandbox.projects.sandbox_ci import managers
from sandbox.projects.sandbox_ci.sandbox_ci_molly_run import SandboxCiMollyRun
from sandbox.projects.sandbox_ci.tests import DotDict
from sandbox.common.types import task as ctt


class BeforeEach:
    @singleton_property
    def meta(self):
        return managers.MetaTaskManager(self)

    @singleton_property
    def task_reports(self):
        return managers.Reports(self)

    @singleton_property
    def release(self):
        return managers.ReleaseManager(self)

    class Parameters():
        description = 'serp/web4#release/v1.200.0'
        target_uri = 'https://some/url'
        project = 'web4'

    class Context():
        molly_run_task_id = None
        report_links = []

    memoize_stage = MemoizeStageMock()
    molly_task = DotDict({'id': 1, 'Parameters': None})


class TestMollyRun(BeforeEach, unittest.TestCase):
    def test_failed_if_child_task_failure(self):
        self.run_and_wait_molly_task = MagicMock()
        self.molly_task.status = ctt.Status.EXCEPTION
        self.molly_task.Parameters = DotDict({'status': False, 'report': 'https://report/url'})
        self.get_molly_run_task = MagicMock(return_value=self.molly_task)

        with self.assertRaises(TaskFailure):
            SandboxCiMollyRun.execute.im_func(self)

    def test_failed_if_vulnerabilities_found(self):
        self.run_and_wait_molly_task = MagicMock()
        self.molly_task.status = ctt.Status.SUCCESS
        self.molly_task.Parameters = DotDict({'status': True, 'report': 'https://report/url'})
        self.get_molly_run_task = MagicMock(return_value=self.molly_task)

        with self.assertRaises(TaskFailure):
            SandboxCiMollyRun.execute.im_func(self)

    def test_failed_if_molly_task_not_found(self):
        self.run_and_wait_molly_task = MagicMock()
        self.molly_task = None
        self.get_molly_run_task = MagicMock(return_value=self.molly_task)

        with self.assertRaises(TaskFailure):
            SandboxCiMollyRun.execute.im_func(self)


class TestFooter(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should add report links to Context"""
        self.Context.report_links = []
        self.run_and_wait_molly_task = MagicMock()
        self.molly_task.status = ctt.Status.SUCCESS
        self.molly_task.Parameters = DotDict({'status': False, 'report': 'https://report/url'})
        self.get_molly_run_task = MagicMock(return_value=self.molly_task)
        self.task_reports.status_badge = MagicMock(return_value='SUCCESS')
        self.task_reports.description = MagicMock(return_value='<a href="https://report/url" target="_blank">molly_report</a>')

        expected_reports = [{
            'Status': ctt.Status.SUCCESS,
            'Report': '<a href="https://report/url" target="_blank">molly_report</a>'
        }]

        SandboxCiMollyRun.execute.im_func(self)

        self.assertEqual(self.Context.report_links, expected_reports)

    @unittest.skip("Flaky test, details: https://ml.yandex-team.ru/thread/sandbox/164944336352482380")
    def test_failure(self):
        """Should add report links to Context"""
        self.Context.report_links = []
        self.run_and_wait_molly_task = MagicMock()
        self.molly_task.Parameters = DotDict({'status': True, 'report': 'https://report/url'})
        self.get_molly_run_task = MagicMock(return_value=self.molly_task)
        self.task_reports.status_badge = MagicMock(return_value='FAILURE')
        self.task_reports.description = MagicMock(return_value='<a href="https://report/url" target="_blank">molly_report</a>')

        expected_reports = [{
            'Status': ctt.Status.FAILURE,
            'Report': '<a href="https://report/url" target="_blank">molly_report</a>'
        }]

        with self.assertRaises(TaskFailure):
            SandboxCiMollyRun.execute.im_func(self)

        self.assertEqual(self.Context.report_links, expected_reports)


class TestBeforeEnd(BeforeEach, unittest.TestCase):
    def test_success(self):
        """Should call add_status_comment in case of release"""
        self.Parameters.send_comment_to_issue = 'SEAREL-1234'
        self.release.add_status_comment = MagicMock()
        SandboxCiMollyRun.before_end.im_func(self, 'SUCCESS')
        self.release.add_status_comment.assert_called_with('SEAREL-1234', 'SUCCESS')

    def test_fail(self):
        """Should not call add_status_comment in case of regular task"""
        self.Parameters.send_comment_to_issue = ''
        self.release.add_status_comment = MagicMock()
        SandboxCiMollyRun.before_end.im_func(self, 'SUCCESS')
        self.assertEqual(self.release.add_status_comment.call_count, 0)
