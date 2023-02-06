# -*- coding: utf-8 -*-

import copy
import json
import logging
import datetime
from sandbox import sdk2
import os
import tempfile
import pathlib2

from sandbox.common.types import task as ctt
from sandbox.sandboxsdk import errors
from sandbox.common.errors import TaskFailure
from sandbox.projects.sandbox_ci.utils import flow
from sandbox.projects.sandbox_ci.utils.list_utils import flatten
from sandbox.projects.sandbox_ci.decorators.in_case_of import in_case_of
from sandbox.projects.sandbox_ci.task.test_task.BaseTestTask import BaseTestTask
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.projects.sandbox_ci.managers.actions_constants import actions_constants
from sandbox.projects.sandbox_ci.managers.arc.arc_cli import save_arc_changed_files
from sandbox.projects.sandbox_ci.utils.git import save_git_changed_files


class BaseHermioneCommonTask(BaseTestTask):
    class Parameters(BaseTestTask.Parameters):
        tests_to_run_resource = sdk2.parameters.Resource(
            'Список тестов для запуска',
            resource_type=SANDBOX_CI_ARTIFACT,
            description='Используется, чтобы запускать определенный набор тестов',
            attrs={
                'type': 'tests-to-run-list'
            },
            multiple=False,
            required=False,
        )
        task_retries = sdk2.parameters.Integer(
            'Максимальное количество перезапусков задачи',
            description='Задача будет перезапущена n раз только для упавших тестов',
            default=None
        )
        task_retries_delay = sdk2.parameters.List(
            'Паузы в минутах между перезапусками задач',
            description='Массив длительностей пауз в минутах между перезапусками упавших задач',
            default=[]
        )
        task_delay = sdk2.parameters.Integer(
            'Задержка перед выполнением задачи',
            description='Перед тем как выполниться, задача будет находиться n минут в состоянии WAIT_TIME',
            default=None
        )
        html_reporter_use_sqlite = sdk2.parameters.Bool(
            'Save test results to sqlite database (FEI-15320)',
            default=True
        )
        with sdk2.parameters.String('Консольный репортер') as console_reporter:
            console_reporter.values['plain'] = console_reporter.Value('plain', default=True)
            console_reporter.values['flat'] = 'flat'
            console_reporter.values[''] = '---'

    class Context(BaseTestTask.Context):
        task_status = ctt.Status.SUCCESS
        is_base_task_failed = False
        current_retry_task_id = None
        subtasks = []

    lifecycle_steps = copy.deepcopy(BaseTestTask.lifecycle_steps)
    lifecycle_steps.update({
        'merge_reports': './node_modules/.bin/hermione merge-reports {reports_refs} -d {report_dest}',
    })

    def on_enqueue(self):
        with self.memoize_stage.task_delay:
            if self.Parameters.task_delay is not None:
                raise sdk2.WaitTime(self.Parameters.task_delay)

        super(BaseHermioneCommonTask, self).on_enqueue()

    @property
    def run_cmd(self):
        return 'node_modules/.bin/hermione'

    def test(self):
        self.run_tests()

        if self.Context.task_status == ctt.Status.FAILURE:
            raise TaskFailure('Errors found, check report test.out.txt')

    def run_tests(self):
        self.__first_test_run()

        if self.__should_retry():
            with self.profile_action(actions_constants['TASK_RETRY'], 'Retry {} task'.format(self.tool)):
                self.__retry_task()

        if self.__has_retries():
            if self.__has_successful_retry():
                self.Context.task_status = ctt.Status.SUCCESS
            with self.profile_action(actions_constants['MERGE_REPORTS'], 'Merging reports'):
                try:
                    self.__merge_reports_from_subtasks()
                except Exception as e:
                    logging.warning('Cannot merge reports\n{}'.format(e))

    def __first_test_run(self):
        with self.memoize_stage.test:
            try:
                with self.profile_action(actions_constants['TEST'], 'Running {} tests'.format(self.tool)):
                    # force disable execution through the shell
                    # to register pid of process rather than shell
                    self.lifecycle('test', shell=False)
            except errors.SandboxSubprocessError:
                self.Context.is_base_task_failed = True
                self.Context.task_status = ctt.Status.FAILURE

                self.Context.retries_count = self.Context.retries_left = (
                    self.Parameters.task_retries
                    if self.Parameters.task_retries is not None
                    else self.config.get_deep_value(['tests', self._tool_config_name, 'task_retries'], 0)
                )
            finally:
                if self.Requirements.semaphores:
                    sdk2.Requirements.semaphores.release()
                    logging.info('{} tests released semaphores'.format(self.tool))

            with self.profile_action(actions_constants['REGISTER_REPORTS'], 'Register reports'):
                self.make_reports(self.Context.task_status)

            try:
                self._validate_plugins_result()
            except Exception as e:
                # Mark task as failed in case of failed plugin check.
                self.Context.task_status = ctt.Status.FAILURE
                raise e

            self.send_statistic()

    def __should_retry(self):
        return self.Context.is_base_task_failed and not self.__has_successful_retry() and self.Context.retries_left > 0

    def __has_retries(self):
        return bool(self.Context.subtasks)

    def __retry_task(self):
        hermione_subtask = self.__create_self_subtask()

        self.Context.current_retry_task_id = hermione_subtask.id
        self.Context.subtasks.append(self.Context.current_retry_task_id)
        self.Context.retries_left -= 1

        raise sdk2.WaitTask(
            tasks=self.meta.start_subtasks([hermione_subtask]),
            statuses=ctt.Status.Group.FINISH | ctt.Status.Group.BREAK,
        )

    @property
    def __task_retry_delay(self):
        task_retries_delay = (
            self.Parameters.task_retries_delay
            if self.Parameters.task_retries_delay
            else self.config.get_deep_value(['tests', self._tool_config_name, 'task_retries_delay'], [])
        )
        delays_count = len(task_retries_delay)

        if delays_count:
            delay_index = min(self.__current_retry_number, delays_count - 1)

            return datetime.timedelta(minutes=int(task_retries_delay[delay_index])).seconds

        return None

    @property
    def _tool_config_name(self):
        # replace "-" with "_", to get correct configuration for hermione-e2e
        return self.tool.replace('-', '_')

    def _get_self_subtask_attrs(self):
        task_attrs = dict(self.Parameters)
        json_report = self.__get_json_report()
        if json_report:
            failed_tests = json_report.failed_tests()
        else:
            logging.warn('json-report not found, retry all tests')
            failed_tests = []

        external_config_semaphores = self.browsers_config.format_external_config(failed_tests)
        task_attrs['external_config'].update(external_config_semaphores)

        test_filter_res = self.__create_test_filter_res(failed_tests)

        task_delay = self.__task_retry_delay

        task_attrs.update({
            'reusable': False,
            'report_github_statuses': False,
            'report_arcanum_checks': False,
            'send_statistic': False,
            'send_comment_to_searel': False,
            'send_comment_to_issue': '',
            'task_retries': 0,
            'tests_to_run_resource': test_filter_res,
            'task_delay': task_delay
        })

        # нужно удалить этот параметр, иначе он перетрет reuse_task_cache,
        # вычисленный на основе reusable в meta.prepare_subtask_parameters
        task_attrs.pop('reuse_task_cache', None)

        return task_attrs

    def __create_self_subtask(self):
        task_attrs = self._get_self_subtask_attrs()

        return self.meta.create_subtask(**dict(
            task_attrs,
            task_type=self.type
        ))

    def __merge_reports_from_subtasks(self):
        self.__merge_json_reports()
        self.__merge_html_reports()

    def __merge_html_reports(self):
        report_type = '{}-report'.format(self.tool)
        output_dirname = '{}-merged_report'.format(self.tool)
        status = self.Context.task_status
        current_html_report = sdk2.Resource.find(task_id=self.id, attrs={'type': report_type}).first()
        task_ids = [self.id] + self.Context.subtasks

        if self.Parameters.html_reporter_use_sqlite:
            is_published = self.html_report.publish_merged_sqlite_report(
                finished_task_ids=task_ids,
                report_type=report_type,
                output_dirname=output_dirname,
                status=status,
                attrs=self.report_common_attributes,
            )
        else:
            is_published = self.html_report.publish_merged_html_reports(
                task_ids=task_ids,
                report_type=report_type,
                output_dirname=output_dirname,
                status=status,
                attrs=self.report_common_attributes,
            )

        if is_published:
            self.Context.report_resources.remove(current_html_report.id)

    def __merge_json_reports(self):
        report_path = '{0}{suffix}{1}'.format(*os.path.splitext(self.json_reporter_file_path), suffix='-merged_report')

        self.json_report.publish_merged_json_reports(
            task_ids=[self.id] + self.Context.subtasks,
            report_path=report_path,
            status=self.Context.task_status,
            tags=','.join(self.Parameters.tags),
            attrs=self.report_common_attributes,
        )

    def __get_json_report(self):
        curr_task = self if not self.Context.current_retry_task_id else self.__get_current_retry_task()
        json_report_res = self.json_report.get_task_report_resource(curr_task.id)
        json_report = None

        if json_report_res:
            json_report = self.json_report.load(json_report_res)

        if json_report:
            self.Context.last_success_json_report = json_report_res.id
        else:
            prev_report_res = self.__get_last_success_json_report_resource()
            if prev_report_res:
                json_report = self.json_report.load(prev_report_res)

        return json_report

    def __get_last_success_json_report_resource(self):
        if self.Context.last_success_json_report:
            return self.artifacts.get_artifact_resource_by_id(self.Context.last_success_json_report)

        return self.json_report.get_task_report_resource(self.id)

    def __get_current_retry_task(self):
        return sdk2.Task.find(id=self.Context.current_retry_task_id, children=True).limit(1).first()

    def __create_test_filter_res(self, failed_tests):
        failed_tests_filter = map(lambda t: {'fullTitle': t['fullName'], 'browserId': t['browserId']}, failed_tests)

        logging.debug('Failed tests filter: {}'.format(failed_tests_filter))

        filter_file_name = 'test-filter-input_{}_{}.json'.format(self.tool, self.__current_retry_number)
        filter_file_path = self.working_path(filter_file_name)

        with open(str(filter_file_path), 'w') as f:
            data = json.dumps(failed_tests_filter, ensure_ascii=False)
            logging.debug(u'Writing {data} to "{file_path}"'.format(
                data=data,
                file_path=filter_file_path,
            ))
            f.write(data.encode('utf8'))

        resource_attrs = dict(
            self.report_common_attributes,
            resource_path=filter_file_path,
            type='tests-to-run-list'
        )

        logging.debug('Creating failed tests filter resource with attributes {}'.format(resource_attrs))

        return self.artifacts.create_report(**resource_attrs)

    def __has_successful_retry(self):
        task_id = self.Context.current_retry_task_id
        if not task_id:
            return False
        task = sdk2.Task.find(id=task_id, children=True).limit(1).first()

        return task.status in ctt.Status.Group.SUCCEED

    @property
    def __current_retry_number(self):
        return self.Context.retries_count - self.Context.retries_left

    @property
    def run_opts(self):
        opts = []

        if (self.Parameters.console_reporter != ''):
            opts.append('--reporter {}'.format(self.Parameters.console_reporter))

        opts.append(super(BaseHermioneCommonTask, self).run_opts)

        return ' '.join(opts)

    @property
    def hermione_profiler_report_path(self):
        return '{}-profiler'.format(self.tool)

    def set_environments(self):
        with self.memoize_stage.set_environments(commit_on_entrance=False):
            super(BaseHermioneCommonTask, self).set_environments()

            # browsers to run tests are defined by platform
            os.environ['PLATFORM'] = self.Parameters.platform

            os.environ['hermione_oauth_token'] = self.vault.read('env.SURFWAX_TOKEN')

            os.environ['hermione_profiler_path'] = self.hermione_profiler_report_path

            os.environ['hermione_faildump_enabled'] = 'true'
            os.environ['hermione_muted_tests_changed_files_path'] = getattr(self.Parameters, 'changed_files', '')

            if self.Parameters.html_reporter_use_sqlite:
                os.environ['html_reporter_save_format'] = 'sqlite'

    def prepare(self):
        self._download_sources(self.Parameters.build_artifacts_resources, self.project_dir)

    def _download_sources(self, resources, target_dir):
        return filter(bool, flatten(flow.parallel(apply, [
            lambda: super(BaseHermioneCommonTask, self)._download_sources(resources, target_dir),
            lambda: self._download_resources(target_dir),
        ])))

    @in_case_of('use_overlayfs', '_download_resources_in_overlayfs_mode')
    def _download_resources(self, target_dir):
        with self.memoize_stage.prepare_resources:
            return self.__download_resources_to_dir(target_dir=target_dir)

    def _download_resources_in_overlayfs_mode(self, *args, **kwargs):
        with self.memoize_stage.prepare_resources:
            target_dir = tempfile.mkdtemp()

            flow.parallel(apply, [
                lambda: self.__warmup_resources(),
                lambda: self.__download_resources_to_dir(pathlib2.Path(target_dir))
            ])

            return target_dir

    def __download_resources_to_dir(self, target_dir):
        with self.profile_action(actions_constants['DOWNLOAD_RESOURCES'], 'Downloading resources'):
            flow.parallel(apply, [
                lambda: self.selective.get_index(target_dir),
                lambda: self.stability_index.prepare_input(target_dir),
                lambda: self.__prepare_tests_to_run_list(target_dir),
                lambda: self._save_changed_files(target_dir)
            ])

    @in_case_of('use_overlayfs', '_save_changed_files_in_overlayfs_mode')
    def _save_changed_files(self, target_dir):
        pass

    def _save_changed_files_in_overlayfs_mode(self, target_dir):
        changed_files = getattr(self.Parameters, 'changed_files', '')
        if not changed_files:
            return

        with self.profile_action(actions_constants['SAVE_CHANGED_FILES'], 'Saving changed files'):
            if self.use_arc:
                return save_arc_changed_files(self.project_sources_dir, target_dir / changed_files)

            return save_git_changed_files(self.project_sources_dir, target_dir / changed_files)

    def __warmup_resources(self):
        if self.config.get_deep_value(['tests', self.tool, 'warmup', 'enabled'], False) and self.lifecycle.has_step('warmup'):
            with self.profile_action(actions_constants['WARMUP_RESOURCES'], 'Warming up resources'):
                self.lifecycle('warmup')

    def configure(self):
        with self.memoize_stage.configure:
            super(BaseHermioneCommonTask, self).configure()
            self.stability_index.configure()

    def execute_custom_command(self):
        with self.memoize_stage.execute_custom_command:
            super(BaseHermioneCommonTask, self).execute_custom_command()

    def __prepare_tests_to_run_list(self, target_dir):
        tests_to_run_resource = self.Parameters.tests_to_run_resource

        if tests_to_run_resource:
            res_path = str(self.project_path(tests_to_run_resource.path))

            os.environ['hermione_test_filter_input_file'] = str(res_path)
            self.artifacts.save_resources([tests_to_run_resource], target_dir)

    def _get_reports_attrs(self, status):
        reports_attrs = super(BaseHermioneCommonTask, self)._get_reports_attrs(status)

        reports_attrs.append(dict(
            resource_path=self.hermione_profiler_report_path,
            type='{}-profiler'.format(self.tool),
            status=status,
            add_to_context=True,
            public=True,
            root_path='index.html'
        ))

        reports_attrs.append(dict(
            resource_path='plugins-profiler',
            type='{}-plugins-profiler'.format(self.tool),
            status=status,
            add_to_context=True,
            public=True,
            root_path='index.html'
        ))

        reports_attrs.append(dict(
            resource_path=self.artifacts.duplicate_artifact_from_task_log('test.out.txt'),
            type='test.out.txt',
            status=status,
            add_to_context=True,
            public=True,
        ))

        reports_attrs.append(self.stability_index.get_output_report_attrs())

        return reports_attrs
