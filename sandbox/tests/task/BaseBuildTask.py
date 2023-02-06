import unittest

from sandbox.projects.sandbox_ci.task.BaseBuildTask import BaseBuildTask


class TestGetRealWaitTasksIds(unittest.TestCase):
    def test_should_return_real_tasks_ids(self):
        wait_tasks = [100, 1001]

        tasks_relations = {100: 1000}

        expected = [1000, 1001]

        actual = BaseBuildTask.get_real_wait_tasks_ids.im_func(self, wait_tasks, tasks_relations)

        self.assertListEqual(actual, expected)


class TestGetRealWaitOutputs(unittest.TestCase):
    def test_should_return_real_wait_outputs(self):
        wait_output_parameters = {
            '100': 'is_artifacts_ready',
            '1001': 'is_something_here'
        }

        tasks_relations = {100: 1000}

        expected = {
            '1000': 'is_artifacts_ready',
            '1001': 'is_something_here'
        }

        actual = BaseBuildTask.get_real_wait_outputs.im_func(self, wait_output_parameters, tasks_relations)

        self.assertEqual(actual, expected)
