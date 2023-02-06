import unittest

from sandbox.common.utils import singleton_property

from sandbox.projects.sandbox_ci.task.BaseTask import BaseTask
from sandbox.projects.sandbox_ci import managers


class BeforeEach:
    @singleton_property
    def meta(self):
        return managers.MetaTaskManager(self)

    @singleton_property
    def task_dependencies(self):
        return managers.TaskDependenciesManager(self)


class TestWaitTimeout(BeforeEach, unittest.TestCase):
    class Parameters():
        kill_timeout = 10

    def test_success(self):
        self.assertEqual(
            BaseTask.wait_timeout.__get__(self),
            20,
        )


class TestParseNoneWaitOutputParameters(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = None

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {},
        )


class TestParseEmptyWaitOutputParameters(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {},
        )


class TestParseWaitOutputParametersWithInvalidId(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {'foo': 'bar', 20: 'param1'}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {20: ['param1']},
        )


class TestParseWaitOutputParameter(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {10: 'param1'}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {10: ['param1']},
        )


class TestParseWaitOutputParameters(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {10: 'param1,param2'}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {10: ['param1', 'param2']},
        )


class TestParseWaitOutputParametersWithSpaces(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {10: '  param1,  param2  '}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {10: ['param1', 'param2']},
        )


class TestParseWaitOutputParametersWithExtraComma(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {10: 'param1,param2,,'}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {10: ['param1', 'param2']},
        )


class TestParseWaitOutputParametersOfSomeTasks(BeforeEach, unittest.TestCase):
    class Parameters():
        wait_output_parameters = {10: 'param1,param2', 20: 'param1,param2'}

    def test_success(self):
        self.assertDictEqual(
            BaseTask.dependency_output_targets.__get__(self),
            {10: ['param1', 'param2'], 20: ['param1', 'param2']},
        )
