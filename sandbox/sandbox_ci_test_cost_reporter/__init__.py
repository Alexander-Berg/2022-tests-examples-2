# -*- coding: utf-8 -*-

import os
import logging
import shutil

from sandbox import sdk2
from sandbox.sandboxsdk import process
from sandbox.common.errors import TaskFailure
from sandbox.common.types import task as ctt, resource as ctr
from sandbox.common.utils import classproperty, singleton_property
from sandbox.sandboxsdk.process import check_process_return_code

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.decorators.in_case_of import in_case_of
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.sandbox_ci.task import OverlayfsMixin, PrepareWorkingCopyMixin, BaseTask
from sandbox.projects.sandbox_ci.utils import testpalm
from sandbox.projects.sandbox_ci.utils.context import GitRetryWrapper, Debug, Node
from sandbox.projects.sandbox_ci.utils.process import format_args_for_run_process
from sandbox.projects.sandbox_ci.utils.release import remove_release_branch_prefix

HERMIONE_SUFFIX = '_HERMIONE'
HERMIONE_E2E_SUFFIX = '_HERMIONE_E2E'

FREE_ISSUE_QUEUES = ['FEI', 'INFRADUTY']
FREE_ISSUE_TAGS = ['manual-js-test', 'skipped-js-test', 'skipped-tests-js', 'skipped-test-js']

REPORTABLE_TASK_STATUSES = [ctt.Status.SUCCESS, ctt.Status.FAILURE, ctt.Status.RELEASING, ctt.Status.RELEASED, ctt.Status.NOT_RELEASED]


