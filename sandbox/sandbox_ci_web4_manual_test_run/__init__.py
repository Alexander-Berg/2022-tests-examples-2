# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseManualTestRunTask


class SandboxCiWeb4ManualTestRun(BaseManualTestRunTask):
    """Создание ручного прогона тестов для web4"""

    name = 'SANDBOX_CI_WEB4_MANUAL_TEST_RUN'

    project_name = 'web4'
    testpalm_project_id = 'serp-js'
    fail_on_deps_fail = False
    needed_artifact_types = ('web4', 'hermione', 'features')
