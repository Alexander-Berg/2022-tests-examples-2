import os
import unittest
from sandbox.projects.sandbox_ci.tests import MagicMock
from sandbox.projects.sandbox_ci.tests import DotDict

from sandbox.sandboxsdk import process
from sandbox.projects.sandbox_ci.managers.selective_checks import SelectiveChecks


class Task:
    class Parameters:
        project_git_base_ref = 'dev'

    project_conf = {'selective_checks': True}
    project_dir = '/foo'
    project_sources_dir = '/foo'
    scripts = DotDict({
        'run_js': MagicMock(return_value={
            'toRun': ['gemini.touch-pad', 'gemini.touch-phone', 'hermione.touch-pad', 'hermione.touch-phone'],
            'toSkip': ['gemini.desktop', 'hermione.desktop']
        })
    })
    os.environ['PATH'] = '/foo'


class TestChecksToSkip(unittest.TestCase):
    def test_success(self):
        """Should return toSkip if enabled"""
        task = Task()
        task.Parameters.selective_checks = True
        process.run_process = MagicMock(return_value=DotDict({
            'communicate': MagicMock(return_value=['some-base'])
        }))

        manager = SelectiveChecks(task)

        self.assertEqual(manager.checks_to_skip(), ['gemini.desktop', 'hermione.desktop'])
        task.scripts.run_js.assert_called_with(
            'script/selective-checks/get-checks-conditions.js',
            {
                'base': 'some-base',
                'working-copy': '/foo',
                'config': '.config/selective-checks.js',
                'json': True,
            }
        )

    def test_disabled_with_parameter(self):
        """Should return empty list if disabled in Parameters"""
        task = Task()
        task.Parameters.selective_checks = False
        task.project_conf = {'selective_checks': True}

        manager = SelectiveChecks(task)

        self.assertEqual(manager.checks_to_skip(), [])

    def test_disabled_with_config(self):
        """Should return empty list if disabled in project_conf"""
        task = Task()
        task.Parameters.selective_checks = True
        task.project_conf = {'selective_checks': False}

        manager = SelectiveChecks(task)

        self.assertEqual(manager.checks_to_skip(), [])