class SandboxCiTestCostReporter(PrepareWorkingCopyMixin, OverlayfsMixin, BaseTask):
    """
    Репортер стоимости ручного тестирования.
    """

    name = 'SANDBOX_CI_TEST_COST_REPORTER'
    use_overlayfs = False

    class Requirements(BaseTask.Requirements):
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(BaseTask.Parameters):
        with sdk2.parameters.Group('Test cost reporter') as test_cost_reporter_block:
            mode = sdk2.parameters.String(
                u'Режим сбора статистики',
                default='pr',
                description=u'Статистиска для релизов и пулл-реквестов собирается по разному из разных источников, поэтому нужно явно указать режим.',
                choices=[
                    ('pr', 'pr'),
                    ('release', 'release'),
                ],
                sub_fields={
                    'pr': ['pr_title', 'pr_number', 'pr_merge_ref'],
                    'release': ['target_task_id', 'release_version']
                },
                required=True,
            )
            target_task_id = sdk2.parameters.Integer('Metatask Id', description=u'Идентификатор метатаски для которой необходимо посчитать стоимость тест-кейсов.')
            release_version = sdk2.parameters.String('Release version', description=u'Версия релиза.')
            release_version_description = sdk2.parameters.String('Release version description', description=u'Описание релиза, которое будет репортиться в worklog.')

            pr_title = sdk2.parameters.String('PR title', description=u'Заголовок пулл-реквеста.')
            pr_number = sdk2.parameters.String('PR number', description=u'Номер пулл-реквеста.')
            pr_merge_ref = sdk2.parameters.String('Merge ref', description=u'Merge ref пулл-реквеста для поиска таски')

            service = sdk2.parameters.String('Service', description=u'Название сервиса (fiji → images, video).')
            required_task_type = sdk2.parameters.String('Task type', description=u'Тип таски, которую нужно найти для подсчета статистики.')
            skipped = sdk2.parameters.Bool('Calculate skipped tests', default=True)
            manual = sdk2.parameters.Bool(
                'Calculate Manual',
                description=u'Считать стоимость мануальных кейсов.',
                default=False,
                sub_fields={
                    'true': ['testpalm_project_name'],
                },
            )
            testpalm_project_name = sdk2.parameters.String('TestPalm project name')

        with sdk2.parameters.Group('ClickHouse settings') as clickhouse_block:
            ch_hosts = sdk2.parameters.List(
                'Hosts of ClickHouse cluster'
            )
            ch_port = sdk2.parameters.Integer(
                'Port for hosts',
                default=8443
            )
            ch_user = sdk2.parameters.String(
                'Login for ClickHouse user',
                default='robot_clickhouse_bot'
            )
            ch_db = sdk2.parameters.String(
                'Db in ClickHouse for reporting stats',
                default='stats'
            )
            ch_table = sdk2.parameters.String(
                'Table in ClickHouse for reporting stats',
                default='issue_time_costs'
            )

        node_js = parameters.NodeJsParameters

        git_checkout_params = sdk2.parameters.JSON('Параметры для чекаута git-репозитория в режиме overlayfs', default={})

    lifecycle_steps = {
        'npm_install': 'npm ci',
        'npm_install_package': 'npm install --prefix ./task_npm_dependencies @yandex-int/skipped-tests-stat@4 --no-save',
        'run': 'DEBUG=* ./task_npm_dependencies/node_modules/@yandex-int/skipped-tests-stat/bin/skips-stat report {flags} {ch_settings}'
    }

    # Таску требуются скрипты для клонирования рабочей копии
    skip_ci_scripts_checkout = False

    def on_enqueue(self):
        super(SandboxCiTestCostReporter, self).on_enqueue()

        self.ensure_static_is_uploaded()

    def on_save(self):
        super(SandboxCiTestCostReporter, self).on_save()

        self.Parameters.release_version = self.cut_release_version_prefixes(self.Parameters.release_version)

        if not self.Parameters.release_version_description:
            self.Parameters.release_version_description = self.Parameters.release_version

    def cut_release_version_prefixes(self, release_version):
        if release_version.startswith('refs/heads/'):
            release_version = release_version.replace('refs/heads/', '', 1)

        if release_version.startswith('tags/'):
            release_version = release_version.replace('tags/', '', 1)

        return release_version

    @singleton_property
    def project_name(self):
        return self.Parameters.project_github_repo

    @singleton_property
    def clickhouse_hosts(self):
        if self.Parameters.ch_hosts:
            return self.Parameters.ch_hosts

        return self.config.get_deep_value(['fei_clickhouse_hosts'], [])

    @classproperty
    def github_context(self):
        return u'[Sandbox CI] Отправка статистики стоимости ручных тестов'

    def execute(self):
        with self.memoize_stage.check_issue_cost:
            if self.is_pull_request_mode():
                os.makedirs(str(self.project_dir))

                with Node(self.Parameters.node_js_version):
                    os.environ.setdefault('NPM_CONFIG_REGISTRY', 'https://npm.yandex-team.ru')
                    self.lifecycle('npm_install_package')

                if self.is_infrastructure_issue():
                    self.set_info('All issue keys related to tickets that do not need to be tested. Skip cost reporting')

                    return

                shutil.rmtree(str(self.project_dir))

        with self.memoize_stage.find_target_task:
            target_task = self.find_task_with_test_subtasks()

            if not target_task:
                raise TaskFailure('The Sandbox task for specified input parameters is not found')

            self.set_info('Found task {}'.format(self.make_task_link(target_task)), do_escape=False)

            self.Context.target_task = target_task.id

            if self.Parameters.skipped:
                logging.debug('Will wait for target task: {}'.format(target_task))

                raise sdk2.WaitTask(target_task, list(ctt.Status.Group.FINISH) + [ctt.Status.WAIT_TASK])

        with self.memoize_stage.find_subtasks:
            test_subtasks = []
            if self.Parameters.skipped:
                target_task = self.get_task_by_id(self.Context.target_task)

                test_subtasks = self.get_test_subtasks(target_task)

                if not test_subtasks:
                    self.set_info('Not found test subtasks in task {}'.format(self.make_task_link(target_task)), do_escape=False)
                    return

                links_to_tasks = ''.join(['\n - ' + self.make_task_link(t) for t in test_subtasks])
                self.set_info('Found test tasks: {}'.format(links_to_tasks), do_escape=False)

            self.Context.target_test_subtasks = [t.id for t in test_subtasks]

        with self.memoize_stage.wait_tasks:
            if len(self.Context.target_test_subtasks) > 0:
                test_subtasks = self.get_tasks_by_id(self.Context.target_test_subtasks)

                logging.debug('Will wait for task dependencies: {}'.format(test_subtasks))

                raise sdk2.WaitTask(test_subtasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

        task = self.get_task_by_id(self.Context.target_task)
        test_subtasks = self.get_tasks_by_id(self.Context.target_test_subtasks)

        self.lifecycle.update_vars(
            flags=self.get_stat_additional_flags(task, test_subtasks),
            ch_settings=self.get_ch_settings()
        )

        self.use_overlayfs = getattr(task, 'use_overlayfs', False)

        self.run_scripts(task)

    @in_case_of('use_overlayfs', 'run_scripts_in_overlayfs_mode')
    def run_scripts(self, task):
        with GitRetryWrapper(), Node(self.Parameters.node_js_version), self.vault.ssh_key():
            self.fetch_project_resource(task.id)
            # Скрипту необходим исполняемый PalmSync-конфиг, который требует некоторых npm-пакетов проекта
            self.dependencies.npm_install()
            self.lifecycle('npm_install_package')
            self.lifecycle('run')

    def run_scripts_in_overlayfs_mode(self, task):
        with self.prepare_working_copy_context(dict(commit=task.Parameters.project_hash)):
            with Node(self.Parameters.node_js_version), self._overlayfs(lower_dirs=[self.project_sources_dir], resources=self.get_project_task_resources(task.id), target_dir=self.project_dir):
                self.lifecycle('npm_install_package')
                self.lifecycle('run')

    def find_task_with_test_subtasks(self):
        """
        :rtype: sdk2.Task
        """
        if self.Parameters.target_task_id:
            return self.get_task_by_id(self.Parameters.target_task_id)

        if self.Parameters.release_version:
            return self.find_release_task()

        if self.Parameters.pr_number:
            return self.find_last_pull_request_task()

    def get_test_subtasks(self, task):
        """
        :param task: Инстанс таски
        :type sdk2.Task:
        :rtype: list of sdk2.Task
        """
        subtasks_ids = self.get_subtasks_ids(task)

        logging.debug('Found subtasks ids {}'.format(subtasks_ids))

        if not subtasks_ids:
            logging.debug('Not found subtasks ids')
            return []

        subtasks = self.get_tasks_by_id(subtasks_ids)

        logging.debug('Found subtasks {}'.format(subtasks))

        if not subtasks:
            logging.debug('Not found subtasks')
            return []

        test_subtasks = self.filter_test_task_by_service(self.get_test_tasks(subtasks))

        if not test_subtasks:
            logging.debug('Not found test tasks')
            return []

        logging.debug('Found test tasks {}'.format(test_subtasks))

        return test_subtasks

    def get_subtasks_ids(self, task):
        """
        :param task: Инстанс таски
        :type task: sdk2.Task
        :rtype: list of int
        """
        return (task.Context.subtasks or []) + (task.Context.non_waitable_subtasks or [])

    def get_tasks_by_id(self, tasks_id):
        """
        :param tasks_id: Идентификаторы задач
        :type tasks_id: list of int
        :rtype: list of sdk2.Task
        """
        if tasks_id:
            return list(sdk2.Task.find(id=tasks_id, children=True).limit(len(tasks_id)))

        return []

    def get_task_by_id(self, task_id):
        """
        :param task_id: Идентификатор задачи
        :type task_id: int
        :rtype: sdk2.Task
        """
        return sdk2.Task.find(id=task_id, children=True).first()

    def get_test_tasks(self, subtasks):
        """
        :param subtasks: Инстансы тасок
        :type subtasks: list of sdk2.Task
        :rtype: list of sdk2.Task
        """
        suffixes = (HERMIONE_E2E_SUFFIX, HERMIONE_SUFFIX)

        test_subtasks = []
        for subtask in subtasks:
            if str(subtask.type.name).endswith(suffixes):
                test_subtasks.append(subtask)

        return test_subtasks

    def filter_test_task_by_service(self, subtasks):
        """
        :param subtasks: Инстансы тасок
        :type subtasks: list of sdk2.Task
        :rtype: list of sdk2.Task
        """
        if not self.Parameters.service:
            return subtasks

        filtered_subtasks = []
        for subtask in subtasks:
            subtask_service = getattr(subtask.Parameters, 'service', None)

            logging.debug('subtask {} has service {}'.format(subtask, subtask_service))

            if not subtask_service or self.Parameters.service == subtask_service:
                filtered_subtasks.append(subtask)

        return filtered_subtasks

    def get_stat_additional_flags(self, task, test_subtasks):
        """
        :param task: Инстанс таски
        :type sdk2.Task:
        :param task: Инстансы тестовых тасок
        :type list of sdk2.Task:
        :rtype: str
        """
        flags = '--owner {owner} --repo {repo}'.format(
            owner=self.Parameters.project_github_owner,
            repo=self.Parameters.project_github_repo,
        )

        if self.Parameters.service:
            flags = '{} --service {}'.format(flags, self.Parameters.service)

        if self.Parameters.pr_number:
            flags = '{} --pull {}'.format(flags, self.Parameters.pr_number)

        if self.Parameters.release_version:
            flags = '{} --release {}'.format(flags, self.Parameters.release_version_description)

        if self.Parameters.skipped:
            flags = '{} {}'.format(flags, self.get_skipped_stat_additional_flags(task, test_subtasks))

        if self.Parameters.manual:
            flags = '{} {}'.format(flags, self.get_manual_stat_additional_flags())

        return flags

    def get_skipped_stat_additional_flags(self, task, test_subtasks):
        """
        :param task: Инстанс таски
        :type sdk2.Task:
        :param task: Инстансы тестовых тасок
        :type list of sdk2.Task:
        :rtype: str
        """
        test_tools = self.get_skipped_test_tools(test_subtasks)

        return '{test_tools} --task-id {task_id} --hash {hash}'.format(
            test_tools=self.format_test_tools_value(test_tools),
            task_id=self.id,
            hash=task.Parameters.project_tree_hash,
        )

    def get_skipped_test_tools(self, test_subtasks):
        """
        :param task: Инстансы тестовых тасок
        :type list of sdk2.Task:
        :rtype: list of BaseTestTask, str
        """
        test_tools = [
            HermioneE2eTestTool(test_subtasks),
            HermioneTestTool(test_subtasks)
        ]

        if self.is_empty_platforms_tools(test_tools):
            raise TaskFailure('Cannot get the platforms for test tools')

        return test_tools

    def format_test_tools_value(self, test_tools):
        """
        :param test_tools: Инстансы BaseTestTask
        :type test_tools: list of BaseTestTask
        :rtype: None
        """
        tools_argv = []

        for tool in test_tools:
            tools_argv.append(tool.get_skipped_tool_argv())

        return ' '.join(tools_argv)

    def get_manual_stat_additional_flags(self):
        """
        :rtype: str
        """
        return '--manual --testpalm-project {}'.format(self.get_testpalm_project())

    def get_testpalm_project(self):
        """
        :rtype: str
        """
        suffix = self.Parameters.pr_number or self.Parameters.release_version

        if not suffix:
            raise TaskFailure('testpalm_project_suffix is asked, but no pr_number or release_version set')

        testpalm_suffix = testpalm.sanitize_project_name(remove_release_branch_prefix(suffix))

        return '{}-{}'.format(self.Parameters.testpalm_project_name, testpalm_suffix)

    def is_empty_platforms_tools(self, test_tools):
        """
        :param test_tools: Инстансы BaseTestTask
        :type test_tools: list of BaseTestTask
        :rtype: bool
        """
        return not bool(len(filter(lambda tool: tool.platforms, test_tools)))

    def get_ch_settings(self):
        """
        :rtype: str
        """
        flags = '--ch-port {port} --ch-user {user} --ch-db {db} --ch-table {table}'.format(
            port=self.Parameters.ch_port,
            user=self.Parameters.ch_user,
            db=self.Parameters.ch_db,
            table=self.Parameters.ch_table
        )

        hosts_flags = ' '.join(map(lambda host: '--ch-host {}'.format(host), self.clickhouse_hosts))

        return '{} {}'.format(flags, hosts_flags)

    def find_last_pull_request_task(self):
        default_pr_merge_ref = 'pull/{}'.format(self.Parameters.pr_number)
        merge_ref = self.Parameters.pr_merge_ref if self.Parameters.pr_merge_ref else default_pr_merge_ref

        input_parameters = dict(
            project_github_owner=self.Parameters.project_github_owner,
            project_github_repo=self.Parameters.project_github_repo,
            project_git_merge_ref=[merge_ref],
            project_build_context='pull-request',
        )

        return sdk2.Task.find(
            type=self.Parameters.required_task_type,
            status=REPORTABLE_TASK_STATUSES,
            input_parameters=input_parameters,
        ).order(-sdk2.Task.id).first()

    def find_release_task(self):
        input_parameters = dict(
            project_github_owner=self.Parameters.project_github_owner,
            project_github_repo=self.Parameters.project_github_repo,
            project_git_base_ref=self.Parameters.release_version,
            project_build_context='release',
        )

        return sdk2.Task.find(
            type=self.Parameters.required_task_type,
            status=REPORTABLE_TASK_STATUSES,
            input_parameters=input_parameters,
        ).order(-sdk2.Task.id).first()

    def is_finished_task(self, task):
        """
        :param task: Инстанс таски
        :type task: sdk2.Task
        :rtype: bool
        """
        return task.status in ctt.Status.Group.FINISH

    def fetch_project_resource(self, task_id):
        """
        :param task_id: Идентификатор проектной таски
        :type task_id: int
        :rtype: None
        """
        resources = self.get_project_task_resources(task_id)

        self.unpack_artifacts(resources)

    def get_project_task_resources(self, task_id):
        """
        :param task_id: Идентификатор проектной таски
        :type task_id: int
        :rtype: list of sdk2.Resource
        """
        def get_resources(resource_types):
            resources = []

            for resource_type in resource_types:
                resource_query = sdk2.Resource.find(
                    task_id=task_id,
                    state=ctr.State.READY,
                    type=SANDBOX_CI_ARTIFACT,
                    attrs={'type': resource_type}
                )

                resource = resource_query.limit(resource_query.count).first()
                if resource is None:
                    continue

                resources.append(resource)

            return resources

        return get_resources(self.artifact_types)

    @property
    @in_case_of('use_overlayfs', 'artifact_types_in_overlayfs_mode')
    @in_case_of('sqsh_artifacts', 'artifact_types_in_sqsh_artifacts_mode')
    def artifact_types(self):
        return [self.project_name, 'hermione', 'features']

    def artifact_types_in_sqsh_artifacts_mode(self):
        return ['{}.sqsh'.format(self.project_name)]

    def artifact_types_in_overlayfs_mode(self):
        return ['{}.squashfs'.format(self.project_name)]

    def unpack_artifacts(self, resources):
        """
        :param resources: Набор ресурсов
        :type resources: list of sdk2.Resource
        :rtype: None
        """
        self.artifacts.unpack_build_artifacts(resources, self.project_dir, unsquash=True)

    def is_pull_request_mode(self):
        """
        :rtype: bool
        """
        return self.Parameters.mode == 'pr'

    def is_infrastructure_issue(self):
        issue_keys = self.parse_issue_keys_from_pr_title(self.Parameters.pr_title)
        non_free_issue_keys = filter(lambda issue: not self.is_free_issue(issue), issue_keys)

        return len(non_free_issue_keys) == 0

    def parse_issue_keys_from_pr_title(self, title):
        """
        :param title: Заголовок пулл-реквеста
        :type title: str
        :rtype: list of str
        """
        keys = title.split(':')[0]
        if not keys:
            return []

        issues = keys.split(',')

        return map(lambda issue: issue.strip(), issues)

    def is_free_issue(self, issue_key):
        """
        :param issue_key: Идентификатор тикета
        :type issue_key: str
        :rtype: bool
        """
        # Пулл-реквест без привязки к тикету
        if issue_key.startswith('TRIVIAL'):
            return True

        command = format_args_for_run_process([
            './node_modules/@yandex-int/skipped-tests-stat/bin/skips-stat is-free-issue',
            issue_key,
            {
                'free-queue': FREE_ISSUE_QUEUES,
                'free-tags': FREE_ISSUE_TAGS,
            }
        ])

        with Debug('*'), Node(self.Parameters.node_js_version):
            command_process = self.run_process(command, 'is-free-issue.log')
            exit_code = command_process.wait()

        # Код "2" означает ошибку
        if exit_code == 2:
            check_process_return_code(command_process)

        return exit_code == 0

    def make_task_link(self, task):
        """
        :param task: Инстанс таски
        :type task: sdk2.Task
        :rtype: str
        """
        return '<a href="https://sandbox.yandex-team.ru/task/{id}">{name}</a> [{id}] ({status})'.format(
            id=task.id,
            name=str(task.type.name),
            status=task.status
        )

    def run_process(self, command, log_prefix):
        return process.run_process(
            command,
            work_dir=str(self.project_dir),
            log_prefix=log_prefix,
            check=False,
            shell=True
        )


class BaseTestTool(object):
    name = None
    test_suffix = None

    def __init__(self, tasks):
        """
        :param task: Список инстансов тасок
        :type task: list of sdk2.Task
        :rtype: BaseTestTool
        """

        self.tasks = tasks
        self.platforms = self.get_platforms()

    def is_test_tool_task(self, task):
        """
        :param task: Инстанс таски
        :type task: sdk2.Task
        :rtype: bool
        """
        return str(task.type.name).endswith(self.test_suffix)

    def get_platforms(self):
        """
        :rtype: list of str
        """

        tasks = filter(self.is_test_tool_task, self.tasks)

        platforms = map(self.get_task_platforms, tasks)

        unique_platforms = list(set(platforms))

        logging.debug('{} platforms: {}'.format(self.name, unique_platforms))

        return unique_platforms

    def get_task_platforms(self, task):
        """
        :param task: Инстанс таски
        :type task: sdk2.Task
        :rtype: str
        """
        # Если поле platform не определено, значит надо искать merged отчёт.
        return getattr(task.Parameters, 'platform', 'merged')

    def get_skipped_tool_argv(self):
        """
        :rtype: str
        """
        if self.platforms:
            return '--{} {}'.format(self.name, ','.join(self.platforms))

        return ''


class HermioneTestTool(BaseTestTool):
    name = 'hermione'
    test_suffix = HERMIONE_SUFFIX


class HermioneE2eTestTool(BaseTestTool):
    name = 'hermione-e2e'
    test_suffix = HERMIONE_E2E_SUFFIX
