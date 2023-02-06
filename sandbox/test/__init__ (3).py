# -*- coding: utf-8 -*-
import os

import subprocess
import sandbox.common.types.misc as ctm
from sandbox import common, sdk2
from sandbox.projects.metrika.utils.artifacts import archive_artifacts_inplace
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.vcs import checkout
from sandbox.sandboxsdk import environments
from sandbox.projects.metrika.utils.parameters import VcsParameters, LastPeasantContainerResource


class TestMobileadsMonitoringJob(sdk2.Task, BaseConsoleMixin):
    WORKING_DIR = 'wd'

    class Requirements(sdk2.Task.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        container = LastPeasantContainerResource('Environment container resource', required=True)
        kill_timeout = 36000
        vcs_block = VcsParameters()

        user_name = sdk2.parameters.String('User name',
                                           description='Имя пользователя, от имени которого '
                                                       'будут делаться запросы в кликхаус',
                                           required=False,
                                           default='robot-patrick')

        vault_owner = sdk2.parameters.String('Private key vault onwer',
                                             description='Имя группы/пользователя, владельца секрета, '
                                                         'в котором хранится приватный ключ',
                                             required=True,
                                             default='YANDEX_MOBILEADS_SDK')

        password_vault_name = sdk2.parameters.String('Password vault name',
                                                     description='Имя секрета в котором хранится пароль',
                                                     required=False)

        private_key_vault_name = sdk2.parameters.String('Private key vault name',
                                                        description='Имя секрета, '
                                                                    'в котором хранится приватный ssh ключ',
                                                        required=True)

        statface_token_vault_name = sdk2.parameters.String('Statface token vault name',
                                                           description='Имя секрета, в котором хранится statface-token',
                                                           required=False)

        startreck_token_vault_name = sdk2.parameters.String('Startreck token vault onwer',
                                                            description='Имя секрета, '
                                                                        'в котором хранится startreck-token',
                                                            required=False)

        script = sdk2.parameters.String('Script to run', required=True)

        with sdk2.parameters.Group('Filling monitoring') as filling_monitoring:
            date_from = sdk2.parameters.String('Monitoring fill start date',
                                               description='Дата начала заполнения монитринга (напр. 2020-01-01)',
                                               required=False)

            date_to = sdk2.parameters.String('Monitoring fill end date',
                                             description='Дата конца заполнения монитринга (напр. 2020-12-31)',
                                             required=False)

        with sdk2.parameters.Group('Reporting') as reporting:
            success_notification = sdk2.parameters.Bool('Send notification in case of task success', default=False)
            failure_notification = sdk2.parameters.Bool('Send notification in case of task failure', default=False)
            report_dir = sdk2.parameters.String('Directory where report will be located', required=False)
            report_name = sdk2.parameters.String('Notification report name in report dir')
            recipients = sdk2.parameters.List('Report recipients', default=['adlib-monitoring'])

    def on_execute(self):
        with sdk2.ssh.Key(self, self.Parameters.vault_owner, self.Parameters.private_key_vault_name):
            with sdk2.helpers.ProgressMeter('Checkout'):
                self._checkout_branch()
            with sdk2.helpers.ProgressMeter('Run script'):
                env = os.environ.copy()
                if self.Parameters.user_name and self.Parameters.password_vault_name:
                    env['ch_user'] = self.Parameters.user_name
                    env['ch_pass'] = sdk2.Vault.data(self.Parameters.vault_owner, self.Parameters.password_vault_name)

                if self.Parameters.statface_token_vault_name:
                    env['STATFACE_TOKEN'] = sdk2.Vault.data(self.Parameters.vault_owner,
                                                            self.Parameters.statface_token_vault_name)

                if self.Parameters.startreck_token_vault_name:
                    env['STARTREK_TOKEN'] = sdk2.Vault.data(self.Parameters.vault_owner,
                                                            self.Parameters.startreck_token_vault_name)

                arguments = self._get_arguments()

                with environments.VirtualEnvironment() as venv:
                    self.__install_requirements(venv)

                    cmd = [venv.executable]
                    if self.Parameters.script.endswith('.py'):
                        cmd.append(os.path.join(self._work_dir(), self.Parameters.script))
                    else:
                        cmd.extend(['-m', self.Parameters.script])

                    with sdk2.helpers.ProcessLog(self, logger="script-log") as pl:
                        subprocess.check_call(
                            cmd + arguments,
                            stdout=pl.stdout,
                            stderr=pl.stdout,
                            cwd=self._work_dir(),
                            env=env)

            if self.Parameters.report_dir:
                with sdk2.helpers.ProgressMeter('Archive artifacts'):
                    report_dir = os.path.join(self._work_dir(), self.Parameters.report_dir)
                    report_dir_resource_id = archive_artifacts_inplace(self, report_dir)
                    self.Context.report_dir_resource_id = report_dir_resource_id

    def __install_requirements(self, venv):
        venv.pip('pip==19.1 setuptools==41.0.1')
        venv.pip('requests==2.23.0')
        venv.pip('numpy==1.16.4')
        venv.pip('gitpython==2.1.15')
        venv.pip('play-scraper==0.6.0')
        venv.pip('pandas==0.24.2')

    def _get_arguments(self):
        arguments = []
        if self.Parameters.date_from:
            arguments.extend(['--date_from', self.Parameters.date_from])
        if self.Parameters.date_to:
            arguments.extend(['--date_to', self.Parameters.date_to])
        return arguments

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
            subject='Monitoring report',
            body=body,
            recipients=self.Parameters.recipients,
            transport=common.types.notification.Transport.EMAIL,
            urgent=False
        )
