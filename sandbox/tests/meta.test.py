# -*- coding: utf-8 -*-

import unittest

import sandbox.common.types.task as ctt

from sandbox.projects.trendbox_ci.beta.modules.meta import get_subtasks, create_subtask


class BeforeEach:

    class Task:

        class Context:
            def __init__(self):
                self.subtasks = []
                self.subtasks_ids = []

        class Query:

            def __init__(self, task, id):
                self.task = task
                self.id = id

            def limit(self, n):
                self.limit = n
                return self.task.Context.subtasks

        def __init__(self, task_id=None, status=None):
            self.id = task_id
            self.status = status
            self.Context = self.Context()

        def find(self, task_type=None, **constraints):
            self.query = self.Query(self, constraints.get('id'))
            return self.query

    def task_type(self, task, **parameters):
        subtask = self.Task(
            parameters.get('id'),
            parameters.get('status')
        )
        task.Context.subtasks.append(subtask)
        return subtask


class TestGetSubtasks(BeforeEach, unittest.TestCase):

    def test_success(self):
        task = self.Task()

        create_subtask(task, self.task_type, id=1)
        create_subtask(task, self.task_type, id=2)
        create_subtask(task, self.task_type, id=3)

        subtasks = get_subtasks(task)
        subtasks_ids = [subtask.id for subtask in subtasks]

        self.assertEqual(subtasks_ids, task.Context.subtasks_ids)

    def test_empty(self):
        task = self.Task()

        get_subtasks(task)

        query = task.query

        self.assertEqual(query.limit, 0)
        self.assertEqual(
            query.id,
            [],
        )

    def test_query(self):
        task = self.Task()

        create_subtask(task, self.task_type, id=4)
        create_subtask(task, self.task_type, id=5)
        create_subtask(task, self.task_type, id=6)

        get_subtasks(task)

        query = task.query

        self.assertEqual(query.limit, 3)
        self.assertEqual(
            query.id,
            [4, 5, 6],
        )


class TestCreateSubtask(BeforeEach, unittest.TestCase):

    def test_success(self):
        task = self.Task()

        create_subtask(task, self.task_type, id=7)
        create_subtask(task, self.task_type, id=8)
        create_subtask(task, self.task_type, id=9)

        self.assertEqual(
            task.Context.subtasks_ids,
            [7, 8, 9],
        )

    def test_empty(self):
        task = self.Task()

        self.assertEqual(
            task.Context.subtasks_ids,
            [],
        )

    def test_with_params(self):
        task = self.Task()

        subtask = create_subtask(task, self.task_type, id=1, status=ctt.Status.PREPARING)

        self.assertEqual(subtask.id, 1)
        self.assertEqual(subtask.status, ctt.Status.PREPARING)
