# -*- coding: utf-8 -*
import datetime
import itertools
import jinja2
import json
import logging
import os

import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import DnsType
from sandbox.common.utils import get_task_link
from sandbox.projects.common.decorators import retries
from sandbox.projects.metrika.mobile.sdk.helpers.GitHelper import GitHelper
from sandbox.projects.metrika.mobile.sdk.helpers.GradleExecutor import GradleExecutor
from sandbox.projects.metrika.mobile.sdk.helpers.ReportsHelper import ReportsHelper
from sandbox.projects.metrika.mobile.sdk.helpers.ShellExecutor import ShellExecutor
from sandbox.projects.metrika.mobile.sdk.helpers.TarResourceHelper import TarResourceHelper
from sandbox.projects.metrika.mobile.sdk.helpers.VcsHelper import VcsHelper
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.mobile.sdk.resources.GenericTestResource import GenericTestResource
from sandbox.projects.metrika.utils import custom_report_logger


class GenericTestsRunner(sdk2.Task):
    """
    Sdk Tests Base
    """

    class Utils:
        vcs_helper = VcsHelper()
        git_helper = GitHelper()
        shell_executor = ShellExecutor()
        gradle_executor = GradleExecutor()
        tar_resource_helper = TarResourceHelper(shell_executor)
        reports_helper = ReportsHelper()

    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64
        disk_space = 16384

    class Parameters(sdk2.Task.Parameters):
        project_repo = VcsParameters()
        new_gradle_parameters = GradleParameters()
        generic = TestParameters()
        expires = datetime.timedelta(hours=24)
        build_agent_parameters = BuildAgentParameters()
        split_parameters = SplitParameters()
        with sdk2.parameters.Group("Experiments") as experiments_parameters:
            add_write_permissions = sdk2.parameters.Bool("Add write permission",
                                                         description="DON'T USE IT. NEVER. "
                                                                     "https://st.yandex-team.ru/FRANKENSTEIN-997",
                                                         default=False)

    class Context(sdk2.Task.Context):
        artifacts_resource_id = None
        report_relative_path = None
        reports = None
        children = {}

    def on_save(self):
        if self.parent is not None and hasattr(self.parent.Parameters, 'add_write_permissions'):
            self.Parameters.add_write_permissions = self.parent.Parameters.add_write_permissions

    def on_enqueue(self):
        self.Context.reports = {name: "reports/" + path for name, path in self.Parameters.reports.items()}

    @retries(5)
    def on_prepare(self):
        with sdk2.helpers.ProgressMeter("Clone repository"):
            self.repo = self.Utils.vcs_helper.clone_with_task(self)

    def on_execute(self):
        with self.repo:
            if self.Parameters.get_config_target:
                self._split()
            else:
                self._run()

    def _work_dir(self, *path):
        return str(self.path("wd", *path))

    def _build(self, gradle_properties):
        if self.Parameters.resource_path and self.Parameters.tests_resource:
            self.Utils.tar_resource_helper.extract_input_resource(
                resource=self.Parameters.tests_resource,
                path=self._work_dir(self.Parameters.resource_path),
                task=self
            )
        elif self.Parameters.build_target:
            for target in filter(None, self.Parameters.build_target):
                for task in target.split():
                    self.Utils.gradle_executor.execute_gradle_with_failure(
                        path=self._work_dir(self.Parameters.gradle_base_dir),
                        tasks=[self.Parameters.gradle_log_level, "--stacktrace", task],
                        gradle_properties=gradle_properties,
                        system_properties=self.Parameters.system_gradle_parameters,
                        timeout=self.execute_shell_timeout,
                        environment=self.env
                    )

    def _get_config(self, gradle_properties):
        for target in filter(None, self.Parameters.get_config_target):
            for task in target.split():
                self.Utils.gradle_executor.execute_gradle_with_failure(
                    path=self._work_dir(self.Parameters.gradle_base_dir),
                    tasks=[self.Parameters.gradle_log_level, "--stacktrace", task],
                    gradle_properties=gradle_properties,
                    system_properties=self.Parameters.system_gradle_parameters,
                    timeout=self.execute_shell_timeout,
                    environment=self.env
                )

    def _split(self):
        with self.memoize_stage['get_config_and_split'](commit_on_entrance=False):
            with sdk2.helpers.ProgressMeter("Get config"):
                self._get_config(self._get_gradle_properties())
            with sdk2.helpers.ProgressMeter("Launch children"):
                with open(self._work_dir(self.Parameters.additional_params_path), "r") as f:
                    additional_params_dict = json.load(f)
                    self.logger.info("Loaded config {}".format(additional_params_dict))
                    for caption, additional_params in additional_params_dict.iteritems():
                        task = self._get_task_with_additional_params(caption, additional_params)
                        self.Context.children.update({caption: task.id})
                        task.enqueue()
                raise sdk2.WaitTask(self.Context.children.values(),
                                    tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK))
        with self.memoize_stage['merge_and_report'](commit_on_entrance=False):
            try:
                with sdk2.helpers.ProgressMeter("Copy reports"):
                    self.Utils.reports_helper.copy_reports_and_merge(
                        tasks=self.Context.children.items(),
                        dst=self._get_output_dir(),
                        temp_dir=self._work_dir("temp")
                    )
                with sdk2.helpers.ProgressMeter("Report results"):
                    self._prepare_custom_logs_resource()
                    self._report_test_results(self._get_gradle_properties())
            except Exception:
                self.logger.error("Exception in scenario", exc_info=True)
                raise
            finally:
                self._add_artifacts_to_custom_logs_resource()
                with sdk2.helpers.ProgressMeter("Check children"):
                    statuses = [(label, self.find(id=task_id).first().status) for (label, task_id) in
                                self.Context.children.items()]
                    failed_statuses = filter(lambda status: status[1] not in ctt.Status.Group.SUCCEED, statuses)

                    if failed_statuses:
                        raise TaskFailure("\n".join(["{0}: {1}".format(label, status) for (label, status) in failed_statuses]))

    def _prepare_additional_info(self):
        if self.Parameters.additional_params_path:
            filename = self._work_dir(self.Parameters.additional_params_path)
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, "w") as f:
                f.write(json.dumps(self.Parameters.additional_params))

    def _run_tests(self, gradle_properties):
        if self.Parameters.run_target:
            additional_cmd_line_args = []
            if self.Parameters.tests_pattern:
                additional_cmd_line_args = list(itertools.chain(*[["--tests", t] for t in self.Parameters.tests_pattern.split(',')]))

            if not self.Parameters.execute_if_failed:
                for target in filter(None, self.Parameters.run_target):
                    for task in target.split():
                        self.Utils.gradle_executor.execute_gradle_with_failure(
                            path=self._work_dir(self.Parameters.gradle_base_dir),
                            tasks=[self.Parameters.gradle_log_level, "--stacktrace", task] + additional_cmd_line_args,
                            gradle_properties=gradle_properties,
                            system_properties=self.Parameters.system_gradle_parameters,
                            timeout=self.execute_shell_timeout,
                            environment=self.env
                        )
            else:
                failures = []
                for target in filter(None, self.Parameters.run_target):
                    for task in target.split():
                        exit_code = self.Utils.gradle_executor.execute_gradle(
                            path=self._work_dir(self.Parameters.gradle_base_dir),
                            tasks=[self.Parameters.gradle_log_level, "--stacktrace", task] + additional_cmd_line_args,
                            gradle_properties=gradle_properties,
                            system_properties=self.Parameters.system_gradle_parameters,
                            timeout=self.execute_shell_timeout,
                            environment=self.env
                        )
                        if exit_code:
                            failures.append(
                                "Command\n{!r}\nFAILED. Exit code: {!r}".format(
                                    ' '.join([task] + additional_cmd_line_args),
                                    exit_code
                                )
                            )
                if failures:
                    raise TaskFailure('\n'.join(failures))

    def _report_test_results(self, gradle_properties):
        if self.Parameters.report_target:
            failures = []
            for target in filter(None, self.Parameters.report_target):
                for task in target.split():
                    exit_code = self.Utils.gradle_executor.execute_gradle(
                        path=self._work_dir(self.Parameters.gradle_base_dir),
                        tasks=[self.Parameters.gradle_log_level, "--stacktrace", task],
                        gradle_properties=gradle_properties,
                        system_properties=self.Parameters.system_gradle_parameters,
                        timeout=self.clean_up_timeout,
                        environment=self.env
                    )
                    if exit_code:
                        failures.append("Command\n{!r}\nFAILED. Exit code: {!r}".format(target, exit_code))
            if failures:
                raise TaskFailure('\n'.join(failures))

    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.getLogger("scenario")
        return self._logger

    @property
    def env(self):
        try:
            return self._env
        except AttributeError:
            self._env = self.Utils.shell_executor.default_env
            GradleParameters.prepare_env(self, self._env)
        return self._env

    @property
    def execute_shell_timeout(self):
        exec_time = self.server.task.current.read()["execution"]["current"]
        remaining_time = self.Parameters.kill_timeout - exec_time
        timeout = remaining_time - self.Parameters.report_duration
        self.logger.info("exec_time %d sec, remains %d sec, shell timeout: %d sec", exec_time, remaining_time, timeout)
        return timeout

    @property
    def clean_up_timeout(self):
        exec_time = self.server.task.current.read()["execution"]["current"]
        timeout = self.Parameters.kill_timeout - exec_time
        self.logger.info("exec_time %d sec, clean up timeout: %d sec", exec_time, timeout)
        return timeout

    def log_path_custom(self, *path):
        """
        Build path relative to custom logs - see log_path
        :param path: path components
        :rtype: pathlib2.Path
        """
        p = self.path("artifacts", *path)
        if not p.exists():
            os.makedirs(str(p))
        return p

    def _prepare_custom_logs_resource(self, backup=False):
        self.log_resource.ttl = 7
        artifacts_resource = self.Utils.tar_resource_helper.create_empty_resource(self, "Atrifacts", self.path(),
                                                                                  "artifacts.tar", ttl=7, backup=backup)
        self.Context.artifacts_resource_id = artifacts_resource.id

    def _add_artifacts_to_custom_logs_resource(self):
        artifacts_resource = sdk2.Resource[self.Context.artifacts_resource_id]
        self.Utils.tar_resource_helper.add_to_resource(artifacts_resource, self.log_path_custom())
        sdk2.ResourceData(artifacts_resource).ready()

    def _create_custom_logs_resource(self, backup=False):
        self.log_resource.ttl = 7
        artifacts_resource = self.Utils.tar_resource_helper.save_to_resource(self, "Atrifacts", self.path(),
                                                                             "artifacts", ttl=7, task_dir=self.path(),
                                                                             backup=backup)
        self.Context.artifacts_resource_id = artifacts_resource.id

    @sdk2.header()
    @custom_report_logger
    def report(self):
        if self.Context.artifacts_resource_id is not None:
            template_context = {
                "resource_link": sdk2.Resource[self.Context.artifacts_resource_id].http_proxy,
                "reports": self.Context.reports,
                "resources": {resource.description: resource.http_proxy
                              for resource in GenericTestResource.find(task=self).limit(0)}
            }
            return jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
                                      extensions=['jinja2.ext.do']).get_template("header.html").render(template_context)
        else:
            return None

    def _get_output_dir(self):
        return str(self.log_path_custom("reports").absolute())

    def _get_scheduler(self):
        task = self
        while task.parent is not None:
            task = task.parent
        return task.scheduler or 0

    def _get_gradle_properties(self):
        gradle_properties = {
            "build.url": get_task_link(self.id),
            "build.reports.url": "https://proxy.sandbox.yandex-team.ru/{0}/reports".format(self.Context.artifacts_resource_id),
            "build.scheduler.id": self._get_scheduler(),
            "build.task.id": self.id,
            self.Parameters.output_dir_param_name: self._get_output_dir(),
        }
        gradle_properties.update({k: v for k, v in self.Parameters.gradle_parameters.iteritems() if v})
        gradle_properties.update({k: sdk2.Vault.data(*v.split(':', 1))
                                  for k, v in self.Parameters.secret_gradle_parameters.iteritems() if v})
        return gradle_properties
