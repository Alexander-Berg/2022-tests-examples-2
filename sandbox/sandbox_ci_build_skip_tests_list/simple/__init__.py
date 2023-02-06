# -*- coding: utf-8 -*-
from sandbox import sdk2
import os
import json
import logging
import re
import shutil

from sandbox.common.types import task as ctt
from sandbox.common.types import misc as ctm
from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.task.ManagersTaskMixin import ManagersTaskMixin
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.sandbox_ci.resources import HermioneSkipTestsList
from sandbox.projects.sandbox_ci.utils import prioritizer
from sandbox.projects.sandbox_ci.utils.github import GitHubApi

PROJECTS = {
    'web4': 'serp',
    'fiji': 'mm-interfaces',
    'nerpa': 'news',
    'turbo': 'serp',
    'webx': 'serp',
    'redir-warning': 'serp',
    'chat': 'serp'
}
ARTIFACT_TYPE = 'skip-tests-list'
# TODO: remove fallback before close FEI-13517
DEV_BRANCH = 'dev'


def defaultGetKey(item):
    return u'{fullName}.{browserId}'.format(**item)


def objArrayToDict(arr, getKey=defaultGetKey):
    return dict((getKey(item), item) for item in arr)


class SandboxCiBuildSkipTestsList(TasksResourceRequirement, ManagersTaskMixin, sdk2.Task):
    """Таск сборки ресурса со списком отключенных тестов"""

    class Requirements(sdk2.Requirements):
        # in order to have access outside (for example to npm)
        dns = ctm.DnsType.DNS64
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        _container = parameters.environment_container()

        project_github_repo = sdk2.parameters.String(
            'Github repo',
            description='Название репозитория'
        )

        project_github_owner = sdk2.parameters.String(
            'GitHub owner',
            description='Название организации'
        )

        main_branch = sdk2.parameters.String(
            'Main branch',
            description='Название основной ветки',
            default=DEV_BRANCH
        )

        project = sdk2.parameters.String(
            'Project',
            required=True,
            description='Название проекта, для которого будет строиться список'
        )

        tool = sdk2.parameters.String(
            'Tool',
            required=True,
            description='Инструмент, для которого будет строиться список'
        )

        changes = parameters.JSONString(
            'Changes',
            required=False,
            description='Список тестов в формате JSON',
            default='{}'
        )

        branch = sdk2.parameters.String('Branch')
        branch_to_copy = sdk2.parameters.String(
            'Branch to copy resource from',
            description='Если для данной ветки нет ресурса, то копировать его из указанной ветки',
            default=DEV_BRANCH
        )
        issue_keys = sdk2.parameters.List(
            'Issue keys',
            description='Тикеты, по которым будут включены тесты'
        )

        node_js = parameters.NodeJsParameters

    def working_path(self, *args):
        return self.path(*args)

    def on_save(self):
        super(SandboxCiBuildSkipTestsList, self).on_save()
        self.Parameters.priority = prioritizer.get_priority(self)

    def _get_skipped_tests_with_fallback(self, branch):
        tests = self.__get_skipped_tests(branch=branch)

        if not tests and branch != self.Parameters.branch_to_copy:
            logging.info('failed to load skip-list for branch {}'.format(branch))
            tests = self.__get_skipped_tests(branch=self.Parameters.branch_to_copy)

        if not tests:
            logging.info('failed to load skip-list for branch {}'.format(self.Parameters.branch_to_copy))
            tests = self.__get_skipped_tests()

        if not tests:
            logging.info('failed to load skip-list for any branch')
            return []

        return tests

    def __get_skipped_tests(self, **kwargs):
        return self.skip_list.get_tests(
            project=self.Parameters.project,
            tool=self.Parameters.tool,
            **kwargs
        )

    def __publish_skips_resource(self, branch, issue_keys=[]):
        tests_data = self._filter_by_issue_keys(self._get_tests_data(branch), issue_keys)

        self.__publish_resource(branch, tests_data)

    def __publish_resource(self, branch, tests_data):
        """
            Создает и публикует ресурс со списком отключенных тестов
        """
        out_file = 'skip-tests-list_{}_{}_{}.json'.format(self.Parameters.tool, self.Parameters.project, branch).replace('/', '.')

        with open(out_file, 'w') as json_file:
            json_file.write(json.dumps(tests_data.values(), ensure_ascii=False).encode('utf8'))

        self.__publish_skip_list_resource(
            resource_type=SANDBOX_CI_ARTIFACT,
            type=ARTIFACT_TYPE,
            relative_path=out_file,
            branch=branch
        )

        separate_type_out_file = 'separate-type-{}'.format(out_file)
        shutil.copy2(out_file, separate_type_out_file)

        self.__publish_skip_list_resource(
            resource_type=HermioneSkipTestsList,
            relative_path=separate_type_out_file,
            branch=branch
        )

    def __publish_skip_list_resource(self, **kwargs):
        resource = self.artifacts.create_artifact_resource(
            project=self.Parameters.project,
            tool=self.Parameters.tool,
            public=True,
            ttl=365,
            **kwargs
        )

        sdk2.ResourceData(resource).ready()

    def _get_tests_data(self, branch):
        changes = objArrayToDict(json.loads(self.Parameters.changes))
        data = objArrayToDict(self._get_skipped_tests_with_fallback(branch))

        for key, value in changes.iteritems():
            if value.get('enabled'):
                data.pop(key, None)
            else:
                value.pop('enabled', None)
                data[key] = value

        return data

    def _filter_by_issue_keys(self, test_data, issue_keys):
        data = {}
        for key, value in test_data.iteritems():
            reason = value.get('reason')
            should_switch_on = filter(lambda id: reason.endswith(id), issue_keys)
            if not should_switch_on:
                data[key] = value

        return data

    def on_enqueue(self):
        self.Requirements.semaphores = ctt.Semaphores(
            acquires=[
                ctt.Semaphores.Acquire(
                    name='sandbox_ci_build_skip_tests_list_{}_{}'.format(
                        self.Parameters.tool,
                        self.Parameters.project,
                    ),
                    capacity=1
                )
            ]
        )

    def on_execute(self):
        os.environ['TESTCOP_AUTH_TOKEN'] = self.vault.read('env.TESTCOP_AUTH_TOKEN')

        branch = self.Parameters.branch

        if self.Parameters.main_branch != 'trunk':
            project_branches = self.get_project_branches()

            if branch == self.Parameters.main_branch:
                for project_branch in project_branches:
                    self.__publish_current_dev_resource(project_branch)

        if branch:
            self.__publish_skips_resource(branch, self.Parameters.issue_keys)
            return

        for project_branch in project_branches:
            self.__publish_skips_resource(project_branch, self.Parameters.issue_keys)

    def get_project_branches(self):
        project = self.Parameters.project
        main_branch = self.Parameters.main_branch
        # TODO: remove fallbacks before close - FEI-13517
        owner = self.Parameters.project_github_owner or PROJECTS[project]
        repo = self.Parameters.project_github_repo or project
        ref_path = 'repos/{}/{}/branches'.format(owner, repo)

        branches = self.fetch_branches(ref_path)
        branches_names = map(lambda branch: branch['name'], branches)

        branch_regexp = '^({}$|release)'.format(main_branch)

        # for monorepo
        if repo != project:
            branch_regexp = '^({}$|release/{}/)'.format(main_branch, project)

        return filter(lambda b: re.match(branch_regexp, b), branches_names)

    def fetch_branches(self, ref_path, page=1):
        page_ref_path = ref_path + '?page={}'.format(page)
        branches = GitHubApi().request(page_ref_path)

        if not branches:
            return []

        return branches + self.fetch_branches(ref_path, page+1)

    def __publish_current_dev_resource(self, project_branch):
        if project_branch == self.Parameters.main_branch or bool(self.__get_skipped_tests(branch=project_branch)):
            return

        dev_tests_data = objArrayToDict(self._get_skipped_tests_with_fallback(self.Parameters.main_branch))
        self.__publish_resource(project_branch, dev_tests_data)
