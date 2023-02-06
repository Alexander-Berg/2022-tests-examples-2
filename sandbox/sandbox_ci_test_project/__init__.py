# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseMetaTask
from sandbox.projects.sandbox_ci.sandbox_ci_test_project_failure import SandboxCiTestProjectFailure
from sandbox.projects.sandbox_ci.sandbox_ci_test_project_success import SandboxCiTestProjectSuccess


class SandboxCiTestProject(BaseMetaTask):
    """
    Тестовый проект для приёмки изменений в сервисе Merge Queue (search-interfaces/merge-queue-test-project)
    """
    project_name = 'merge-queue-test-project'

    github_context = u'[Sandbox CI] Автосборка'

    def declare_subtasks(self):
        failure_subtask = self.create_failure_subtask()
        success_subtask = self.create_success_subtask()

        return [
            failure_subtask,
            success_subtask,
        ]

    def create_failure_subtask(self):
        return self.meta.declare_subtask(
            task_type=SandboxCiTestProjectFailure,
        )

    def create_success_subtask(self):
        return self.meta.declare_subtask(
            task_type=SandboxCiTestProjectSuccess,
        )
