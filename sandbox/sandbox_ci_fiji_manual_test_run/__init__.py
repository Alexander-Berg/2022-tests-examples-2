# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseManualTestRunTask


class SandboxCiFijiManualTestRun(BaseManualTestRunTask):
    """Создание ручного прогона тестов для fiji"""

    name = 'SANDBOX_CI_FIJI_MANUAL_TEST_RUN'

    project_name = 'fiji'
    testpalm_project_id = 'fiji'
    fail_on_deps_fail = False
    needed_artifact_types = ('fiji',)
