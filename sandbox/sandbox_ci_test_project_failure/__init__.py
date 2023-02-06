# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseTask


class SandboxCiTestProjectFailure(BaseTask):
    """
    Всегда красная проверка для тестирования MQ
    """
    project_name = 'merge-queue-test-project'

    github_context = u'[Sandbox CI] Красная проверка'

    def execute(self):
        raise Exception('This task always fails by design')
