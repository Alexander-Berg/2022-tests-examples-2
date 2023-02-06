# -*- coding: utf-8 -*-
import os
import logging
from sandbox import sdk2
from sandbox.projects.sandbox_ci.managers import BrowsersConfigManager
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.base import SandboxCiCompareLoadTestBase
from sandbox.projects.sandbox_ci.task.ManagersTaskMixin import ManagersTaskMixin


class SandboxCiCompareLoadTestWeb4(SandboxCiCompareLoadTestBase, ManagersTaskMixin):

    """
        Нагрузочная таска
    """

    name = 'SANDBOX_CI_COMPARE_LOAD_TEST_WEB4'

    @property
    def conf(self):
        return self.config.get_properties()

    @property
    def project_conf(self):
        return self.config.get_project_conf(self.conf, {
            'project_name': 'web4',
            'build_context': None
        })

    def create_tests_subtask(self):
        return self.tests_dev_task.type(self,
            sqsh_build_artifacts_resources=self.tests_dev_task.Parameters.sqsh_build_artifacts_resources,
            build_artifacts_resources=self.tests_dev_task.Parameters.build_artifacts_resources,
            platforms=self.tests_dev_task.Parameters.platforms,
            project_build_context=self.tests_dev_task.Parameters.project_build_context,

            report_github_statuses=False,

            reuse_subtasks_cache=False,
            reusable=False,

            send_statistic=False,
            selective_run=False,

            custom_opts='{} {}'.format(self.__get_browsers_run_cmd(), self.Parameters.custom_opts),
            environ = self.__get_env_params(),
            external_config = self.__get_external_config(),
            project_github_owner=self.tests_dev_task.Parameters.project_github_owner,
            project_github_repo=self.tests_dev_task.Parameters.project_github_repo,
            data_center=self.Parameters.data_center
        ).enqueue()

    def __get_env_params(self):
        res = {}

        res.update({'hermione_grid_url': self.Parameters.grid_url})

        if self.Parameters.browser_id:
            res.update({'HERMIONE_BROWSERS': self.Parameters.browser_id})

        if self.Parameters.skip_list_id:
            res.update({'EXTERNAL_SKIP_HERMIONE_WEB4_DEV': self.Parameters.skip_list_id})

        return res

    def __get_browsers_run_cmd(self):
        total = self.Parameters.session_cnt / self.project_conf.get('environ', {}).get('hermione_chunks_count', 7)

        return BrowsersConfigManager.format_sessions_per_browser_cli_option(self.Parameters.browser_id, total)

    def __get_external_config(self):
        tests_dev_task = self.Parameters.tests_dev_task
        semaphore_env_preifx = '*.tests.hermione.browsers'

        for platform in tests_dev_task.Parameters.platforms:
            semaphores_for_platform = tests_dev_task.browsers_config.get_semaphores_for_platform(platform)

            for s in semaphores_for_platform:
                browser = BrowsersConfigManager.parse_browser(s)

                if browser['id'] == self.Parameters.browser_id:
                    return {'{}.{}.{}'.format(semaphore_env_preifx, platform, s): 1}

        return {}

    def get_tests_reports(self):
        from sandbox.yasandbox.manager.task import TaskManager
        res = []
        subtasks_ids = TaskManager.list_subtasks(self)

        for task_id in subtasks_ids:
            subtask = sdk2.Task.find(id=task_id).first()

            resources = subtask.Context.report_resources
            res += subtask.task_reports.reports(resources)

        return res

    def get_task_key(self):
        return '_'.join(self.Parameters.tags)
