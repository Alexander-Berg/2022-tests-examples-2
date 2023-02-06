# coding=utf-8

import os
from sandbox import sdk2
from sandbox.common.types.misc import DnsType
from sandbox.projects.resource_types import TASK_CUSTOM_LOGS
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.artifacts import list_artifacts, archive_artifacts
from sandbox.projects.ofd.common import VcsParameters


class OfdBackendRunTests(BaseConsoleMixin, sdk2.Task):
    """
    Запускает ofd-backend тесты
    """

    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64
        disk_space = 1024

    class Context(sdk2.Task.Context):
        artifact_resource_id = None

    class Parameters(sdk2.Task.Parameters):
        vcs_block = VcsParameters()
        container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=888715431,
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
                wd = self._work_dir()
                self._execute_script('''#!/bin/bash -xe \
sleep 5
echo "!1" > cwd_list.log 2>&1
ls -al {}/ofd/backend/* >> cwd_list.log 2>&1
echo "!2" >> cwd_list.log 2>&1
cp -rfv {}/ofd/backend/* {}/ >> cwd_list.log 2>&1
echo "!3" >> cwd_list.log 2>&1
ls -al {}/* >> cwd_list.log 2>&1
'''.format(wd, wd, wd, wd), cwd=wd)
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
        project_url = os.path.join(self.Parameters.vcs_block.arcadia_url, self.Parameters.vcs_block.arcadia_path)
        if self.Parameters.apply_revision:
            sdk2.vcs.svn.Arcadia.checkout(project_url, self._work_dir(), revision=self.Parameters.revision_id)
        else:
            sdk2.vcs.svn.Arcadia.checkout(project_url, self._work_dir())

    def _run_tests(self):
        self._execute_script('''#!/bin/bash -xe
python3.4 -mvenv ../myenv > install.log 2>&1 && \
../myenv/bin/pip install pip==18.1 --upgrade -i https://pypi.yandex-team.ru/simple >> install.log 2>&1 && \
../myenv/bin/pip install cython >> install.log 2>&1
../myenv/bin/pip install nose >> install.log 2>&1
../myenv/bin/pip install flake8==3.0.0 >> install.log 2>&1
../myenv/bin/pip install -r requirements.txt >> install.log 2>&1
../myenv/bin/pip install . >> install.log 2>&1
''', cwd=self._work_dir())
        self._execute_script('''#!/bin/bash -xe
PYTHONPATH="" ../myenv/bin/pytest tests/module tests/test_ofd_app -vv -m "not service" -r s > tests.log 2>&1
''', cwd=self._work_dir())
        self._execute_script('''#!/bin/bash -xe
../myenv/bin/flake8 --config=".flake8" > flake.log 2>&1
''', cwd=self._work_dir())
