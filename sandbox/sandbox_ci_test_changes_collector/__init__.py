# -*- coding: utf-8 -*-

import os
import json

from sandbox import sdk2
from sandbox.common.utils import classproperty, singleton_property

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.utils.context import Node
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.sandbox_ci.decorators.in_case_of import in_case_of
from sandbox.projects.sandbox_ci.task import OverlayfsMixin, PrepareWorkingCopyMixin, BaseTask
from sandbox.projects.sandbox_ci.utils.git import save_git_changed_files_with_statuses, get_git_last_merge_commit_issues
from sandbox.projects.sandbox_ci.managers.arc.arc_cli import save_arc_changed_files_with_statuses, get_arc_last_merge_commit_issues


class SandboxCiTestChangesCollector(PrepareWorkingCopyMixin, OverlayfsMixin, BaseTask):
    """
    Сбор статистики по частоте изменений тестов в проекте
    """

    changed_files = 'changed-files.json'

    class Requirements(BaseTask.Requirements):
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(BaseTask.Parameters):
        project_hash = parameters.project_hash()

        build_artifacts_resources = sdk2.parameters.Resource(
            'Артефакты сборки',
            resource_type=SANDBOX_CI_ARTIFACT,
            multiple=True,
        )

        with sdk2.parameters.Group('Test changes collector') as test_changes_collector_block:
            test_types = sdk2.parameters.List(
                u'Типы тестов',
                required=True,
            )
            concurrency = sdk2.parameters.Integer(
                u'Параллельность обработки разных типов тестов',
                default=1,
            )
            dry_run = sdk2.parameters.Bool(
                u'Не записывать результаты в таблицу базы данных',
                default=False,
            )
            test_read_environs = sdk2.parameters.JSON(
                u'Список окружений для чтения тестов',
                description='Опция актуальна для проектов, которые завазяны на переменные среды окружения при чтении тестов',
                default=[],
            )
            issue_keys = sdk2.parameters.List(
                u'Список id-задач в Startrek',
                description='Если рабочая копия формируется с помощью overlayfs, то этот параметр определяется автоматически в таске',
                default=[],
            )

    lifecycle_steps = {
        'npm_install': 'npm ci',
        'run_collector': 'DEBUG=test-changes-collector:* npx @yandex-int/test-changes-collector {collector_options}',
    }

    @singleton_property
    def project_name(self):
        return self.Parameters.project_github_repo

    @classproperty
    def github_context(self):
        return u'[Sandbox CI] Сбор статистики по частоте изменений тестов в проекте'

    def on_save(self):
        super(SandboxCiTestChangesCollector, self).on_save()

        semaphore_name = 'test_changes_collector_{}'.format(self.project_name)
        self.set_semaphore(semaphore_name)

    def execute(self):
        self.__set_environments()
        self._exec()

    @in_case_of('use_overlayfs', '_exec_in_overlayfs_mode')
    def _exec(self):
        self._download_sources(self.Parameters.build_artifacts_resources, self.project_dir)

        with Node(self.Parameters.node_js_version):
            self._install_dependencies()
            self.__run_collector()

    def _exec_in_overlayfs_mode(self):
        with self.prepare_working_copy_context():
            self.__save_changed_files(self.project_sources_dir, self.changed_files)

            with Node(self.Parameters.node_js_version), self._overlayfs(lower_dirs=[self.project_sources_dir], resources=self.Parameters.build_artifacts_resources, target_dir=self.project_dir):
                self.__run_collector()

    def __run_collector(self):
        self.lifecycle.update_vars(collector_options=self.__format_collector_options())
        self.lifecycle('run_collector')

    def __set_environments(self):
        os.environ['CLICKHOUSE_PASSWORD'] = os.environ.get('FEI_CH_PASSWORD')
        os.environ['CLICKHOUSE_TABLE'] = self.config.get_deep_value(['tests', 'changes_collector', 'db_table_name'])
        os.environ['hermione_muted_tests_stability_index_output_enabled'] = 'false'

    def __save_changed_files(self, work_dir, file_path):
        save_arc_changed_files_with_statuses(work_dir, file_path) if self.use_arc else save_git_changed_files_with_statuses(work_dir, file_path)

    def __format_collector_options(self):
        options = [
            '--run-id {}'.format(self.id),
            '--type {}'.format(' '.join(self.Parameters.test_types)),
            '--concurrency {}'.format(self.Parameters.concurrency),
            '--project {}'.format(self.Parameters.project_github_repo),
            '--dry-run {}'.format('true' if self.Parameters.dry_run else 'false'),
            '--changed-files {}'.format(self.changed_files),
        ]

        merge_commit_issues = self.__get_merge_commit_issues(self.project_sources_dir)
        if len(merge_commit_issues):
            options.append('--issue {}'.format(' '.join(merge_commit_issues)))

        if len(self.Parameters.test_read_environs):
            options.append('--envs \'{}\''.format(json.dumps(self.Parameters.test_read_environs)))

        return ' '.join(options)

    def __get_merge_commit_issues(self, work_dir):
        if not self.use_overlayfs:
            return self.Parameters.issue_keys

        return get_arc_last_merge_commit_issues(work_dir) if self.use_arc else get_git_last_merge_commit_issues(work_dir)
