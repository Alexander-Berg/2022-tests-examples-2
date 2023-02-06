# -*- coding: utf-8 -*-

import datetime
import dateutil
import logging

from sandbox import sdk2
from sandbox.common.types import misc as ctm, task as ctt

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.projects.sandbox_ci.sandbox_ci_test_cost_reporter import SandboxCiTestCostReporter


class TaskRequirements(sdk2.Requirements):
    dns = ctm.DnsType.LOCAL
    cores = 1

    class Caches(sdk2.Requirements.Caches):
        pass


class TaskParameters(parameters.CommonParameters):
    _default_created_from = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    _default_created_till = datetime.datetime.today().strftime("%Y-%m-%d")

    _container = parameters.environment_container()

    task_type = sdk2.parameters.String(
        "Task type",
        description="Тип тасок релиза репорта, для которых нужно собрать статистику",
        required=True
    )
    created_from = sdk2.parameters.String(
        "Created from (format: YYYY-MM-DD)",
        description="Будут найдены таски, которые созданы после указанной даты. По умолчанию будет использоваться сегодняшняя дата",
        default=_default_created_from
    )
    created_till = sdk2.parameters.String(
        "Created till (format: YYYY-MM-DD)",
        description="Будут найдены таски, которые созданы до указанной даты. По умолчанию будет использоваться вчерашняя дата",
        default=_default_created_till
    )

    with sdk2.parameters.Output():
        reported_release_tasks = sdk2.parameters.List(
            'Reported release tasks',
            value_type=sdk2.parameters.Integer,
            required=True,
            default=[],
            description='Идентификаторы релизных тасок, которые были зарепорчены'
        )

    node_js = parameters.NodeJsParameters


class TaskContext(sdk2.Context):
    report_resources = []


class SandboxCiTestCostReportReleasesReporter(TasksResourceRequirement, sdk2.Task):
    """
    Таск, ищущий все релизы репорта за временной промежуток и запускающий подсчёт их приблизительной стоимости для
    ручного тестирования.
    """

    class Requirements(TaskRequirements):
        pass

    class Parameters(TaskParameters):
        pass

    class Context(TaskContext):
        pass

    def on_save(self):
        if not self.Parameters.created_from:
            self.Parameters.created_from = self.Parameters._default_created_from

        if not self.Parameters.created_till:
            self.Parameters.created_till = self.Parameters._default_created_till

    def on_execute(self):
        previous_tasks = self._find_previously_reported_release_tasks()
        release_tasks = self._find_report_release_tasks()

        tasks = filter(lambda task: task.id not in previous_tasks, release_tasks)

        if len(tasks) == 0:
            logging.debug('Not found release tasks')
            return

        logging.debug('Tasks to reporting: {}'.format(tasks))

        self._start_test_cost_reporter_tasks(tasks)

        self.Parameters.reported_release_tasks = map(lambda task: task.id, tasks)

    def _find_previously_reported_release_tasks(self):
        """
        Получаем предыдущие 20 тасок, чтобы не репортить предыдущие релизы. Пока считаем, что этого достаточно, так как
        у нас нет задачи сделать точный инструмент.

        :rtype: list of int
        """
        previous_tasks = list(sdk2.Task.find(
            type=self.type,
            status=[ctt.Status.SUCCESS, ctt.Status.FAILURE],
            input_parameters=dict(
                task_type=self.Parameters.task_type
            )
        ).limit(20).order(-sdk2.Task.id))

        logging.debug('Found previous tasks: {}'.format(previous_tasks))

        previously_reported_release_tasks = []

        for previous_task in previous_tasks:
            reported_release_tasks = previous_task.Parameters.reported_release_tasks

            if reported_release_tasks:
                previously_reported_release_tasks.extend(reported_release_tasks)

        previously_reported_release_tasks = list(set(previously_reported_release_tasks))

        logging.debug('Previously reported release tasks: {}'.format(previously_reported_release_tasks))

        return previously_reported_release_tasks

    def _find_report_release_tasks(self):
        created_from = dateutil.parser.parse(self.Parameters.created_from).isoformat()
        created_till = dateutil.parser.parse(self.Parameters.created_till).isoformat()

        found_tasks = list(sdk2.Task.find(
            hidden=True,
            type=sdk2.Task[self.Parameters.task_type],
            status=[ctt.Status.SUCCESS, ctt.Status.FAILURE, ctt.Status.RELEASING, ctt.Status.RELEASED],
            created=created_from + '..' + created_till,
            input_parameters=dict(
                release='latest',
                tests_source='nothing',
                release_machine_mode=True
            )
        ).limit(50).order(-sdk2.Task.id))  # 50 releases should be enough for everyone

        logging.debug('Found report release tasks: {}'.format(found_tasks))

        tasks_index = {}

        for task in found_tasks:
            key = self._format_report_release_description(task.Parameters.component_name, task.Parameters.release_number)

            if key in tasks_index:
                logging.debug('Filter duplicate release "{key}" ({id})'.format(key=key, id=task.id))
            else:
                tasks_index[key] = task

        return tasks_index.values()

    def _start_test_cost_reporter_tasks(self, release_tasks):
        subtasks = []

        for release_task in release_tasks:
            release_version_description = self._format_report_release_description(
                component=release_task.Parameters.component_name,
                number=release_task.Parameters.release_number
            )

            subtask_id = release_task.Context.subtask_id
            subtask = sdk2.Task[subtask_id]

            logging.debug('Start tasks for subtask: {}'.format(subtask_id))

            subtask = SandboxCiTestCostReporter(
                self,
                description='Report release ({})'.format(release_version_description),
                project_github_owner=subtask.Parameters.project_github_owner,
                project_github_repo=subtask.Parameters.project_github_repo,
                mode='release',
                release_version=subtask.Parameters.project_git_base_ref,
                release_version_description=release_version_description,
                skipped=True
            ).enqueue()

            subtasks.append(subtask)

        return subtasks

    def _format_report_release_description(self, component, number):
        return '{}/{}'.format(component, number)
