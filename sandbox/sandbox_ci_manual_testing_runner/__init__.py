# -*- coding: utf-8 -*-

import os
import shutil
import logging

from sandbox import sdk2
from sandbox.common.types import misc as ctm, task as ctt, resource as ctr
from sandbox.common.errors import TaskStop, ResourceNotFound

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.task import ManagersTaskMixin
from sandbox.projects.sandbox_ci.task.binary_task import TasksResourceRequirement
from sandbox.sandboxsdk import process, errors
from sandbox.projects.sandbox_ci.utils.process import format_args_for_run_process
from sandbox.projects.sandbox_ci.utils.context import Debug, Node

from sandbox.projects.common import solomon
from sandbox.projects.UrlsByShowCounters.resource_types import ABSOLUTE_URLS_BY_SHOW_COUNTERS_DATA
from sandbox.projects.resource_types import OTHER_RESOURCE

ASSESSORS_CLI_COMMAND = 'assessors'
TESTPALM_UNITED_RUNNER_CLI_COMMAND = 'tpur'
YML2TSV_CLI_COMMAND = 'yml2tsv'

DEPENDENCIES = [
    '@yandex-int/si.ci.assessors-cli@5.11',
    '@yandex-int/si.ci.testpalm-united-runner-cli@8.2',
    '@yandex-int/si.ci.yml2tsv-cli@7.1'
]

REPORTS_DIR = 'reports'
REPORTS_PATHS = {
    'assessors_fetch': 'assessors_fetch.json',
    'assessors_configure_valid': 'assessors_configure_valid.json',
    'assessors_configure_invalid': 'assessors_configure_invalid.json',
    'assessors_links': 'assessors_links.json',
    'assessors_bugs': 'assessors_bugs.json',
    'yml2tsv_output': 'yml2tsv_output.json',
    'yml2tsv_error': 'yml2tsv_error.json',
    'tpur_prepare': 'tpur_prepare.json',
    'tpur_run': 'tpur_run.json'
}

SOLOMON_PUSH_COMMON_PARAMETERS = {
    'project': 'fei',
    'cluster': 'sandbox',
    'service': 'sandbox_ci_manual_testing_runner',
}

MAX_RETRY_INSTALLATION_DEPENDENCIES_COUNT = 1

SIMILAR_TASK_SEARCH_STATUSES = list(set(ctt.Status.Group.ALL) - set([
    ctt.Status.DRAFT,
    ctt.Status.DELETED,
]))

# Время ожидания перехода черновика таска в любой статус из DRAFT в секундах
SIMILAR_TASK_DRAFT_WAIT_TIMEOUT = 1 * 60

logger = logging.getLogger(__name__)


class TaskRequirements(sdk2.Requirements):
    dns = ctm.DnsType.LOCAL
    cores = 1

    class Caches(sdk2.Requirements.Caches):
        pass


