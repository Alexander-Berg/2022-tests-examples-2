# -*- coding: utf-8 -*-
import logging

from sandbox import sdk2
from sandbox.common.types import resource as ctr
from sandbox.common.types import task as ctt
from sandbox.common.errors import TaskFailure, TaskError
from sandbox.common.utils import singleton_property

from sandbox.projects.report_renderer.resource_types import (
    REPORT_RENDERER_BUNDLE, AHPROXY_EXECUTABLE,
)
from sandbox.projects.report_renderer.parameters import ReportRendererBundlePackage
from sandbox.projects.report_renderer.BenchmarkReportRendererBase.task import BenchmarkPlan
from sandbox.projects.report_renderer.BenchmarkReportRendererBase.task import Templates

from sandbox.projects.resource_types import REPORT_RENDERER_BLOCKSTAT_LOG

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.task import BaseTask
from sandbox.projects.sandbox_ci.pulse.resources import ReportRendererPlan
from sandbox.projects.sandbox_ci.pulse.resources import ReportRendererPlanApphost
from sandbox.projects.sandbox_ci.utils.process import run_process
from sandbox.projects.sandbox_ci.resources import BlockstatYsonLog
from sandbox.projects.sandbox_ci.resources import LogfellerStdinParserBinary


class SandboxCiBlockstatTest(BaseTask):
    """Проверка логов blockstat"""

    class Parameters(BaseTask.Parameters):
        with sdk2.parameters.Group('Blockstat') as blockstat_block:
            ammo = sdk2.parameters.Resource(
                'Ammo',
                description=u'Последний стабильный релиз патронов, если не указан',
                required=False,
            )
            platform = sdk2.parameters.String(
                'Platform',
                description=u'Платформа для которой будет производится обстрел',
            )
            project_name = sdk2.parameters.String(
                'Project',
                description=u'Проект (web4,...)',
                required=True,
                default=None
            )
            ref = sdk2.parameters.String(
                'Build Branch',
                description=u'Ветка в репо проекта',
                required=True,
            )
            templates = sdk2.parameters.Resource(
                'Templates',
                description=u'Шаблоны для которых будет производится обстрел',
                required=True,
            )
            is_apphost = sdk2.parameters.Bool(
                'Is apphost?',
                description=u'Нужны ли ресурсы для apphost',
                default=False
            )

            with sdk2.parameters.String('Формат blockstat лога') as blockstat_format:
                blockstat_format.values['yson'] = blockstat_format.Value('yson', default=True)
                blockstat_format.values['raw'] = 'raw'

        with BaseTask.Parameters.tracker_block() as tracker_block:
            send_comment_to_issue = parameters.send_comment_to_issue()

    @property
    def github_context(self):
        return u'[Sandbox CI] Проверка логов blockstat: {}'.format(self.Parameters.platform)

    @property
    def project_name(self):
        return self.Parameters.project_name

    def create_subtask(self, task_type, **params):
        """
        Создает и запускает указанную sdk1-задачу с указанными параметрами.

        :param task_type: название задачи
        :type task_type: str
        :rtype: int
        """
        return self.meta.run_task(
            task_type,
            {
                'description': self.Parameters.description,
                'notifications': self.server.task[self.id].read()['notifications'],
                'owner': self.owner,
                'priority': {
                    'class': self.Parameters.priority.cls,
                    'subclass': self.Parameters.priority.scls,
                },
                'custom_fields': [{'name': name, 'value': value} for (name, value) in params.items()],
            },
        )['id']

    @property
    def benchmark_plan_resource_id(self):
        """
        Возвращает id ресурса с планом обстрела

        :rtype: int
        """
        cached_resource_id = self.Context.benchmark_plan_resource_id

        current_plan = ReportRendererPlanApphost if self.Parameters.is_apphost else ReportRendererPlan

        if cached_resource_id:
            logging.debug('Found in cache {} resource #{}'.format(current_plan.__name__, cached_resource_id))
            return cached_resource_id

        if self.Parameters.ammo:
            logging.debug('Ammo resource id is specified: #{}'.format(self.Parameters.ammo.id))
            return self.Parameters.ammo.id

        attrs = {
            'platform': self.Parameters.platform,
            'project': self.project_name,
            'released': ctt.ReleaseStatus.STABLE,
        }
        logging.debug(u'Trying to find {} resource with parameters: {}'.format(current_plan.__name__, attrs))
        resource = sdk2.Resource.find(
            resource_type=current_plan,
            attrs=attrs,
        ).order(-sdk2.Resource.id).first()

        if resource is None:
            raise TaskError(u'Could not find {} resource → infraduty@'.format(current_plan.__name__,))

        logging.debug('Found {} resource #{}'.format(current_plan.__name__, resource.id))
        self.Context.benchmark_plan_resource_id = resource.id

        return resource.id

    @property
    def rr_bundle_resource_id(self):
        """
        Возвращает id ресурса с бандлом ynode + report-renderer

        :rtype: int
        """
        cached_resource_id = self.Context.rr_bundle_resource_id

        if cached_resource_id:
            logging.debug('Found in cache REPORT_RENDERER_BUNDLE resource #{}'.format(cached_resource_id))
            return cached_resource_id

        attrs = {
            'released': ctt.ReleaseStatus.STABLE,
        }
        logging.debug(u'Trying to find REPORT_RENDERER_BUNDLE resource with parameters: {}'.format(attrs))
        resource = sdk2.Resource.find(
            resource_type=REPORT_RENDERER_BUNDLE,
            attrs=attrs,
        ).order(-sdk2.Resource.id).first()

        if resource is None:
            raise TaskError(u'Could not find REPORT_RENDERER_BUNDLE resource → infraduty@')

        logging.debug('Found REPORT_RENDERER_BUNDLE resource #{}'.format(resource.id))
        self.Context.rr_bundle_resource_id = resource.id

        return resource.id

    def get_blockstat_logs(self):
        """
        Находит ресурс с логами, которые созданные в результате обстрела

        :rtype: sdk2.Resource
        """
        benchmark_rr_subtask_id = self.Context.benchmark_rr_subtask_id
        logging.debug(u'Trying to find REPORT_RENDERER_BLOCKSTAT_LOG resource from task {}'.format(benchmark_rr_subtask_id))
        resource = REPORT_RENDERER_BLOCKSTAT_LOG.find(
            state=ctr.State.READY,
            task_id=benchmark_rr_subtask_id,
        ).first()

        if resource is None:
            raise TaskFailure('Could not find REPORT_RENDERER_BLOCKSTAT_LOG resource, checkout subtask')

        logging.debug('Found REPORT_RENDERER_BLOCKSTAT_LOG resource#{}'.format(resource.id))

        return resource

    def wait(self, task_id):
        """Отправляет текущую задачу в WAIT_TASK для ожидания указанной подзадачи"""
        raise sdk2.WaitTask(
            task_id,
            ctt.Status.Group.FINISH | ctt.Status.Group.BREAK,
            timeout=self.Parameters.kill_timeout,
            wait_all=True,
        )

    def get_subtask_context(self, task_id):
        """
        Возвращает контекст задачи по указанному айдишнику

        :param task_id: айдишник подзадачи
        :type task_id: str
        :rtype: dict
        """
        ctx = self.server.task[task_id].context[:]
        logging.debug(u'Fetching context of task={0}, ctx={1}', task_id, ctx)

        return ctx

    def get_subtask(self, task_id):
        """
        Возвращает данные задачи по указанному айдишнику

        :param task_id: айдишник подзадачи
        :type task_id: str
        :rtype: dict
        """
        return self.server.task[task_id].read()

    @singleton_property
    def _logfeller_stdin_parser_path(self):
        res = LogfellerStdinParserBinary.find(
            state=ctr.State.READY,
            attrs=dict(
                released=ctt.ReleaseStatus.STABLE,
            ),
        ).first()

        if not res:
            raise TaskFailure('LogfellerStdinParserBinary resource not found')

        return str(sdk2.ResourceData(res).path)

    def _convert_blockstat_log_to_yson(self, blockstat_raw_log_resource):
        blockstat_raw_log_path = sdk2.ResourceData(blockstat_raw_log_resource).path
        blockstat_yson_log_path = str(self.path('blockstat.yson'))

        logging.info('Converting blockstat to yson...')

        run_process(['{} --parser search-blockstat-log < {} > {}'.format(
            self._logfeller_stdin_parser_path,
            blockstat_raw_log_path,
            blockstat_yson_log_path,
        )], shell=True)

        blockstat_yson_log_resource = BlockstatYsonLog(self, "blockstat log converted to yson", blockstat_yson_log_path)
        sdk2.ResourceData(blockstat_yson_log_resource).ready()

        logging.info('blockstat.yson is ready: %s', blockstat_yson_log_resource.id)

        return blockstat_yson_log_resource

    def execute(self):
        """
        Работает в три этапа:

        - shooting: обстрел для получения ресурса с логами
        - testing: тестирование полученных логов
        - results: пишем результаты в info задачи
        """
        with self.memoize_stage.shooting(commit_on_entrance=False):
            if self.Parameters.is_apphost:
                benchmark_rr_subtask_id = self.create_subtask(
                    'BENCHMARK_REPORT_RENDERER_BASE_APPHOST',
                    **{
                        'report_renderer_bundle': self.rr_bundle_resource_id,
                        'dolbilo_plan': self.benchmark_plan_resource_id,
                        'templates': self.Parameters.templates.id,
                        'rr_workers': 8,
                        'ahproxy': AHPROXY_EXECUTABLE.find(
                            attrs={'released': 'stable'}
                        ).first().id,
                        'request_limit': 50000
                    }
                )
            else:
                benchmark_rr_subtask_id = self.create_subtask(
                    'BENCHMARK_REPORT_RENDERER_BASE',
                    **{
                        BenchmarkPlan.name: self.benchmark_plan_resource_id,
                        ReportRendererBundlePackage.name: self.rr_bundle_resource_id,
                        Templates.name: self.Parameters.templates.id,
                    }
                )
            self.Context.benchmark_rr_subtask_id = benchmark_rr_subtask_id
            self.wait(benchmark_rr_subtask_id)

        with self.memoize_stage.testing(commit_on_entrance=False):
            blockstat_log_resource = self.get_blockstat_logs()

            if self.Parameters.blockstat_format == 'yson':
                blockstat_log_resource = self._convert_blockstat_log_to_yson(blockstat_log_resource)

            test_logs_id = self.create_subtask(
                'TEST_REPORT_LOGS',
                log_name='blockstat_log',
                input_data=blockstat_log_resource.id,
            )
            self.Context.test_logs_id = test_logs_id
            self.wait(test_logs_id)

        with self.memoize_stage.results(commit_on_entrance=False):
            test_logs_id = self.Context.test_logs_id

            task_info = self.get_subtask(test_logs_id)
            status = task_info['status']
            if status != ctt.Status.SUCCESS:
                raise TaskFailure(u'TEST_REPORT_LOGS subtask is in {} status'.format(status))

            ctx = self.get_subtask_context(test_logs_id)
            test_result = ctx['result_stats']['test_result']

            self.Context.report_resources += ctx['test_task_resources']

            if test_result != 'OK':
                raise TaskFailure(u'TEST_REPORT_LOGS test result is {}'.format(test_result))

    def before_end(self, status):
        """
        Вызывается перед завершением таски
        :param status: статус задачи (SUCCESS, FAILED)
        :type status: sandbox.common.types.task
        """
        issue_key = self.Parameters.send_comment_to_issue
        if issue_key:
            self.release.add_status_comment(issue_key, status)

    def on_before_end(self, status):
        super(SandboxCiBlockstatTest, self).on_before_end(status)
        self.before_end(status)
