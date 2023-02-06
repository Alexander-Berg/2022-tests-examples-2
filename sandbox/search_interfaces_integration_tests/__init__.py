# -*- coding: utf-8 -*-

from sandbox import sdk2

from sandbox.common.errors import TaskFailure
from sandbox.common.types import task as ctt
from sandbox.common.utils import singleton_property

from sandbox.projects.report_renderer.resource_types import REPORT_RENDERER_NODEJS_PACKAGE

from sandbox.projects.resource_types import CALC_METRICS_DAEMON_EXECUTABLE, CLICKDAEMON_EXECUTABLE, \
    REPORT_RENDERER_PACKAGE

from sandbox.projects.sandbox_ci.utils import env
from sandbox.projects.sandbox_ci.task import BaseTask
from sandbox.projects.sandbox_ci.sandbox_ci_hermione import SandboxCiHermione
from sandbox.projects.sandbox_ci.sandbox_ci_fiji_hermione import SandboxCiFijiHermione
from sandbox.projects.sandbox_ci.sandbox_ci_hermione_e2e import SandboxCiHermioneE2E


class ProjectParameters(sdk2.Parameters):
    with sdk2.parameters.Group('Custom command') as command_block:
        custom_command = sdk2.parameters.String('Кастомная команда перед запуском тестов', multiline=True)

    with sdk2.parameters.Group('Projects') as projects_block:
        run_web4_tests = sdk2.parameters.Bool('Запускать тесты web4', default=True)
        run_fiji_tests = sdk2.parameters.Bool('Запускать тесты fiji', default=True)

    with sdk2.parameters.Group('Test types') as test_block:
        run_hermione_tests = sdk2.parameters.Bool('Запускать hermione-тесты', default=True)
        hermione_task_retries = sdk2.parameters.Integer(
            'Максимальное количество перезапусков hermione-задачи',
            description='Задача будет перезапущена n раз только для упавших тестов',
            default=None
        )
        run_e2e_tests = sdk2.parameters.Bool('Запускать e2e-тесты', default=True)


