# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseTask


class SandboxCiTestProjectSuccess(BaseTask):
    """
    Всегда зелёная проверка для тестирования MQ
    """
    project_name = 'merge-queue-test-project'

    github_context = u'[Sandbox CI] Зелёная проверка'

    def execute(self):
        pass
