# -*- coding: utf-8 -*-

import os
from sandbox import sdk2
import logging

from sandbox.common.types import misc as ctm
from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.utils.context import GitRetryWrapper, Node
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.projects.sandbox_ci.task.ManagersTaskMixin import ManagersTaskMixin

TESTCOP_CLI_VERSION = "1.0.0"


class SandboxCiTestcopEnableTests(TasksResourceRequirement, ManagersTaskMixin, sdk2.Task):
    """
        Таск для включения тестов через testcop-cli
    """
    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64
        disk_space = 1024

    class Parameters(sdk2.Parameters):
        description = 'Включаем тесты в testcop'

        projects = sdk2.parameters.String(
            'Projects',
            required=True,
            description='Проекты, для которых включаем тесты (разделитель - запятая)'
        )

        branch = sdk2.parameters.String(
            'Branch',
            required=True,
            description='Ветка, для которой включаем тесты'
        )

        pullRequestNumber = sdk2.parameters.String(
            'Pull request number',
            required=False,
            description='Номер pull request-а, из заголовка которого будут взяты тикеты для включения тестов'
        )

        mergeCommitTitle = sdk2.parameters.String(
            'Merge commit title',
            required=False,
            description='Заголовок merge commit-а, из которого будут взяты тикеты для включения тестов'
        )

        testcopHost = sdk2.parameters.String(
            "Testcop host",
            required=False,
            description='По умолчанию https://testcop.si.yandex-team.ru'
        )

        with sdk2.parameters.Group('Other') as other_block:
            _container = parameters.environment_container()

        node_js = parameters.NodeJsParameters

    lifecycle_steps = {
        'npm_install': 'npm i @yandex-int/testcop-cli@{cli_version} --production --registry=http://npm.yandex-team.ru',
        'enable-tests': 'npx testcop-cli enable --projects="{projects}" --branch="{branch}" --pull-request-number="{pr_number}" --merge-commit-title="{merge_commit_title}"',
    }

    def on_prepare(self):
        if self.Parameters.testcopHost:
            os.environ['TESTCOP_HOST'] = self.Parameters.testcopHost

        merge_commit_title = self.Parameters.mergeCommitTitle

        if merge_commit_title:
            merge_commit_title = self.Parameters.mergeCommitTitle.replace('"', '\\\"')

        self.lifecycle.update_vars(
            cli_version=TESTCOP_CLI_VERSION,
            projects=self.Parameters.projects,
            branch=self.Parameters.branch,
            pr_number=self.Parameters.pullRequestNumber,
            merge_commit_title=merge_commit_title,
        )

    def on_execute(self):
        os.environ['TESTCOP_AUTH_TOKEN'] = self.vault.read('env.TESTCOP_AUTH_TOKEN')

        with GitRetryWrapper(), Node(self.Parameters.node_js_version):
            logging.info('Testcop-cli install')
            self.lifecycle('npm_install')

            logging.info('Testcop-cli start')
            self.lifecycle('enable-tests')
            logging.info('Testcop-cli finish')

    """
    Наличие свойста "project_name" и методов "project_dir" "working_path" "project_path"
    обусловлено желанием по максимуму использовать существующую функциональность
    из sandbox.projects.sandbox_ci.managers. Но код модулей managers предполагает использование
    совместно с sandbox.projects.sandbox_ci.task.BaseTask. И чтобы реиспользовать код пришлось
    добавить и переопределить вышеуказанные свойства и методы в данной задаче.
    """
    @property
    def project_name(self):
        return ''

    @property
    def project_dir(self):
        return self.working_path()

    def working_path(self, *args):
        return self.path(*args)

    def project_path(self, *args):
        return self.project_dir.joinpath(*args)
