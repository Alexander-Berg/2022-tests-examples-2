# -*- coding: utf-8 -*-
from sandbox import sdk2
import re
from itertools import chain

from sandbox.common.types import task as ctt
from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.task.ManagersTaskMixin import ManagersTaskMixin
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.sandboxsdk.environments import PipEnvironment
from sandbox.projects.sandbox_ci.sandbox_ci_build_skip_tests_list.startrek_client_facade import StartrekClientFacade
from sandbox.projects.sandbox_ci.sandbox_ci_build_skip_tests_list.simple import SandboxCiBuildSkipTestsList
from sandbox.projects.sandbox_ci.utils import prioritizer

TASK_ID_PARSE_REG_EXP = re.compile('[A-Z]+-\d+')


class SandboxCiBuildSkipTestsListIntegral(TasksResourceRequirement, ManagersTaskMixin, sdk2.Task):
    """Интеграционная задача для запуска SANDBOX_CI_BUILD_SKIP_TESTS_LIST для указанных инструментов"""

    class Requirements(sdk2.Requirements):
        environments = [PipEnvironment("startrek_client")]

    class Parameters(sdk2.Task.Parameters):
        project_github_repo = sdk2.parameters.String('Github repo')
        project_github_owner = sdk2.parameters.String('Github owner')
        main_branch = sdk2.parameters.String('Main branch')
        project = sdk2.parameters.String('Project name')

        tools = sdk2.parameters.List(
            'Tools',
            description='Инструменты, для которых будет строиться список'
        )

        merge_commit = sdk2.parameters.String(
            'merge_commit title',
            description='тайтл merge_commit-а, из которого будут взяты тикеты для включения тестов'
        )

        branch = sdk2.parameters.String('Ветка, для которой будут включены тесты')
        branch_to_copy = sdk2.parameters.String(
            'Ветка, из которой надо скопировать данные в случае отсутствия данных для вышеуказанной ветки'
        )

        node_js = parameters.NodeJsParameters

    class Context(sdk2.Context):
        noncritical_errors = []

    def on_save(self):
        super(SandboxCiBuildSkipTestsListIntegral, self).on_save()
        self.Parameters.priority = prioritizer.get_priority(self)

        # correct branches
        self.Parameters.branch = self.Parameters.branch.replace('refs/heads/', '')
        self.Parameters.branch_to_copy = self.Parameters.branch_to_copy\
            .replace('refs/heads/', '')\
            .replace('refs/tags', 'release')

    def on_execute(self):
        st_client = self._get_startrek_client()
        issue_keys = TASK_ID_PARSE_REG_EXP.findall(self.Parameters.merge_commit)
        linked_issue_keys = list(chain(*map(st_client.get_linked_tasks_ids, issue_keys)))

        with self.memoize_stage.mk_subtasks(commit_on_entrance=False):
            subtasks = []

            for tool in self.Parameters.tools:
                subtasks.append(self.create_subtask(
                    tool=tool,
                    issue_keys=linked_issue_keys,
                    branch_to_copy=self.Parameters.branch_to_copy
                ))

            raise sdk2.WaitTask(
                tasks=self.meta.start_subtasks(subtasks),
                statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK
            )

    def create_subtask(self, tool, issue_keys, **kwargs):
        return self.meta.create_subtask(
            task_type=SandboxCiBuildSkipTestsList,
            priority=self.Parameters.priority,
            tool=tool,
            project=self.Parameters.project,
            project_github_repo=self.Parameters.project_github_repo,
            project_github_owner=self.Parameters.project_github_owner,
            main_branch=self.Parameters.main_branch,
            issue_keys=issue_keys,
            branch=self.Parameters.branch,
            node_js_version=self.Parameters.node_js_version,
            **kwargs
        )

    @staticmethod
    def _get_startrek_client():
        from startrek_client import Startrek, exceptions

        return StartrekClientFacade(Startrek, exceptions, sdk2.Vault.data('robot-serp-bot_startrek_token'))
