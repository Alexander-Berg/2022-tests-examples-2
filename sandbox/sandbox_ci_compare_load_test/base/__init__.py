# -*- coding: utf-8 -*-

from sandbox.common.types import task as ctt
from sandbox import sdk2
from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test import runner_parameters
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement


class SandboxCiCompareLoadTestBase(TasksResourceRequirement, sdk2.Task):
    """
        Нагрузочная таска
    """

    class Parameters(sdk2.Parameters):
        quota_block = runner_parameters.QuotaParameters
        tests_block = runner_parameters.TestsParameters
        session_cnt = sdk2.parameters.Integer('Кол-во сессий для прогона (на все чанки в сумме)',
            required=True
        )
        grid_url = sdk2.parameters.String('Значение переменной окружения hermione_grid_url',
            required=True
        )

        tests_dev_task = sdk2.parameters.Task(
            'Dev-таска, на которой будет запущено нагрузочное тестирование',
            required=False,
            default=None,
        )
        data_center = parameters.data_center()

    @property
    def tests_dev_task(self):
        return self.Parameters.tests_dev_task

    def on_execute(self):
        with self.memoize_stage.create_task:
            tests_task = self.create_tests_subtask()

            raise sdk2.WaitTask(tests_task, statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)
