# -*- coding: utf-8 -*-

import unittest
from mock import Mock, ANY

from sandbox.projects.sandbox_ci.managers.meta import TaskDeclaration
from sandbox.projects.sandbox_ci.task import ManualRunMetaTaskMixin
from sandbox.projects.sandbox_ci.task.ManualRunMetaTaskMixinModule import MANUAL_TESTING_GITHUB_CONTEXT
from sandbox.projects.sandbox_ci.task.test_task.BaseTestTask import BaseTestTask


class MockAnotherTask(object):
    pass


class MockTestTask(BaseTestTask):
    pass


class TestManualRun(object):
    needed_artifact_types = ['type1', 'type2']

    @classmethod
    def format_github_context(cls):
        return 'Test github context'


class TestMetaTask(ManualRunMetaTaskMixin):
    Parameters = Mock()

    manual_run_task_type = TestManualRun
    testpalm_project_suffix = 'test'

    def __init__(self):
        self.config = Mock()
        self.github_statuses = object()
        self.get_registered_artifact_id = Mock()
        self.meta = Mock()
        self.ref = 'Test ref'
        self.project_name = 'some_project'


class TestsManualRunMetaTaskMixin(unittest.TestCase):
    def setUp(self):
        self.instance = TestMetaTask()
        self.instance.config.is_enabled = Mock(return_value=True)
        self.instance.Parameters.manual_test_runs.force_manual_test_runs = False

    def assertManualTestingStatusSkip(self, reason, message):
        self.instance.meta.skip_step.assert_any_call(
            github_context=MANUAL_TESTING_GITHUB_CONTEXT,
            description=message,
            label='manual_testing',
            reason=reason
        )
        self.instance.meta.skip_step.assert_any_call(
            github_context='Test github context',
            description=message,
            label='manual_runs',
            reason=reason
        )

    def assertManualTestingNotSkipped(self):
        self.assertFalse(self.instance.meta.skip_step.called)

    def test_trivial(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': True,
            'keys': []
        })

        self.assertManualTestingStatusSkip('is trivial', u'TRIVIAL не тестируются вручную')

    def test_empty_keys(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': []
        })

        self.assertManualTestingNotSkipped()

    def test_single_fei(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['FEI-15']
        })

        self.assertManualTestingStatusSkip('from fei', u'Задачи из очереди FEI не тестируются вручную')

    def test_several_fei(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['FEI-15', 'FEI-17']
        })
        self.assertManualTestingStatusSkip('from fei', u'Задачи из очереди FEI не тестируются вручную')

    def test_single_serp(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['SERP-15']
        })

        self.assertManualTestingNotSkipped()

    def test_mix(self):
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['FEI-15', 'SERP-15']
        })

        self.assertManualTestingNotSkipped()

    def test_empty_wait_tasks_not_allowed_and_has_test_tasks(self):
        self.instance.create_manual_run_subtask(
            issues_info={
                'has_trivial': False,
                'keys': ['FEI-15', 'SERP-15']
            },
            wait_tasks=[TaskDeclaration(MockTestTask, [], {}), TaskDeclaration(MockAnotherTask, [], {})],
        )

        self.assertManualTestingNotSkipped()

    def test_deploy_turned_off(self):
        self.instance.config.is_enabled = Mock(return_value=False)
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['FEI-15', 'SERP-15']
        }, wait_tasks=[TaskDeclaration(MockTestTask, [], {}), TaskDeclaration(MockTestTask, [], {})])

        self.assertManualTestingStatusSkip('disabled', u'Создание ранов для ручного тестирования выключено в секции genisys deploy.testpalm_manual_run')

    def test_subtask_is_created_if_not_skipped(self):
        expected = object()
        self.instance.meta.create_subtask = Mock(return_value=expected)
        self.instance.Parameters.description = 'Test description'

        test_task = TaskDeclaration(MockTestTask, [], {})

        res = self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': False,
            'keys': ['SERP-15']
        }, wait_tasks=[test_task])

        self.assertEqual(res, expected)
        self.instance.meta.create_subtask.assert_called_once_with(
            task_type=TestManualRun,
            waitable=ANY,
            description='Test description',
            project_suffix='test',
            build_artifacts_resources=ANY,
            ref='Test ref',
            issues_info=ANY,
            wait_tasks=[test_task],
        )

    def test_subtask_is_created_if_forced(self):
        self.instance.Parameters.manual_test_runs.force_manual_test_runs = True
        self.instance.create_manual_run_subtask(issues_info={
            'has_trivial': True,
            'keys': []
        }, wait_tasks=[])

        self.instance.meta.skip_step.assert_called_once_with(
            github_context=MANUAL_TESTING_GITHUB_CONTEXT,
            description=ANY,
            label=ANY,
            reason=ANY
        )
        self.assertTrue(self.instance.meta.create_subtask.called)
