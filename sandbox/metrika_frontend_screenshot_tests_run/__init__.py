# coding=utf-8
import json
import os
import shutil

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.admins import base_metrika_tests
from sandbox.projects.metrika.frontend.metrika_frontend_screenshot_tests_run import view
from sandbox.projects.metrika.utils import artifacts, parameters, settings, vcs
from sandbox.projects.metrika.utils.base_metrika_task import base_metrika_task as bmt
from sandbox.projects.metrika.utils.mixins import console

TESTS_DIR = "metrika/frontend/tests/screenshooter"

SERVICES = [
    "appmetrica",
    "metrika",
    "radar"
]

PACKS = [
    "full",
    "full-crossbrowser",
    "desktop",
    "desktop-crossbrowser",
    "mobile",
    "mobile-crossbrowser"
]

TESTS = {
    "appmetrica": [
        "full",
        "desktop",
        "desktop-crossbrowser"
    ],
    "metrika": [
        "full",
        "full-crossbrowser",
        "desktop",
        "desktop-crossbrowser",
        "mobile",
        "mobile-crossbrowser"
    ],
    "radar": [
        "full",
        "full-crossbrowser",
        "desktop",
        "desktop-crossbrowser",
        "mobile",
        "mobile-crossbrowser"
    ]
}


@bmt.with_parents
class MetrikaFrontendScreenshotTestsRun(base_metrika_tests.BaseMetrikaTests, console.BaseConsoleMixin, sdk2.Task):
    """
    Run frontend screenshot tests
    """

    class Parameters(utils.CommonParameters):
        description = "Run Frontend Screenshot Tests"
        container = parameters.LastFrontendTestsContainerResource("Environment container resource", required=True)

        with sdk2.parameters.Group("Main parameters") as main_block:
            arcadia_url = sdk2.parameters.ArcadiaUrl("Arcadia URL", required=False, default="arcadia-arc:/#trunk")
            frontend_url = sdk2.parameters.Url("Frontend URL", required=True)

        with sdk2.parameters.Group("Startrek parameters") as st_block:
            comment_issue = sdk2.parameters.Bool("Comment issue with tests report", required=False, default=False)
            with comment_issue.value[True]:
                issue_key = parameters.TrackerIssue("Issue Key", required=True)

        with sdk2.parameters.Group("Testing parameters") as testing_block:
            service = sdk2.parameters.String(
                "Tested service", default=SERVICES[0], choices=[(item, item) for item in SERVICES]
            )
            pack = sdk2.parameters.String(
                "Tests pack", default=PACKS[0], choices=[(item, item) for item in PACKS]
            )
            workers_count = sdk2.parameters.Integer("Number of workers", default=5)
            env_vars = sdk2.parameters.Dict("Optional environment variables", required=False)
            fail_task_on_test_failure = sdk2.parameters.Bool(
                "Fail task on tests failures", required=False, default=False
            )

        with sdk2.parameters.Group("Secret parameters") as secret_block:
            tus_token = sdk2.parameters.YavSecretWithKey(
                "TUS token", required=False, default="{}#tus-token".format(settings.yav_uuid)
            )

        with sdk2.parameters.Output:
            with sdk2.parameters.Group("Results") as output_block:
                report_resource = sdk2.parameters.Resource("Report resource")
                test_results = sdk2.parameters.JSON("Tests results")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        with sdk2.helpers.ProgressMeter("Checkout"):
            self._checkout_branch()
        with sdk2.helpers.ProgressMeter("Build"):
            self._build()
        with sdk2.helpers.ProgressMeter("Run tests"):
            self._run_tests()
        with sdk2.helpers.ProgressMeter("Generate report"):
            self._generate_report()
        if self.Parameters.comment_issue:
            with sdk2.helpers.ProgressMeter("Comment issue"):
                self._report_startrek()
        self._analyze_results()

    def _checkout_branch(self):
        with vcs.mount_arc(self.Parameters.arcadia_url) as arcadia_root:
            shutil.copytree(str(os.path.join(arcadia_root, TESTS_DIR)), self.wd())

    def _build(self):
        self._execute_shell_and_check(["npm", "run", "build"], cwd=self.wd())

    def _run_tests(self):
        env = os.environ.copy()
        if self.Parameters.env_vars is not None:
            env.update(self.Parameters.env_vars)

        env["TUS_TOKEN"] = self.Parameters.tus_token.value()
        env["BASE_URL"] = self.Parameters.frontend_url

        if self.Parameters.pack in TESTS[self.Parameters.service]:
            self._execute_shell([
                "npm",
                "run",
                "{}:{}".format(self.Parameters.service, self.Parameters.pack),
                "--",
                "--workers",
                str(self.Parameters.workers_count)
            ], cwd=self.wd(), env=env)

    def _generate_report(self):
        self._execute_shell(["npm", "run", "build:static-report"], cwd=self.wd())
        artifacts_resource_id = artifacts.archive_artifacts_inplace(self, self.wd("allure-report"))

        self.Parameters.report_resource = sdk2.Resource.find(id=artifacts_resource_id).first()
        self.Parameters.test_results = self._extract_test_results()

    def _extract_test_results(self):
        with open(self.wd("allure-report/data/suites.json"), "r") as json_file:
            suites = json.load(json_file)
        with open(self.wd("allure-report/widgets/summary.json"), "r") as json_file:
            summary = json.load(json_file)

        statistic = summary["statistic"]
        return {
            "total": statistic["total"],
            "success": statistic["passed"],
            "failed": statistic["total"] - statistic["passed"],
            "suites": suites["children"],
            "failed_suites": []
        }

    def _get_view_model(self):
        return view.ViewModel(self)

    def shortcut(self):
        return "Скриншотные тесты фронтенда {}".format(self.Parameters.service)

    def report_description(self):
        return "Отчёт о тестировании"
