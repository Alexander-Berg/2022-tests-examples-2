# -*- coding: utf-8 -*-

import mock
import unittest

from sandbox.common.utils import singleton_property
from sandbox.common.types import task as ctt
from sandbox.common.types import resource as ctr
from sandbox.common.types.misc import NotExists

from sandbox.projects.sandbox_ci import managers
from sandbox.projects.sandbox_ci.tests import DotDict


class BeforeEach:
    class Context:
        subtasks = NotExists
        pass

    @singleton_property
    def meta(self):
        return managers.MetaTaskManager(self)

    class Task:
        def __init__(self, task_id, status):
            self.id = task_id
            self.status = status

    class Query():
        def __init__(self, subtasks):
            self.subtasks = subtasks

        def limit(self, count):
            return self.subtasks[count:]

    def find(self, task_type=None):
        return self.Query(self.subtasks)


class TestSubtasksFilter(BeforeEach, unittest.TestCase):

    class Context:
        subtasks = [1, 2]

    def test_success(self):
        """Should return subtasks filtered by Context.subtasks"""
        self.subtasks = [
            self.Task(1, ctt.Status.SUCCESS),
            self.Task(2, ctt.Status.SUCCESS),
            self.Task(3, ctt.Status.SUCCESS),
        ]
        self.assertEqual(
            [task.id for task in self.meta.subtasks],
            [1, 2],
        )


class TestSubtasksFallBack(BeforeEach, unittest.TestCase):

    def test_success(self):
        """Should return all subtasks if there's no Context.subtasks as a fallback"""
        self.subtasks = [
            self.Task(1, ctt.Status.SUCCESS),
            self.Task(2, ctt.Status.SUCCESS),
            self.Task(3, ctt.Status.SUCCESS),
        ]
        self.assertEqual(
            [task.id for task in self.meta.subtasks],
            [1, 2, 3],
        )


class TestGetNotFinishedSubtasks(BeforeEach, unittest.TestCase):
    class Context:
        subtasks = [1, 2, 3]

    def test_1(self):
        """Should return in progress subtasks from meta"""
        self.subtasks = [
            self.Task(1, ctt.Status.ENQUEUED),
            self.Task(2, ctt.Status.EXECUTING),
            self.Task(3, ctt.Status.SUCCESS),
        ]
        self.assertEqual(
            [task.id for task in self.meta.not_finished_subtasks],
            [1, 2],
        )

    def test_2(self):
        """Should skip subtasks which are not in Context.subtasks"""
        self.subtasks = [
            self.Task(1, ctt.Status.ENQUEUED),
            self.Task(2, ctt.Status.EXECUTING),
            self.Task(4, ctt.Status.DRAFT),
        ]
        self.assertEqual(
            [task.id for task in self.meta.not_finished_subtasks],
            [1, 2],
        )


class TestFilterFailed(BeforeEach, unittest.TestCase):

    def test_success(self):
        """Should return only failed tasks"""
        self.subtasks = [
            self.Task(1, ctt.Status.ENQUEUED),
            self.Task(2, ctt.Status.EXECUTING),
            self.Task(3, ctt.Status.SUCCESS),
            self.Task(4, ctt.Status.FAILURE),
            self.Task(5, ctt.Status.EXCEPTION),
        ]
        self.assertEqual(
            [task.id for task in self.meta.failed_subtasks],
            [4, 5],
        )


class TestGetSubtasksArtifactsIds(BeforeEach, unittest.TestCase):
    def generate_fake_resource(self, resource_id, state=ctr.State.READY):
        return DotDict({
            'id': resource_id,
            'http': DotDict({'proxy': 'proxy'}),
            'type': 'type',
            'state': state,
            'attributes': DotDict({'public': True}),
        })

    @mock.patch.object(managers.MetaTaskManager, 'get_subtask_resources')
    def test_should_return_artifacts_ids(self, mock_get_subtask_resources):
        """
        Should return ids of artifacts of resources.

        :param mock_get_subtask_resources:
        :type mock_get_subtask_resources: mock.Mock
        """
        self.subtasks = [
            self.Task(1, ctt.Status.SUCCESS),
        ]

        mock_get_subtask_resources.return_value = [
            self.generate_fake_resource(1),
            self.generate_fake_resource(2),
        ]

        expected = [1, 2]

        actual = self.meta.get_subtasks_artifacts_ids()

        self.assertEquals(actual, expected)