class TaskParameters(parameters.CommonParameters):
    _container = parameters.environment_container()

    with sdk2.parameters.Group('Common') as common_block:
        check_duplication = sdk2.parameters.Bool(
            'Check duplication',
            default=True,
            description='Проверка таска на дубликаты. Проверяется наличие таска с такими же параметрами. Причина в FEI-13832.'
        )

    with sdk2.parameters.Group('Launch') as launch_block:
        project = sdk2.parameters.String(
            'TestPalm project',
            required=True,
            description='Идентификатор проекта в TestPalm, для которого производится разадача заданий.'
        )
        service = sdk2.parameters.String(
            'TestPalm service',
            required=True,
            description='Идентификатор корневого проекта в TestPalm. Например, для serp-js-100 — serp-js.'
        )
        testRunIds = sdk2.parameters.List(
            'Identifiers of test runs',
            required=True,
            value_type=sdk2.parameters.String,
            description='Идентификаторы запускаемых тест-ранов.'
        )

    with sdk2.parameters.Group('assessors-cli') as assessors_block:
        assessors_testid_tag = sdk2.parameters.String(
            'Testid tag name',
            required=True,
            description='Название тега, по которому будет осуществляться поиск testid для экспериментальных тегов.'
        )

    with sdk2.parameters.Group('yml2tsv-cli') as yml2tsv_block:
        yml2tsv_formatter = sdk2.parameters.String(
            'Formatter',
            required=True,
            description='Название форматтера, используемого для преобразования тест-ранов.'
        )
        yml2tsv_group_size = sdk2.parameters.Integer(
            'Group size',
            required=True,
            description='Максимальное число тест-кейсов в группе.'
        )
        yml2tsv_group_time = sdk2.parameters.Integer(
            'Group time',
            required=True,
            description='Максимальное время, которое должно занимать выполнение тест-кейсов в группе.'
        )
        yml2tsv_plugins = sdk2.parameters.List(
            'Plugins',
            default=[],
            value_type=sdk2.parameters.String,
            description='Плагины, которые нужно использовать при запуске.'
        )

    with sdk2.parameters.Group('tpur') as tpur_block:
        tpur_enable_deadline_calculation = sdk2.parameters.Bool(
            'Enable deadline calculation',
            required=True,
            description='Автоматический расчёт дедлайнов по параметрам запуска.'
        )
        tpur_min_deadline_in_hours = sdk2.parameters.Float(
            'Minimal deadline',
            required=True,
            description='Минимальный дедлайн в часах.'
        )
        tpur_min_test_run_count_for_calculation = sdk2.parameters.Integer(
            'Minimal test run count for calculation',
            required=True,
            description='Минимальное число тест-ранов в запуске, необходимое для расчёта дедлайнов.'
        )
        tpur_additional_time_by_test_run_count_time = sdk2.parameters.Float(
            'Additional time step in hours',
            required=True,
            description='Время, выраженное в часах, добавляемое к дедлайну каждые N-шагов.'
        )
        tpur_additional_time_by_test_run_count_step = sdk2.parameters.Integer(
            'Additional time step in pieces',
            required=True,
            description='Шаг, выраженный в числе тест-ранов, при достижении которого добавляется время к дедлайну.'
        )
        tpur_additional_testrun_tags = sdk2.parameters.List(
            'Additional testrun tags',
            default=[],
            value_type=sdk2.parameters.String,
            description='Дополнительные теги, добавляемые к тест-рану.'
        )
        tpur_hitman_process_id = sdk2.parameters.String(
            'Hitman process id',
            required=True,
            description='Идентификатор запускаемого Hitman-процесса. Поддержка плейсхолдера "{{service}}" из конфига.'
        )

    node_js = parameters.NodeJsParameters


class TaskContext(sdk2.Context):
    report_resources = []


