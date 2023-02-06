# -*- coding: utf-8 -*-

import logging
import json

from sandbox import sdk2

from sandbox.common.types import resource as ctr
from sandbox.common.errors import TaskFailure
from sandbox.common.utils import singleton_property

from sandbox.sandboxsdk.errors import SandboxSubprocessError

from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.sandbox_ci.utils.context import Debug
from sandbox.projects.sandbox_ci.task.BaseTask import BaseTask
from sandbox.projects.sandbox_ci.utils.process import run_process


class SandboxCiTestidsForFlags(BaseTask):
    """Конвертирует флаги TestPalm-сьютов в эксперименты (testid)"""

    class Requirements(BaseTask.Requirements):
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Parameters):
        project_name = sdk2.parameters.String(
            'Project name',
            default='web4',
            required=True,
        )

        with sdk2.parameters.Group('Flow') as flow_block:
            ignore_script_errors = sdk2.parameters.Bool(
                'Ignore script errors',
                description=u'Игнорировать ошибки выполнения скрипта.',
                default=False,
            )

        with sdk2.parameters.Group('TestPalm') as testpalm_block:
            testpalm_project_name = sdk2.parameters.String(
                'TestPalm project name',
                description=u'Полное имя проекта в TestPalm (например, serp-js-100500)',
                required=True,
            )

        with sdk2.parameters.Group('Script parameters') as script_block:
            is_dry_run = sdk2.parameters.Bool(
                'Dry run',
                description=u'Для всех найденных флагов задаётся test-id, равный «1». При этом ресурс не создаётся.',
                default=False,
            )
            author = sdk2.parameters.String(
                'Author',
                description=u'Пользователь, от имени которого создаются эксперименты. Токен берётся из переменной окружения AB_EXPERIMENTS_TOKEN.',
                default='robot-serp-bot'
            )
            foreverdata_condition = sdk2.parameters.Bool(
                'Set condition to foreverdata',
                description='Устанавливать CONDITION cgi.text = "foreverdata" в test-id с флагом foreverdata',
                default=True,
            )
            config = sdk2.parameters.JSON(
                'Config',
                description='Конфиг'
            )

        base_params = BaseTask.Parameters

    github_context = u'[Sandbox CI] Конвертация флагов в эксперименты'

    @singleton_property
    def project_name(self):
        return self.Parameters.project_name

    skip_ci_scripts_checkout = False

    def execute(self):
        errors = []

        try:
            self.create_from_testpalm()
        except TaskFailure as e:
            errors.append(e)

        # Удалить после FEI-17530
        if errors and self.Parameters.ignore_script_errors is False:
            raise TaskFailure('\n'.join([str(error) for error in errors]))

    def create_from_testpalm(self):
        config = self.get_testids_for_flags_config_path()
        logging.debug('config for create-from-testpalm: {config}'.format(config=config))

        script = 'create-from-testpalm {project} {author} {foreverdata_condition} {dry} {config}'.format(
            project=self.Parameters.testpalm_project_name,
            author=self.Parameters.author,
            config='--config={c}'.format(c=config) if config else '',
            foreverdata_condition='--set-condition-to-foreverdata' if self.Parameters.foreverdata_condition else '',
            dry='--dry' if self.Parameters.is_dry_run else '',
        )

        self.run_script(script)

    def get_testids_for_flags_config_path(self):
        if not self.Parameters.config:
            return None

        path = str(self.working_path('testids-for-flags-config.json'))

        with open(path, 'w') as config_file:
            json.dump(self.Parameters.config, config_file)

        logging.debug('config json saved to {path}'.format(path=path))

        return path

    def run_script(self, args, opts={}):
        cmd = './script/testid-cli.js {}'.format(args)

        with Debug('serp:testid:*'):
            try:
                return self.scripts.run_js(cmd, *opts)
            except SandboxSubprocessError:
                raise TaskFailure('{} failed'.format(cmd))
