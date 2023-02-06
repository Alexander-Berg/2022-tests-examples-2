# coding=utf-8

import os
from sandbox import sdk2
from sandbox.common.types.misc import DnsType
from sandbox.projects.resource_types import TASK_CUSTOM_LOGS
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.artifacts import list_artifacts, archive_artifacts
from sandbox.projects.ofd.common import VcsParameters


class OfdRuntimeRunTests(BaseConsoleMixin, sdk2.Task):
    """
    Запускает ofd-runtime тесты
    """

    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64

    class Context(sdk2.Task.Context):
        artifact_resource_id = None

    class Parameters(sdk2.Task.Parameters):
        vcs_block = VcsParameters()
        container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=806900009,
            required=True,
        )
        apply_revision = sdk2.parameters.Bool("Собрать из ревизии", default=False)
        with apply_revision.value[True]:
            revision_id = sdk2.parameters.String("Revision id", default="", description="Номер ревизии в аркадии")
        apply_patch = sdk2.parameters.Bool("Применить патч", default=False)
        with apply_patch.value[True]:
            review_id = sdk2.parameters.List("Review id", default=[], description="ID ревью в аркануме")

    def on_execute(self):
        with self.memoize_stage.build(commit_on_entrance=False):
            with sdk2.helpers.ProgressMeter("Checkout"):
                self._checkout_branch()
            if self.Parameters.apply_patch:
                with sdk2.helpers.ProgressMeter("Patch"):
                    for rid in self.Parameters.review_id:
                        sdk2.vcs.svn.Arcadia.fetch_patch('rb:{}'.format(rid), self._work_dir())
                        sdk2.vcs.svn.Arcadia.apply_patch_file(self._work_dir(), os.path.join(self._work_dir(), 'arcadia.patch'), is_zipatch=True)
            try:
                with sdk2.helpers.ProgressMeter("Run tests"):
                    self._run_tests()
            finally:
                with sdk2.helpers.ProgressMeter("Archive Artifacts"):
                    archive_artifacts(self, self._work_dir(), "tests_logs", TASK_CUSTOM_LOGS,
                                            *list_artifacts(self._work_dir(), '\.log$'))

    def _work_dir(self, *path):
        return str(self.path("wd", *path))

    def _checkout_branch(self):
        project_url = os.path.join(self.Parameters.arcadia_url, self.Parameters.arcadia_path)
        if self.Parameters.apply_revision:
            sdk2.vcs.svn.Arcadia.checkout(project_url, os.path.join(self._work_dir(), 'ofd/runtime'), revision=self.Parameters.revision_id)
        else:
            sdk2.vcs.svn.Arcadia.checkout(project_url, os.path.join(self._work_dir(), 'ofd/runtime'))

    def _run_tests(self):
        self._execute_script('''#!/bin/bash -xe
python3.5 -mvenv venv && \
source ./venv/bin/activate && \
./venv/bin/pip install pip==18.1 --upgrade -i https://pypi.yandex-team.ru/simple && \
./venv/bin/pip install --upgrade setuptools && \
./venv/bin/pip install pytest-runner && \
./venv/bin/pip install pytest==3.0.5 && \
./venv/bin/pip install flake8==3.0.0 && \
./venv/bin/pip install pytest_asyncio==0.5.0 && \
./venv/bin/pip install asynctest && \
./venv/bin/pip install pytest-xdist==1.24.0 && \
./venv/bin/pip install pytest-forked==0.2 && \
./venv/bin/pip install crcmod==1.7 && \
cd ofd/runtime && \
../../venv/bin/pip install . && \
cd ../../
''', cwd=self._work_dir())
        self._execute_script('''#!/bin/bash -xe
source ./venv/bin/activate && \
cd ofd/runtime && \
./venv/bin/pytest tests/unit > tests.log 2>&1
cd ../../
''', cwd=self._work_dir())
        self._execute_script('''#!/bin/bash -xe
./venv/bin/flake8 ofd/runtime/ofd > flake.log 2>&1
''', cwd=self._work_dir())