class SearchInterfacesIntegrationTests(BaseTask):
    """
        Таск запуска интеграционных тестов search-interfaces проектов.
    """

    project_name = 'search-interfaces-integration-tests'

    github_context = u'[Sandbox CI] Интеграционные тесты'

    class Parameters(BaseTask.Parameters):
        project_params = ProjectParameters

        calc_metrics_daemon_executable = sdk2.parameters.Resource(
            'calc_metrics_daemon executable',
            resource_type=CALC_METRICS_DAEMON_EXECUTABLE,
        )
        clickdaemon_executable = sdk2.parameters.Resource(
            'clickdaemon executable',
            resource_type=CLICKDAEMON_EXECUTABLE,
        )
        report_renderer_package = sdk2.parameters.Resource(
            'ReportRenderer package',
            resource_type=REPORT_RENDERER_PACKAGE,
        )
        report_renderer_nodejs_package = sdk2.parameters.Resource(
            'Node JS binary package',
            resource_type=REPORT_RENDERER_NODEJS_PACKAGE,
        )

    class Context(BaseTask.Context):
        run_failed = []

    def get_project_conf(self, project_name):
        return self.config.get_project_conf(self.conf, {
            'project_name': project_name,
            'build_context': self.Parameters.project_build_context or None,
            'external_config': self.Parameters.external_config,
        })

    def use_overlayfs_in_project(self, project_name):
        project_conf = self.get_project_conf(project_name)
        return project_conf.get('use_overlayfs', False) and project_conf.get('use_arc', False)

    def execute(self):
        with self.memoize_stage.mk_subtasks:
            subtasks = []

            if self.Parameters.run_web4_tests:
                subtasks += self.populate_web4_test_tasks()

            if self.Parameters.run_fiji_tests:
                subtasks += self.populate_fiji_test_tasks()

            if len(subtasks) == 0:
                raise TaskFailure('Unable to run any tests')

            raise sdk2.WaitTask(
                tasks=self.meta.start_subtasks(subtasks),
                statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK
            )

        with self.memoize_stage.process:
            if self.Context.run_failed:
                self.set_info('Could not find artifacts and start tests for {}'.format(','.join(self.Context.run_failed)))

            if self.meta.failed_subtasks:
                self.meta.store_failed_tasks(self.meta.failed_subtasks)

                raise TaskFailure('Has failed subtasks, see reports for more details')

    def populate_web4_test_tasks(self):
        owner = 'serp'
        repo = 'web4'
        resources = self.get_dev_ready_resources(
            attrs_list=[{'type': 'web4.squashfs'}],
            owner=owner,
            repo=repo
        )

        if resources is None:
            self.Context.run_failed.append('web4')
            return []

        project_task = sdk2.Task.find(id=resources[0].task_id).limit(1).first()
        project_hash = project_task.Parameters.project_hash

        subtasks = []

        if self.Parameters.run_hermione_tests:
            subtasks.append(self.create_test_subtask(
                task_type=SandboxCiHermione,
                platforms=['desktop', 'touch-pad', 'touch-phone'],
                resources=resources,
                task_retries=self.Parameters.hermione_task_retries,
                sqsh_build_artifacts_resources=resources,
                html_reporter_use_sqlite=True,
                project_github_owner=owner,
                project_github_repo=repo,
                project_hash=project_hash,
                use_overlayfs=self.use_overlayfs_in_project(repo),
            ))

        # E2E tests use one platform intentionally: https://st.yandex-team.ru/FEI-8275
        if self.Parameters.run_e2e_tests:
            subtasks.append(self.create_test_subtask(
                task_type=SandboxCiHermioneE2E,
                platform='touch-pad',
                resources=resources,
                hermione_base_url='https://hamster.yandex.ru',
                project_name='web4',
                project_github_owner=owner,
                project_github_repo=repo,
                project_hash=project_hash,
                use_overlayfs=self.use_overlayfs_in_project(repo),
            ))

        return subtasks

    def populate_fiji_test_tasks(self):
        owner = 'mm-interfaces'
        repo = 'fiji'
        resources = self.get_dev_ready_resources(
            attrs_list=[{'type': 'fiji'}],
            owner=owner,
            repo=repo
        )

        if resources is None:
            self.Context.run_failed.append('fiji')
            return []

        subtasks = []

        for platform in ['desktop', 'touch-pad', 'touch-phone']:
            for service in ['images', 'video']:
                if self.Parameters.run_hermione_tests:
                    subtasks.append(self.create_test_subtask(
                        task_type=SandboxCiFijiHermione,
                        platform=platform,
                        resources=resources,
                        service=service,
                        task_retries=self.Parameters.hermione_task_retries,
                        project_github_owner=owner,
                        project_github_repo=repo,
                    ))

        return subtasks

    def get_dev_ready_resources(self, attrs_list, owner, repo):
        return self.artifacts.get_dev_ready_resources(
            attrs_list=self.get_attrs_list(attrs_list, repo),
            owner=owner,
            repo=repo,
            YENV='testing'
        )

    def get_attrs_list(self, attrs_list, project_name):
        if self.use_overlayfs_in_project(project_name):
            return [{'type': '{}.squashfs'.format(project_name)}]

        return attrs_list

    @singleton_property
    def subtask_environ(self):
        # Выключаем репортинг падений тестов
        environ = {
            'json_reporter_enabled': 'false',
            'stat_reporter_enabled': 'false',
            'hermione_plugins_faildump': 'false',
        }

        resources_list = [
            (self.Parameters.calc_metrics_daemon_executable, 'TEMPLAR_CALC_METRICS_DAEMON_RESOURCE_ID'),
            (self.Parameters.clickdaemon_executable, 'TEMPLAR_CLICKDAEMON_RESOURCE_ID'),
            (self.Parameters.report_renderer_nodejs_package, 'TEMPLAR_YNODE_RESOURCE_ID'),
            (self.Parameters.report_renderer_package, 'TEMPLAR_REPORT_RENDERER_RESOURCE_ID'),
        ]

        for (resource, env_var) in resources_list:
            if resource:
                if env_var in self.Parameters.environ:
                    raise TaskFailure('{} conflict - both resource and environment id is set'.format(env_var))
                environ[env_var] = resource.id

        return env.merge((environ, self.Parameters.environ))

    def create_test_subtask(self, task_type, resources, platform=None, **kwargs):
        params = {}

        if platform:
            params['platform'] = platform
            # Выставляем дополнительные теги подзадачам
            params['additional_tags'] = [platform]

        for name, value in kwargs.items():
            params[name] = value

        return self.meta.create_subtask(
            task_type=task_type,
            build_artifacts_resources=resources,
            description=self.get_test_subtask_description(platform),
            project_build_context='dev',
            project_tree_hash=resources[0].project_tree_hash,
            # Отключаем доставку статусов на Гитхаб
            report_github_statuses=False,
            # Отключаем доставку статистики в stat
            send_statistic=False,
            custom_command=self.Parameters.custom_command,
            environ=self.subtask_environ,
            # Выключаем селективность
            selective_run=False,
            **params
        )
