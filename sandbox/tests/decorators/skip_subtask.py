# -*- coding: utf-8 -*-

import unittest
from sandbox.projects.sandbox_ci.tests import MagicMock

from sandbox.projects.sandbox_ci.sandbox_ci_palmsync.validate import SandboxCiPalmsyncValidate
from sandbox.projects.sandbox_ci.task.BasePulseTask import BasePulseTask
from sandbox.projects.sandbox_ci.decorators.skip_subtask import skip_subtask

from sandbox.projects.sandbox_ci.tests import DotDict


class BeforeEach:
    checks_to_skip = ['palmsync']

    meta = DotDict({
        'skip_step': MagicMock()
    })

    def need_to_skip_check(self, label):
        return label in self.checks_to_skip


class TestSkipSubtask(BeforeEach, unittest.TestCase):
    def test_should_return_none(self):
        @skip_subtask(SandboxCiPalmsyncValidate, 'skip')
        def decorated_func(self, arg1, arg2, arg3):
            return '{}{}{}'.format(arg1, arg2, arg3)

        actual = decorated_func(self, 1, 2, 3)

        self.meta.skip_step.assert_called_with(
            reason='not modified',
            github_context=u'[Sandbox CI] Валидация тестовых сценариев',
            description='skip',
            label='palmsync')

        self.assertIsNone(actual)

    def test_should_return_task(self):
        @skip_subtask(BasePulseTask, 'skip')
        def decorated_func(self, arg1, arg2, arg3):
            return '{}{}{}'.format(arg1, arg2, arg3)

        actual = decorated_func(self, 1, 2, 3)

        self.assertEqual(actual, '123')