class SandboxCiManualTestingRunner(TasksResourceRequirement, ManagersTaskMixin, sdk2.Task):
    """
    Таск для подготовки и раздачи заданий на асессоров.
    """

    class Requirements(TaskRequirements):
        pass

    class Parameters(TaskParameters):
        pass

    class Context(TaskContext):
        pass

    @property
    def project_name(self):
        return ''

    @property
    def project_dir(self):
        return self.working_path()

    def working_path(self, *args):
        return self.path(*args)

    def on_enqueue(self):
        if not self.Parameters.check_duplication:
            logger.debug('Skip check duplication')
            return

        with self.memoize_stage.wait_similar_task_draft:
            # Ожидаем черновик похожего таска с таймаутом. Если за время ожидания черновик таска не перешёл
            # в другой статус, то такой таск уже не будет запущен. Он был создан механизмом ретраев.
            self._wait_similar_task_draft()

        with self.memoize_stage.check_duplication:
            # Проверяем дубликаты, исключая черновики, чтобы не прекращать раздачу в том случае, если
            # предыдущий таск был создан механизмом ретраев.
            self._check_task_duplication()

    def on_execute(self):
        self._set_env_variables()
        self._prepare_reports_dir()

        try:
            with Debug('*'), Node(self.Parameters.node_js_version):
                self._install_dependencies()
                self._fetch_testruns()
                self._configure_testruns()

                self._report_invalid_launches()

                if not self._has_valid_launches():
                    logger.debug('Cannot find valid launches. Skip next steps.')
                    return

                self._set_links()
                self._set_bugs_safe()
                self._run_yml2tsv()
                self._run_tpur_prepare()
                self._run_tpur_run()

                self._report_success_launch()
                self._report_yml2tsv_errors()

                self._finish_testruns()
        finally:
            self._save_artifacts()

    def _wait_similar_task_draft(self):
        similar_task_draft = self._search_similar_task(
            status=ctt.Status.Group.DRAFT,
            # Текущий таск уже не в DRAFT. Мы ищем только черновики. Нам важен хотя бы один.
            similar_tasks_search_count=1,
        )

        if similar_task_draft is not None:
            raise sdk2.WaitTask(
                [similar_task_draft.id],
                statuses=SIMILAR_TASK_SEARCH_STATUSES,
                timeout=SIMILAR_TASK_DRAFT_WAIT_TIMEOUT,
            )

    def _check_task_duplication(self):
        similar_task = self._search_similar_task(
            status=SIMILAR_TASK_SEARCH_STATUSES,
            # Текущий таск тоже участвует в поиске.
            similar_tasks_search_count=2,
        )

        if similar_task is not None:
            raise TaskStop('\n'.join([
                'Looks like a duplicate for the previous task (#{}). Stop the current task.'.format(similar_task.id),
                'You can clone task and uncheck the "Check duplication" parameter if you want to distribute test runs unconditionally.'
            ]))

    def _search_similar_task(self, status, similar_tasks_search_count):
        """
        Возвращает None в случае, если подобных запусков ранее не было.
        """
        logger.debug('Trying to find tasks with same parameters')

        # Первый запуск всегда автоматический и автором будет робот. Второй от человека.
        # Если авторы разные, то это перезапуск. Скорее всего перезапуск от дежурного, поэтому не мешаем ему.
        similar_tasks = list(sdk2.Task.find(
            type=SandboxCiManualTestingRunner,
            status=status,
            author=self.author,
            input_parameters=dict(
                project=self.Parameters.project,
                service=self.Parameters.service,
                testRunIds=self.Parameters.testRunIds,
            )
        ).order(-sdk2.Task.id).limit(similar_tasks_search_count))

        if len(similar_tasks) < similar_tasks_search_count:
            return None

        logger.debug('Found similar task (with the current task): {}'.format(similar_tasks))

        if similar_tasks[-1].id == self.id:
            return None

        return similar_tasks[-1]

    def _set_env_variables(self):
        os.environ.update({
            'NODE_EXTRA_CA_CERTS': '/etc/ssl/certs/YandexInternalRootCA.pem',
            'NPM_CONFIG_REGISTRY': 'http://npm.yandex-team.ru',
            'NPM_CONFIG_USER_AGENT': 'npm/6.2.0 (verdaccio yandex canary)',
            'TESTPALM_OAUTH_TOKEN': self.vault.read('env.TESTPALM_OAUTH_TOKEN'),
            'HITMAN_TOKEN': self.vault.read('env.HITMAN_TOKEN'),
            'AB_EXPERIMENTS_TOKEN': self.vault.read('env.AB_EXPERIMENTS_TOKEN'),
            'AB_ECOO_TOKEN': self.vault.read('env.AB_ECOO_TOKEN'),
            'STARTREK_TOKEN': self.vault.read('env.STARTREK_TOKEN')
        })

    def _set_env_variable(self, key, value):
        os.environ[key] = value

    def _unset_env_variable(self, key):
        del os.environ[key]

    def _prepare_reports_dir(self):
        os.makedirs(REPORTS_DIR)

    def _install_dependencies(self):
        retry = 0

        while retry <= MAX_RETRY_INSTALLATION_DEPENDENCIES_COUNT:
            try:
                self._run_process('npm install --no-save {}'.format(' '.join(DEPENDENCIES)), 'install_dependencies')
                break
            except Exception as error:
                retry += 1
                logger.exception('Cannot install dependencies (attempt {attempt}): {error}'.format(
                    attempt=retry,
                    error=error
                ))

    def _fetch_testruns(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} fetch'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'project-id': self.Parameters.project,
                'testrun-ids': self.Parameters.testRunIds
            },
            '> {}'.format(REPORTS_PATHS.get('assessors_fetch'))
        ])

        self._run_process(command, 'assessors_fetch')

    def _finish_testruns(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} finish'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'project-id': self.Parameters.project,
                'testrun-ids': self.Parameters.testRunIds
            }
        ])

        self._run_process(command, 'assessors_finish')

    def _configure_testruns(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} configure'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'project-id': self.Parameters.project,
                'service': self.Parameters.service,
                'testruns': REPORTS_PATHS.get('assessors_fetch'),
                'devices': self._get_last_devices_resource_path(),
                'output': REPORTS_PATHS.get('assessors_configure_valid'),
                'error': REPORTS_PATHS.get('assessors_configure_invalid')
            }
        ])

        self._run_process(command, 'assessors_configure')

    def _set_links(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} links'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('assessors_configure_valid'),
                'testid-exp-flag-tag': self.Parameters.assessors_testid_tag
            },
            '> {}'.format(REPORTS_PATHS.get('assessors_links'))
        ])

        self._run_process(command, 'assessors_links')

    def _set_bugs_safe(self):
        try:
            self._set_bugs()
        except errors.SandboxSubprocessError as error:
            previous_step_report = os.path.join(REPORTS_DIR, REPORTS_PATHS.get('assessors_links'))
            current_step_report = os.path.join(REPORTS_DIR, REPORTS_PATHS.get('assessors_bugs'))

            # Следующая команда ожидает файл с результатом выполнения этой команды, но его не будет.
            # Копируем результат предыдущего шага в файл результата текущего шага.
            shutil.copyfile(previous_step_report, current_step_report)

            logger.exception('Cannot link bugs: {}'.format(error))

            self._send_solomon_sensors([{
                'labels': {'sensor': 'link_bugs_error'},
                'kind': 'IGAUGE',
                'value': 1
            }])

    def _set_bugs(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} link-bugs'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('assessors_links')
            },
            '> {}'.format(REPORTS_PATHS.get('assessors_bugs'))
        ])

        self._run_process(command, 'assessors_bugs')

    def _run_yml2tsv(self):
        alternative_queries_resource_path = self._get_last_alternative_queries_resource_path_safe()

        command = format_args_for_run_process([
            'npx --no-install {cli}'.format(cli=YML2TSV_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('assessors_bugs'),
                'output': REPORTS_PATHS.get('yml2tsv_output'),
                'error': REPORTS_PATHS.get('yml2tsv_error'),
                'formatter': self.Parameters.yml2tsv_formatter,
                'group-size': self.Parameters.yml2tsv_group_size,
                'group-time': self.Parameters.yml2tsv_group_time,
                'plugins': self.Parameters.yml2tsv_plugins,
                'resources.urlsByShowCounters': alternative_queries_resource_path
            }
        ])

        if not alternative_queries_resource_path:
            self.set_info('WARN: Cannot find resource with alternative queries')

        self._run_process(command, 'yml2tsv')

    def _run_tpur_prepare(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} prepare'.format(cli=TESTPALM_UNITED_RUNNER_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('yml2tsv_output'),
                'enable-deadline-calculation': self.Parameters.tpur_enable_deadline_calculation,
                'min-deadline-in-hours': self.Parameters.tpur_min_deadline_in_hours,
                'min-test-run-count-for-calculation': self.Parameters.tpur_min_test_run_count_for_calculation,
                'additional-time-by-test-run-count-time': self.Parameters.tpur_additional_time_by_test_run_count_time,
                'additional-time-by-test-run-count-step': self.Parameters.tpur_additional_time_by_test_run_count_step,
                'additional-test-run-tags': self.Parameters.tpur_additional_testrun_tags
            },
            '> {}'.format(REPORTS_PATHS.get('tpur_prepare'))
        ])

        self._run_process(command, 'tpur_prepare')

    def _run_tpur_run(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} run'.format(cli=TESTPALM_UNITED_RUNNER_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('tpur_prepare'),
                'hitman-process-id': self.Parameters.tpur_hitman_process_id
            },
            '> {}'.format(REPORTS_PATHS.get('tpur_run'))
        ])

        self._run_process(command, 'tpur_run')

    def _report_yml2tsv_errors(self):
        yml2tsv_errors_filepath = REPORTS_PATHS.get('yml2tsv_error')
        yml2tsv_errors_fullpath = os.path.join(REPORTS_DIR, yml2tsv_errors_filepath)

        if not os.path.exists(yml2tsv_errors_fullpath):
            logger.debug('The "{}" file not found. Skip yml2tsv errors reporting.'.format(yml2tsv_errors_fullpath))
            return

        command = format_args_for_run_process([
            'npx --no-install {cli} report-yml2tsv-errors'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'project-id': self.Parameters.project,
                'config': yml2tsv_errors_filepath
            }
        ])

        self._run_process(command, 'assessors_report_yml2tsv_errors')

    def _report_invalid_launches(self):
        invalid_launches_filepath = REPORTS_PATHS.get('assessors_configure_invalid')
        invalid_launches_fullpath = os.path.join(REPORTS_DIR, invalid_launches_filepath)

        if not os.path.exists(invalid_launches_fullpath):
            logger.debug('The "{}" file not found. Skip invalid launches reporting.'.format(invalid_launches_fullpath))
            return

        command = format_args_for_run_process([
            'npx --no-install {cli} report-invalid-launches'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'config': invalid_launches_filepath
            }
        ])

        self._run_process(command, 'assessors_report_invalid_launches')

    def _report_success_launch(self):
        command = format_args_for_run_process([
            'npx --no-install {cli} report-success-launch'.format(cli=ASSESSORS_CLI_COMMAND),
            {
                'config': REPORTS_PATHS.get('tpur_run')
            }
        ])
        self._run_process(command, 'assessors_report_success_launch')

    def _run_process(self, command, log_prefix):
        process.run_process(
            command,
            work_dir=str(self.path(REPORTS_DIR)),
            log_prefix=log_prefix,
            shell=True
        )

    def _get_last_devices_resource_path(self):
        resource = sdk2.Resource.find(
            type=OTHER_RESOURCE,
            state=ctr.State.READY,
            attrs={'type': 'assessors_devices'}
        ).first()

        return str(sdk2.ResourceData(resource).path)

    def _get_last_alternative_queries_resource_path_safe(self):
        try:
            return self._get_last_alternative_queries_resource_path()
        except Exception as error:
            logger.exception('Cannot find resource with alternative queries: {}'.format(error))

            self._send_solomon_sensors([{
                'labels': {'sensor': 'alternative_queries_resource_not_found'},
                'kind': 'IGAUGE',
                'value': 1
            }])

        return None

    def _get_last_alternative_queries_resource_path(self):
        resource = sdk2.Resource.find(
            type=ABSOLUTE_URLS_BY_SHOW_COUNTERS_DATA,
            state=ctr.State.READY,
            attrs={'tlds_coverage': True}
        ).first()

        if resource:
            return str(sdk2.ResourceData(resource).path)

        raise ResourceNotFound('Resource with alternative queries was not found')

    def _save_artifacts(self):
        self.artifacts.create_report(
            resource_path=REPORTS_DIR,
            type='reports',
            status=ctt.Status.SUCCESS,
            add_to_context=True
        )

    # https://wiki.yandex-team.ru/solomon/api/dataformat/json/
    def _send_solomon_sensors(self, sensors):
        try:
            solomon.push_to_solomon_v2(
                token=self.vault.read('env.SOLOMON_OAUTH_TOKEN'),
                params=SOLOMON_PUSH_COMMON_PARAMETERS,
                sensors=sensors
            )
            logger.debug('Sensors pushed: {}'.format(sensors))
        except Exception as error:
            logger.exception('Cannot send sensors ({sensors}): {error}'.format(
                sensors=sensors,
                error=error
            ))

    def _has_valid_launches(self):
        valid_launches_filepath = REPORTS_PATHS.get('assessors_configure_valid')
        valid_launches_fullpath = os.path.join(REPORTS_DIR, valid_launches_filepath)
        return os.path.exists(valid_launches_fullpath)
