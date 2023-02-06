# -*- coding: utf-8 -*-

import os
import json
import logging

from sandbox import sdk2
from sandbox.common.types import misc as ctm
from sandbox.sandboxsdk import process

from sandbox.projects.release_machine import input_params2 as rm_params2
from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.decorators.in_case_of import in_case_of
from sandbox.projects.sandbox_ci.task import ProjectPathsMixin, ManagersTaskMixin, PrepareWorkingCopyMixin
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.projects.sandbox_ci.utils.process import format_args_for_run_process
from sandbox.projects.sandbox_ci.utils.context import Debug, Node

TESTPALM_SUITE_RUNNER_PKG = '@yandex-int/si.ci.testpalm-suite-runner-cli@4.1'
TESTPALM_CLI_PKG = '@yandex-int/si.ci.testpalm-cli@6.1'


class TaskRequirements(sdk2.Requirements):
    dns = ctm.DnsType.LOCAL
    cores = 1

    class Caches(sdk2.Requirements.Caches):
        pass


class TaskParameters(parameters.CommonParameters):
    _container = parameters.environment_container()

    project_github_repository = parameters.ProjectGitHubRepositoryParameters

    with sdk2.parameters.Group('TestPalm project') as project_block:
        testpalm_project_suffix = sdk2.parameters.String(
            'TestPalm project suffix',
            description='Суффикс для проекта в TestPalm. Используется для указания версии тестируемого релиза.',
        )
        testpalm_base_project_name = sdk2.parameters.String(
            'TestPalm base project',
            description='Идентификатор базового проекта в TestPalm',
            default='',
        )

    with sdk2.parameters.Group('Flow control') as flow_control_block:
        ticket_id = sdk2.parameters.String(
            'Ticket',
            description='Ключ тикета в Трекере.',
        )
        need_clone_testpalm_project = sdk2.parameters.Bool(
            'Clone base service project',
            description='Клонировать базовый проект сервиса в новый (service + suffix)',
            default=False,
        )
        need_validate_config = sdk2.parameters.Bool(
            'Validate testpalm suite runner config',
            description='Валидировать конфигурацию для testpalm-suite-runner',
            default=True
        )
        is_dry_run = sdk2.parameters.Bool(
            'Dry run',
            description='Создавать тест-раны, но не запускать их раздачу на асессоров.',
            default=False,
        )
        is_flags_release = sdk2.parameters.Bool(
            'Flags release',
            description='Запускать только те тест-сьюты, что относятся к релизу флагов.',
            default=False,
        )
        testpalm_base_project_name = sdk2.parameters.String(
            'TestPalm Base Project Name',
            description='Название базового проекта в TestPalm',
            default='',
        )

    with sdk2.parameters.Group('Custom settings') as custom_settings_block:
        booking_id = sdk2.parameters.String(
            'Booking Id',
            description='Идентификатор брони для ручного запуска',
            default='',
        )

    with sdk2.parameters.Group('Manual run') as manual_block:
        is_manual_run = sdk2.parameters.Bool('Show manual run parameters', default=False)

        with is_manual_run.value[True]:
            manual_config = sdk2.parameters.JSON(
                'Suite config',
                description='Конфиг, содержащий описание запускаемых тест-сьютов.'
            )

    with sdk2.parameters.Group('Resource run') as resource_block:
        is_resource_run = sdk2.parameters.Bool('Show resource run parameters', default=True)

        with is_resource_run.value[True]:
            build_artifacts_resources = parameters.build_artifacts_resources(required=False)

            config_path = sdk2.parameters.String(
                'Config path',
                description='Путь до конфига в предоставленном ресурсе.'
                            'Если не указать, то параметры запуска берутся из блока параметров ручного запуска.'
            )

    with sdk2.parameters.Group('Arc') as arc_block:
        use_arc = sdk2.parameters.Bool(
            'Use Arc',
            description='Используется ли arc.',
            default=False,
        )
        project_name = sdk2.parameters.String(
            'Project',
            description='Название проекта.',
            default='',
        )
        project_hash = parameters.project_hash()

    with sdk2.parameters.Group('Project params') as project_params:
        git_checkout_params = sdk2.parameters.JSON('Параметры для чекаута git-репозитория', default={})

    dependencies = parameters.DependenceParameters
    scripts_sources = parameters.ScriptsSourcesParameters

    with sdk2.parameters.Group('Overlayfs') as overlayfs:
        use_overlayfs = sdk2.parameters.Bool(
            'Use overlayfs',
            description='Использовать overlayfs (тестовый режим)',
            default=False
        )

    node_js = parameters.NodeJsParameters

    with sdk2.parameters.Group('Релизная машина') as release_machine_block:
        component_name_params = rm_params2.ComponentName2()
        run_flags_mode = sdk2.parameters.Bool(
            'Для компоненты ab_flags запустить выполнение задачи',
            description="Используется только для запусков из компоненты ab_flags RM",
            default=False,
        )


