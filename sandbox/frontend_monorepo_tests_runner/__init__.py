# -*- coding: utf-8 -*-
import copy
import json
import logging
import os
import re

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types import task as ctt
from sandbox.common.utils import singleton_property

from sandbox.projects.sandbox_ci import managers
from sandbox.projects.sandbox_ci.sandbox_ci_ab_experiments.ab_experiments_api import ABExperimentsApi
from sandbox.projects.sandbox_ci.utils.github import GitHubApi
from sandbox.projects.trendbox_ci.beta.tasks.trendbox_ci_job import TrendboxCiJob


class FrontendMonorepoTestsRunner(sdk2.Task):
    """Запуск тестов с изменениями"""

    class Parameters(sdk2.Task.Parameters):
        with sdk2.parameters.Group('What to run') as params:
            service = sdk2.parameters.String('Service', required=True)
            release_ticket = sdk2.parameters.String('Release ticket key', required=True)

            with sdk2.parameters.RadioGroup('Code version') as launch:
                launch.values['release'] = launch.Value('Latest release', default=True)
                launch.values['dev'] = launch.Value('Latest dev')

            with sdk2.parameters.RadioGroup('Tests version', sub_fields={'dev': ['tests_commit']}) as tests:
                tests.values['nothing'] = tests.Value('Dont change tests', default=True)
                tests.values['dev'] = tests.Value('Get tests from dev')
            tests_commit = sdk2.parameters.String('Commit for getting tests', description='Leave it empty if you need the latest dev')

            with sdk2.parameters.CheckGroup('Checks', required=True) as checks:
                checks.values['Hermione'] = checks.Value('Hermione (dumps)', checked=False)
                checks.values['Hermione e2e'] = checks.Value('Hermione (e2e)', checked=False)

        with sdk2.parameters.Group('Modifications') as mods_block:
            flags = sdk2.parameters.JSON('JSON with flags')
            test_id = sdk2.parameters.String('test-id')
            flags_handler = sdk2.parameters.String('Flags Handler')
            test_id_flags_paths = sdk2.parameters.List(
                'Paths to flags in the test_id context',
                description='Must be separated by a dot (e.g., MAIN.REPORT.templates)'
            )
            hermione_e2e_base_url = sdk2.parameters.String('[Hermione e2e] base url', default='https://hamster.yandex.ru')
            allow_data_flags = sdk2.parameters.Bool(
                'Allow launching with data flags',
                description=u'''It only affects tests using dumps. \
                                You can not trust the results of the test run on dumps \
                                if the data flags were set. \
                                https://wiki.yandex-team.ru/test/serp/prodtesting/#neverstochnyeflagi.''',
                default=False
            )
        
        with sdk2.parameters.Output():
            hermione_params = sdk2.parameters.JSON('Parameters for Hermione')
            hermione_e2e_params = sdk2.parameters.JSON('Parameters for Hermione e2e')

    @singleton_property
    def vault(self):
        return managers.VaultManager(self, self.owner)

    @singleton_property
    def experiments_api(self):
        token = self.vault.read('env.AB_EXPERIMENTS_TOKEN')
        return ABExperimentsApi(token)

    @singleton_property
    def github_api(self):
        token = self.vault.read('env.GITHUB_API_TOKEN')
        return GitHubApi(token)

    def on_prepare(self):
        self.init_environ()

    def init_environ(self):
        os.environ['SANDBOX_TASK_ID'] = str(self.id)

    def on_execute(self):
        self.check_params()

        flags = self.get_flags()
        flags_affecting_data = self.validate_flags(flags)

        with self.memoize_stage.create_children:
            for check in self.Parameters.checks:
                if not self.Parameters.allow_data_flags and check == 'Hermione' and flags_affecting_data:
                    logging.debug('Skipping running Hermione, because the following flags depend on data: {}'.format(
                        ', '.join(flags_affecting_data)
                    ))
                    continue

                self.set_output_params_for_job(check, flags)

            self.run_workflow()

    def check_params(self):
        if not self.Parameters.checks:
            raise TaskFailure('No checks are selected. Nothing to run.')

        if not self.Parameters.flags and not self.Parameters.test_id:
            raise TaskFailure('No flags or test_id are passed.')

        if self.Parameters.test_id and not (self.Parameters.flags_handler and self.Parameters.test_id_flags_paths):
            raise TaskFailure('Need to pass both the handler and the paths to the flags if the test_id is set.')

    def get_flags(self):
        flags = {}

        if self.Parameters.flags:
            flags.update(self.Parameters.flags)

        if self.Parameters.test_id:
            test_id = self.fetch_test_id(self.Parameters.test_id)
            flags.update(self.extract_flags_from_test_id(test_id, self.Parameters.test_id_flags_paths))

        return flags

    def fetch_test_id(self, test_id):
        try:
            config = self.experiments_api.get_test_id(test_id)
            logging.debug('Loaded configuration with test_id {} config: {}'.format(test_id, config))
        except Exception as e:
            logging.exception(e)
            raise TaskFailure('Could not load test_id {} configuration'.format(test_id))

        return json.loads(config['params'])

    def extract_flags_from_test_id(self, test_id, flags_paths):
        flags = {}
        test_id_configs = self.get_related_to_handler_test_id_configs(test_id, self.Parameters.flags_handler)

        if not test_id_configs:
            raise TaskFailure('There is no handlers with name {} in the test_id {}'.format(
                self.Parameters.flags_handler,
                self.Parameters.test_id
            ))

        for test_id_config in test_id_configs:
            context = test_id_config.get('CONTEXT', {})

            for flags_path in flags_paths:
                try:
                    flags.update(self.get_flags_by_path(context, flags_path))
                except Exception as error:
                    raise TaskFailure('Got an error while getting flags from test_id {} by path {}: {}'.format(
                        test_id,
                        flags_path,
                        error.message
                    ))

        if not flags:
            raise TaskFailure('test_id {} has no flags by paths:\n{}'.format(
                test_id,
                flags_paths
            ))

        return flags

    def get_related_to_handler_test_id_configs(self, test_id, handler):
        return list(filter(lambda test_id_config: test_id_config.get('HANDLER', None) == handler, test_id))

    def get_flags_by_path(self, context, path):
        steps = path.split('.')

        try:
            flags = reduce(dict.__getitem__, steps, context)
        except TypeError as error:
            raise Exception('test_id context has no content at the path: {}'.format(path))

        try:
            self.check_flags(flags)
        except Exception as error:
            raise Exception('Unsupported flags format at the path {}: {}'.format(path, error.message))
        return flags

    def check_flags(self, flags):
        if not isinstance(flags, dict):
            raise Exception('Flags must be contained in the object, got {}'.format(flags))

        for flag_value in flags.values():
            if isinstance(flag_value, dict) or isinstance(flag_value, list):
                raise Exception('Flag values must be pritive values, got {}'.format(flag_value))

    def validate_flags(self, flags):
        flags_wich_affect_dumps = []

        for flag_name in flags.keys():
            flag_info = self.experiments_api.get_flag(self.Parameters.flags_handler, flag_name)

            if not flag_info.get('is_used_in_frontend'):
                flags_wich_affect_dumps.append(flag_name)

        return flags_wich_affect_dumps

    def set_output_params_for_job(self, job_name, flags):
        if job_name == 'Hermione':
            self.set_output_param_for_hermione(job_name, flags)
        
        if job_name == 'Hermione e2e':
            self.set_output_param_for_hermione_e2e(job_name, flags)

    def set_output_param_for_hermione(self, job_name, flags):
        task = self.find_task(job_name)
        actual_task_workcopy = task.Parameters.trendbox_config['workcopies']['after']

        self.Parameters.hermione_params = dict(
            templates_commit=actual_task_workcopy['commit'],
            tests_commit=actual_task_workcopy['commit'] if self.Parameters.tests == 'nothing' else self.Parameters.tests_commit or 'master',
            envs=self._get_hermione_flags_env(flags) if flags else {},
            release_branch=actual_task_workcopy['branch'],
            ticket_id=self.Parameters.release_ticket
        )

    def _get_hermione_flags_env(self, flags):
        return dict(
            ARCHON_KOTIK_TEMPLATE_FLAG=json.dumps(flags)
        )

    def set_output_param_for_hermione_e2e(self, job_name, flags):
        task = self.find_task(job_name)
        actual_task_workcopy = task.Parameters.trendbox_config['workcopies']['after']

        self.Parameters.hermione_e2e_params = dict(
            templates_commit=actual_task_workcopy['commit'],
            tests_commit=actual_task_workcopy['commit'] if self.Parameters.tests == 'nothing' else self.Parameters.tests_commit or 'master',
            envs=self._get_hermione_e2e_flags_env(flags) if flags else {},
            release_branch=actual_task_workcopy['branch'],
            ticket_id=self.Parameters.release_ticket
        )

    def _get_hermione_e2e_flags_env(self, flags):
        pairs = map(lambda k: '{}={}'.format(k, flags[k]), flags.keys())
        flags_env = reduce(lambda f1, f2: f1 + ';' + f2, pairs)

        return dict(
            HERMIONE_URL_QUERY_EXP_FLAGS=flags_env,
            hermione_base_url=self.Parameters.hermione_e2e_base_url
        )

    def find_task(self, job_name):
        if self.Parameters.launch == 'release':
            return self.find_last_release_task(job_name)

        if self.Parameters.launch == 'dev':
            return self.find_last_dev_task(job_name)

    def find_last_release_task(self, job_name):
        full_job_name = '{}: release'.format(job_name)
        branch_reg_exp = 'search-interfaces/frontend@release/{}/.*'.format(self.Parameters.service)

        return self.find_last_task(full_job_name, branch_reg_exp)

    def find_last_dev_task(self, job_name):
        branch_reg_exp = 'search-interfaces/frontend@master'

        return self.find_last_task(job_name, branch_reg_exp)

    def find_last_task(self, job_name, branch_reg_exp):
        task_search_parameters = dict(
            type=TrendboxCiJob,
            description='{}.*\n.*{}'.format(job_name, branch_reg_exp),
            status=ctt.Status.Group.FINISH
        )

        logging.debug('Trying to find task with the following parameters: {}'.format(task_search_parameters))

        task = sdk2.Task.find(**task_search_parameters).first()

        if task:
            logging.debug('Found last task for {name}: {id}'.format(name=job_name, id=task.id))
            return task

        raise TaskFailure('Could not find success {task} with name {name} and branch regexp: {regexp}'.format(
            task=TrendboxCiJob,
            name=job_name,
            regexp=branch_reg_exp
        ))

    def run_workflow(self):
        owner = 'search-interfaces'
        repo = 'frontend'
        ref = 'refs/heads/flags/{}'.format(self.id)
        sha = self.github_api.get_branch(owner, repo, 'master').get('commit', {}).get('sha', None)

        self.github_api.create_ref(owner, repo, ref, sha)
