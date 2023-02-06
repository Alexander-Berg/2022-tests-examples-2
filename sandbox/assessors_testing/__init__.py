# -*- coding: utf-8 -*-
import os

import sandbox.common.types.misc as ctm
from sandbox import common, sdk2
from sandbox.projects.metrika.utils.artifacts import archive_artifacts_inplace
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.parameters import VcsParameters, LastPeasantContainerResource
from sandbox.projects.metrika.utils.vcs import checkout


class MobileadsAssessorsTestJob(sdk2.Task, BaseConsoleMixin):
    WORKING_DIR = 'wd'

    class Requirements(sdk2.Task.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        container = LastPeasantContainerResource("Environment container resource", required=True)
        kill_timeout = 36000
        vcs_block = VcsParameters()
        test_project = sdk2.parameters.String("Test project name",
                                              description="ADLIB or PCODE or ADSDK",
                                              required=True)

        testpalm_environment = sdk2.parameters.String("Testpalm environment",
                                                      description="Platforms for testing: Android && Sniffer OR "
                                                                  "iOS && Sniffer",
                                                      required=True)

        platform = sdk2.parameters.String("Test platform",
                                          description="iOS or Android",
                                          required=True)

        testpalm_project = sdk2.parameters.String("Testpalm project",
                                                  required=True,
                                                  default="adlib")

        testplan_id = sdk2.parameters.String("Testplan id",
                                             description="Testplan id from testpalm",
                                             required=True)

        overlap = sdk2.parameters.String("Number of overlaps",
                                             default="3",
                                             description="Indicates how much runs for each test suite will be created",
                                             required=True)

        hitman_process = sdk2.parameters.String("Hitman process",
                                                default="testing_inapp_pcode",
                                                required=True)

        hitman_requester = sdk2.parameters.String("Requester",
                                                  description="This value will be passed as REQUESTER parameter "
                                                              "to hitman process",
                                                  required=True,
                                                  default="robot-patrick")

        vault_owner = sdk2.parameters.String("Private key vault onwer",
                                             description="Group/user name owner of secret in vault",
                                             required=True,
                                             default="YANDEX_MOBILEADS_SDK")

        private_key_vault_name = sdk2.parameters.String("Private key vault name",
                                                        description="Vault name where private ssh key stored",
                                                        required=True)

        startrek_token_vault_name = sdk2.parameters.String("Startrek token vault name",
                                                           required=True,
                                                           default="robot-patrick-startreck-token")

        hitman_token_vault_name = sdk2.parameters.String("Hitman token vault name",
                                                         required=True,
                                                         default="robot-patrick-hitman-token")

        testpalm_token_vault_name = sdk2.parameters.String("Testpalm token vault name",
                                                           required=True,
                                                           default="robot-patrick-testpalm-token")
        report_dir = sdk2.parameters.String("Directory where report will be located", required=False)

        script = sdk2.parameters.String("Script to run", required=True, default="assessors_testing.py")

        with sdk2.parameters.Group('Reporting') as star_track_block:
            success_notification = sdk2.parameters.Bool('Send notification in case of task success', default=False)
            failure_notification = sdk2.parameters.Bool('Send notification in case of task failure', default=False)
            report_name = sdk2.parameters.String('Notification report name in report dir')
            recipients = sdk2.parameters.List('Report recipients', default=[])

    def on_execute(self):
        with sdk2.ssh.Key(self, self.Parameters.vault_owner, self.Parameters.private_key_vault_name):
            with sdk2.helpers.ProgressMeter("Checkout"):
                self._checkout_branch()
            with sdk2.helpers.ProgressMeter("Run script"):
                env = os.environ.copy()
                arguments = self._get_arguments()
                cmd = ['python']
                if self.Parameters.script.endswith('.py'):
                    cmd.append(os.path.join(self._work_dir(), self.Parameters.script))
                else:
                    cmd.extend(['-m', self.Parameters.script])
                self._execute_shell_and_check(
                    cmd + arguments,
                    cwd=self._work_dir(),
                    env=env,
                    verbose=False
                )

            if self.Parameters.report_dir:
                with sdk2.helpers.ProgressMeter("Archive artifacts"):
                    report_dir = os.path.join(self._work_dir(), self.Parameters.report_dir)
                    report_dir_resource_id = archive_artifacts_inplace(self, report_dir)
                    self.Context.report_dir_resource_id = report_dir_resource_id

    def on_success(self, prev_status):
        if self.Parameters.success_notification:
            self._send_notification('success')

    def on_failure(self, prev_status):
        if self.Parameters.failure_notification:
            self._send_notification('failure')

    def _checkout_branch(self):
        checkout(self.Parameters.vcs_block, self._work_dir())

    def _work_dir(self, *path):
        return str(self.path(self.WORKING_DIR, *path))

    def _get_arguments(self):
        startrek_token = sdk2.Vault.data(self.Parameters.vault_owner, self.Parameters.startrek_token_vault_name)
        testpalm_token = sdk2.Vault.data(self.Parameters.vault_owner, self.Parameters.testpalm_token_vault_name)
        hitman_token = sdk2.Vault.data(self.Parameters.vault_owner, self.Parameters.hitman_token_vault_name)
        arguments = []
        arguments.extend(["--startrek_token", startrek_token])
        arguments.extend(["--startrek_platform", self.Parameters.platform])
        arguments.extend(["--testpalm_token", testpalm_token])
        arguments.extend(["--testpalm_project", self.Parameters.testpalm_project])
        arguments.extend(["--test_project", self.Parameters.test_project])
        arguments.extend(["--hitman_token", hitman_token])
        arguments.extend(["--hitman_requester", self.Parameters.hitman_requester])
        arguments.extend(["--hitman_process", self.Parameters.hitman_process])
        arguments.extend(["--testplan", self.Parameters.testplan_id])
        arguments.extend(["--environment", self.Parameters.testpalm_environment])
        arguments.extend(["--overlap", self.Parameters.overlap])
        return arguments

    def _get_email_body(self, status):
        body = 'Task: {}\n'.format(self._get_task_url())
        body += 'Task status: {}\n'.format(status)
        if self.Parameters.report_dir and self.Parameters.report_name:
            report_url = self._get_report_url()
            body += 'Report: {}'.format(report_url)
        return body

    def _get_task_url(self):
        return 'https://sandbox.yandex-team.ru/task/{}'.format(self.id)

    def _get_report_url(self):
        url_template = 'https://proxy.sandbox.yandex-team.ru/task/{task_id}/{wd}/{report_dir}/{report_name}'
        report_url = url_template.format(
            task_id=self.id,
            wd=self.WORKING_DIR,
            report_dir=self.Parameters.report_dir,
            report_name=self.Parameters.report_name
        )
        return report_url

    def _send_notification(self, status):
        body = self._get_email_body(status)

        self.server.notification(
            subject='Auto assessors testing report {} {}'.format(self.Parameters.platform,
                                                                 self.Parameters.test_project),
            body=body,
            recipients=self.Parameters.recipients,
            transport=common.types.notification.Transport.EMAIL,
            urgent=False
        )
