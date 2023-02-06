# coding=utf-8
import jinja2
import logging
import os
import os.path

import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskError
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import DnsType
from sandbox.common.utils import get_task_link
from sandbox.projects.common.utils import colored_status
from sandbox.projects.metrika.mobile.sdk.android_gradle_runner import AndroidGradleRunner
from sandbox.projects.metrika.mobile.sdk.helpers.AndroidContainerFinder import AndroidContainerFinder
from sandbox.projects.metrika.mobile.sdk.helpers.ReportsHelper import ReportsHelper
from sandbox.projects.metrika.mobile.sdk.helpers.ShellExecutor import ShellExecutor
from sandbox.projects.metrika.mobile.sdk.helpers.TarResourceHelper import TarResourceHelper
from sandbox.projects.metrika.mobile.sdk.helpers.TeamCityArtifactPublisher import TeamCityArtifactPublisher
from sandbox.projects.metrika.mobile.sdk.parameters.AggregatedReportParameters import AggregatedReportParameters
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TeamcityParameters import TeamcityParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.utils import custom_report_logger

WORKING_DIR = "wd"


class GenericTestsLauncher(sdk2.Task):
    """
    Base for tests launcher
    """

    class Utils:
        android_container_finder = AndroidContainerFinder()
        teamcity_publisher = TeamCityArtifactPublisher()
        tar_resource_helper = TarResourceHelper()
        shell_executor = ShellExecutor()
        reports_helper = ReportsHelper()

    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64
        disk_space = 1024
        cores = 4
        ram = 16384

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        project_repo = VcsParameters
        new_gradle_parameters = GradleParameters
        build_agent_parameters = BuildAgentParameters
        generic = TestParameters
        aggregated_report = AggregatedReportParameters
        teamcity_parameters = TeamcityParameters
        split_parameters = SplitParameters

        with sdk2.parameters.Group("Other parameters") as other_parameters_group:
            container_version = sdk2.parameters.String("Container version", required=True, default="stable")
            retry_count = sdk2.parameters.Integer("Retry count for child tasks", default=0)
            time_to_kill = sdk2.parameters.Integer("Time to kill",
                                                   description="Максимальное время выполнения дочерних задач в секундах",
                                                   default=3 * 60 * 60)
        with sdk2.parameters.Group("Experiments") as experiments_parameters:
            add_write_permissions = sdk2.parameters.Bool("Add write permission",
                                                         description="DON'T USE IT. NEVER. "
                                                                     "https://st.yandex-team.ru/FRANKENSTEIN-997",
                                                         default=False)

    class Context(sdk2.Task.Context):
        children = {}
        reports = None
        aggregated_reports = None
        build_task_id = None
        test_task_ids = {}
        report_task_id = None

    def on_save(self):
        if self.parent is not None and hasattr(self.parent.Parameters, 'add_write_permissions'):
            self.Parameters.add_write_permissions = self.parent.Parameters.add_write_permissions

    def on_enqueue(self):
        self.Context.reports = {name: "reports/" + path for name, path in self.Parameters.reports.items()}
        self.Context.aggregated_reports = self.Parameters.aggregated_report.aggregated_reports
        self.Context.retry_count = self.Parameters.retry_count or 0

    @sdk2.header()
    @custom_report_logger
    def report(self):
        reports = {name: "reports/" + path for name, path in self.Parameters.reports.items()}
        aggregated_reports = self.Parameters.aggregated_report.aggregated_reports
        context = []
        if self.Context.build_task_id:
            task_id = self.Context.build_task_id
            task_context = {
                "label": "Build task",
                "task_id": task_id,
                "task_link": get_task_link(task_id),
                "reports": {},
            }
            task = sdk2.Task.find(id=task_id, children=True).first()
            status = task.status if task is not None else "-"
            task_context["status"] = colored_status(status)

            context.append(task_context)

        if self.Context.test_task_ids:
            for (label, task_id) in sorted(self.Context.test_task_ids.items()):
                task_context = {
                    "label": label,
                    "task_id": task_id,
                    "task_link": get_task_link(task_id),
                    "reports": reports or {},
                }
                task = sdk2.Task.find(id=task_id, children=True).first()
                status = task.status if task is not None else "-"
                task_context["status"] = colored_status(status)
                if task and task.Context.artifacts_resource_id:
                    task_context["resource_link"] = sdk2.Resource.find(
                        id=task.Context.artifacts_resource_id).first().http_proxy

                context.append(task_context)

        if self.Context.report_task_id:
            task_id = self.Context.report_task_id
            task_context = {
                "label": "Report task",
                "task_id": task_id,
                "task_link": get_task_link(task_id),
                "reports": aggregated_reports or {},
            }
            task = sdk2.Task.find(id=task_id, children=True).first()
            status = task.status if task is not None else "-"
            task_context["status"] = colored_status(status)
            if task and task.Context.artifacts_resource_id:
                task_context["resource_link"] = sdk2.Resource.find(
                    id=task.Context.artifacts_resource_id).first().http_proxy

            context.append(task_context)

        template_context = {"rows": context}

        return jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
                                  extensions=['jinja2.ext.do']).get_template("header.html").render(template_context)

    def _task_succeed(self, task_id):
        task = sdk2.Task[task_id]
        return bool(task and task.status in ctt.Status.Group.SUCCEED)

    def _task_finished_without_exception(self, task_id):
        task = sdk2.Task[task_id]
        return bool(task and task.status != ctt.Status.EXCEPTION)

    def _work_dir(self, *path):
        return str(self.path(WORKING_DIR, *path))

    def _get_report_task(self):
        reports = self.Utils.tar_resource_helper.save_to_resource(
            task=self,
            description="Aggregated reports resource",
            current_dir=self.path(),
            resource_dir_name=WORKING_DIR,
            ttl=1,
            task_dir=self.path()
        )
        params = {}
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update({
            AndroidGradleRunner.Parameters.run_target.name: self.Parameters.aggregated_report_task,
            AndroidGradleRunner.Parameters.container.name:
                self.Utils.android_container_finder.get_build_container(self.Parameters.container_version),

            AndroidGradleRunner.Parameters.input_resource.name: reports,
            AndroidGradleRunner.Parameters.input_resource_path_param_name.name: self.Parameters.tasks_reports_dir_param_name,
            AndroidGradleRunner.Parameters.output_resource_path_param_name.name: self.Parameters.aggregated_reports_dir_param_name,
            AndroidGradleRunner.Parameters.output_resource_ttl.name: 7,
            AndroidGradleRunner.Parameters.output_resource_reports.name: self.Parameters.aggregated_reports,

            AndroidGradleRunner.Requirements.disk_space.name: self.Requirements.disk_space,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return AndroidGradleRunner(
            self,
            description="Generate aggregated report for tests",
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def on_execute(self):
        if not self.Parameters.tests_resource and self.Parameters.resource_path:
            try_idx = 0
            while True:
                if try_idx > self.Context.retry_count:
                    raise TaskError("Build task failed")
                with self.memoize_stage['build_plugin_resource_{}'.format(try_idx)](commit_on_entrance=False):
                    build_task = self._get_build_task()
                    build_task.enqueue()
                    self.Context.children['Build task'] = build_task.id
                    self.Context.build_task_id = build_task.id
                    raise sdk2.WaitTask(self.Context.children.values(),
                                        tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK))
                try_idx += 1
                if self.Context.build_task_id and self._task_succeed(self.Context.build_task_id):
                    break

        finished_without_exception_tasks = []
        try_idx = 0
        while True:
            if try_idx > self.Context.retry_count:
                break
            with self.memoize_stage['launch_tests_per_platform_{}'.format(try_idx)](commit_on_entrance=False):
                for caption, task in self._get_tasks().iteritems():
                    if caption not in finished_without_exception_tasks:
                        task.enqueue()
                        self.Context.children.update({caption: task.id})
                        self.Context.test_task_ids.update({caption: task.id})
                raise sdk2.WaitTask(self.Context.children.values(),
                                    tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK))
            try_idx += 1
            finished_without_exception_tasks = [
                caption
                for (caption, id) in self.Context.test_task_ids.iteritems()
                if self._task_finished_without_exception(id)
            ]
            logging.info("All tasks {}".format(self.Context.test_task_ids))
            logging.info("Finished without exception tasks {}".format(finished_without_exception_tasks))
            if len(finished_without_exception_tasks) == len(self.Context.test_task_ids):
                break

        if self.Parameters.aggregated_report_task or self.Parameters.pass_reports_to_teamcity:
            self.Utils.reports_helper.copy_reports(self)

        if self.Parameters.aggregated_report_task:
            with self.memoize_stage.make_aggregated_report(commit_on_entrance=False):
                report_task = self._get_report_task()
                report_task.enqueue()
                self.Context.children['Report task'] = report_task.id
                self.Context.report_task_id = report_task.id
                raise sdk2.WaitTask(self.Context.children.values(),
                                    tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK))
            if self.Context.report_task_id and not self._task_succeed(self.Context.report_task_id):
                raise TaskError("Report task failed")

        if self.Parameters.pass_reports_to_teamcity:
            with self.memoize_stage.create_teamcity_artifacts(commit_on_entrance=False):
                self.Utils.reports_helper.copy_aggregated_report(self)
                self.Utils.reports_helper.copy_log_dir(self)
                self.Utils.teamcity_publisher.publish_teamcity_artifacts(
                    self,
                    str(self.path("teamcity_messages.log")),
                    WORKING_DIR,
                    self.Parameters.teamcity_artifact_name or "report.zip"
                )

        with self.memoize_stage.check_children(commit_on_entrance=False):
            statuses = [(label, self.find(id=task_id).first().status) for (label, task_id) in
                        self.Context.children.items()]
            failed_statuses = filter(lambda status: status[1] not in ctt.Status.Group.SUCCEED, statuses)

            if failed_statuses:
                raise TaskFailure("\n".join(["{0}: {1}".format(label, status) for (label, status) in failed_statuses]))