class TaskContext(sdk2.Context):
    failed_tasks = []


class SandboxCiTestpalmSuiteRunner(TasksResourceRequirement, ManagersTaskMixin, ProjectPathsMixin, PrepareWorkingCopyMixin, sdk2.Task):
    """
    Таск для запуска тестирования на асессорах по заранее написанному конфигу в репозитории проекта или переданному
    конфигу в случае ручного запуска.
    """
    github_context = '[Sandbox CI] Запуск тестирования на асессорах'

    class Requirements(TaskRequirements):
        pass

    class Parameters(TaskParameters):
        pass

    class Context(TaskContext):
        pass

    skip_action_profile = True

    @property
    def use_overlayfs(self):
        return self.Parameters.use_overlayfs

    @property
    def testpalm_suite_runner_output(self):
        return 'testpalm_suite_runner.json'

    @property
    def use_arc(self):
        return self.Parameters.use_arc and self.Parameters.project_name

    @property
    def project_name(self):
        return self.Parameters.project_name

    @property
    def target_dir(self):
        return self.path('artifacts')

    def on_enqueue(self):
        self.task_dependencies.wait_tasks(fail_on_deps_fail=True)
        self.task_dependencies.wait_output_parameters(timeout=(self.Parameters.kill_timeout * 2))
        self.task_dependencies.ensure_output_parameter('is_static_uploaded', True, 'Static is not uploaded')

    def on_prepare(self):
        if not self.use_arc and self.use_overlayfs:
            self.scripts.sync_resource()

    def on_execute(self):
        self.set_env_variables()
        self.execute()

    @in_case_of('use_overlayfs', 'execute_with_checkout')
    def execute(self):
        self.run()

    def execute_with_checkout(self):
        with self.prepare_working_copy_context():
            os.symlink(str(self.project_sources_dir), str(self.target_dir))

            self.run()

    def run(self):
        if (
            self.Parameters.component_name_params.component_name in ["ab_flags", "ab_flags_testids"]
            and not self.Parameters.run_flags_mode
        ):
            self.set_info("Got component 'ab_flags' but run_flags_mode is disabled, should skip this task.")
            return

        config_filepath = self.build_config_path()

        self.set_booking_id_to_test_suites(config_filepath)

        config = self.read_json(config_filepath)

        base_service_name = self.get_base_service_name(config)
        testpalm_project_name = self.format_project_name(base_service_name)

        if self.Parameters.need_clone_testpalm_project:
            self.clone_testpalm_project(base_service_name, testpalm_project_name)

        if self.Parameters.need_validate_config:
            self.validate_config(config_filepath, testpalm_project_name)

        self.run_suites(config_filepath, testpalm_project_name)

    def build_config_path(self):
        if self.Parameters.is_manual_run:
            return self.save_config_from_task_parameters()

        return self.build_config_path_from_sources()

    def save_config_from_task_parameters(self):
        logging.debug('build config path from task parameters')

        config_filepath = str(self.path('manual.json'))

        self.write_json(config_filepath, self.Parameters.manual_config)

        return config_filepath

    def build_config_path_from_sources(self):
        self.artifacts.unpack_build_artifacts(self.Parameters.build_artifacts_resources, self.target_dir)

        logging.debug('build config path from resource')

        config_filepath = os.path.join(str(self.target_dir), self.Parameters.config_path)

        if os.path.exists(config_filepath):
            return config_filepath

        raise Exception('Cannot find config by specified filepath ("{config_filepath}")'.format(
            config_filepath=config_filepath,
        ))

    def set_booking_id_to_test_suites(self, config_filepath):
        logging.debug('trying to set booking id to test suites')

        booking_id = self.Parameters.booking_id

        if booking_id == '':
            logging.debug('skipping setting of the booking id, because it is not presented')
            return

        config = self.read_json(config_filepath)

        for suite in config.get('suites', []):
            suite_properties = suite.get('testsuite_properties', {})

            suite_properties['hitman_booking_id'] = booking_id

        self.write_json(config_filepath, config)

    def read_json(self, filepath):
        with open(filepath, 'r') as f:
            return json.loads(f.read())

    def write_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def get_base_service_name(self, config):
        # Сейчас мы вынуждены получать имя сервиса из первого элемента конфига, так как идентификатор репозитория
        # сервиса на GitHub и проекта в TestPalm никак не связаны. Например, web4 в TestPalm имеет название serp-js.
        # Сейчас это исправлять сложно, но на будущее есть тикет: FEI-9348
        return config.get('suites')[0].get('service')

    def format_project_name(self, service_name):
        service_suffix = self.Parameters.testpalm_project_suffix

        if not service_suffix:
            return service_name

        return '{service_name}-{service_suffix}'.format(
            service_name=service_name,
            service_suffix=service_suffix,
        )

    def set_env_variables(self):
        os.environ.update({
            'NODE_EXTRA_CA_CERTS': '/etc/ssl/certs/YandexInternalRootCA.pem',
            'NPM_CONFIG_REGISTRY': 'http://npm.yandex-team.ru',
            'NPM_CONFIG_USER_AGENT': 'npm/6.2.0 (verdaccio yandex canary)',
            'TESTPALM_OAUTH_TOKEN': self.vault.read('env.TESTPALM_OAUTH_TOKEN'),
            'ARC_TOKEN': self.vault.read('env.ARC_TOKEN')
        })

    def validate_config(self, config_filepath, project_name):
        command = format_args_for_run_process([
            'npx {} validate'.format(TESTPALM_SUITE_RUNNER_PKG),
            config_filepath,
            {
                'project-id': project_name
            }
        ])

        self.run_process(command, 'testpalm_suite_runner_cli_validate')

    def clone_testpalm_project(self, source_project, target_project):
        command = format_args_for_run_process([
            'npx {} clone'.format(TESTPALM_CLI_PKG),
            source_project,
            target_project
        ])

        self.run_process(command, 'testpalm_cli')

    def run_suites(self, config_filepath, project_name):
        command = format_args_for_run_process([
            'npx {}'.format(TESTPALM_SUITE_RUNNER_PKG),
            config_filepath,
            {
                'project-id': project_name,
                'dry-run': self.Parameters.is_dry_run,
                'release-flags': self.Parameters.is_flags_release
            },
            '> {}'.format(self.testpalm_suite_runner_output)
        ])

        self.run_process(command, 'testpalm_suite_runner_cli')

    def run_process(self, command, log_prefix):
        with Debug('*'), Node(self.Parameters.node_js_version):
            process.run_process(
                command,
                work_dir=str(self.path()),
                log_prefix=log_prefix,
                shell=True
            )
