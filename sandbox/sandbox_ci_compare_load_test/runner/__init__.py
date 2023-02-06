# -*- coding: utf-8 -*-

import os
import logging
from sandbox import sdk2
from sandbox.common.utils import singleton_property
from sandbox.common.errors import TaskFailure
from sandbox.common.types import task as ctt
from sandbox.common.types import resource as ctr
from sandbox.common.types import misc as ctm
import sandbox.common.types.client as ctc
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.projects.sandbox_ci import parameters, managers
from sandbox.projects.sandbox_ci.task import ManagersTaskMixin
from sandbox.projects.sandbox_ci.resources import HermioneSkipTestsList
from sandbox.projects.sandbox_ci.sandbox_ci_hermione import SandboxCiHermione
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.web4 import SandboxCiCompareLoadTestWeb4
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test import runner_parameters
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_builder import ReportsBuilder
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.quota import QuotaManager

PROJECT_TASKS_MAP = {
    'web4': {
        'owner': 'serp',
        'repo': 'web4',
        'task_type': SandboxCiHermione,
        'test_tool': 'hermione'
    }
}

TAGS = {
    'full': 'FULL',
    'half': 'HALF'
}

FULL_LOAD_TASK_CNT = 2


class SandboxCiCompareLoadTestRunner(TasksResourceRequirement, ManagersTaskMixin, sdk2.Task):
    """
        Запуск нагрузочных тасок
    """
    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Parameters):
        _container = parameters.environment_container()

        project = sdk2.parameters.String(
            'Проект',
            description='Проект, для которого запустится нагрузочное тестирование',
            default='web4',
            choices=[
                ('web4', 'web4'),
            ],
        )

        data_center = parameters.data_center()
        quota_block = runner_parameters.QuotaParameters
        tests_block = runner_parameters.TestsParameters

        tests_source = sdk2.parameters.RadioGroup(
            'Режим тестирования',
            description='task id, последний прогон из dev-а или коммит',
            choices=(
                ('task_id', 'task_id'),
                ('dev', 'dev'),
                (u'Указать', 'specify'),
            ),
            sub_fields={'specify': ['tests_hash'], 'task_id': ['task_id']},
            default='dev',
            required=True,
        )
        tests_hash = sdk2.parameters.String('Хэш коммита', required=True)
        task_id = sdk2.parameters.String('Task ID', required=True)

        node_js = parameters.NodeJsParameters

    class Context(sdk2.Context):
        reports = {}

    def working_path(self, *args):
        return self.path(*args)

    @singleton_property
    def quota(self):
        return QuotaManager(self)

    @property
    def grid_url(self):
        name = self.Parameters.quota_name
        password = self.vault.read('grid_password_from_quota_{}'.format(name), 'SANDBOX_CI_SEARCH_INTERFACES')

        return 'http://{}:{}@sg.yandex-team.ru:4444/wd/hub'.format(name, password)

    @property
    def browser_id(self):
        return self.Parameters.browser_id

    @property
    def browser_version(self):
        return self.Parameters.browser_version

    @property
    def browser_total(self):
        url = self.grid_url
        logging.debug('grid url: {}'.format(url))

        return self.quota.get_total(url)

    @property
    def data_center(self):
        return self.Parameters.data_center

    def on_save(self):
        super(SandboxCiCompareLoadTestRunner, self).on_save()
        self.Requirements.client_tags = ctc.Tag.MAN

    def on_execute(self):
        os.environ['TESTCOP_AUTH_TOKEN'] = self.vault.read('env.TESTCOP_AUTH_TOKEN')

        dev_task = self.__get_dev_task(PROJECT_TASKS_MAP[self.Parameters.project])
        skip_list_id = self.__get_skip_list_id()
        total = self.browser_total
        logging.debug('total: {}'.format(total))
        half_capacity = int(total) / FULL_LOAD_TASK_CNT

        with self.memoize_stage.create_half_task:
            compare_load_task = self.__create_compare_load_task(
                    dev_task,
                    skip_list_id,
                    half_capacity,
                    [TAGS['half']]
                )

            self.__run_compare_load_tasks(compare_load_task)

        with self.memoize_stage.create_full_task:
            compare_load_tasks = []

            for _ in range(FULL_LOAD_TASK_CNT):
                compare_load_tasks.append(self.__create_compare_load_task(
                    dev_task,
                    skip_list_id,
                    half_capacity,
                    [TAGS['full']]
                ))

            self.__run_compare_load_tasks(compare_load_tasks)

    def on_finish(self, prev_status, status):
        super(SandboxCiCompareLoadTestRunner, self).on_finish(prev_status, status)

        reports_builder = ReportsBuilder(self)
        subtasks = self.find(SandboxCiCompareLoadTestRunner, status=ctt.Status.Group.FINISH)

        for subtask in subtasks:
            reports_builder.add_reports(subtask)

        self.Context.reports = reports_builder.reports

    @sdk2.header()
    def header(self):
        return self.Context.reports

    def __create_compare_load_task(self, dev_task, skip_list_id, browser_total, tags):
        return SandboxCiCompareLoadTestWeb4(
                self,
                browser_id=self.Parameters.browser_id,
                browser_version=self.Parameters.browser_version,
                custom_opts=self.Parameters.custom_opts,
                data_center=self.Parameters.data_center,
                grid_url=self.grid_url,
                quota_name=self.Parameters.quota_name,
                session_cnt=browser_total,
                skip_list_id=skip_list_id,
                tests_dev_task=dev_task,
                tags=tags
            ).enqueue()

    def __run_compare_load_tasks(self, tasks):
        raise sdk2.WaitTask(tasks, statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

    def __get_dev_task(self, project_obj):
        if self.Parameters.tests_source == 'task_id':
            self.Context.dev_task_id = self.Parameters.task_id

            return sdk2.Task.find(id=self.Parameters.task_id).first()

        input_parameters = dict(
            project_build_context='dev',
            project_github_owner=project_obj['owner'],
            project_github_repo=project_obj['repo'],
        )

        if self.Parameters.tests_source == 'specify':
            input_parameters.update(project_github_commit=self.Parameters.tests_hash)

        logging.debug('Searching for task with parameters: {}'.format(input_parameters))

        params = dict()
        if self.Context.dev_task_id is not ctm.NotExists:
            params.update(id=self.Context.dev_task_id)

        task = sdk2.Task.find(
            type=project_obj['task_type'],
            input_parameters=input_parameters,
            status=ctt.Status.Group.FINISH,
            **params
        ).first()

        if task is None:
            raise TaskFailure('Could not find test task for running')

        self.Context.dev_task_id = task.id
        return task

    def __get_skip_list_id(self):
        if self.Parameters.skip_list_id:
            return self.Parameters.skip_list_id

        if self.Context.skip_list_id is not ctm.NotExists:
            return self.Context.skip_list_id

        skip_list_id = self.skip_list.get_id(
            project=self.Parameters.project,
            tool=PROJECT_TASKS_MAP[self.Parameters.project]['test_tool'],
        )

        if skip_list_id is None:
            raise TaskFailure('Could not find skip list id')

        self.Context.skip_list_id = skip_list_id

        return skip_list_id
